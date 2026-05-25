#!/usr/bin/env python3
"""
ftmo-compliance-checker.py -- Verifica reglas de consistencia FTMO

Lee el historial de trades desde results/mt5-trades.json y verifica:
  1. Best Day Rule      -- mejor dia no supera 50% del profit total
  2. Consistency Check  -- ningun trade individual > 40% del profit del dia
  3. Min Trading Days   -- dias con al menos 1 trade cerrado (minimo 4)
  4. Profit Target      -- progreso hacia objetivo Challenge (10%) / Verification (5%)

Uso:
    python scripts/ftmo-compliance-checker.py --capital 25000 --mode challenge
    python scripts/ftmo-compliance-checker.py --capital 25000 --mode verification
    python scripts/ftmo-compliance-checker.py --capital 25000 --check
    python scripts/ftmo-compliance-checker.py --dry-run --capital 25000

Requiere: results/mt5-trades.json (escrito por EA de MT5)
    [
      {"close_time": "2026-05-24 15:30:00", "profit": 125.50, "symbol": "EURUSD"},
      ...
    ]

Salida: results/ftmo-compliance-state.json
"""

import argparse
import io
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    import pytz
except ImportError:
    print("ERROR: pytz no instalado. Ejecuta: pip install pytz")
    sys.exit(1)

ROOT             = Path(__file__).parent.parent
MT5_TRADES_PATH  = ROOT / "results" / "mt5-trades.json"
COMPLIANCE_STATE = ROOT / "results" / "ftmo-compliance-state.json"
PRAGUE_TZ        = pytz.timezone("Europe/Prague")

BEST_DAY_LIMIT_PCT  = 0.50   # mejor dia <= 50% del profit total
CONSISTENCY_PCT     = 0.40   # ningun trade > 40% del profit del dia
MIN_TRADING_DAYS    = 4

PROFIT_TARGETS = {
    "challenge":    0.10,
    "verification": 0.05,
}


# ─── I/O ──────────────────────────────────────────────────────────────────────

def _load_trades() -> list[dict]:
    if not MT5_TRADES_PATH.exists():
        return []
    try:
        raw = json.loads(MT5_TRADES_PATH.read_text(encoding="utf-8"))
        return raw if isinstance(raw, list) else []
    except Exception as e:
        print(f"  WARN: no se pudo leer {MT5_TRADES_PATH}: {e}")
        return []


def _save_state(state: dict) -> None:
    COMPLIANCE_STATE.parent.mkdir(parents=True, exist_ok=True)
    COMPLIANCE_STATE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _notify(level: str, message: str, dry_run: bool = False) -> None:
    notifier = ROOT / "scripts" / "telegram-notifier.py"
    if not notifier.exists():
        return
    if dry_run:
        print(f"  [DRY-RUN] Telegram {level}: {message}")
        return
    subprocess.run(
        [sys.executable, str(notifier), "--level", level, "--message", message],
        capture_output=True,
    )


# ─── Parseo de trades ──────────────────────────────────────────────────────────

def _parse_close_time(raw: str) -> datetime | None:
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt_naive = datetime.strptime(raw.strip(), fmt)
            dt_utc   = pytz.utc.localize(dt_naive)
            return dt_utc.astimezone(PRAGUE_TZ)
        except ValueError:
            continue
    return None


def _group_by_day(trades: list[dict]) -> dict[str, list[dict]]:
    """Agrupa trades por fecha Prague (YYYY-MM-DD)."""
    by_day: dict[str, list[dict]] = defaultdict(list)
    for t in trades:
        close_raw = t.get("close_time", "")
        dt = _parse_close_time(close_raw)
        if dt is None:
            continue
        profit = float(t.get("profit", 0.0))
        by_day[dt.strftime("%Y-%m-%d")].append({
            "close_time": close_raw,
            "profit":     profit,
            "symbol":     t.get("symbol", ""),
        })
    return dict(by_day)


# ─── Checks ───────────────────────────────────────────────────────────────────

