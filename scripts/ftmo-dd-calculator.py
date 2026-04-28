#!/usr/bin/env python3
"""
ftmo-dd-calculator.py — Simulacion del DD diario y total FTMO 2-Step

Uso:
    python ftmo-dd-calculator.py --trades-csv trades.csv --capital 25000 --mode simulate
    python ftmo-dd-calculator.py --trades-csv trades.csv --mode verify

Formato CSV de trades:
    timestamp,pnl
    2026-01-05 14:30:00,250.50
    2026-01-05 16:00:00,-120.00
"""

import argparse
import csv
import sys
from datetime import datetime, date
from pathlib import Path

try:
    import pytz
except ImportError:
    print("ERROR: pytz no instalado. Ejecuta: pip install pytz")
    sys.exit(1)

PRAGUE_TZ = pytz.timezone("Europe/Prague")
DAILY_DD_LIMIT = 0.05   # 5% dinamico
TOTAL_DD_LIMIT = 0.10   # 10% dinamico trailing


def calculate_daily_dd(balance_at_midnight: float, current_equity: float) -> dict:
    """DD diario respecto al balance de la medianoche anterior."""
    dd_usd = balance_at_midnight - current_equity
    dd_pct = dd_usd / balance_at_midnight * 100
    limit_usd = balance_at_midnight * DAILY_DD_LIMIT
    limit_equity = balance_at_midnight - limit_usd
    alert = current_equity < limit_equity

    return {
        "balance_midnight": balance_at_midnight,
        "current_equity": current_equity,
        "dd_usd": round(dd_usd, 2),
        "dd_pct": round(dd_pct, 4),
        "limit_usd": round(limit_usd, 2),
        "limit_equity": round(limit_equity, 2),
        "alert": alert,
        "alert_msg": f"ALERTA: equity {current_equity:.2f} < limite {limit_equity:.2f} ({DAILY_DD_LIMIT*100}% DD diario)" if alert else "OK",
    }


def calculate_total_dd(peak_equity: float, current_equity: float) -> dict:
    """DD total dinamico trailing respecto al pico de equity."""
    dd_usd = peak_equity - current_equity
    dd_pct = dd_usd / peak_equity * 100
    limit_usd = peak_equity * TOTAL_DD_LIMIT
    limit_equity = peak_equity - limit_usd
    alert = current_equity < limit_equity

    return {
        "peak_equity": peak_equity,
        "current_equity": current_equity,
        "dd_usd": round(dd_usd, 2),
        "dd_pct": round(dd_pct, 4),
        "limit_usd": round(limit_usd, 2),
        "limit_equity": round(limit_equity, 2),
        "alert": alert,
        "alert_msg": f"ALERTA: equity {current_equity:.2f} < limite {limit_equity:.2f} ({TOTAL_DD_LIMIT*100}% DD total)" if alert else "OK",
    }


def _parse_trades_csv(csv_path: Path) -> list[dict]:
    trades = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts_raw = row["timestamp"].strip()
            # Intentar varios formatos
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
                try:
                    dt_naive = datetime.strptime(ts_raw, fmt)
                    break
                except ValueError:
                    continue
            else:
                print(f"ERROR: timestamp no reconocido: {ts_raw}")
                sys.exit(1)
            # Asumir UTC y convertir a Prague
            dt_utc = pytz.utc.localize(dt_naive)
            dt_prague = dt_utc.astimezone(PRAGUE_TZ)
            trades.append({"dt_prague": dt_prague, "pnl": float(row["pnl"].strip())})
    return sorted(trades, key=lambda t: t["dt_prague"])


