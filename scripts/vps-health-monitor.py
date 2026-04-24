"""
vps-health-monitor.py
Monitorea la salud del VPS en produccion.

Verificaciones:
  1. Latencia al servidor del broker (ping)
  2. Conexion a Internet (ping a 1.1.1.1)
  3. Ghost Freeze detector (timestamp del EA)
  4. Sincronizacion NTP
  5. Conexion MT5 al broker

Alertas via Telegram en tres niveles: INFO / WARNING / CRITICAL.

Uso:
    python vps-health-monitor.py --broker-server eightcap-server.com
    python vps-health-monitor.py --broker-server 1.2.3.4 \\
        --telegram-token TOKEN --telegram-chat-id CHAT_ID \\
        --heartbeat-file C:\\trading-lab\\heartbeat.txt

Argumento --check-interval controla los segundos entre verificaciones
(default 300 = 5 minutos).

Compatible con Windows y Linux — detecta el OS automaticamente.
"""

import argparse
import json
import os
import platform
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path


# ─── Configuracion ────────────────────────────────────────────────────────────

LATENCY_WARNING_MS      = 10     # ms — umbral de warning
LATENCY_CRITICAL_MS     = 50     # ms — umbral critico
PACKET_LOSS_THRESHOLD   = 50     # % — perdida de paquetes maxima
PACKET_LOSS_WINDOW_SEC  = 120    # segundos — ventana de observacion
HEARTBEAT_TIMEOUT_SEC   = 180    # 3 minutos sin heartbeat → MT5 congelado
NTP_DRIFT_MAX_SEC       = 10     # segundos — desfase NTP maximo
MT5_DISCONNECT_TIMEOUT  = 300    # 5 minutos desconectado → alerta
PING_COUNT              = 4      # paquetes por ping

IS_WINDOWS = platform.system() == "Windows"


# ─── Utilidades de sistema ────────────────────────────────────────────────────

def ping(host: str, count: int = PING_COUNT) -> tuple[float, float]:
    """
    Realiza ping al host y devuelve (latencia_ms, perdida_pct).
    Compatible con Windows y Linux.
    """
    if IS_WINDOWS:
        cmd = ["ping", "-n", str(count), host]
    else:
        cmd = ["ping", "-c", str(count), "-W", "2", host]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout + result.stderr

        # Extraer latencia promedio
        latency_ms = 0.0
        if IS_WINDOWS:
            for line in output.splitlines():
                if "Average" in line or "Media" in line:
                    parts = line.split("=")
                    if parts:
                        val = parts[-1].strip().replace("ms", "").strip()
                        try:
                            latency_ms = float(val)
                        except ValueError:
                            pass
                        break
        else:
            for line in output.splitlines():
                if "avg" in line or "rtt" in line:
                    # Formato: rtt min/avg/max/mdev = 1.2/3.4/5.6/0.8 ms
                    parts = line.split("=")
                    if len(parts) > 1:
                        values = parts[1].strip().split("/")
                        if len(values) >= 2:
                            try:
                                latency_ms = float(values[1])
                            except ValueError:
                                pass
                    break

        # Extraer perdida de paquetes
        loss_pct = 0.0
        for line in output.splitlines():
            if "%" in line and ("loss" in line.lower() or "perdid" in line.lower()):
                for token in line.split():
                    if "%" in token:
                        try:
                            loss_pct = float(token.replace("%", "").replace(",", "."))
                        except ValueError:
                            pass
                        break
                break

        return latency_ms, loss_pct

    except subprocess.TimeoutExpired:
        return 9999.0, 100.0
    except Exception:
        return 9999.0, 100.0


def get_ntp_offset_seconds(ntp_server: str = "pool.ntp.org") -> float:
    """
    Calcula el desfase entre la hora del sistema y el servidor NTP.
    Devuelve el offset en segundos (absoluto).
    Usa socket UDP simple sin dependencias externas.
    """
    import socket
    import struct

    NTP_PORT = 123
    NTP_PACKET_FORMAT = "!12I"
    NTP_DELTA = 2208988800  # segundos entre 1900 y 1970

    try:
        packet = b"\x1b" + 47 * b"\0"
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(5)
            sock.sendto(packet, (ntp_server, NTP_PORT))
            data, _ = sock.recvfrom(1024)

        if data:
            unpacked = struct.unpack(NTP_PACKET_FORMAT, data[:48])
            ntp_time = unpacked[10] + float(unpacked[11]) / 2**32 - NTP_DELTA
            local_time = time.time()
            return abs(ntp_time - local_time)

    except Exception:
        return -1.0  # -1 indica que no se pudo verificar

    return -1.0


