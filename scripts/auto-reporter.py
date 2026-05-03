#!/usr/bin/env python3
"""
auto-reporter.py — Genera informe semanal automatico del proyecto TradingLab

Uso:
    python scripts/auto-reporter.py
    python scripts/auto-reporter.py --no-telegram --no-ollama
    python scripts/auto-reporter.py --output-dir results/reports/
"""

import argparse
import json
import subprocess
import sys
import urllib.request
import ssl
from datetime import datetime
from pathlib import Path

ROOT       = Path(__file__).parent.parent
RESULTS    = ROOT / "results"
SCRIPTS    = ROOT / "scripts"


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _load_json(path: Path) -> dict | list:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


# ── 1. Estado del pipeline ─────────────────────────────────────────────────

def _pipeline_state() -> dict:
    lock = RESULTS / "pipeline.lock"
    gate = _load_json(RESULTS / "evaluation-gate-results.json")
    port = _load_json(RESULTS / "portfolio-selected.json")

    strategies_csv = list(RESULTS.rglob("Strategy*.csv"))
    session_log    = _load_json(RESULTS / "session-log.json")

    last_session = ""
    if isinstance(session_log, list) and session_log:
        last_session = session_log[-1].get("timestamp", "")[:19]

    return {
        "build_activo":       lock.read_text(encoding="utf-8").strip() if lock.exists() else "ninguno",
        "strategies_csv":     len(strategies_csv),
        "evalgate_pasan":     gate.get("pasan", 0) if isinstance(gate, dict) else 0,
        "evalgate_total":     gate.get("total", 0) if isinstance(gate, dict) else 0,
        "portfolio_size":     (port.get("metricas_portfolio", {}).get("estrategias", 0)
                               if isinstance(port, dict) else 0),
        "portfolio_estado":   port.get("estado", "N/A") if isinstance(port, dict) else "N/A",
        "last_session":       last_session,
    }


# ── 2. Métricas del portfolio ──────────────────────────────────────────────

def _portfolio_metrics() -> dict:
    health = _load_json(RESULTS / "system-health.json")
    port   = _load_json(RESULTS / "portfolio-selected.json")

    strategies = []
    if isinstance(port, dict):
        for s in port.get("portfolio", []):
            strategies.append({
                "id":     s.get("id", s.get("file", "?")),
                "symbol": s.get("symbol", s.get("activo", "?")),
                "peso":   s.get("peso_hrp", 0),
            })

    return {
        "estrategias": strategies,
        "health_ok":   health.get("summary", {}).get("ok", 0) if isinstance(health, dict) else 0,
        "health_warn": health.get("summary", {}).get("warn", 0) if isinstance(health, dict) else 0,
        "health_fail": health.get("summary", {}).get("fail", 0) if isinstance(health, dict) else 0,
    }


# ── 3. Lecciones estructurales ────────────────────────────────────────────

def _structural_lessons() -> list[str]:
    text = _read_text(ROOT / "docs" / "lessons-learned.md")
    lines = text.splitlines()

    # 1. Encontrar la sección "## HISTORIAL DE LECCIONES"
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("## HISTORIAL DE LECCIONES"):
            start_idx = i + 1
            break

    if start_idx is None:
        return []

    # 2. Buscar lecciones a partir de esa sección
    lessons = []
    history = lines[start_idx:]
    for i, line in enumerate(history):
        if not line.strip().startswith("### LECCION-"):
            continue
        title = line.strip().lstrip("#").strip()
        # 3. Buscar "Ocurrencias confirmadas:" en las siguientes 30 líneas
        is_structural = False
        for j in range(1, min(31, len(history) - i)):
            candidate = history[i + j].strip()
            if candidate.lower().startswith("ocurrencias confirmadas:"):
                value = candidate.upper()
                if "ESTRUCTURAL" in value or "PERMANENTE" in value:
                    is_structural = True
                break
        # 4. Incluir solo lecciones estructurales o permanentes
        if is_structural:
            lessons.append(title)

    return lessons[:5]


# ── 4. Progreso del planning maestro ──────────────────────────────────────

