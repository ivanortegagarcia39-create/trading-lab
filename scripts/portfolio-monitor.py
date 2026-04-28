#!/usr/bin/env python3
"""
portfolio-monitor.py — Monitoreo del portfolio en produccion

Uso:
    python portfolio-monitor.py --mode report
    python portfolio-monitor.py --mode monitor --interval 300

Lee datos de:
    results/strategies-registry.json
    results/accounts-inventory.json

Alertas via telegram-notifier.py:
    DD > 3%           → WARNING
    DD > 4.5%         → CRITICAL
    Correlacion > 0.85 → CRITICAL (Modo Panico)
    Z-Score <= -2.0 por 4 semanas → WARNING (Decay)
    Sin trades 15 dias → WARNING (Inactividad)
"""

import argparse
import json
import math
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPTS_DIR.parent / "results"
REGISTRY_PATH = RESULTS_DIR / "strategies-registry.json"
ACCOUNTS_PATH = RESULTS_DIR / "accounts-inventory.json"

DD_WARNING = 3.0
DD_CRITICAL = 4.5
CORR_PANIC = 0.85
ZSCORE_DECAY = -2.0
ZSCORE_WEEKS_DECAY = 4
INACTIVITY_DAYS = 15


def _load_json(path: Path) -> dict | list:
    if not path.exists():
        print(f"ERROR: {path} no encontrado.")
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def _send_alert(level: str, message: str, dry_run: bool = False):
    import subprocess
    notifier = SCRIPTS_DIR / "telegram-notifier.py"
    if not notifier.exists():
        print(f"[{level}] {message}")
        return
    cmd = [sys.executable, str(notifier), "--level", level, "--message", message]
    if dry_run:
        cmd.append("--dry-run")
    subprocess.run(cmd, check=False)


def _calc_rolling_pf(trades: list[dict], weeks: int = 4) -> float:
    cutoff = datetime.now() - timedelta(weeks=weeks)
    recent = [t for t in trades if datetime.fromisoformat(t["timestamp"]) >= cutoff]
    wins = sum(t["pnl"] for t in recent if t["pnl"] > 0)
    losses = abs(sum(t["pnl"] for t in recent if t["pnl"] < 0))
    return round(wins / losses, 4) if losses > 0 else float("inf")


def _calc_rolling_correlation(strategies: list[dict], days: int = 30) -> float:
    """Correlacion promedio entre todos los pares de estrategias en los ultimos N dias."""
    cutoff = datetime.now() - timedelta(days=days)
    daily_pnls: dict[str, dict[str, float]] = {}

    for s in strategies:
        sid = s["id"]
        for t in s.get("trades", []):
            try:
                dt = datetime.fromisoformat(t["timestamp"])
            except (KeyError, ValueError):
                continue
            if dt < cutoff:
                continue
            day = dt.strftime("%Y-%m-%d")
            daily_pnls.setdefault(sid, {})
            daily_pnls[sid][day] = daily_pnls[sid].get(day, 0) + t["pnl"]

    sids = list(daily_pnls.keys())
    if len(sids) < 2:
        return 0.0

    all_days = sorted(set(d for v in daily_pnls.values() for d in v))
    vectors: dict[str, list[float]] = {sid: [daily_pnls[sid].get(d, 0) for d in all_days] for sid in sids}

    def pearson(a: list[float], b: list[float]) -> float:
        n = len(a)
        if n < 2:
            return 0.0
        ma = sum(a) / n
        mb = sum(b) / n
        num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
        da = math.sqrt(sum((x - ma) ** 2 for x in a))
        db = math.sqrt(sum((y - mb) ** 2 for y in b))
        return num / (da * db) if da * db > 0 else 0.0

    corrs = []
    for i in range(len(sids)):
        for j in range(i + 1, len(sids)):
            corrs.append(abs(pearson(vectors[sids[i]], vectors[sids[j]])))

    return round(sum(corrs) / len(corrs), 4) if corrs else 0.0


