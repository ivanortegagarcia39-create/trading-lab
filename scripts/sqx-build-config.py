#!/usr/bin/env python3
"""
sqx-build-config.py — Documenta la configuracion exacta de cada build de SQ

Genera results/build-N-config.json y results/build-N-config.md.
Valida que spread_backtest_sucio = 2 * spread_real_ftmo.

Uso:
    python sqx-build-config.py --build 10 --activo XAUUSD --spread-real 30
    python sqx-build-config.py --build 11 --activo EURUSD --spread-real 0.5 --notas "primer build EURUSD"
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Defaults de configuracion (config/build-defaults.json si existe)
DEFAULTS_PATH = Path("config/build-defaults.json")


def load_defaults():
    if DEFAULTS_PATH.exists():
        with open(DEFAULTS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def build_config(args, defaults):
    spread_real    = args.spread_real
    spread_backtest = args.spread_backtest if args.spread_backtest else spread_real * 2
    spread_ok      = abs(spread_backtest - spread_real * 2) < 0.01

    slippage_map = defaults.get("slippage_pips", {})
    slippage     = slippage_map.get(args.activo.upper(), 0.5)

    comision  = defaults.get("comision_usd_por_lote", 7)
    capital   = defaults.get("capital_inicial", 25000)
    riesgo    = defaults.get("riesgo_por_trade_pct", 1)
    max_trades = defaults.get("max_trades_dia", 2)
    sesion_ini = defaults.get("sesion_inicio", "08:00")
    sesion_fin = defaults.get("sesion_fin", "20:00")

    sl_mult   = defaults.get("sl_atr_multiplicador", {"min": 1.5, "max": 3.0})
    tp_mult   = defaults.get("tp_atr_multiplicador", {"min": 3.0, "max": 6.0})
    genetica  = defaults.get("genetica", {
        "generaciones": 30, "poblacion_por_isla": 100,
        "islas": 4, "modo_continuo": True, "max_estrategias": 1000
    })
    filtros_sq = defaults.get("filtros_sq", {
        "pf_minimo": 1.3, "trades_mes_minimo": 6, "ret_dd_minimo": 0.8
    })
    filtros_py = defaults.get("filtros_python", {
        "H1": {"total_trades": 120, "win_rate": 38, "dd_max": 7}
    })
    tf_filtros = filtros_py.get(args.timeframe, filtros_py.get("H1", {}))

    swaps = defaults.get("swaps_ftmo", {}).get(args.activo.upper(), {})

    cfg = {
        "build_num":            args.build,
        "fecha":                datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "activo":               args.activo.upper(),
        "simbolo_sq":           args.simbolo_sq or args.activo.upper(),
        "instrumento":          args.instrumento or args.activo.upper(),
        "timeframe":            args.timeframe,
        "periodo_is":           args.periodo_is,
        "periodo_oos":          args.periodo_oos,
        "spread_real_ftmo":     spread_real,
        "spread_backtest_sucio": spread_backtest,
        "spread_2x_correcto":   spread_ok,
        "slippage_configurado": slippage,
        "comision_usd_lote":    comision,
        "riesgo_por_trade_pct": riesgo,
        "capital_inicial":      capital,
        "max_trades_dia":       max_trades,
        "sesion_inicio":        sesion_ini,
        "sesion_fin":           sesion_fin,
        "sl_atr_multiplicador": sl_mult,
        "tp_atr_multiplicador": tp_mult,
        "ratio_tp_sl_minimo_pct": defaults.get("ratio_tp_sl_minimo_pct", 200),
        "genetica":             genetica,
        "filtros_sq":           filtros_sq,
        "filtros_python":       tf_filtros,
        "comprobaciones_cruzadas": True,
        "swaps_ftmo":           swaps,
        "notas":                args.notas or "",
        "advertencias":         [],
    }

    if not spread_ok:
        msg = (
            f"SPREAD NO ES 2x EL REAL FTMO: "
            f"configurado {spread_backtest} pips, "
            f"requerido {spread_real * 2} pips. "
            f"Corregir antes del proximo build."
        )
        cfg["advertencias"].append(msg)
        print(f"\n[WARNING] {msg}")

    return cfg


def save_json(cfg, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def save_md(cfg, path):
    warns = cfg["advertencias"]
    warn_block = ""
    if warns:
        warn_block = "\n## ADVERTENCIAS\n\n"
        for w in warns:
            warn_block += f"- **{w}**\n"
        warn_block += "\n"

    spread_status = "OK" if cfg["spread_2x_correcto"] else "ERROR — no es 2x el real"

    md = f"""# Build {cfg['build_num']} — {cfg['activo']} — Configuracion SQ
{warn_block}
## Identificacion

