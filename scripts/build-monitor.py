#!/usr/bin/env python3
"""
build-monitor.py — Monitorea el progreso de un build activo en SQ en tiempo real.

Uso:
    python scripts/build-monitor.py --once
    python scripts/build-monitor.py --watch
    python scripts/build-monitor.py --watch --build 11
"""

import argparse
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent

SQ_LOG_DIRS = [
    Path(os.environ.get("APPDATA", "")) / "StrategyQuantX" / "logs",
    Path("C:/Users") / os.environ.get("USERNAME", "") / "AppData" / "Roaming" / "StrategyQuantX" / "logs",
]

WATCH_INTERVAL_SEC  = 300   # 5 minutos
STALL_THRESHOLD_MIN = 30    # alerta si sin progreso > 30 min
PF_ALERT_THRESHOLD  = 1.5


def _find_sq_log_dir() -> Path | None:
    for p in SQ_LOG_DIRS:
        if p.exists():
            return p
    return None


def _latest_log(log_dir: Path) -> Path | None:
    logs = sorted(log_dir.glob("*.log"), key=lambda f: f.stat().st_mtime, reverse=True)
    return logs[0] if logs else None


def _parse_sq_log(log_path: Path) -> dict:
    """Extrae métricas del log de SQ con patrones flexibles."""
    stats = {
        "generated": 0,
        "databank":  0,
        "best_pf":   0.0,
        "last_event": None,
        "log_lines":  0,
    }
    try:
        content = log_path.read_text(encoding="utf-8", errors="ignore")
        lines   = content.splitlines()
        stats["log_lines"] = len(lines)

        for line in lines:
            # Estrategias generadas
            m = re.search(r"(?:generated|generadas?)[^\d]*(\d+)", line, re.IGNORECASE)
            if m:
                stats["generated"] = max(stats["generated"], int(m.group(1)))

            # Databank
            m = re.search(r"(?:databank|bank)[^\d]*(\d+)", line, re.IGNORECASE)
            if m:
                stats["databank"] = max(stats["databank"], int(m.group(1)))

            # Mejor PF
            m = re.search(r"(?:pf|profit\s*factor)[^\d]*(\d+\.?\d*)", line, re.IGNORECASE)
            if m:
                pf = float(m.group(1))
                if 1.0 < pf < 20.0:
                    stats["best_pf"] = max(stats["best_pf"], pf)

            # Timestamp de ultimo evento
            m = re.search(r"(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2})", line)
            if m:
                try:
                    stats["last_event"] = datetime.fromisoformat(m.group(1).replace(" ", "T"))
                except ValueError:
                    pass

    except Exception:
        pass
    return stats


def _compute_rate(stats: dict, log_mtime: datetime) -> float:
    """Estrategias/hora basado en el tiempo de vida del log."""
    if stats["generated"] == 0:
        return 0.0
    age_hours = (datetime.now() - log_mtime).total_seconds() / 3600
    if age_hours < 0.01:
        return 0.0
    return round(stats["generated"] / max(age_hours, 0.01), 1)


def _eta(generated: int, rate: float) -> str:
    """ETA simple: si vamos a 1000 estrategias meta."""
    TARGET = 1000
    if rate <= 0 or generated >= TARGET:
        return "N/A"
    remaining = TARGET - generated
    hours = remaining / rate
    eta_dt = datetime.now() + timedelta(hours=hours)
    return eta_dt.strftime("%H:%M")


def _build_status(stats: dict, rate: float) -> str:
    if stats["log_lines"] == 0:
        return "NO LOG"
    last = stats["last_event"]
    if last is None:
        return "RUNNING"
    mins_since = (datetime.now() - last).total_seconds() / 60
    if mins_since > STALL_THRESHOLD_MIN:
        return "STALLED"
    if stats["generated"] == 0:
        return "STARTING"
    return "RUNNING"


def _send_telegram(level: str, msg: str) -> None:
    notifier = ROOT / "scripts" / "telegram-notifier.py"
    if not notifier.exists():
        return
    subprocess.run(
        [sys.executable, str(notifier), "--level", level, "--message", msg],
        capture_output=True, cwd=ROOT
    )


