#!/usr/bin/env python3
"""
risk-calculator.py — Calcula el tamaño de posicion correcto para cada trade

Uso:
    python scripts/risk-calculator.py --balance 25000 --sl-pips 150 --activo XAUUSD
    python scripts/risk-calculator.py --balance 25000 --sl-pips 50 --activo EURUSD \\
        --dd-actual 3.5 --num-estrategias 3
"""

import argparse
import json
import sys
from pathlib import Path

ROOT   = Path(__file__).parent.parent
CONFIG = ROOT / "config" / "pipeline-config.json"
BUILD_DEFAULTS = ROOT / "config" / "build-defaults.json"

# Valor pip por activo en USD para 1 lote estandar (100k unidades)
# Para XAUUSD: 1 pip = 1 USD/lote (precio en USD, pip = 0.01)
# Para Forex majors: 1 pip = 10 USD/lote
PIP_VALUE_USD = {
    "XAUUSD":  1.0,    # 0.01 x 100 oz = 1 USD/lote
    "XAGUSD":  50.0,   # plata — verificar con broker
    "EURUSD":  10.0,
    "GBPUSD":  10.0,
    "USDJPY":  9.1,    # aprox segun USDJPY ~110
    "USDCHF":  10.5,
    "AUDUSD":  10.0,
    "NZDUSD":  10.0,
    "USDCAD":  10.0,
    "EURGBP":  12.5,
    "EURJPY":  9.1,
    "GBPJPY":  9.1,
    "EURAUD":  10.0,
    "GBPAUD":  10.0,
    "AUDJPY":  9.1,
    "US30":    1.0,    # puntos, no pips
    "US500":   10.0,
    "NAS100":  1.0,
    "DE40":    1.0,
}

MIN_LOT  = 0.01
MAX_LOT  = 10.0
LOT_STEP = 0.01


def _load_risk_config() -> dict:
    if CONFIG.exists():
        try:
            cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
            rm  = cfg.get("risk_manager", {})
            return {
                "riesgo_normal":   rm.get("riesgo_normal_pct", 1.0),
                "dd_warning":      rm.get("dd_warning_pct", 3.0),
                "dd_reduccion":    rm.get("dd_reduccion_pct", 4.0),
                "riesgo_reducido": rm.get("riesgo_reducido_pct", 0.5),
                "dd_critico":      rm.get("dd_critico_pct", 6.0),
                "riesgo_minimo":   rm.get("riesgo_minimo_pct", 0.25),
                "dd_stop":         rm.get("dd_stop_pct", 4.8),
            }
        except Exception:
            pass
    return {
        "riesgo_normal": 1.0, "dd_warning": 3.0,
        "dd_reduccion": 4.0,  "riesgo_reducido": 0.5,
        "dd_critico": 6.0,    "riesgo_minimo": 0.25,
        "dd_stop": 4.8,
    }


def _pip_value(activo: str) -> float:
    return PIP_VALUE_USD.get(activo.upper(), 10.0)


def _kelly_fraction(win_rate_pct: float = 50.0, rr_ratio: float = 2.0) -> float:
    """Kelly fraccionado al 25%."""
    p = win_rate_pct / 100.0
    q = 1.0 - p
    b = rr_ratio
    kelly = (p * b - q) / b
    return max(0.0, kelly * 0.25)  # 25% del Kelly


def _adjust_for_portfolio(riesgo_base: float, num_estrategias: int) -> float:
    """Ajusta el riesgo por trade segun el numero de estrategias activas."""
    if num_estrategias <= 1:
        return riesgo_base
    # Con 3 estrategias: 1.0% -> 0.8%; con 5: -> 0.6%; con 8: -> 0.5%
    factor = max(0.5, 1.0 - (num_estrategias - 1) * 0.1)
    return round(riesgo_base * factor, 4)


def _adjust_for_dd(riesgo_base: float, dd_actual: float, cfg: dict) -> tuple[float, str]:
    """Reduce el riesgo segun el DD actual. Devuelve (riesgo_ajustado, razon)."""
    if dd_actual >= cfg["dd_stop"]:
        return 0.0, f"DD {dd_actual:.1f}% >= stop {cfg['dd_stop']:.1f}% — NO OPERAR"
    if dd_actual >= cfg["dd_critico"]:
        return cfg["riesgo_minimo"], f"DD critico ({dd_actual:.1f}%) — riesgo minimo {cfg['riesgo_minimo']:.2f}%"
    if dd_actual >= cfg["dd_reduccion"]:
        return cfg["riesgo_reducido"], f"DD elevado ({dd_actual:.1f}%) — riesgo reducido {cfg['riesgo_reducido']:.2f}%"
    if dd_actual >= cfg["dd_warning"]:
        return riesgo_base * 0.75, f"DD advertencia ({dd_actual:.1f}%) — riesgo -25%"
    return riesgo_base, "DD dentro de limites — riesgo normal"


