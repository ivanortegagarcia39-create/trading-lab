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
import importlib.util
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

CFX_DEFAULT = Path(r"D:\user\projects\Builder\project.cfx")

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


def _read_cfx_task_xml(cfx_path: Path):
    p = cfx_path or CFX_DEFAULT
    if not p.exists():
        return None, f"CFX no encontrado: {p}"
    try:
        with zipfile.ZipFile(p, "r") as zf:
            return zf.read("Build-Task1.xml").decode("utf-8", errors="ignore"), None
    except Exception as e:
        return None, f"Error leyendo CFX: {e}"


def check_is_period(cfx_path):
    xml, err = _read_cfx_task_xml(cfx_path)
    if xml is None:
        return "WARN", err
    m = re.search(r'<EvoInSamplePeriod ratio="(\d+)"', xml)
    if not m:
        return "WARN", "EvoInSamplePeriod no encontrado en CFX — verificar manualmente"
    ratio = int(m.group(1))
    if ratio < 100:
        return "FAIL", f"IS period = {ratio}% — debe ser 100%. Corregir en SQ antes de lanzar."
    return "PASS", f"IS period = {ratio}% (OK)"


def check_slpt_ratio(cfx_path):
    xml, err = _read_cfx_task_xml(cfx_path)
    if xml is None:
        return "WARN", err
    sl_m = re.search(r'<Param key="MinimumSL" className="MinMaxSLPT">(\d+)</Param>', xml)
    pt_m = re.search(r'<Param key="MinimumPT" className="MinMaxSLPT">(\d+)</Param>', xml)
    if not sl_m or not pt_m:
        return "WARN", "MinimumSL/MinimumPT no encontrados en CFX — verificar manualmente"
    sl_min = int(sl_m.group(1))
    pt_min = int(pt_m.group(1))
    ratio = pt_min / sl_min if sl_min > 0 else 0.0
    if ratio < 2.0:
        return "FAIL", f"PT_min ({pt_min}) / SL_min ({sl_min}) = {ratio:.2f} — ratio minimo 2:1 requerido"
    return "PASS", f"PT_min {pt_min} / SL_min {sl_min} = ratio {ratio:.1f}:1 (OK)"


def check_asset_viability(activo, results_dir):
    avr = Path(results_dir) / "asset-viability-ranking.json"
    if not avr.exists():
        return "WARN", f"asset-viability-ranking.json no encontrado en {results_dir} — verificar manualmente"
    try:
        data = json.loads(avr.read_text(encoding="utf-8"))
        for entry in data.get("ranking", []):
            if entry.get("activo", "").upper() == activo.upper():
                estado = entry.get("estado", "")
                if "DESCARTADO" in estado.upper():
                    return "FAIL", f"{activo} estado: {estado} — activo descartado, no lanzar build"
                return "PASS", f"{activo} estado: {estado} (OK)"
        return "WARN", f"{activo} no encontrado en asset-viability-ranking.json — verificar manualmente"
    except Exception as e:
        return "WARN", f"Error leyendo asset-viability-ranking.json: {e}"


def check_slpt_cfx(cfx_path, activo):
    sqpg = Path(__file__).parent / "sq-project-generator.py"
    if not sqpg.exists():
        return "WARN", "sq-project-generator.py no encontrado — no se puede verificar catalogo SL/PT"
    try:
        spec = importlib.util.spec_from_file_location("sqpg", str(sqpg))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        catalog = getattr(mod, "ACTIVOS", None)
        if catalog is None:
            return "WARN", "ACTIVOS no encontrado en sq-project-generator.py"
        cfg = catalog.get(activo.upper())
        if cfg is None:
            return "WARN", f"{activo} no esta en el catalogo de sq-project-generator.py"
    except Exception as e:
        return "WARN", f"Error cargando catalogo SL/PT: {e}"

    xml, err = _read_cfx_task_xml(cfx_path)
    if xml is None:
        return "WARN", err

    sl_min_m = re.search(r'<Param key="MinimumSL" className="MinMaxSLPT">(\d+)</Param>', xml)
    sl_max_m = re.search(r'<Param key="MaximumSL" className="MinMaxSLPT">(\d+)</Param>', xml)
    pt_min_m = re.search(r'<Param key="MinimumPT" className="MinMaxSLPT">(\d+)</Param>', xml)
    pt_max_m = re.search(r'<Param key="MaximumPT" className="MinMaxSLPT">(\d+)</Param>', xml)

    if not all([sl_min_m, sl_max_m, pt_min_m, pt_max_m]):
        return "WARN", "MinimumSL/MaximumSL/MinimumPT/MaximumPT no encontrados en CFX"

    sl_min, sl_max = int(sl_min_m.group(1)), int(sl_max_m.group(1))
    pt_min, pt_max = int(pt_min_m.group(1)), int(pt_max_m.group(1))
    exp = (cfg["sl_min_pips"], cfg["sl_max_pips"], cfg["pt_min_pips"], cfg["pt_max_pips"])

    mismatches = []
    if sl_min != exp[0]: mismatches.append(f"MinimumSL {sl_min} != {exp[0]}")
    if sl_max != exp[1]: mismatches.append(f"MaximumSL {sl_max} != {exp[1]}")
    if pt_min != exp[2]: mismatches.append(f"MinimumPT {pt_min} != {exp[2]}")
    if pt_max != exp[3]: mismatches.append(f"MaximumPT {pt_max} != {exp[3]}")

    if mismatches:
        return "FAIL", "CFX SL/PT no coincide con catalogo: " + ", ".join(mismatches)
    return "PASS", f"SL [{sl_min}-{sl_max}] PT [{pt_min}-{pt_max}] coincide con catalogo (OK)"


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
    parser.add_argument("--cfx-path",    default=str(CFX_DEFAULT), help="Ruta al .cfx del proyecto Builder")
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

    cfx_path = Path(args.cfx_path)

    add("Spread 2x configurado",    *check_spread(args.activo, args.spread))
    add("OOS date reciente",        *check_oos_date(args.oos_end))
    add("Datos M1 disponibles",     *check_data(args.data_path, args.activo))
    add("Sin pipeline.lock activo", *check_pipeline_lock(args.results_dir))
    add("IS period 100%",           *check_is_period(cfx_path))
    add("Ratio PT/SL >= 2:1",       *check_slpt_ratio(cfx_path))
    add("Activo no descartado",     *check_asset_viability(args.activo, args.results_dir))
    add("SL/PT coincide catalogo",  *check_slpt_cfx(cfx_path, args.activo))

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
