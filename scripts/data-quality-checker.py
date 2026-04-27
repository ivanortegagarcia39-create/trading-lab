#!/usr/bin/env python3
"""
data-quality-checker.py — Verifica calidad de datos M1 para builds

Uso:
    python scripts/data-quality-checker.py --data-folder data/
    python scripts/data-quality-checker.py --data-folder data/ --activo XAUUSD

Formato CSV esperado (exportado desde Dukascopy/SQ):
    timestamp,open,high,low,close,volume
    2003-01-02 00:00:00,1234.5,1235.0,1234.0,1234.8,100

Limitaciones conocidas documentadas:
    XAUUSD M1 Dukascopy: gaps estructurales ~2.6% — aceptable para H1
    EURUSD M1 Dukascopy: gaps ~0.16% — excelente
"""

import argparse
import csv
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
RESULTS_DIR = ROOT / "results"
CONFIG_PATH = ROOT / "config" / "build-defaults.json"

# Thresholds de gaps aceptables por tipo de activo
GAP_THRESHOLDS = {
    "XAUUSD": 5.0,   # gaps estructurales Dukascopy ~2.6%
    "XAGUSD": 5.0,
    "default_metals": 5.0,
    "default_forex": 0.5,
    "default_indices": 2.0,
    "default_crypto": 10.0,
}

KNOWN_GAPS = {
    "XAUUSD": {"expected_pct": 2.6, "note": "gaps estructurales Dukascopy — aceptable para H1"},
    "EURUSD": {"expected_pct": 0.16, "note": "calidad excelente"},
}

DATA_START_MIN = datetime(2003, 1, 1)


def _load_activos() -> list[str]:
    if not CONFIG_PATH.exists():
        return []
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return list(cfg.get("spreads_ftmo", {}).keys())


def _gap_threshold(activo: str) -> float:
    if activo in GAP_THRESHOLDS:
        return GAP_THRESHOLDS[activo]
    activo_upper = activo.upper()
    if any(x in activo_upper for x in ["XAU", "XAG"]):
        return GAP_THRESHOLDS["default_metals"]
    if any(x in activo_upper for x in ["BTC", "ETH"]):
        return GAP_THRESHOLDS["default_crypto"]
    if any(x in activo_upper for x in ["US30", "US500", "NAS", "DE40", "UK100", "JP225"]):
        return GAP_THRESHOLDS["default_indices"]
    return GAP_THRESHOLDS["default_forex"]


def _parse_timestamps(csv_path: Path) -> list[datetime]:
    timestamps = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if not row:
                continue
            ts_raw = row[0].strip()
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y.%m.%d %H:%M"):
                try:
                    timestamps.append(datetime.strptime(ts_raw, fmt))
                    break
                except ValueError:
                    continue
    return sorted(timestamps)


def _analyze_gaps(timestamps: list[datetime]) -> dict:
    """Calcula gaps esperados vs reales en velas M1 (solo sesiones Forex)."""
    if len(timestamps) < 2:
        return {"gaps": 0, "total_expected": 0, "gap_pct": 0.0}

    start = timestamps[0]
    end = timestamps[-1]
    total_minutes = int((end - start).total_seconds() / 60)

    # Contar velas reales presentes
    ts_set = set(timestamps)
    actual = len(ts_set)

    # Estimar velas esperadas: 24h * 5 dias/semana aprox
    # Para M1: ~7200 velas/semana en mercado 24h5d
    weeks = total_minutes / (60 * 24 * 7)
    expected = int(weeks * 60 * 24 * 5)  # aprox sesion forex
    if expected == 0:
        expected = total_minutes

    gaps = max(0, expected - actual)
    gap_pct = gaps / expected * 100 if expected > 0 else 0.0

    return {
        "total_candles": actual,
        "total_expected_approx": expected,
        "gaps_estimated": gaps,
        "gap_pct": round(gap_pct, 4),
        "date_start": start.strftime("%Y-%m-%d"),
        "date_end": end.strftime("%Y-%m-%d"),
        "years_coverage": round((end - start).days / 365.25, 1),
    }


