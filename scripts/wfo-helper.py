#!/usr/bin/env python3
"""
wfo-helper.py — Guia el proceso WFO en SQ tras el Retester.
Lee las estrategias que pasan el Paso 12b y genera instrucciones WFO.

Uso:
    python scripts/wfo-helper.py
    python scripts/wfo-helper.py --checklist results/retester-checklist-2026-04-28.md
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT    = Path(__file__).parent.parent
RESULTS = ROOT / "results"

# Criterios WFO (de config/pipeline-config.json)
CRITERIA_WFO = {
    "wfe_minimo":             50,
    "ventanas_pf_min_09":     0,
    "dd_oos_maximo":          7.0,
    "pf_oos_ultima_min":      1.1,
    "pf_oos_promedio_min":    1.25,
    "params_desviacion_max":  25,
}

VETO_WFO = {
    "wfe_veto":               40,
    "catastrophic_veto_pf":   0.8,
    "catastrophic_veto_dd":   10,
    "ventanas_negativas_consec": 2,
}


def _header(text: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def find_latest_checklist() -> Path | None:
    files = sorted(RESULTS.glob("retester-checklist-*.md"), reverse=True)
    return files[0] if files else None


def load_strategies_from_checklist(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    strategies = []
    in_section = False
    for line in text.splitlines():
        if "Estrategias que pasan al WFO" in line:
            in_section = True
            continue
        if in_section:
            if line.startswith("## ") and strategies:
                break
            m = re.match(r"- \[x\] (.+)", line, re.IGNORECASE)
            if m:
                strategies.append(m.group(1).strip())
    return strategies


def _example_strategies() -> list[str]:
    return ["Strategy 3.1.114.sqx", "Strategy 2.15.153.sqx"]


def show_wfo_config() -> None:
    print("""
  CONFIGURACION WFO EN SQ — SQ Optimizer → Walk Forward
  ─────────────────────────────────────────────────────────
  Modo          : Walk Forward Matrix
  IS split      : 70%
  OOS split     : 30%
  Ventanas      : 5
  Anchored WFO  : NO (ventanas deslizantes)
  WF Matrix     : ACTIVADO
  Catastrophic Veto : ACTIVADO

  Datos         : 2003-01-01 → 2026-04-01 (completo)
  Generaciones  : 20 por ventana
  Parametros    : Mismo rango que el Builder original

  IMPORTANTE:
  • Usar los mismos datos que el Builder — NO datos nuevos
  • NO cambiar el rango de parametros
  • Guardar resultados de cada ventana
""")


def show_strategy_instructions(idx: int, name: str) -> None:
    print(f"\n  [{idx}] {name}")
    print(f"       → Cargar en SQ Optimizer: buscar '{name}' en el databank")
    print(f"       → Configurar WFO segun parametros arriba")
    print(f"       → Anotar: WFE%, PF OOS de cada ventana, DD OOS max")


def show_wfo_criteria() -> None:
    print(f"""
  CRITERIOS DE APROBACION WFO
  ─────────────────────────────────────────────────────────
  APROBACION FINAL (todos deben cumplirse):
    WFE                    ≥ {CRITERIA_WFO['wfe_minimo']}%
    Ventanas con PF < 0.9  = {CRITERIA_WFO['ventanas_pf_min_09']} (ninguna)
    DD OOS max             ≤ {CRITERIA_WFO['dd_oos_maximo']}% en todas las ventanas
    PF OOS ultima ventana  ≥ {CRITERIA_WFO['pf_oos_ultima_min']}
    PF OOS promedio        ≥ {CRITERIA_WFO['pf_oos_promedio_min']}
    Desviacion parametros  < {CRITERIA_WFO['params_desviacion_max']}%

  VETO AUTOMATICO (cualquiera → descartar):
    WFE                    < {VETO_WFO['wfe_veto']}%
    Ventanas PF            < {VETO_WFO['catastrophic_veto_pf']} (Catastrophic Veto)
    Ventanas negativas consec ≥ {VETO_WFO['ventanas_negativas_consec']}
    DD OOS                 > {VETO_WFO['catastrophic_veto_dd']}% en cualquier ventana
