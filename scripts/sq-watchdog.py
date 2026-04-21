"""
sq-watchdog.py
Monitorea que StrategyQuant X no se congele durante builds largos de 24-48h.
Si SQ no genera nuevas estrategias en 30 minutos → matar y reiniciar.
Tambien verifica integridad del Custom Project y hace backup horario.

Compatible con Windows (taskkill + subprocess).

Uso:
    python sq-watchdog.py \
        --sq-log-path "C:/StrategyQuantX/logs/sq.log" \
        --sq-exe-path "C:/StrategyQuantX/StrategyQuantX.exe" \
        --sq-project-path "C:/StrategyQuantX/projects/tradinglab.sqp" \
        --backup-dir backups/sq_configs/ \
        --check-interval 30

Argumentos:
    --sq-log-path      Ruta al archivo de log de SQ (monitoreo de actividad)
    --sq-exe-path      Ruta al ejecutable de SQ (para reinicio)
    --sq-project-path  Ruta al archivo de proyecto SQ (para backup e integridad)
    --backup-dir       Carpeta de backups (default: backups/sq_configs/)
    --check-interval   Minutos entre comprobaciones (default: 30)
    --activity-timeout Minutos sin actividad antes de reiniciar (default: 30)
    --audit-log        Ruta al audit trail (default: results/audit-trail.log)
"""

import argparse
import hashlib
import logging
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Patron en el log de SQ que indica actividad del Builder
ACTIVITY_PATTERNS = [
    "Strategy Generated",
    "strategies",
    "Building strategy",
    "Generation",
    "New best",
    "Evaluating",
]

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
log = logging.getLogger("sq-watchdog")


# ─── Utilidades ───────────────────────────────────────────────────────────────

def get_last_activity_time(sq_log_path: str) -> float | None:
    """
    Lee las ultimas lineas del log de SQ y devuelve el timestamp
    (epoch) de la ultima linea que contiene alguno de los patrones
    de actividad. Devuelve None si no hay actividad.
    """
    if not os.path.exists(sq_log_path):
        log.warning(f"Log de SQ no encontrado: {sq_log_path}")
        return None

    try:
        # Leer las ultimas 500 lineas del log (eficiente para archivos grandes)
        with open(sq_log_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        recent = lines[-500:] if len(lines) > 500 else lines
    except OSError as e:
        log.error(f"No se pudo leer el log de SQ: {e}")
        return None

    # Buscar la ultima linea con patron de actividad
    for line in reversed(recent):
        if any(pat.lower() in line.lower() for pat in ACTIVITY_PATTERNS):
            # Intentar parsear timestamp del comienzo de la linea
            # Formato comun en SQ: "2026-04-21 09:15:33 ..."
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    ts_str = f"{parts[0]} {parts[1]}"
                    dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                    return dt.replace(tzinfo=timezone.utc).timestamp()
                except ValueError:
                    pass
            # Si no se puede parsear el timestamp, usar mtime del archivo
            return os.path.getmtime(sq_log_path)

    return None


def is_sq_running(sq_exe_path: str) -> bool:
    """Verifica si el proceso de SQ esta corriendo en Windows."""
    exe_name = os.path.basename(sq_exe_path)
    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {exe_name}", "/NH"],
            capture_output=True, text=True, timeout=10
        )
        return exe_name.lower() in result.stdout.lower()
    except Exception as e:
        log.error(f"Error verificando proceso SQ: {e}")
        return False


def kill_sq(sq_exe_path: str) -> bool:
    """Mata el proceso de SQ en Windows (taskkill)."""
    exe_name = os.path.basename(sq_exe_path)
    log.warning(f"Matando proceso SQ: {exe_name}")
    try:
        result = subprocess.run(
            ["taskkill", "/F", "/IM", exe_name],
            capture_output=True, text=True, timeout=15
        )
        success = result.returncode == 0
        if success:
            log.info("Proceso SQ terminado correctamente.")
        else:
            log.error(f"Error al terminar SQ: {result.stderr.strip()}")
        return success
    except Exception as e:
        log.error(f"Excepcion al matar SQ: {e}")
        return False


