"""
strategy-fingerprint.py
Genera un hash unico de la logica de una estrategia SQ (.sqx)
para detectar duplicados entre el databank y el portfolio activo.

Una estrategia duplicada es aquella con similitud > 80% en su
logica normalizada. Entre duplicados, conservar solo la de mayor IPR.

Uso:
    # Generar fingerprint de un archivo
    python strategy-fingerprint.py fingerprint --file ruta/estrategia.sqx

    # Comparar dos estrategias
    python strategy-fingerprint.py compare --file1 a.sqx --file2 b.sqx

    # Buscar duplicados en una carpeta
    python strategy-fingerprint.py find-duplicates --folder results/eval-gate/

    # Formato libre: los archivos .sqx son XML — este script
    # tambien puede procesar archivos CSV exportados con columna "Logic"

Formato del fingerprint:
    SHA-256 de la logica normalizada (indicadores + operadores + orden)

Similitud (0.0 a 1.0):
    1.0 = logica identica
    0.8+ = probable duplicado — conservar mayor IPR
    < 0.8 = estrategias distintas
"""

import argparse
import csv
import hashlib
import json
import os
import sys
import xml.etree.ElementTree as ET
from collections import Counter


# ─── Extraccion de logica desde .sqx (XML) ────────────────────────────────────

def parse_sqx_file(filepath: str) -> dict:
    """
    Extrae los componentes de logica de un archivo .sqx de SQ.
    Devuelve un diccionario con los componentes normalizados.
    """
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except ET.ParseError as e:
        raise ValueError(f"Error parseando XML en {filepath}: {e}")

    components = {
        "indicators": [],
        "operators": [],
        "entry_conditions": [],
        "exit_conditions": [],
        "direction": "",
        "sl_type": "",
        "tp_type": "",
    }

    # Extraer indicadores (buscar elementos con atributo "type" o "name")
    for elem in root.iter():
        tag = elem.tag.lower()
        attribs = {k.lower(): v.lower() for k, v in elem.attrib.items()}

        if "indicator" in tag or attribs.get("type", "") in (
            "ema", "sma", "rsi", "macd", "atr", "adx", "cci",
            "stochastic", "bollinger", "dema", "hma", "aroon",
            "momentum", "roc", "demarker", "keltner", "donchian",
            "williamsr", "sar", "highest", "lowest",
        ):
            name = attribs.get("name") or attribs.get("type") or tag
            period = attribs.get("period", "")
            components["indicators"].append(f"{name}:{period}")

        if "operator" in tag or attribs.get("operator"):
            op = attribs.get("operator") or elem.text or ""
            components["operators"].append(op.strip().lower())

        if "entry" in tag and "condition" in tag:
            text = (elem.text or "").strip()
            if text:
                components["entry_conditions"].append(text)

        if "exit" in tag and "condition" in tag:
            text = (elem.text or "").strip()
            if text:
                components["exit_conditions"].append(text)

        if tag in ("direction", "tradedirection"):
            components["direction"] = (elem.text or "").strip().lower()

        if "stoploss" in tag or tag == "sl":
            components["sl_type"] = attribs.get("type", "atr")

        if "takeprofit" in tag or tag == "tp":
            components["tp_type"] = attribs.get("type", "atr")

    return components


