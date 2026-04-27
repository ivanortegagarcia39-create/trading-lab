#!/usr/bin/env python3
"""
challenge-simulator.py — Simula resultado de un challenge FTMO con Monte Carlo

Usa los trades del forward test o backtest IS para estimar:
  - Probabilidad de exito (1000 simulaciones, orden aleatorio)
  - Dias estimados para alcanzar objetivo 10%
  - Trades mas peligrosos (mayor DD provocado)
  - Cuenta optima recomendada (10k / 25k / 50k)

Uso:
    python scripts/challenge-simulator.py --strategy-csv trades.csv
    python scripts/challenge-simulator.py --strategy-csv trades.csv --capital 25000 --simulations 1000
"""

import argparse
import csv
import json
import random
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
RESULTS_DIR = ROOT / "results"

DAILY_DD_LIMIT = 0.05   # 5% FTMO
TOTAL_DD_LIMIT = 0.10   # 10% FTMO
PROFIT_TARGET  = 0.10   # 10% objetivo

ACCOUNT_SIZES = [10_000, 25_000, 50_000, 100_000]


def _parse_csv(path: Path) -> list[float]:
    pnls = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = next((k for k in row if "pnl" in k.lower()), None)
            if key is None:
                # Intentar segunda columna
                vals = list(row.values())
                if len(vals) >= 2:
                    try:
                        pnls.append(float(vals[1]))
                    except ValueError:
                        pass
            else:
                try:
                    pnls.append(float(row[key]))
                except ValueError:
                    pass
    return pnls


def _simulate_once(pnls: list[float], capital: float, rng: random.Random) -> dict:
    """
    Simula un challenge con los trades en orden aleatorio.
    Devuelve: result (PASA/FALLA), dias, reason.
    Asume 1 trade = 1 dia para calcular dias minimos (conservador).
    """
    shuffled = pnls[:]
    rng.shuffle(shuffled)

    equity = capital
    peak_equity = capital
    min_equity_day = capital
    trading_days = 0
    balance_midnight = capital
    day_start_equity = capital

    for i, pnl in enumerate(shuffled):
        equity += pnl
        trading_days += 1

        if equity < min_equity_day:
            min_equity_day = equity

        if equity > peak_equity:
            peak_equity = equity

        # DD diario
        if equity < balance_midnight * (1 - DAILY_DD_LIMIT):
            return {"result": "FALLA", "days": trading_days,
                    "final_equity": equity, "reason": "viola_dd_diario"}

        # DD total trailing
        if equity < peak_equity * (1 - TOTAL_DD_LIMIT):
            return {"result": "FALLA", "days": trading_days,
                    "final_equity": equity, "reason": "viola_dd_total"}

        # Objetivo alcanzado
        profit_pct = (equity - capital) / capital
        if profit_pct >= PROFIT_TARGET and trading_days >= 4:
            return {"result": "PASA", "days": trading_days,
                    "final_equity": equity, "reason": "objetivo_alcanzado"}

        balance_midnight = equity

    profit_pct = (equity - capital) / capital
    if profit_pct >= PROFIT_TARGET and trading_days >= 4:
        return {"result": "PASA", "days": trading_days,
                "final_equity": equity, "reason": "objetivo_alcanzado"}

    return {"result": "EN_PROGRESO", "days": trading_days,
            "final_equity": equity, "reason": "trades_insuficientes"}


def _find_dangerous_trades(pnls: list[float], capital: float, top_n: int = 5) -> list[dict]:
    """Identifica los trades que causan mayor DD si ocurren seguidos al inicio."""
    dangerous = []
    for i, pnl in enumerate(pnls):
        if pnl >= 0:
            continue
        dd_pct = abs(pnl) / capital * 100
        dangerous.append({"index": i, "pnl": round(pnl, 2), "dd_pct": round(dd_pct, 4)})

    dangerous.sort(key=lambda x: x["dd_pct"], reverse=True)
    return dangerous[:top_n]


def _recommend_account(pnls: list[float], n_simulations: int, seed: int = 42) -> dict:
    """Evalua que tamaño de cuenta da mayor probabilidad de exito."""
    rng = random.Random(seed)
    recommendations = {}
    for size in ACCOUNT_SIZES:
        wins = sum(
            1 for _ in range(min(n_simulations, 200))
            if _simulate_once(pnls, size, rng)["result"] == "PASA"
        )
        prob = wins / min(n_simulations, 200) * 100
        recommendations[str(size)] = round(prob, 1)

    best = max(recommendations.items(), key=lambda x: x[1])
    return {"by_size": recommendations, "recommended": best[0], "recommended_prob": best[1]}


