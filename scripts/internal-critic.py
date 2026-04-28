#!/usr/bin/env python3
"""
internal-critic.py — El Crítico Interno automático (P2.5).

Revisa retrospectivamente las últimas 20 decisiones del pipeline,
identifica los 3 errores más costosos, genera hipótesis de causa
y propone ajustes concretos al bayesian-updater.

Uso:
    python scripts/internal-critic.py --run
    python scripts/internal-critic.py --dry-run
    python scripts/internal-critic.py --report
"""

import argparse
import io
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT           = Path(__file__).parent.parent
AUDIT_PATH     = ROOT / "config" / "bayesian-audit-trail.jsonl"
CC_AUDIT       = ROOT / "config" / "cc-audit-trail.jsonl"
CRITIC_LOG     = ROOT / "config" / "internal-critic-log.jsonl"
LESSONS_PATH   = ROOT / "docs" / "lessons-learned.md"

_PYTHON = sys.executable


# ─── I/O ──────────────────────────────────────────────────────────────────────

def _read_audit(path: Path, n: int = 20) -> list:
    if not path.exists():
        return []
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries[-n:]


def _run_cmd(cmd: list, dry_run: bool = False) -> str:
    if dry_run:
        print(f"  [DRY-RUN] {' '.join(str(c) for c in cmd)}")
        return ""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()