def _planning_progress() -> dict:
    text = _read_text(ROOT / "docs" / "roadmap" / "planning-maestro-status.md")
    completadas = total = 0
    for line in text.splitlines():
        if "Total completadas" in line or "Total:" in line:
            import re
            nums = re.findall(r"\d+", line)
            if len(nums) >= 2:
                completadas, total = int(nums[0]), int(nums[1])
                break
    pct = round(completadas / total * 100, 1) if total else 0
    return {"completadas": completadas, "total": total, "pct": pct}


# ── 5. Próximas acciones ───────────────────────────────────────────────────

def _proxima_semana() -> dict:
    """Datos para la seccion 'Proxima semana' del informe."""
    result: dict = {
        "proximo_activo": "—",
        "cola_activos":   [],
        "bayesian_ajuste": "—",
        "shadow_terminan": [],
    }

    # Próximo activo por Thompson Sampling
    ts_script = SCRIPTS / "thompson-sampling.py"
    if ts_script.exists():
        try:
            r = subprocess.run(
                [sys.executable, str(ts_script), "--next-asset"],
                capture_output=True, text=True, timeout=15,
            )
            for line in r.stdout.splitlines():
                import re as _re
                m = _re.search(r"\b([A-Z]{6}|XAU/?USD|XAG/?USD|US\d{2,3})\b", line)
                if m:
                    result["proximo_activo"] = m.group(1).replace("/", "")
                    break
        except Exception:
            pass

    # Cola de builds
    queue = SCRIPTS / "build-queue-manager.py"
    if queue.exists():
        try:
            r = subprocess.run(
                [sys.executable, str(queue), "list"],
                capture_output=True, text=True, timeout=10,
            )
            for line in r.stdout.splitlines()[:5]:
                if line.strip() and not line.startswith("#"):
                    result["cola_activos"].append(line.strip())
        except Exception:
            pass

    # Criterios bayesianos candidatos a ajuste
    bc_path = ROOT / "config" / "bayesian-criteria.json"
    if bc_path.exists():
        try:
            criteria = json.loads(bc_path.read_text(encoding="utf-8"))
            # Criterios con confidence < 0.6 son candidatos
            candidatos = [
                k for k, v in criteria.items()
                if isinstance(v, dict) and v.get("confidence", 1.0) < 0.6
            ]
            result["bayesian_ajuste"] = ", ".join(candidatos[:3]) if candidatos else "sin ajustes pendientes"
        except Exception:
            pass

    # Estrategias en shadow mode que terminan pronto
    cc_path = ROOT / "results" / "champion-challenger.json"
    if cc_path.exists():
        try:
            import os as _os
            from datetime import timedelta
            cc       = json.loads(cc_path.read_text(encoding="utf-8"))
            today_ts = datetime.now().timestamp()
            for cid, info in cc.get("challengers", {}).items():
                end_str = info.get("end_date", "")
                if end_str:
                    try:
                        end_ts = datetime.fromisoformat(end_str).timestamp()
                        days_left = (end_ts - today_ts) / 86400
                        if 0 <= days_left <= 7:
                            result["shadow_terminan"].append(
                                f"{cid} ({days_left:.0f}d restantes)"
                            )
                    except Exception:
                        pass
        except Exception:
            pass

    return result


def _next_actions() -> str:
    text = _read_text(ROOT / "docs" / "project-status.md")
    in_section = False
    lines = []
    for line in text.splitlines():
        if "SIGUIENTE ACCION" in line.upper() or "PROXIMA ACCION" in line.upper():
            in_section = True
            continue
        if in_section:
            if line.startswith("## ") and lines:
                break
            if line.strip():
                lines.append(line.strip())
            if len(lines) >= 4:
                break
    return "\n".join(lines) if lines else "Ver docs/project-status.md"


# ── 6. Sistema de Autoaprendizaje ─────────────────────────────────────────

