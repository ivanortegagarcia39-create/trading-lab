#!/usr/bin/env python3
"""
portfolio-monitor-dashboard.py — Dashboard ASCII del estado del portfolio.
Muestra estrategias activas, DD combinado, alertas y estado del pipeline.

Uso:
    python scripts/portfolio-monitor-dashboard.py
    python scripts/portfolio-monitor-dashboard.py --watch
    python scripts/portfolio-monitor-dashboard.py --watch --interval 30
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import pytz
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False

ROOT    = Path(__file__).parent.parent
RESULTS = ROOT / "results"

DD_WARNING   = 3.0
DD_CRITICAL  = 4.5
DD_COMBINED  = 12.0
CORR_WARNING = 0.5


def _load_json(path: Path):
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _time_to_prague_midnight() -> str:
    if not HAS_PYTZ:
        return "pytz no instalado"
    try:
        prague = pytz.timezone("Europe/Prague")
        now_prague = datetime.now(prague)
        midnight = now_prague.replace(hour=0, minute=0, second=0, microsecond=0)
        from datetime import timedelta
        next_midnight = midnight + timedelta(days=1)
        delta = next_midnight - now_prague
        h = delta.seconds // 3600
        m = (delta.seconds % 3600) // 60
        return f"{h}h {m:02d}m"
    except Exception:
        return "—"


def _semaforo(dd_pct: float) -> str:
    if dd_pct >= DD_CRITICAL:
        return "ROJO"
    if dd_pct >= DD_WARNING:
        return "AMARILLO"
    return "VERDE"


def _semaforo_icon(estado: str) -> str:
    return {"VERDE": "[OK  ]", "AMARILLO": "[WARN]", "ROJO": "[CRIT]"}.get(estado, "[----]")


def _line(char: str = "─", width: int = 62) -> str:
    return char * width


def draw_header(now_str: str) -> None:
    print(_line("═"))
    print(f"  TRADINGLAB — Portfolio Monitor — {now_str}")
    print(_line("═"))


def draw_portfolio_section(registry: dict, portfolio: dict) -> list:
    strategies = []
    if isinstance(portfolio, dict):
        for s in portfolio.get("portfolio", []):
            strategies.append(s)

    if not strategies:
        return []

    alerts = []
    print(f"\n  PORTFOLIO — {len(strategies)} estrategia(s) activa(s)")
    print(_line())
    print(f"  {'Estrategia':<28} {'Activo':<8} {'PF':>5} {'DD%':>6}  Estado")
    print(_line())

    dd_values = []
    corr_values = []

    for s in strategies:
        name   = s.get("id", s.get("file", "?"))[:27]
        activo = s.get("symbol", s.get("activo", "?"))[:7]
        pf     = s.get("pf_actual", s.get("pf_is", 0))
        dd     = s.get("dd_actual", s.get("dd", 0))
        dd_values.append(float(dd) if dd else 0)
        estado = _semaforo(float(dd) if dd else 0)
        icon   = _semaforo_icon(estado)
        print(f"  {name:<28} {activo:<8} {pf:>5.2f} {dd:>5.1f}%  {icon} {estado}")
        if estado != "VERDE":
            alerts.append(f"{name}: DD {dd:.1f}% — {estado}")

    print(_line())

    dd_combined = sum(dd_values) / len(dd_values) if dd_values else 0
    dd_icon = "[WARN]" if dd_combined > DD_COMBINED * 0.7 else "[OK  ]"
    print(f"  DD combinado  : {dd_combined:.1f}%   (límite: {DD_COMBINED}%)  {dd_icon}")

    corr = portfolio.get("metricas_portfolio", {}).get("correlacion_media", None)
    if corr is not None:
        corr_icon = "[WARN]" if float(corr) > CORR_WARNING else "[OK  ]"
        print(f"  Corr. media   : {float(corr):.2f}    (límite: {CORR_WARNING})     {corr_icon}")

    return alerts


def draw_no_portfolio_section() -> None:
    lock = RESULTS / "pipeline.lock"
    build_activo = lock.read_text(encoding="utf-8").strip() if lock.exists() else "ninguno"

    queue_file = RESULTS / "build-queue.json"
    queue = _load_json(queue_file)
    next_build = next(
        (q for q in (queue if isinstance(queue, list) else [])
         if q.get("estado") in ("PENDIENTE", "EN_CURSO")),
        None
    )

    health = _load_json(RESULTS / "system-health.json")
    s = health.get("summary", {}) if health else {}
    ts = health.get("timestamp", "")[:19] if health else ""

    print(f"\n  MODO: SIN ESTRATEGIAS ACTIVAS (Capa 0)")
    print(_line())
    print(f"  Build activo  : {build_activo}")

    if next_build:
        score = next_build.get("score") or "TBD"
        print(f"  Próximo build : {next_build.get('activo','?')}  Score:{score}  "
              f"[{next_build.get('estado','?')}]")
        if next_build.get("notas"):
            print(f"  Notas         : {next_build['notas'][:55]}")

    if s:
        ok   = s.get("ok", 0)
        warn = s.get("warn", 0)
        fail = s.get("fail", 0)
        sys_icon = "[OK  ]" if fail == 0 else "[FAIL]"
        print(f"  Sistema       : OK:{ok} WARN:{warn} FAIL:{fail}  {sys_icon}  {ts}")


def draw_alerts(alerts: list) -> None:
    if not alerts:
        return
    print(f"\n  ALERTAS ({len(alerts)} activa(s))")
    print(_line())
    for a in alerts:
        print(f"  [!] {a}")


def draw_footer() -> None:
    reset_str = _time_to_prague_midnight()
    print(_line())
    print(f"  FTMO reset en : {reset_str}  (00:00 hora Prague)")
    print(_line("═"))


def render(once: bool = False) -> None:
    if not once:
        os.system("cls" if os.name == "nt" else "clear")

    now_str  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    registry = _load_json(RESULTS / "strategies-registry.json")
    portfolio = _load_json(RESULTS / "portfolio-selected.json")

    draw_header(now_str)

    alerts = draw_portfolio_section(registry, portfolio)
    if not alerts and not portfolio.get("portfolio"):
        draw_no_portfolio_section()

    draw_alerts(alerts)
    draw_footer()


def main() -> int:
    parser = argparse.ArgumentParser(description="Portfolio Monitor Dashboard — TradingLab")
    parser.add_argument("--watch",    action="store_true", help="Refrescar periodicamente")
    parser.add_argument("--interval", type=int, default=60, help="Intervalo en segundos (default: 60)")
    args = parser.parse_args()

    if args.watch:
        print(f"Modo watch activado — refrescando cada {args.interval}s (Ctrl+C para salir)")
        try:
            while True:
                render()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nMonitoreo detenido.")
    else:
        render(once=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
