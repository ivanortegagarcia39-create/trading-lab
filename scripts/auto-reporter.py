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
        # 3. Buscar "Estado:" en las siguientes 20 líneas
        estado = None
        for j in range(1, min(21, len(history) - i)):
            candidate = history[i + j].strip()
            if candidate.lower().startswith("estado:"):
                estado = candidate.split(":", 1)[1].strip().upper()
                break
        # 4. Incluir solo ESTRUCTURAL o PERMANENTE
        if estado in ("ESTRUCTURAL", "PERMANENTE"):
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


# ── 6. Estado del sistema ──────────────────────────────────────────────────

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
                 ollama_text: str | None, week_str: str) -> str:
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
{ollama_section}
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

    pipeline     = _pipeline_state()
    portfolio    = _portfolio_metrics()
    lessons      = _structural_lessons()
    planning     = _planning_progress()
    next_actions = _next_actions()
    sys_status   = _system_status()

    ollama_text = None
    if not args.no_ollama:
        ollama_text = _ollama_summary(pipeline, planning)
        if ollama_text:
            print("  Resumen Ollama generado.")

    report_md = _generate_md(pipeline, portfolio, lessons, planning,
                             next_actions, sys_status, ollama_text, week_str)

    out_path = output_dir / f"weekly-report-{date_str}.md"
    out_path.write_text(report_md, encoding="utf-8")
    print(f"  Informe guardado: {out_path}")

    _send_telegram(pipeline, planning, args.no_telegram)

    print(f"\nResumen:")
    print(f"  Planning   : {planning['completadas']}/{planning['total']} ({planning['pct']}%)")
    print(f"  Build      : {pipeline['build_activo']}")
    print(f"  Portfolio  : {pipeline['portfolio_size']} estrategias")
    print(f"  Sistema    : {sys_status}")


if __name__ == "__main__":
    main()