def _calc_zscore_pf(trades: list[dict]) -> dict:
    """Z-Score del PF mensual de los ultimos 4 meses."""
    monthly: dict[str, list[float]] = {}
    for t in trades:
        try:
            dt = datetime.fromisoformat(t["timestamp"])
        except (KeyError, ValueError):
            continue
        key = dt.strftime("%Y-%m")
        monthly.setdefault(key, []).append(t["pnl"])

    monthly_pf = {}
    for month, pnls in monthly.items():
        w = sum(p for p in pnls if p > 0)
        l = abs(sum(p for p in pnls if p < 0))
        monthly_pf[month] = w / l if l > 0 else float("inf")

    sorted_months = sorted(monthly_pf.keys())
    last4 = sorted_months[-4:]
    pfs = [monthly_pf[m] for m in last4 if monthly_pf[m] != float("inf")]

    if len(pfs) < 2:
        return {"zscore": 0.0, "months": last4, "pfs": pfs}

    mean = sum(pfs) / len(pfs)
    std = math.sqrt(sum((x - mean) ** 2 for x in pfs) / (len(pfs) - 1))
    last_pf = pfs[-1]
    zscore = (last_pf - mean) / std if std > 0 else 0.0
    return {"zscore": round(zscore, 4), "months": last4, "pfs": pfs}


def _days_since_last_trade(trades: list[dict]) -> int:
    if not trades:
        return 9999
    last_ts = max(datetime.fromisoformat(t["timestamp"]) for t in trades
                  if "timestamp" in t)
    return (datetime.now() - last_ts).days


def _calc_portfolio_dd(account: dict) -> tuple[float, float]:
    """Retorna (dd_daily_pct, dd_total_pct)."""
    balance = account.get("balance", 0)
    equity = account.get("equity", balance)
    balance_midnight = account.get("balance_midnight", balance)
    peak_equity = account.get("peak_equity", balance)

    dd_daily = (balance_midnight - equity) / balance_midnight * 100 if balance_midnight > 0 else 0
    dd_total = (peak_equity - equity) / peak_equity * 100 if peak_equity > 0 else 0
    return round(max(dd_daily, 0), 4), round(max(dd_total, 0), 4)


def generate_report(dry_run: bool = False) -> dict:
    registry = _load_json(REGISTRY_PATH)
    accounts = _load_json(ACCOUNTS_PATH)

    strategies = registry if isinstance(registry, list) else registry.get("strategies", [])
    account_list = accounts if isinstance(accounts, list) else accounts.get("accounts", [])

    report = {
        "timestamp": datetime.now().isoformat(),
        "strategies": [],
        "portfolio": {},
        "alerts": [],
    }

    all_trades = []
    for s in strategies:
        all_trades.extend(s.get("trades", []))

    # Metricas portfolio
    avg_corr = _calc_rolling_correlation(strategies)
    rolling_pf = _calc_rolling_pf(all_trades)
    zscore_data = _calc_zscore_pf(all_trades)

    # DD portfolio desde cuentas
    dd_daily_max = 0.0
    dd_total_max = 0.0
    for acc in account_list:
        dd_d, dd_t = _calc_portfolio_dd(acc)
        dd_daily_max = max(dd_daily_max, dd_d)
        dd_total_max = max(dd_total_max, dd_t)

    report["portfolio"] = {
        "dd_daily_pct": dd_daily_max,
        "dd_total_pct": dd_total_max,
        "rolling_pf_4w": rolling_pf,
        "avg_correlation_30d": avg_corr,
        "zscore_pf_monthly": zscore_data["zscore"],
        "zscore_months": zscore_data["months"],
        "active_strategies": len(strategies),
    }

    # Metricas por estrategia
    for s in strategies:
        trades = s.get("trades", [])
        days_inactive = _days_since_last_trade(trades)
        s_rolling_pf = _calc_rolling_pf(trades)
        s_zscore = _calc_zscore_pf(trades)
        report["strategies"].append({
            "id": s.get("id", "N/A"),
            "symbol": s.get("symbol", "N/A"),
            "rolling_pf_4w": s_rolling_pf,
            "days_since_trade": days_inactive,
            "zscore_pf": s_zscore["zscore"],
        })

    # Alertas
    alerts = []

    if dd_daily_max >= DD_CRITICAL:
        msg = f"PORTFOLIO: DD diario {dd_daily_max:.2f}% >= {DD_CRITICAL}%"
        alerts.append(("CRITICAL", msg))
    elif dd_daily_max >= DD_WARNING:
        msg = f"PORTFOLIO: DD diario {dd_daily_max:.2f}% >= {DD_WARNING}%"
        alerts.append(("WARNING", msg))

    if dd_total_max >= DD_CRITICAL:
        msg = f"PORTFOLIO: DD total {dd_total_max:.2f}% >= {DD_CRITICAL}%"
        alerts.append(("CRITICAL", msg))
    elif dd_total_max >= DD_WARNING:
        msg = f"PORTFOLIO: DD total {dd_total_max:.2f}% >= {DD_WARNING}%"
        alerts.append(("WARNING", msg))

    if avg_corr > CORR_PANIC:
        msg = f"MODO PANICO: correlacion media {avg_corr:.3f} > {CORR_PANIC} — reducir exposicion"
        alerts.append(("CRITICAL", msg))

    if zscore_data["zscore"] <= ZSCORE_DECAY and len(zscore_data["months"]) >= ZSCORE_WEEKS_DECAY:
        msg = f"DECAY DETECTADO: Z-Score PF {zscore_data['zscore']:.2f} <= {ZSCORE_DECAY} por {ZSCORE_WEEKS_DECAY} meses"
        alerts.append(("WARNING", msg))

    for s_data in report["strategies"]:
        if s_data["days_since_trade"] >= INACTIVITY_DAYS:
            msg = f"INACTIVIDAD: {s_data['id']} sin trades hace {s_data['days_since_trade']} dias"
            alerts.append(("WARNING", msg))

    report["alerts"] = [{"level": a[0], "message": a[1]} for a in alerts]

    # Enviar alertas
    for level, msg in alerts:
        _send_alert(level, msg, dry_run=dry_run)

    return report


