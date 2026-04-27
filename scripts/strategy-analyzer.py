#!/usr/bin/env python3
"""
strategy-analyzer.py — Analisis detallado de estrategia desde databank SQ

Uso:
    python strategy-analyzer.py --strategy-csv strategy.csv --strategy-id B10-001
    python strategy-analyzer.py --strategy-csv strategy.csv --strategy-id B10-001 --timeframe H4

Formato CSV esperado (exportado desde SQ):
    date,pnl,balance,equity,drawdown,trades
    2015-01-05,250.50,25250.50,25250.50,0,1
    ...
"""

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent / "results"

# Swaps XAUUSD estimados por noche
SWAP_LONG_PER_LOT = -50.63
SWAP_SHORT_PER_LOT = 17.67

# Criterios EvalGate por timeframe
EVALGATE = {
    "H1": {"pf_min": 1.5, "dd_max": 7.0, "trades_min": 120, "trades_mes_min": 8,
           "wr_min": 38.0, "sharpe_min": 0.5, "dd_anno_max": 8.0,
           "pf_postswaps_ratio": 0.80, "triple_swap_max_pct": 15.0},
    "H4": {"pf_min": 1.5, "dd_max": 7.0, "trades_min": 50, "trades_mes_min": 3,
           "wr_min": 38.0, "sharpe_min": 0.5, "dd_anno_max": 8.0,
           "pf_postswaps_ratio": 0.80, "triple_swap_max_pct": 15.0},
}


def _parse_csv(path: Path) -> list[dict]:
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "date": datetime.strptime(row["date"].strip(), "%Y-%m-%d"),
                "pnl": float(row.get("pnl", 0)),
                "balance": float(row.get("balance", 0)),
                "equity": float(row.get("equity", row.get("balance", 0))),
                "drawdown": float(row.get("drawdown", 0)),
                "trades": int(row.get("trades", 0)),
            })
    return sorted(rows, key=lambda r: r["date"])


def _compute_metrics(rows: list[dict]) -> dict:
    if not rows:
        return {}

    pnls = [r["pnl"] for r in rows]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]

    gross_profit = sum(wins) if wins else 0.0
    gross_loss = abs(sum(losses)) if losses else 0.0
    pf = gross_profit / gross_loss if gross_loss > 0 else float("inf")
    wr = len(wins) / len(pnls) * 100 if pnls else 0.0
    net_profit = sum(pnls)

    # Max DD desde equity curve
    balances = [r["balance"] for r in rows]
    peak = balances[0]
    max_dd_pct = 0.0
    for b in balances:
        if b > peak:
            peak = b
        dd = (peak - b) / peak * 100 if peak > 0 else 0
        if dd > max_dd_pct:
            max_dd_pct = dd

    # Sharpe mensual
    monthly_pnl = defaultdict(float)
    for r in rows:
        key = (r["date"].year, r["date"].month)
        monthly_pnl[key] += r["pnl"]

    monthly_returns = list(monthly_pnl.values())
    if len(monthly_returns) >= 2:
        mean_r = sum(monthly_returns) / len(monthly_returns)
        std_r = math.sqrt(sum((x - mean_r) ** 2 for x in monthly_returns) / (len(monthly_returns) - 1))
        sharpe = (mean_r / std_r) * math.sqrt(12) if std_r > 0 else 0.0
    else:
        sharpe = 0.0

    # Meses positivos
    pct_positive_months = sum(1 for v in monthly_returns if v > 0) / len(monthly_returns) * 100 if monthly_returns else 0

    return {
        "total_trades": len(pnls),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": round(wr, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_loss": round(gross_loss, 2),
        "net_profit": round(net_profit, 2),
        "profit_factor": round(pf, 4),
        "max_dd_pct": round(max_dd_pct, 4),
        "sharpe": round(sharpe, 4),
        "months": len(monthly_returns),
        "pct_positive_months": round(pct_positive_months, 2),
        "monthly_pnl": {f"{k[0]}-{k[1]:02d}": round(v, 2) for k, v in sorted(monthly_pnl.items())},
    }