def simulate_challenge(trades_list: list[dict], initial_capital: float) -> dict:
    """
    Simula un challenge FTMO completo.
    trades_list: lista de dicts con keys dt_prague (datetime) y pnl (float)
    Devuelve: equity_curve, daily_dd, max_total_dd, trading_days, result
    """
    equity = initial_capital
    peak_equity = initial_capital
    equity_curve = [{"date": None, "equity": equity, "trade": 0, "pnl": 0.0}]

    # Agrupar por dia Prague
    days: dict[date, list[dict]] = {}
    for t in trades_list:
        d = t["dt_prague"].date()
        days.setdefault(d, []).append(t)

    daily_dd_report = []
    max_total_dd_pct = 0.0
    trading_days = 0
    eliminated = False
    elimination_reason = ""

    sorted_days = sorted(days.keys())
    balance_at_midnight = initial_capital

    for day in sorted_days:
        day_trades = days[day]
        trading_days += 1
        day_min_equity = equity

        for t in day_trades:
            equity += t["pnl"]
            if equity < day_min_equity:
                day_min_equity = equity
            if equity > peak_equity:
                peak_equity = equity
            equity_curve.append({
                "date": t["dt_prague"].strftime("%Y-%m-%d %H:%M"),
                "equity": round(equity, 2),
                "pnl": t["pnl"],
                "trade": 1,
            })

        # DD diario: usando el minimo intraday
        daily = calculate_daily_dd(balance_at_midnight, day_min_equity)
        # DD total: usando el minimo intraday
        total = calculate_total_dd(peak_equity, day_min_equity)

        total_dd_pct = total["dd_pct"]
        if total_dd_pct > max_total_dd_pct:
            max_total_dd_pct = total_dd_pct

        daily_dd_report.append({
            "day": str(day),
            "balance_midnight": balance_at_midnight,
            "equity_close": round(equity, 2),
            "min_equity_intraday": round(day_min_equity, 2),
            "daily_dd_pct": daily["dd_pct"],
            "daily_dd_alert": daily["alert"],
            "total_dd_pct": round(total_dd_pct, 4),
            "peak_equity": round(peak_equity, 2),
        })

        if daily["alert"] and not eliminated:
            eliminated = True
            elimination_reason = f"VIOLA DD DIARIO el {day}: equity minima {day_min_equity:.2f} < limite {daily['limit_equity']:.2f}"

        if total["alert"] and not eliminated:
            eliminated = True
            elimination_reason = f"VIOLA DD TOTAL el {day}: equity minima {day_min_equity:.2f} < limite {total['limit_equity']:.2f}"

        # El balance de medianoche del dia siguiente es el equity al cierre
        balance_at_midnight = equity

    profit_pct = (equity - initial_capital) / initial_capital * 100
    target_reached = profit_pct >= 10.0
    min_days_ok = trading_days >= 4

    if eliminated:
        result = "FALLA"
        reason = elimination_reason
    elif not min_days_ok:
        result = "FALLA"
        reason = f"Dias de trading insuficientes: {trading_days} < 4"
    elif not target_reached:
        result = "EN PROGRESO"
        reason = f"Beneficio {profit_pct:.2f}% — objetivo 10% no alcanzado aun"
    else:
        result = "PASA"
        reason = f"Beneficio {profit_pct:.2f}% >= 10%, {trading_days} dias de trading, DD max {max_total_dd_pct:.2f}%"

    return {
        "initial_capital": initial_capital,
        "final_equity": round(equity, 2),
        "profit_usd": round(equity - initial_capital, 2),
        "profit_pct": round(profit_pct, 4),
        "peak_equity": round(peak_equity, 2),
        "max_total_dd_pct": round(max_total_dd_pct, 4),
        "trading_days": trading_days,
        "total_trades": len(trades_list),
        "result": result,
        "reason": reason,
        "equity_curve": equity_curve,
        "daily_dd": daily_dd_report,
    }


def _print_simulation_report(sim: dict):
    print("\n" + "=" * 55)
    print("  SIMULACION CHALLENGE FTMO 2-Step")
    print("=" * 55)
    print(f"  Capital inicial : ${sim['initial_capital']:,.2f}")
    print(f"  Equity final    : ${sim['final_equity']:,.2f}")
    print(f"  Beneficio       : ${sim['profit_usd']:,.2f} ({sim['profit_pct']:.2f}%)")
    print(f"  Pico equity     : ${sim['peak_equity']:,.2f}")
    print(f"  DD total maximo : {sim['max_total_dd_pct']:.2f}%")
    print(f"  Dias trading    : {sim['trading_days']}")
    print(f"  Trades totales  : {sim['total_trades']}")
    print("-" * 55)
    print(f"  RESULTADO       : {sim['result']}")
    print(f"  Razon           : {sim['reason']}")
    print("=" * 55)

    print("\nDD DIARIO POR DIA:")
    print(f"  {'Dia':<12} {'Bal.Midnight':>13} {'Eq.Min.':>10} {'DD%':>7} {'Alert':>6}")
    print("  " + "-" * 52)
    for d in sim["daily_dd"]:
        alert_str = "VIOLA" if d["daily_dd_alert"] else "OK"
        print(f"  {d['day']:<12} {d['balance_midnight']:>13,.2f} {d['min_equity_intraday']:>10,.2f} {d['daily_dd_pct']:>6.2f}% {alert_str:>6}")


def main():
    parser = argparse.ArgumentParser(description="FTMO DD Calculator — TradingLab")
    parser.add_argument("--trades-csv", required=True, help="CSV con columnas timestamp,pnl")
    parser.add_argument("--capital", type=float, default=25000, help="Capital inicial (default 25000)")
    parser.add_argument("--mode", choices=["simulate", "verify"], default="simulate",
                        help="simulate: simulacion completa | verify: verificacion rapida de DD actual")
    args = parser.parse_args()

    csv_path = Path(args.trades_csv)
    if not csv_path.exists():
        print(f"ERROR: archivo no encontrado: {csv_path}")
        sys.exit(1)

    trades = _parse_trades_csv(csv_path)
    if not trades:
        print("ERROR: no se encontraron trades en el CSV")
        sys.exit(1)

    if args.mode == "simulate":
        sim = simulate_challenge(trades, args.capital)
        _print_simulation_report(sim)

    elif args.mode == "verify":
        # Verificacion rapida: calcula DD actual desde inicio
        equity = args.capital
        peak_equity = args.capital
        for t in trades:
            equity += t["pnl"]
            if equity > peak_equity:
                peak_equity = equity

        # DD total actual
        total = calculate_total_dd(peak_equity, equity)
        print(f"\nVerificacion DD actual:")
        print(f"  Capital inicial : ${args.capital:,.2f}")
        print(f"  Equity actual   : ${equity:,.2f}")
        print(f"  Pico equity     : ${peak_equity:,.2f}")
        print(f"  DD total actual : {total['dd_pct']:.2f}% (${total['dd_usd']:,.2f})")
        print(f"  Limite equity   : ${total['limit_equity']:,.2f}")
        print(f"  Estado          : {total['alert_msg']}")


if __name__ == "__main__":
    main()