def _print_dashboard(build_n: int | None, stats: dict, rate: float, status: str, log_path: Path | None) -> None:
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bld  = f"Build {build_n}" if build_n else "Build activo"
    eta  = _eta(stats["generated"], rate)

    print("\033[2J\033[H", end="")  # clear screen
    print("=" * 55)
    print(f"  BUILD MONITOR — {bld}")
    print(f"  {now}")
    print("=" * 55)
    print(f"  Estado          : {status}")
    print(f"  Estrategias gen.: {stats['generated']:,}")
    print(f"  En databank     : {stats['databank']:,}")
    print(f"  Tasa generacion : {rate:.1f} estrategias/hora")
    print(f"  ETA (1000 gen.) : {eta}")
    pf_str = f"{stats['best_pf']:.2f}" if stats["best_pf"] > 0 else "sin datos"
    print(f"  Mejor PF        : {pf_str}")
    last = stats["last_event"].strftime("%H:%M:%S") if stats["last_event"] else "?"
    print(f"  Ultimo evento   : {last}")
    if log_path:
        print(f"  Log activo      : {log_path.name}")
    print("=" * 55)
    print("  Ctrl+C para salir")


def _check_and_alert(stats: dict, status: str, prev_databank: int, prev_pf: float) -> tuple[int, float]:
    """Envía alertas Telegram si hay eventos relevantes. Devuelve (nuevo_databank, nuevo_pf)."""
    # Primera estrategia en databank
    if stats["databank"] > 0 and prev_databank == 0:
        _send_telegram("INFO", f"Primera estrategia en databank. PF={stats['best_pf']:.2f}")

    # PF superó umbral
    if stats["best_pf"] >= PF_ALERT_THRESHOLD and prev_pf < PF_ALERT_THRESHOLD:
        _send_telegram("INFO", f"PF máximo supera {PF_ALERT_THRESHOLD}: {stats['best_pf']:.2f}")

    # STALLED
    if status == "STALLED":
        _send_telegram("WARN", f"SQ lleva >{STALL_THRESHOLD_MIN}min sin generar — posible freeze")

    return stats["databank"], stats["best_pf"]


def _show_once(build_n: int | None, log_dir: Path | None) -> None:
    if log_dir is None:
        print("WARN: directorio de logs SQ no encontrado.")
        _print_manual_instructions()
        return

    log_path = _latest_log(log_dir)
    if log_path is None:
        print("No se encontraron archivos .log en el directorio de SQ.")
        _print_manual_instructions()
        return

    stats    = _parse_sq_log(log_path)
    log_mtime = datetime.fromtimestamp(log_path.stat().st_mtime)
    rate     = _compute_rate(stats, log_mtime)
    status   = _build_status(stats, rate)
    _print_dashboard(build_n, stats, rate, status, log_path)


def _watch_loop(build_n: int | None, log_dir: Path | None) -> None:
    if log_dir is None:
        print("WARN: directorio de logs SQ no encontrado.")
        _print_manual_instructions()
        return

    prev_databank = 0
    prev_pf       = 0.0

    try:
        while True:
            log_path = _latest_log(log_dir)
            if log_path:
                stats     = _parse_sq_log(log_path)
                log_mtime = datetime.fromtimestamp(log_path.stat().st_mtime)
                rate      = _compute_rate(stats, log_mtime)
                status    = _build_status(stats, rate)
                _print_dashboard(build_n, stats, rate, status, log_path)
                prev_databank, prev_pf = _check_and_alert(stats, status, prev_databank, prev_pf)
            else:
                print(f"[{datetime.now().strftime('%H:%M')}] Sin log SQ activo — reintentando en {WATCH_INTERVAL_SEC}s")

            time.sleep(WATCH_INTERVAL_SEC)
    except KeyboardInterrupt:
        print("\nMonitor detenido.")


def _print_manual_instructions() -> None:
    print("\n--- VERIFICACION MANUAL EN SQ ---")
    print("Builder → Statistics tab:")
    print("  - Estrategias generadas: columna 'Generated'")
    print("  - Databank: columna 'Passed'")
    print("  - Mejor PF: columna 'Best PF'")
    print("\nLog de SQ esperado en:")
    for p in SQ_LOG_DIRS:
        print(f"  {p}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Monitor — TradingLab")
    parser.add_argument("--watch", action="store_true", help="Modo continuo (actualiza cada 5 min)")
    parser.add_argument("--once",  action="store_true", help="Mostrar estado una vez y salir")
    parser.add_argument("--build", type=int, default=None, help="Número de build a monitorear")
    args = parser.parse_args()

    if not args.watch and not args.once:
        args.once = True  # default

    log_dir = _find_sq_log_dir()

    if args.watch:
        _watch_loop(args.build, log_dir)
    else:
        _show_once(args.build, log_dir)

    return 0


if __name__ == "__main__":
    sys.exit(main())