def check_heartbeat(heartbeat_file: Path, timeout_sec: int = HEARTBEAT_TIMEOUT_SEC) -> tuple[bool, int]:
    """
    Verifica si el EA esta vivo leyendo su archivo de heartbeat.
    Devuelve (esta_vivo, segundos_desde_ultimo_heartbeat).
    Si el archivo no existe: devuelve (None, -1) — no monitoreable.
    """
    if not heartbeat_file or not heartbeat_file.exists():
        return None, -1

    try:
        content = heartbeat_file.read_text(encoding="utf-8").strip()
        # El EA escribe un timestamp ISO-8601 o Unix timestamp
        try:
            ts = float(content)
        except ValueError:
            # Intentar parsear ISO-8601
            try:
                dt = datetime.fromisoformat(content)
                ts = dt.timestamp()
            except ValueError:
                return False, -1

        elapsed = int(time.time() - ts)
        return elapsed < timeout_sec, elapsed

    except Exception:
        return False, -1


def force_restart_mt5() -> bool:
    """
    Intenta forzar el reinicio de MT5 en Windows.
    Solo funciona en Windows — en Linux devuelve False.
    """
    if not IS_WINDOWS:
        return False

    try:
        # Cerrar MT5
        subprocess.run(["taskkill", "/F", "/IM", "terminal64.exe"], capture_output=True)
        time.sleep(5)

        # Buscar terminal64.exe en rutas comunes
        mt5_paths = [
            Path("C:/Program Files/MetaTrader 5/terminal64.exe"),
            Path("C:/Program Files (x86)/MetaTrader 5/terminal64.exe"),
        ]
        for path in mt5_paths:
            if path.exists():
                subprocess.Popen([str(path)])
                return True

        return False
    except Exception:
        return False


# ─── Telegram ─────────────────────────────────────────────────────────────────

def send_telegram(
    message: str,
    level: str,
    token: str,
    chat_id: str,
) -> bool:
    """
    Envia alerta via Telegram.
    Formato: "[VPS] [NIVEL] Descripcion - Timestamp"
    """
    if not token or not chat_id:
        return False

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text = f"[VPS] [{level}] {message} - {timestamp}"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False


# ─── Verificaciones individuales ──────────────────────────────────────────────

def check_broker_latency(broker_server: str, token: str, chat_id: str) -> str:
    """Verifica latencia al servidor del broker."""
    latency_ms, loss_pct = ping(broker_server)

    if latency_ms >= LATENCY_CRITICAL_MS:
        msg = f"Latencia critica al broker {broker_server}: {latency_ms:.1f}ms (limite: {LATENCY_CRITICAL_MS}ms)"
        send_telegram(msg, "CRITICAL", token, chat_id)
        return f"CRITICAL: {msg}"
    elif latency_ms >= LATENCY_WARNING_MS:
        msg = f"Latencia alta al broker {broker_server}: {latency_ms:.1f}ms (limite: {LATENCY_WARNING_MS}ms)"
        send_telegram(msg, "WARNING", token, chat_id)
        return f"WARNING: {msg}"
    else:
        return f"OK: Latencia broker {broker_server}: {latency_ms:.1f}ms, perdida: {loss_pct:.0f}%"


def check_internet(token: str, chat_id: str) -> str:
    """Verifica conectividad a Internet via Cloudflare DNS."""
    latency_ms, loss_pct = ping("1.1.1.1")

    if loss_pct >= PACKET_LOSS_THRESHOLD:
        msg = f"Perdida de paquetes Internet: {loss_pct:.0f}% (limite: {PACKET_LOSS_THRESHOLD}%)"
        send_telegram(msg, "CRITICAL", token, chat_id)
        return f"CRITICAL: {msg}"
    elif latency_ms >= LATENCY_CRITICAL_MS:
        msg = f"Conexion Internet lenta: {latency_ms:.1f}ms"
        send_telegram(msg, "WARNING", token, chat_id)
        return f"WARNING: {msg}"
    else:
        return f"OK: Internet {latency_ms:.1f}ms, perdida: {loss_pct:.0f}%"


def check_heartbeat_status(
    heartbeat_file: Path,
    token: str,
    chat_id: str,
    auto_restart: bool = False,
) -> str:
    """Verifica el Ghost Freeze del EA via archivo de heartbeat."""
    alive, elapsed = check_heartbeat(heartbeat_file)

    if alive is None:
        return f"SKIP: Heartbeat no configurado o archivo no encontrado: {heartbeat_file}"

    if not alive:
        msg = (
            f"Ghost Freeze detectado en MT5. "
            f"Ultimo heartbeat hace {elapsed}s (limite: {HEARTBEAT_TIMEOUT_SEC}s)."
        )
        if auto_restart:
            msg += " Intentando reinicio automatico de MT5..."
            restarted = force_restart_mt5()
            msg += " Reinicio OK." if restarted else " Reinicio fallido — accion manual requerida."

        send_telegram(msg, "CRITICAL", token, chat_id)
        return f"CRITICAL: {msg}"
    else:
        return f"OK: EA activo. Ultimo heartbeat hace {elapsed}s"


