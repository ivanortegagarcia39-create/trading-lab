#!/usr/bin/env python3
"""
news-filter-checker.py — Verifica si hay noticias de alto impacto proximas.

Uso:
    python scripts/news-filter-checker.py --check-now
    python scripts/news-filter-checker.py --check-now --activo XAUUSD
"""

import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import urllib.request
    import ssl
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False

# Noticias HIGH impact que afectan a XAUUSD (USD + global)
# Formato: (dia_semana, hora_utc, nombre, tipo)
# dia_semana: 0=Lunes, 1=Martes, 2=Miercoles, 3=Jueves, 4=Viernes
HARDCODED_EVENTS = [
    # Martes
    (1, "09:00", "Datos empleo europeos (ZEW/employment)", "MEDIUM"),
    (1, "13:30", "Datos EEUU (Retail Sales / PPI / CPI martes)", "HIGH"),
    # Miercoles
    (2, "13:30", "Datos EEUU (CPI / ADP Employment)", "HIGH"),
    (2, "18:00", "FOMC Statement / Minutes (si aplica)", "FOMC"),
    (2, "18:30", "Conferencia FOMC (si aplica)", "FOMC"),
    # Jueves
    (3, "07:45", "BCE Decision de tipos (si aplica)", "HIGH"),
    (3, "08:30", "Conferencia BCE (si aplica)", "HIGH"),
    (3, "13:30", "Jobless Claims / Philly Fed", "MEDIUM"),
    # Viernes
    (4, "13:30", "NFP — Nominas no agricolas (primer viernes del mes)", "NFP"),
    (4, "13:30", "Datos EEUU (PPI / Retail Sales viernes)", "HIGH"),
]

# Activos afectados por tipo de evento
ACTIVOS_AFECTADOS = {
    "HIGH":   ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "NZDUSD", "USDCAD"],
    "MEDIUM": ["EURUSD", "GBPUSD", "USDJPY"],
    "FOMC":   ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "NZDUSD", "USDCAD"],
    "NFP":    ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "NZDUSD", "USDCAD"],
}

# Ventana de proteccion por tipo (minutos antes y despues)
VENTANAS = {
    "NFP":    60,
    "FOMC":   60,
    "HIGH":   30,
    "MEDIUM": 15,
}


def _fetch_forexfactory(fecha: str) -> list | None:
    """Intenta obtener calendario de ForexFactory. Devuelve None si falla."""
    if not HAS_URLLIB:
        return None
    try:
        url = f"https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data if isinstance(data, list) else None
    except Exception:
        return None


def _parse_ff_event(event: dict) -> dict | None:
    """Parsea un evento de ForexFactory al formato interno."""
    try:
        impact = event.get("impact", "").lower()
        if impact not in ("high", "medium"):
            return None
        date_str = event.get("date", "")
        if not date_str:
            return None
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        tipo = "HIGH" if impact == "high" else "MEDIUM"
        title = event.get("title", "")
        currency = event.get("country", "")
        if any(k in title.upper() for k in ("NFP", "NONFARM", "NON-FARM")):
            tipo = "NFP"
        if any(k in title.upper() for k in ("FOMC", "FED RATE", "FEDERAL FUNDS")):
            tipo = "FOMC"
        return {
            "dt_utc": dt,
            "nombre": f"{currency} {title}",
            "tipo":   tipo,
        }
    except Exception:
        return None


def _build_events_today_hardcoded(now_utc: datetime, activo: str | None) -> list:
    """Construye lista de eventos del dia de hoy desde horarios hardcodeados."""
    dow = now_utc.weekday()
    events = []
    for (wd, hora_str, nombre, tipo) in HARDCODED_EVENTS:
        if wd != dow:
            continue
        if activo and activo.upper() not in ACTIVOS_AFECTADOS.get(tipo, []):
            continue
        h, m = hora_str.split(":")
        dt = now_utc.replace(hour=int(h), minute=int(m), second=0, microsecond=0)
        events.append({"dt_utc": dt, "nombre": nombre, "tipo": tipo})
    return events