def run_monte_carlo(pnls: list[float], capital: float,
                    n_simulations: int, seed: int = 42) -> dict:
    rng = random.Random(seed)
    results = [_simulate_once(pnls, capital, rng) for _ in range(n_simulations)]

    passed   = [r for r in results if r["result"] == "PASA"]
    failed   = [r for r in results if r["result"] == "FALLA"]
    progress = [r for r in results if r["result"] == "EN_PROGRESO"]

    prob_exito = len(passed) / n_simulations * 100

    days_passed = [r["days"] for r in passed]
    dias_estimados = round(sum(days_passed) / len(days_passed), 1) if days_passed else None

    fail_reasons: dict[str, int] = {}
    for r in failed:
        k = r.get("reason", "desconocido")
        fail_reasons[k] = fail_reasons.get(k, 0) + 1

    return {
        "n_simulations": n_simulations,
        "capital": capital,
        "prob_exito_pct": round(prob_exito, 2),
        "pasa": len(passed),
        "falla": len(failed),
        "en_progreso": len(progress),
        "dias_estimados": dias_estimados,
        "fail_reasons": fail_reasons,
    }


def main():
    parser = argparse.ArgumentParser(description="Challenge Simulator Monte Carlo — TradingLab")
    parser.add_argument("--strategy-csv", required=True, help="CSV con columna pnl")
    parser.add_argument("--capital", type=float, default=10_000,
                        help="Capital del challenge (default 10000)")
    parser.add_argument("--simulations", type=int, default=1000,
                        help="Numero de simulaciones Monte Carlo (default 1000)")
    parser.add_argument("--strategy-id", default="unknown", help="ID de la estrategia")
    args = parser.parse_args()

    csv_path = Path(args.strategy_csv)
    if not csv_path.exists():
        print(f"ERROR: archivo no encontrado: {csv_path}")
        sys.exit(1)

    pnls = _parse_csv(csv_path)
    if not pnls:
        print("ERROR: no se encontraron trades en el CSV")
        sys.exit(1)

    # Escalar PnLs al capital especificado si el CSV usa capital diferente
    print(f"\nChallenge Simulator — {args.strategy_id}")
    print(f"Trades cargados  : {len(pnls)}")
    print(f"Capital          : ${args.capital:,.0f}")
    print(f"Simulaciones     : {args.simulations}")

    # Monte Carlo principal
    mc = run_monte_carlo(pnls, args.capital, args.simulations)

    # Trades peligrosos
    dangerous = _find_dangerous_trades(pnls, args.capital)

    # Recomendacion de cuenta
    account_rec = _recommend_account(pnls, args.simulations)

    # Veredicto
    prob = mc["prob_exito_pct"]
    if prob >= 80:
        veredicto = "PROCEDER — alta probabilidad de exito"
    elif prob >= 70:
        veredicto = "PROCEDER CON CAUTELA — probabilidad aceptable"
    elif prob >= 50:
        veredicto = "REVISION NECESARIA — probabilidad insuficiente"
    else:
        veredicto = "NO PROCEDER — probabilidad de exito muy baja"

    print(f"\n{'='*55}")
    print(f"  RESULTADO MONTE CARLO ({args.simulations} simulaciones)")
    print(f"{'='*55}")
    print(f"  Probabilidad exito : {prob:.1f}%")
    print(f"  Pasa               : {mc['pasa']}")
    print(f"  Falla              : {mc['falla']}")
    print(f"  En progreso        : {mc['en_progreso']}")
    print(f"  Dias estimados     : {mc['dias_estimados'] or 'N/A'}")
    if mc["fail_reasons"]:
        for reason, count in mc["fail_reasons"].items():
            print(f"  Fallo por {reason:<20}: {count}")
    print(f"\n  Veredicto : {veredicto}")

    print(f"\n  Trades mas peligrosos:")
    for t in dangerous:
        print(f"    Trade #{t['index']+1}: ${t['pnl']:,.2f} ({t['dd_pct']:.2f}% DD)")

    print(f"\n  Cuenta recomendada: ${int(account_rec['recommended']):,} "
          f"({account_rec['recommended_prob']:.1f}% exito)")
    for size, prob_s in account_rec["by_size"].items():
        print(f"    ${int(size):>8,}: {prob_s:.1f}%")
    print(f"{'='*55}")

    # Guardar resultado
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "strategy_id": args.strategy_id,
        "timestamp": datetime.now().isoformat(),
        "capital": args.capital,
        "n_trades": len(pnls),
        "monte_carlo": mc,
        "probabilidad_exito_pct": prob,
        "dias_estimados": mc["dias_estimados"],
        "trades_peligrosos": dangerous,
        "cuenta_recomendada": account_rec["recommended"],
        "cuenta_recomendada_prob": account_rec["recommended_prob"],
        "cuenta_por_tamaño": account_rec["by_size"],
        "veredicto": veredicto,
    }
    out_path = RESULTS_DIR / f"challenge-simulation-{args.strategy_id}.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResultado guardado: {out_path}")


if __name__ == "__main__":
    main()
