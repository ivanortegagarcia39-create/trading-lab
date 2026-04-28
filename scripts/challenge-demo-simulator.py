"""
AutoDemoPipeline v3.0 — Motor de simulacion de challenge en demo.
Simula reglas exactas de prop firms tick a tick sobre trades historicos.
"""
import argparse
import csv
import json
import os
import sys
from datetime import datetime, date, timedelta
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "propfirm-rules.json"
RESULTS_DIR = Path(__file__).parent.parent / "results"

# Margen de seguridad del 20% sobre los limites reales
SAFETY_MARGIN = 0.20


def load_propfirm_rules(propfirm_id: str) -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        all_rules = json.load(f)
    if propfirm_id not in all_rules:
        raise ValueError(f"Prop firm '{propfirm_id}' no encontrada en {CONFIG_PATH}")
    return all_rules[propfirm_id]


def load_trades(trades_csv: str) -> list[dict]:
    """Carga trades desde CSV con columnas: timestamp, pnl, balance"""
    trades = []
    with open(trades_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            trades.append({
                "timestamp": datetime.fromisoformat(row["timestamp"]),
                "pnl": float(row["pnl"]),
                "balance": float(row["balance"]),
            })
    trades.sort(key=lambda x: x["timestamp"])
    return trades


def apply_safety_margin(rules: dict) -> dict:
    """Aplica margen de seguridad del 20% a los limites de DD."""
    safe = dict(rules)
    safe["daily_dd_limit_pct"] = rules["daily_dd_limit_pct"] * (1 - SAFETY_MARGIN)
    safe["max_dd_limit_pct"] = rules["max_dd_limit_pct"] * (1 - SAFETY_MARGIN)
    return safe


def simulate_phase(trades: list[dict], phase_rules: dict, phase_name: str,
                   capital: float) -> dict:
    """
    Simula una fase del challenge tick a tick.
    Retorna dict con veredicto PASS/FAIL/TIMEOUT y metricas completas.
    """
    safe_rules = apply_safety_margin(phase_rules)

    initial_balance = capital
    current_balance = capital
    peak_balance = capital  # para DD dinamico

    profit_target = capital * (phase_rules["profit_target_pct"] / 100)
    daily_dd_limit = initial_balance * (safe_rules["daily_dd_limit_pct"] / 100)
    total_dd_limit = initial_balance * (safe_rules["max_dd_limit_pct"] / 100)
    dd_type = phase_rules["dd_type"]

    trading_days: set[date] = set()
    max_daily_dd = 0.0
    max_total_dd = 0.0
    timeout_days = phase_rules["simulation_timeout_days"]

    if not trades:
        return _build_result(phase_name, "FAIL", "Sin trades disponibles",
                             0, 0.0, 0.0, 0.0, 0, capital, capital)

    start_date = trades[0]["timestamp"].date()
    last_date = trades[-1]["timestamp"].date()
    elapsed_days = (last_date - start_date).days

    day_open_balance: dict[date, float] = {}

    for trade in trades:
        trade_date = trade["timestamp"].date()
        elapsed = (trade_date - start_date).days

        if elapsed > timeout_days:
            return _build_result(phase_name, "TIMEOUT",
                                 f"Superado timeout de {timeout_days} dias sin completar objetivo",
                                 len(trading_days), current_balance - initial_balance,
                                 max_daily_dd, max_total_dd, elapsed, capital, current_balance)

        if trade_date not in day_open_balance:
            day_open_balance[trade_date] = current_balance

        current_balance += trade["pnl"]
        trading_days.add(trade_date)

        # DD diario (desde balance de apertura del dia)
        day_dd = day_open_balance[trade_date] - current_balance
        if day_dd > max_daily_dd:
            max_daily_dd = day_dd
        if day_dd > daily_dd_limit:
            cause = (f"DD diario {day_dd:.2f} supera limite seguro "
                     f"{daily_dd_limit:.2f} ({safe_rules['daily_dd_limit_pct']:.1f}%)")
            return _build_result(phase_name, "FAIL", cause,
                                 len(trading_days), current_balance - initial_balance,
                                 max_daily_dd, max_total_dd, elapsed, capital, current_balance)

        # DD total
        if dd_type == "dynamic":
            if current_balance > peak_balance:
                peak_balance = current_balance
            total_dd = peak_balance - current_balance
        else:
            total_dd = initial_balance - current_balance

        if total_dd > max_total_dd:
            max_total_dd = total_dd
        if total_dd > total_dd_limit:
            cause = (f"DD total {total_dd:.2f} supera limite seguro "
                     f"{total_dd_limit:.2f} ({safe_rules['max_dd_limit_pct']:.1f}%)")
            return _build_result(phase_name, "FAIL", cause,
                                 len(trading_days), current_balance - initial_balance,
                                 max_daily_dd, max_total_dd, elapsed, capital, current_balance)

        # Verificar objetivo alcanzado
        profit = current_balance - initial_balance
        if profit >= profit_target:
            trading_days_count = len(trading_days)
            min_days = phase_rules.get("min_trading_days", 0)
            if trading_days_count < min_days:
                continue  # objetivo alcanzado pero faltan dias minimos
            return _build_result(phase_name, "PASS", "Objetivo alcanzado",
                                 trading_days_count, profit,
                                 (max_daily_dd / initial_balance) * 100,
                                 (max_total_dd / initial_balance) * 100,
                                 elapsed, capital, current_balance)

    # Fin de trades sin alcanzar objetivo
    profit = current_balance - initial_balance
    if profit >= profit_target and len(trading_days) >= phase_rules.get("min_trading_days", 0):
        return _build_result(phase_name, "PASS", "Objetivo alcanzado al final",
                             len(trading_days), profit,
                             (max_daily_dd / initial_balance) * 100,
                             (max_total_dd / initial_balance) * 100,
                             elapsed_days, capital, current_balance)

    return _build_result(phase_name, "TIMEOUT",
                         f"Trades agotados sin alcanzar objetivo. Profit: {profit:.2f}",
                         len(trading_days), profit,
                         (max_daily_dd / initial_balance) * 100,
                         (max_total_dd / initial_balance) * 100,
                         elapsed_days, capital, current_balance)


def _build_result(phase_name, verdict, cause, trading_days, profit,
                  max_daily_dd_pct, max_total_dd_pct, elapsed_days,
                  initial_capital, final_balance) -> dict:
    profit_pct = (profit / initial_capital) * 100 if initial_capital > 0 else 0
    return {
        "phase": phase_name,
        "verdict": verdict,
        "cause": cause,
        "trading_days": trading_days,
        "profit": round(profit, 2),
        "profit_pct": round(profit_pct, 2),
        "max_daily_dd_pct": round(max_daily_dd_pct, 2),
        "max_total_dd_pct": round(max_total_dd_pct, 2),
        "elapsed_days": elapsed_days,
        "initial_capital": initial_capital,
        "final_balance": round(final_balance, 2),
    }


def calculate_pf(trades: list[dict]) -> float:
    """Calcula Profit Factor del conjunto de trades."""
    gross_profit = sum(t["pnl"] for t in trades if t["pnl"] > 0)
    gross_loss = abs(sum(t["pnl"] for t in trades if t["pnl"] < 0))
    if gross_loss == 0:
        return 999.0
    return round(gross_profit / gross_loss, 3)


def calculate_score(phase1: dict, phase2: dict, pf: float, timeout_days: int) -> int:
    """Calcula Score Final 0-100."""
    score = 0

    # Profit alcanzado (30 pts): promedio de ambas fases
    p1_ratio = min(phase1["profit_pct"] / 10.0, 1.0)
    p2_ratio = min(phase2["profit_pct"] / 5.0, 1.0)
    score += int(((p1_ratio + p2_ratio) / 2) * 30)

    # DD diario max fase 1 (20 pts)
    dd_limit = 4.0
    dd1_score = max(0, (1 - phase1["max_daily_dd_pct"] / dd_limit)) * 20
    score += int(dd1_score)

    # DD diario max fase 2 (20 pts)
    dd2_score = max(0, (1 - phase2["max_daily_dd_pct"] / dd_limit)) * 20
    score += int(dd2_score)

    # PF del periodo (20 pts)
    pf_score = min(pf / 1.5, 1.0) * 20
    score += int(pf_score)

    # Dias usados (10 pts): eficiencia
    total_days = phase1["elapsed_days"] + phase2["elapsed_days"]
    days_score = max(0, (1 - total_days / (timeout_days * 2))) * 10
    score += int(days_score)

    return min(score, 100)


def simulate_full_challenge(trades_csv: str, propfirm_id: str,
                            strategy_id: str, capital: float,
                            output_dir: str) -> dict:
    rules = load_propfirm_rules(propfirm_id)
    trades = load_trades(trades_csv)

    phase1 = simulate_phase(trades, rules["challenge"], "challenge", capital)

    if phase1["verdict"] != "PASS":
        final_verdict = phase1["verdict"]
        phase2 = {"phase": "verification", "verdict": "NO_EJECUTADA",
                  "cause": "Fase 1 no superada", "trading_days": 0,
                  "profit": 0.0, "profit_pct": 0.0, "max_daily_dd_pct": 0.0,
                  "max_total_dd_pct": 0.0, "elapsed_days": 0,
                  "initial_capital": capital, "final_balance": capital}
        pf = calculate_pf(trades)
        score = 0
    else:
        # Fase 2 con balance resultante de fase 1
        capital_f2 = phase1["final_balance"]
        phase2 = simulate_phase(trades, rules["verification"], "verification", capital_f2)
        pf = calculate_pf(trades)

        if phase2["verdict"] == "PASS":
            final_verdict = "PASS"
        else:
            final_verdict = phase2["verdict"]

        score = calculate_score(phase1, phase2, pf,
                                rules["challenge"]["simulation_timeout_days"])

    result = {
        "strategy_id": strategy_id,
        "propfirm_id": propfirm_id,
        "propfirm_name": rules["name"],
        "capital": capital,
        "simulation_date": datetime.now().isoformat(),
        "trades_csv": trades_csv,
        "final_verdict": final_verdict,
        "profit_factor": pf,
        "score": score,
        "phase1": phase1,
        "phase2": phase2,
    }

    # Guardar resultado
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    sim_date = datetime.now().strftime("%Y%m%d")
    filename = f"challenge-sim-{strategy_id}-{sim_date}.json"
    filepath = output_path / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Resultado guardado en: {filepath}")

    return result


def generate_telegram_message(result: dict) -> str:
    """Genera el mensaje de autorizacion para Telegram."""
    p1 = result["phase1"]
    p2 = result["phase2"]
    verdict = result["final_verdict"]

    if verdict == "PASS":
        header = "CHALLENGE SIMULADO SUPERADO"
    elif verdict == "FAIL":
        header = "CHALLENGE SIMULADO FALLADO"
    else:
        header = f"CHALLENGE SIMULADO — {verdict}"

    msg = f"""{header}

Estrategia: {result['strategy_id']}
Prop Firm:  {result['propfirm_name']} | Cuenta: {result['capital']:,.0f} USD

Fase 1 — Challenge:
  Duracion:      {p1['trading_days']} dias de trading
  Profit:        +{p1['profit_pct']:.1f}%
  DD Diario Max: {p1['max_daily_dd_pct']:.1f}%
  DD Total Max:  {p1['max_total_dd_pct']:.1f}%
  Resultado:     {p1['verdict']}"""

    if p2["verdict"] != "NO_EJECUTADA":
        msg += f"""

Fase 2 — Verification:
  Duracion:      {p2['trading_days']} dias de trading
  Profit:        +{p2['profit_pct']:.1f}%
  DD Diario Max: {p2['max_daily_dd_pct']:.1f}%
  DD Total Max:  {p2['max_total_dd_pct']:.1f}%
  Resultado:     {p2['verdict']}"""

    msg += f"""

PF del periodo: {result['profit_factor']:.2f}
Score Final:    {result['score']}/100"""

    if verdict == "PASS":
        msg += "\n\nAutorizar compra del challenge?\nResponder SI para confirmar."
    elif verdict == "FAIL":
        msg += f"\n\nCausa del fallo: {p1['cause'] if p1['verdict'] == 'FAIL' else p2['cause']}"

    return msg


def main():
    parser = argparse.ArgumentParser(description="AutoDemoPipeline v3.0 — Simulacion de challenge")
    parser.add_argument("--trades-csv", required=True, help="CSV con trades del forward test")
    parser.add_argument("--propfirm", required=True,
                        choices=["ftmo_2step", "e8_funding", "brightfunded"],
                        help="ID de la prop firm")
    parser.add_argument("--strategy-id", required=True, help="ID de la estrategia")
    parser.add_argument("--capital", type=float, default=10000.0,
                        help="Tamano de la cuenta (default 10000)")
    parser.add_argument("--output", default=str(RESULTS_DIR),
                        help="Carpeta de salida para el resultado JSON")
    args = parser.parse_args()

    result = simulate_full_challenge(
        trades_csv=args.trades_csv,
        propfirm_id=args.propfirm,
        strategy_id=args.strategy_id,
        capital=args.capital,
        output_dir=args.output,
    )

    msg = generate_telegram_message(result)
    print("\n" + "=" * 60)
    print(msg)
    print("=" * 60)

    sys.exit(0 if result["final_verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
