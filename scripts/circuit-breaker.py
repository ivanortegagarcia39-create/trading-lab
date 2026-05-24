#!/usr/bin/env python3
"""
circuit-breaker.py — Proteccion de drawdown diario para cuentas FTMO.

Conecta a MT5, calcula el DD diario actual y actua segun umbrales:
  >= 3.0% → WARNING Telegram
  >= 4.0% → ALERTA + flag de reduccion de lotaje 50%
  >= 4.5% → cierre TOTAL de todas las posiciones

Uso:
    python scripts/circuit-breaker.py
    python scripts/circuit-breaker.py --dry-run

Estado guardado en: results/circuit-breaker-state.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from subprocess import run as _run

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

ROOT    = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"
STATE_PATH = ROOT / "results" / "circuit-breaker-state.json"

# Umbrales de drawdown diario (%)
DD_WARNING  = 3.0
DD_ALERT    = 4.0
DD_SHUTDOWN = 4.5


def _notify(level: str, msg: str) -> None:
    notifier = SCRIPTS / "telegram-notifier.py"
    if not notifier.exists():
        return
    _run([sys.executable, str(notifier), "--level", level, "--message", msg],
         capture_output=True)


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False),
                          encoding="utf-8")


def _load_state() -> dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def connect_mt5():
    try:
        import MetaTrader5 as mt5
    except ImportError:
        print("ERROR: MetaTrader5 no instalado. Ejecuta: pip install MetaTrader5")
        sys.exit(1)

    if not mt5.initialize():
        print(f"ERROR: mt5.initialize() fallo: {mt5.last_error()}")
        mt5.shutdown()
        sys.exit(1)

    return mt5


def get_account_data(mt5) -> dict:
    info = mt5.account_info()
    if info is None:
        print(f"ERROR: mt5.account_info() fallo: {mt5.last_error()}")
        mt5.shutdown()
        sys.exit(1)

    equity  = info.equity
    balance = info.balance

    # Balance de ayer = balance actual - suma de P&L cerrado hoy
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    deals = mt5.history_deals_get(today_start, datetime.now())
    today_pnl = sum(d.profit + d.commission + d.swap for d in deals) if deals else 0.0
    balance_ayer = balance - today_pnl

    return {
        "equity":        equity,
        "balance":       balance,
        "balance_ayer":  balance_ayer,
        "today_pnl":     round(today_pnl, 2),
        "account_login": info.login,
        "account_name":  info.name,
        "currency":      info.currency,
    }


def calc_drawdown(equity: float, balance_ayer: float) -> float:
    if balance_ayer <= 0:
        return 0.0
    return round((balance_ayer - equity) / balance_ayer * 100, 2)


def close_all_positions(mt5, dry_run: bool) -> int:
    positions = mt5.positions_get()
    if not positions:
        return 0

    closed = 0
    for pos in positions:
        tick = mt5.symbol_info_tick(pos.symbol)
        if tick is None:
            print(f"  WARN: no se pudo obtener tick para {pos.symbol}")
            continue

        order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price      = tick.bid if pos.type == mt5.POSITION_TYPE_BUY else tick.ask

        if dry_run:
            print(f"  [DRY-RUN] Cerrar {pos.symbol} {pos.volume} lots ticket={pos.ticket}")
            closed += 1
            continue

        request = {
            "action":      mt5.TRADE_ACTION_DEAL,
            "symbol":      pos.symbol,
            "volume":      pos.volume,
            "type":        order_type,
            "position":    pos.ticket,
            "price":       price,
            "deviation":   20,
            "magic":       0,
            "comment":     "circuit-breaker",
            "type_time":   mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            retcode = result.retcode if result else "None"
            print(f"  WARN: no se pudo cerrar {pos.symbol} ticket={pos.ticket} retcode={retcode}")
        else:
            closed += 1

    return closed


def main() -> int:
    parser = argparse.ArgumentParser(description="Circuit Breaker — TradingLab")
    parser.add_argument("--dry-run", action="store_true", help="Simular sin cerrar posiciones")
    args = parser.parse_args()

    timestamp = datetime.now(timezone.utc).isoformat()
    prev_state = _load_state()

    # Conectar MT5
    mt5 = connect_mt5()

    try:
        data = get_account_data(mt5)
    finally:
        mt5.shutdown()

    equity       = data["equity"]
    balance_ayer = data["balance_ayer"]
    dd           = calc_drawdown(equity, balance_ayer)

    print(f"[{timestamp}]")
    print(f"  Equity hoy   : {equity:.2f} {data['currency']}")
    print(f"  Balance ayer : {balance_ayer:.2f} {data['currency']}")
    print(f"  DD diario    : {dd:.2f}%")

    action   = "ok"
    lot_factor = prev_state.get("lot_factor", 1.0)

    if dd >= DD_SHUTDOWN:
        action = "shutdown"
        print(f"  SHUTDOWN: DD {dd}% >= {DD_SHUTDOWN}% — cerrando todas las posiciones")
        mt5_conn = connect_mt5()
        try:
            closed = close_all_positions(mt5_conn, args.dry_run)
        finally:
            mt5_conn.shutdown()
        lot_factor = 0.0
        msg = (f"CIRCUIT BREAKER ACTIVADO — DD diario {dd}% "
               f"Todas las posiciones cerradas ({closed}). "
               f"Cuenta {data['account_login']} PROTEGIDA.")
        if not args.dry_run:
            _notify("CRITICAL", msg)
        else:
            print(f"  [DRY-RUN] Telegram CRITICAL: {msg}")

    elif dd >= DD_ALERT:
        action = "alert"
        lot_factor = 0.5
        print(f"  ALERTA: DD {dd}% >= {DD_ALERT}% — reduciendo lotaje al 50%")
        msg = (f"ALERTA DD — {dd}% drawdown diario. "
               f"Lotaje reducido al 50%. Cuenta {data['account_login']}.")
        if not args.dry_run:
            _notify("WARNING", msg)
        else:
            print(f"  [DRY-RUN] Telegram WARNING: {msg}")

    elif dd >= DD_WARNING:
        action = "warning"
        print(f"  WARNING: DD {dd}% >= {DD_WARNING}%")
        # Solo notificar si no se notifico en los ultimos 30 min
        last_warn = prev_state.get("last_warning_ts", "")
        already_warned = False
        if last_warn:
            try:
                dt_last = datetime.fromisoformat(last_warn)
                if dt_last.tzinfo is None:
                    dt_last = dt_last.replace(tzinfo=timezone.utc)
                delta = (datetime.now(timezone.utc) - dt_last).total_seconds()
                already_warned = delta < 1800
            except Exception:
                pass
        if not already_warned:
            msg = f"WARNING DD — {dd}% drawdown diario. Cuenta {data['account_login']}."
            if not args.dry_run:
                _notify("WARNING", msg)
            else:
                print(f"  [DRY-RUN] Telegram WARNING: {msg}")
    else:
        print(f"  OK: DD {dd}% < {DD_WARNING}% — sin accion")
        lot_factor = 1.0

    state = {
        "timestamp":      timestamp,
        "account_login":  data["account_login"],
        "equity":         equity,
        "balance_ayer":   balance_ayer,
        "dd_pct":         dd,
        "action":         action,
        "lot_factor":     lot_factor,
        "positions_closed": 0,
        "dry_run":        args.dry_run,
    }
    if action == "warning":
        state["last_warning_ts"] = timestamp
    elif prev_state.get("last_warning_ts"):
        state["last_warning_ts"] = prev_state["last_warning_ts"]

    if not args.dry_run:
        _save_state(state)
    else:
        print(f"  [DRY-RUN] state: {json.dumps(state)}")

    return 0 if action in ("ok", "warning", "alert", "shutdown") else 1


if __name__ == "__main__":
    sys.exit(main())
