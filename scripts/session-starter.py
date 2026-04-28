#!/usr/bin/env python3
"""
session-starter.py — Preparacion del entorno al inicio de cada sesion

Uso:
    python scripts/session-starter.py
    python scripts/session-starter.py --device alber
    python scripts/session-starter.py --device ivano
"""

import argparse
import json
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
RESULTS_DIR = ROOT / "results"
SESSION_LOG = RESULTS_DIR / "session-log.json"


def _auto_detect_device() -> str:
    hostname = socket.gethostname().lower()
    if "alber" in hostname:
        return "alber"
    return "ivano"


def _run_health_check() -> str:
    """Ejecuta system-health-check.py y devuelve el veredicto."""
    health_script = ROOT / "scripts" / "system-health-check.py"
    if not health_script.exists():
        return "HEALTH CHECK NO DISPONIBLE"

    result = subprocess.run(
        [sys.executable, str(health_script)],
        capture_output=True, text=True, cwd=ROOT
    )
    # Extraer ultima linea de veredicto
    lines = result.stdout.strip().splitlines()
    for line in reversed(lines):
        if any(v in line for v in ["SISTEMA LISTO", "ADVERTENCIAS", "SISTEMA CON ERRORES"]):
            return line.strip().lstrip("→ ").strip()
    return "SISTEMA LISTO" if result.returncode == 0 else "ADVERTENCIAS"


def _show_build_status():
    """Muestra estado del build activo desde pipeline.lock."""
    lock_path = RESULTS_DIR / "pipeline.lock"
    if lock_path.exists():
        content = lock_path.read_text(encoding="utf-8").strip()
        print(f"  Build activo    : {content}")
    else:
        print("  Build activo    : sin pipeline.lock — no hay build corriendo")


def _count_strategies() -> int:
    """Cuenta archivos Strategy*.csv en results/."""
    count = len(list(RESULTS_DIR.rglob("Strategy*.csv")))
    return count


def _last_audit_entry() -> str:
    """Ultima entrada del audit trail (hash-logger)."""
    audit_path = RESULTS_DIR / "audit-trail.log"
    if not audit_path.exists():
        return "audit-trail.log no existe aun"
    lines = audit_path.read_text(encoding="utf-8").splitlines()
    non_empty = [l for l in lines if l.strip()]
    if non_empty:
        return non_empty[-1][:100]
    return "sin entradas"


def _structural_lessons() -> list[str]:
    """Lee las 2 primeras lecciones ESTRUCTURAL de lessons-learned.md."""
    lessons_path = ROOT / "docs" / "lessons-learned.md"
    if not lessons_path.exists():
        return ["docs/lessons-learned.md no encontrado"]

    content = lessons_path.read_text(encoding="utf-8")
    lessons = []
    for line in content.splitlines():
        if "ESTRUCTURAL" in line.upper() and line.strip().startswith("|"):
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if cells:
                lessons.append(cells[0][:80])
            if len(lessons) >= 2:
                break
    if not lessons:
        # Buscar lineas con "## " que sean lecciones
        for line in content.splitlines():
            if line.startswith("## ") and len(line) > 4:
                lessons.append(line.lstrip("# ").strip()[:80])
            if len(lessons) >= 2:
                break
    return lessons if lessons else ["Sin lecciones estructurales registradas aun"]


def _next_action() -> str:
    """Lee la proxima accion desde project-status.md."""
    status_path = ROOT / "docs" / "project-status.md"
    if not status_path.exists():
        return "docs/project-status.md no encontrado"

    content = status_path.read_text(encoding="utf-8")
    in_next = False
    for line in content.splitlines():
        if "SIGUIENTE ACCION" in line.upper() or "PROXIMA ACCION" in line.upper():
            in_next = True
            continue
        if in_next and line.strip() and not line.startswith("#"):
            return line.strip().lstrip("*- ").strip()[:120]
    return "Ver docs/project-status.md para proxima accion"


def _send_telegram(device: str, health: str):
    """Notifica inicio de sesion via telegram-notifier.py."""
    notifier = ROOT / "scripts" / "telegram-notifier.py"
    if not notifier.exists():
        return
    msg = f"Sesion iniciada en {device}. Sistema: {health}"
    subprocess.run(
        [sys.executable, str(notifier), "--level", "INFO", "--message", msg],
        cwd=ROOT, capture_output=True
    )


def _log_session(device: str, health: str):
    """Crea entrada en results/session-log.json."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    entries = []
    if SESSION_LOG.exists():
        try:
            entries = json.loads(SESSION_LOG.read_text(encoding="utf-8"))
        except Exception:
            entries = []
    entries.append({
        "timestamp": datetime.now().isoformat(),
        "device": device,
        "health": health,
        "type": "start"
    })
    # Mantener solo los ultimos 100 registros
    entries = entries[-100:]
    SESSION_LOG.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Session Starter — TradingLab")
    parser.add_argument("--device", choices=["ivano", "alber"],
                        default=None, help="Dispositivo (default: auto-detectar)")
    args = parser.parse_args()

    device = args.device or _auto_detect_device()

    print("=" * 60)
    print(f"  TradingLab — Inicio de Sesion")
    print(f"  Dispositivo : {device}")
    print(f"  Fecha       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. Health check
    print("\n[1/7] Ejecutando system-health-check...")
    health = _run_health_check()
    print(f"      → {health}")

    # 2. Build activo
    print("\n[2/7] Estado del build activo")
    _show_build_status()

    # 3. Estrategias en results/
    print("\n[3/7] Estrategias en results/")
    n = _count_strategies()
    print(f"  Archivos Strategy*.csv : {n}")

    # 4. Ultima entrada audit trail
    print("\n[4/7] Ultima entrada audit trail")
    audit = _last_audit_entry()
    print(f"  {audit}")

    # 5. Lecciones estructurales
    print("\n[5/7] Lecciones estructurales")
    lessons = _structural_lessons()
    for i, l in enumerate(lessons, 1):
        print(f"  {i}. {l}")

    # 6. Proxima accion
    print("\n[6/7] Proxima accion (project-status.md)")
    action = _next_action()
    print(f"  → {action}")

    # 7. Telegram + log
    print("\n[7/7] Notificacion Telegram y log de sesion")
    _send_telegram(device, health)
    _log_session(device, health)
    print(f"  Sesion registrada en results/session-log.json")

    print("\n" + "=" * 60)
    print("  Entorno listo. Puedes empezar a trabajar.")
    print(f"  git pull origin main  (si no lo has hecho)")
    print("=" * 60)


if __name__ == "__main__":
    main()
