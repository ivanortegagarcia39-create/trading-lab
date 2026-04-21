"""
coordination-detector.py — Detector de coordinacion entre estrategias

Mide el indice de coordinacion entre dos estrategias para determinar
si pueden operar simultaneamente en la misma prop firm sin violar
las reglas anti-coordinacion (group trading detection).

Tres dimensiones de analisis:
  1. Logica (Jaccard similarity de fingerprints)
  2. Timing (correlacion de horas de entrada entre estrategias)
  3. Activos (mismos activos operados)

Indice final = media ponderada de las tres dimensiones.

Umbral critico: 0.70 → no pueden operar simultaneamente
                        en la misma prop firm
Umbral medio:   0.50 → pueden operar con delay extra entre señales
Por debajo:     sin restriccion

Uso:
  python coordination-detector.py --strategy1 path1 --strategy2 path2
  python coordination-detector.py --strategy1 path1 --strategy2 path2 --output result.json

Formatos de entrada soportados: .sqx (XML) o .csv (SQ export)

Dependencia: strategy-fingerprint.py (debe estar en el mismo directorio)
"""

import argparse
import csv
import json
import math
import os
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime


# ---------------------------------------------------------------------------
# Umbrales de decision
# ---------------------------------------------------------------------------

THRESHOLD_CRITICAL = 0.70  # No operar juntas en misma prop firm
THRESHOLD_CAUTION = 0.50   # Operar con delay extra entre señales

# Pesos de cada dimension en el indice final
WEIGHT_LOGIC = 0.40    # Similitud de logica (mayor peso — riesgo principal)
WEIGHT_TIMING = 0.35   # Correlacion de horarios
WEIGHT_ASSETS = 0.25   # Solapamiento de activos


# ---------------------------------------------------------------------------
# Parseo de estrategias
# ---------------------------------------------------------------------------

def parse_sqx_file(filepath: str) -> dict:
    """
    Extrae informacion relevante de un archivo .sqx (XML de StrategyQuant).
    Retorna dict con: indicators, conditions, direction, sl_type, tp_type,
                      assets, entry_hours
    """
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except ET.ParseError as e:
        raise ValueError(f"Error parseando XML en {filepath}: {e}")

    info = {
        "indicators": [],
        "conditions": [],
        "direction": "unknown",
        "sl_type": "unknown",
        "tp_type": "unknown",
        "assets": [],
        "entry_hours": [],
        "source": filepath,
    }

    # Extraer indicadores
    for node in root.iter():
        tag = node.tag.lower()
        if "indicator" in tag:
            name = node.get("name") or node.get("type") or node.text
            if name:
                info["indicators"].append(name.strip().upper())
        if "symbol" in tag or "instrument" in tag:
            val = node.get("value") or node.text
            if val:
                info["assets"].append(val.strip().upper())
        if "direction" in tag:
            val = node.get("value") or node.text
            if val:
                info["direction"] = val.strip().lower()

    # Normalizar listas
    info["indicators"] = sorted(set(info["indicators"]))
    info["assets"] = sorted(set(info["assets"]))

    return info


def parse_csv_file(filepath: str) -> dict:
    """
    Extrae informacion de un archivo CSV exportado de SQ.
    El CSV puede tener separador ; y formato numerico europeo.
    """
    info = {
        "indicators": [],
        "conditions": [],
        "direction": "unknown",
        "sl_type": "unknown",
        "tp_type": "unknown",
        "assets": [],
        "entry_hours": [],
        "source": filepath,
    }

    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            # Detectar separador
            sample = f.read(2048)
            f.seek(0)
            sep = ";" if sample.count(";") > sample.count(",") else ","
            reader = csv.DictReader(f, delimiter=sep)
            rows = list(reader)
    except Exception as e:
        raise ValueError(f"Error leyendo CSV {filepath}: {e}")

    if not rows:
        return info

    # Buscar columnas relevantes
    header_lower = {k.lower(): k for k in rows[0].keys()}

    symbol_col = next(
        (header_lower[k] for k in header_lower if "symbol" in k or "instrument" in k),
        None
    )
    logic_col = next(
        (header_lower[k] for k in header_lower if "logic" in k or "strategy" in k),
        None
    )
    direction_col = next(
        (header_lower[k] for k in header_lower if "direction" in k or "side" in k),
        None
    )

    assets = set()
    directions = []
    indicators_found = []

    for row in rows:
        if symbol_col and row.get(symbol_col):
            assets.add(row[symbol_col].strip().upper())
        if direction_col and row.get(direction_col):
            directions.append(row[direction_col].strip().lower())
        if logic_col and row.get(logic_col):
            logic_text = row[logic_col].upper()
            # Extraer nombres de indicadores conocidos del texto de logica
            for ind in _KNOWN_INDICATORS:
                if ind in logic_text:
                    indicators_found.append(ind)

    info["assets"] = sorted(assets)
    info["indicators"] = sorted(set(indicators_found))
    if directions:
        counter = Counter(directions)
        info["direction"] = counter.most_common(1)[0][0]

    return info


