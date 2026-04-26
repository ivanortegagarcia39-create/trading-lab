#!/usr/bin/env python3
"""
market-regime-snapshot.py — Foto del regimen de mercado al inicio/fin de build

Calcula ADX(14) y ATR(14) sobre un CSV de precios OHLC y clasifica
el regimen. Detecta deriva entre inicio y fin del build.

Uso:
    python market-regime-snapshot.py --prices-csv data/XAUUSD_H1.csv \\
        --build 10 --activo XAUUSD --mode start

    python market-regime-snapshot.py --prices-csv data/XAUUSD_H1.csv \\
        --build 10 --activo XAUUSD --mode end
"""

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SNAPSHOT_PATH = Path("results/build-regime-snapshot.json")

# Umbrales de clasificacion (agents/market-regime-detector.md)
ADX_TENDENCIA = 25.0
ADX_NEUTRAL_LOW = 20.0
ATR_HIGH_MULT = 1.5
ATR_LOW_MULT = 0.7
DERIVA_THRESHOLD = 0.30   # 30%


def load_ohlc(filepath):
    """Lee CSV OHLC. Acepta coma y semicolon como delimitador."""
    rows = []
    for delim in (",", ";", "\t"):
        try:
            with open(filepath, encoding="utf-8-sig", errors="replace") as f:
                reader = csv.DictReader(f, delimiter=delim)
                data = list(reader)
                if data and len(data[0]) >= 4:
                    rows = data
                    break
        except Exception:
            continue
    if not rows:
        print(f"[ERROR] No se puede leer {filepath}")
        sys.exit(1)
    return rows


def find_col(headers, candidates):
    for c in candidates:
        for h in headers:
            if c.lower() == h.strip().lower():
                return h.strip()
    return None


def to_float(val):
    try:
        return float(str(val).replace(",", ".").strip())
    except (ValueError, TypeError):
        return None


def extract_ohlc(rows):
    if not rows:
        return [], [], [], []
    headers = list(rows[0].keys())
    h_col = find_col(headers, ["High", "high", "H"])
    l_col = find_col(headers, ["Low", "low", "L"])
    c_col = find_col(headers, ["Close", "close", "C", "Price"])
    if not all([h_col, l_col, c_col]):
        print(f"[ERROR] No se encuentran columnas High/Low/Close. Headers: {headers}")
        sys.exit(1)
    highs  = [to_float(r[h_col]) for r in rows]
    lows   = [to_float(r[l_col]) for r in rows]
    closes = [to_float(r[c_col]) for r in rows]
    return highs, lows, closes


def calc_atr(highs, lows, closes, period=14):
    """ATR(period) — True Range medio."""
    trs = []
    for i in range(1, len(closes)):
        h, l, pc = highs[i], lows[i], closes[i - 1]
        if None in (h, l, pc):
            continue
        tr = max(h - l, abs(h - pc), abs(l - pc))
        trs.append(tr)
    if len(trs) < period:
        return None, None
    # ATR actual: media de los ultimos `period` TRs
    atr_current = sum(trs[-period:]) / period
    # Media ATR de 20 periodos: media de los ultimos 20 valores ATR(14)
    atr_series = []
    for i in range(period, len(trs) + 1):
        atr_series.append(sum(trs[i - period:i]) / period)
    if len(atr_series) < 20:
        atr_mean_20 = sum(atr_series) / len(atr_series)
    else:
        atr_mean_20 = sum(atr_series[-20:]) / 20
    return round(atr_current, 5), round(atr_mean_20, 5)


def calc_adx(highs, lows, closes, period=14, lookback=50):
    """ADX(period) simplificado sobre los ultimos `lookback` periodos."""
    # Usar solo los ultimos lookback+period+1 velas para eficiencia
    n = lookback + period + 1
    highs  = highs[-n:]
    lows   = lows[-n:]
    closes = closes[-n:]

    plus_dm  = []
    minus_dm = []
    trs      = []

    for i in range(1, len(closes)):
        h,  l,  c  = highs[i],  lows[i],  closes[i]
        ph, pl, pc = highs[i-1], lows[i-1], closes[i-1]
        if None in (h, l, c, ph, pl, pc):
            plus_dm.append(0)
            minus_dm.append(0)
            trs.append(0)
            continue
        up   = h - ph
        down = pl - l
        pdm  = up   if (up > down and up > 0)   else 0
        mdm  = down if (down > up and down > 0) else 0
        plus_dm.append(pdm)
        minus_dm.append(mdm)
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))

    if len(trs) < period * 2:
        return None

    def smooth(arr, p):
        s = sum(arr[:p])
        result = [s]
        for v in arr[p:]:
            s = s - s / p + v
            result.append(s)
        return result

    str_atr  = smooth(trs,      period)
    str_pdm  = smooth(plus_dm,  period)
    str_mdm  = smooth(minus_dm, period)

    dx_vals = []
    for i in range(len(str_atr)):
        atr_v = str_atr[i]
        if atr_v == 0:
            continue
        pdi = 100 * str_pdm[i] / atr_v
        mdi = 100 * str_mdm[i] / atr_v
        s   = pdi + mdi
        dx_vals.append(100 * abs(pdi - mdi) / s if s > 0 else 0)

    if len(dx_vals) < period:
        return None
    adx = sum(dx_vals[-period:]) / period
    return round(adx, 2)