def parse_csv_logic(filepath: str) -> dict:
    """
    Extrae logica de un CSV exportado por SQ que tenga columna 'Logic'
    o columnas de indicadores separadas.
    Fallback cuando el archivo .sqx no esta disponible.
    """
    components = {
        "indicators": [],
        "operators": [],
        "entry_conditions": [],
        "exit_conditions": [],
        "direction": "",
        "sl_type": "atr",
        "tp_type": "atr",
    }

    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        headers = reader.fieldnames or []
        norm_headers = {h.strip().lower(): h for h in headers}

        for row in reader:
            # Buscar columna Logic o Description
            for col_key in ("logic", "description", "strategy logic"):
                if col_key in norm_headers:
                    logic_text = row.get(norm_headers[col_key], "").strip()
                    if logic_text:
                        # Tokenizar la logica textual
                        tokens = logic_text.lower().split()
                        known_indicators = {
                            "ema", "sma", "rsi", "macd", "atr", "adx", "cci",
                            "stochastic", "bollinger", "dema", "hma", "aroon",
                            "momentum", "roc", "demarker", "keltner", "donchian",
                            "williamsr", "sar", "highest", "lowest",
                        }
                        known_operators = {
                            "crosses", "above", "below", "greater", "less",
                            "rising", "falling", "equals",
                        }
                        for token in tokens:
                            if token in known_indicators:
                                components["indicators"].append(token)
                            if token in known_operators:
                                components["operators"].append(token)
                    break
            break  # Solo primera fila para fingerprint de archivo

    return components


# ─── Normalizacion y hash ─────────────────────────────────────────────────────

def normalize_components(components: dict) -> str:
    """
    Normaliza los componentes a una representacion canonica.
    El orden de los indicadores no importa (set) pero los operadores
    y condiciones se ordenan para consistencia.
    """
    indicators_sorted = sorted(set(components.get("indicators", [])))
    operators_sorted = sorted(set(components.get("operators", [])))
    entry_sorted = sorted(components.get("entry_conditions", []))
    exit_sorted = sorted(components.get("exit_conditions", []))
    direction = components.get("direction", "").lower()
    sl_type = components.get("sl_type", "").lower()
    tp_type = components.get("tp_type", "").lower()

    canonical = (
        f"IND:{','.join(indicators_sorted)}|"
        f"OPS:{','.join(operators_sorted)}|"
        f"ENTRY:{','.join(entry_sorted)}|"
        f"EXIT:{','.join(exit_sorted)}|"
        f"DIR:{direction}|SL:{sl_type}|TP:{tp_type}"
    )
    return canonical