def _append_critic_log(entry: dict):
    CRITIC_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(CRITIC_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ─── Análisis de decisiones ───────────────────────────────────────────────────

def _classify_decision(entry: dict) -> dict | None:
    """Clasifica una entrada del audit trail como error, acierto o neutral."""
    outcome = entry.get("outcome", "")
    if not outcome:
        return None

    is_error = outcome in ("false_positive", "false_negative")
    cost     = entry.get("pct_change", 0.0)  # magnitud del cambio en el criterio

    return {
        "timestamp":  entry.get("timestamp", ""),
        "criterion":  entry.get("criterion", ""),
        "outcome":    outcome,
        "is_error":   is_error,
        "cost":       abs(cost),
        "action":     entry.get("action", ""),
    }


def _analyze_false_positive_rate(decisions: list) -> dict:
    """Tasa de FP por criterio."""
    by_criterion: dict[str, dict] = {}
    for d in decisions:
        if not d:
            continue
        crit = d["criterion"]
        if crit not in by_criterion:
            by_criterion[crit] = {"total": 0, "fp": 0, "fn": 0, "tp": 0, "tn": 0}
        by_criterion[crit]["total"] += 1
        if d["outcome"] in ("false_positive",):
            by_criterion[crit]["fp"] += 1
        elif d["outcome"] in ("false_negative",):
            by_criterion[crit]["fn"] += 1
        elif d["outcome"] in ("true_positive",):
            by_criterion[crit]["tp"] += 1
        elif d["outcome"] in ("true_negative",):
            by_criterion[crit]["tn"] += 1
    return by_criterion


def _generate_hypothesis(error: dict, rates: dict) -> str:
    """Genera hipótesis de causa para un error dado."""
    crit    = error.get("criterion", "")
    outcome = error.get("outcome", "")
    stats   = rates.get(crit, {})
    fp_rate = stats.get("fp", 0) / max(stats.get("total", 1), 1)
    fn_rate = stats.get("fn", 0) / max(stats.get("total", 1), 1)

    if outcome == "false_positive":
        if fp_rate > 0.3:
            return (f"El criterio '{crit}' es sistemáticamente demasiado permisivo "
                    f"(FP rate={fp_rate:.1%}). Hipótesis: umbral demasiado bajo.")
        return f"Caso aislado de FP en '{crit}'. Umbral actual posiblemente correcto."

    if outcome == "false_negative":
        if fn_rate > 0.3:
            return (f"El criterio '{crit}' es sistemáticamente demasiado estricto "
                    f"(FN rate={fn_rate:.1%}). Hipótesis: umbral demasiado alto.")
        return f"Caso aislado de FN en '{crit}'. Revisar datos del período."

    return "Sin hipótesis clara — necesita más observaciones."


def _try_llm_analysis(error: dict, dry_run: bool) -> str:
    """Intenta usar model-router (deepseek local) para análisis causal."""
    router = ROOT / "scripts" / "model-router.py"
    if not router.exists():
        return ""
    prompt = (
        f"Analiza este error del pipeline de trading: {json.dumps(error)}. "
        "¿Cuál es la causa más probable? ¿Qué ajuste concreto al umbral resolvería el problema? "
        "Responde en máximo 2 frases."
    )
    out = _run_cmd([_PYTHON, str(router), "--task", "causal_analysis", "--prompt", prompt], dry_run)
    return out[:300] if out else ""


def _propose_bayesian_update(error: dict, hypothesis: str, dry_run: bool):
    """Propone un ajuste al bayesian-updater si la hipótesis es sistemática."""
    crit    = error.get("criterion", "")
    outcome = error.get("outcome", "")
    if not crit or not outcome:
        return

    # Solo proponer si la hipótesis menciona "sistemáticamente"
    if "sistemáticamente" not in hypothesis:
        print(f"  [CRITIC] Hipótesis no sistemática para {crit} — sin propuesta")
        return

    # Convertir el error en un outcome inverso para el bayesian-updater
    # FP → registrar como false_positive para que suba el umbral
    # FN → registrar como false_negative para que baje el umbral
    bayesian = ROOT / "scripts" / "bayesian-criteria-updater.py"
    if not bayesian.exists():
        return

    print(f"  [CRITIC] Proponiendo update bayesiano: {crit} ← {outcome}")
    _run_cmd([_PYTHON, str(bayesian), "--update", crit, outcome], dry_run)


def _append_lessons_md(errors: list[dict], hypotheses: list[str], dry_run: bool):
    """Añade las lecciones del crítico al lessons-learned.md."""
    if dry_run:
        print("  [DRY-RUN] Append a lessons-learned.md omitido")
        return
    LESSONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    lines = [f"\n## Critic Review {date_str}\n"]
    for err, hyp in zip(errors, hypotheses):
        lines.append(f"- **{err.get('criterion','')}** ({err.get('outcome','')}): {hyp}")
    lines.append("")
    with open(LESSONS_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Lecciones añadidas a {LESSONS_PATH}")


# ─── Proceso principal ────────────────────────────────────────────────────────

def run_review(dry_run: bool = False) -> dict:
    """Ejecuta la revisión completa del crítico interno."""
    started = datetime.now().isoformat()
    print(f"\n{'[DRY-RUN] ' if dry_run else ''}CRITICO INTERNO — {started}")
    print("=" * 55)

    # 1. Leer últimas 20 decisiones
    print("\n[1/7] Leyendo audit trail...")
    raw_entries = _read_audit(AUDIT_PATH, n=20)
    print(f"      {len(raw_entries)} entradas leídas.")

    # 2. Clasificar decisiones
    print("\n[2/7] Clasificando decisiones...")
    decisions = [_classify_decision(e) for e in raw_entries]
    decisions = [d for d in decisions if d]
    errors    = [d for d in decisions if d["is_error"]]
    print(f"      Total: {len(decisions)}  Errores: {len(errors)}")

    # 3. Identificar 3 errores más costosos
    print("\n[3/7] Identificando errores más costosos...")
    top3 = sorted(errors, key=lambda x: x["cost"], reverse=True)[:3]
    for i, err in enumerate(top3, 1):
        print(f"      #{i} {err['criterion']} ({err['outcome']}) cost={err['cost']:.2f}%")

    # 4. Calcular tasas de error por criterio
    rates = _analyze_false_positive_rate(decisions)

    # 5. Generar hipótesis para cada error
    print("\n[4/7] Generando hipótesis de causa...")
    hypotheses = []
    llm_analyses = []
    for err in top3:
        hyp = _generate_hypothesis(err, rates)
        hypotheses.append(hyp)
        print(f"      {err['criterion']}: {hyp[:80]}")

        llm_out = _try_llm_analysis(err, dry_run)
        if llm_out:
            llm_analyses.append(llm_out)
            print(f"      [LLM] {llm_out[:80]}")

    # 6. Verificar hipótesis contra datos históricos (backtesting conceptual)
    print("\n[5/7] Verificando hipótesis...")
    rates_summary = []
    for crit, stats in rates.items():
        total = stats["total"]
        if total == 0:
            continue
        fp = stats["fp"] / total
        fn = stats["fn"] / total
        acc = (stats["tp"] + stats["tn"]) / total
        rates_summary.append(f"      {crit:<30} FP={fp:.1%} FN={fn:.1%} Acc={acc:.1%}")
    for line in rates_summary[:5]:
        print(line)

    # 7. Proponer ajustes al bayesian-updater
    print("\n[6/7] Proponiendo ajustes bayesianos...")
    for err, hyp in zip(top3, hypotheses):
        _propose_bayesian_update(err, hyp, dry_run)

    # 8. Registrar en KG y lessons-learned.md
    print("\n[7/7] Registrando lecciones...")
    _append_lessons_md(top3, hypotheses, dry_run)

    summary = {
        "started_at":    started,
        "dry_run":       dry_run,
        "decisions":     len(decisions),
        "errors":        len(errors),
        "top3_errors":   top3,
        "hypotheses":    hypotheses,
        "rates":         {k: v for k, v in rates.items()},
        "finished_at":   datetime.now().isoformat(),
    }
    _append_critic_log(summary)
    print(f"\n{'[DRY-RUN] ' if dry_run else ''}Revisión completada.")
    return summary


def show_report():
    """Muestra el último informe del crítico."""
    if not CRITIC_LOG.exists():
        print("No hay revisiones registradas aún.")
        return
    entries = []
    with open(CRITIC_LOG) as f:
        for line in f:
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    if not entries:
        print("Log vacío.")
        return

    last = entries[-1]
    print(f"\nÚltima revisión: {last.get('started_at', '?')[:10]}")
    print(f"  Decisiones analizadas: {last.get('decisions', 0)}")
    print(f"  Errores encontrados:   {last.get('errors', 0)}")
    print("  Top 3 errores:")
    for err, hyp in zip(last.get("top3_errors", []), last.get("hypotheses", [])):
        print(f"    {err.get('criterion','')} ({err.get('outcome','')}) → {hyp[:70]}")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Internal Critic — TradingLab")
    parser.add_argument("--run",     action="store_true", help="Ejecutar revisión completa")
    parser.add_argument("--dry-run", action="store_true", help="Simular sin aplicar cambios")
    parser.add_argument("--report",  action="store_true", help="Ver último informe")
    args = parser.parse_args()

    if args.run:
        run_review(dry_run=False)
    elif args.dry_run:
        run_review(dry_run=True)
    elif args.report:
        show_report()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