| Campo | Valor |
|-------|-------|
| Build | {cfg['build_num']} |
| Fecha | {cfg['fecha']} |
| Activo | {cfg['activo']} |
| Simbolo SQ | {cfg['simbolo_sq']} |
| Timeframe | {cfg['timeframe']} |
| Periodo IS | {cfg['periodo_is']} |
| Periodo OOS | {cfg['periodo_oos']} |

## Costes y Ejecucion

| Campo | Valor | Estado |
|-------|-------|--------|
| Spread real FTMO | {cfg['spread_real_ftmo']} pips | — |
| Spread backtest sucio | {cfg['spread_backtest_sucio']} pips | {spread_status} |
| Slippage | {cfg['slippage_configurado']} pips | — |
| Comision | {cfg['comision_usd_lote']} USD/lote | — |

## Gestion de Riesgo

| Campo | Valor |
|-------|-------|
| Riesgo por trade | {cfg['riesgo_por_trade_pct']}% |
| Capital inicial | {cfg['capital_inicial']} USD |
| Max trades/dia | {cfg['max_trades_dia']} |
| Sesion | {cfg['sesion_inicio']} – {cfg['sesion_fin']} CEST |

## Configuracion Genetica

| Campo | Valor |
|-------|-------|
| Generaciones | {cfg['genetica'].get('generaciones')} |
| Poblacion/isla | {cfg['genetica'].get('poblacion_por_isla')} |
| Islas | {cfg['genetica'].get('islas')} |
| Modo continuo | {cfg['genetica'].get('modo_continuo')} |
| Max estrategias | {cfg['genetica'].get('max_estrategias')} |

## Filtros Activos

### Filtros SQ (en Builder)
- PF minimo: {cfg['filtros_sq'].get('pf_minimo')}
- Trades/mes minimo: {cfg['filtros_sq'].get('trades_mes_minimo')}
- Ret/DD minimo: {cfg['filtros_sq'].get('ret_dd_minimo')}

### Filtros Python (evaluator-assistant.py)
- Total trades: {cfg['filtros_python'].get('total_trades')}
- Win Rate: {cfg['filtros_python'].get('win_rate')}%
- DD maximo: {cfg['filtros_python'].get('dd_max')}%

## Notas

{cfg['notas'] if cfg['notas'] else 'Sin notas adicionales.'}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)


def main():
    parser = argparse.ArgumentParser(
        description="Documenta la configuracion exacta de un build de SQ"
    )
    parser.add_argument("--build",         required=True, type=int)
    parser.add_argument("--activo",        required=True)
    parser.add_argument("--spread-real",   required=True, type=float,
                        help="Spread real del activo en FTMO (pips)")
    parser.add_argument("--spread-backtest", type=float,
                        help="Spread configurado en backtest (default: spread-real * 2)")
    parser.add_argument("--timeframe",     default="H1", choices=["H1", "H4", "M30", "M15"])
    parser.add_argument("--periodo-is",    default="2003-2020")
    parser.add_argument("--periodo-oos",   default="2021-actual")
    parser.add_argument("--simbolo-sq",    help="Nombre exacto del simbolo en SQ")
    parser.add_argument("--instrumento",   help="Instrumento del broker")
    parser.add_argument("--notas",         help="Notas libres sobre el build")
    parser.add_argument("--output-dir",    default="results")
    args = parser.parse_args()

    defaults = load_defaults()
    cfg      = build_config(args, defaults)

    out_dir  = Path(args.output_dir)
    json_path = out_dir / f"build-{args.build}-config.json"
    md_path   = out_dir / f"build-{args.build}-config.md"

    save_json(cfg, json_path)
    save_md(cfg, md_path)

    print(f"\n=== SQX BUILD CONFIG — Build {args.build} ===")
    print(f"Activo:          {cfg['activo']}")
    print(f"Spread real:     {cfg['spread_real_ftmo']} pips")
    print(f"Spread backtest: {cfg['spread_backtest_sucio']} pips ({'OK' if cfg['spread_2x_correcto'] else 'ERROR'})")
    print(f"JSON:            {json_path}")
    print(f"Markdown:        {md_path}")

    if cfg["advertencias"]:
        sys.exit(2)


if __name__ == "__main__":
    main()