def classify_regime(adx, atr, atr_mean):
    """Devuelve regimen, adx_cat, vol_cat."""
    if adx is None:
        return "desconocido", "DESCONOCIDO", "DESCONOCIDO"

    if adx > ADX_TENDENCIA:
        adx_cat = "TENDENCIA_ACTIVA"
        trend   = "tendencia"
    elif adx >= ADX_NEUTRAL_LOW:
        adx_cat = "ZONA_NEUTRAL"
        trend   = "neutral"
    else:
        adx_cat = "RANGO"
        trend   = "rango"

    if atr is None or atr_mean is None or atr_mean == 0:
        vol_cat = "VOLATILIDAD_NORMAL"
        vol     = "normalvol"
    elif atr > atr_mean * ATR_HIGH_MULT:
        vol_cat = "VOLATILIDAD_ALTA"
        vol     = "altavol"
    elif atr < atr_mean * ATR_LOW_MULT:
        vol_cat = "VOLATILIDAD_BAJA"
        vol     = "bajovol"
    else:
        vol_cat = "VOLATILIDAD_NORMAL"
        vol     = "normalvol"

    # Regimen final (4 regimenes de market-regime-detector.md)
    if trend == "neutral":
        base = "rango" if adx < (ADX_TENDENCIA + ADX_NEUTRAL_LOW) / 2 else "tendencia"
        regime = f"{base}-{vol} (neutral ADX)"
    else:
        regime = f"{trend}-{vol}"

    return regime, adx_cat, vol_cat


def mode_start(args, adx, atr, atr_mean, regime, adx_cat, vol_cat):
    snapshot = {
        "build_num":             args.build,
        "activo":                args.activo,
        "snapshot_inicio": {
            "timestamp":         datetime.now(timezone.utc).isoformat(),
            "adx_14":            adx,
            "atr_14":            atr,
            "atr_media_20p":     atr_mean,
            "atr_ratio":         round(atr / atr_mean, 3) if (atr and atr_mean) else None,
            "regimen":           regime,
            "adx_categoria":     adx_cat,
            "vol_categoria":     vol_cat,
        },
        "snapshot_fin": {
            "timestamp": None, "adx_14": None, "atr_14": None,
            "atr_media_20p": None, "atr_ratio": None, "regimen": None,
        },
        "deriva_adx_pct":    None,
        "build_en_curso":    True,
        "advertencia_deriva": False,
    }
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    print(f"\n=== REGIME SNAPSHOT — INICIO ===")
    print(f"Build:    {args.build} | Activo: {args.activo}")
    print(f"ADX(14):  {adx} → {adx_cat}")
    print(f"ATR(14):  {atr} (media 20p: {atr_mean}) → {vol_cat}")
    print(f"Regimen:  {regime}")
    print(f"Guardado: {SNAPSHOT_PATH}")


def mode_end(args, adx, atr, atr_mean, regime, adx_cat, vol_cat):
    if not SNAPSHOT_PATH.exists():
        print(f"[ERROR] No existe snapshot de inicio: {SNAPSHOT_PATH}")
        sys.exit(1)
    with open(SNAPSHOT_PATH, encoding="utf-8") as f:
        snapshot = json.load(f)

    adx_inicio = snapshot.get("snapshot_inicio", {}).get("adx_14")
    deriva = None
    advertencia = False
    if adx_inicio and adx_inicio > 0 and adx is not None:
        deriva = round(abs(adx - adx_inicio) / adx_inicio, 4)
        advertencia = deriva > DERIVA_THRESHOLD

    snapshot["snapshot_fin"] = {
        "timestamp":     datetime.now(timezone.utc).isoformat(),
        "adx_14":        adx,
        "atr_14":        atr,
        "atr_media_20p": atr_mean,
        "atr_ratio":     round(atr / atr_mean, 3) if (atr and atr_mean) else None,
        "regimen":       regime,
        "adx_categoria": adx_cat,
        "vol_categoria": vol_cat,
    }
    snapshot["deriva_adx_pct"]    = deriva
    snapshot["build_en_curso"]     = False
    snapshot["advertencia_deriva"] = advertencia

    with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)

    print(f"\n=== REGIME SNAPSHOT — FIN ===")
    print(f"Build:     {args.build} | Activo: {args.activo}")
    print(f"ADX fin:   {adx} → {adx_cat}")
    print(f"Regimen:   {regime}")
    print(f"Deriva ADX: {deriva*100:.1f}%" if deriva is not None else "Deriva ADX: N/A")
    if advertencia:
        reg_inicio = snapshot["snapshot_inicio"].get("regimen", "?")
        print(f"\n[WARNING] Deriva ADX > 30%")
        print(f"  Regimen inicio: {reg_inicio}")
        print(f"  Regimen fin:    {regime}")
        print(f"  Las estrategias pueden estar optimizadas para un regimen que ya no existe.")
    print(f"Guardado: {SNAPSHOT_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Foto del regimen de mercado para un build de SQ")
    parser.add_argument("--prices-csv", required=True, help="CSV de precios OHLC del activo")
    parser.add_argument("--build",      required=True, type=int, help="Numero del build")
    parser.add_argument("--activo",     required=True, help="Simbolo del activo (ej: XAUUSD)")
    parser.add_argument("--mode",       required=True, choices=["start", "end"])
    args = parser.parse_args()

    rows           = load_ohlc(args.prices_csv)
    highs, lows, closes = extract_ohlc(rows)

    adx      = calc_adx(highs, lows, closes)
    atr, atr_mean = calc_atr(highs, lows, closes)
    regime, adx_cat, vol_cat = classify_regime(adx, atr, atr_mean)

    if args.mode == "start":
        mode_start(args, adx, atr, atr_mean, regime, adx_cat, vol_cat)
    else:
        mode_end(args, adx, atr, atr_mean, regime, adx_cat, vol_cat)


if __name__ == "__main__":
    main()