def check_ntp(token: str, chat_id: str) -> str:
    """Verifica sincronizacion NTP del sistema."""
    offset = get_ntp_offset_seconds()

    if offset < 0:
        return "SKIP: No se pudo verificar NTP (timeout o red)"

    if offset > NTP_DRIFT_MAX_SEC:
        msg = (
            f"Desfase NTP critico: {offset:.1f}s (limite: {NTP_DRIFT_MAX_SEC}s). "
            f"Forzar sincronizacion: w32tm /resync (Windows) o ntpdate pool.ntp.org (Linux)"
        )
        send_telegram(msg, "CRITICAL", token, chat_id)
        return f"CRITICAL: {msg}"
    else:
        return f"OK: Desfase NTP: {offset:.2f}s"


def check_mt5_connection(token: str, chat_id: str) -> str:
    """
    Verifica si MT5 esta corriendo (solo Windows).
    En Linux o si MT5 no es detectable: devuelve SKIP.
    """
    if not IS_WINDOWS:
        return "SKIP: Verificacion de proceso MT5 solo disponible en Windows"

    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq terminal64.exe", "/NH"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if "terminal64.exe" in result.stdout:
            return "OK: MT5 (terminal64.exe) esta corriendo"
        else:
            msg = "MT5 (terminal64.exe) no detectado en procesos activos"
            send_telegram(msg, "WARNING", token, chat_id)
            return f"WARNING: {msg}"
    except Exception as e:
        return f"SKIP: No se pudo verificar proceso MT5: {e}"


# ─── Loop principal ───────────────────────────────────────────────────────────

def run_checks(args: argparse.Namespace) -> None:
    """Ejecuta todas las verificaciones y reporta resultados."""
    timestamp = datetime.now(tz=timezone.utc).isoformat(timespec="seconds")
    print(f"\n{'='*60}")
    print(f"VPS Health Monitor — {timestamp}")
    print(f"{'='*60}")

    results = []

    # 1. Latencia al broker
    r = check_broker_latency(args.broker_server, args.telegram_token, args.telegram_chat_id)
    results.append(r)
    print(f"  [Broker latency]  {r}")

    # 2. Conexion a Internet
    r = check_internet(args.telegram_token, args.telegram_chat_id)
    results.append(r)
    print(f"  [Internet]        {r}")

    # 3. Ghost Freeze detector
    hb_file = Path(args.heartbeat_file) if args.heartbeat_file else None
    r = check_heartbeat_status(hb_file, args.telegram_token, args.telegram_chat_id)
    results.append(r)
    print(f"  [Heartbeat]       {r}")

    # 4. NTP sync
    r = check_ntp(args.telegram_token, args.telegram_chat_id)
    results.append(r)
    print(f"  [NTP]             {r}")

    # 5. MT5 proceso
    r = check_mt5_connection(args.telegram_token, args.telegram_chat_id)
    results.append(r)
    print(f"  [MT5 process]     {r}")

    # Resumen
    criticals = [r for r in results if r.startswith("CRITICAL")]
    warnings  = [r for r in results if r.startswith("WARNING")]
    print(f"\nResumen: {len(criticals)} criticos, {len(warnings)} warnings")

    if not criticals and not warnings:
        print("  Estado general: TODO OK")


def main() -> int:
    parser = argparse.ArgumentParser(description="VPS Health Monitor — TradingLab")
    parser.add_argument(
        "--broker-server",
        required=True,
        help="IP o hostname del servidor del broker (ej: eightcap-server.com)",
    )
    parser.add_argument(
        "--telegram-token",
        default="",
        help="Token del bot de Telegram (opcional)",
    )
    parser.add_argument(
        "--telegram-chat-id",
        default="",
        help="Chat ID de Telegram (opcional)",
    )
    parser.add_argument(
        "--heartbeat-file",
        default="",
        help="Ruta al archivo de heartbeat escrito por el EA (opcional)",
    )
    parser.add_argument(
        "--check-interval",
        type=int,
        default=300,
        help="Segundos entre verificaciones (default: 300 = 5 min)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Ejecutar una sola vez y salir (sin loop continuo)",
    )
    args = parser.parse_args()

    print(f"VPS Health Monitor iniciado")
    print(f"Broker: {args.broker_server}")
    print(f"Intervalo: {args.check_interval}s")
    print(f"Telegram: {'configurado' if args.telegram_token else 'no configurado'}")
    print(f"Heartbeat: {args.heartbeat_file or 'no configurado'}")

    if args.once:
        run_checks(args)
        return 0

    # Loop continuo
    while True:
        try:
            run_checks(args)
        except KeyboardInterrupt:
            print("\nMonitor detenido por el usuario.")
            return 0
        except Exception as e:
            print(f"[ERROR] en verificacion: {e}")

        time.sleep(args.check_interval)

    return 0


if __name__ == "__main__":
    sys.exit(main())
