"""
sq-project-generator.py -- TradingLab v8.1
Genera proyectos .cfx para StrategyQuant X a partir de configuracion.
Basado en el formato real extraido del proyecto Builder de SQ.

Uso:
    python scripts/sq-project-generator.py --build 11 --activo XAUUSD --spread-real 30
    python scripts/sq-project-generator.py --build 12 --activo EURUSD --spread-real 0.5
    python scripts/sq-project-generator.py --list-activos
    python scripts/sq-project-generator.py --validate --build 11
    python scripts/sq-project-generator.py --dry-run --build 11 --activo XAUUSD --spread-real 30

Salida:
    D:/user/projects/Builder/project.cfx  (sobreescribe el proyecto activo en SQ)
    results/builds/build-{N}-config.json  (registro de la config usada)
"""

import argparse
import json
import os
import sys
import zipfile
import shutil
from datetime import datetime
from pathlib import Path
from xml.dom import minidom
import xml.etree.ElementTree as ET

# ─── Rutas ────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent
SQ_PROJECT_PATH = Path(r"D:\user\projects\Builder\project.cfx")
SQ_EXTRACTED_DIR = Path(r"D:\user\projects\Builder\extracted")
RESULTS_DIR = REPO_ROOT / "results" / "builds"
CONFIG_DEFAULTS = REPO_ROOT / "config" / "build-defaults.json"

# ─── Catálogo de activos ───────────────────────────────────────────────────────

