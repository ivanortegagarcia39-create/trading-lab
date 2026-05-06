#!/usr/bin/env python3
"""
sqcli-pipeline.py — Controla proyectos de SQ via sqcli.exe (modo headless).

REQUISITO: sqcli.exe requiere que el SQ GUI este CERRADO.
           Ambos usan el puerto 5050 como instancia unica.

Uso:
    python scripts/sqcli-pipeline.py --retester  --build 11 --activo XAUUSD
    python scripts/sqcli-pipeline.py --wfo        --build 11 --activo XAUUSD
    python scripts/sqcli-pipeline.py --monitor    --project Retester
    python scripts/sqcli-pipeline.py --copy-db    --from-project Builder --to-project Retester
"""

import argparse
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT   = Path(__file__).parent.parent
SQCLI  = Path(r"D:\sqcli.exe")
CONFIGS = Path(r"D:\user\settings\Configs")

# Nombre de databank usado como origen/destino entre proyectos
DB_RESULTS = "Results"
DB_INPUT   = "Input"

# Mapeo activo → archivo .cfx
CFX_MAP = {
    "XAUUSD": "XAUUSD CFD H1.cfx",
    "XAGUSD": "XAGUSD CFD H1.cfx",
    "EURUSD": "EURUSD FX H1.cfx",
    "GBPUSD": "GBPUSD FX H1.cfx",
    "USDJPY": "USDJPY FX H1.cfx",
    "GBPJPY": "GBPJPY FX H1.cfx",
    "NAS100": "NQ CFD H1.cfx",
    "US30":   "DJ CFD H1.cfx",
}


def _sq_running() -> bool:
    """True si el SQ GUI esta ocupando el puerto 5050."""
    try:
        with socket.create_connection(("localhost", 5050), timeout=1):
            return True
    except OSError:
        return False


def _sqcli(*args: str, timeout: int = 120) -> tuple[int, str]:
    """
    Ejecuta sqcli.exe con los argumentos dados.
    Devuelve (returncode, stdout+stderr combinados).
    """
    cmd = [str(SQCLI)] + list(args)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode, output
    except subprocess.TimeoutExpired:
        return -1, f"sqcli timeout tras {timeout}s"
    except FileNotFoundError:
        return -1, f"sqcli no encontrado en {SQCLI}"


def _cfx_path(activo: str) -> Path | None:
    """Devuelve la ruta al .cfx del activo, o None si no existe."""
    name = CFX_MAP.get(activo.upper())
    if name:
        p = CONFIGS / name
        return p if p.exists() else None
    # Busqueda por patron si no esta en el mapa
    matches = list(CONFIGS.glob(f"{activo.upper()}*.cfx"))
    return matches[0] if matches else None


def run_retester(build: int, activo: str) -> bool:
    """
    Carga la config del activo en el proyecto Retester y lo arranca.
    Prerequisito: estrategias ya copiadas al databank Input de Retester.
    """
    activo = activo.upper()
    cfx = _cfx_path(activo)
    if cfx is None:
        print(f"  ERROR: no se encontro .cfx para {activo} en {CONFIGS}")
        return False

    print(f"  Cargando config: {cfx.name} → Retester")
    rc, out = _sqcli("-project", f"action=loadconfig", f"name=Retester", f"file={cfx}")
    if rc != 0:
        print(f"  ERROR loadconfig: {out}")
        return False

    print("  Iniciando proyecto Retester...")
    rc, out = _sqcli("-project", "action=start", "name=Retester")
    if rc != 0:
        print(f"  ERROR start: {out}")
        return False

    print(f"  Retester iniciado — Build {build} | {activo}")
    return True


def run_wfo(build: int, activo: str) -> bool:
    """
    Carga la config del activo en el proyecto Optimizer y lo arranca.
    Prerequisito: estrategias ya copiadas al databank Input de Optimizer.
    """
    activo = activo.upper()
    cfx = _cfx_path(activo)
    if cfx is None:
        print(f"  ERROR: no se encontro .cfx para {activo} en {CONFIGS}")
        return False

    print(f"  Cargando config: {cfx.name} → Optimizer")
    rc, out = _sqcli("-project", "action=loadconfig", "name=Optimizer", f"file={cfx}")
    if rc != 0:
        print(f"  ERROR loadconfig: {out}")
        return False

    print("  Iniciando proyecto Optimizer (WFO)...")
    rc, out = _sqcli("-project", "action=start", "name=Optimizer")
    if rc != 0:
        print(f"  ERROR start: {out}")
        return False

    print(f"  WFO iniciado — Build {build} | {activo}")
    return True


