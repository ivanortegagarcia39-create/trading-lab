#!/usr/bin/env python3
"""
retester-helper.py — Guia el proceso del Retester en SQ tras el EvalGate.
Lee las estrategias aprobadas y genera instrucciones + checklist de resultados.

Uso:
    python scripts/retester-helper.py
    python scripts/retester-helper.py --eval-results results/evaluation-gate-results.json
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT    = Path(__file__).parent.parent
RESULTS = ROOT / "results"

# Fechas IS / OOS del pipeline
IS_START  = "2003-01-01"
IS_END    = "2020-12-31"
OOS_START = "2021-01-01"
OOS_END   = "2026-04-01"

# Criterios Paso 12b (de config/pipeline-config.json)
CRITERIA_12B = {
    "pf_oos_minimo":          1.3,
    "caida_pf_maxima_pct":    20,
    "dd_oos_maximo":          6.5,
    "trades_mes_oos_minimo":  6,
}

VETO_12B = {
    "pf_oos_veto":            1.2,
    "caida_pf_veto_pct":      25,
    "dd_oos_veto":            7.0,
    "trades_mes_oos_veto":    5,
}


def _header(text: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def load_eval_results(path: Path) -> dict:
    if not path.exists():
        print(f"\n  AVISO: {path} no encontrado.")
        print("  Ejecuta primero el EvalGate:")
        print("  python scripts/evaluator-assistant.py --results-folder results/")
        print()
        print("  Mostrando ejemplo con datos ficticios para referencia.\n")
        return _example_results()
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  ERROR al leer {path}: {e}")
        return {}


def _example_results() -> dict:
    return {
        "timestamp": datetime.now().isoformat(),
        "total": 5,
        "pasan": 2,
        "passed": [
            {"metrics": {"file": "Strategy 3.1.114.sqx", "pf": 1.72, "dd": 5.1,
                         "trades": 187, "wr": 41.2, "sharpe": 0.82}},
            {"metrics": {"file": "Strategy 2.15.153.sqx", "pf": 1.58, "dd": 6.3,
                         "trades": 142, "wr": 38.7, "sharpe": 0.67}},
        ],
        "_ejemplo": True,
    }


def show_retester_config() -> None:
    print("""
  CONFIGURACION DEL RETESTER EN SQ
  ─────────────────────────────────────────────────────────
  Datos IS   : {IS_START} → {IS_END}
  Datos OOS  : {OOS_START} → {OOS_END}
  Monte Carlo: SI — 200 simulaciones, 95% confianza
  Modo       : Standard Retester (no Optimizer)
  Comisiones : Iguales que el Builder (no cambiar)
  Posiciones : Iguales que el Builder (no cambiar)

  IMPORTANTE:
  • Cargar las estrategias aprobadas del databank
  • NO modificar parametros antes del Retester
  • Monte Carlo OBLIGATORIO en esta fase
  • Anotar los resultados OOS en el checklist
""".format(IS_START=IS_START, IS_END=IS_END,
           OOS_START=OOS_START, OOS_END=OOS_END))


def show_strategy_instructions(idx: int, metrics: dict) -> None:
    fname = metrics.get("file", f"Estrategia_{idx}")
    pf_is = metrics.get("pf", "?")
    dd_is = metrics.get("dd", "?")
    trades = metrics.get("trades", "?")
    wr = metrics.get("wr", "?")

    # El .sqx puede tener el mismo nombre sin extension .sqx o con ella
    sqx_name = fname if fname.endswith(".sqx") else fname.replace(".csv", ".sqx")

    print(f"\n  [{idx}] {sqx_name}")
    print(f"       PF IS: {pf_is} | DD IS: {dd_is}% | Trades: {trades} | WR: {wr}%")
    print(f"       → Cargar en Retester: buscar '{sqx_name}' en el databank")
    print(f"       → PF OOS esperado: ≥ {CRITERIA_12B['pf_oos_minimo']} "
          f"(IS: {pf_is} → max caida {CRITERIA_12B['caida_pf_maxima_pct']}%)")


def show_paso12b_criteria() -> None:
    print(f"""
  CRITERIOS PASO 12b — verificar tras el Retester
  ─────────────────────────────────────────────────────────
  APROBACION (todos deben cumplirse):
    PF OOS          ≥ {CRITERIA_12B['pf_oos_minimo']}
    Caida PF IS→OOS ≤ {CRITERIA_12B['caida_pf_maxima_pct']}%
    DD OOS          ≤ {CRITERIA_12B['dd_oos_maximo']}%
    Trades/mes OOS  ≥ {CRITERIA_12B['trades_mes_oos_minimo']}

  VETO AUTOMATICO (cualquiera → descartar):
    PF OOS          < {VETO_12B['pf_oos_veto']}
    Caida PF IS→OOS > {VETO_12B['caida_pf_veto_pct']}%
    DD OOS          > {VETO_12B['dd_oos_veto']}%
    Trades/mes OOS  < {VETO_12B['trades_mes_oos_veto']}
