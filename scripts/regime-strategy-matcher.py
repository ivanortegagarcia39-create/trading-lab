#!/usr/bin/env python3
"""
regime-strategy-matcher.py — Conecta el régimen de mercado actual
con las estrategias más adecuadas para ese régimen.

Una estrategia generada en tendencia-altavol puede fallar en rango-bajovol.
Este script aprende qué estrategias funcionan mejor en cada régimen.

Uso:
    python scripts/regime-strategy-matcher.py --recommend
    python scripts/regime-strategy-matcher.py --best-for tendencia-altavol
    python scripts/regime-strategy-matcher.py --compatibility STRAT001
    python scripts/regime-strategy-matcher.py --record STRAT001 tendencia-altavol 1.85
"""

import argparse
import io
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT        = Path(__file__).parent.parent
PERF_PATH   = ROOT / "results" / "regime-performance.json"

REGIMES = [
    "tendencia-altavol",
    "tendencia-bajovol",
    "rango-altavol",
    "rango-bajovol",
]

MIN_OBS_FOR_RECOMMENDATION = 3  # observaciones mínimas para recomendar

_PYTHON = sys.executable


# ─── I/O ──────────────────────────────────────────────────────────────────────

def _load_perf() -> dict:
    if not PERF_PATH.exists():
        return {}
    with open(PERF_PATH, encoding="utf-8") as f:
        return json.load(f)


def _save_perf(data: dict):
    PERF_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PERF_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ─── Funciones principales ────────────────────────────────────────────────────

def record_regime_performance(strategy_id: str, regime: str, week_pf: float):
    """Registra el PF de una estrategia en un régimen específico."""
    if regime not in REGIMES:
        print(f"ERROR: régimen '{regime}' no válido. Opciones: {REGIMES}")
        sys.exit(1)

    data = _load_perf()
    if strategy_id not in data:
        data[strategy_id] = {r: [] for r in REGIMES}

    data[strategy_id][regime].append({
        "pf":        round(week_pf, 4),
        "timestamp": datetime.now().isoformat(),
    })
    _save_perf(data)

    obs = len(data[strategy_id][regime])
    print(f"  Registrado: {strategy_id} en {regime} → PF={week_pf:.4f}  (obs={obs})")


def get_best_strategies_for_regime(regime: str) -> list[dict]:
    """Devuelve estrategias ordenadas por PF medio en el régimen dado."""
    if regime not in REGIMES:
        print(f"ERROR: régimen '{regime}' no válido.")
        return []

    data    = _load_perf()
    results = []

    for sid, regimes in data.items():
        obs = regimes.get(regime, [])
        if len(obs) < MIN_OBS_FOR_RECOMMENDATION:
            continue
        pf_values = [o["pf"] for o in obs]
        mean_pf   = sum(pf_values) / len(pf_values)
        results.append({
            "strategy_id": sid,
            "mean_pf":     round(mean_pf, 4),
            "obs":         len(obs),
            "min_pf":      round(min(pf_values), 4),
            "max_pf":      round(max(pf_values), 4),
        })

    results.sort(key=lambda x: x["mean_pf"], reverse=True)
    return results


def get_regime_compatibility(strategy_id: str) -> dict:
    """Para una estrategia, muestra su PF medio en cada régimen."""
    data = _load_perf()
    if strategy_id not in data:
        return {"strategy_id": strategy_id, "status": "SIN_DATOS"}

    compat = {"strategy_id": strategy_id, "regimes": {}}
    best_regime, best_pf = None, -999.0
    worst_regime, worst_pf = None, 999.0

    for regime in REGIMES:
        obs = data[strategy_id].get(regime, [])
        if not obs:
            compat["regimes"][regime] = {"mean_pf": None, "obs": 0}
            continue
        pf_values = [o["pf"] for o in obs]
        mean_pf   = sum(pf_values) / len(pf_values)
        compat["regimes"][regime] = {"mean_pf": round(mean_pf, 4), "obs": len(obs)}
        if mean_pf > best_pf:
            best_pf, best_regime = mean_pf, regime
        if mean_pf < worst_pf:
            worst_pf, worst_regime = mean_pf, regime

    compat["best_regime"]  = best_regime
    compat["worst_regime"] = worst_regime
    return compat