def monitor_project(project_name: str, poll_interval: int = 30, timeout_hours: int = 24) -> str:
    """
    Consulta el estado del proyecto cada poll_interval segundos
    hasta que no este RUNNING o se alcance timeout_hours.
    Devuelve el estado final como string.
    """
    deadline = time.time() + timeout_hours * 3600
    print(f"  Monitoreando {project_name} (poll cada {poll_interval}s, timeout {timeout_hours}h)...")

    while time.time() < deadline:
        rc, out = _sqcli("-project", "action=status", f"name={project_name}", timeout=30)

        if rc != 0:
            print(f"  WARN sqcli status error: {out}")
            time.sleep(poll_interval)
            continue

        # El output de sqcli status contiene lineas como "Status: RUNNING"
        status = "UNKNOWN"
        for line in out.splitlines():
            line_up = line.upper()
            if "RUNNING" in line_up:
                status = "RUNNING"
                break
            if "FINISHED" in line_up or "DONE" in line_up:
                status = "FINISHED"
                break
            if "STOPPED" in line_up or "PAUSED" in line_up:
                status = "STOPPED"
                break
            if "STATUS:" in line_up:
                status = line.split(":", 1)[-1].strip().upper()

        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  [{ts}] {project_name}: {status}")

        if status != "RUNNING":
            return status

        time.sleep(poll_interval)

    return "TIMEOUT"


def copy_databank(from_project: str, to_project: str,
                  from_db: str = DB_RESULTS, to_db: str = DB_INPUT) -> bool:
    """
    Copia el databank from_db del proyecto origen al databank to_db del destino.
    Uso tipico: Builder/Results → Retester/Input, Retester/Results → Optimizer/Input.
    """
    print(f"  Copiando {from_project}/{from_db} → {to_project}/{to_db}...")
    rc, out = _sqcli(
        "-databank",
        "action=copy",
        f"project={from_project}",
        f"name={from_db}",
        f"toproject={to_project}",
        f"toname={to_db}",
    )
    if rc != 0:
        print(f"  ERROR copy databank: {out}")
        return False
    print(f"  Copia completada")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="sqcli Pipeline — TradingLab")
    parser.add_argument("--retester",     action="store_true", help="Cargar config y arrancar Retester")
    parser.add_argument("--wfo",          action="store_true", help="Cargar config y arrancar WFO (Optimizer)")
    parser.add_argument("--monitor",      action="store_true", help="Monitorear proyecto hasta que termine")
    parser.add_argument("--copy-db",      action="store_true", help="Copiar databank entre proyectos")
    parser.add_argument("--build",        type=int,            help="Numero del build")
    parser.add_argument("--activo",                            help="Activo (ej: XAUUSD)")
    parser.add_argument("--project",                           help="Nombre del proyecto SQ para --monitor")
    parser.add_argument("--from-project",                      help="Proyecto origen para --copy-db")
    parser.add_argument("--to-project",                        help="Proyecto destino para --copy-db")
    parser.add_argument("--poll",         type=int, default=30, help="Segundos entre polls (default: 30)")
    args = parser.parse_args()

    if not any([args.retester, args.wfo, args.monitor, args.copy_db]):
        parser.print_help()
        return 0

    if not SQCLI.exists():
        print(f"ERROR: sqcli.exe no encontrado en {SQCLI}")
        return 1

    if _sq_running():
        print("ERROR: SQ GUI esta corriendo en el puerto 5050.")
        print("       sqcli no puede ejecutarse simultaneamente con el GUI.")
        print("       Cierra StrategyQuant X antes de usar este script.")
        return 1

    if args.retester:
        if not args.build or not args.activo:
            print("ERROR: --retester requiere --build y --activo")
            return 1
        ok = run_retester(args.build, args.activo)
        return 0 if ok else 1

    if args.wfo:
        if not args.build or not args.activo:
            print("ERROR: --wfo requiere --build y --activo")
            return 1
        ok = run_wfo(args.build, args.activo)
        return 0 if ok else 1

    if args.monitor:
        if not args.project:
            print("ERROR: --monitor requiere --project")
            return 1
        status = monitor_project(args.project, poll_interval=args.poll)
        print(f"\n  Estado final: {status}")
        return 0 if status in ("FINISHED", "STOPPED") else 1

    if args.copy_db:
        if not args.from_project or not args.to_project:
            print("ERROR: --copy-db requiere --from-project y --to-project")
            return 1
        ok = copy_databank(args.from_project, args.to_project)
        return 0 if ok else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
