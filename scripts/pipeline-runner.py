#!/usr/bin/env python3
"""
pipeline-runner.py — Coordina el pipeline completo post-build

Un solo comando ejecuta todo el pipeline de evaluacion despues
de que SQ termina un build.

Flujo:
  evaluator-assistant.py → portfolio-builder.py →
  build-analyzer.py → market-regime-snapshot.py --mode end →
  informe final → hash-logger.py

Uso:
    python pipeline-runner.py --build 10 --activo XAUUSD
    python pipeline-runner.py --build 11 --activo EURUSD --timeframe H1 \\
        --results-folder results/
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
RESULTS_DIR = Path("results")


def run(cmd, step_name, critical=True):
    """Ejecuta un subcomando y devuelve (exit_code, stdout, stderr)."""
    print(f"\n[STEP] {step_name}")
    print(f"       {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(
        [sys.executable] + [str(c) for c in cmd],
        capture_output=True, text=True
    )
    if result.stdout:
        for line in result.stdout.strip().splitlines():
            print(f"       {line}")
    if result.returncode != 0:
        status = "FAIL" if critical else "WARN"
        print(f"       [{status}] exit code {result.returncode}")
        if result.stderr:
            print(f"       stderr: {result.stderr.strip()[:300]}")
    else:
        print(f"       [OK]")
    return result.returncode, result.stdout, result.stderr


def count_csvs(folder):
    return len(list(Path(folder).glob("Strategy*.csv")))


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def generate_report(args, gate_data, portfolio_data, regime_data, report_path):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    total     = gate_data.get("total", 0)
    pasan     = gate_data.get("pasan", 0)
    descartan = gate_data.get("descartan", 0)
    tasa      = gate_data.get("tasa_aprobacion_pct", 0.0)

    port_estado   = portfolio_data.get("estado", "N/A")
    port_n        = portfolio_data.get("metricas_portfolio", {}).get("estrategias", 0)
    port_dd       = portfolio_data.get("metricas_portfolio", {}).get("dd_combinado_estimado", 0)
    port_pf       = portfolio_data.get("metricas_portfolio", {}).get("pf_medio", 0)

    reg_inicio = regime_data.get("snapshot_inicio", {}).get("regimen", "N/A")
    reg_fin    = regime_data.get("snapshot_fin", {}).get("regimen", "N/A")
    deriva     = regime_data.get("deriva_adx_pct")
    advertencia = regime_data.get("advertencia_deriva", False)

    # Proximos pasos
    pasos = []
    if pasan == 0:
        pasos.append("- ACCION REQUERIDA: Ninguna estrategia paso el EvalGate. Revisar configuracion del Builder.")
        pasos.append("- Verificar spread_backtest_sucio = 2x spread real FTMO.")
        pasos.append("- Verificar que los datos M1 son suficientes (2003-2020 IS).")
    elif port_estado == "PORTFOLIO_INSUFICIENTE":
        pasos.append(f"- Solo {port_n} estrategias en portfolio (minimo 3). Continuar builds en otros activos.")
        pasos.append("- Ejecutar Retester en SQ con las estrategias que pasaron EvalGate.")
        pasos.append("- Ejecutar WFO en SQ tras el Retester.")
    else:
        pasos.append(f"- {port_n} estrategias seleccionadas en portfolio. Proceder con Retester OOS.")
        pasos.append("- Ejecutar Stress Test con los 5 periodos criticos (skill-stress-test.md).")
        pasos.append("- Ejecutar WFO Matrix en SQ tras el Retester.")
        pasos.append("- Exportar a MT5 y lanzar Forward Test en demo.")

    if advertencia:
        pasos.append(f"- ADVERTENCIA: Deriva de regimen ADX > 30% durante el build.")
        pasos.append(f"  Regimen inicio: {reg_inicio} | Regimen fin: {reg_fin}")
        pasos.append("  Las estrategias pueden estar optimizadas para un regimen que ya no existe.")

    # Tabla de estrategias que pasan
    passed_rows = ""
    for s in gate_data.get("passed", []):
        m = s["metrics"]
        passed_rows += (
            f"| {m.get('file','')[:35]:<35} "
            f"| {m.get('pf',''):<5} "
            f"| {m.get('dd',''):<5} "
            f"| {m.get('trades',''):<7} "
            f"| {m.get('wr',''):<5} |\n"
        )
    if not passed_rows:
        passed_rows = "| (ninguna) | — | — | — | — |\n"

    # Tabla portfolio
    port_rows = ""
    for s in portfolio_data.get("portfolio", []):
        m = s["metrics"]
        port_rows += (
            f"| {m.get('file','')[:30]:<30} "
            f"| {s.get('activo',''):<10} "
            f"| {s.get('score',''):<6} "
            f"| {s.get('peso_hrp', 0):.1%} |\n"
        )
    if not port_rows:
        port_rows = "| (ninguna) | — | — | — |\n"

    md = f"""# Pipeline Report — Build {args.build} — {args.activo}