def start_sq(sq_exe_path: str, sq_project_path: str) -> bool:
    """Inicia SQ con el proyecto activo."""
    if not os.path.exists(sq_exe_path):
        log.error(f"Ejecutable SQ no encontrado: {sq_exe_path}")
        return False
    log.info(f"Iniciando SQ: {sq_exe_path}")
    try:
        subprocess.Popen(
            [sq_exe_path, sq_project_path],
            creationflags=subprocess.DETACHED_PROCESS
            if hasattr(subprocess, "DETACHED_PROCESS") else 0,
        )
        time.sleep(15)  # Dar tiempo a SQ para arrancar
        return is_sq_running(sq_exe_path)
    except Exception as e:
        log.error(f"Error iniciando SQ: {e}")
        return False


# ─── Integridad del Custom Project ────────────────────────────────────────────

def compute_file_hash(filepath: str) -> str | None:
    """Calcula SHA-256 de un archivo."""
    if not os.path.exists(filepath):
        return None
    sha = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha.update(chunk)
        return sha.hexdigest()
    except OSError:
        return None


# ─── Backup horario ───────────────────────────────────────────────────────────

def do_backup(sq_project_path: str, backup_dir: str) -> str | None:
    """
    Copia el archivo de proyecto SQ a backups/sq_configs/ con timestamp.
    Devuelve la ruta del backup o None si fallo.
    """
    if not os.path.exists(sq_project_path):
        log.warning(f"Proyecto SQ no encontrado para backup: {sq_project_path}")
        return None

    os.makedirs(backup_dir, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    fname = os.path.basename(sq_project_path)
    name, ext = os.path.splitext(fname)
    dest = os.path.join(backup_dir, f"{name}_{ts}{ext}")

    try:
        shutil.copy2(sq_project_path, dest)
        log.info(f"Backup guardado: {dest}")
        return dest
    except OSError as e:
        log.error(f"Error en backup: {e}")
        return None


def log_alert(audit_log_path: str, message: str) -> None:
    """Escribe una alerta en el archivo de log del watchdog."""
    os.makedirs(os.path.dirname(audit_log_path) or ".", exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(audit_log_path, "a", encoding="utf-8") as f:
        f.write(f"{ts} [WATCHDOG] {message}\n")


# ─── Loop principal ───────────────────────────────────────────────────────────

def run_watchdog(
    sq_log_path: str,
    sq_exe_path: str,
    sq_project_path: str,
    backup_dir: str,
    check_interval_min: int,
    activity_timeout_min: int,
    audit_log_path: str,
) -> None:

    log.info("sq-watchdog iniciado.")
    log.info(f"  Log SQ:            {sq_log_path}")
    log.info(f"  Exe SQ:            {sq_exe_path}")
    log.info(f"  Proyecto SQ:       {sq_project_path}")
    log.info(f"  Backup dir:        {backup_dir}")
    log.info(f"  Check interval:    {check_interval_min} min")
    log.info(f"  Activity timeout:  {activity_timeout_min} min")

    known_project_hash = compute_file_hash(sq_project_path)
    log.info(f"  Hash proyecto SQ:  {known_project_hash[:16] if known_project_hash else 'N/A'}...")

    last_backup_hour = -1
    restart_count = 0
    MAX_RESTARTS = 3  # Maximo de reinicios automaticos antes de alerta critica

    while True:
        now = time.time()
        now_dt = datetime.now(timezone.utc)

        # ── 1. Backup horario ──────────────────────────────────────────────────
        current_hour = now_dt.hour
        if current_hour != last_backup_hour:
            do_backup(sq_project_path, backup_dir)
            last_backup_hour = current_hour

        # ── 2. Verificar integridad del Custom Project ─────────────────────────
        current_hash = compute_file_hash(sq_project_path)
        if known_project_hash and current_hash and current_hash != known_project_hash:
            msg = (
                f"ALERTA: hash del proyecto SQ cambio sin autorizacion. "
                f"Antes: {known_project_hash[:16]} Ahora: {current_hash[:16]}"
            )
            log.error(msg)
            log_alert(audit_log_path, msg)
            log.error("Deteniendo build — posible modificacion no autorizada.")
            # No reiniciar automaticamente — alerta critica
            break
        elif current_hash:
            known_project_hash = current_hash  # actualizar si cambio autorizado (no esperado)

        # ── 3. Verificar actividad de SQ ───────────────────────────────────────
        last_activity = get_last_activity_time(sq_log_path)
        if last_activity is None:
            log.warning("No se pudo determinar ultima actividad de SQ.")
        else:
            minutes_inactive = (now - last_activity) / 60
            log.info(f"Ultima actividad SQ hace {minutes_inactive:.1f} min.")

            if minutes_inactive >= activity_timeout_min:
                if restart_count >= MAX_RESTARTS:
                    msg = (
                        f"ALERTA CRITICA: SQ congelado {restart_count} veces. "
                        f"Intervencion humana requerida."
                    )
                    log.error(msg)
                    log_alert(audit_log_path, msg)
                    break  # No seguir reiniciando

                msg = (
                    f"SQ inactivo {minutes_inactive:.1f} min (umbral: {activity_timeout_min} min). "
                    f"Reiniciando... (intento {restart_count + 1}/{MAX_RESTARTS})"
                )
                log.warning(msg)
                log_alert(audit_log_path, msg)

                # Backup antes de matar
                do_backup(sq_project_path, backup_dir)

                if kill_sq(sq_exe_path):
                    time.sleep(5)
                    if start_sq(sq_exe_path, sq_project_path):
                        restart_count += 1
                        log.info("SQ reiniciado correctamente.")
                        log_alert(audit_log_path, f"SQ reiniciado (intento {restart_count}).")
                    else:
                        msg = "ALERTA CRITICA: No se pudo reiniciar SQ."
                        log.error(msg)
                        log_alert(audit_log_path, msg)
                        break
                else:
                    msg = "ALERTA CRITICA: No se pudo matar el proceso SQ."
                    log.error(msg)
                    log_alert(audit_log_path, msg)
                    break

        # ── 4. Verificar que SQ esta corriendo ─────────────────────────────────
        if not is_sq_running(sq_exe_path):
            log.warning("SQ no esta corriendo. Intentando iniciar...")
            if not start_sq(sq_exe_path, sq_project_path):
                msg = "ALERTA CRITICA: SQ no esta corriendo y no se pudo iniciar."
                log.error(msg)
                log_alert(audit_log_path, msg)
                break

        # Esperar hasta la proxima comprobacion
        log.info(f"Proxima comprobacion en {check_interval_min} min.")
        time.sleep(check_interval_min * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Watchdog para StrategyQuant X durante builds largos."
    )
    parser.add_argument("--sq-log-path", required=True,
                        help="Ruta al log de actividad de SQ")
    parser.add_argument("--sq-exe-path", required=True,
                        help="Ruta al ejecutable de SQ")
    parser.add_argument("--sq-project-path", required=True,
                        help="Ruta al archivo de proyecto SQ (.sqp)")
    parser.add_argument("--backup-dir", default="backups/sq_configs/",
                        help="Carpeta de backups horarios (default: backups/sq_configs/)")
    parser.add_argument("--check-interval", type=int, default=30,
                        help="Minutos entre comprobaciones (default: 30)")
    parser.add_argument("--activity-timeout", type=int, default=30,
                        help="Minutos sin actividad antes de reiniciar (default: 30)")
    parser.add_argument("--audit-log", default="results/watchdog.log",
                        help="Ruta al log del watchdog (default: results/watchdog.log)")
    args = parser.parse_args()

    run_watchdog(
        sq_log_path=args.sq_log_path,
        sq_exe_path=args.sq_exe_path,
        sq_project_path=args.sq_project_path,
        backup_dir=args.backup_dir,
        check_interval_min=args.check_interval,
        activity_timeout_min=args.activity_timeout,
        audit_log_path=args.audit_log,
    )


if __name__ == "__main__":
    main()
