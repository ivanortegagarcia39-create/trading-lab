#!/usr/bin/env python3
"""
auto-build-launcher.py — Lanza el siguiente build automáticamente.

Lee el ranking de activos, determina el siguiente build,
lanza sqcli Builder y actualiza el pipeline.lock.

Uso:
    python scripts/auto-build-launcher.py
    python scripts/auto-build-launcher.py --dry-run
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

ROOT    = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"
RESULTS = ROOT / "results"

RANKING_PATH = RESULTS / "asset-viability-ranking.json"
LOCK_PATH    = RESULTS / "pipeline.lock"

# Spreads reales por activo (pips)
DEFAULT_SPREADS = {
    "EURUSD": 0.5,
    "GBPUSD": 0.8,
    "USDJPY": 0.5,
    "USDCHF": 0.8,
    "AUDUSD": 0.8,
    "NZDUSD": 1.0,
    "USDCAD": 1.0,
    "GBPJPY": 1.5,
    "EURJPY": 1.0,
    "EURGBP": 0.8,
    "XAUUSD": 30.0,
    "XAGUSD": 3.0,
}


def _ok(msg: str) -> None:
    print(f"    OK  {msg}")


def _warn(msg: str) -> None:
    print(f"    WARN  {msg}")


def _step(n: int, msg: str) -> None:
    print(f"\n[{n}] {msg}")


def _header(msg: str) -> None:
    print(f"\n{'='*60}\n  {msg}\n{'='*60}")


def _notify(level: str, msg: str) -> None:
    notifier = SCRIPTS / "telegram-notifier.py"
    if not notifier.exists():
        return
    subprocess.run(
        [sys.executable, str(notifier), "--level", level, "--message", msg],
        capture_output=True,
    )


def get_next_asset() -> dict | None:
    """Devuelve el primer activo en ranking que no sea ACTIVO ni DESCARTADO."""
    if not RANKING_PATH.exists():
        print(f"  ERROR: {RANKING_PATH} no encontrado")
        return None
    data = json.loads(RANKING_PATH.read_text(encoding="utf-8"))
    for item in data.get("ranking", []):
        estado = item.get("estado", "").upper()
        if "ACTIVO" in estado or "DESCARTADO" in estado:
            continue
        return item
    return None


def get_current_build() -> int:
    """Lee pipeline.lock y devuelve el build actual (0 si no existe)."""
    if not LOCK_PATH.exists():
        return 0
    try:
        return json.loads(LOCK_PATH.read_text(encoding="utf-8")).get("build", 0)
    except Exception:
        return 0


def update_pipeline_lock(build: int, activo: str, spread: float, dry_run: bool) -> None:
    lock = {
        "build":       build,
        "activo":      activo,
        "spread_real": spread,
        "started":     datetime.now().isoformat(),
        "status":      "running",
    }
    if dry_run:
        print(f"  [DRY-RUN] pipeline.lock: {json.dumps(lock)}")
        return
    LOCK_PATH.write_text(json.dumps(lock, indent=2), encoding="utf-8")
    _ok(f"pipeline.lock actualizado — Build {build} {activo}")


def update_ranking_estado(activo: str, build: int, dry_run: bool) -> None:
    if not RANKING_PATH.exists():
        return
    data = json.loads(RANKING_PATH.read_text(encoding="utf-8"))
    for item in data.get("ranking", []):
        if item.get("activo", "").upper() == activo.upper():
            item["estado"] = f"ACTIVO - Build {build}"
            break
    if dry_run:
        print(f"  [DRY-RUN] ranking: {activo} -> ACTIVO - Build {build}")
        return
    RANKING_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    _ok(f"Ranking actualizado: {activo} → ACTIVO - Build {build}")


def run_sq_project_generator(build: int, activo: str, spread: float, dry_run: bool) -> bool:
    cmd = [
        sys.executable,
        str(SCRIPTS / "sq-project-generator.py"),
        "--build", str(build),
        "--activo", activo,
        "--spread-real", str(spread),
    ]
    if dry_run:
        print(f"  [DRY-RUN] {' '.join(cmd)}")
        return True
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        _warn(f"sq-project-generator falló: {result.stderr[:200]}")
        return False
    _ok("sq-project-generator completado")
    return True


def close_sq_gui(dry_run: bool) -> None:
    if dry_run:
        print("  [DRY-RUN] taskkill StrategyQuantX.exe + espera 5s")
        return
    subprocess.run(
        ["taskkill", "/F", "/IM", "StrategyQuantX.exe"],
        capture_output=True,
    )
    _ok("SQ GUI cerrado (o no estaba abierto)")
    time.sleep(5)


def launch_builder(build: int, activo: str, dry_run: bool) -> bool:
    cmd = [
        sys.executable,
        str(SCRIPTS / "sqcli-pipeline.py"),
        "--builder",
        "--build", str(build),
        "--activo", activo,
    ]
    if dry_run:
        print(f"  [DRY-RUN] {' '.join(cmd)}")
        return True
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        _warn(f"sqcli-pipeline --builder falló: {result.stderr[:200]}")
        return False
    _ok("Builder lanzado via sqcli")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Auto Build Launcher — TradingLab")
    parser.add_argument("--dry-run", action="store_true", help="Simular sin ejecutar nada")
    args = parser.parse_args()

    _header("AUTO BUILD LAUNCHER")

    # Paso 1: siguiente activo
    _step(1, "Buscando siguiente activo en cola...")
    next_asset = get_next_asset()
    if next_asset is None:
        print("  No hay activos disponibles en cola. Pipeline finalizado.")
        _notify("WARNING", "Auto-launcher: no hay activos en cola. Pipeline detenido.")
        return 0

    activo = next_asset["activo"].upper()
    spread = DEFAULT_SPREADS.get(activo, 1.0)
    _ok(f"Siguiente activo: {activo} (spread real: {spread} pips)")

    # Paso 2: calcular número de build
    _step(2, "Calculando número de build...")
    current_build = get_current_build()
    next_build    = current_build + 1
    _ok(f"Build actual: {current_build} -> Siguiente: {next_build}")

    # Paso 3: generar proyecto SQ
    _step(3, f"Generando proyecto SQ (build {next_build} — {activo})...")
    if not run_sq_project_generator(next_build, activo, spread, args.dry_run):
        _notify("WARNING", f"Auto-launcher: sq-project-generator falló para {activo}.")
        return 1

    # Paso 4: cerrar SQ GUI
    _step(4, "Cerrando SQ GUI si está abierto...")
    close_sq_gui(args.dry_run)

    # Paso 5: lanzar Builder via sqcli
    _step(5, "Lanzando Builder via sqcli-pipeline...")
    if not launch_builder(next_build, activo, args.dry_run):
        _notify("WARNING", f"Auto-launcher: sqcli Builder falló para {activo}.")
        return 1

    # Paso 6: actualizar pipeline.lock
    _step(6, "Actualizando pipeline.lock...")
    update_pipeline_lock(next_build, activo, spread, args.dry_run)

    # Paso 7: notificar Telegram
    _step(7, "Notificando Telegram...")
    msg = f"Build {next_build} lanzado automaticamente — {activo}"
    if not args.dry_run:
        _notify("INFO", f"🚀 {msg}")
    else:
        print(f"  [DRY-RUN] Telegram: {msg}")
    _ok("Telegram notificado")

    # Paso 8: marcar activo en ranking
    _step(8, "Actualizando ranking...")
    update_ranking_estado(activo, next_build, args.dry_run)

    _header(f"Build {next_build} lanzado — {activo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