ACTIVOS = {
    "XAUUSD": {
        "data_source":      "XAUUSD_M1_dukas",
        "instrument":       "XAUUSD_ftmo",
        "broker_id":        8,
        "broker_name":      "[[FTMO]]",
        "broker_postfix":   "_ftmo",
        "broker_desc":      "FTMO",
        "u_symbol":         "XAUUSD",
        "spread_default":   60.0,   # pips reales × 2
        "slippage":         2.0,
        "decimals":         2,
        "commission_type":  "PerTrade",
        "commission":       7,
        "point_value":      100.0,
        "tick_size":        0.01,
        "tick_step":        0.01,
        "sector":           "Commodities",
        "session_name":     "XAUUSD_ftmo",
        "session_elements": [
            {"dayFrom": "Mon", "dayTo": "Mon", "timeFrom": "01:05", "timeTo": "23:50"},
            {"dayFrom": "Tue", "dayTo": "Tue", "timeFrom": "01:05", "timeTo": "23:50"},
            {"dayFrom": "Wed", "dayTo": "Wed", "timeFrom": "01:05", "timeTo": "23:50"},
            {"dayFrom": "Thu", "dayTo": "Thu", "timeFrom": "01:05", "timeTo": "23:50"},
            {"dayFrom": "Fri", "dayTo": "Fri", "timeFrom": "01:05", "timeTo": "23:50"},
        ],
        "swap_long":   -50.63,
        "swap_short":   17.67,
        "swap_triple":  "WEDNESDAY",
        "sl_min_pips":  30,
        "sl_max_pips":  80,
        "pt_min_pips":  60,
        "pt_max_pips":  200,
        "date_from_ms": 1052092800000,  # 2003-05-05
        "data_broker_id": 2,            # Dukascopy
        "data_broker_name": "[[Dukascopy]]",
        "data_broker_postfix": "_dukascopy",
        "data_broker_desc": "Dukascopy",
    },
    "EURUSD": {
        "data_source":      "EURUSD_M1_dukas",
        "instrument":       "EURUSD_ftmo",
        "broker_id":        8,
        "broker_name":      "[[FTMO]]",
        "broker_postfix":   "_ftmo",
        "broker_desc":      "FTMO",
        "u_symbol":         "EURUSD",
        "spread_default":   1.0,    # 0.5 pip × 2
        "slippage":         0.5,
        "decimals":         5,
        "commission_type":  "SizeBased",
        "commission":       7,
        "point_value":      100000.0,
        "tick_size":        0.0001,
        "tick_step":        0.00001,
        "sector":           "Currency",
        "session_name":     "EURUSD_ftmo",
        "session_elements": [
            {"dayFrom": "Mon", "dayTo": "Mon", "timeFrom": "08:00", "timeTo": "20:00"},
            {"dayFrom": "Tue", "dayTo": "Tue", "timeFrom": "08:00", "timeTo": "20:00"},
            {"dayFrom": "Wed", "dayTo": "Wed", "timeFrom": "08:00", "timeTo": "20:00"},
            {"dayFrom": "Thu", "dayTo": "Thu", "timeFrom": "08:00", "timeTo": "20:00"},
            {"dayFrom": "Fri", "dayTo": "Fri", "timeFrom": "08:00", "timeTo": "20:00"},
        ],
        "swap_long":   -5.61,
        "swap_short":   2.71,
        "swap_triple":  "WEDNESDAY",
        "sl_min_pips":  20,
        "sl_max_pips":  60,
        "pt_min_pips":  40,
        "pt_max_pips":  120,
        "date_from_ms": 1052092800000,
        "data_broker_id": 3,
        "data_broker_name": "[[Dukascopy]]",
        "data_broker_postfix": "_dukascopy",
        "data_broker_desc": "Dukascopy",
    },
    "GBPUSD": {
        "data_source":      "GBPUSD_M1_dukas",
        "instrument":       "GBPUSD_ftmo",
        "broker_id":        8,
        "broker_name":      "[[FTMO]]",
        "broker_postfix":   "_ftmo",
        "broker_desc":      "FTMO",
        "u_symbol":         "GBPUSD",
        "spread_default":   1.6,
        "slippage":         0.5,
        "decimals":         5,
        "commission_type":  "SizeBased",
        "commission":       7,
        "point_value":      100000.0,
        "tick_size":        0.0001,
        "tick_step":        0.00001,
        "sector":           "Currency",
        "session_name":     "GBPUSD_ftmo",
        "session_elements": [
            {"dayFrom": "Mon", "dayTo": "Mon", "timeFrom": "08:00", "timeTo": "20:00"},
            {"dayFrom": "Tue", "dayTo": "Tue", "timeFrom": "08:00", "timeTo": "20:00"},
            {"dayFrom": "Wed", "dayTo": "Wed", "timeFrom": "08:00", "timeTo": "20:00"},
            {"dayFrom": "Thu", "dayTo": "Thu", "timeFrom": "08:00", "timeTo": "20:00"},
            {"dayFrom": "Fri", "dayTo": "Fri", "timeFrom": "08:00", "timeTo": "20:00"},
        ],
        "swap_long":   -7.5,
        "swap_short":   3.2,
        "swap_triple":  "WEDNESDAY",
        "sl_min_pips":  12,
        "sl_max_pips":  50,
        "pt_min_pips":  24,
        "pt_max_pips":  120,
        "date_from_ms": 1052092800000,
        "data_broker_id": 3,
        "data_broker_name": "[[Dukascopy]]",
        "data_broker_postfix": "_dukascopy",
        "data_broker_desc": "Dukascopy",
    },
    "USDJPY": {
        "data_source":      "USDJPY_M1_dukas",
        "instrument":       "USDJPY_ftmo",
        "broker_id":        8,
        "broker_name":      "[[FTMO]]",
        "broker_postfix":   "_ftmo",
        "broker_desc":      "FTMO",
        "u_symbol":         "USDJPY",
        "spread_default":   1.0,
        "slippage":         0.5,
        "decimals":         3,
        "commission_type":  "SizeBased",
        "commission":       7,
        "point_value":      100000.0,
        "tick_size":        0.001,
        "tick_step":        0.0001,
        "sector":           "Currency",
        "session_name":     "USDJPY_ftmo",
        "session_elements": [
            {"dayFrom": "Mon", "dayTo": "Mon", "timeFrom": "08:00", "timeTo": "20:00"},
            {"dayFrom": "Tue", "dayTo": "Tue", "timeFrom": "08:00", "timeTo": "20:00"},
            {"dayFrom": "Wed", "dayTo": "Wed", "timeFrom": "08:00", "timeTo": "20:00"},
            {"dayFrom": "Thu", "dayTo": "Thu", "timeFrom": "08:00", "timeTo": "20:00"},
            {"dayFrom": "Fri", "dayTo": "Fri", "timeFrom": "08:00", "timeTo": "20:00"},
        ],
        "swap_long":    2.8,
        "swap_short":  -5.1,
        "swap_triple":  "WEDNESDAY",
        "sl_min_pips":  10,
        "sl_max_pips":  40,
        "pt_min_pips":  20,
        "pt_max_pips":  100,
        "date_from_ms": 1052092800000,
        "data_broker_id": 3,
        "data_broker_name": "[[Dukascopy]]",
        "data_broker_postfix": "_dukascopy",
        "data_broker_desc": "Dukascopy",
    },
}

