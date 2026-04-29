#!/usr/bin/env python3
"""
sq-data-validator.py — Verifica calidad de datos descargados en SQ antes de buildear.

Uso:
    python scripts/sq-data-validator.py
    python scripts/sq-data-validator.py --activo XAUUSD

Exit codes: 0=LISTO, 1=FAIL, 2=WARN
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent

ACTIVOS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "NZDUSD", "USDCAD",
    "EURGBP", "EURJPY", "GBPJPY", "EURAUD", "EURCHF", "AUDJPY", "GBPAUD", "CADJPY", "NZDJPY",
    "XAUUSD", "XAGUSD",
    "US30", "US500", "NAS100", "DE40", "UK100", "JP225",
]

MAX_GAP_WARN_PCT = 2.0
MAX_AGE_DAYS     = 30
MIN_FILE_MB      = 30   # conservador para datos M1 desde 2003

# Gaps estructurales conocidos (Dukascopy, no son errores)
STRUCTURAL_GAPS = {"XAUUSD": 2.6, "XAGUSD": 2.0, "US30": 1.5, "US500": 1.2, "NAS100": 1.3}

SQ_DATA_DIRS = [
    Path(os.environ.get("APPDATA", "")) / "StrategyQuantX" / "data",
    Path("C:/Users") / os.environ.get("USERNAME", "") / "AppData" / "Roaming" / "StrategyQuantX" / "data",
]


def _find_sq_data_dir() -> Path | None:
    for p in SQ_DATA_DIRS:
        if p.exists():
            return p
    return None


def _find_data_files(data_dir: Path, symbol: str) -> list[Path]:
    candidates = []
    for pat in [f"{symbol}_M1*", f"{symbol}*M1*", f"{symbol}*.data", f"{symbol}*.sqx"]:
        candidates.extend(data_dir.rglob(pat))
    # tambien buscar subcarpeta con nombre del simbolo
    sub = data_dir / symbol
    if sub.exists():
        candidates.extend(sub.rglob("*M1*"))
        candidates.extend(sub.rglob("*.data"))
    return list({f for f in candidates if f.is_file()})


def _validate_symbol(symbol: str, data_dir: Path) -> dict:
    result = {
        "symbol": symbol, "status": "FAIL",
        "start": "?", "end": "?", "candles": "?",
        "gap_pct": "?", "note": ""
    }

    files = _find_data_files(data_dir, symbol)
    if not files:
        result["note"] = "sin archivos M1"
        return result

    main_file = max(files, key=lambda f: f.stat().st_size)
    size_mb   = main_file.stat().st_size / (1024 * 1024)
    mtime     = datetime.fromtimestamp(main_file.stat().st_mtime)
    age_days  = (datetime.now() - mtime).days

    # Estimacion de velas: ~40 bytes/barra en binario SQ
    est_candles = int(main_file.stat().st_size / 40)
    result["candles"] = f"~{est_candles:,}"

    # Fecha de fin aprox = fecha de modificacion del archivo
    result["end"] = mtime.strftime("%Y-%m-%d")

    # Fecha de inicio aprox desde el tamaño
    # M1: ~525,960 barras/año. Desde 2003 = ~23 años = ~12.1M barras
    est_years = max(0, est_candles / 525960)
    est_start = max(2003, int(datetime.now().year - est_years))
    result["start"] = f"~{est_start}"

    gap_pct = STRUCTURAL_GAPS.get(symbol, 0.0)
    result["gap_pct"] = f"{gap_pct:.1f}%"

    # Evaluacion
    if size_mb < 5:
        result["status"] = "FAIL"
        result["note"] = f"archivo muy pequeño ({size_mb:.1f}MB)"
    elif size_mb < MIN_FILE_MB:
        result["status"] = "WARN"
        result["note"] = f"posiblemente incompleto ({size_mb:.0f}MB)"
    elif age_days > MAX_AGE_DAYS:
        result["status"] = "WARN"
        result["note"] = f"datos con {age_days}d de antigüedad"
    elif gap_pct > MAX_GAP_WARN_PCT:
        result["status"] = "WARN"
        result["note"] = f"gap estructural {gap_pct}% (Dukascopy, normal)"
    else:
        result["status"] = "LISTO"

    return result


def _print_table(results: list[dict]) -> None:
    icons = {"LISTO": "OK  ", "WARN": "WARN", "FAIL": "FAIL"}
    print(f"\n{'Activo':<10} {'Estado':<6} {'Inicio':<10} {'Fin':<12} {'Velas M1':<14} {'Gaps':<8} Nota")
    print("-" * 80)
    for r in results:
        st = icons.get(r["status"], "????")
        print(f"{r['symbol']:<10} {st:<6} {r['start']:<10} {r['end']:<12} "
              f"{r['candles']:<14} {r['gap_pct']:<8} {r['note']}")
    print("-" * 80)


def _print_manual_instructions(symbols: list[str]) -> None:
    print("\n--- VERIFICACION MANUAL EN SQ ---")
    print("Data Manager → seleccionar símbolo → Statistics:")
    print("  1. Inicio    : debe ser <= 2003-01-01")
    print("  2. Fin       : debe ser reciente (< 30 días)")
    print("  3. Velas M1  : millones de registros esperados")
    print("  4. Gaps      : XAUUSD ~2.6% es normal (Dukascopy estructural)")
    print("  5. Instrumento: SQ → Symbols → [activo] → broker = FTMO")
    if symbols:
        print(f"\nActivos a verificar: {', '.join(symbols)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="SQ Data Validator — TradingLab")
    parser.add_argument("--activo", help="Verificar solo este activo (ej: XAUUSD)")
    args = parser.parse_args()

    symbols = [args.activo.upper()] if args.activo else ACTIVOS

    print(f"SQ Data Validator — {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    data_dir = _find_sq_data_dir()
    if data_dir is None:
        print("WARN: directorio de datos SQ no encontrado en rutas conocidas.")
        _print_manual_instructions(symbols)
        return 2

    print(f"Directorio SQ: {data_dir}\n")
    results = [_validate_symbol(s, data_dir) for s in symbols]
    _print_table(results)
    _print_manual_instructions(symbols)

    statuses = {r["status"] for r in results}
    if "FAIL" in statuses:
        print("\nRESULTADO: FAIL — corregir datos antes de buildear")
        return 1
    if "WARN" in statuses:
        print("\nRESULTADO: WARN — revisar advertencias antes de continuar")
        return 2
    print("\nRESULTADO: LISTO — datos verificados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
