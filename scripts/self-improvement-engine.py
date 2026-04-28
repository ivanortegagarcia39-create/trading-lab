#!/usr/bin/env python3
"""
self-improvement-engine.py — Orquestador del ciclo de autoaprendizaje.

Coordina DSPy y Bayesian Updating para ejecutar el ciclo completo
de mejora continua sin intervención humana.

Uso:
    python scripts/self-improvement-engine.py --run
    python scripts/self-improvement-engine.py --dry-run
    python scripts/self-improvement-engine.py --report
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT       = Path(__file__).parent.parent
AUDIT_PATH = ROOT / "config" / "bayesian-audit-trail.jsonl"
SIE_LOG    = ROOT / "config" / "self-improvement-log.jsonl"

PYTHON = sys.executable


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _run(cmd: list, dry_run: bool = False) -> str:
    if dry_run:
        print(f"  [DRY-RUN] {' '.join(cmd)}")
        return ""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and result.stderr:
        print(f"  STDERR: {result.stderr.strip()}")
    return result.stdout.strip()


def _log_cycle(entry: dict):
    SIE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(SIE_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def _read_audit_trail_week() -> list:
    """Lee las entradas del audit trail de la última semana."""
    if not AUDIT_PATH.exists():
        return []
    cutoff = (datetime.now() - timedelta(days=7)).isoformat()
    entries = []
    with open(AUDIT_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if entry.get("timestamp", "") >= cutoff:
                    entries.append(entry)
            except json.JSONDecodeError:
                pass
    return entries


def _send_telegram(message: str, dry_run: bool):
    notifier = ROOT / "scripts" / "telegram-notifier.py"
    if not notifier.exists():
        print(f"  Telegram: {message}")
        return
    cmd = [PYTHON, str(notifier), "--level", "INFO", "--message", message]
    if dry_run:
        cmd.append("--dry-run")
    _run(cmd, dry_run=False)  # ejecutar siempre (el --dry-run va dentro)


def _register_kg(cycle_summary: dict, dry_run: bool):
    """Registra el ciclo en el Knowledge Graph."""
    kg = ROOT / "scripts" / "knowledge-graph.py"
    if not kg.exists():
        return
    data = json.dumps({
        "event":    "self_improvement_cycle",
        "date":     datetime.now().isoformat(),
        "summary":  cycle_summary,
    })
    _run([PYTHON, str(kg), "--mode", "add-build", "--data", data], dry_run)


# ─── Ciclo de autoaprendizaje ─────────────────────────────────────────────────

def run_cycle(dry_run: bool = False) -> dict:
    """Ejecuta el ciclo completo de autoaprendizaje."""
    started_at = datetime.now().isoformat()
    print(f"\n{'[DRY-RUN] ' if dry_run else ''}CICLO DE AUTOAPRENDIZAJE — {started_at}")
    print("=" * 60)

    summary = {
        "started_at":           started_at,
        "dry_run":              dry_run,
        "audit_entries_week":   0,
        "bayesian_updates":     0,
        "dspy_examples_added":  0,
        "dspy_compilations":    0,
        "recalibrations_done":  0,
        "errors":               [],
    }

    bayesian = ROOT / "scripts" / "bayesian-criteria-updater.py"
    dspy_opt = ROOT / "scripts" / "dspy-optimizer.py"

    # PASO 1: Leer audit trail de la última semana
    print("\n[1/7] Leyendo audit trail de la última semana...")
    recent_entries = _read_audit_trail_week()
    summary["audit_entries_week"] = len(recent_entries)
    print(f"      {len(recent_entries)} entradas encontradas.")

    # PASO 2: Actualizar criterios bayesianos y añadir ejemplos DSPy
    print("\n[2/7] Procesando decisiones del pipeline...")

    # Mapeo de outcomes en el audit trail a criterios bayesianos
    criterion_map = {
        "evalgate_pf":    "pf_minimo_evalgate",
        "evalgate_dd":    "dd_maximo_evalgate",
        "oos_sharpe":     "sharpe_minimo_oos",
        "wfo_wfe":        "wfe_minimo",
        "forward_pf":     "pf_forward_test_ratio",
    }

    for entry in recent_entries:
        if "criterion" in entry and "outcome" in entry:
            criterion = entry["criterion"]
            outcome   = entry["outcome"]
            if criterion in criterion_map.values() and outcome in {
                "true_positive", "false_positive", "true_negative", "false_negative"
            }:
                print(f"      Bayesian update: {criterion} ← {outcome}")
                _run([PYTHON, str(bayesian), "--update", criterion, outcome], dry_run)
                summary["bayesian_updates"] += 1

            # Añadir ejemplo DSPy si tiene input/output
            if "dspy_module" in entry and "input" in entry and "output" in entry:
                module = entry["dspy_module"]
                score  = str(entry.get("score", 0.7))
                inp    = json.dumps(entry["input"])
                out    = json.dumps(entry["output"])
                print(f"      DSPy ejemplo: {module} (score={score})")
                _run([PYTHON, str(dspy_opt), "--add-example", module, inp, out, score], dry_run)
                summary["dspy_examples_added"] += 1

    # PASO 2b: Concept drift check
    print("\n[2b/7] Verificando drift y cambios de régimen...")
    drift_detector = ROOT / "scripts" / "concept-drift-detector.py"
    if drift_detector.exists():
        drift_out = _run([PYTHON, str(drift_detector), "--check"], dry_run=False)
        if drift_out:
            print(f"      {drift_out[:200]}")
            if "CHANGE_POINT" in drift_out or "DRIFT_DETECTED" in drift_out:
                summary["drift_alert"] = drift_out[:200]
                summary.setdefault("alerts", []).append("DRIFT detectado — ver concept-drift-detector")
    else:
        print("      concept-drift-detector.py no encontrado — omitido")

    # PASO 2c: Champion-Challenger evaluation
    print("\n[2c/7] Evaluando challengers activos...")
    cc_script = ROOT / "scripts" / "champion-challenger.py"
    cc_state  = ROOT / "results" / "champion-challenger.json"
    promotions = []
    if cc_script.exists() and cc_state.exists():
        import json as _json
        with open(cc_state) as f:
            cc_data = _json.load(f)
        challengers = list(cc_data.get("challengers", {}).keys())
        if challengers:
            for sid in challengers:
                eval_out = _run([PYTHON, str(cc_script), "--evaluate", sid], dry_run=False)
                if eval_out:
                    print(f"      {sid}: {eval_out[-100:].strip()}")
                if "PROMOTE" in eval_out:
                    promotions.append(sid)
                    summary.setdefault("alerts", []).append(f"Challenger {sid} listo para PROMOTION")
        else:
            print("      Sin challengers activos")
    else:
        print("      champion-challenger.py o estado no encontrado — omitido")
    summary["challengers_ready_to_promote"] = promotions

    # PASO 2d: Internal Critic (dry-run siempre, para no modificar criterios dos veces)
    print("\n[2d/7] Ejecutando Crítico Interno...")
    critic = ROOT / "scripts" / "internal-critic.py"
    if critic.exists():
        critic_out = _run([PYTHON, str(critic), "--dry-run"], dry_run=False)
        if critic_out:
            # Incluir resumen del crítico en el informe final
            lines = [l for l in critic_out.split("\n") if l.strip()]
            summary["critic_summary"] = lines[-5:] if len(lines) >= 5 else lines
            for line in summary["critic_summary"]:
                print(f"      {line}")
    else:
        print("      internal-critic.py no encontrado — omitido")

    # PASO 2e: PropFirm monitor
    print("\n[2e/7] Verificando cambios en T&C de prop firms...")
    propfirm_mon = ROOT / "scripts" / "propfirm-monitor.py"
    if propfirm_mon.exists():
        pf_out = _run([PYTHON, str(propfirm_mon), "--check", "--dry-run"], dry_run=False)
        if pf_out:
            for line in pf_out.split("\n")[:6]:
                if line.strip():
                    print(f"      {line.strip()}")
            if "CRÍTICO" in pf_out:
                summary.setdefault("alerts", []).append("CAMBIO CRÍTICO en T&C de prop firm — revisar urgente")
            elif "IMPORTANTE" in pf_out:
                summary.setdefault("alerts", []).append("Cambio IMPORTANTE en T&C de prop firm")
    else:
        print("      propfirm-monitor.py no encontrado — omitido")

    # PASO 2f: Actualizar Thompson Sampling con builds de la semana
    print("\n[2f/7] Actualizando Thompson Sampling con resultados recientes...")
    thompson = ROOT / "scripts" / "thompson-sampling.py"
    thompson_updates = 0
    if thompson.exists():
        # Leer builds completados en el audit trail de la semana
        build_outcomes = [e for e in recent_entries
                          if e.get("event") == "build_completed" and "activo" in e]
        if build_outcomes:
            for build in build_outcomes:
                activo  = build.get("activo", "")
                tf      = build.get("tf", "H1")
                success = str(build.get("success", False)).lower()
                if activo:
                    _run([PYTHON, str(thompson), "--update-asset", activo, tf, success], dry_run)
                    thompson_updates += 1
            print(f"      {thompson_updates} builds actualizados en Thompson Sampling")
        else:
            print("      Sin builds completados esta semana en el audit trail")
        # También actualizar estrategias activas si hay resultados semanales
        strategy_outcomes = [e for e in recent_entries
                             if e.get("event") == "strategy_weekly_result" and "strategy_id" in e]
        for so in strategy_outcomes:
            sid     = so["strategy_id"]
            success = str(so.get("success", False)).lower()
            _run([PYTHON, str(thompson), "--update-strategy", sid, success], dry_run)
    else:
        print("      thompson-sampling.py no encontrado — omitido")
    summary["thompson_updates"] = thompson_updates

    # PASO 3: Verificar si hay suficientes ejemplos para recompilar
    print("\n[3/7] Verificando estado de compilación DSPy...")
    stats_out = _run([PYTHON, str(dspy_opt), "--stats"], dry_run=False)
    print(f"      {stats_out[:200] if stats_out else '(sin datos)'}")

    # PASO 4: Recompilar módulos si hay suficientes ejemplos
    print("\n[4/7] Recompilando módulos DSPy si procede...")
    for module in ["StrategyEvaluator", "LessonSynthesizer", "BuildAnalyzer"]:
        training_file = ROOT / "config" / "dspy-training" / f"{module}.jsonl"
        if training_file.exists():
            count = sum(1 for line in open(training_file) if line.strip())
            if count >= 10:
                print(f"      Compilando {module} ({count} ejemplos)...")
                _run([PYTHON, str(dspy_opt), "--compile", module], dry_run)
                summary["dspy_compilations"] += 1
            else:
                print(f"      {module}: {count}/10 ejemplos (no recompilado)")

    # PASO 5: Verificar criterios que necesitan recalibración
    print("\n[5/7] Verificando criterios bayesianos...")
    report_out = _run([PYTHON, str(bayesian), "--thresholds"], dry_run=False)
    if report_out:
        for line in report_out.split("\n")[:8]:
            print(f"      {line}")
    summary["recalibrations_done"] = summary["bayesian_updates"]

    # PASO 6: Generar informe de mejoras
    print("\n[6/7] Generando informe...")
    report_lines = [
        f"Ciclo autoaprendizaje {started_at[:10]}",
        f"- Entradas audit: {summary['audit_entries_week']}",
        f"- Updates bayesianos: {summary['bayesian_updates']}",
        f"- Ejemplos DSPy añadidos: {summary['dspy_examples_added']}",
        f"- Compilaciones DSPy: {summary['dspy_compilations']}",
    ]
    if summary.get("drift_alert"):
        report_lines.append(f"- ALERTA DRIFT: {summary['drift_alert'][:60]}")
    if summary.get("challengers_ready_to_promote"):
        report_lines.append(f"- Challengers para promover: {summary['challengers_ready_to_promote']}")
    if summary.get("alerts"):
        for alert in summary["alerts"]:
            report_lines.append(f"- ALERTA: {alert}")
    report = "\n".join(report_lines)
    print("\n" + report)

    # PASO 7: Enviar resumen via Telegram y registrar en KG
    print("\n[7/7] Notificando y registrando...")
    _send_telegram(report.replace("\n", " | "), dry_run)
    _register_kg(summary, dry_run)

    summary["finished_at"] = datetime.now().isoformat()
    _log_cycle(summary)

    print(f"\n{'[DRY-RUN] ' if dry_run else ''}Ciclo completado.")
    return summary


def show_report():
    """Muestra el historial de ciclos de autoaprendizaje."""
    if not SIE_LOG.exists():
        print("No hay ciclos registrados aún.")
        return
    cycles = []
    with open(SIE_LOG) as f:
        for line in f:
            if line.strip():
                try:
                    cycles.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    print(f"\nHistorial de ciclos de autoaprendizaje ({len(cycles)} total)")
    print("-" * 65)
    for c in cycles[-10:]:
        date    = c.get("started_at", "?")[:10]
        dry     = " [DRY]" if c.get("dry_run") else ""
        updates = c.get("bayesian_updates", 0)
        comps   = c.get("dspy_compilations", 0)
        print(f"  {date}{dry}  bayesian={updates}  dspy_compilaciones={comps}  "
              f"ejemplos={c.get('dspy_examples_added', 0)}")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Self-Improvement Engine — TradingLab")
    parser.add_argument("--run",     action="store_true", help="Ejecutar ciclo completo")
    parser.add_argument("--dry-run", action="store_true", help="Simular sin aplicar cambios")
    parser.add_argument("--report",  action="store_true", help="Ver historial de ciclos")
    args = parser.parse_args()

    if args.run:
        run_cycle(dry_run=False)
    elif args.dry_run:
        run_cycle(dry_run=True)
    elif args.report:
        show_report()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
