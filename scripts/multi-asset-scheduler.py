#!/usr/bin/env python3
"""
multi-asset-scheduler.py — Gestiona builds secuenciales multi-activo.

Cuando termina un build, usa Thompson Sampling para decidir el siguiente
activo y lanzarlo automaticamente.

Uso:
    python scripts/multi-asset-scheduler.py --next
    python scripts/multi-asset-scheduler.py --schedule
    python scripts/multi-asset-scheduler.py --run
"""

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT    = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"
RESULTS = ROOT / "results"

BUILD_DURATION_H = 48   # horas maximas por build


def _notify(level: str, msg: str) -> None:
    notifier = SCRIPTS / "telegram-notifier.py"
    if not notifier.exists():
        return
    subprocess.run(
        [sys.executable, str(notifier), "--level", level, "--message", msg],
        capture_output=True,
    )


def get_next_build_candidate() -> dict | None:
    """Consultar Thompson Sampling para el proximo activo optimo."""
    ts_script = SCRIPTS / "thompson-sampling.py"
    if not ts_script.exists():
        print("  thompson-sampling.py no encontrado")
        return None

    r = subprocess.run(
        [sys.executable, str(ts_script), "--next-asset"],
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0:
        print(f"  Error en Thompson Sampling: {r.stderr[:200]}")
        return None

    # Parsear activo y spread estimado de la salida
    for line in r.stdout.splitlines():
        m = re.search(r"([A-Z]{6}|XAU/?USD|XAG/?USD|US\d{2,3}).*?(\d+\.?\d*)\s*pips?",
                      line, re.IGNORECASE)
        if m:
            return {
                "activo":      m.group(1).replace("/", ""),
                "timeframe":   "H1",
                "spread_real": float(m.group(2)),
                "razon":       line.strip(),
            }

    # Fallback: tomar primer token que parezca activo
    for line in r.stdout.splitlines():
        m = re.search(r"\b([A-Z]{6}|XAU/?USD|XAG/?USD|US\d{2,3})\b", line)
        if m:
            return {
                "activo":      m.group(1).replace("/", ""),
                "timeframe":   "H1",
                "spread_real": 1.0,
                "razon":       line.strip(),
            }
    return None


def _get_current_build_n() -> int:
    """Determinar numero del build actual."""
    lock = RESULTS / "pipeline.lock"
    if lock.exists():
        m = re.search(r"build[_\s-]?(\d+)", lock.read_text(encoding="utf-8"), re.IGNORECASE)
        if m:
            return int(m.group(1))
    builds = list(RESULTS.glob("build-*-report.md")) + list(RESULTS.glob("build-*-config.md"))
    nums = [int(f.stem.split("-")[1]) for f in builds if f.stem.split("-")[1].isdigit()]
    return max(nums, default=10)


def schedule_next_build() -> dict | None:
    """Determinar y programar el proximo build."""
    candidate = get_next_build_candidate()
    if not candidate:
        return None

    build_n         = _get_current_build_n() + 1
    candidate["build_n"] = build_n

    # Actualizar cola
    queue_script = SCRIPTS / "build-queue-manager.py"
    if queue_script.exists():
        subprocess.run(
            [sys.executable, str(queue_script), "add",
             "--activo", candidate["activo"],
             "--spread", str(candidate["spread_real"])],
            capture_output=True, timeout=30,
        )

    msg = (f"Proximo build programado: Build {build_n} — {candidate['activo']} "
           f"(spread {candidate['spread_real']} pips)")
    print(f"  {msg}")
    _notify("INFO", msg)

    plan_path = RESULTS / "next-build-plan.json"
    plan_path.write_text(json.dumps(candidate, indent=2, ensure_ascii=False), encoding="utf-8")
    return candidate


def _wait_for_build_completion(build_n: int, max_hours: int = BUILD_DURATION_H) -> bool:
    """Esperar a que el Builder reporte estado FINISHED o timeout."""
    ctrl = SCRIPTS / "sq-controller.py"
    if not ctrl.exists():
        print(f"  sq-controller.py no encontrado — esperando {max_hours}h fijo")
        time.sleep(max_hours * 3600)
        return True

    deadline        = time.time() + max_hours * 3600
    last_count      = -1
    last_grow_time  = time.time()

    print(f"  Esperando fin del Build {build_n} (max {max_hours}h)...")
    while time.time() < deadline:
        r = subprocess.run(
            [sys.executable, str(ctrl), "--status"],
            capture_output=True, text=True, timeout=30,
        )
        for line in r.stdout.splitlines():
            if "finished" in line.lower():
                print("  Build finalizado (FINISHED)")
                return True
            m = re.search(r"\d+", line)
            if m and ("estrategia" in line.lower() or "databank" in line.lower()):
                count = int(m.group())
                if count != last_count:
                    last_count     = count
                    last_grow_time = time.time()

        # Sin crecimiento 6h = build terminado
        if last_count > 0 and (time.time() - last_grow_time) > 6 * 3600:
            print("  Build considerado finalizado (sin crecimiento en 6h)")
            return True

        time.sleep(900)

    print(f"  Timeout {max_hours}h alcanzado")
    return True


def run_continuous_scheduler() -> None:
    """Bucle principal: espera build actual, lanza siguiente."""
    print("Multi-asset scheduler iniciado — modo continuo")
    print("  Ctrl+C para detener\n")

    while True:
        build_n = _get_current_build_n()
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Build activo: {build_n}")

        _wait_for_build_completion(build_n)

        # Post-build
        finisher = SCRIPTS / "build-finisher.py"
        if finisher.exists():
            print(f"  Ejecutando build-finisher para Build {build_n}...")
            subprocess.run(
                [sys.executable, str(finisher),
                 "--build", str(build_n), "--activo", "AUTO", "--results-folder", "results/"],
                timeout=300,
            )

        candidate = schedule_next_build()
        if not candidate:
            print("  Sin candidato — reintento en 1h")
            time.sleep(3600)
            continue

        launcher = SCRIPTS / "build-launcher.py"
        if launcher.exists():
            print(f"  Lanzando Build {candidate['build_n']} — {candidate['activo']}...")
            subprocess.run(
                [sys.executable, str(launcher),
                 "--build",       str(candidate["build_n"]),
                 "--activo",      candidate["activo"],
                 "--spread-real", str(candidate["spread_real"]),
                 "--auto"],
                timeout=120,
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Multi-Asset Scheduler — TradingLab")
    parser.add_argument("--next",     action="store_true", help="Mostrar proximo activo sugerido")
    parser.add_argument("--schedule", action="store_true", help="Programar proximo build")
    parser.add_argument("--run",      action="store_true", help="Ejecutar scheduler continuo")
    args = parser.parse_args()

    if args.next:
        c = get_next_build_candidate()
        if c:
            print(f"  Proximo activo : {c['activo']}")
            print(f"  Timeframe      : {c['timeframe']}")
            print(f"  Spread estimado: {c['spread_real']} pips")
            print(f"  Razon          : {c['razon']}")
        else:
            print("  No se pudo determinar proximo candidato")

    elif args.schedule:
        c = schedule_next_build()
        if c:
            print(f"\n  Build {c['build_n']} programado — {c['activo']}")
            print("  Plan guardado en results/next-build-plan.json")

    elif args.run:
        try:
            run_continuous_scheduler()
        except KeyboardInterrupt:
            print("\nScheduler detenido.")
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