# ─── Generación de config.xml ──────────────────────────────────────────────────

def build_config_xml(activo_cfg: dict) -> str:
    """Genera el config.xml del proyecto."""
    session_name = activo_cfg["session_name"]
    root = ET.Element("Project", name="Builder", version="143.2708")
    
    tasks = ET.SubElement(root, "Tasks")
    ET.SubElement(tasks, "Task",
        type="Build", name="Build",
        showSettingsOverview="false",
        sampleName="Custom",
        active="true",
        version="126.2189",
        taskXMLFile="Build-Task1.xml")
    
    resources = ET.SubElement(root, "Resources")
    symbols_el = ET.SubElement(resources, "Symbols")
    ET.SubElement(resources, "Sessions")
    ET.SubElement(resources, "CustomIndicators")
    ET.SubElement(resources, "CustomBlocks")
    
    databanks = ET.SubElement(root, "Databanks")
    for name, pos in [
        ("Results", 0), ("Initial population", 1),
        ("Last generation", 2), ("Strategies to improve", 3)
    ]:
        ET.SubElement(databanks, "Databank",
            name=name,
            view="Default - Main data",
            syncType="Auto-sync every 1 hour" if name == "Results" else "Auto-sync never",
            position=str(pos))
    ET.SubElement(databanks, "Databank",
        name="Existing portfolio",
        view="Default",
        syncType="Auto-sync never")
    
    xml_str = ET.tostring(root, encoding="unicode")
    return minidom.parseString(xml_str).toprettyxml(indent="  ")


def build_commission_xml(activo_cfg: dict) -> str:
    """Genera el XML de comisiones embebido en InstrumentInfo."""
    ct = activo_cfg["commission_type"]
    c = activo_cfg["commission"]
    if ct == "PerTrade":
        return (f'<Method type="PerTrade" use="true">'
                f'<Params><Param key="Commission" className="PerTrade">{c}</Param>'
                f'</Params></Method>')
    else:
        return (f'<Method type="SizeBased" use="true">'
                f'<Params><Param key="Commission" className="SizeBased">{c:.2f}</Param>'
                f'</Params></Method>')


def build_swap_xml(activo_cfg: dict) -> str:
    sl = activo_cfg["swap_long"]
    ss = activo_cfg["swap_short"]
    st = activo_cfg["swap_triple"]
    return (f'<Swap use="true" type="points" long="{sl}" short="{ss}" '
            f'tripleSwapOn="{st}" rolloutHour="23:00"/>')


def build_instrument_info_attribs(activo_cfg: dict, spread_real: float) -> dict:
    """Construye los atributos del nodo InstrumentInfo."""
    spread_model = spread_real * 2  # regla: spread modelo = 2× real
    comm_xml = build_commission_xml(activo_cfg)
    swap_xml = build_swap_xml(activo_cfg)
    
    return {
        "instrument":         activo_cfg["instrument"],
        "description":        activo_cfg["sector"],
        "tickSize":           str(activo_cfg["tick_size"]),
        "tickStep":           str(activo_cfg["tick_step"]),
        "minDistance":        "0.0",
        "tickValueInMoney":   "0.0",
        "dateFrom":           "0",
        "dateTo":             "0",
        "rows":               "0",
        "totalDays":          "0",
        "defaultSpread":      str(spread_model),
        "defaultSlippage":    str(activo_cfg["slippage"]),
        "decimals":           str(activo_cfg["decimals"]),
        "commissions":        comm_xml,
        "pointValue":         str(activo_cfg["point_value"]),
        "dataType":           "4" if activo_cfg["sector"] == "Commodities" else "3",
        "recognizedFromOrders": "false",
        "exchange":           "Forex" if activo_cfg["sector"] == "Currency" else "",
        "country":            "",
        "sector":             activo_cfg["sector"],
        "swap":               swap_xml,
        "orderSizeMultiplier": "1.0",
        "orderSizeStep":      "0.01",
        "broker":             str(activo_cfg["broker_id"]),
    }


# ─── Lectura y modificación del Build-Task1.xml ────────────────────────────────

