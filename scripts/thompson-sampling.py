#!/usr/bin/env python3
"""
thompson-sampling.py — Selección óptima de activos y estrategias via Thompson Sampling.

Cada par (activo, timeframe) tiene una distribución Beta(α, β) que representa
la probabilidad de producir builds exitosos. El sistema aprende y prioriza.

Uso:
    python scripts/thompson-sampling.py --rankings
    python scripts/thompson-sampling.py --next-asset
    python scripts/thompson-sampling.py --update-asset XAUUSD H1 true
    python scripts/thompson-sampling.py --update-strategy STRAT001 true
    python scripts/thompson-sampling.py --allocations
"""

import argparse
import io
import json
import math
import random
import sys
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT        = Path(__file__).parent.parent
STATE_PATH  = ROOT / "results" / "thompson-state.json"

# Activos del universo (de CLAUDE.md)
UNIVERSE = [
    ("EURUSD", "H1"), ("GBPUSD", "H1"), ("USDJPY", "H1"), ("USDCHF", "H1"),
    ("AUDUSD", "H1"), ("NZDUSD", "H1"), ("USDCAD", "H1"),
    ("EURGBP", "H1"), ("EURJPY", "H1"), ("GBPJPY", "H1"), ("EURAUD", "H1"),
    ("EURCHF", "H1"), ("AUDJPY", "H1"), ("GBPAUD", "H1"), ("CADJPY", "H1"),
    ("NZDJPY", "H1"),
    ("XAUUSD", "H1"), ("XAGUSD", "H1"),
    ("US30",   "H1"), ("US500",  "H1"), ("NAS100", "H1"),
    ("DE40",   "H1"), ("UK100",  "H1"), ("JP225",  "H1"),
]

MIN_BUILDS_FOR_THOMPSON = 3  # mínimo de builds por activo para usar Thompson


# ─── I/O de estado ────────────────────────────────────────────────────────────

def _load_state() -> dict:
    if not STATE_PATH.exists():
        return _initial_state()
    with open(STATE_PATH, encoding="utf-8") as f:
        return json.load(f)


def _initial_state() -> dict:
    assets = {}
    for activo, tf in UNIVERSE:
        key = f"{activo}_{tf}"
        assets[key] = {"activo": activo, "tf": tf, "alpha": 1, "beta": 1,
                        "builds": 0, "last_updated": None}
    return {"assets": assets, "strategies": {}}