def _monthly_analysis(metrics: dict) -> dict:
    monthly = metrics["monthly_pnl"]
    if not monthly:
        return {}
    best_month = max(monthly.items(), key=lambda x: x[1])
    worst_month = min(monthly.items(), key=lambda x: x[1])
    return {"best_month": best_month, "worst_month": worst_month}


def _yearly_analysis(rows: list[dict]) -> dict:
    yearly: dict[int, dict] = {}
    for r in rows:
        y = r["date"].year
        if y not in yearly:
            yearly[y] = {"pnls": [], "balances": []}
        yearly[y]["pnls"].append(r["pnl"])
        yearly[y]["balances"].append(r["balance"])

    result = {}
    for y, data in sorted(yearly.items()):
        pnls = data["pnls"]
        balances = data["balances"]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]
        gp = sum(wins)
        gl = abs(sum(losses))
        pf = gp / gl if gl > 0 else float("inf")

        peak = balances[0]
        max_dd = 0.0
        for b in balances:
            if b > peak:
                peak = b
            dd = (peak - b) / peak * 100 if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd

        result[str(y)] = {
            "trades": len(pnls),
            "net_pnl": round(sum(pnls), 2),
            "pf": round(pf, 4),
            "max_dd_pct": round(max_dd, 4),
        }
    return result


def _estimate_swaps(rows: list[dict]) -> dict:
    """Estimacion de swaps XAUUSD asumiendo 0.01 lot por trade."""
    long_trades = [r for r in rows if r["pnl"] > 0]
    short_trades = [r for r in rows if r["pnl"] < 0]
    n_long = len(long_trades)
    n_short = len(short_trades)
    lot_size = 0.01

    swap_long_total = n_long * SWAP_LONG_PER_LOT * lot_size
    swap_short_total = n_short * SWAP_SHORT_PER_LOT * lot_size
    swap_total = swap_long_total + swap_short_total

    net_profit = sum(r["pnl"] for r in rows)
    gross_loss = abs(sum(r["pnl"] for r in rows if r["pnl"] < 0))
    gross_profit = sum(r["pnl"] for r in rows if r["pnl"] > 0)

    # Triple swap miercoles (aprox 3/7 del total)
    triple_swap_impact = abs(swap_total) * (3 / 7)
    triple_swap_pct = triple_swap_impact / abs(net_profit) * 100 if net_profit != 0 else 0

    # PF post-swaps
    gp_post = gross_profit + max(swap_total, 0)
    gl_post = gross_loss + abs(min(swap_total, 0))
    pf_original = gross_profit / gross_loss if gross_loss > 0 else float("inf")
    pf_post = gp_post / gl_post if gl_post > 0 else float("inf")
    pf_ratio = pf_post / pf_original if pf_original > 0 and pf_original != float("inf") else 1.0

    return {
        "n_long": n_long,
        "n_short": n_short,
        "swap_long_total": round(swap_long_total, 2),
        "swap_short_total": round(swap_short_total, 2),
        "swap_total": round(swap_total, 2),
        "triple_swap_impact": round(triple_swap_impact, 2),
        "triple_swap_pct": round(triple_swap_pct, 2),
        "pf_original": round(pf_original, 4),
        "pf_post_swaps": round(pf_post, 4),
        "pf_ratio": round(pf_ratio, 4),
    }


