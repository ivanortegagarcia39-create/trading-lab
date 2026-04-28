#!/usr/bin/env python3
"""
build-comparator.py — Compara dos builds para detectar mejora real

Uso:
    python scripts/build-comparator.py \\
        --build-a-folder results/build10/ --build-a-name Build10 \\
        --build-b-folder results/build11/ --build-b-name Build11

Input: carpetas con Strategy*.csv de dos builds
Output: results/build-comparison-[A]-vs-[B].md
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT       = Path(__file__).parent.parent
RESULTS    = ROOT / "results"
CONFIG     = ROOT / "config" / "pipeline-config.json"

# Criterios EvalGate H1 (fallback si no hay config)
EVALGATE_H1 = {"pf_min": 1.5, "dd_max": 7.0, "trades_min": 120, "wr_min": 38.0}


def _load_evalgate_config() -> dict:
    if CONFIG.exists():
        try:
            cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
            h1 = cfg.get("eval_gate", {}).get("H1", {})
            return {
                "pf_min":     h1.get("pf_minimo", EVALGATE_H1["pf_min"]),
                "dd_max":     h1.get("dd_maximo_pct", EVALGATE_H1["dd_max"]),
                "trades_min": h1.get("trades_minimos", EVALGATE_H1["trades_min"]),
                "wr_min":     h1.get("win_rate_minimo", EVALGATE_H1["wr_min"]),
            }
        except Exception:
            pass
    return EVALGATE_H1


def _parse_strategy_csv(path: Path) -> dict | None:
    """Extrae metricas basicas de un Strategy*.csv de SQ."""
    try:
        rows = []
        with open(path, newline="", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)

        if not rows:
            return None

        # Buscar columnas clave (SQ puede variar el nombre)
        def _col(row, *candidates):
            for c in candidates:
                for k in row:
                    if k.strip().lower() == c.lower():
                        return k
            return None

        sample = rows[0]
        col_pnl    = _col(sample, "pnl", "profit", "net profit", "NetProfit")
        col_bal    = _col(sample, "balance", "equity", "Balance")

        if not col_pnl:
            return None

        pnls = []
        balances = []
        for r in rows:
            try:
                if col_pnl:
                    pnls.append(float(r[col_pnl]))
                if col_bal:
                    balances.append(float(r[col_bal]))
            except (ValueError, KeyError):
                pass

        if not pnls:
            return None

        wins   = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]
        gp     = sum(wins)
        gl     = abs(sum(losses))
        pf     = gp / gl if gl > 0 else 0.0
        wr     = len(wins) / len(pnls) * 100 if pnls else 0.0

        # Max DD desde balance
        if balances:
            peak = balances[0]
            max_dd = 0.0
            for b in balances:
                if b > peak:
                    peak = b
                dd = (peak - b) / peak * 100 if peak > 0 else 0
                if dd > max_dd:
                    max_dd = dd
        else:
            max_dd = 0.0

        return {
            "file":   path.name,
            "trades": len(pnls),
            "pf":     round(pf, 4),
            "wr":     round(wr, 2),
            "dd":     round(max_dd, 4),
            "net":    round(sum(pnls), 2),
        }
    except Exception:
        return None


def _load_build(folder: Path) -> list[dict]:
    csvs = list(folder.glob("Strategy*.csv"))
    strategies = []
    for f in csvs:
        m = _parse_strategy_csv(f)
        if m:
            strategies.append(m)
    return strategies


def _build_stats(strategies: list[dict], cfg: dict) -> dict:
    if not strategies:
        return {
            "total":          0,
            "pf_max":         0.0,
            "pf_mean":        0.0,
            "dd_mean":        0.0,
            "evalgate_pass":  0,
            "evalgate_rate":  0.0,
        }

    pfs = [s["pf"] for s in strategies]
    dds = [s["dd"] for s in strategies]

    passing = [
        s for s in strategies
        if s["pf"] >= cfg["pf_min"]
        and s["dd"] <= cfg["dd_max"]
        and s["trades"] >= cfg["trades_min"]
        and s["wr"] >= cfg["wr_min"]
    ]

    return {
        "total":         len(strategies),
        "pf_max":        round(max(pfs), 4),
        "pf_mean":       round(sum(pfs) / len(pfs), 4),
        "dd_mean":       round(sum(dds) / len(dds), 4),
        "evalgate_pass": len(passing),
        "evalgate_rate": round(len(passing) / len(strategies) * 100, 2),
    }


def _verdict(a: dict, b: dict) -> tuple[str, list[str]]:
    """Determina que build es mejor con razonamiento."""
    score_a = score_b = 0
    reasons = []

    # PF maximo
    if a["pf_max"] > b["pf_max"] * 1.05:
        score_a += 2
        reasons.append(f"PF max: {a['pf_max']} vs {b['pf_max']} → A mejor")
    elif b["pf_max"] > a["pf_max"] * 1.05:
        score_b += 2
        reasons.append(f"PF max: {a['pf_max']} vs {b['pf_max']} → B mejor")
    else:
        reasons.append(f"PF max: {a['pf_max']} vs {b['pf_max']} → similar")

    # PF medio
    if a["pf_mean"] > b["pf_mean"] * 1.05:
        score_a += 1
        reasons.append(f"PF medio: {a['pf_mean']} vs {b['pf_mean']} → A mejor")
    elif b["pf_mean"] > a["pf_mean"] * 1.05:
        score_b += 1
        reasons.append(f"PF medio: {a['pf_mean']} vs {b['pf_mean']} → B mejor")
    else:
        reasons.append(f"PF medio: {a['pf_mean']} vs {b['pf_mean']} → similar")

    # Tasa EvalGate
    if a["evalgate_rate"] > b["evalgate_rate"] + 2:
        score_a += 2
        reasons.append(f"EvalGate rate: {a['evalgate_rate']}% vs {b['evalgate_rate']}% → A mejor")
    elif b["evalgate_rate"] > a["evalgate_rate"] + 2:
        score_b += 2
        reasons.append(f"EvalGate rate: {a['evalgate_rate']}% vs {b['evalgate_rate']}% → B mejor")
    else:
        reasons.append(f"EvalGate rate: {a['evalgate_rate']}% vs {b['evalgate_rate']}% → similar")

    # DD medio (menor es mejor)
    if b["dd_mean"] > a["dd_mean"] * 1.1:
        score_a += 1
        reasons.append(f"DD medio: {a['dd_mean']}% vs {b['dd_mean']}% → A mejor (menos DD)")
    elif a["dd_mean"] > b["dd_mean"] * 1.1:
        score_b += 1
        reasons.append(f"DD medio: {a['dd_mean']}% vs {b['dd_mean']}% → B mejor (menos DD)")
    else:
        reasons.append(f"DD medio: {a['dd_mean']}% vs {b['dd_mean']}% → similar")

    # Estrategias que pasan EvalGate (numero absoluto)
    if a["evalgate_pass"] > b["evalgate_pass"]:
        score_a += 1
        reasons.append(f"Pasan EvalGate: {a['evalgate_pass']} vs {b['evalgate_pass']} → A mejor")
    elif b["evalgate_pass"] > a["evalgate_pass"]:
        score_b += 1
        reasons.append(f"Pasan EvalGate: {a['evalgate_pass']} vs {b['evalgate_pass']} → B mejor")
    else:
        reasons.append(f"Pasan EvalGate: {a['evalgate_pass']} vs {b['evalgate_pass']} → igual")

    if score_a > score_b + 1:
        verdict = "BUILD_A_MEJOR"
    elif score_b > score_a + 1:
        verdict = "BUILD_B_MEJOR"
    else:
        verdict = "SIN_DIFERENCIA_SIGNIFICATIVA"

    return verdict, reasons


def _generate_report(name_a: str, name_b: str,
                     stats_a: dict, stats_b: dict,
                     verdict: str, reasons: list[str]) -> str:
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    def row(label, va, vb):
        mejor = ""
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            if va > vb * 1.02:
                mejor = " ← mejor"
            elif vb > va * 1.02:
                mejor = "         mejor →"
        return f"| {label:<35} | {str(va):>10} | {str(vb):>10} |{mejor}\n"

    table  = f"| {'Metrica':<35} | {name_a:>10} | {name_b:>10} |\n"
    table += f"|{'-'*37}|{'-'*12}|{'-'*12}|\n"
    table += row("Estrategias en databank",       stats_a["total"],          stats_b["total"])
    table += row("PF maximo",                     stats_a["pf_max"],         stats_b["pf_max"])
    table += row("PF medio",                      stats_a["pf_mean"],        stats_b["pf_mean"])
    table += row("DD medio (%)",                  stats_a["dd_mean"],        stats_b["dd_mean"])
    table += row("Pasan EvalGate",                stats_a["evalgate_pass"],  stats_b["evalgate_pass"])
    table += row("Tasa EvalGate (%)",             stats_a["evalgate_rate"],  stats_b["evalgate_rate"])

    reason_lines = "\n".join(f"- {r}" for r in reasons)

    return f"""# Comparacion de Builds — {name_a} vs {name_b}
