#!/usr/bin/env python3
"""
evaluator-assistant.py — Evaluation Gate automatico post-build

Aplica los filtros del EvalGate sobre Strategy*.csv del databank de SQ.
Filtros que SQ Build 143 no tiene disponibles en su interfaz.

Uso:
    python evaluator-assistant.py --results-folder results/ --timeframe H1
    python evaluator-assistant.py --results-folder results/ --output results/gate.json
"""

import argparse
import csv
import glob
import json
import sys
from datetime import datetime
from pathlib import Path

# Umbrales por timeframe
THRESHOLDS = {
    "H1":  {"min_trades": 120, "trades_per_month": 8},
    "H4":  {"min_trades": 50,  "trades_per_month": 3},
    "M30": {"min_trades": 180, "trades_per_month": 15},
    "M15": {"min_trades": 300, "trades_per_month": 25},
}

# Umbrales globales (skill-evaluation-auto.md)
GLOBAL = {
    "min_win_rate":          38.0,
    "max_drawdown":           7.0,
    "min_sharpe":             0.5,
    "max_dd_per_year":        8.0,
    "max_neg_years_pct":     35.0,
    "max_single_month_pct":  45.0,
}

# Aliases de columnas para distintas versiones de SQ
COLUMN_ALIASES = {
    "pf":     ["Profit Factor", "ProfitFactor", "PF", "Profit factor (IS)", "Profit factor (OOS)"],
    "dd":     ["Max DD", "MaxDD", "Max Drawdown", "MaxDrawdown", "DrawDown", "Max. Drawdown (IS)", "Max. Drawdown (OOS)"],
    "trades": ["Total Trades", "TotalTrades", "Trades", "# Trades", "# of trades (IS)", "# of trades (OOS)"],
    "wr":     ["Win Rate", "WinRate", "Win%", "Percent Profitable", "Win rate (IS)", "Win rate (OOS)"],
    "sharpe": ["Sharpe Ratio", "SharpeRatio", "Sharpe", "Sharpe Ratio (IS)", "Sharpe Ratio (OOS)"],
    "net":    ["Net Profit", "NetProfit", "Profit", "Total Net Profit", "Net profit (IS)", "Net profit (OOS)"],
    "name":   ["Strategy Name", "Name", "Strategy"],
}


def find_column(headers, aliases):
    for alias in aliases:
        for h in headers:
            if alias.lower() == h.strip().lower():
                return h.strip()
    return None


def parse_float(val):
    if val is None or str(val).strip() in ("", "N/A", "-", "n/a"):
        return None
    try:
        return float(str(val).replace(",", ".").replace("%", "").strip())
    except ValueError:
        return None


def detect_timeframe(filepath, fallback="H1"):
    name = Path(filepath).stem.upper()
    for tf in ["H4", "H1", "M30", "M15"]:
        if tf in name:
            return tf
    return fallback


def load_csv(filepath):
    """Intenta semicolon y luego coma como delimitador."""
    for delim in (";", ","):
        try:
            with open(filepath, encoding="utf-8-sig", errors="replace") as f:
                reader = csv.DictReader(f, delimiter=delim)
                rows = list(reader)
                if rows and len(rows[0]) > 3:
                    return rows
        except Exception:
            continue
    return []