def _autoaprendizaje_status() -> dict:
    """Recopila estado de todos los componentes de autoaprendizaje."""
    result = {}

    # Knowledge Graph
    kg_db = ROOT / ".kuzu" / "tradinglab.db"
    result["kg_ok"] = kg_db.exists()
    if kg_db.exists():
        import os
        import re as _re
        mtime_str = datetime.fromtimestamp(os.path.getmtime(str(kg_db))).strftime("%Y-%m-%d")
        kg_script = ROOT / "scripts" / "knowledge-graph.py"
        builds = strategies = 0
        if kg_script.exists():
            try:
                r = subprocess.run(
                    [sys.executable, str(kg_script), "stats"],
                    capture_output=True, text=True, cwd=ROOT, timeout=15
                )
                for line in (r.stdout + r.stderr).splitlines():
                    m = _re.search(r"build\w*\s*[:\-]?\s*(\d+)", line, _re.IGNORECASE)
                    if m:
                        builds = int(m.group(1))
                    m = _re.search(r"strateg\w*\s*[:\-]?\s*(\d+)", line, _re.IGNORECASE)
                    if m:
                        strategies = int(m.group(1))
            except Exception:
                pass
        result["kg_label"] = f"{builds} builds, {strategies} estrategias"
        result["kg_date"]  = mtime_str
    else:
        result["kg_label"] = "no inicializado"
        result["kg_date"]  = "—"

    # Bayesian Criteria
    bc_path = ROOT / "config" / "bayesian-criteria.json"
    if bc_path.exists():
        import os
        try:
            criteria = json.loads(bc_path.read_text(encoding="utf-8"))
            result["bayesian_label"] = f"{len(criteria)} criterios"
            result["bayesian_date"]  = datetime.fromtimestamp(
                os.path.getmtime(str(bc_path))).strftime("%Y-%m-%d")
        except Exception:
            result["bayesian_label"] = "error"
            result["bayesian_date"]  = "—"
    else:
        result["bayesian_label"] = "no inicializado"
        result["bayesian_date"]  = "—"

    # DSPy Optimizer
    dspy_dir = ROOT / "config" / "dspy-compiled"
    if dspy_dir.exists():
        compiled = list(dspy_dir.glob("*.json"))
        result["dspy_label"] = f"{len(compiled)} módulos compilados"
    else:
        result["dspy_label"] = "sin compilaciones"
    result["dspy_date"] = "—"

    # Thompson Sampling
    ts_path = ROOT / "results" / "thompson-state.json"
    if ts_path.exists():
        import os
        try:
            ts = json.loads(ts_path.read_text(encoding="utf-8"))
            assets = ts.get("assets", {})
            result["thompson_label"] = f"{len(assets)} activos registrados"
            result["thompson_date"]  = datetime.fromtimestamp(
                os.path.getmtime(str(ts_path))).strftime("%Y-%m-%d")
        except Exception:
            result["thompson_label"] = "error"
            result["thompson_date"]  = "—"
    else:
        result["thompson_label"] = "no inicializado"
        result["thompson_date"]  = "—"

    # Concept Drift
    drift_path = ROOT / "results" / "drift-detection.json"
    if drift_path.exists():
        import os
        try:
            drift = json.loads(drift_path.read_text(encoding="utf-8"))
            prob = drift.get("bocpd", {}).get("last_prob", 0.0)
            crit = sum(1 for d in drift.get("addm", {}).values()
                       if d.get("level") == "CRITICAL")
            result["drift_label"] = f"BOCPD: {float(prob):.3f}, ADDM crit: {crit}"
            result["drift_date"]  = datetime.fromtimestamp(
                os.path.getmtime(str(drift_path))).strftime("%Y-%m-%d")
        except Exception:
            result["drift_label"] = "error"
            result["drift_date"]  = "—"
    else:
        result["drift_label"] = "sin datos"
        result["drift_date"]  = "—"

    # Champion-Challenger
    cc_path = ROOT / "results" / "champion-challenger.json"
    if cc_path.exists():
        import os
        try:
            cc = json.loads(cc_path.read_text(encoding="utf-8"))
            champions   = len(cc.get("champions", {}))
            challengers = len(cc.get("challengers", {}))
            result["cc_label"] = f"{champions} champions, {challengers} challengers"
            result["cc_date"]  = datetime.fromtimestamp(
                os.path.getmtime(str(cc_path))).strftime("%Y-%m-%d")
        except Exception:
            result["cc_label"] = "error"
            result["cc_date"]  = "—"
    else:
        result["cc_label"] = "sin datos"
        result["cc_date"]  = "—"

    # Self-improvement last cycle
    log_path = ROOT / "config" / "self-improvement-log.jsonl"
    if log_path.exists():
        try:
            lines = [l.strip() for l in log_path.read_text(encoding="utf-8").splitlines()
                     if l.strip()]
            if lines:
                last = json.loads(lines[-1])
                result["si_label"] = f"Último ciclo: {last.get('timestamp','')[:10]}"
                result["si_date"]  = last.get("timestamp", "")[:10]
            else:
                result["si_label"] = "sin registros"
                result["si_date"]  = "—"
        except Exception:
            result["si_label"] = "error"
            result["si_date"]  = "—"
    else:
        result["si_label"] = "nunca ejecutado"
        result["si_date"]  = "—"

    warns = [k for k in ("kg_label", "bayesian_label", "thompson_label")
             if "no inicializado" in result.get(k, "")]
    result["overall"] = "WARN" if warns else "OK"
    return result