Generado: {date_str}

---

## Tabla Comparativa

{table}
---

## Analisis

{reason_lines}

---

## Veredicto

**{verdict}**

---
*Generado por build-comparator.py — TradingLab*
"""


def main():
    parser = argparse.ArgumentParser(description="Build Comparator — TradingLab")
    parser.add_argument("--build-a-folder", required=True)
    parser.add_argument("--build-b-folder", required=True)
    parser.add_argument("--build-a-name", default="BuildA")
    parser.add_argument("--build-b-name", default="BuildB")
    args = parser.parse_args()

    folder_a = Path(args.build_a_folder)
    folder_b = Path(args.build_b_folder)

    for f, name in [(folder_a, args.build_a_name), (folder_b, args.build_b_name)]:
        if not f.exists():
            print(f"ERROR: carpeta no encontrada: {f}")
            sys.exit(1)

    cfg = _load_evalgate_config()

    print(f"Cargando {args.build_a_name}...")
    strats_a = _load_build(folder_a)
    print(f"  {len(strats_a)} estrategias leidas")

    print(f"Cargando {args.build_b_name}...")
    strats_b = _load_build(folder_b)
    print(f"  {len(strats_b)} estrategias leidas")

    stats_a = _build_stats(strats_a, cfg)
    stats_b = _build_stats(strats_b, cfg)
    verdict, reasons = _verdict(stats_a, stats_b)

    report = _generate_report(args.build_a_name, args.build_b_name,
                              stats_a, stats_b, verdict, reasons)

    RESULTS.mkdir(parents=True, exist_ok=True)
    slug_a = args.build_a_name.replace(" ", "")
    slug_b = args.build_b_name.replace(" ", "")
    out_path = RESULTS / f"build-comparison-{slug_a}-vs-{slug_b}.md"
    out_path.write_text(report, encoding="utf-8")

    print(f"\nVeredicto  : {verdict}")
    print(f"Informe    : {out_path}")


if __name__ == "__main__":
    main()