def calculate_lots(balance: float, sl_pips: float, activo: str,
                   riesgo_pct: float) -> float:
    """Calcula lotes para arriesgar exactamente riesgo_pct del balance."""
    pip_val = _pip_value(activo)
    if pip_val <= 0 or sl_pips <= 0:
        return MIN_LOT

    riesgo_usd = balance * riesgo_pct / 100.0
    lotes_raw  = riesgo_usd / (sl_pips * pip_val)

    # Redondear al step de lote
    lotes = round(lotes_raw / LOT_STEP) * LOT_STEP
    lotes = max(MIN_LOT, min(MAX_LOT, lotes))
    return round(lotes, 2)


def main():
    parser = argparse.ArgumentParser(description="Risk Calculator — TradingLab")
    parser.add_argument("--balance",          type=float, required=True, help="Balance actual de la cuenta")
    parser.add_argument("--sl-pips",          type=float, required=True, help="Stop Loss en pips")
    parser.add_argument("--activo",           required=True,             help="Activo (ej. XAUUSD)")
    parser.add_argument("--dd-actual",        type=float, default=0.0,   help="DD actual en %% (default 0)")
    parser.add_argument("--num-estrategias",  type=int,   default=1,     help="Numero de estrategias activas (default 1)")
    parser.add_argument("--win-rate",         type=float, default=50.0,  help="Win rate estimado %% (para Kelly, default 50)")
    parser.add_argument("--rr-ratio",         type=float, default=2.0,   help="Ratio TP/SL (para Kelly, default 2.0)")
    args = parser.parse_args()

    activo = args.activo.upper()
    cfg    = _load_risk_config()

    # Riesgo base
    riesgo_base = cfg["riesgo_normal"]

    # Ajuste por portfolio
    riesgo_port = _adjust_for_portfolio(riesgo_base, args.num_estrategias)

    # Ajuste por DD actual
    riesgo_final, dd_razon = _adjust_for_dd(riesgo_port, args.dd_actual, cfg)

    if riesgo_final <= 0:
        print(f"\n{'='*55}")
        print(f"  {dd_razon}")
        print(f"  Lotes recomendados : 0 — no abrir posiciones")
        print(f"{'='*55}")
        sys.exit(0)

    # Calcular lotes
    lotes = calculate_lots(args.balance, args.sl_pips, activo, riesgo_final)
    riesgo_usd = args.sl_pips * _pip_value(activo) * lotes

    # Kelly como referencia
    kelly_pct  = _kelly_fraction(args.win_rate, args.rr_ratio)
    kelly_lots = calculate_lots(args.balance, args.sl_pips, activo, kelly_pct) if kelly_pct > 0 else 0

    # Verificar limites FTMO
    max_risk_day_usd = args.balance * cfg["dd_stop"] / 100
    trade_pct_of_day = riesgo_usd / max_risk_day_usd * 100 if max_risk_day_usd > 0 else 0

    print(f"\n{'='*55}")
    print(f"  Risk Calculator — {activo}")
    print(f"{'='*55}")
    print(f"  Balance          : ${args.balance:,.2f}")
    print(f"  SL               : {args.sl_pips} pips")
    print(f"  Valor pip        : ${_pip_value(activo):.2f}/lote")
    print(f"  Estrategias      : {args.num_estrategias}")
    print(f"  DD actual        : {args.dd_actual:.1f}%")
    print(f"{'─'*55}")
    print(f"  Riesgo base      : {riesgo_base:.2f}%")
    if args.num_estrategias > 1:
        print(f"  Riesgo portfolio : {riesgo_port:.2f}% ({args.num_estrategias} estrategias)")
    print(f"  Riesgo final     : {riesgo_final:.2f}%  ({dd_razon})")
    print(f"{'─'*55}")
    print(f"  LOTES            : {lotes:.2f}")
    print(f"  Riesgo USD       : ${riesgo_usd:.2f} ({riesgo_final:.2f}% del balance)")
    print(f"  % del DD diario  : {trade_pct_of_day:.1f}% del limite {cfg['dd_stop']:.1f}%")
    print(f"{'─'*55}")
    print(f"  Kelly ref (25%)  : {kelly_pct:.2f}% → {kelly_lots:.2f} lotes")
    print(f"{'='*55}")

    # Advertencia si el lote es muy alto respecto al DD diario
    if trade_pct_of_day > 50:
        print(f"\n  ADVERTENCIA: este trade consume {trade_pct_of_day:.0f}% del limite DD diario.")
        print(f"  Considera reducir el SL o esperar a que el DD baje.")


if __name__ == "__main__":
    main()
