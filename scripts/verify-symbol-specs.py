"""
verify-symbol-specs.py
Compara las especificaciones de simbolos exportadas desde SQ
con los valores esperados para FTMO.

Uso:
    python verify-symbol-specs.py --sq-export ruta/export.csv

WARNING — LIMITACION CONOCIDA (SQ Build 143):
SQ Build 143 no exporta especificaciones de simbolos en un
formato CSV compatible con este script. Si usas SQ Build 143,
este script mostrara un error de columnas y no podra validar
automaticamente. En ese caso, verificar las specs manualmente
en SQ: Symbol Manager → seleccionar simbolo → ver propiedades.

Specs esperadas (FTMO):
  XAUUSD: PipSize 1.0, PointValue 1.0,   TickSize 0.01
  EURUSD: PipSize 0.0001, PointValue 10.0, TickSize 0.00001
  GBPUSD: PipSize 0.0001, PointValue 10.0, TickSize 0.00001
  USDJPY: PipSize 0.01,   PointValue 1000.0, TickSize 0.001
"""

import argparse
import csv
import sys

# Specs esperadas para FTMO
EXPECTED_SPECS: dict[str, dict[str, float]] = {
    "XAUUSD": {"PipSize": 1.0, "PointValue": 1.0, "TickSize": 0.01},
    "EURUSD": {"PipSize": 0.0001, "PointValue": 10.0, "TickSize": 0.00001},
    "GBPUSD": {"PipSize": 0.0001, "PointValue": 10.0, "TickSize": 0.00001},
    "USDJPY": {"PipSize": 0.01, "PointValue": 1000.0, "TickSize": 0.001},
}

# Columnas requeridas en el CSV exportado desde SQ
REQUIRED_COLUMNS = {"Symbol", "PipSize", "PointValue", "TickSize"}


def parse_european_number(value: str) -> float:
    """Convierte numero europeo (coma decimal) a float."""
    value = value.strip()
    if "," in value and "." in value:
        value = value.replace(".", "").replace(",", ".")
    elif "," in value:
        value = value.replace(",", ".")
    return float(value)


def load_sq_export(filepath: str) -> list[dict]:
    """Carga el CSV de exportacion de SQ."""
    rows = []
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        # Intentar con separador ; primero (formato SQ europeo)
        content = f.read()

    # Detectar separador
    separator = ";" if content.count(";") > content.count(",") else ","

    reader = csv.DictReader(content.splitlines(), delimiter=separator)
    headers = reader.fieldnames

    if headers is None:
        print("ERROR: No se pudo leer el encabezado del CSV.")
        sys.exit(1)

    # Normalizar nombres de columnas (eliminar espacios)
    normalized_headers = [h.strip() for h in headers]
    missing = REQUIRED_COLUMNS - set(normalized_headers)

    if missing:
        print("=" * 60)
        print("WARNING — LIMITACION SQ BUILD 143")
        print("=" * 60)
        print(
            "SQ Build 143 no exporta especificaciones de simbolos en")
        print("formato compatible con este script.")
        print()
        print(f"Columnas requeridas: {sorted(REQUIRED_COLUMNS)}")
        print(f"Columnas encontradas: {sorted(normalized_headers)}")
        print(f"Columnas faltantes: {sorted(missing)}")
        print()
        print("ACCION MANUAL REQUERIDA:")
        print("  SQ → Symbol Manager → seleccionar simbolo → propiedades")
        print("  Verificar PipSize, PointValue y TickSize manualmente.")
        print("=" * 60)
        sys.exit(2)

    for row in reader:
        normalized_row = {k.strip(): v.strip() for k, v in row.items()}
        rows.append(normalized_row)

    return rows


def validate_specs(rows: list[dict]) -> bool:
    """Valida las specs de cada simbolo conocido contra los valores esperados."""
    all_pass = True
    symbols_found = set()

    for row in rows:
        symbol = row.get("Symbol", "").strip().upper()
        # Normalizar: quitar sufijos como _ftmo, _M1_dukas, etc.
        base_symbol = symbol.split("_")[0]

        if base_symbol not in EXPECTED_SPECS:
            continue

        symbols_found.add(base_symbol)
        expected = EXPECTED_SPECS[base_symbol]
        errors = []

        for spec_name, expected_val in expected.items():
            raw = row.get(spec_name, "").strip()
            if raw == "":
                errors.append(f"  {spec_name}: valor vacio en CSV")
                continue
            try:
                actual_val = parse_european_number(raw)
            except ValueError:
                errors.append(f"  {spec_name}: no se pudo parsear '{raw}'")
                continue

            if abs(actual_val - expected_val) > expected_val * 0.001:
                errors.append(
                    f"  {spec_name}: esperado {expected_val}, encontrado {actual_val}"
                )

        if errors:
            print(f"FAIL — {symbol}")
            for e in errors:
                print(e)
            all_pass = False
        else:
            specs_str = ", ".join(
                f"{k}={expected[k]}" for k in expected
            )
            print(f"PASS — {symbol} ({specs_str})")

    # Advertir sobre simbolos esperados no encontrados en el export
    not_found = set(EXPECTED_SPECS.keys()) - symbols_found
    if not_found:
        print()
        print(f"INFO: Simbolos no encontrados en el export: {sorted(not_found)}")
        print("  Verificar manualmente en SQ Symbol Manager.")

    return all_pass


def main():
    print("=" * 60)
    print("WARNING — LIMITACION CONOCIDA (SQ Build 143)")
    print("SQ Build 143 puede no exportar specs en formato")
    print("compatible. Si el script falla con error de columnas,")
    print("verificar specs manualmente en SQ Symbol Manager.")
    print("=" * 60)
    print()

    parser = argparse.ArgumentParser(
        description="Verifica specs de simbolos SQ contra valores esperados FTMO."
    )
    parser.add_argument(
        "--sq-export",
        required=True,
        help="Ruta al CSV exportado desde SQ con specs de simbolos",
    )
    args = parser.parse_args()

    print(f"Archivo: {args.sq_export}")
    print()

    rows = load_sq_export(args.sq_export)
    print(f"Filas cargadas: {len(rows)}")
    print()

    ok = validate_specs(rows)
    print()

    if ok:
        print("RESULTADO: PASS — todas las specs verificadas correctamente")
        sys.exit(0)
    else:
        print("RESULTADO: FAIL — hay discrepancias en las specs")
        sys.exit(1)


if __name__ == "__main__":
    main()