def evaluate_row(row, tf, filepath):
    thresholds = THRESHOLDS.get(tf, THRESHOLDS["H1"])
    headers = list(row.keys())

    def get(key):
        col = find_column(headers, COLUMN_ALIASES.get(key, [key]))
        return parse_float(row.get(col)) if col else None

    pf     = get("pf")
    dd     = get("dd")
    trades = get("trades")
    wr     = get("wr")
    sharpe = get("sharpe")

    # Sharpe estimado si no esta disponible directamente
    if sharpe is None and pf is not None:
        sharpe = round((pf - 1.0) * 0.8, 3)  # aproximacion conservadora

    metrics = {
        "file":      Path(filepath).name,
        "timeframe": tf,
        "pf":        pf,
        "dd":        dd,
        "trades":    trades,
        "wr":        wr,
        "sharpe":    sharpe,
    }

    reasons = []

    # Filtro 1: Trades minimos por timeframe
    if trades is None or trades < thresholds["min_trades"]:
        reasons.append(
            f"Trades {trades} < {thresholds['min_trades']} minimos para {tf}"
        )

    # Filtro 2: Win Rate
    if wr is None or wr < GLOBAL["min_win_rate"]:
        reasons.append(f"Win Rate {wr}% < {GLOBAL['min_win_rate']}%")

    # Filtro 3: Max Drawdown
    if dd is None or dd > GLOBAL["max_drawdown"]:
        reasons.append(f"DD {dd}% > {GLOBAL['max_drawdown']}%")

    # Filtro 4: Sharpe estimado
    if sharpe is None or sharpe < GLOBAL["min_sharpe"]:
        reasons.append(f"Sharpe {sharpe} < {GLOBAL['min_sharpe']}")

    return metrics, reasons


def main():
    parser = argparse.ArgumentParser(
        description="Evaluation Gate automatico — aplica filtros sobre CSVs de SQ"
    )
    parser.add_argument(
        "--results-folder", default="results",
        help="Carpeta con los Strategy*.csv (default: results/)"
    )
    parser.add_argument(
        "--timeframe", default="H1", choices=["H1", "H4", "M30", "M15"],
        help="Timeframe del build (default: H1)"
    )
    parser.add_argument(
        "--output", default="results/evaluation-gate-results.json",
        help="Ruta del JSON de salida"
    )
    args = parser.parse_args()

    folder = Path(args.results_folder)
    csv_files = sorted(glob.glob(str(folder / "Strategy*.csv")))
    if not csv_files:
        csv_files = sorted(glob.glob(str(folder / "**" / "Strategy*.csv"), recursive=True))

    if not csv_files:
        print(f"[WARN] No se encontraron Strategy*.csv en {folder}")
        sys.exit(0)

    passed    = []
    discarded = []

    for filepath in csv_files:
        tf   = detect_timeframe(filepath, args.timeframe)
        rows = load_csv(filepath)
        if not rows:
            continue
        for row in rows:
            metrics, reasons = evaluate_row(row, tf, filepath)
            if reasons:
                discarded.append({
                    "metrics": metrics,
                    "criterio": "; ".join(reasons)
                })
            else:
                passed.append({"metrics": metrics})

    total = len(passed) + len(discarded)
    pct   = round(len(passed) / total * 100, 1) if total else 0.0

    output = {
        "timestamp":           datetime.utcnow().isoformat() + "Z",
        "timeframe":           args.timeframe,
        "total":               total,
        "pasan":               len(passed),
        "descartan":           len(discarded),
        "tasa_aprobacion_pct": pct,
        "passed":              passed,
        "discarded":           discarded,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Resumen en consola
    print(f"\n{'='*40}")
    print(f"EVALUATION GATE — {args.timeframe}")
    print(f"{'='*40}")
    print(f"Total evaluadas:  {total}")
    print(f"PASAN:            {len(passed)} ({pct}%)")
    print(f"DESCARTAN:        {len(discarded)}")
    print(f"Guardado en:      {out_path}")

    if passed:
        print("\nEstrategias que PASAN:")
        for s in passed:
            m = s["metrics"]
            print(
                f"  {m['file']:<40} "
                f"PF {m['pf']:<5} | DD {m['dd']}% | "
                f"Trades {m['trades']} | WR {m['wr']}% | Sharpe {m['sharpe']}"
            )

    if discarded and len(discarded) <= 10:
        print("\nPrimeras descartadas:")
        for s in discarded[:10]:
            m = s["metrics"]
            print(f"  {m['file']:<40} → {s['criterio']}")


if __name__ == "__main__":
    main()