def _get_current_regime() -> str | None:
    """Detecta el régimen actual via market-regime-snapshot."""
    snapshot = ROOT / "scripts" / "market-regime-snapshot.py"
    if not snapshot.exists():
        return None
    try:
        result = subprocess.run(
            [_PYTHON, str(snapshot), "--current"],
            capture_output=True, text=True, timeout=10,
        )
        out = result.stdout.strip()
        for r in REGIMES:
            if r in out.lower():
                return r
        # Intentar parsear JSON si lo devuelve
        if out.startswith("{"):
            import json as _json
            d = _json.loads(out)
            regime = d.get("regime", d.get("nombre", ""))
            if regime in REGIMES:
                return regime
    except Exception:
        pass

    # Fallback: leer último snapshot guardado
    snap_file = ROOT / "results" / "regime-snapshot-current.json"
    if snap_file.exists():
        try:
            with open(snap_file, encoding="utf-8") as f:
                d = json.load(f)
            regime = d.get("regime", d.get("nombre", ""))
            if regime in REGIMES:
                return regime
        except Exception:
            pass

    return None


def recommend_for_current_regime() -> dict:
    """Detecta el régimen actual y recomienda las estrategias más adecuadas."""
    regime = _get_current_regime()
    if not regime:
        print("Régimen actual: no detectado")
        print("  Ejecuta market-regime-snapshot para registrar el régimen actual.")
        return {"status": "SIN_REGIMEN"}

    print(f"Régimen actual: {regime}")
    best = get_best_strategies_for_regime(regime)

    if not best:
        print(f"  Sin datos suficientes para {regime} (mínimo {MIN_OBS_FOR_RECOMMENDATION} obs).")
        return {"status": "SIN_DATOS", "regime": regime}

    print(f"\nMejores estrategias para {regime}:")
    print(f"  {'Estrategia':<25} {'PF medio':>8}  {'Obs':>4}  Rango")
    print("  " + "-" * 55)
    for r in best[:5]:
        print(f"  {r['strategy_id']:<25} {r['mean_pf']:>8.4f}  {r['obs']:>4}  "
              f"[{r['min_pf']:.3f} – {r['max_pf']:.3f}]")

    return {"status": "OK", "regime": regime, "recommendations": best[:5]}


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Regime-Strategy Matcher — TradingLab")
    parser.add_argument("--record",        nargs=3,
                        metavar=("STRATEGY_ID", "REGIME", "WEEK_PF"),
                        help="Registrar PF semanal de estrategia en régimen")
    parser.add_argument("--best-for",      metavar="REGIME",
                        help="Mejores estrategias para un régimen")
    parser.add_argument("--compatibility", metavar="STRATEGY_ID",
                        help="Compatibilidad de una estrategia con cada régimen")
    parser.add_argument("--recommend",     action="store_true",
                        help="Recomendar estrategias para el régimen actual")
    args = parser.parse_args()

    if args.record:
        sid, regime, pf_str = args.record
        try:
            week_pf = float(pf_str)
        except ValueError:
            print(f"ERROR: WEEK_PF debe ser un número, recibido: {pf_str}")
            sys.exit(1)
        record_regime_performance(sid, regime, week_pf)

    elif args.best_for:
        results = get_best_strategies_for_regime(args.best_for)
        if not results:
            print(f"Sin estrategias con suficientes datos para {args.best_for} "
                  f"(mínimo {MIN_OBS_FOR_RECOMMENDATION} obs).")
        else:
            print(f"\nMejores estrategias para régimen '{args.best_for}':")
            print(f"  {'Estrategia':<25} {'PF medio':>8}  {'Obs':>4}")
            print("  " + "-" * 42)
            for r in results:
                print(f"  {r['strategy_id']:<25} {r['mean_pf']:>8.4f}  {r['obs']:>4}")

    elif args.compatibility:
        compat = get_regime_compatibility(args.compatibility)
        if compat.get("status") == "SIN_DATOS":
            print(f"Sin datos para {args.compatibility}.")
        else:
            print(f"\nCompatibilidad de {args.compatibility}:")
            for regime, info in compat.get("regimes", {}).items():
                pf_str = f"{info['mean_pf']:.4f}" if info["mean_pf"] is not None else "N/A"
                marker = " <-- MEJOR" if regime == compat.get("best_regime") else \
                         " <-- PEOR"  if regime == compat.get("worst_regime") else ""
                print(f"  {regime:<22} PF={pf_str:>8}  obs={info['obs']}{marker}")

    elif args.recommend:
        recommend_for_current_regime()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