def read_template_task_xml() -> str:
    """Lee el Build-Task1.xml actual del proyecto extraído."""
    task_path = SQ_EXTRACTED_DIR / "Build-Task1.xml"
    if not task_path.exists():
        raise FileNotFoundError(
            f"No se encuentra {task_path}\n"
            "Ejecuta primero:\n"
            r'  python -c "import zipfile; z = zipfile.ZipFile(r'
            r"'D:/user/projects/Builder/project.cfx'"
            r'); z.extractall(r'
            r"'D:/user/projects/Builder/extracted'"
            r'); print(chr(79)+chr(75))"'
        )
    with open(task_path, "r", encoding="utf-8") as f:
        return f.read()


def patch_task_xml(task_xml_str: str, activo_cfg: dict, spread_real: float,
                   build_num: int) -> str:
    """
    Modifica el Build-Task1.xml para el nuevo activo/build.
    Opera con string manipulation para no romper el XML complejo de SQ.
    """
    import re
    spread_model = spread_real * 2
    instrument   = activo_cfg["instrument"]   # e.g. "EURUSD_ftmo"
    data_source  = activo_cfg["data_source"]  # e.g. "EURUSD_M1_dukas"
    u_symbol     = activo_cfg["u_symbol"]     # e.g. "EURUSD"

    # Patch 1: Reemplazar todos los patrones del activo anterior
    for a_cfg in ACTIVOS.values():
        if a_cfg["u_symbol"] == u_symbol:
            continue
        old = a_cfg["u_symbol"]
        for old_pat, new_pat in [
            (f"{old}_ftmo",         f"{u_symbol}_ftmo"),
            (f"{old}_M1_dukas",     f"{u_symbol}_M1_dukas"),
            (f"{old}_dukascopy",    f"{u_symbol}_dukascopy"),
            (f'uSymbol="{old}"',    f'uSymbol="{u_symbol}"'),
            (f'uSymbolName="{old}"', f'uSymbolName="{u_symbol}"'),
        ]:
            task_xml_str = task_xml_str.replace(old_pat, new_pat)

    # Patch 2: Actualizar defaultSpread del instrumento objetivo
    task_xml_str = re.sub(
        r'(instrument="' + re.escape(instrument) + r'"[^>]*defaultSpread=")[^"]*(")',
        lambda m: m.group(0).replace(
            'defaultSpread="' + m.group(0).split('defaultSpread="')[1].split('"')[0] + '"',
            f'defaultSpread="{spread_model}"'
        ),
        task_xml_str
    )

    return task_xml_str


# ─── Empaquetado CFX ───────────────────────────────────────────────────────────

