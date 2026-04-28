"""
build-analyzer.py
Genera resumen ejecutivo automatico tras cada build de StrategyQuant X.

Lee archivos Strategy*.csv de la carpeta de resultados, extrae metricas clave
y produce estadisticas del build completo. Si Ollama esta disponible en
localhost:11434 genera ademas un resumen interpretativo con deepseek-r1:7b.

Uso:
    python build-analyzer.py
    python build-analyzer.py --results-folder results/
    python build-analyzer.py --results-folder results/ --build-num 10
    python build-analyzer.py --no-ollama
"""

import argparse
import csv
import importlib.util
import json
import sys
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Importación dinámica del model-router (nombre con guión)
_router_path = Path(__file__).parent / "model-router.py"
if _router_path.exists():
    _router_spec = importlib.util.spec_from_file_location("model_router", _router_path)
    _model_router = importlib.util.module_from_spec(_router_spec)
    _router_spec.loader.exec_module(_model_router)
else:
    _model_router = None


# ─── Estructuras de datos ─────────────────────────────────────────────────────

@dataclass
class StrategyMetrics:
    name: str
    pf: float
    dd_max: float
    trades_total: int
    win_rate: float
    trades_per_month: float
    sharpe_estimated: float


@dataclass
class BuildSummary:
    build_num: int
    timestamp: str
    total_generated: int
    total_in_databank: int
    strategies: list[StrategyMetrics] = field(default_factory=list)

    @property
    def approval_rate(self) -> float:
        if self.total_generated == 0:
            return 0.0
        return self.total_in_databank / self.total_generated * 100

    @property
    def pf_values(self) -> list[float]:
        return [s.pf for s in self.strategies]

    @property
    def pf_max(self) -> float:
        return max(self.pf_values) if self.pf_values else 0.0

    @property
    def pf_min(self) -> float:
        return min(self.pf_values) if self.pf_values else 0.0

    @property
    def pf_avg(self) -> float:
        return sum(self.pf_values) / len(self.pf_values) if self.pf_values else 0.0

    def pf_distribution(self) -> dict:
        dist = {"<1.3": 0, "1.3-1.5": 0, "1.5-1.8": 0, "1.8-2.0": 0, ">=2.0": 0}
        for pf in self.pf_values:
            if pf < 1.3:
                dist["<1.3"] += 1
            elif pf < 1.5:
                dist["1.3-1.5"] += 1
            elif pf < 1.8:
                dist["1.5-1.8"] += 1
            elif pf < 2.0:
                dist["1.8-2.0"] += 1
            else:
                dist[">=2.0"] += 1
        return dist


# ─── Lectura de CSV de SQ ─────────────────────────────────────────────────────

# Columnas conocidas del export CSV de SQ (separador ;, decimal ,)
# Los nombres exactos pueden variar segun la version de SQ.
COLUMN_ALIASES = {
    "pf":          ["Profit Factor", "PF", "Profit_Factor", "profitFactor"],
    "dd_max":      ["Max. Drawdown [%]", "Max DD", "MaxDrawdown", "drawdown", "Max. Drawdown"],
    "trades":      ["# Trades", "Trades", "Total Trades", "NumTrades", "totalTrades"],
    "win_rate":    ["Win Rate [%]", "Win Rate", "WinRate", "winRate"],
    "tpm":         ["Avg. Trades/Month", "Trades/Month", "TradesPerMonth", "tradesPerMonth"],
    "sharpe":      ["Sharpe Ratio", "Sharpe", "sharpeRatio"],
}


def _find_column(headers: list[str], aliases: list[str]) -> str | None:
    for alias in aliases:
        if alias in headers:
            return alias
    return None


def _parse_float(value: str) -> float:
    """Parsea floats con formato europeo (coma decimal) o ingles (punto)."""
    value = value.strip().replace(" ", "")
    if value in ("", "-", "N/A", "n/a"):
        return 0.0
    # SQ usa coma como decimal en algunos exports
    if "," in value and "." not in value:
        value = value.replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return 0.0


def _parse_int(value: str) -> int:
    try:
        return int(value.strip().replace(" ", "").replace(",", "").replace(".", ""))
    except ValueError:
        return 0