def _print_report(report: dict):
    p = report["portfolio"]
    print("\n" + "=" * 60)
    print("  PORTFOLIO MONITOR — " + report["timestamp"][:19])
    print("=" * 60)
    print(f"  DD diario actual   : {p['dd_daily_pct']:.2f}%")
    print(f"  DD total actual    : {p['dd_total_pct']:.2f}%")
    print(f"  PF rolling 4 sem.  : {p['rolling_pf_4w']}")
    print(f"  Corr. media 30d    : {p['avg_correlation_30d']}")
    print(f"  Z-Score PF mensual : {p['zscore_pf_monthly']}")
    print(f"  Estrategias activas: {p['active_strategies']}")
    print("-" * 60)

    if report["strategies"]:
        print(f"  {'ID':<15} {'PF 4w':>8} {'Sin trade':>10} {'Z-Score':>8}")
        print("  " + "-" * 45)
        for s in report["strategies"]:
            print(f"  {s['id']:<15} {s['rolling_pf_4w']:>8} {s['days_since_trade']:>9}d {s['zscore_pf']:>8.2f}")

    if report["alerts"]:
        print("\n  ALERTAS:")
        for a in report["alerts"]:
            print(f"  [{a['level']}] {a['message']}")
    else:
        print("\n  Sin alertas activas.")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Portfolio Monitor — TradingLab")
    parser.add_argument("--mode", choices=["monitor", "report"], default="report",
                        help="monitor: bucle continuo | report: reporte unico")
    parser.add_argument("--interval", type=int, default=300,
                        help="Intervalo en segundos para modo monitor (default 300)")
    parser.add_argument("--dry-run", action="store_true", help="No envia Telegram")
    args = parser.parse_args()

    if args.mode == "report":
        report = generate_report(dry_run=args.dry_run)
        _print_report(report)
    else:
        print(f"Modo monitor activo. Intervalo: {args.interval}s. Ctrl+C para salir.")
        while True:
            try:
                report = generate_report(dry_run=args.dry_run)
                _print_report(report)
                time.sleep(args.interval)
            except KeyboardInterrupt:
                print("\nMonitor detenido.")
                break
            except Exception as e:
                print(f"ERROR en ciclo de monitoreo: {e}")
                time.sleep(60)


if __name__ == "__main__":
    main()
