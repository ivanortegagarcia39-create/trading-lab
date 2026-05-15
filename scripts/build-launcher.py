#!/usr/bin/env python3
"""
build-launcher.py — Guia el lanzamiento de un nuevo build en alber.
Lista de verificacion interactiva antes de iniciar el Builder en SQ.

Uso:
    python scripts/build-launcher.py --build 11 --activo XAUUSD --spread-real 30
    python scripts/build-launcher.py --build 11 --activo XAUUSD --spread-real 30 --dry-run
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT    = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"
RESULTS = ROOT / "results"


def _run(cmd: list) -> int:
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


def _run_quiet(cmd: list) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def _notify(level: str, msg: str) -> None:
    notifier = SCRIPTS / "telegram-notifier.py"
    if not notifier.exists():
        return
    subprocess.run(
        [sys.executable, str(notifier), "--level", level, "--message", msg],
        capture_output=True
    )


def _header(text: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def _step(n: int, text: str) -> None:
    print(f"\n[{n}] {text}")


def _ok(text: str) -> None:
    print(f"    OK  {text}")


def _warn(text: str) -> None:
    print(f"    WARN  {text}")


def run_data_validator(activo: str, dry_run: bool) -> bool:
    """PASO 0 — Verifica datos SQ disponibles antes de cualquier otra comprobacion."""
    _step(0, f"Verificando datos disponibles en SQ para {activo}...")
    validator = SCRIPTS / "sq-data-validator.py"
    if not validator.exists():
        _warn("sq-data-validator.py no encontrado — saltando verificacion")
        return True
    if dry_run:
        print(f"  [DRY-RUN] sq-data-validator.py --activo {activo}")
        return True
    rc = _run([sys.executable, str(validator), "--activo", activo])
    if rc == 1:
        print(f"\n  FAIL — datos insuficientes para {activo}.")
        print("  Completar la descarga en SQ Data Manager antes de continuar.")
        return False
    if rc == 2:
        _warn(f"datos con advertencias para {activo}.")
        resp = input("  ¿Continuar de todas formas? (s/n): ").strip().lower()
        return resp in ("s", "si", "y", "yes")
    _ok(f"datos verificados para {activo}")
    return True


def run_pre_build_checklist(activo: str, spread: float) -> bool:
    _step(1, "Ejecutando pre-build-checklist.py...")
    checklist = SCRIPTS / "pre-build-checklist.py"
    if not checklist.exists():
        _warn("pre-build-checklist.py no encontrado — saltando")
        return True
    rc = _run([sys.executable, str(checklist),
               "--activo", activo, "--spread", str(spread)])
    if rc == 1:
        print("\n  FAIL — pre-build-checklist encontro errores criticos.")
        print("  Corregir antes de continuar.")
        return False
    if rc == 2:
        print("  WARN — hay advertencias. Revisar antes de lanzar.")
    else:
        _ok("pre-build-checklist PASS")
    return True


def show_build_config(activo: str, build_n: int, spread_real: float) -> None:
    _step(2, "Configuracion del build a lanzar")
    spread_sq = spread_real * 2
    print(f"""
    Activo    : {activo}
    Build N   : {build_n}
    TF        : H1
    Spread SQ : {spread_sq:.1f} pips  (= {spread_real:.1f} real x 2)
    Comision  : 7 USD/lote
    Slippage  : 2 pips (XAUUSD) / 0.5 pips (Forex)
    Capital   : 25,000 USD
    Riesgo    : 1% por trade
    Max trades: 2 por dia
    Sesion    : 08:00–20:00 (UTC)
    Modo      : Builder libre — Start again when finished ACTIVADO
    Duracion  : 24–48 horas
    """)


def show_sq_instructions(activo: str, spread_sq: float) -> None:
    _step(3, "Instrucciones para configurar SQ")
    print(f"""
    a) SQ → Data Manager → verificar datos M1 de {activo} disponibles
       Confirmar periodo: IS hasta 2020-12-31, OOS desde 2021-01-01

    b) Verificar que el instrumento FTMO esta asignado a {activo}
       SQ → Symbols → {activo} → verificar broker = FTMO

    c) Verificar spread configurado: debe ser {spread_sq:.1f} pips (2x el real)
       SQ → Symbols → {activo} → Spread = {spread_sq:.1f}

    d) Builder → verificar configuracion segun skill-builder-libre.md
       - Paleta completa activada (TODOS los grupos)
       - Generaciones: 30 por ciclo
       - Poblacion por isla: 100
       - Islas: 4
       - PF minimo Builder: 1.3
       - Trades/mes minimo: 6

    e) Verificar Conditions exit rule max = 2
       Builder → Settings → Max conditions in exit rule = 2

    f) Verificar que Monte Carlo esta DESACTIVADO en Builder
       Builder → Monte Carlo → disabled

    g) Verificar que Comprobaciones cruzadas estan DESACTIVADAS
       Builder → Cross-checks → disabled
    """)


def confirm(dry_run: bool) -> bool:
    if dry_run:
        print("\n  [DRY-RUN] Saltando confirmacion")
        return True
    resp = input("\n¿Todo verificado? Lanzar build ahora (s/n): ").strip().lower()
    return resp in ("s", "si", "y", "yes")


def document_build(build_n: int, activo: str, spread_real: float, dry_run: bool) -> None:
    _step(5, "Documentando configuracion del build...")
    config_script = SCRIPTS / "sqx-build-config.py"
    if not config_script.exists():
        _warn("sqx-build-config.py no encontrado — saltando documentacion")
        return
    cmd = [sys.executable, str(config_script),
           "--build", str(build_n),
           "--activo", activo,
           "--spread", str(spread_real * 2)]
    if dry_run:
        print(f"  [DRY-RUN] {' '.join(cmd)}")
        return
    _run_quiet(cmd)
    _ok(f"Configuracion documentada en results/build-{build_n}-config.md")


def log_to_audit(build_n: int, activo: str, dry_run: bool) -> None:
    _step(7, "Registrando inicio en audit trail...")
    logger = SCRIPTS / "hash-logger.py"
    if not logger.exists():
        _warn("hash-logger.py no encontrado — saltando audit")
        return
    event = f"BUILD_START"
    desc  = f"Build {build_n} iniciado — {activo} H1 — {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    cmd = [sys.executable, str(logger),
           "--event", event, "--description", desc]
    if dry_run:
        print(f"  [DRY-RUN] {' '.join(cmd)}")
        return
    _run_quiet(cmd)
    _ok("Entrada registrada en audit-trail.log")


def run_auto_mode(activo: str, build_n: int, spread_real: float) -> bool:
    """Configurar y arrancar SQ automaticamente via sq-controller."""
    controller = SCRIPTS / "sq-controller.py"
    if not controller.exists():
        print("  ERROR: sq-controller.py no encontrado — modo --auto no disponible")
        return False

    spread_sq = spread_real * 2
    print(f"\n  Modo AUTO activado — configurando SQ via Selenium...")

    rc_cfg = _run([sys.executable, str(controller),
                   "--configure", "--build", str(build_n), "--activo", activo])
    if rc_cfg != 0:
        print("  ERROR: sq-controller --configure fallo")
        return False

    rc_start = _run([sys.executable, str(controller), "--start"])
    if rc_start != 0:
        print("  ERROR: sq-controller --start fallo")
        return False

    print("  Builder iniciado automaticamente")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Launcher — TradingLab")
    parser.add_argument("--build",       type=int,   required=True, help="Numero del build (ej: 11)")
    parser.add_argument("--activo",      required=True,             help="Activo (ej: XAUUSD)")
    parser.add_argument("--spread-real", type=float, required=True, help="Spread real en pips (ej: 30)")
    parser.add_argument("--dry-run",     action="store_true",       help="Simular sin ejecutar nada")
    parser.add_argument("--auto",        action="store_true",       help="Configurar y arrancar SQ automaticamente via Selenium")
    args = parser.parse_args()

    activo     = args.activo.upper()
    spread_sq  = args.spread_real * 2

    _header(f"BUILD LAUNCHER — Build {args.build} | {activo}")
    if args.dry_run:
        print("  [MODO DRY-RUN — sin cambios reales]")

    # Paso 0: verificar datos SQ
    if not run_data_validator(activo, args.dry_run):
        return 1

    # Paso 1: pre-build-checklist
    if not run_pre_build_checklist(activo, spread_sq):
        return 1

    # Paso 2: configuracion del build
    show_build_config(activo, args.build, args.spread_real)

    # Paso 3: instrucciones SQ (solo en modo manual)
    if not args.auto:
        show_sq_instructions(activo, spread_sq)

    # Paso 4: configurar/arrancar SQ o confirmar manualmente
    if args.auto:
        _step(4, "Modo automatico — configurando SQ via sq-controller")
        if not args.dry_run:
            if not run_auto_mode(activo, args.build, args.spread_real):
                return 1
        else:
            print(f"  [DRY-RUN] sq-controller --configure --build {args.build} --activo {activo}")
            print("  [DRY-RUN] sq-controller --start")
    else:
        _step(4, "Confirmacion del usuario")
        if not confirm(args.dry_run):
            print("  Lanzamiento cancelado.")
            return 0

    # Paso 5: documentar configuracion
    document_build(args.build, activo, args.spread_real, args.dry_run)

    # Paso 6: notificacion Telegram
    _step(6, "Enviando notificacion Telegram...")
    msg = f"Build {args.build} iniciado — {activo} H1 — spread {spread_sq:.0f} pips SQ"
    if not args.dry_run:
        _notify("INFO", msg)
        _ok("Telegram notificado")
    else:
        print(f"  [DRY-RUN] Telegram: {msg}")

    # Paso 6b: escribir pipeline.lock
    _step(6, "Actualizando pipeline.lock...")
    lock = {
        "build": args.build,
        "activo": activo,
        "spread_real": args.spread_real,
        "started": datetime.now().isoformat(),
        "status": "running",
    }
    lock_path = RESULTS / "pipeline.lock"
    if not args.dry_run:
        lock_path.write_text(json.dumps(lock, indent=2), encoding="utf-8")
        _ok(f"pipeline.lock actualizado — Build {args.build} {activo}")
    else:
        print(f"  [DRY-RUN] pipeline.lock: {json.dumps(lock)}")

    # Paso 7: audit trail
    log_to_audit(args.build, activo, args.dry_run)

    _header(f"Build {args.build} lanzado correctamente")
    print(f"  Activo   : {activo}")
    print(f"  Spread SQ: {spread_sq:.0f} pips")
    print(f"  Duracion : 24–48 horas")
    print(f"\n  Proxima accion: cuando SQ termine →")
    print(f"  python scripts/build-finisher.py --build {args.build} --activo {activo} --results-folder results/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