# ── 7. Estado del sistema ──────────────────────────────────────────────────

def _system_status() -> str:
    health = _load_json(RESULTS / "system-health.json")
    if not health:
        return "Sin datos (ejecutar system-health-check.py)"
    s = health.get("summary", {})
    ts = health.get("timestamp", "")[:19]
    return f"OK:{s.get('ok',0)} WARN:{s.get('warn',0)} FAIL:{s.get('fail',0)} — {ts}"


# ── Ollama resumen ejecutivo ───────────────────────────────────────────────

def _ollama_summary(pipeline: dict, planning: dict) -> str | None:
    try:
        prompt = (
            f"Resumen ejecutivo del proyecto TradingLab esta semana: "
            f"Planning {planning['completadas']}/{planning['total']} tareas ({planning['pct']}%), "
            f"Build activo: {pipeline['build_activo']}, "
            f"Estrategias en databank: {pipeline['strategies_csv']}, "
            f"EvalGate: {pipeline['evalgate_pasan']}/{pipeline['evalgate_total']} pasan, "
            f"Portfolio: {pipeline['portfolio_size']} estrategias. "
            "Responde en 3 lineas: estado general, logro principal de la semana, proximo paso critico."
        )
        payload = json.dumps({"model": "deepseek-r1:7b", "prompt": prompt, "stream": False}).encode()
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=payload, headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            return json.loads(resp.read())["response"].strip()
    except Exception:
        return None


# ── Generar informe Markdown ───────────────────────────────────────────────

def _generate_md(pipeline: dict, portfolio: dict, lessons: list[str],
                 planning: dict, next_actions: str, sys_status: str,
                 ollama_text: str | None, week_str: str,
                 auto_status: dict | None = None,
                 proxima_semana: dict | None = None) -> str:
    date_str = datetime.now().strftime("%Y-%m-%d")

    strat_rows = ""
    for s in portfolio["estrategias"]:
        strat_rows += f"| {s['id']:<25} | {s['symbol']:<10} | {s['peso']:.1%} |\n"
    if not strat_rows:
        strat_rows = "| (ninguna activa) | — | — |\n"

    lesson_lines = "\n".join(f"- {l}" for l in lessons) if lessons else "- Sin lecciones registradas"

    ollama_section = ""
    if ollama_text:
        ollama_section = f"\n## Resumen Ejecutivo (deepseek-r1:7b)\n\n{ollama_text}\n"

    auto_section = ""
    if auto_status:
        a = auto_status
        auto_section = f"""
## Sistema de Autoaprendizaje

| Componente | Estado | Última actualización |
|------------|--------|---------------------|
| Knowledge Graph | {a.get('kg_label', '—')} | {a.get('kg_date', '—')} |
| Bayesian Criteria | {a.get('bayesian_label', '—')} | {a.get('bayesian_date', '—')} |
| DSPy Optimizer | {a.get('dspy_label', '—')} | {a.get('dspy_date', '—')} |
| Thompson Sampling | {a.get('thompson_label', '—')} | {a.get('thompson_date', '—')} |
| Concept Drift | {a.get('drift_label', '—')} | {a.get('drift_date', '—')} |
| Champion-Challenger | {a.get('cc_label', '—')} | {a.get('cc_date', '—')} |
| Self-improvement | {a.get('si_label', '—')} | {a.get('si_date', '—')} |

---
"""

    # Sección próxima semana
    proxima_section = ""
    if proxima_semana:
        p = proxima_semana
        cola_str    = "\n".join(f"  - {a}" for a in p["cola_activos"]) if p["cola_activos"] else "  - (vacia)"
        shadow_str  = "\n".join(f"  - {s}" for s in p["shadow_terminan"]) if p["shadow_terminan"] else "  - ninguna"
        proxima_section = f"""
## Proxima Semana

| Elemento | Detalle |
|----------|---------|
| Proximo build (Thompson) | {p['proximo_activo']} |
| Criterios bayesianos a revisar | {p['bayesian_ajuste']} |

**Cola de activos pendientes:**
{cola_str}

**Shadow mode terminando esta semana:**
{shadow_str}

---
"""

    return f"""# Informe Semanal — {week_str}
Generado: {date_str}

---

## Estado del Pipeline

| Metrica | Valor |
|---------|-------|
| Build activo | {pipeline['build_activo']} |
| Estrategias en databank | {pipeline['strategies_csv']} |
| EvalGate: pasan | {pipeline['evalgate_pasan']} / {pipeline['evalgate_total']} |
| Portfolio | {pipeline['portfolio_size']} estrategias ({pipeline['portfolio_estado']}) |
| Ultima sesion | {pipeline['last_session'] or 'N/A'} |

---

## Portfolio Activo

| Estrategia | Activo | Peso HRP |
|------------|--------|----------|
{strat_rows}
---

## Estado del Sistema

{sys_status}

Health checks: OK:{portfolio['health_ok']} — WARN:{portfolio['health_warn']} — FAIL:{portfolio['health_fail']}

---

## Planning Maestro

**{planning['completadas']} / {planning['total']} tareas completadas ({planning['pct']}%)**

---

## Lecciones Estructurales

{lesson_lines}

---

## Proximas Acciones

{next_actions}
{proxima_section}{auto_section}{ollama_section}
---
*Generado por auto-reporter.py — TradingLab*
"""


