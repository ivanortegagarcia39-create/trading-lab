"""
validate-sqx-build.py
Compara dos archivos CSV unicos de SQ y calcula la divergencia
en la columna Balance entre un baseline y un nuevo build.

Uso:
    python validate-sqx-build.py \
        --baseline ruta/baseline.csv \
        --new ruta/nuevo.csv \
        --threshold 10

PASS si divergencia media < threshold
FAIL si divergencia media >= threshold

Nota: SQ exporta CSVs con separador ; y numeros europeos
(coma decimal). Este script maneja ese formato correctamente.
"""

import argparse
import csv
import sys


def parse_european_number(value: str) -> float:
    """Convierte numero europeo (coma decimal) a float."""
    value = value.strip()
    # Si tiene punto y coma: 1.234,56 → reemplazar punto por nada, coma por punto
    if "," in value and "." in value:
        value = value.replace(".", "").replace(",", ".")
    elif "," in value:
        value = value.replace(",", ".")
    return float(value)


def read_balance_column(filepath: str) -> list[float]:
    """Lee la columna Balance de un CSV exportado por SQ (separador ;)."""
    balances = []
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        headers = reader.fieldnames
        if headers is None:
            print(f"ERROR: No se pudo leer el encabezado de {filepath}")
            sys.exit(1)

        balance_key = next(
            (k for k in headers if k.strip().lower() == "balance"), None
        )
        if balance_key is None:
            print(f"ERROR: No se encontro columna 'Balance' en {filepath}")
            print(f"  Columnas disponibles: {headers}")
            sys.exit(1)

        for row in reader:
            raw = row[balance_key].strip()
            if raw == "" or raw == "-":
                continue
            try:
                balances.append(parse_european_number(raw))
            except ValueError:
                pass  # Ignorar filas no numericas

    return balances


def compute_divergence(baseline_vals: list[float], new_vals: list[float]) -> float:
    """
    Calcula divergencia media porcentual entre dos series de Balance.
    Compara punto a punto hasta el minimo de longitud de ambas.
    """
    if not baseline_vals or not new_vals:
        return 0.0

    n = min(len(baseline_vals), len(new_vals))
    divergences = []
    for i in range(n):
        b = baseline_vals[i]
        nv = new_vals[i]
        if b == 0:
            continue
        pct_diff = abs(nv - b) / abs(b) * 100
        divergences.append(pct_diff)

    if not divergences:
        return 0.0
    return sum(divergences) / len(divergences)


def main():
    parser = argparse.ArgumentParser(
        description="Compara dos CSVs de SQ y calcula divergencia en columna Balance."
    )
    parser.add_argument("--baseline", required=True, help="CSV de referencia (baseline)")
    parser.add_argument("--new", required=True, help="CSV del nuevo build")
    parser.add_argument(
        "--threshold",
        type=float,
        default=10.0,
        help="Umbral de divergencia en %% (default: 10)",
    )
    args = parser.parse_args()

    print(f"Baseline : {args.baseline}")
    print(f"New      : {args.new}")
    print(f"Threshold: {args.threshold}%%")
    print()

    baseline_vals = read_balance_column(args.baseline)
    new_vals = read_balance_column(args.new)

    print(f"Filas baseline : {len(baseline_vals)}")
    print(f"Filas new      : {len(new_vals)}")

    mean_div = compute_divergence(baseline_vals, new_vals)
    print(f"Divergencia media: {mean_div:.2f}%%")
    print()

    if mean_div < args.threshold:
        print(f"RESULTADO: PASS — divergencia {mean_div:.2f}%% < umbral {args.threshold}%%")
        sys.exit(0)
    else:
        print(f"RESULTADO: FAIL — divergencia {mean_div:.2f}%% >= umbral {args.threshold}%%")
        sys.exit(1)


if __name__ == "__main__":
    main()
