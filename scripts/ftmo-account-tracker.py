#!/usr/bin/env python3
"""
ftmo-account-tracker.py — Trackea el progreso de un challenge o cuenta funded FTMO.

Uso:
    # Primera vez — registrar cuenta nueva
    python scripts/ftmo-account-tracker.py --account-id FTMO-25K-001 \
        --initial-balance 25000 --mode update --current-balance 25000

    # Actualizar balance diario
    python scripts/ftmo-account-tracker.py --account-id FTMO-25K-001 \
        --current-balance 25480 --mode update

    # Ver estado actual
    python scripts/ftmo-account-tracker.py --account-id FTMO-25K-001 --mode report
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    import pytz
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False

ROOT    = Path(__file__).parent.parent
RESULTS = ROOT / "results"

# Umbrales FTMO 2-Step (25k)
DD_DAILY_LIMIT_PCT   = 5.0
DD_TOTAL_LIMIT_PCT   = 10.0
PROFIT_TARGET_PCT    = 10.0
MIN_TRADING_DAYS     = 4

# Umbrales de alerta (buffer antes del límite)
DD_DAILY_ALERT_PCT   = 3.0
DD_TOTAL_ALERT_PCT   = 7.0


def _account_file(account_id: str) -> Path:
    return RESULTS / f"account-{account_id}-tracker.json"


def _load_account(account_id: str) -> dict:
    path = _account_file(account_id)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_account(account_id: str, data: dict) -> None:
    path = _account_file(account_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _prague_midnight_balance_note() -> str:
    if not HAS_PYTZ:
        return "(pytz no instalado — usar balance a medianoche manual)"
    try:
        prague = pytz.timezone("Europe/Prague")
        now = datetime.now(prague)
        return f"Hora Prague actual: {now.strftime('%H:%M')} — balance medianoche se resetea a las 00:00"
    except Exception:
        return ""


def _semaforo(dd_daily: float, dd_total: float, profit_pct: float) -> str:
    if dd_daily >= 4.5 or dd_total >= 7.5:
        return "ROJO"
    if dd_daily >= DD_DAILY_ALERT_PCT or dd_total >= DD_TOTAL_ALERT_PCT:
        return "AMARILLO"
    return "VERDE"


def _notify(level: str, msg: str) -> None:
    import subprocess
    notifier = ROOT / "scripts" / "telegram-notifier.py"
    if not notifier.exists():
        return
    subprocess.run(
        [sys.executable, str(notifier), "--level", level, "--message", msg],
        capture_output=True
    )


def cmd_update(account_id: str, current_balance: float,
               initial_balance: float | None, balance_midnight: float | None) -> None:
    data = _load_account(account_id)

    # Primera vez
    if not data:
        if initial_balance is None:
            print(f"  ERROR: cuenta '{account_id}' no existe. Usa --initial-balance para crearla.")
            sys.exit(1)
        data = {
            "account_id":       account_id,
            "initial_balance":  initial_balance,
            "capital_base":     initial_balance,
            "peak_balance":     initial_balance,
            "trading_days":     0,
            "history":          [],
            "created":          _today(),
        }
        print(f"  Cuenta '{account_id}' creada con balance inicial: ${initial_balance:,.2f}")

    capital   = data["capital_base"]
    peak      = max(data["peak_balance"], current_balance)
    data["peak_balance"] = peak

    # Balance de medianoche para DD diario
    mid_balance = balance_midnight
    if mid_balance is None:
        # Usar el ultimo balance de cierre del dia anterior como referencia
        history = data.get("history", [])
        mid_balance = history[-1]["balance_eod"] if history else capital

    dd_daily  = round((mid_balance - current_balance) / mid_balance * 100, 2)
    dd_daily  = max(dd_daily, 0.0)

    dd_total  = round((peak - current_balance) / peak * 100, 2)
    dd_total  = max(dd_total, 0.0)

    profit_usd = current_balance - capital
    profit_pct = round(profit_usd / capital * 100, 2)

    # Contar dias de trading (dias con entrada unica por dia)
    today = _today()
    history = data.get("history", [])
    dates_in_history = {e["date"] for e in history}
    if today not in dates_in_history:
        data["trading_days"] = data.get("trading_days", 0) + 1

    semaforo = _semaforo(dd_daily, dd_total, profit_pct)

    entry = {
        "date":              today,
        "balance_midnight":  mid_balance,
        "balance_eod":       current_balance,
        "peak_balance":      peak,
        "dd_daily_pct":      dd_daily,
        "dd_total_pct":      dd_total,
        "profit_usd":        round(profit_usd, 2),
        "profit_pct":        profit_pct,
        "trading_days":      data["trading_days"],
        "semaforo":          semaforo,
    }

    # Reemplazar si ya hay entrada de hoy
    data["history"] = [e for e in history if e["date"] != today]
    data["history"].append(entry)
    _save_account(account_id, data)

    # Mostrar resumen
    print(f"\n  Cuenta actualizada: {account_id}")
    print(f"  {_prague_midnight_balance_note()}")
    print(f"  {'─'*50}")
    print(f"  Balance actual     : ${current_balance:>10,.2f}")
    print(f"  Profit acumulado   : {profit_pct:>+.2f}%  (${profit_usd:>+,.2f})")
    print(f"  Objetivo           : {PROFIT_TARGET_PCT:.0f}%  "
          f"(${capital * PROFIT_TARGET_PCT / 100:,.2f})")
    print(f"  Progreso           : {min(profit_pct/PROFIT_TARGET_PCT*100, 100):.1f}%")
    print(f"  DD diario hoy      : {dd_daily:.2f}%  (alerta: {DD_DAILY_ALERT_PCT}% | límite: {DD_DAILY_LIMIT_PCT}%)")
    print(f"  DD total           : {dd_total:.2f}%  (alerta: {DD_TOTAL_ALERT_PCT}% | límite: {DD_TOTAL_LIMIT_PCT}%)")
    print(f"  Días de trading    : {data['trading_days']}  (mínimo: {MIN_TRADING_DAYS})")
    print(f"  Semáforo           : {semaforo}")

    # Alertas
    alerts = []
    if dd_daily >= DD_DAILY_ALERT_PCT:
        alerts.append(f"DD diario {dd_daily:.2f}% — acercándose al límite {DD_DAILY_LIMIT_PCT}%")
    if dd_total >= DD_TOTAL_ALERT_PCT:
        alerts.append(f"DD total {dd_total:.2f}% — acercándose al límite {DD_TOTAL_LIMIT_PCT}%")

    if alerts:
        print(f"\n  ALERTAS:")
        for a in alerts:
            print(f"  [!] {a}")
        level = "CRITICAL" if semaforo == "ROJO" else "WARNING"
        _notify(level, f"Cuenta {account_id}: {' | '.join(alerts)}")

    # Check si se puede parar voluntariamente
    if profit_pct >= PROFIT_TARGET_PCT and data["trading_days"] >= MIN_TRADING_DAYS:
        print(f"\n  *** OBJETIVO ALCANZADO — puedes detener el EA ***")
        print(f"  Profit: {profit_pct:.2f}% >= {PROFIT_TARGET_PCT}% | "
              f"Días: {data['trading_days']} >= {MIN_TRADING_DAYS}")
        _notify("INFO", f"Cuenta {account_id}: OBJETIVO ALCANZADO — "
                        f"profit {profit_pct:.2f}%, {data['trading_days']} días")


def cmd_report(account_id: str) -> None:
    data = _load_account(account_id)
    if not data:
        print(f"  Cuenta '{account_id}' no encontrada.")
        print(f"  Archivo esperado: {_account_file(account_id)}")
        return

    history = data.get("history", [])
    capital = data["capital_base"]

    print(f"\n  {'═'*60}")
    print(f"  REPORTE — {account_id}")
    print(f"  {'═'*60}")
    print(f"  Capital base      : ${capital:>10,.2f}")
    print(f"  Balance pico      : ${data['peak_balance']:>10,.2f}")
    print(f"  Días de trading   : {data.get('trading_days', 0)}")
    print(f"  Creada            : {data.get('created', '?')}")
    print()

    if history:
        latest = history[-1]
        print(f"  ÚLTIMA ACTUALIZACIÓN — {latest['date']}")
        print(f"  {'─'*50}")
        print(f"  Balance EOD       : ${latest['balance_eod']:>10,.2f}")
        print(f"  Profit acumulado  : {latest['profit_pct']:>+.2f}%  "
              f"(${latest['profit_usd']:>+,.2f})")
        print(f"  Progreso objetivo : {min(latest['profit_pct']/PROFIT_TARGET_PCT*100,100):.1f}%")
        print(f"  DD diario         : {latest['dd_daily_pct']:.2f}%")
        print(f"  DD total          : {latest['dd_total_pct']:.2f}%")
        print(f"  Semáforo          : {latest['semaforo']}")

    if len(history) > 1:
        print(f"\n  HISTORIAL (últimos {min(7, len(history))} días)")
        print(f"  {'─'*60}")
        print(f"  {'Fecha':<12} {'Balance':>10} {'Profit%':>8} {'DD diario':>10} {'DD total':>9} {'Estado'}")
        print(f"  {'─'*60}")
        for e in history[-7:]:
            print(f"  {e['date']:<12} ${e['balance_eod']:>9,.2f} "
                  f"{e['profit_pct']:>7.2f}% "
                  f"{e['dd_daily_pct']:>9.2f}% "
                  f"{e['dd_total_pct']:>8.2f}%  {e['semaforo']}")

    print(f"  {'═'*60}")


def main() -> int:
    parser = argparse.ArgumentParser(description="FTMO Account Tracker — TradingLab")
    parser.add_argument("--account-id",       required=True,     help="ID de la cuenta (ej: FTMO-25K-001)")
    parser.add_argument("--initial-balance",  type=float,        help="Balance inicial (solo primera vez)")
    parser.add_argument("--current-balance",  type=float,        help="Balance actual para actualizar")
    parser.add_argument("--balance-midnight", type=float,        help="Balance a medianoche Prague (para DD diario)")
    parser.add_argument("--mode",             default="report",  choices=["update", "report"],
                        help="update: registrar balance | report: ver estado (default: report)")
    args = parser.parse_args()

    if args.mode == "update":
        if args.current_balance is None:
            print("  ERROR: --current-balance es obligatorio en modo update")
            return 1
        cmd_update(
            args.account_id,
            args.current_balance,
            args.initial_balance,
            args.balance_midnight,
        )
    else:
        cmd_report(args.account_id)

    return 0


if __name__ == "__main__":
    sys.exit(main())
