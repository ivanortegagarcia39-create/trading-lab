"""
validate-sqx-folder.py
Compara dos carpetas de CSVs de SQ (Strategy*.csv) y calcula
la divergencia media en la columna Balance entre un baseline
y un nuevo build.

Uso:
    python validate-sqx-folder.py \
        --baseline-folder ruta/baseline \
        --new-folder ruta/nuevo \
        --threshold 10

PASS si divergencia media < threshold
FAIL si divergencia media >= threshold

Nota: SQ exporta CSVs con separador ; y numeros europeos
(coma decimal). Este script maneja ese formato correctamente.
"""

import argparse
import csv
import os
import sys
from glob import glob


def parse_european_number(value: str) -> float:
    """Convierte numero europeo (coma decimal) a float."""
    # Eliminar espacios y posibles separadores de miles (punto)
    value = value.strip()
    # Si tiene punto y coma: 1.234,56 → reemplazar punto por nada, coma por punto
    if "," in value and "." in value:
        value = value.replace(".", "").replace(",", ".")
    elif "," in value:
        value = value.replace(",", ".")
    return float(value)


def read_balance_from_csv(filepath: str) -> list[float]:
    """Lee la columna Balance de un CSV exportado por SQ (separador ;)."""
    balances = []
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            # Buscar columna Balance (puede tener espacios o variaciones)
            balance_key = next(
                (k for k in row.keys() if k.strip().lower() == "balance"), None
            )
            if balance_key is None:
                continue
            raw = row[balance_key].strip()
            if raw == "" or raw == "-":
                continue
            try:
                balances.append(parse_european_number(raw))
            except ValueError:
                pass  # Ignorar filas no numericas
    return balances


def load_folder_balances(folder: str) -> dict[str, list[float]]:
    """Carga todos los Strategy*.csv de una carpeta."""
    pattern = os.path.join(folder, "Strategy*.csv")
    files = sorted(glob(pattern))
    if not files:
        print(f"ERROR: No se encontraron archivos Strategy*.csv en: {folder}")
        sys.exit(1)
    result = {}
    for f in files:
        name = os.path.basename(f)
        balances = read_balance_from_csv(f)
        if balances:
            result[name] = balances
    return result


def compute_mean_divergence(
    baseline: dict[str, list[float]], new: dict[str, list[float]]
) -> float:
    """
    Calcula la divergencia media entre baseline y nuevo build.
    Para cada archivo comun, calcula el ultimo balance de cada uno
    y la divergencia porcentual absoluta.
    """
    common_files = set(baseline.keys()) & set(new.keys())
    if not common_files:
        print("WARNING: No hay archivos en comun entre las dos carpetas.")
        print(f"  Baseline: {list(baseline.keys())[:5]}")
        print(f"  New:      {list(new.keys())[:5]}")
        return 0.0

    divergences = []
    for fname in sorted(common_files):
        b_last = baseline[fname][-1]
        n_last = new[fname][-1]
        if b_last == 0:
            continue
        pct_diff = abs(n_last - b_last) / abs(b_last) * 100
        divergences.append(pct_diff)

    if not divergences:
        return 0.0
    return sum(divergences) / len(divergences)


def main():
    parser = argparse.ArgumentParser(
        description="Compara dos carpetas de CSVs de SQ y calcula divergencia en Balance."
    )
    parser.add_argument("--baseline-folder", required=True, help="Carpeta del build de referencia")
    parser.add_argument("--new-folder", required=True, help="Carpeta del nuevo build")
    parser.add_argument(
        "--threshold",
        type=float,
        default=10.0,
        help="Umbral de divergencia en %% (default: 10)",
    )
    args = parser.parse_args()

    print(f"Baseline folder : {args.baseline_folder}")
    print(f"New folder      : {args.new_folder}")
    print(f"Threshold       : {args.threshold}%%")
    print()

    baseline = load_folder_balances(args.baseline_folder)
    new = load_folder_balances(args.new_folder)

    print(f"Archivos en baseline : {len(baseline)}")
    print(f"Archivos en new      : {len(new)}")

    mean_div = compute_mean_divergence(baseline, new)
    print(f"Divergencia media    : {mean_div:.2f}%%")
    print()

    if mean_div < args.threshold:
        print(f"RESULTADO: PASS — divergencia {mean_div:.2f}%% < umbral {args.threshold}%%")
        sys.exit(0)
    else:
        print(f"RESULTADO: FAIL — divergencia {mean_div:.2f}%% >= umbral {args.threshold}%%")
        sys.exit(1)


if __name__ == "__main__":
    main()