def _evaluate_events(events: list, now_utc: datetime) -> tuple[str, list]:
    """Evalua eventos y devuelve (estado, lista_alertas)."""
    alertas = []
    estado = "SAFE"

    for ev in events:
        dt    = ev["dt_utc"]
        tipo  = ev["tipo"]
        nombre = ev["nombre"]
        ventana = VENTANAS.get(tipo, 30)

        delta_min = (dt - now_utc).total_seconds() / 60

        # Dentro de la ventana (antes o despues)
        if -ventana <= delta_min <= ventana:
            if tipo in ("NFP", "FOMC"):
                estado = "DANGER"
                alertas.append(f"DANGER — {tipo}: {nombre} en {delta_min:.0f} min (ventana {ventana}m)")
            elif tipo == "HIGH":
                if estado != "DANGER":
                    estado = "DANGER"
                alertas.append(f"DANGER — {tipo}: {nombre} en {delta_min:.0f} min")
            elif tipo == "MEDIUM":
                if estado == "SAFE":
                    estado = "WARNING"
                alertas.append(f"WARNING — {tipo}: {nombre} en {delta_min:.0f} min")

    return estado, alertas


def cmd_check_now(activo: str | None) -> None:
    now_utc = datetime.now(timezone.utc)
    print(f"\n  News Filter Checker — {now_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"  {'─'*50}")

    # Intentar ForexFactory primero
    ff_data = _fetch_forexfactory(now_utc.strftime("%Y-%m-%d"))
    source = "ForexFactory API"
    events = []

    if ff_data:
        for raw in ff_data:
            parsed = _parse_ff_event(raw)
            if parsed is None:
                continue
            if activo and activo.upper() not in ACTIVOS_AFECTADOS.get(parsed["tipo"], []):
                continue
            delta_min = (parsed["dt_utc"] - now_utc).total_seconds() / 60
            if -60 <= delta_min <= 60:
                events.append(parsed)
    else:
        source = "Horarios hardcodeados (FF no disponible)"
        events = _build_events_today_hardcoded(now_utc, activo)

    print(f"  Fuente   : {source}")
    if activo:
        print(f"  Activo   : {activo.upper()}")

    estado, alertas = _evaluate_events(events, now_utc)

    estado_icons = {"SAFE": "[SAFE   ]", "WARNING": "[WARNING]", "DANGER": "[DANGER ]"}
    print(f"  Estado   : {estado_icons.get(estado, estado)}  {estado}")
    print()

    if alertas:
        print(f"  Alertas ({len(alertas)}):")
        for a in alertas:
            print(f"  -> {a}")
    else:
        print(f"  Sin noticias de impacto en los proximos 30 minutos.")

    # Proximos eventos del dia (informativo)
    proximos = []
    for ev in _build_events_today_hardcoded(now_utc, activo):
        delta_min = (ev["dt_utc"] - now_utc).total_seconds() / 60
        if 0 < delta_min <= 480:  # proximas 8 horas
            proximos.append((delta_min, ev))

    if proximos and not ff_data:
        proximos.sort(key=lambda x: x[0])
        print(f"\n  Proximos eventos del dia (hardcoded, proximas 8h):")
        for delta_min, ev in proximos[:5]:
            h = int(delta_min // 60)
            m = int(delta_min % 60)
            print(f"  {ev['dt_utc'].strftime('%H:%M')} UTC  [{ev['tipo']:6}]  {ev['nombre']}  "
                  f"(en {h}h {m:02d}m)")

    print()

    # Exit code segun estado
    if estado == "DANGER":
        sys.exit(2)
    elif estado == "WARNING":
        sys.exit(1)
    sys.exit(0)


def main() -> int:
    parser = argparse.ArgumentParser(description="News Filter Checker — TradingLab")
    parser.add_argument("--check-now", action="store_true", help="Verificar estado actual")
    parser.add_argument("--activo",    default=None,        help="Filtrar por activo (ej: XAUUSD)")
    args = parser.parse_args()

    if args.check_now:
        cmd_check_now(args.activo)
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    main()
