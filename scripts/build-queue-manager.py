#!/usr/bin/env python3
"""
build-queue-manager.py — Gestiona la cola de builds pendientes.

Uso:
    python scripts/build-queue-manager.py list
    python scripts/build-queue-manager.py next
    python scripts/build-queue-manager.py complete XAUUSD
    python scripts/build-queue-manager.py add EURUSD 75 "Siguiente tras XAUUSD ciclo 2"
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT       = Path(__file__).parent.parent
QUEUE_FILE = ROOT / "results" / "build-queue.json"

DEFAULT_QUEUE = [
    {
        "activo":  "XAUUSD",
        "score":   80,
        "razon":   "Build 10 completado (spread 30 pips). Build 11 pendiente con spread 60 pips.",
        "estado":  "EN_CURSO",
        "build":   11,
        "tf":      "H1",
        "notas":   "Spread corregido a 60 pips. Lanzar en alber.",
        "fecha_add": "2026-04-27",
    },
    {
        "activo":  "EURUSD",
        "score":   80,
        "razon":   "Siguiente tras XAUUSD. Score 80 — mismo nivel de prioridad.",
        "estado":  "PENDIENTE",
        "build":   None,
        "tf":      "H1",
        "notas":   "Comisiones: spread 0.5 pips + 7 USD/lote. Verificar antes del build.",
        "fecha_add": "2026-04-27",
    },
    {
        "activo":  "GBPUSD",
        "score":   None,
        "razon":   "Recalcular score tras Ciclo 1 completo.",
        "estado":  "PENDIENTE",
        "build":   None,
        "tf":      "H1",
        "notas":   "Score TBD — esperar resultados de XAUUSD y EURUSD.",
        "fecha_add": "2026-04-27",
    },
    {
        "activo":  "USDJPY",
        "score":   None,
        "razon":   "Recalcular score tras Ciclo 1 completo.",
        "estado":  "PENDIENTE",
        "build":   None,
        "tf":      "H1",
        "notas":   "Score TBD — esperar resultados de XAUUSD y EURUSD.",
        "fecha_add": "2026-04-27",
    },
]


def _load_queue() -> list:
    if QUEUE_FILE.exists():
        try:
            return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return list(DEFAULT_QUEUE)


def _save_queue(queue: list) -> None:
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_FILE.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")


def cmd_list(queue: list) -> None:
    print(f"Cola de Builds — {len(queue)} activos\n{'='*60}")
    for i, item in enumerate(queue, 1):
        score = item.get("score") or "TBD"
        build = f"Build {item['build']}" if item.get("build") else "—"
        estado = item["estado"]
        marker = "▶" if estado == "EN_CURSO" else " "
        print(f"{marker} {i}. {item['activo']:<10} Score:{score:<5} {estado:<12} {build}")
        print(f"      {item['razon']}")
        if item.get("notas"):
            print(f"      Notas: {item['notas']}")
    print()


def cmd_next(queue: list) -> None:
    activo = next(
        (q for q in queue if q["estado"] in ("PENDIENTE", "EN_CURSO")),
        None
    )
    if not activo:
        print("Cola vacía — no hay builds pendientes.")
        return

    print(f"\nPróximo build: {activo['activo']}")
    print(f"{'='*40}")
    print(f"Activo   : {activo['activo']}")
    print(f"TF       : {activo.get('tf', 'H1')}")
    print(f"Score    : {activo.get('score') or 'TBD'}")
    print(f"Estado   : {activo['estado']}")
    print(f"Build N  : {activo.get('build') or 'Asignar al lanzar'}")
    print(f"Razón    : {activo['razon']}")
    print(f"Notas    : {activo.get('notas', '—')}")
    print()
    print("Acciones antes de lanzar:")
    print("  1. git pull origin main en alber")
    print("  2. Verificar datos M1 disponibles en SQ")
    print(f"  3. Verificar comisiones reales para {activo['activo']} en FTMO")
    print("  4. Configurar Builder según skill-builder-libre.md")
    print("  5. Lanzar en modo continuo 24-48h")


def cmd_complete(queue: list, activo_str: str) -> list:
    activo_str = activo_str.upper()
    idx = next((i for i, q in enumerate(queue) if q["activo"] == activo_str), None)
    if idx is None:
        print(f"Activo '{activo_str}' no encontrado en la cola.")
        return queue

    queue[idx]["estado"] = "COMPLETADO"
    queue[idx]["fecha_completado"] = datetime.now().strftime("%Y-%m-%d")

    # Activar el siguiente PENDIENTE
    for q in queue:
        if q["estado"] == "PENDIENTE":
            q["estado"] = "EN_CURSO"
            print(f"Build completado: {activo_str}")
            print(f"Siguiente activado: {q['activo']}")
            break
    else:
        print(f"Build completado: {activo_str}")
        print("No hay más builds pendientes en la cola.")

    return queue


def cmd_add(queue: list, activo_str: str, score_str: str, razon: str) -> list:
    activo_str = activo_str.upper()
    if any(q["activo"] == activo_str for q in queue):
        print(f"'{activo_str}' ya está en la cola. Usa 'list' para ver el estado.")
        return queue

    try:
        score = int(score_str)
    except ValueError:
        score = None

    queue.append({
        "activo":    activo_str,
        "score":     score,
        "razon":     razon,
        "estado":    "PENDIENTE",
        "build":     None,
        "tf":        "H1",
        "notas":     "",
        "fecha_add": datetime.now().strftime("%Y-%m-%d"),
    })
    print(f"Añadido: {activo_str} (score={score}) — {razon}")
    return queue


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Queue Manager — TradingLab")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list",  help="Mostrar cola completa")
    sub.add_parser("next",  help="Mostrar configuración del próximo build")

    p_complete = sub.add_parser("complete", help="Marcar build como completado")
    p_complete.add_argument("activo", help="Activo completado (ej: XAUUSD)")

    p_add = sub.add_parser("add", help="Añadir activo a la cola")
    p_add.add_argument("activo", help="Activo (ej: EURUSD)")
    p_add.add_argument("score",  help="Score del market-selector (ej: 75)")
    p_add.add_argument("razon",  help="Razón para incluir en la cola")

    args = parser.parse_args()
    queue = _load_queue()

    if args.command == "list":
        cmd_list(queue)

    elif args.command == "next":
        cmd_next(queue)

    elif args.command == "complete":
        queue = cmd_complete(queue, args.activo)
        _save_queue(queue)

    elif args.command == "add":
        queue = cmd_add(queue, args.activo, args.score, args.razon)
        _save_queue(queue)

    # Guardar si el archivo no existía aún
    if not QUEUE_FILE.exists():
        _save_queue(queue)

    return 0


if __name__ == "__main__":
    sys.exit(main())