Generado: {now}
Timeframe: {args.timeframe}

---

## Resumen del Build

| Metrica | Valor |
|---------|-------|
| Total estrategias evaluadas | {total} |
| Pasan EvalGate | {pasan} ({tasa}%) |
| Descartadas EvalGate | {descartan} |
| Portfolio estado | {port_estado} |
| Estrategias en portfolio | {port_n} |
| DD combinado estimado | {port_dd}% |
| PF medio portfolio | {port_pf} |

---

## Estrategias que Pasan el EvalGate

| Archivo | PF | DD% | Trades | WR% |
|---------|-----|-----|--------|-----|
{passed_rows}
---

## Portfolio Seleccionado

| Archivo | Activo | Score | Peso HRP |
|---------|--------|-------|----------|
{port_rows}
---

## Regimen de Mercado

| | Inicio | Fin |
|-|--------|-----|
| Regimen | {reg_inicio} | {reg_fin} |
| Deriva ADX | — | {f'{deriva*100:.1f}%' if deriva is not None else 'N/A'} |
| Advertencia | — | {'SI' if advertencia else 'NO'} |

---

## Proximos Pasos

{chr(10).join(pasos)}

---

*Generado por pipeline-runner.py — TradingLab*
"""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md)


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline maestro post-build — coordina evaluacion completa"
    )
    parser.add_argument("--build",          required=True, type=int)
    parser.add_argument("--activo",         required=True)
    parser.add_argument("--timeframe",      default="H1", choices=["H1", "H4", "M30", "M15"])
    parser.add_argument("--results-folder", default="results")
    parser.add_argument("--prices-csv",     help="CSV de precios para regime snapshot (opcional)")
    args = parser.parse_args()

    results_folder = Path(args.results_folder)
    fecha_str      = datetime.now().strftime("%Y%m%d-%H%M")
    report_path    = results_folder / f"pipeline-report-{fecha_str}.md"

    gate_json      = results_folder / "evaluation-gate-results.json"
    portfolio_json = results_folder / "portfolio-selected.json"
    snapshot_json  = results_folder / "build-regime-snapshot.json"

    print(f"\n{'='*50}")
    print(f"PIPELINE RUNNER — Build {args.build} | {args.activo} {args.timeframe}")
    print(f"{'='*50}")

    # Verificar que hay CSVs
    n_csvs = count_csvs(results_folder)
    if n_csvs == 0:
        print(f"\n[ERROR] No se encuentran Strategy*.csv en {results_folder}")
        print("        SQ debe haber exportado el databank antes de ejecutar el pipeline.")
        sys.exit(2)
    print(f"\n[INFO]  {n_csvs} archivos Strategy*.csv encontrados en {results_folder}")

    # PASO 1 — EvalGate
    rc1, _, _ = run(
        [SCRIPTS_DIR / "evaluator-assistant.py",
         "--results-folder", str(results_folder),
         "--timeframe", args.timeframe,
         "--output", str(gate_json)],
        "Evaluation Gate (evaluator-assistant.py)",
        critical=True,
    )

    gate_data = load_json(gate_json)
    pasan     = gate_data.get("pasan", 0)

    if pasan == 0:
        print(f"\n[STOP] Ninguna estrategia paso el EvalGate.")
        print("       Revisar configuracion del Builder:")
        print("       - Spread backtest_sucio = 2x spread real FTMO?")
        print("       - Datos IS suficientes (2003-2020)?")
        print("       - Filtros SQ demasiado restrictivos?")
        sys.exit(1)

    print(f"\n[INFO]  {pasan} estrategias pasan el EvalGate — continuando pipeline.")

    # PASO 2 — Portfolio Builder
    rc2, _, _ = run(
        [SCRIPTS_DIR / "portfolio-builder.py",
         "--eval-results", str(gate_json),
         "--output", str(portfolio_json)],
        "Portfolio Builder (portfolio-builder.py)",
        critical=False,
    )

    portfolio_data = load_json(portfolio_json)

    # PASO 3 — Build Analyzer (Ollama opcional — no critico)
    analysis_path = results_folder / f"build-{args.build}-analysis.md"
    run(
        [SCRIPTS_DIR / "build-analyzer.py",
         "--results-folder", str(results_folder),
         "--output", str(analysis_path)],
        "Build Analyzer (build-analyzer.py — Ollama opcional)",
        critical=False,
    )

    # PASO 4 — Regime Snapshot end (solo si hay CSV de precios)
    regime_data = load_json(snapshot_json) if snapshot_json.exists() else {}
    if args.prices_csv and Path(args.prices_csv).exists():
        run(
            [SCRIPTS_DIR / "market-regime-snapshot.py",
             "--prices-csv", args.prices_csv,
             "--build", str(args.build),
             "--activo", args.activo,
             "--mode", "end"],
            "Market Regime Snapshot end",
            critical=False,
        )
        regime_data = load_json(snapshot_json)

    # PASO 5 — Generar informe final
    print(f"\n[STEP] Generando informe final")
    generate_report(args, gate_data, portfolio_data, regime_data, report_path)
    print(f"       [OK] {report_path}")

    # PASO 6 — Hash logger (audit trail)
    port_estado = portfolio_data.get("estado", "N/A")
    decision_msg = (
        f"BUILD-{args.build}-PIPELINE-COMPLETO: "
        f"{args.activo} {args.timeframe} — "
        f"EvalGate {pasan}/{gate_data.get('total',0)} — "
        f"Portfolio {port_estado}"
    )
    hash_script = SCRIPTS_DIR / "hash-logger.py"
    if hash_script.exists():
        run(
            [hash_script, "--event", decision_msg],
            "Hash Logger (audit trail)",
            critical=False,
        )

    # Resultado final
    port_n = portfolio_data.get("metricas_portfolio", {}).get("estrategias", 0)
    min_strat = 3

    print(f"\n{'='*50}")
    print(f"PIPELINE COMPLETADO — Build {args.build}")
    print(f"{'='*50}")
    print(f"EvalGate:    {pasan}/{gate_data.get('total',0)} pasan ({gate_data.get('tasa_aprobacion_pct',0)}%)")
    print(f"Portfolio:   {port_n} estrategias — {port_estado}")
    print(f"Informe:     {report_path}")

    if port_n >= min_strat:
        print(f"\nSIGUIENTE PASO: Ejecutar Retester en SQ con las {pasan} estrategias.")
        sys.exit(0)
    else:
        print(f"\nINSUFICIENTE: {port_n} estrategias en portfolio (minimo {min_strat}).")
        print("Continuar builds en otros activos para completar el portfolio.")
        sys.exit(1)


if __name__ == "__main__":
    main()
