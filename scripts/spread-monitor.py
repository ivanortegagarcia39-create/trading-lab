#!/usr/bin/env python3
"""
spread-monitor.py — Monitorea el spread actual de activos para detectar condiciones anomalas.

Uso:
    python scripts/spread-monitor.py --activo XAUUSD
    python scripts/spread-monitor.py --activo XAUUSD --watch
    python scripts/spread-monitor.py --activo XAUUSD --watch --check-interval 30
    python scripts/spread-monitor.py  # todos los activos del config
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT   = Path(__file__).parent.parent
CONFIG = ROOT / "config" / "build-defaults.json"

# Factores de clasificacion
FACTOR_NORMAL   = 1.5
FACTOR_ELEVATED = 3.0

try:
    import MetaTrader5 as mt5
    HAS_MT5 = True
except ImportError:
    HAS_MT5 = False


def _load_reference_spreads() -> dict:
    """Lee spreads de referencia desde config/build-defaults.json."""
    if not CONFIG.exists():
        return {}
    try:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        return {k: v["real"] for k, v in data.get("spreads_ftmo", {}).items()}
    except Exception:
        return {}


def _get_spread_mt5(activo: str) -> float | None:
    """Intenta obtener el spread actual desde MetaTrader5."""
    if not HAS_MT5:
        return None
    try:
        if not mt5.initialize():
            return None
        info = mt5.symbol_info(activo)
        if info is None:
            return None
        # spread en puntos, convertir a pips segun digitos
        spread_pts = info.spread
        digits     = info.digits
        # Para XAUUSD (2 decimales): 1 pip = 0.01 = 1 punto
        # Para EURUSD (5 decimales): 1 pip = 0.0001 = 10 puntos
        if digits == 2:
            return float(spread_pts)
        elif digits == 3:
            return float(spread_pts) / 10
        elif digits == 5:
            return float(spread_pts) / 10
        else:
            return float(spread_pts)
    except Exception:
        return None
    finally:
        try:
            mt5.shutdown()
        except Exception:
            pass


def _classify(factor: float) -> str:
    if factor >= FACTOR_ELEVATED:
        return "EXTREME"
    if factor >= FACTOR_NORMAL:
        return "ELEVATED"
    return "NORMAL"


def _estado_icon(estado: str) -> str:
    return {"NORMAL": "[OK    ]", "ELEVATED": "[WARN  ]", "EXTREME": "[DANGER]"}.get(estado, "[------]")


def _check_activo(activo: str, refs: dict) -> dict:
    activo_up  = activo.upper()
    ref_spread = refs.get(activo_up)

    if ref_spread is None:
        return {"activo": activo_up, "estado": "UNKNOWN", "factor": 0, "spread_actual": None, "spread_ref": None}

    spread_actual = _get_spread_mt5(activo_up)
    source = "MT5"

    if spread_actual is None:
        # Sin MT5: usar spread de referencia directamente (factor = 1.0 siempre)
        spread_actual = ref_spread
        source = "config (MT5 no disponible)"

    factor = round(spread_actual / ref_spread, 2) if ref_spread > 0 else 0
    estado = _classify(factor)

    return {
        "activo":        activo_up,
        "spread_actual": spread_actual,
        "spread_ref":    ref_spread,
        "factor":        factor,
        "estado":        estado,
        "source":        source,
    }


def render(activos: list[str], once: bool = False) -> None:
    if not once:
        os.system("cls" if os.name == "nt" else "clear")

    refs      = _load_reference_spreads()
    now_str   = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    print("═" * 62)
    print(f"  TRADINGLAB — Spread Monitor — {now_str} UTC")
    print("═" * 62)

    if not HAS_MT5:
        print(f"  [INFO] MetaTrader5 no instalado — usando spreads de referencia")

    print(f"\n  {'Activo':<10} {'Spread ref':>11} {'Spread actual':>14} {'Factor':>7}  Estado")
    print("  " + "─" * 58)

    worst = "NORMAL"
    for activo in activos:
        r = _check_activo(activo, refs)
        if r["estado"] == "UNKNOWN":
            print(f"  {r['activo']:<10} {'—':>11} {'—':>14} {'—':>7}  [UNKNOWN] sin datos")
            continue

        icon = _estado_icon(r["estado"])
        print(f"  {r['activo']:<10} {r['spread_ref']:>10.1f}p "
              f"{r['spread_actual']:>13.1f}p "
              f"{r['factor']:>6.2f}x  {icon} {r['estado']}")

        if r["estado"] == "EXTREME":
            worst = "EXTREME"
        elif r["estado"] == "ELEVATED" and worst != "EXTREME":
            worst = "ELEVATED"

    print("  " + "─" * 58)
    print(f"\n  Leyenda:")
    print(f"  NORMAL   factor < {FACTOR_NORMAL}x   — operar normalmente")
    print(f"  ELEVATED factor {FACTOR_NORMAL}x-{FACTOR_ELEVATED}x — operar con precaucion")
    print(f"  EXTREME  factor > {FACTOR_ELEVATED}x   — NO operar (DSP activado)")
    print(f"\n  Estado global: {_estado_icon(worst)} {worst}")
    print("═" * 62)


def main() -> int:
    parser = argparse.ArgumentParser(description="Spread Monitor — TradingLab")
    parser.add_argument("--activo",         default=None,    help="Activo especifico (ej: XAUUSD). Sin valor = todos.")
    parser.add_argument("--watch",          action="store_true", help="Refrescar periodicamente")
    parser.add_argument("--check-interval", type=int, default=60, help="Intervalo en segundos (default: 60)")
    args = parser.parse_args()

    refs = _load_reference_spreads()

    if args.activo:
        activos = [args.activo.upper()]
    else:
        activos = list(refs.keys()) if refs else ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]

    if args.watch:
        print(f"Modo watch — refrescando cada {args.check_interval}s (Ctrl+C para salir)")
        try:
            while True:
                render(activos)
                time.sleep(args.check_interval)
        except KeyboardInterrupt:
            print("\nMonitoreo detenido.")
    else:
        render(activos, once=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