def load_strategies_from_csv(csv_path: Path) -> list[StrategyMetrics]:
    """Carga metricas de estrategias desde un CSV exportado por SQ."""
    strategies = []
    with csv_path.open(encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f, delimiter=";")
        headers = reader.fieldnames or []

        col_pf       = _find_column(headers, COLUMN_ALIASES["pf"])
        col_dd       = _find_column(headers, COLUMN_ALIASES["dd_max"])
        col_trades   = _find_column(headers, COLUMN_ALIASES["trades"])
        col_wr       = _find_column(headers, COLUMN_ALIASES["win_rate"])
        col_tpm      = _find_column(headers, COLUMN_ALIASES["tpm"])
        col_sharpe   = _find_column(headers, COLUMN_ALIASES["sharpe"])

        if col_pf is None:
            print(f"  [WARN] No se encontro columna PF en {csv_path.name}. Columnas: {headers[:10]}")

        for row in reader:
            name = row.get("Name", row.get("Strategy", csv_path.stem))
            pf        = _parse_float(row.get(col_pf, "0") if col_pf else "0")
            dd        = _parse_float(row.get(col_dd, "0") if col_dd else "0")
            trades    = _parse_int(row.get(col_trades, "0") if col_trades else "0")
            wr        = _parse_float(row.get(col_wr, "0") if col_wr else "0")
            tpm       = _parse_float(row.get(col_tpm, "0") if col_tpm else "0")
            sharpe    = _parse_float(row.get(col_sharpe, "0") if col_sharpe else "0")

            if pf > 0:  # Ignorar filas vacias o de cabecera repetida
                strategies.append(StrategyMetrics(
                    name=name,
                    pf=pf,
                    dd_max=dd,
                    trades_total=trades,
                    win_rate=wr,
                    trades_per_month=tpm,
                    sharpe_estimated=sharpe,
                ))

    return strategies


# ─── Escaneo de carpeta de resultados ────────────────────────────────────────

def scan_results_folder(results_folder: Path) -> list[StrategyMetrics]:
    """Busca todos los CSV de estrategias en la carpeta de resultados."""
    all_strategies = []
    csv_files = list(results_folder.glob("Strategy*.csv")) + list(results_folder.glob("strategy*.csv"))

    if not csv_files:
        # Buscar tambien en subcarpetas un nivel
        csv_files = list(results_folder.glob("*/Strategy*.csv")) + list(results_folder.glob("*/strategy*.csv"))

    if not csv_files:
        print(f"  [WARN] No se encontraron archivos Strategy*.csv en {results_folder}")
        return []

    for csv_file in csv_files:
        strategies = load_strategies_from_csv(csv_file)
        print(f"  Cargado: {csv_file.name} ({len(strategies)} estrategias)")
        all_strategies.extend(strategies)

    return all_strategies


# ─── Ollama ───────────────────────────────────────────────────────────────────

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "deepseek-r1:7b"
OLLAMA_TIMEOUT = 120


def ollama_available(base_url: str = OLLAMA_URL) -> bool:
    try:
        req = urllib.request.urlopen(f"{base_url}/api/tags", timeout=5)
        return req.status == 200
    except Exception:
        return False