def check_best_day(by_day: dict, total_profit: float) -> dict:
    """Mejor dia no debe superar BEST_DAY_LIMIT_PCT del profit total."""
    if total_profit <= 0:
        return {"ok": True, "best_day": 0.0, "best_day_date": None,
                "ratio": 0.0, "limit_pct": BEST_DAY_LIMIT_PCT, "alert": False}

    daily_profits = {day: sum(t["profit"] for t in ts) for day, ts in by_day.items()}
    best_day_date = max(daily_profits, key=daily_profits.get)
    best_day_profit = daily_profits[best_day_date]

    ratio = best_day_profit / total_profit if total_profit > 0 else 0.0
    alert = ratio > BEST_DAY_LIMIT_PCT and best_day_profit > 0

    return {
        "ok":             not alert,
        "best_day":       round(best_day_profit, 2),
        "best_day_date":  best_day_date,
        "ratio":          round(ratio, 4),
        "ratio_pct":      round(ratio * 100, 1),
        "limit_pct":      BEST_DAY_LIMIT_PCT * 100,
        "alert":          alert,
    }


def check_consistency(by_day: dict) -> dict:
    """Ningun trade individual > CONSISTENCY_PCT del profit total del dia."""
    violations = []
    for day, trades in by_day.items():
        day_profit = sum(t["profit"] for t in trades)
        if day_profit <= 0:
            continue
        for t in trades:
            if t["profit"] <= 0:
                continue
            ratio = t["profit"] / day_profit
            if ratio > CONSISTENCY_PCT:
                violations.append({
                    "date":       day,
                    "trade_profit": round(t["profit"], 2),
                    "day_profit":   round(day_profit, 2),
                    "ratio_pct":    round(ratio * 100, 1),
                    "symbol":       t["symbol"],
                    "close_time":   t["close_time"],
                })
    return {
        "ok":         len(violations) == 0,
        "violations": violations,
        "limit_pct":  CONSISTENCY_PCT * 100,
        "alert":      len(violations) > 0,
    }


def check_trading_days(by_day: dict) -> dict:
    """Cuenta dias con al menos 1 trade cerrado."""
    days_traded = len(by_day)
    days_remaining = max(0, MIN_TRADING_DAYS - days_traded)
    return {
        "ok":             days_traded >= MIN_TRADING_DAYS,
        "days_traded":    days_traded,
        "days_remaining": days_remaining,
        "minimum":        MIN_TRADING_DAYS,
        "alert":          False,  # informativo, no bloquea
    }


def check_profit_target(total_profit: float, capital: float, mode: str) -> dict:
    """Progreso hacia el objetivo de profit."""
    target_pct = PROFIT_TARGETS.get(mode, PROFIT_TARGETS["challenge"])
    target_usd  = capital * target_pct
    current_pct = total_profit / capital if capital > 0 else 0.0
    progress    = current_pct / target_pct if target_pct > 0 else 0.0

    return {
        "ok":          current_pct >= target_pct,
        "target_pct":  round(target_pct * 100, 1),
        "target_usd":  round(target_usd, 2),
        "current_usd": round(total_profit, 2),
        "current_pct": round(current_pct * 100, 2),
        "progress_pct": round(min(progress * 100, 100.0), 1),
        "remaining_usd": round(max(target_usd - total_profit, 0.0), 2),
        "alert":        False,
    }


# ─── Runner principal ─────────────────────────────────────────────────────────

def run_compliance(capital: float, mode: str, dry_run: bool) -> dict:
    trades = _load_trades()

    if not trades:
        print("  INFO: no hay trades en mt5-trades.json — nada que verificar")
        state = {
            "timestamp": datetime.now().isoformat(),
            "capital":   capital,
            "mode":      mode,
            "trades_total": 0,
            "trading_days": 0,
            "total_profit_usd": 0.0,
            "checks": {
                "best_day":    {"ok": True, "alert": False, "best_day_date": None,
                                "best_day": 0.0, "ratio_pct": 0.0, "limit_pct": BEST_DAY_LIMIT_PCT * 100},
                "consistency": {"ok": True, "alert": False, "violations": [], "limit_pct": CONSISTENCY_PCT * 100},
                "trading_days":  {"ok": False, "days_traded": 0, "days_remaining": MIN_TRADING_DAYS,
                                  "minimum": MIN_TRADING_DAYS},
                "profit_target": {"ok": False, "current_pct": 0.0, "progress_pct": 0.0,
                                  "target_pct": PROFIT_TARGETS.get(mode, 0.10) * 100,
                                  "remaining_usd": capital * PROFIT_TARGETS.get(mode, 0.10)},
            },
            "overall_ok": True,
            "alerts": [],
        }
        _save_state(state)
        return state

    by_day       = _group_by_day(trades)
    total_profit = sum(t.get("profit", 0.0) for t in trades)

    best_day    = check_best_day(by_day, total_profit)
    consistency = check_consistency(by_day)
    t_days      = check_trading_days(by_day)
    profit_prog = check_profit_target(total_profit, capital, mode)

    alerts = []

    if best_day["alert"]:
        msg = (f"FTMO Best Day Rule: mejor dia ({best_day['best_day_date']}) "
               f"= {best_day['ratio_pct']}% del profit total "
               f"(limite: {best_day['limit_pct']}%)")
        alerts.append(msg)
        _notify("WARNING", msg, dry_run)

    if consistency["alert"]:
        for v in consistency["violations"]:
            msg = (f"FTMO Consistency: trade {v['symbol']} {v['close_time']} "
                   f"= {v['ratio_pct']}% del profit del dia "
                   f"(limite: {consistency['limit_pct']}%)")
            alerts.append(msg)
            _notify("WARNING", msg, dry_run)

    state = {
        "timestamp":        datetime.now().isoformat(),
        "capital":          capital,
        "mode":             mode,
        "trades_total":     len(trades),
        "trading_days":     len(by_day),
        "total_profit_usd": round(total_profit, 2),
        "checks": {
            "best_day":      best_day,
            "consistency":   consistency,
            "trading_days":  t_days,
            "profit_target": profit_prog,
        },
        "overall_ok": not alerts,
        "alerts":     alerts,
    }

    _save_state(state)
    return state


