"""
inflation-diagnostic.py
Calcula el Inflation Diagnostic para detectar sobreajuste estadistico post-WFO.

Compara la distribucion de metricas IS vs OOS para detectar inflacion artificial
de resultados. Un ratio IS/OOS alto indica que el sistema fue optimizado en exceso
para el periodo in-sample y no generaliza.

Umbrales:
  inflation_score > 1.4 → sobreajuste SEVERO — descartar
  inflation_score 1.2-1.4 → sobreajuste MODERADO — revisar
  inflation_score < 1.2 → ACEPTABLE — continuar

Uso:
    python inflation-diagnostic.py --wfo-results ruta/wfo-results.csv
    python inflation-diagnostic.py --wfo-results ruta/wfo-results.csv --verbose
"""

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path


# ─── Estructuras de datos ─────────────────────────────────────────────────────

@dataclass
class WFOWindow:
    window_num: int
    pf_is:      float
    pf_oos:     float
    sharpe_is:  float
    sharpe_oos: float
    dd_is:      float
    dd_oos:     float


@dataclass
class InflationReport:
    inflation_score:  float
    pf_ratio:         float
    sharpe_ratio:     float
    dd_ratio:         float
    classification:   str   # SEVERO / MODERADO / ACEPTABLE
    recommendation:   str
    windows:          list[WFOWindow]

    @property
    def passes(self) -> bool:
        return self.inflation_score < 1.4


# ─── Clasificacion ────────────────────────────────────────────────────────────

def classify(score: float) -> tuple[str, str]:
    if score > 1.4:
        return (
            "SEVERO",
            "DESCARTAR. El sistema esta severamente sobreajustado. "
            "La diferencia IS/OOS indica que los parametros estan optimizados "
            "para el ruido del periodo IS, no para el edge real.",
        )
    elif score >= 1.2:
        return (
            "MODERADO",
            "REVISAR. Sobreajuste moderado detectado. "
            "Considerar reducir el numero de parametros optimizados "
            "o ampliar el rango de busqueda del WFO.",
        )
    else:
        return (
            "ACEPTABLE",
            "Continuar. El inflation score es aceptable. "
            "La degradacion IS→OOS esta dentro de los limites esperados.",
        )


# ─── Lectura del CSV del WFO ──────────────────────────────────────────────────

# Aliases de columnas para mayor compatibilidad con distintas versiones de SQ
COLUMN_ALIASES = {
    "pf_is":      ["PF IS", "IS PF", "IS_PF", "ProfitFactor_IS", "Profit Factor IS"],
    "pf_oos":     ["PF OOS", "OOS PF", "OOS_PF", "ProfitFactor_OOS", "Profit Factor OOS"],
    "sharpe_is":  ["Sharpe IS", "IS Sharpe", "SharpeRatio_IS", "Sharpe Ratio IS"],
    "sharpe_oos": ["Sharpe OOS", "OOS Sharpe", "SharpeRatio_OOS", "Sharpe Ratio OOS"],
    "dd_is":      ["DD IS", "IS DD", "Drawdown IS", "Max DD IS", "Max. Drawdown IS [%]"],
    "dd_oos":     ["DD OOS", "OOS DD", "Drawdown OOS", "Max DD OOS", "Max. Drawdown OOS [%]"],
}


def _find_col(headers: list[str], aliases: list[str]) -> str | None:
    for alias in aliases:
        if alias in headers:
            return alias
    return None


def _parse_float(value: str) -> float:
    value = value.strip().replace(" ", "")
    if value in ("", "-", "N/A", "n/a"):
        return 0.0
    if "," in value and "." not in value:
        value = value.replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return 0.0


def load_wfo_results(csv_path: Path) -> list[WFOWindow]:
    windows = []
    with csv_path.open(encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f, delimiter=";")
        headers = reader.fieldnames or []

        # Si el delimitador no funciono, intentar con coma
        if len(headers) <= 1:
            f.seek(0)
            reader = csv.DictReader(f, delimiter=",")
            headers = reader.fieldnames or []

        col_pf_is  = _find_col(headers, COLUMN_ALIASES["pf_is"])
        col_pf_oos = _find_col(headers, COLUMN_ALIASES["pf_oos"])
        col_sh_is  = _find_col(headers, COLUMN_ALIASES["sharpe_is"])
        col_sh_oos = _find_col(headers, COLUMN_ALIASES["sharpe_oos"])
        col_dd_is  = _find_col(headers, COLUMN_ALIASES["dd_is"])
        col_dd_oos = _find_col(headers, COLUMN_ALIASES["dd_oos"])

        if col_pf_is is None or col_pf_oos is None:
            print(f"[WARN] No se encontraron columnas PF IS/OOS. Columnas disponibles: {headers}")
            print("Asegurate de exportar el CSV del WFO con los nombres correctos de columna.")

        for i, row in enumerate(reader, 1):
            pf_is  = _parse_float(row.get(col_pf_is,  "0") if col_pf_is  else "0")
            pf_oos = _parse_float(row.get(col_pf_oos, "0") if col_pf_oos else "0")

            # Ignorar filas vacias o de totales
            if pf_is == 0 and pf_oos == 0:
                continue

            windows.append(WFOWindow(
                window_num=i,
                pf_is=pf_is,
                pf_oos=pf_oos,
                sharpe_is=_parse_float(row.get(col_sh_is,  "0") if col_sh_is  else "0"),
                sharpe_oos=_parse_float(row.get(col_sh_oos, "0") if col_sh_oos else "0"),
                dd_is=_parse_float(row.get(col_dd_is,  "0") if col_dd_is  else "0"),
                dd_oos=_parse_float(row.get(col_dd_oos, "0") if col_dd_oos else "0"),
            ))

    return windows