def _check_evalgate(metrics: dict, swap_data: dict, yearly: dict, timeframe: str) -> list[dict]:
    cfg = EVALGATE.get(timeframe, EVALGATE["H1"])
    checks = []

    def chk(name, value, threshold, ok_condition, fmt=".2f"):
        passed = ok_condition(value, threshold)
        checks.append({
            "criterio": name,
            "valor": f"{value:{fmt}}",
            "umbral": f"{threshold:{fmt}}",
            "estado": "PASA" if passed else "FALLA",
        })

    chk("PF in-sample", metrics["profit_factor"], cfg["pf_min"], lambda v, t: v >= t, ".4f")
    chk("Max DD (%)", metrics["max_dd_pct"], cfg["dd_max"], lambda v, t: v <= t)
    chk("Trades totales", metrics["total_trades"], cfg["trades_min"], lambda v, t: v >= t, "d")
    chk("Win Rate (%)", metrics["win_rate"], cfg["wr_min"], lambda v, t: v >= t)
    chk("Sharpe ratio", metrics["sharpe"], cfg["sharpe_min"], lambda v, t: v >= t, ".4f")
    chk("% meses positivos", metrics["pct_positive_months"], 65.0, lambda v, t: v >= t)

    # DD maximo anual
    max_annual_dd = max((y["max_dd_pct"] for y in yearly.values()), default=0)
    chk("DD maximo anual (%)", max_annual_dd, cfg["dd_anno_max"], lambda v, t: v <= t)

    # Triple swap
    chk("Triple swap (% beneficio)", swap_data["triple_swap_pct"], cfg["triple_swap_max_pct"],
        lambda v, t: v <= t)

    # PF post-swaps ratio
    chk("PF post-swaps ratio", swap_data["pf_ratio"], cfg["pf_postswaps_ratio"],
        lambda v, t: v >= t, ".4f")

    # Trades por mes estimado
    trades_mes = metrics["total_trades"] / metrics["months"] if metrics["months"] > 0 else 0
    chk("Trades/mes", trades_mes, cfg["trades_mes_min"], lambda v, t: v >= t, ".1f")

    return checks


def _ollama_analysis(metrics: dict, strategy_id: str) -> str:
    try:
        import urllib.request
        import json as json_mod

        prompt = (
            f"Analiza brevemente esta estrategia de trading algoritmico (ID: {strategy_id}):\n"
            f"PF={metrics['profit_factor']}, DD={metrics['max_dd_pct']}%, "
            f"Trades={metrics['total_trades']}, WR={metrics['win_rate']}%, "
            f"Sharpe={metrics['sharpe']}, Meses positivos={metrics['pct_positive_months']}%.\n"
            "Responde en 3-4 lineas: fortalezas, debilidades, y si recomendarias continuar el pipeline."
        )

        payload = json_mod.dumps({
            "model": "deepseek-r1:7b",
            "prompt": prompt,
            "stream": False
        }).encode("utf-8")

        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json_mod.loads(resp.read().decode("utf-8"))
            return data.get("response", "").strip()
    except Exception:
        return None


