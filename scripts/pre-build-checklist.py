#!/usr/bin/env python3
"""
pre-build-checklist.py — Verificacion antes de lanzar un build en SQ

Evita lanzar builds con configuracion incorrecta.
Salida: PASS (exit 0), WARN (exit 2), FAIL (exit 1)

Uso:
    python pre-build-checklist.py --activo XAUUSD --spread 60 --oos-end 2026-04-20
    python pre-build-checklist.py --activo EURUSD --spread 1.0 --data-path data/EURUSD/
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Spreads minimos requeridos: 2x spread real (skill-builder-libre.md)
REQUIRED_SPREADS = {
    "XAUUSD": 60.0,   # 30 pips real * 2
    "XAGUSD":  6.0,   # 3 pips real * 2
    "EURUSD":  1.0,   # 0.5 pips real * 2
    "GBPUSD":  1.6,   # 0.8 pips real * 2
    "USDJPY":  1.0,
    "USDCHF":  1.4,
    "AUDUSD":  1.2,
    "NZDUSD":  1.6,
    "USDCAD":  1.4,
    "EURGBP":  1.6,
    "EURJPY":  2.0,
    "GBPJPY":  2.4,
    "EURAUD":  3.0,
    "GBPAUD":  3.0,
    "AUDJPY":  2.0,
    "US30":   10.0,
    "US500":   2.0,
    "NAS100": 10.0,
    "DE40":    6.0,
}


def check_spread(activo, spread_configurado):
    required = REQUIRED_SPREADS.get(activo.upper())
    if required is None:
        return "WARN", (
            f"Activo {activo} no tiene spread de referencia configurado. "
            f"Verificar manualmente que es >= 2x spread real de FTMO."
        )
    if spread_configurado is None:
        return "FAIL", (
            f"Spread no especificado. "
            f"Requerido para {activo}: >= {required} pips (2x spread real)."
        )
    if spread_configurado < required:
        return "FAIL", (
            f"Spread {spread_configurado} pips < {required} pips requeridos "
            f"(2x spread real para {activo}). Corregir en SQ antes de lanzar."
        )
    return "PASS", f"Spread {spread_configurado} pips >= {required} pips (OK)"


def check_oos_date(oos_end_date_str):
    if oos_end_date_str is None:
        return "WARN", "Fecha OOS no especificada. Verificar que OOS termina en fecha reciente (< 30 dias)."
    try:
        oos_end = datetime.strptime(oos_end_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        now     = datetime.now(timezone.utc)
        days    = (now - oos_end).days
        if days > 30:
            return "WARN", (
                f"OOS termina hace {days} dias ({oos_end_date_str}). "
                f"Recomendado: actualizar datos antes del build."
            )
        return "PASS", f"OOS termina en {oos_end_date_str} ({days} dias antes de hoy — OK)"
    except ValueError:
        return "WARN", f"Formato de fecha OOS incorrecto: '{oos_end_date_str}'. Usar YYYY-MM-DD."


def check_data(data_path, activo):
    if data_path is None:
        return "WARN", (
            f"Ruta de datos no especificada para {activo}. "
            f"Verificar manualmente que los datos M1 estan disponibles en SQ."
        )
    p = Path(data_path)
    if not p.exists():
        return "FAIL", f"No se encuentra: {data_path}. Datos M1 no disponibles para {activo}."
    mtime    = datetime.fromtimestamp(p.stat().st_mtime)
    days_old = (datetime.now() - mtime).days
    if days_old > 7:
        return "WARN", (
            f"Datos de {activo} modificados hace {days_old} dias. "
            f"Recomendado: actualizar antes del build."
        )
    return "PASS", f"Datos de {activo} actualizados hace {days_old} dias (OK)"


def check_pipeline_lock(results_dir):
    lock = Path(results_dir) / "pipeline.lock"
    if lock.exists():
        mtime = datetime.fromtimestamp(lock.stat().st_mtime)
        return "WARN", (
            f"pipeline.lock existe (modificado: {mtime.strftime('%Y-%m-%d %H:%M')}). "
            f"Puede haber otro proceso corriendo."
        )
    return "PASS", "No hay pipeline.lock activo"


def check_data_freshness(data_path, activo):
    """Alias de check_data para compatibilidad."""
    return check_data(data_path, activo)


def main():
    parser = argparse.ArgumentParser(
        description="Verificacion pre-build — evita builds con configuracion incorrecta"
    )
    parser.add_argument("--activo",      required=True, help="Simbolo del activo (ej: XAUUSD)")
    parser.add_argument("--spread",      type=float,    help="Spread configurado en SQ (pips)")
    parser.add_argument("--oos-end",                    help="Fecha fin del periodo OOS (YYYY-MM-DD)")
    parser.add_argument("--data-path",                  help="Ruta a carpeta/archivo de datos M1")
    parser.add_argument("--results-dir", default="results", help="Carpeta de resultados del pipeline")
    parser.add_argument("--output",      default="results/pre-build-check.json")
    args = parser.parse_args()

    checks  = []
    overall = "PASS"

    def add(name, status, message):
        nonlocal overall
        checks.append({"check": name, "status": status, "message": message})
        if status == "FAIL":
            overall = "FAIL"
        elif status == "WARN" and overall == "PASS":
            overall = "WARN"

    add("Spread 2x configurado",    *check_spread(args.activo, args.spread))
    add("OOS date reciente",        *check_oos_date(args.oos_end))
    add("Datos M1 disponibles",     *check_data(args.data_path, args.activo))
    add("Sin pipeline.lock activo", *check_pipeline_lock(args.results_dir))

    result = {
        "timestamp":          datetime.utcnow().isoformat() + "Z",
        "activo":             args.activo,
        "spread_configurado": args.spread,
        "resultado_global":   overall,
        "checks":             checks,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    icons = {"PASS": " OK ", "WARN": "WARN", "FAIL": "FAIL"}
    print(f"\n{'='*40}")
    print(f"PRE-BUILD CHECKLIST — {args.activo}")
    print(f"{'='*40}")
    for c in checks:
        print(f"  [{icons[c['status']]}] {c['check']}")
        print(f"         {c['message']}")
    print(f"\nRESULTADO: {overall}")
    print(f"Guardado en: {out_path}")

    exit_codes = {"PASS": 0, "WARN": 2, "FAIL": 1}
    sys.exit(exit_codes[overall])


if __name__ == "__main__":
    main()