# ─── Calculo del Inflation Diagnostic ────────────────────────────────────────

def compute_inflation(windows: list[WFOWindow]) -> InflationReport:
    """
    Calcula el inflation score como media de los ratios IS/OOS.

    Para PF y Sharpe: ratio = IS / OOS (mayor ratio = mas inflado)
    Para DD: ratio = OOS / IS (un DD OOS mayor que IS es penalizado)
    inflation_score = media de los tres ratios
    """
    if not windows:
        return InflationReport(
            inflation_score=0.0,
            pf_ratio=0.0,
            sharpe_ratio=0.0,
            dd_ratio=0.0,
            classification="SIN DATOS",
            recommendation="No se pudieron cargar ventanas WFO.",
            windows=[],
        )

    ratios_pf     = []
    ratios_sharpe = []
    ratios_dd     = []

    for w in windows:
        # PF ratio
        if w.pf_oos > 0:
            ratios_pf.append(w.pf_is / w.pf_oos)

        # Sharpe ratio (solo si ambos son positivos)
        if w.sharpe_is > 0 and w.sharpe_oos > 0:
            ratios_sharpe.append(w.sharpe_is / w.sharpe_oos)

        # DD ratio (OOS/IS — un DD mayor en OOS indica degradacion)
        if w.dd_is > 0 and w.dd_oos > 0:
            ratios_dd.append(w.dd_oos / w.dd_is)

    pf_ratio     = sum(ratios_pf)     / len(ratios_pf)     if ratios_pf     else 1.0
    sharpe_ratio = sum(ratios_sharpe) / len(ratios_sharpe) if ratios_sharpe else 1.0
    dd_ratio     = sum(ratios_dd)     / len(ratios_dd)     if ratios_dd     else 1.0

    # Calcular inflation_score como media ponderada
    # PF tiene mas peso (50%) ya que es la metrica principal del proyecto
    weights = [(pf_ratio, 0.5), (sharpe_ratio, 0.3), (dd_ratio, 0.2)]
    inflation_score = sum(r * w for r, w in weights)

    classification, recommendation = classify(inflation_score)

    return InflationReport(
        inflation_score=round(inflation_score, 4),
        pf_ratio=round(pf_ratio, 4),
        sharpe_ratio=round(sharpe_ratio, 4),
        dd_ratio=round(dd_ratio, 4),
        classification=classification,
        recommendation=recommendation,
        windows=windows,
    )


# ─── Presentacion de resultados ───────────────────────────────────────────────

def print_report(report: InflationReport, verbose: bool = False) -> None:
    print(f"\n{'='*60}")
    print(f"INFLATION DIAGNOSTIC")
    print(f"{'='*60}")
    print(f"Ventanas WFO analizadas: {len(report.windows)}")
    print(f"")
    print(f"Ratios IS/OOS:")
    print(f"  PF ratio:     {report.pf_ratio:.4f}  (IS/OOS — ideal: < 1.4)")
    print(f"  Sharpe ratio: {report.sharpe_ratio:.4f}  (IS/OOS — ideal: < 1.4)")
    print(f"  DD ratio:     {report.dd_ratio:.4f}  (OOS/IS — ideal: < 1.4)")
    print(f"")
    print(f"  INFLATION SCORE: {report.inflation_score:.4f}")
    print(f"  CLASIFICACION:   {report.classification}")
    print(f"")
    print(f"  {report.recommendation}")
    print(f"")

    if report.passes:
        print(f"  RESULTADO: PASA → Continuar con el pipeline")
    else:
        print(f"  RESULTADO: DESCARTAR → Estrategia sobreajustada")

    if verbose and report.windows:
        print(f"\n{'─'*60}")
        print(f"Detalle por ventana:")
        print(f"{'Ventana':>8} {'PF IS':>8} {'PF OOS':>8} {'Ratio PF':>10} {'DD IS':>7} {'DD OOS':>7}")
        print(f"{'─'*8:>8} {'─'*8:>8} {'─'*8:>8} {'─'*10:>10} {'─'*7:>7} {'─'*7:>7}")
        for w in report.windows:
            ratio = w.pf_is / w.pf_oos if w.pf_oos > 0 else 0
            flag = " *** ALTO" if ratio > 1.4 else ""
            print(f"{w.window_num:>8} {w.pf_is:>8.2f} {w.pf_oos:>8.2f} {ratio:>10.4f} "
                  f"{w.dd_is:>7.1f} {w.dd_oos:>7.1f}{flag}")

    print(f"{'='*60}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Inflation Diagnostic — TradingLab")
    parser.add_argument(
        "--wfo-results",
        type=Path,
        required=True,
        help="CSV con resultados IS/OOS del WFO exportado desde SQ",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Mostrar detalle por ventana WFO",
    )
    args = parser.parse_args()

    if not args.wfo_results.exists():
        print(f"[ERROR] Archivo no encontrado: {args.wfo_results}")
        print("Exportar desde SQ: WFO → Export Results → CSV")
        return 1

    print(f"Cargando: {args.wfo_results}")
    windows = load_wfo_results(args.wfo_results)

    if not windows:
        print("[ERROR] No se encontraron ventanas WFO validas en el CSV.")
        return 1

    print(f"  {len(windows)} ventanas cargadas.")

    report = compute_inflation(windows)
    print_report(report, verbose=args.verbose)

    # Exit code segun resultado (util para scripts de automatizacion)
    # 0 = ACEPTABLE, 1 = MODERADO, 2 = SEVERO
    if report.classification == "ACEPTABLE":
        return 0
    elif report.classification == "MODERADO":
        return 1
    else:
        return 2


if __name__ == "__main__":
    sys.exit(main())