def _generate_report(strategy_id: str, timeframe: str, metrics: dict,
                     monthly_anal: dict, yearly: dict, swap_data: dict,
                     evalgate: list[dict], ollama_text: str | None) -> str:
    lines = [
        f"# Analisis Estrategia {strategy_id} — {timeframe}",
        "",
        "## Metricas Basicas",
        f"- Profit Factor     : {metrics['profit_factor']}",
        f"- Max DD            : {metrics['max_dd_pct']}%",
        f"- Total Trades      : {metrics['total_trades']}",
        f"- Win Rate          : {metrics['win_rate']}%",
        f"- Sharpe Ratio      : {metrics['sharpe']}",
        f"- Net Profit        : ${metrics['net_profit']:,.2f}",
        f"- Meses positivos   : {metrics['pct_positive_months']}%",
        "",
        "## Distribucion Mensual",
    ]

    for month, pnl in sorted(metrics["monthly_pnl"].items()):
        sign = "+" if pnl >= 0 else ""
        lines.append(f"- {month}: {sign}${pnl:,.2f}")

    if monthly_anal:
        lines += [
            "",
            "## Mejores/Peores Meses",
            f"- Mejor mes  : {monthly_anal['best_month'][0]} (${monthly_anal['best_month'][1]:,.2f})",
            f"- Peor mes   : {monthly_anal['worst_month'][0]} (${monthly_anal['worst_month'][1]:,.2f})",
        ]

    lines += ["", "## Analisis Anual"]
    for year, data in sorted(yearly.items()):
        lines.append(f"- {year}: PF={data['pf']}, DD={data['max_dd_pct']}%, Trades={data['trades']}, PnL=${data['net_pnl']:,.2f}")

    lines += [
        "",
        "## Estimacion Swaps XAUUSD",
        f"- Trades largos     : {swap_data['n_long']}",
        f"- Trades cortos     : {swap_data['n_short']}",
        f"- Swap total est.   : ${swap_data['swap_total']:,.2f}",
        f"- Triple swap mierc.: ${swap_data['triple_swap_impact']:,.2f} ({swap_data['triple_swap_pct']:.1f}% beneficio)",
        f"- PF original       : {swap_data['pf_original']}",
        f"- PF post-swaps     : {swap_data['pf_post_swaps']}",
        f"- Ratio PF post/pre : {swap_data['pf_ratio']}",
        "",
        "## Verificacion EvalGate",
        f"{'Criterio':<30} {'Valor':>10} {'Umbral':>10} {'Estado':>8}",
        "-" * 62,
    ]

    all_pass = True
    for c in evalgate:
        lines.append(f"{c['criterio']:<30} {c['valor']:>10} {c['umbral']:>10} {c['estado']:>8}")
        if c["estado"] == "FALLA":
            all_pass = False

    veredicto = "PASA EVALGATE" if all_pass else "FALLA EVALGATE"
    lines += ["", f"**Veredicto: {veredicto}**"]

    if ollama_text:
        lines += ["", "## Analisis Cualitativo (deepseek-r1:7b)", "", ollama_text]

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Strategy Analyzer — TradingLab")
    parser.add_argument("--strategy-csv", required=True, help="CSV exportado de SQ")
    parser.add_argument("--strategy-id", required=True, help="Identificador de la estrategia")
    parser.add_argument("--timeframe", default="H1", choices=["H1", "H4"], help="Timeframe (default H1)")
    args = parser.parse_args()

    csv_path = Path(args.strategy_csv)
    if not csv_path.exists():
        print(f"ERROR: archivo no encontrado: {csv_path}")
        sys.exit(1)

    rows = _parse_csv(csv_path)
    if not rows:
        print("ERROR: CSV vacio o formato incorrecto")
        sys.exit(1)

    metrics = _compute_metrics(rows)
    monthly_anal = _monthly_analysis(metrics)
    yearly = _yearly_analysis(rows)
    swap_data = _estimate_swaps(rows)
    evalgate = _check_evalgate(metrics, swap_data, yearly, args.timeframe)

    ollama_text = None
    try:
        import urllib.request  # noqa: F401
        ollama_text = _ollama_analysis(metrics, args.strategy_id)
        if ollama_text:
            print("Analisis cualitativo Ollama incluido.")
    except Exception:
        pass

    report = _generate_report(
        args.strategy_id, args.timeframe, metrics,
        monthly_anal, yearly, swap_data, evalgate, ollama_text
    )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / f"strategy-{args.strategy_id}-analysis.md"
    out_path.write_text(report, encoding="utf-8")

    # Print summary to stdout
    all_pass = all(c["estado"] == "PASA" for c in evalgate)
    veredicto = "PASA EVALGATE" if all_pass else "FALLA EVALGATE"
    print(f"\nEstrategia : {args.strategy_id} ({args.timeframe})")
    print(f"PF         : {metrics['profit_factor']} | DD: {metrics['max_dd_pct']}% | Trades: {metrics['total_trades']}")
    print(f"Veredicto  : {veredicto}")
    print(f"Informe    : {out_path}")


if __name__ == "__main__":
    main()
