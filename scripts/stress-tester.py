#!/usr/bin/env python3
"""
stress-tester.py — Guia el stress test historico de las 5 epocas criticas.
Lee las estrategias aprobadas por WFO y genera instrucciones + tabla de resultados.

Uso:
    python scripts/stress-tester.py
    python scripts/stress-tester.py --checklist results/wfo-checklist-2026-04-28.md
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT    = Path(__file__).parent.parent
RESULTS = ROOT / "results"

# 5 epocas criticas con fechas exactas para SQ Retester
STRESS_PERIODS = [
    {
        "id":     1,
        "nombre": "Crisis Financiera Global 2008",
        "inicio": "2007-10-01",
        "fin":    "2009-03-31",
        "evento": "Quiebra Lehman Brothers. Volatilidad extrema. Gaps masivos.",
    },
    {
        "id":     2,
        "nombre": "Flash CHF 2015",
        "inicio": "2015-01-01",
        "fin":    "2015-03-31",
        "evento": "SNB elimina el peg EUR/CHF. Pico de volatilidad en Forex.",
    },
    {
        "id":     3,
        "nombre": "COVID-19 2020",
        "inicio": "2020-02-01",
        "fin":    "2020-05-31",
        "evento": "Crash global por pandemia. Mayor volatilidad en 10 anos.",
    },
    {
        "id":     4,
        "nombre": "Inflacion y subida de tasas 2022",
        "inicio": "2022-01-01",
        "fin":    "2022-12-31",
        "evento": "Fed sube tasas agresivamente. Mercados en tendencia bajista sostenida.",
    },
    {
        "id":     5,
        "nombre": "SVB y crisis bancaria 2023",
        "inicio": "2023-02-01",
        "fin":    "2023-06-30",
        "evento": "Quiebra SVB y Signature Bank. Riesgo sistemico bancario.",
    },
]

DD_MAX_CRITERIO = 8.0
PERIODOS_MIN_PASAR = 3


def _header(text: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def find_latest_wfo_checklist() -> Path | None:
    files = sorted(RESULTS.glob("wfo-checklist-*.md"), reverse=True)
    return files[0] if files else None


def load_strategies_from_checklist(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    strategies = []
    in_section = False
    for line in text.splitlines():
        if "Estrategias que pasan al Stress Test" in line:
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
    return ["Strategy 3.1.114.sqx"]


def show_stress_config() -> None:
    print("""
  CONFIGURACION DEL STRESS TEST EN SQ
  ─────────────────────────────────────────────────────────
  Herramienta : SQ Retester (no Optimizer)
  Modo        : Standard — una estrategia por vez
  Comisiones  : Iguales que el Builder original
  Criterio    : DD < 8% en cada periodo

  Para cada periodo:
  1. Abrir SQ Retester
  2. Cargar la estrategia
  3. Cambiar las fechas al periodo del stress test
  4. Ejecutar y anotar el DD maximo y PF del periodo
""")


def show_period_instructions() -> None:
    print("\n  PERIODOS CRITICOS A TESTEAR:")
    for p in STRESS_PERIODS:
        print(f"\n  [{p['id']}] {p['nombre']}")
        print(f"       Fechas : {p['inicio']}  →  {p['fin']}")
        print(f"       Evento : {p['evento']}")
        print(f"       Criterio: DD < {DD_MAX_CRITERIO}%")


def generate_results_table(strategies: list[str], date_str: str) -> str:
    lines = [
        f"# Stress Test Results — {date_str}",
        "",
        "Rellenar tras ejecutar el Retester en cada periodo.",
        "Estado por periodo: PASA (DD < 8%) / FALLA (DD >= 8%)",
        "",
        "---",
        "",
        "## Periodos criticos",
        "",
        "| # | Periodo | Fechas | Evento |",
        "|---|---------|--------|--------|",
    ]
    for p in STRESS_PERIODS:
        lines.append(f"| {p['id']} | {p['nombre']} | {p['inicio']} → {p['fin']} | {p['evento']} |")

    lines += ["", "---", "", "## Resultados por estrategia", ""]

    for i, name in enumerate(strategies, 1):
        lines += [
            f"### [{i}] {name}",
            "",
            f"| Periodo | DD max (%) | PF periodo | Estado |",
            f"|---------|-----------|------------|--------|",
        ]
        for p in STRESS_PERIODS:
            lines.append(f"| {p['nombre']:<40} |           |            |        |")
        lines += [
            "",
            f"| **Periodos superados** | /5 |",
            f"|---|---|",
            f"| **Score final**        |    |",
            f"| **RESULTADO**          | APROBADA / FALLA |",
            "",
        ]

    lines += [
        "---",
        "",
        "## Criterios de aprobacion",
        "",
        f"- DD < {DD_MAX_CRITERIO}% en CADA periodo — criterio por periodo",
        f"- Superar al menos {PERIODOS_MIN_PASAR}/5 periodos para pasar al siguiente paso",
        f"- PF > 1.0 en al menos 3 de 5 periodos (referencia)",
        "",
        "## Estrategias que pasan al Multimarket Test",
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
        "Siguiente paso: Multimarket Test en SQ Retester, luego `portfolio-builder.py`",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Stress Tester — TradingLab")
    parser.add_argument(
        "--checklist",
        default=None,
        help="Ruta al checklist del WFO (default: mas reciente en results/)",
    )
    args = parser.parse_args()

    if args.checklist:
        checklist_path = Path(args.checklist)
    else:
        checklist_path = find_latest_wfo_checklist()

    strategies = []
    is_example = False

    if checklist_path and checklist_path.exists():
        strategies = load_strategies_from_checklist(checklist_path)
        print(f"\n  Leyendo checklist WFO: {checklist_path.name}")
        if not strategies:
            print("  No se encontraron estrategias marcadas con [x].")
            print("  Rellenar primero el checklist del WFO.")
            print("  Mostrando ejemplo.\n")
            strategies = _example_strategies()
            is_example = True
    else:
        print("\n  No se encontro checklist del WFO.")
        print("  Ejecuta primero: python scripts/wfo-helper.py")
        print("  Mostrando ejemplo para referencia.\n")
        strategies = _example_strategies()
        is_example = True

    _header("STRESS TESTER — 5 EPOCAS CRITICAS" + (" — MODO EJEMPLO" if is_example else ""))
    print(f"  Estrategias para stress test: {len(strategies)}")
    print(f"  Periodos criticos: {len(STRESS_PERIODS)}")
    print(f"  Criterio por periodo: DD < {DD_MAX_CRITERIO}%")

    show_stress_config()
    show_period_instructions()

    date_str = datetime.now().strftime("%Y-%m-%d")
    results  = generate_results_table(strategies, date_str)
    out_path = RESULTS / f"stress-test-results-{date_str}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(results, encoding="utf-8")

    print(f"\n  Tabla de resultados guardada: {out_path}")
    print(f"\n  PROXIMA ACCION:")
    print(f"  1. Ejecutar SQ Retester para cada estrategia en cada periodo")
    print(f"  2. Rellenar la tabla: {out_path.name}")
    print(f"  3. Marcar estrategias que pasan con [x]")
    print(f"  4. Cuando termines: python scripts/portfolio-builder.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