def check_activo(csv_path: Path, activo: str) -> dict:
    result = {
        "activo": activo,
        "csv": str(csv_path),
        "status": "OK",
        "warnings": [],
        "errors": [],
    }

    if not csv_path.exists():
        result["status"] = "NO_DATA"
        result["errors"].append(f"CSV no encontrado: {csv_path}")
        return result

    timestamps = _parse_timestamps(csv_path)
    if not timestamps:
        result["status"] = "EMPTY"
        result["errors"].append("CSV vacio o formato de timestamp no reconocido")
        return result

    gap_data = _analyze_gaps(timestamps)
    result.update(gap_data)

    threshold = _gap_threshold(activo)
    gap_pct = gap_data["gap_pct"]

    # Verificar fecha inicio
    start = datetime.strptime(gap_data["date_start"], "%Y-%m-%d")
    if start > DATA_START_MIN:
        years_missing = round((start - DATA_START_MIN).days / 365.25, 1)
        result["warnings"].append(
            f"Datos inician en {gap_data['date_start']} — faltan ~{years_missing} años desde 2003"
        )

    # Verificar gaps
    known = KNOWN_GAPS.get(activo, {})
    if gap_pct <= threshold:
        if known:
            result["warnings"].append(
                f"Gaps {gap_pct:.2f}% — {known.get('note', '')} "
                f"(esperado ~{known.get('expected_pct', 0):.2f}%)"
            )
    else:
        result["status"] = "WARN"
        result["warnings"].append(
            f"Gaps {gap_pct:.2f}% supera umbral {threshold:.1f}% para {activo}"
        )

    # Verificar cobertura minima
    if gap_data["years_coverage"] < 10:
        result["status"] = "WARN"
        result["warnings"].append(
            f"Cobertura solo {gap_data['years_coverage']} años — recomendado >= 10 para IS robusto"
        )

    if result["status"] == "OK" and not result["warnings"]:
        result["note"] = "Calidad optima"

    return result


def _ollama_comment(results: list[dict]) -> str | None:
    try:
        import urllib.request, json as json_mod, ssl
        summary = "; ".join(
            f"{r['activo']}: gaps={r.get('gap_pct', 'N/A')}%, cobertura={r.get('years_coverage', 'N/A')}a"
            for r in results if r["status"] != "NO_DATA"
        )
        prompt = (
            f"Analiza brevemente la calidad de datos de trading: {summary}. "
            "Responde en 2-3 lineas: si los datos son adecuados para backtesting y que precauciones tomar."
        )
        payload = json_mod.dumps({"model": "deepseek-r1:7b", "prompt": prompt, "stream": False}).encode()
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=payload, headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            return json_mod.loads(resp.read())["response"].strip()
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="Data Quality Checker — TradingLab")
    parser.add_argument("--data-folder", required=True, help="Carpeta con CSVs de datos M1")
    parser.add_argument("--activo", help="Verificar solo este activo (ej. XAUUSD)")
    args = parser.parse_args()

    data_folder = Path(args.data_folder)
    if not data_folder.exists():
        print(f"ERROR: carpeta no encontrada: {data_folder}")
        sys.exit(1)

    activos = [args.activo] if args.activo else _load_activos()
    if not activos:
        # Detectar CSVs presentes
        activos = [f.stem.upper() for f in data_folder.glob("*.csv")]

    if not activos:
        print("ERROR: no hay activos en config/build-defaults.json ni CSVs en la carpeta")
        sys.exit(1)

    print(f"\nData Quality Checker — {len(activos)} activos")
    print(f"Carpeta: {data_folder}\n")
    print(f"{'Activo':<10} {'Estado':<10} {'Velas':>8} {'Gaps%':>7} {'Cobertura':>10}  Notas")
    print("-" * 75)

    results = []
    for activo in activos:
        # Buscar CSV con nombre del activo (case-insensitive)
        candidates = list(data_folder.glob(f"{activo}*.csv")) + \
                     list(data_folder.glob(f"{activo.lower()}*.csv"))
        csv_path = candidates[0] if candidates else data_folder / f"{activo}.csv"
        r = check_activo(csv_path, activo)
        results.append(r)

        candles = r.get("total_candles", "-")
        gap_pct = f"{r.get('gap_pct', 0):.2f}%" if "gap_pct" in r else "-"
        coverage = f"{r.get('years_coverage', '-')}a"
        notes = (r["warnings"] + r["errors"])
        note_str = notes[0][:40] if notes else r.get("note", "")
        print(f"{activo:<10} {r['status']:<10} {str(candles):>8} {gap_pct:>7} {coverage:>10}  {note_str}")

    # Ollama
    ollama_text = _ollama_comment(results)

    # Guardar informe
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "timestamp": datetime.now().isoformat(),
        "data_folder": str(data_folder),
        "activos": results,
        "summary": {
            "ok": sum(1 for r in results if r["status"] == "OK"),
            "warn": sum(1 for r in results if r["status"] == "WARN"),
            "no_data": sum(1 for r in results if r["status"] == "NO_DATA"),
        }
    }
    if ollama_text:
        report["ollama_comment"] = ollama_text

    out_path = RESULTS_DIR / "data-quality-report.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nInforme guardado: {out_path}")
    ok = report["summary"]["ok"]
    warn = report["summary"]["warn"]
    no_data = report["summary"]["no_data"]
    print(f"Resumen: {ok} OK, {warn} WARN, {no_data} sin datos")

    if ollama_text:
        print(f"\nOllama: {ollama_text}")


if __name__ == "__main__":
    main()