# ─── Output ───────────────────────────────────────────────────────────────────

def _print_report(state: dict) -> None:
    c = state["checks"]
    bd = c["best_day"]
    cs = c["consistency"]
    td = c["trading_days"]
    pt = c["profit_target"]

    print(f"\n{'='*55}")
    print(f"  FTMO COMPLIANCE CHECK")
    print(f"{'='*55}")
    print(f"  Capital    : ${state['capital']:>10,.2f}")
    print(f"  Modo       : {state['mode'].upper()}")
    print(f"  Trades     : {state['trades_total']}  |  Dias: {state['trading_days']}")
    print(f"  Profit     : ${state['total_profit_usd']:>+10,.2f}")
    print(f"  Timestamp  : {state['timestamp'][:19]}")
    print(f"{'─'*55}")

    # Best Day
    status = "ALERTA" if bd["alert"] else "OK"
    if bd.get("best_day_date"):
        print(f"  [1] Best Day Rule  : {status}")
        print(f"      Mejor dia      : {bd['best_day_date']}  ${bd['best_day']:,.2f}")
        print(f"      % del profit   : {bd['ratio_pct']}%  (limite: {bd['limit_pct']}%)")
    else:
        print(f"  [1] Best Day Rule  : OK (sin profit positivo)")

    # Consistency
    status = "ALERTA" if cs["alert"] else "OK"
    print(f"  [2] Consistency    : {status}  ({len(cs['violations'])} violaciones)")
    for v in cs["violations"]:
        print(f"      {v['date']} {v['symbol']}: trade={v['ratio_pct']}% del dia")

    # Trading Days
    status = "OK" if td["ok"] else f"FALTAN {td['days_remaining']} dias"
    print(f"  [3] Trading Days   : {status}  ({td['days_traded']}/{td['minimum']})")

    # Profit Target
    status = "ALCANZADO" if pt["ok"] else f"{pt['progress_pct']}% completado"
    print(f"  [4] Profit Target  : {status}")
    print(f"      Actual         : {pt['current_pct']}%  (objetivo: {pt['target_pct']}%)")
    if not pt["ok"]:
        print(f"      Faltan         : ${pt['remaining_usd']:,.2f}")

    print(f"{'─'*55}")
    overall = "OK" if state["overall_ok"] else "ALERTAS ACTIVAS"
    print(f"  RESULTADO GLOBAL   : {overall}")
    if state["alerts"]:
        for a in state["alerts"]:
            print(f"  [!] {a}")
    print(f"{'='*55}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="FTMO Compliance Checker -- TradingLab")
    parser.add_argument("--capital",  type=float, default=25000,
                        help="Capital inicial (default: 25000)")
    parser.add_argument("--mode",     choices=["challenge", "verification"], default="challenge",
                        help="Fase del challenge (default: challenge)")
    parser.add_argument("--check",    action="store_true",
                        help="Modo check rapido (para N8N / API)")
    parser.add_argument("--dry-run",  action="store_true",
                        help="No envia Telegram, solo imprime")
    args = parser.parse_args()

    state = run_compliance(args.capital, args.mode, args.dry_run)

    if args.check:
        print(json.dumps(state, indent=2, ensure_ascii=False))
    else:
        _print_report(state)

    return 0 if state["overall_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
