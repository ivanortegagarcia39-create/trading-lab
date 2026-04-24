#!/usr/bin/env python3
"""
portfolio-builder.py — Construccion automatica del portfolio

Lee evaluation-gate-results.json y selecciona estrategias usando
algoritmo greedy con correlacion simplificada y filtros de diversificacion.

Uso:
    python portfolio-builder.py --eval-results results/evaluation-gate-results.json
    python portfolio-builder.py --max-strategies 8 --min-strategies 3
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Clasificacion de activos por factor de riesgo (skill-pca-portfolio.md)
FACTOR_DOLAR = {
    "EURUSD", "GBPUSD", "AUDUSD", "XAUUSD",
    "NZDUSD", "USDCAD", "USDCHF", "USDJPY",
}
FACTOR_CARRY = {"USDJPY", "GBPJPY", "AUDJPY", "CADJPY", "NZDJPY"}
FACTOR_RISK  = {"US500", "US30", "NAS100", "DE40", "UK100", "JP225"}

MAX_USD_ACTIVOS = 2


def get_factor(activo):
    a = activo.upper().replace("/", "").replace("_", "").replace("-", "")
    if a in FACTOR_RISK:   return "risk"
    if a in FACTOR_CARRY:  return "carry"
    if a in FACTOR_DOLAR:  return "dolar"
    return "other"


def extract_activo(metrics):
    """Intenta extraer el activo del nombre del archivo o del campo activo."""
    filename = metrics.get("file", "")
    # Patron: XAUUSD-B10-... o Strategy_EURUSD_...
    for known in list(FACTOR_DOLAR | FACTOR_CARRY | FACTOR_RISK):
        if known.upper() in filename.upper():
            return known
    return filename.split("-")[0].split("_")[0].upper()


def correlation_estimate(activo1, activo2):
    """Correlacion simplificada sin datos de produccion real."""
    if activo1.upper() == activo2.upper():
        return 0.9
    f1, f2 = get_factor(activo1), get_factor(activo2)
    if f1 == f2 and f1 != "other":
        return 0.6
    return 0.2


def score_strategy(m):
    """
    Score individual segun skill-portfolio-selection.md:
    Score = PF*30 + Sharpe*20 + (1-DD/10)*25 + WinRate*25
    """
    pf     = m.get("pf")     or 1.0
    sharpe = m.get("sharpe") or 0.0
    dd     = m.get("dd")     or 10.0
    wr     = m.get("wr")     or 0.0
    dd_capped = min(dd, 10.0)
    return round(pf * 30 + sharpe * 20 + (1 - dd_capped / 10) * 25 + (wr / 100) * 25, 2)


def combined_dd_estimate(portfolio):
    """
    DD combinado estimado (conservador).
    Suma ponderada con factor de correlacion parcial.
    """
    if not portfolio:
        return 0.0
    dds = [s["metrics"].get("dd") or 0 for s in portfolio]
    # Con correlacion parcial (0.6) el DD combinado es menor que la suma
    return round(sum(dds) * 0.6, 2)


def main():
    parser = argparse.ArgumentParser(
        description="Construccion automatica del portfolio desde EvalGate results"
    )
    parser.add_argument(
        "--eval-results", default="results/evaluation-gate-results.json",
        help="Ruta al JSON del EvalGate (default: results/evaluation-gate-results.json)"
    )
    parser.add_argument(
        "--max-strategies", type=int, default=5,
        help="Maximo de estrategias en el portfolio (default: 5)"
    )
    parser.add_argument(
        "--min-strategies", type=int, default=3,
        help="Minimo requerido para portfolio valido (default: 3)"
    )
    parser.add_argument(
        "--output", default="results/portfolio-selected.json",
        help="Ruta del JSON de salida"
    )
    args = parser.parse_args()

    eval_path = Path(args.eval_results)
    if not eval_path.exists():
        print(f"[ERROR] No se encuentra {eval_path}")
        print("        Ejecutar evaluator-assistant.py primero.")
        sys.exit(1)

    with open(eval_path, encoding="utf-8") as f:
        data = json.load(f)

    candidates = data.get("passed", [])
    if not candidates:
        print("[WARN] No hay estrategias aprobadas en el EvalGate. Portfolio vacio.")
        output = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "portfolio": [],
            "espera":    [],
            "metricas_portfolio": {},
            "estado": "PORTFOLIO_INSUFICIENTE",
        }
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        sys.exit(0)

    # Calcular score y ordenar descendente
    for c in candidates:
        c["score"]  = score_strategy(c["metrics"])
        c["activo"] = extract_activo(c["metrics"])
    candidates.sort(key=lambda x: x["score"], reverse=True)

    portfolio = []
    waiting   = []
    usd_count = 0

    for candidate in candidates:
        if len(portfolio) >= args.max_strategies:
            waiting.append({
                "metrics": candidate["metrics"],
                "score":   candidate["score"],
                "razon":   "Portfolio lleno"
            })
            continue

        activo = candidate["activo"]
        factor = get_factor(activo)

        # Anti-monocultivo USD (max 2 activos Factor Dolar)
        if factor == "dolar" and usd_count >= MAX_USD_ACTIVOS:
            waiting.append({
                "metrics": candidate["metrics"],
                "score":   candidate["score"],
                "razon":   f"Anti-monocultivo USD: ya hay {usd_count} activos Factor Dolar (max {MAX_USD_ACTIVOS})"
            })
            continue

        # Verificar correlacion < 0.5 con las ya incluidas
        max_corr = max(
            (correlation_estimate(activo, s["activo"]) for s in portfolio),
            default=0.0
        )
        if max_corr >= 0.5:
            waiting.append({
                "metrics": candidate["metrics"],
                "score":   candidate["score"],
                "razon":   f"Correlacion estimada {max_corr:.2f} >= 0.5 con estrategia existente"
            })
            continue

        # Verificar DD combinado < 12%
        portfolio.append(candidate)
        cdd = combined_dd_estimate(portfolio)
        if cdd > 12.0:
            portfolio.pop()
            waiting.append({
                "metrics": candidate["metrics"],
                "score":   candidate["score"],
                "razon":   f"DD combinado estimado {cdd:.1f}% > 12%"
            })
            continue

        if factor == "dolar":
            usd_count += 1

    # Pesos HRP simplificados (1/volatilidad proporcional)
    total_inv_dd = sum(1.0 / max(s["metrics"].get("dd") or 1, 0.1) for s in portfolio)
    for s in portfolio:
        dd = max(s["metrics"].get("dd") or 1, 0.1)
        s["peso_hrp"] = round((1.0 / dd) / total_inv_dd, 4) if total_inv_dd > 0 else 0.0

    n = len(portfolio)
    metricas = {
        "estrategias":              n,
        "dd_combinado_estimado":    combined_dd_estimate(portfolio),
        "pf_medio":                 round(sum(s["metrics"].get("pf") or 0 for s in portfolio) / max(n, 1), 3),
        "score_medio":              round(sum(s["score"] for s in portfolio) / max(n, 1), 2),
        "activos_factor_dolar":     usd_count,
    }

    estado = "PORTFOLIO_VALIDO" if n >= args.min_strategies else "PORTFOLIO_INSUFICIENTE"

    output = {
        "timestamp":          datetime.utcnow().isoformat() + "Z",
        "portfolio":          portfolio,
        "espera":             waiting,
        "metricas_portfolio": metricas,
        "estado":             estado,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*40}")
    print(f"PORTFOLIO BUILDER")
    print(f"{'='*40}")
    print(f"Candidatas evaluadas: {len(candidates)}")
    print(f"Incluidas:            {n}")
    print(f"En espera:            {len(waiting)}")
    print(f"DD combinado est.:    {metricas['dd_combinado_estimado']}%")
    print(f"PF medio:             {metricas['pf_medio']}")
    print(f"Estado:               {estado}")
    print(f"Guardado en:          {out_path}")

    if portfolio:
        print("\nPortfolio seleccionado:")
        for s in portfolio:
            m = s["metrics"]
            print(
                f"  {s['activo']:<10} Score {s['score']:<6} "
                f"PF {m.get('pf'):<5} DD {m.get('dd')}% "
                f"Peso HRP {s['peso_hrp']:.2%}"
            )

    if waiting:
        print("\nEn espera:")
        for s in waiting[:5]:
            print(f"  {s['metrics'].get('file',''):<40} → {s['razon']}")


if __name__ == "__main__":
    main()