def _save_state(state: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ─── Beta sampling ────────────────────────────────────────────────────────────

def _beta_sample(alpha: float, beta: float) -> float:
    """Muestra de distribución Beta(α, β) usando método de Johnk."""
    # Python random.betavariate está disponible en stdlib
    return random.betavariate(alpha, beta)


def _beta_mean(alpha: float, beta: float) -> float:
    return alpha / (alpha + beta)


def _beta_std(alpha: float, beta: float) -> float:
    n = alpha + beta
    return math.sqrt(alpha * beta / (n * n * (n + 1)))


# ─── Funciones principales ────────────────────────────────────────────────────

def sample_next_asset(exclude_in_progress: list | None = None) -> dict:
    """
    Muestrea de Beta(α+1, β+1) para cada activo y devuelve el de mayor muestra.
    Solo usa Thompson si hay >= MIN_BUILDS_FOR_THOMPSON builds en algún activo.
    """
    state  = _load_state()
    assets = state["assets"]
    excl   = set(exclude_in_progress or [])

    # Verificar si hay suficientes datos para Thompson
    max_builds = max((a["builds"] for a in assets.values()), default=0)
    if max_builds < MIN_BUILDS_FOR_THOMPSON:
        # Sin suficientes datos → devolver el primero no excluido con builds=0
        for key, a in assets.items():
            if a["activo"] not in excl:
                return {
                    "activo": a["activo"], "tf": a["tf"],
                    "method": "fifo", "reason": f"Datos insuficientes (max_builds={max_builds})"
                }

    # Thompson Sampling: muestrear de Beta para cada activo
    best_key    = None
    best_sample = -1.0
    for key, a in assets.items():
        if a["activo"] in excl:
            continue
        sample = _beta_sample(a["alpha"], a["beta"])
        if sample > best_sample:
            best_sample = sample
            best_key    = key

    if not best_key:
        return {"activo": None, "tf": None, "method": "none", "reason": "Todos excluidos"}

    a = assets[best_key]
    return {
        "activo":  a["activo"],
        "tf":      a["tf"],
        "sample":  round(best_sample, 4),
        "mean":    round(_beta_mean(a["alpha"], a["beta"]), 4),
        "alpha":   a["alpha"],
        "beta":    a["beta"],
        "builds":  a["builds"],
        "method":  "thompson",
    }


def update_asset_outcome(activo: str, tf: str, success: bool):
    """Actualiza α o β según el resultado del build."""
    state = _load_state()
    key   = f"{activo}_{tf}"

    if key not in state["assets"]:
        state["assets"][key] = {
            "activo": activo, "tf": tf, "alpha": 1, "beta": 1,
            "builds": 0, "last_updated": None
        }

    a = state["assets"][key]
    if success:
        a["alpha"] += 1
    else:
        a["beta"] += 1
    a["builds"]       += 1
    a["last_updated"]  = datetime.now().isoformat()

    _save_state(state)
    mean = _beta_mean(a["alpha"], a["beta"])
    outcome_str = "ÉXITO" if success else "FALLO"
    print(f"  {activo}/{tf} [{outcome_str}]: α={a['alpha']} β={a['beta']} "
          f"media={mean:.3f} builds={a['builds']}")


def update_strategy_outcome(strategy_id: str, success: bool):
    """Actualiza la distribución Beta de una estrategia activa."""
    state = _load_state()
    if strategy_id not in state["strategies"]:
        state["strategies"][strategy_id] = {
            "alpha": 1, "beta": 1, "weeks": 0, "last_updated": None
        }

    s = state["strategies"][strategy_id]
    if success:
        s["alpha"] += 1
    else:
        s["beta"] += 1
    s["weeks"]       += 1
    s["last_updated"]  = datetime.now().isoformat()

    _save_state(state)
    mean = _beta_mean(s["alpha"], s["beta"])
    print(f"  {strategy_id}: α={s['alpha']} β={s['beta']} media={mean:.3f}")


def sample_strategy_allocation(portfolio_strategies: list[str]) -> dict:
    """
    Muestrea de Beta de cada estrategia y devuelve pesos normalizados.
    """
    state   = _load_state()
    samples = {}
    for sid in portfolio_strategies:
        if sid in state["strategies"]:
            s = state["strategies"][sid]
            samples[sid] = _beta_sample(s["alpha"], s["beta"])
        else:
            samples[sid] = _beta_sample(1, 1)  # prior no informativo

    total = sum(samples.values())
    if total == 0:
        n = len(portfolio_strategies)
        return {sid: round(1.0 / n, 4) for sid in portfolio_strategies}

    return {sid: round(v / total, 4) for sid, v in samples.items()}


def get_asset_rankings() -> list:
    """Lista activos ordenados por media posterior Beta."""
    state  = _load_state()
    ranked = []
    for key, a in state["assets"].items():
        mean = _beta_mean(a["alpha"], a["beta"])
        std  = _beta_std(a["alpha"], a["beta"])
        conf = a["alpha"] + a["beta"]
        ranked.append({
            "activo":     a["activo"],
            "tf":         a["tf"],
            "mean":       round(mean, 4),
            "std":        round(std, 4),
            "alpha":      a["alpha"],
            "beta":       a["beta"],
            "builds":     a["builds"],
            "confidence": conf,
        })
    ranked.sort(key=lambda x: x["mean"], reverse=True)
    return ranked


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Thompson Sampling — TradingLab")
    parser.add_argument("--next-asset",      action="store_true",
                        help="Sugerir próximo activo a buildear")
    parser.add_argument("--rankings",        action="store_true",
                        help="Ver rankings de activos por media posterior")
    parser.add_argument("--update-asset",    nargs=3,
                        metavar=("ACTIVO", "TF", "SUCCESS"),
                        help="Actualizar resultado de build (true/false)")
    parser.add_argument("--update-strategy", nargs=2,
                        metavar=("STRATEGY_ID", "SUCCESS"),
                        help="Actualizar resultado semanal de estrategia")
    parser.add_argument("--allocations",     nargs="+", metavar="STRATEGY_ID",
                        help="Ver allocations sugeridas para lista de estrategias")
    parser.add_argument("--exclude",         nargs="*", default=[],
                        help="Activos a excluir de --next-asset")
    args = parser.parse_args()

    if args.next_asset:
        result = sample_next_asset(exclude_in_progress=args.exclude)
        print(f"\nPróximo activo sugerido: {result.get('activo')} ({result.get('tf')})")
        print(f"  Método: {result.get('method')}")
        if result.get("method") == "thompson":
            print(f"  Media posterior: {result.get('mean')}  "
                  f"Muestra: {result.get('sample')}  Builds: {result.get('builds')}")
        else:
            print(f"  Razón: {result.get('reason')}")

    elif args.rankings:
        rankings = get_asset_rankings()
        print(f"\nRankings de activos (Thompson Sampling — {len(rankings)} activos):")
        print(f"{'Activo':<10} {'TF':<5} {'Media':>6} {'Builds':>7} {'α':>4} {'β':>4} {'Conf':>5}")
        print("-" * 50)
        for r in rankings[:15]:
            star = " *" if r["builds"] == 0 else ""
            print(f"  {r['activo']:<10} {r['tf']:<5} {r['mean']:>6.4f} "
                  f"{r['builds']:>7}  {r['alpha']:>3}  {r['beta']:>3}  {r['confidence']:>4}{star}")
        if len(rankings) > 15:
            print(f"  ... y {len(rankings) - 15} más")
        print("  (* = sin builds aún)")

    elif args.update_asset:
        activo, tf, success_str = args.update_asset
        success = success_str.lower() in ("true", "1", "yes", "si", "sí")
        update_asset_outcome(activo.upper(), tf.upper(), success)

    elif args.update_strategy:
        sid, success_str = args.update_strategy
        success = success_str.lower() in ("true", "1", "yes", "si", "sí")
        update_strategy_outcome(sid, success)

    elif args.allocations:
        allocs = sample_strategy_allocation(args.allocations)
        print("\nAllocations sugeridas:")
        for sid, weight in sorted(allocs.items(), key=lambda x: x[1], reverse=True):
            bar = "#" * int(weight * 40)
            print(f"  {sid:<20} {weight:.4f}  {bar}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