""")


def generate_checklist(strategies: list[str], date_str: str) -> str:
    ventanas = ["V1", "V2", "V3", "V4", "V5"]
    lines = [
        f"# Checklist WFO — {date_str}",
        "",
        "Rellenar tras ejecutar el WFO en SQ.",
        "Estado: APROBADA / VETO / FALLA",
        "",
        "---",
        "",
        "## Resultados WFO por estrategia",
        "",
    ]
    for i, name in enumerate(strategies, 1):
        lines += [
            f"### [{i}] {name}",
            "",
            f"| Ventana | PF OOS | DD OOS | Estado |",
            f"|---------|--------|--------|--------|",
        ]
        for v in ventanas:
            lines.append(f"| {v}     |        |        |        |")
        lines += [
            "",
            f"| Metrica | Valor |",
            f"|---------|-------|",
            f"| WFE (%)             |       |",
            f"| PF OOS promedio     |       |",
            f"| PF OOS ultima vent. |       |",
            f"| DD OOS maximo       |       |",
            f"| Desviacion params   |       |",
            f"| Catastrophic Veto   |       |",
            f"| **RESULTADO**       |       |",
            "",
        ]

    lines += [
        "---",
        "",
        "## Criterios de referencia",
        "",
        f"- WFE ≥ {CRITERIA_WFO['wfe_minimo']}%",
        f"- Ninguna ventana PF < 0.9",
        f"- DD OOS ≤ {CRITERIA_WFO['dd_oos_maximo']}% en todas las ventanas",
        f"- PF OOS ultima ventana ≥ {CRITERIA_WFO['pf_oos_ultima_min']}",
        f"- PF OOS promedio ≥ {CRITERIA_WFO['pf_oos_promedio_min']}",
        "",
        "## Estrategias que pasan al Stress Test",
        "",
        "_(Marcar con [x] las aprobadas)_",
        "",
    ]
    for name in strategies:
        lines.append(f"- [ ] {name}")

    lines += [
        "",
        "---",
        "",
        f"Generado: {date_str}",
        "Siguiente paso: `python scripts/stress-tester.py`",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="WFO Helper — TradingLab")
    parser.add_argument(
        "--checklist",
        default=None,
        help="Ruta al checklist del Retester (default: mas reciente en results/)",
    )
    args = parser.parse_args()

    if args.checklist:
        checklist_path = Path(args.checklist)
    else:
        checklist_path = find_latest_checklist()

    strategies = []
    is_example = False

    if checklist_path and checklist_path.exists():
        strategies = load_strategies_from_checklist(checklist_path)
        print(f"\n  Leyendo checklist: {checklist_path.name}")
        if not strategies:
            print("  No se encontraron estrategias marcadas con [x] en el checklist.")
            print("  Rellenar primero el checklist del Retester.")
            print("  Mostrando ejemplo.\n")
            strategies = _example_strategies()
            is_example = True
    else:
        print("\n  No se encontro checklist del Retester.")
        print("  Ejecuta primero: python scripts/retester-helper.py")
        print("  Mostrando ejemplo para referencia.\n")
        strategies = _example_strategies()
        is_example = True

    _header("WFO HELPER" + (" — MODO EJEMPLO" if is_example else ""))
    print(f"  Estrategias para WFO: {len(strategies)}")

    show_wfo_config()

    print("  ESTRATEGIAS A CARGAR EN EL WFO:")
    for i, name in enumerate(strategies, 1):
        show_strategy_instructions(i, name)

    show_wfo_criteria()

    date_str  = datetime.now().strftime("%Y-%m-%d")
    checklist = generate_checklist(strategies, date_str)
    out_path  = RESULTS / f"wfo-checklist-{date_str}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(checklist, encoding="utf-8")

    print(f"\n  Checklist WFO guardado: {out_path}")
    print(f"\n  PROXIMA ACCION:")
    print(f"  1. Ejecutar WFO en SQ con las {len(strategies)} estrategias")
    print(f"  2. Rellenar checklist: {out_path.name}")
    print(f"  3. Cuando termines: python scripts/stress-tester.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