def ollama_analyze_build(summary: BuildSummary, base_url: str = OLLAMA_URL) -> str:
    """Analiza el build usando el model-router (con fallback a Ollama directo)."""
    dist = summary.pf_distribution()
    top5 = sorted(summary.strategies, key=lambda s: s.pf, reverse=True)[:5]
    top5_text = "\n".join(
        f"  - {s.name[:40]}: PF={s.pf:.2f}, DD={s.dd_max:.1f}%, "
        f"trades={s.trades_total}, WR={s.win_rate:.1f}%"
        for s in top5
    )

    build_stats = {
        "build_num":        summary.build_num,
        "total_generated":  summary.total_generated,
        "total_in_databank": summary.total_in_databank,
        "approval_rate":    round(summary.approval_rate, 1),
        "pf_max":           round(summary.pf_max, 2),
        "pf_min":           round(summary.pf_min, 2),
        "pf_avg":           round(summary.pf_avg, 2),
        "pf_distribution":  dist,
        "top5":             top5_text,
    }

    prompt = (
        "Eres el build-analyzer de TradingLab. "
        "Analiza estas metricas del build y genera un resumen ejecutivo "
        "en espanol de maximo 200 palabras. "
        "Destaca: calidad general, estrategias mas prometedoras, "
        "patrones detectados, recomendacion para siguiente paso."
    )

    # Usar model-router si está disponible
    if _model_router is not None:
        try:
            return _model_router.route("build_analysis", prompt, context=build_stats)
        except Exception as e:
            pass  # Fallback a Ollama directo

    # Fallback: llamada directa a Ollama
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt + "\n\n" + json.dumps(build_stats, ensure_ascii=False),
        "stream": False,
    }).encode()

    req = urllib.request.Request(
        f"{base_url}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
            data = json.loads(resp.read())
            return data.get("response", "").strip()
    except Exception as e:
        return f"[Error LLM: {e}]"


# ─── Generacion de informe ────────────────────────────────────────────────────

def build_report(summary: BuildSummary, ollama_analysis: str = "") -> str:
    dist = summary.pf_distribution()
    top5 = sorted(summary.strategies, key=lambda s: s.pf, reverse=True)[:5]

    lines = [
        f"# Build Analyzer — Build {summary.build_num}",
        f"",
        f"Fecha: {summary.timestamp}",
        f"",
        f"## Estadisticas del build",
        f"",
        f"| Metrica               | Valor               |",
        f"|-----------------------|---------------------|",
        f"| Total generadas       | {summary.total_generated}           |",
        f"| Total en databank     | {summary.total_in_databank}           |",
        f"| Tasa de aprobacion    | {summary.approval_rate:.1f}%          |",
        f"| PF maximo             | {summary.pf_max:.2f}               |",
        f"| PF minimo             | {summary.pf_min:.2f}               |",
        f"| PF promedio           | {summary.pf_avg:.2f}               |",
        f"",
        f"## Distribucion por rango de PF",
        f"",
        f"| Rango PF | Estrategias |",
        f"|----------|-------------|",
        f"| < 1.3    | {dist['<1.3']}           |",
        f"| 1.3-1.5  | {dist['1.3-1.5']}           |",
        f"| 1.5-1.8  | {dist['1.5-1.8']}           |",
        f"| 1.8-2.0  | {dist['1.8-2.0']}           |",
        f"| >= 2.0   | {dist['>=2.0']}           |",
        f"",
        f"## Top 5 estrategias por PF",
        f"",
    ]

    for i, s in enumerate(top5, 1):
        lines.append(
            f"{i}. **{s.name[:50]}** — PF={s.pf:.2f}, "
            f"DD={s.dd_max:.1f}%, trades={s.trades_total}, "
            f"WR={s.win_rate:.1f}%, tpm={s.trades_per_month:.1f}"
        )

    if ollama_analysis:
        lines += [
            f"",
            f"## Analisis Ollama (deepseek-r1:7b)",
            f"",
            ollama_analysis,
        ]
    else:
        lines += [
            f"",
            f"## Analisis Ollama",
            f"",
            f"_Ollama no disponible — solo estadisticas estaticas generadas._",
        ]

    return "\n".join(lines)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Build Analyzer — TradingLab")
    parser.add_argument(
        "--results-folder",
        type=Path,
        default=Path("results"),
        help="Carpeta con los CSV de resultados (default: results/)",
    )
    parser.add_argument(
        "--build-num",
        type=int,
        default=0,
        help="Numero de build para el informe (default: auto-detectado)",
    )
    parser.add_argument(
        "--no-ollama",
        action="store_true",
        help="Desactivar integracion con Ollama",
    )
    parser.add_argument(
        "--ollama-url",
        default=OLLAMA_URL,
        help=f"URL de Ollama (default: {OLLAMA_URL})",
    )
    args = parser.parse_args()

    results_folder = args.results_folder
    if not results_folder.exists():
        print(f"[ERROR] Carpeta no encontrada: {results_folder}")
        return 1

    print(f"\nBuild Analyzer — TradingLab")
    print(f"Carpeta: {results_folder.resolve()}")
    print(f"{'='*60}")

    # Cargar estrategias
    strategies = scan_results_folder(results_folder)
    if not strategies:
        print("[WARN] No se encontraron estrategias. Generando informe vacio.")

    # Auto-detectar numero de build si no se especifico
    build_num = args.build_num
    if build_num == 0:
        # Buscar en pipeline.lock o usar timestamp
        lock_file = Path("results/pipeline.lock")
        if lock_file.exists():
            parts = lock_file.read_text().strip().split("|")
            if len(parts) >= 5:
                try:
                    build_num = int(parts[4])
                except ValueError:
                    build_num = 0
        if build_num == 0:
            build_num = 99  # Fallback

    summary = BuildSummary(
        build_num=build_num,
        timestamp=datetime.now().isoformat(timespec="seconds"),
        total_generated=len(strategies),
        total_in_databank=len([s for s in strategies if s.pf >= 1.3]),
        strategies=strategies,
    )

    # Intentar Ollama
    ollama_analysis = ""
    if not args.no_ollama:
        print(f"\nVerificando Ollama en {args.ollama_url}...")
        if ollama_available(args.ollama_url):
            print("Ollama disponible. Generando analisis con deepseek-r1:7b...")
            ollama_analysis = ollama_analyze_build(summary, args.ollama_url)
            print("Analisis completado.")
        else:
            print("Ollama no disponible. Continuando sin analisis semantico.")

    # Generar informe
    report = build_report(summary, ollama_analysis)

    # Guardar informe
    output_path = results_folder / f"build-{build_num}-analysis.md"
    output_path.write_text(report, encoding="utf-8")

    # Imprimir resumen en consola
    print(f"\n{'='*60}")
    print(f"BUILD {build_num} — RESUMEN")
    print(f"{'='*60}")
    print(f"Total generadas:     {summary.total_generated}")
    print(f"Total en databank:   {summary.total_in_databank}")
    print(f"Tasa aprobacion:     {summary.approval_rate:.1f}%")
    print(f"PF max/min/avg:      {summary.pf_max:.2f} / {summary.pf_min:.2f} / {summary.pf_avg:.2f}")
    if ollama_analysis:
        print(f"\n--- Analisis Ollama ---")
        print(ollama_analysis[:500] + ("..." if len(ollama_analysis) > 500 else ""))
    print(f"\nInforme guardado en: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