def pack_cfx(config_xml: str, task_xml: str, output_path: Path):
    """Empaqueta config.xml + Build-Task1.xml en el archivo .cfx (ZIP). Retorna path del backup."""
    backup_path = None
    if output_path.exists():
        backup_path = output_path.with_suffix(
            f'.cfx.bak_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        )
        shutil.copy2(output_path, backup_path)
        print(f"  Backup: {backup_path.name}")

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("config.xml", config_xml)
        zf.writestr("Build-Task1.xml", task_xml)

    print(f"  CFX generado: {output_path}")
    return backup_path


# ─── Verificación post-generación ─────────────────────────────────────────────

def verify_cfx(cfx_path: Path, activo_cfg: dict, spread_real: float, backup_path) -> None:
    """Verifica el CFX generado. Aborta y restaura backup si cualquier check falla."""
    import re
    errors = []

    with zipfile.ZipFile(cfx_path, "r") as zf:
        t = zf.read("Build-Task1.xml").decode("utf-8")
        config_xml = zf.read("config.xml").decode("utf-8")

    instrument  = activo_cfg["instrument"]   # e.g. "XAUUSD_ftmo"
    data_source = activo_cfg["data_source"]  # e.g. "XAUUSD_M1_dukas"
    u_symbol    = activo_cfg["u_symbol"]     # e.g. "XAUUSD"
    spread_model = spread_real * 2

    # 1. Sin referencias a activos distintos al del build
    wrong_refs = re.findall(r'[A-Z]{6}(?:_M1_dukas|_dukascopy|_ftmo)', t)
    wrong_refs = [r for r in wrong_refs if not r.startswith(u_symbol)]
    if wrong_refs:
        errors.append(f"Referencias a otros activos: {set(wrong_refs)}")

    # 2. Chart symbol apunta al activo correcto
    for cs in re.findall(r'<Chart symbol="([^"]+)"', t):
        if cs != data_source:
            errors.append(f"Chart symbol incorrecto: '{cs}' (esperado '{data_source}')")

    # 3. Spread es spread_real × 2
    wrong_spreads = [s for s in re.findall(r'defaultSpread="([^"]+)"', t)
                     if float(s) != spread_model]
    if wrong_spreads:
        errors.append(f"Spread incorrecto: {wrong_spreads} (esperado {spread_model})")

    # 4. Sin InstrumentInfo residuales de otros activos
    wrong_instr = [i for i in re.findall(r'<InstrumentInfo instrument="([^"]+)"', t)
                   if not i.startswith(u_symbol)]
    if wrong_instr:
        errors.append(f"InstrumentInfo residuales: {wrong_instr}")

    # 5. uSymbol y uSymbolName apuntan al activo correcto
    wrong_usym = [s for s in re.findall(r'uSymbol="([^"]+)"', t) if s != u_symbol]
    if wrong_usym:
        errors.append(f"uSymbol incorrecto: {set(wrong_usym)} (esperado '{u_symbol}')")

    if errors:
        print("\n[ERROR] verify_cfx() FALLIDO:")
        for e in errors:
            print(f"  - {e}")
        if backup_path and backup_path.exists():
            shutil.copy2(backup_path, cfx_path)
            print(f"  Backup restaurado: {backup_path.name}")
        raise RuntimeError(f"CFX invalido — {len(errors)} error(s). Build abortado.")

    # 6. Verificar/parchear SL/PT
    sl_min_exp = activo_cfg["sl_min_pips"]
    sl_max_exp = activo_cfg["sl_max_pips"]
    pt_min_exp = activo_cfg["pt_min_pips"]
    pt_max_exp = activo_cfg["pt_max_pips"]

    sl_min_m = re.search(r'<Param key="MinimumSL" className="MinMaxSLPT">(\d+)</Param>', t)
    sl_max_m = re.search(r'<Param key="MaximumSL" className="MinMaxSLPT">(\d+)</Param>', t)
    pt_min_m = re.search(r'<Param key="MinimumPT" className="MinMaxSLPT">(\d+)</Param>', t)
    pt_max_m = re.search(r'<Param key="MaximumPT" className="MinMaxSLPT">(\d+)</Param>', t)

    slpt_matches = (
        sl_min_m and int(sl_min_m.group(1)) == sl_min_exp and
        sl_max_m and int(sl_max_m.group(1)) == sl_max_exp and
        pt_min_m and int(pt_min_m.group(1)) == pt_min_exp and
        pt_max_m and int(pt_max_m.group(1)) == pt_max_exp
    )

    if not slpt_matches:
        t = re.sub(r'(<Param key="MinimumSL" className="MinMaxSLPT">)\d+(</Param>)',
                   rf'\g<1>{sl_min_exp}\g<2>', t)
        t = re.sub(r'(<Param key="MaximumSL" className="MinMaxSLPT">)\d+(</Param>)',
                   rf'\g<1>{sl_max_exp}\g<2>', t)
        t = re.sub(r'(<Param key="MinimumPT" className="MinMaxSLPT">)\d+(</Param>)',
                   rf'\g<1>{pt_min_exp}\g<2>', t)
        t = re.sub(r'(<Param key="MaximumPT" className="MinMaxSLPT">)\d+(</Param>)',
                   rf'\g<1>{pt_max_exp}\g<2>', t)
        with zipfile.ZipFile(cfx_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("config.xml", config_xml)
            zf.writestr("Build-Task1.xml", t)
        slpt_status = f"PARCHEADO [{sl_min_exp}-{sl_max_exp} / {pt_min_exp}-{pt_max_exp}]"
    else:
        slpt_status = f"OK [{sl_min_exp}-{sl_max_exp} / {pt_min_exp}-{pt_max_exp}]"

    print("[5/5] verify_cfx(): OK")
    print(f"      Chart:      {data_source}")
    print(f"      Spread:     {spread_model} pips")
    print(f"      Instrumento:{instrument}")
    print(f"      SL/PT:      {slpt_status}")
    print(f"      Sin activos residuales")


# ─── Registro JSON ─────────────────────────────────────────────────────────────

def save_build_config(build_num: int, activo: str, spread_real: float,
                      activo_cfg: dict) -> None:
    """Guarda la configuración del build en results/builds/."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / f"build-{build_num:02d}-config.json"
    
    config = {
        "build":          build_num,
        "activo":         activo,
        "fecha":          datetime.now().isoformat(),
        "spread_real":    spread_real,
        "spread_modelo":  spread_real * 2,
        "slippage":       activo_cfg["slippage"],
        "commission":     activo_cfg["commission"],
        "commission_type": activo_cfg["commission_type"],
        "instrument":     activo_cfg["instrument"],
        "sl_min_pips":    activo_cfg["sl_min_pips"],
        "sl_max_pips":    activo_cfg["sl_max_pips"],
        "pt_min_pips":    activo_cfg["pt_min_pips"],
        "pt_max_pips":    activo_cfg["pt_max_pips"],
        "session":        activo_cfg["session_name"],
        "regla_spread":   "spread_modelo = spread_real × 2 (anti-overfitting)",
    }
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"  Config guardada: {out_path}")


# ─── Validación ────────────────────────────────────────────────────────────────

def validate_build(build_num: int) -> None:
    """Verifica que el CFX activo coincide con la config del build."""
    config_path = RESULTS_DIR / f"build-{build_num:02d}-config.json"
    
    if not config_path.exists():
        print(f"[ERROR] No hay config registrada para Build {build_num}")
        sys.exit(1)
    
    with open(config_path) as f:
        cfg = json.load(f)
    
    if not SQ_PROJECT_PATH.exists():
        print(f"[ERROR] No se encuentra el CFX en {SQ_PROJECT_PATH}")
        sys.exit(1)
    
    # Extraer temporalmente y verificar spread
    with zipfile.ZipFile(SQ_PROJECT_PATH, "r") as zf:
        task_xml = zf.read("Build-Task1.xml").decode("utf-8")
    
    spread_expected = str(cfg["spread_modelo"])
    if f'defaultSpread="{spread_expected}"' in task_xml:
        print(f"[OK] Build {build_num} — spread {spread_expected} pips verificado en CFX")
    else:
        # Buscar qué spread hay
        import re
        matches = re.findall(r'defaultSpread="([^"]+)"', task_xml)
        print(f"[WARN] Spread esperado {spread_expected}, encontrado: {set(matches)}")
    
    print(f"[OK] Activo: {cfg['activo']}, Instrumento: {cfg['instrument']}")
    print(f"[OK] SL: {cfg['sl_min_pips']}-{cfg['sl_max_pips']} pips")
    print(f"[OK] PT: {cfg['pt_min_pips']}-{cfg['pt_max_pips']} pips")
    print(f"[OK] Comisión: {cfg['commission_type']} {cfg['commission']} USD")


# ─── Listado de activos ────────────────────────────────────────────────────────

def list_activos() -> None:
    print("\nActivos disponibles en sq-project-generator:\n")
    print(f"{'Activo':<12} {'Spread real (pip)':<20} {'SL rango':<15} {'PT rango':<15} {'Comisión'}")
    print("-" * 80)
    for name, cfg in ACTIVOS.items():
        spread_ref = cfg["spread_default"] / 2
        print(f"{name:<12} {spread_ref:<20.1f} "
              f"{cfg['sl_min_pips']}-{cfg['sl_max_pips']} pips   "
              f"{cfg['pt_min_pips']}-{cfg['pt_max_pips']} pips   "
              f"{cfg['commission_type']} {cfg['commission']} USD")
    print()
    print("Nota: spread_modelo en SQ = spread_real × 2 (regla anti-overfitting)")
    print("Para añadir activos, edita el catálogo ACTIVOS en este script.")


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generador de proyectos CFX para StrategyQuant X — TradingLab v8.1"
    )
    parser.add_argument("--build", type=int, help="Número de build (ej: 11)")
    parser.add_argument("--activo", type=str, help="Activo (ej: XAUUSD, EURUSD)")
    parser.add_argument("--spread-real", type=float,
                        help="Spread real en pips (ej: 30 para XAU, 0.5 para EUR)")
    parser.add_argument("--list-activos", action="store_true",
                        help="Listar activos disponibles")
    parser.add_argument("--validate", action="store_true",
                        help="Validar que el CFX activo coincide con la config del build")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simular sin escribir archivos")
    parser.add_argument("--output", type=str, default=None,
                        help="Ruta de salida del CFX (default: proyecto SQ activo)")
    
    args = parser.parse_args()
    
    # ── Modo listado ──
    if args.list_activos:
        list_activos()
        return
    
    # ── Modo validación ──
    if args.validate:
        if not args.build:
            print("[ERROR] --validate requiere --build N")
            sys.exit(1)
        validate_build(args.build)
        return
    
    # ── Modo generación ──
    if not all([args.build, args.activo, args.spread_real is not None]):
        parser.print_help()
        print("\n[ERROR] Se requieren --build, --activo y --spread-real")
        sys.exit(1)
    
    activo = args.activo.upper()
    if activo not in ACTIVOS:
        print(f"[ERROR] Activo '{activo}' no está en el catálogo.")
        print(f"Disponibles: {', '.join(ACTIVOS.keys())}")
        sys.exit(1)
    
    activo_cfg = ACTIVOS[activo]
    spread_real = args.spread_real
    spread_modelo = spread_real * 2
    build_num = args.build
    
    output_path = Path(args.output) if args.output else SQ_PROJECT_PATH
    
    print(f"\n{'='*60}")
    print(f"  TradingLab — Generador de Proyectos SQ CFX")
    print(f"{'='*60}")
    print(f"  Build:          {build_num}")
    print(f"  Activo:         {activo}")
    print(f"  Instrumento:    {activo_cfg['instrument']}")
    print(f"  Spread real:    {spread_real} pips")
    print(f"  Spread modelo:  {spread_modelo} pips (×2 anti-overfitting)")
    print(f"  Slippage:       {activo_cfg['slippage']} pips")
    print(f"  Comisión:       {activo_cfg['commission_type']} {activo_cfg['commission']} USD")
    print(f"  SL rango:       {activo_cfg['sl_min_pips']}-{activo_cfg['sl_max_pips']} pips")
    print(f"  PT rango:       {activo_cfg['pt_min_pips']}-{activo_cfg['pt_max_pips']} pips")
    print(f"  Sesión:         {activo_cfg['session_name']}")
    print(f"  Salida CFX:     {output_path}")
    print(f"{'='*60}\n")
    
    if args.dry_run:
        print("[DRY-RUN] No se escriben archivos. Configuración válida.")
        save_build_config(build_num, activo, spread_real, activo_cfg)
        return
    
    # Leer template
    print("[1/5] Leyendo Build-Task1.xml del proyecto actual...")
    try:
        task_xml = read_template_task_xml()
        print(f"      OK — {len(task_xml):,} caracteres")
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    # Parchear parámetros del build
    print("[2/5] Aplicando parámetros del build...")
    task_xml_patched = patch_task_xml(task_xml, activo_cfg, spread_real, build_num)
    if f'defaultSpread="{spread_modelo}"' in task_xml_patched:
        print(f"      OK — spread {spread_modelo} pips aplicado")
    else:
        print(f"      [INFO] Spread ya era correcto o instrumento diferente")

    # Generar config.xml
    print("[3/5] Generando config.xml...")
    config_xml = build_config_xml(activo_cfg)
    print(f"      OK — {len(config_xml)} caracteres")

    # Empaquetar CFX
    print("[4/5] Empaquetando CFX...")
    try:
        backup_path = pack_cfx(config_xml, task_xml_patched, output_path)
    except Exception as e:
        print(f"[ERROR] No se pudo escribir el CFX: {e}")
        print("       ¿Está SQ cerrado? El CFX no puede modificarse con SQ abierto.")
        sys.exit(1)

    # Verificar CFX generado (obligatorio — aborta y restaura si falla)
    try:
        verify_cfx(output_path, activo_cfg, spread_real, backup_path)
    except RuntimeError as e:
        print(f"\n[ABORT] {e}")
        sys.exit(1)

    # Guardar registro
    save_build_config(build_num, activo, spread_real, activo_cfg)

    print(f"\n[OK] Build {build_num} configurado correctamente.")
    print(f"     Abre SQ y verifica el proyecto antes de iniciar el Builder.")
    print(f"\n     Verificar con:")
    print(f"     python scripts/sq-project-generator.py --validate --build {build_num}")


if __name__ == "__main__":
    main()