# ── Notificacion Telegram ─────────────────────────────────────────────────

def _send_telegram(pipeline: dict, planning: dict, no_telegram: bool):
    if no_telegram:
        return
    notifier = SCRIPTS / "telegram-notifier.py"
    if not notifier.exists():
        return
    msg = (
        f"Informe semanal TradingLab. "
        f"Planning: {planning['completadas']}/{planning['total']} ({planning['pct']}%). "
        f"Build: {pipeline['build_activo']}. "
        f"Databank: {pipeline['strategies_csv']} estrategias. "
        f"EvalGate: {pipeline['evalgate_pasan']}/{pipeline['evalgate_total']}. "
        f"Portfolio: {pipeline['portfolio_size']} activas."
    )
    subprocess.run(
        [sys.executable, str(notifier), "--level", "INFO", "--message", msg],
        capture_output=True
    )


def main():
    parser = argparse.ArgumentParser(description="Auto Reporter — TradingLab")
    parser.add_argument("--output-dir", default="results", help="Carpeta de salida (default: results/)")
    parser.add_argument("--no-telegram", action="store_true", help="No enviar Telegram")
    parser.add_argument("--no-ollama",   action="store_true", help="No usar Ollama")
    args = parser.parse_args()

    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    week_str = datetime.now().strftime("%Y-W%W")
    date_str = datetime.now().strftime("%Y%m%d")

    print(f"Auto Reporter — {week_str}")

    pipeline       = _pipeline_state()
    portfolio      = _portfolio_metrics()
    lessons        = _structural_lessons()
    planning       = _planning_progress()
    next_actions   = _next_actions()
    sys_status     = _system_status()
    auto_status    = _autoaprendizaje_status()
    proxima_semana = _proxima_semana()

    ollama_text = None
    if not args.no_ollama:
        ollama_text = _ollama_summary(pipeline, planning)
        if ollama_text:
            print("  Resumen Ollama generado.")

    report_md = _generate_md(pipeline, portfolio, lessons, planning,
                             next_actions, sys_status, ollama_text, week_str,
                             auto_status, proxima_semana)

    out_path = output_dir / f"weekly-report-{date_str}.md"
    out_path.write_text(report_md, encoding="utf-8")
    print(f"  Informe guardado: {out_path}")

    _send_telegram(pipeline, planning, args.no_telegram)

    print(f"\nResumen:")
    print(f"  Planning       : {planning['completadas']}/{planning['total']} ({planning['pct']}%)")
    print(f"  Build          : {pipeline['build_activo']}")
    print(f"  Portfolio      : {pipeline['portfolio_size']} estrategias")
    print(f"  Sistema        : {sys_status}")
    print(f"  Autoaprendizaje: [{auto_status.get('overall', 'OK')}]")


if __name__ == "__main__":
    main()