""")


def generate_checklist(strategies: list, date_str: str) -> str:
    lines = [
        f"# Checklist Retester — {date_str}",
        "",
        "Rellenar tras ejecutar el Retester en SQ.",
        "Estado: PASA / FALLA / VETO",
        "",
        "---",
        "",
        "## Resultados por estrategia",
        "",
        "| # | Estrategia | PF IS | PF OOS | Caida % | DD OOS | Trades/mes | MC 95% | Estado |",
        "|---|------------|-------|--------|---------|--------|-----------|--------|--------|",
    ]
    for i, s in enumerate(strategies, 1):
        m = s["metrics"]
        fname = m.get("file", f"estrategia_{i}")
        pf_is = m.get("pf", "?")
        lines.append(f"| {i} | {fname} | {pf_is} | | | | | | |")

    lines += [
        "",
        "---",
        "",
        "## Criterios de referencia",
        "",
        f"- PF OOS ≥ {CRITERIA_12B['pf_oos_minimo']}",
        f"- Caida PF IS→OOS ≤ {CRITERIA_12B['caida_pf_maxima_pct']}%",
        f"- DD OOS ≤ {CRITERIA_12B['dd_oos_maximo']}%",
        f"- Trades/mes OOS ≥ {CRITERIA_12B['trades_mes_oos_minimo']}",
        "",
        "## Estrategias que pasan al WFO",
        "",
        "_(Rellenar tras revisar los resultados)_",
        "",
    ]
    for i, s in enumerate(strategies, 1):
        m = s["metrics"]
        fname = m.get("file", f"estrategia_{i}")
        lines.append(f"- [ ] {fname}")

    lines += [
        "",
        "---",
        "",
        f"Generado: {date_str}",
        "Siguiente paso: `python scripts/wfo-helper.py`",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Retester Helper — TradingLab")
    parser.add_argument(
        "--eval-results",
        default=str(RESULTS / "evaluation-gate-results.json"),
        help="Ruta al archivo de resultados del EvalGate",
    )
    args = parser.parse_args()

    eval_path = Path(args.eval_results)
    data = load_eval_results(eval_path)
    if not data:
        return 1

    passed = data.get("passed", [])
    total  = data.get("total", 0)
    is_example = data.get("_ejemplo", False)

    _header("RETESTER HELPER" + (" — MODO EJEMPLO" if is_example else ""))
    print(f"  EvalGate: {len(passed)} / {total} estrategias aprobadas")
    if not passed:
        print("\n  Sin estrategias aprobadas. Revisar resultados del EvalGate.")
        return 0

    # Configuracion del Retester
    show_retester_config()

    # Instrucciones por estrategia
    print("  ESTRATEGIAS A CARGAR EN EL RETESTER:")
    for i, s in enumerate(passed, 1):
        show_strategy_instructions(i, s["metrics"])

    # Criterios paso 12b
    show_paso12b_criteria()

    # Generar checklist
    date_str  = datetime.now().strftime("%Y-%m-%d")
    checklist = generate_checklist(passed, date_str)
    out_path  = RESULTS / f"retester-checklist-{date_str}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(checklist, encoding="utf-8")

    print(f"\n  Checklist guardado: {out_path}")
    print(f"\n  PROXIMA ACCION:")
    print(f"  1. Ejecutar Retester en SQ con las {len(passed)} estrategias")
    print(f"  2. Rellenar checklist: {out_path.name}")
    print(f"  3. Cuando termines: python scripts/wfo-helper.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