def generate_fingerprint(filepath: str) -> str:
    """
    Genera el fingerprint SHA-256 de la logica normalizada de una estrategia.

    Args:
        filepath: Ruta al archivo .sqx o .csv exportado de SQ

    Returns:
        String hexadecimal SHA-256 (64 caracteres)
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".sqx":
        components = parse_sqx_file(filepath)
    elif ext in (".csv", ".txt"):
        components = parse_csv_logic(filepath)
    else:
        raise ValueError(f"Formato no soportado: {ext}. Usar .sqx o .csv")

    canonical = normalize_components(components)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ─── Similitud entre dos fingerprints ─────────────────────────────────────────

def component_similarity(fp1_components: dict, fp2_components: dict) -> float:
    """
    Calcula similitud entre 0.0 y 1.0 basada en los componentes.
    No en el hash final (que es binario) sino en los componentes individuales.
    Usa coeficiente de Jaccard sobre el conjunto de indicadores + operadores.
    """
    def to_set(comp: dict) -> set:
        items = set()
        items.update(comp.get("indicators", []))
        items.update(comp.get("operators", []))
        items.update(comp.get("entry_conditions", []))
        return items

    s1 = to_set(fp1_components)
    s2 = to_set(fp2_components)

    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0

    intersection = len(s1 & s2)
    union = len(s1 | s2)
    return intersection / union


def compare_strategies(file1: str, file2: str) -> float:
    """
    Compara dos estrategias y devuelve similitud (0.0 a 1.0).

    Args:
        file1: Ruta al primer archivo .sqx o .csv
        file2: Ruta al segundo archivo .sqx o .csv

    Returns:
        Similitud entre 0.0 (completamente diferentes) y 1.0 (identicas)
    """
    ext1 = os.path.splitext(file1)[1].lower()
    ext2 = os.path.splitext(file2)[1].lower()

    loader = lambda f, e: (
        parse_sqx_file(f) if e == ".sqx" else parse_csv_logic(f)
    )

    comp1 = loader(file1, ext1)
    comp2 = loader(file2, ext2)

    return component_similarity(comp1, comp2)


# ─── Deteccion de duplicados en carpeta ───────────────────────────────────────

def find_duplicates(folder: str, threshold: float = 0.80) -> list[dict]:
    """
    Encuentra pares de estrategias duplicadas en una carpeta.

    Args:
        folder:    Carpeta con archivos .sqx o .csv
        threshold: Umbral de similitud para considerar duplicado (default: 0.80)

    Returns:
        Lista de dicts con pares duplicados:
        [{"file1": ..., "file2": ..., "similitud": ..., "accion": ...}, ...]
    """
    # Recopilar archivos
    files = []
    for fname in os.listdir(folder):
        if fname.lower().endswith((".sqx", ".csv")):
            files.append(os.path.join(folder, fname))

    if len(files) < 2:
        return []

    # Cargar todos los componentes
    file_components = {}
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        try:
            if ext == ".sqx":
                file_components[f] = parse_sqx_file(f)
            else:
                file_components[f] = parse_csv_logic(f)
        except Exception as e:
            print(f"  WARNING: No se pudo parsear {f}: {e}", file=sys.stderr)

    parsed_files = list(file_components.keys())

    # Comparar todos contra todos (O(n^2) — asumible para < 1000 estrategias)
    duplicates = []
    for i in range(len(parsed_files)):
        for j in range(i + 1, len(parsed_files)):
            f1, f2 = parsed_files[i], parsed_files[j]
            sim = component_similarity(file_components[f1], file_components[f2])
            if sim >= threshold:
                duplicates.append({
                    "file1": f1,
                    "file2": f2,
                    "similitud": round(sim, 4),
                    "accion": "conservar_mayor_IPR",
                })

    # Ordenar por similitud descendente
    duplicates.sort(key=lambda x: -x["similitud"])
    return duplicates


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Fingerprint y deteccion de duplicados de estrategias SQ."
    )
    subparsers = parser.add_subparsers(dest="command")

    # fingerprint
    fp_p = subparsers.add_parser("fingerprint", help="Generar fingerprint de un archivo")
    fp_p.add_argument("--file", required=True)

    # compare
    cmp_p = subparsers.add_parser("compare", help="Comparar dos estrategias")
    cmp_p.add_argument("--file1", required=True)
    cmp_p.add_argument("--file2", required=True)

    # find-duplicates
    dup_p = subparsers.add_parser("find-duplicates", help="Buscar duplicados en carpeta")
    dup_p.add_argument("--folder", required=True)
    dup_p.add_argument("--threshold", type=float, default=0.80)
    dup_p.add_argument("--output-json", default=None)

    args = parser.parse_args()

    if args.command == "fingerprint":
        fp = generate_fingerprint(args.file)
        print(f"Fingerprint: {fp}")
        print(f"Archivo: {args.file}")

    elif args.command == "compare":
        sim = compare_strategies(args.file1, args.file2)
        print(f"Similitud: {sim:.2%}")
        if sim >= 0.80:
            print("DUPLICADO — conservar la de mayor IPR")
        elif sim >= 0.60:
            print("SIMILAR — revisar manualmente")
        else:
            print("DISTINTAS — sin accion necesaria")

    elif args.command == "find-duplicates":
        print(f"Buscando duplicados en: {args.folder}")
        print(f"Umbral de similitud: {args.threshold:.0%}")
        dups = find_duplicates(args.folder, args.threshold)
        if not dups:
            print("Sin duplicados detectados.")
        else:
            print(f"\n{len(dups)} par(es) de duplicados encontrados:")
            for d in dups:
                print(f"\n  {os.path.basename(d['file1'])} <-> {os.path.basename(d['file2'])}")
                print(f"  Similitud: {d['similitud']:.2%}")
                print(f"  Accion: {d['accion']}")
        if args.output_json:
            os.makedirs(os.path.dirname(args.output_json) or ".", exist_ok=True)
            with open(args.output_json, "w", encoding="utf-8") as f:
                json.dump(dups, f, indent=2, ensure_ascii=False)
            print(f"\nResultado guardado en: {args.output_json}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