# Indicadores conocidos para buscar en textos de logica CSV
_KNOWN_INDICATORS = [
    "EMA", "SMA", "DEMA", "HMA", "RSI", "MACD", "ADX", "ATR",
    "CCI", "STOCHASTIC", "WILLIAMS", "MOMENTUM", "ROC", "DEMARKER",
    "BOLLINGER", "KELTNER", "DONCHIAN", "PARABOLIC", "AROON",
    "HIGHEST", "LOWEST",
]


def load_strategy(filepath: str) -> dict:
    """Carga una estrategia segun su extension."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Archivo no encontrado: {filepath}")

    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".sqx":
        return parse_sqx_file(filepath)
    elif ext == ".csv":
        return parse_csv_file(filepath)
    else:
        raise ValueError(f"Extension no soportada: {ext}. Usar .sqx o .csv")


# ---------------------------------------------------------------------------
# Dimension 1: Similitud de logica (Jaccard)
# ---------------------------------------------------------------------------

def jaccard_similarity(set_a: set, set_b: set) -> float:
    """
    Similitud de Jaccard entre dos conjuntos.
    Retorna 0.0 si ambos estan vacios.
    """
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def compute_logic_similarity(s1: dict, s2: dict) -> float:
    """
    Similitud de logica entre dos estrategias.
    Combina: similitud de indicadores + misma direccion.
    """
    ind_sim = jaccard_similarity(
        set(s1["indicators"]),
        set(s2["indicators"])
    )

    # Bonus si la direccion es identica (mismo sesgo direccional)
    direction_bonus = 0.0
    d1 = s1.get("direction", "unknown")
    d2 = s2.get("direction", "unknown")
    if d1 != "unknown" and d2 != "unknown":
        if d1 == d2:
            direction_bonus = 0.15  # mismo sesgo → mas coordinacion
        elif {d1, d2} == {"long", "short"}:
            direction_bonus = -0.10  # opuestos → menos coordinacion

    # Similitud de tipo de SL/TP
    sl_sim = 1.0 if s1.get("sl_type") == s2.get("sl_type") else 0.0
    tp_sim = 1.0 if s1.get("tp_type") == s2.get("tp_type") else 0.0
    exit_sim = (sl_sim + tp_sim) / 2.0

    logic_score = 0.70 * ind_sim + 0.20 * exit_sim + 0.10 * direction_bonus
    return max(0.0, min(1.0, logic_score))


# ---------------------------------------------------------------------------
# Dimension 2: Correlacion de timing
# ---------------------------------------------------------------------------

def compute_timing_similarity(s1: dict, s2: dict) -> float:
    """
    Correlacion de horas de entrada entre estrategias.
    Si no hay datos de horas, se usa similitud basada en la sesion configurada.
    La sesion por defecto del proyecto es 08:00-20:00 — mismo para todas.
    Sin datos de trades reales, asumir correlacion media de 0.5.
    """
    hours1 = s1.get("entry_hours", [])
    hours2 = s2.get("entry_hours", [])

    if not hours1 or not hours2:
        # Sin datos de horas — misma sesion configurada (08:00-20:00)
        # Las estrategias pueden entrar en cualquier momento del rango
        # Correlacion de timing indeterminada → asumir 0.5 (neutral)
        return 0.5

    # Calcular distribucion por hora del dia (0-23)
    def hour_distribution(hours: list) -> list:
        counts = [0] * 24
        for h in hours:
            h_int = int(h) % 24
            counts[h_int] += 1
        total = sum(counts)
        return [c / total for c in counts] if total > 0 else counts

    dist1 = hour_distribution(hours1)
    dist2 = hour_distribution(hours2)

    # Correlacion de Pearson entre distribuciones
    n = 24
    mean1 = sum(dist1) / n
    mean2 = sum(dist2) / n

    num = sum((dist1[i] - mean1) * (dist2[i] - mean2) for i in range(n))
    den1 = math.sqrt(sum((dist1[i] - mean1) ** 2 for i in range(n)))
    den2 = math.sqrt(sum((dist2[i] - mean2) ** 2 for i in range(n)))

    if den1 == 0 or den2 == 0:
        return 0.5

    corr = num / (den1 * den2)
    # Normalizar correlacion [-1, 1] → similitud [0, 1]
    return (corr + 1.0) / 2.0


# ---------------------------------------------------------------------------
# Dimension 3: Solapamiento de activos
# ---------------------------------------------------------------------------

def compute_asset_similarity(s1: dict, s2: dict) -> float:
    """
    Solapamiento de activos operados entre estrategias.
    Si ambas operan exactamente los mismos activos → 1.0
    Si no tienen ningun activo en comun → 0.0
    """
    assets1 = set(s1.get("assets", []))
    assets2 = set(s2.get("assets", []))

    if not assets1 and not assets2:
        # Sin informacion de activos — asumir mismo activo (caso tipico
        # cuando ambas estrategias son del mismo build)
        return 1.0

    return jaccard_similarity(assets1, assets2)


# ---------------------------------------------------------------------------
# Indice de coordinacion final
# ---------------------------------------------------------------------------

def compute_coordination_index(s1: dict, s2: dict) -> dict:
    """
    Calcula el indice de coordinacion entre dos estrategias.

    Retorna dict con:
      - coordination_index: float [0.0, 1.0]
      - logic_similarity: float
      - timing_similarity: float
      - asset_similarity: float
      - recommendation: str
      - can_operate_same_firm: bool
      - requires_delay: bool
    """
    logic_sim = compute_logic_similarity(s1, s2)
    timing_sim = compute_timing_similarity(s1, s2)
    asset_sim = compute_asset_similarity(s1, s2)

    index = (
        WEIGHT_LOGIC * logic_sim
        + WEIGHT_TIMING * timing_sim
        + WEIGHT_ASSETS * asset_sim
    )
    index = round(max(0.0, min(1.0, index)), 4)

    if index >= THRESHOLD_CRITICAL:
        recommendation = (
            f"RESTRICCION: Indice de coordinacion {index:.2f} >= {THRESHOLD_CRITICAL}. "
            "Estas estrategias NO pueden operar simultaneamente en la misma prop firm. "
            "Asignar a prop firms diferentes."
        )
        can_operate_same_firm = False
        requires_delay = False
    elif index >= THRESHOLD_CAUTION:
        recommendation = (
            f"PRECAUCION: Indice de coordinacion {index:.2f} en zona de cautela "
            f"[{THRESHOLD_CAUTION}, {THRESHOLD_CRITICAL}). "
            "Pueden operar en la misma prop firm con delay extra entre señales. "
            "Configurar retraso minimo de 5 minutos entre entradas simultaneas."
        )
        can_operate_same_firm = True
        requires_delay = True
    else:
        recommendation = (
            f"LIBRE: Indice de coordinacion {index:.2f} < {THRESHOLD_CAUTION}. "
            "Sin restriccion. Pueden operar simultaneamente en la misma prop firm."
        )
        can_operate_same_firm = True
        requires_delay = False

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "strategy1": os.path.basename(s1["source"]),
        "strategy2": os.path.basename(s2["source"]),
        "coordination_index": index,
        "dimensions": {
            "logic_similarity": round(logic_sim, 4),
            "timing_similarity": round(timing_sim, 4),
            "asset_similarity": round(asset_sim, 4),
        },
        "weights": {
            "logic": WEIGHT_LOGIC,
            "timing": WEIGHT_TIMING,
            "assets": WEIGHT_ASSETS,
        },
        "thresholds": {
            "critical": THRESHOLD_CRITICAL,
            "caution": THRESHOLD_CAUTION,
        },
        "can_operate_same_firm": can_operate_same_firm,
        "requires_delay": requires_delay,
        "recommendation": recommendation,
        "assets_s1": s1.get("assets", []),
        "assets_s2": s2.get("assets", []),
        "indicators_s1": s1.get("indicators", []),
        "indicators_s2": s2.get("indicators", []),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Detecta el indice de coordinacion entre dos estrategias de trading."
    )
    parser.add_argument(
        "--strategy1",
        required=True,
        help="Ruta a la primera estrategia (.sqx o .csv)",
    )
    parser.add_argument(
        "--strategy2",
        required=True,
        help="Ruta a la segunda estrategia (.sqx o .csv)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Ruta al archivo JSON de salida (opcional). Si no se especifica, imprime en stdout.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Mostrar detalle de componentes ademas del resultado.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        s1 = load_strategy(args.strategy1)
        s2 = load_strategy(args.strategy2)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    result = compute_coordination_index(s1, s2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Resultado guardado en: {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

    if args.verbose:
        print("\n--- DESGLOSE ---")
        print(f"Logica  (peso {WEIGHT_LOGIC:.0%}): {result['dimensions']['logic_similarity']:.4f}")
        print(f"Timing  (peso {WEIGHT_TIMING:.0%}): {result['dimensions']['timing_similarity']:.4f}")
        print(f"Activos (peso {WEIGHT_ASSETS:.0%}): {result['dimensions']['asset_similarity']:.4f}")
        print(f"INDICE FINAL: {result['coordination_index']:.4f}")
        print(f"\n{result['recommendation']}")

    # Exit code segun nivel de coordinacion
    if not result["can_operate_same_firm"]:
        sys.exit(2)  # Coordinacion critica
    elif result["requires_delay"]:
        sys.exit(1)  # Coordinacion media — precaucion
    else:
        sys.exit(0)  # Sin restriccion


if __name__ == "__main__":
    main()
