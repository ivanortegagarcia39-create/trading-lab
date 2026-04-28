#!/usr/bin/env python3
"""
concept-drift-detector.py — Detección de cambios de régimen y drift del mercado.

BOCPD: detecta cambios abruptos de régimen (distribución Normal conjugada).
ADDM: detecta drift gradual en las predicciones del sistema (residuales PF).

Uso:
    python scripts/concept-drift-detector.py --check
    python scripts/concept-drift-detector.py --report
    python scripts/concept-drift-detector.py --update-bocpd 0.012 0.008 -0.005 0.015 ...
    python scripts/concept-drift-detector.py --update-addm STRAT001 1.8 1.4
"""

import argparse
import io
import json
import math
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT        = Path(__file__).parent.parent
STATE_PATH  = ROOT / "results" / "drift-detection.json"
SCRIPTS_DIR = ROOT / "scripts"

BOCPD_WINDOW      = 50    # retornos en ventana deslizante
BOCPD_HAZARD_RATE = 0.01  # probabilidad a priori de cambio en cada paso
ADDM_CONSEC_WARN  = 3     # periodos consecutivos para DRIFT_DETECTED

import sys as _sys
_PYTHON = _sys.executable


# ─── I/O de estado ────────────────────────────────────────────────────────────

def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {
            "bocpd": {
                "returns_window": [],
                "change_points":  [],
                "last_prob":      0.0,
                "last_updated":   None,
            },
            "addm": {},
        }
    with open(STATE_PATH) as f:
        return json.load(f)


def _save_state(state: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


# ─── BOCPD (distribución Normal conjugada) ────────────────────────────────────

def _normal_pdf(x: float, mu: float, sigma2: float) -> float:
    """Densidad de distribución Normal."""
    if sigma2 <= 0:
        return 1e-300
    return (1.0 / math.sqrt(2 * math.pi * sigma2)) * math.exp(-0.5 * (x - mu) ** 2 / sigma2)


def _bocpd_probability(window: list[float]) -> float:
    """
    Calcula la probabilidad de que haya un cambio de punto al final
    de la ventana usando distribución Normal conjugada (NIG).
    Retorna probabilidad [0, 1].
    """
    n = len(window)
    if n < 10:
        return 0.0

    half = n // 2
    seg1 = window[:half]
    seg2 = window[half:]

    mu1    = sum(seg1) / len(seg1)
    mu2    = sum(seg2) / len(seg2)
    var1   = sum((x - mu1) ** 2 for x in seg1) / max(len(seg1) - 1, 1)
    var2   = sum((x - mu2) ** 2 for x in seg2) / max(len(seg2) - 1, 1)
    var_all = var1 + var2

    if var_all < 1e-10:
        return 0.0

    # Distancia estandarizada entre medias
    pooled_std = math.sqrt(var_all / 2)
    z_score    = abs(mu2 - mu1) / (pooled_std + 1e-10)

    # Convertir z-score a probabilidad usando tabla normal simplificada
    # P(Z > z) para z > 0: aproximación de cola derecha
    z_clipped = min(z_score, 6.0)
    # Φ aproximada: 1 - Φ(z) ≈ exp(-z²/2) / (z * sqrt(2π)) para z grande
    if z_clipped > 1.0:
        p_tail = math.exp(-z_clipped ** 2 / 2) / (z_clipped * math.sqrt(2 * math.pi))
        p_change = min(1.0, 2 * p_tail * (1 + BOCPD_HAZARD_RATE * n))
    else:
        # Para z pequeños usar aproximación lineal
        p_change = z_clipped * 0.16 * BOCPD_HAZARD_RATE * n

    return min(1.0, p_change)


def update_bocpd(returns: list[float], timestamp: str | None = None) -> dict:
    """Actualiza el modelo BOCPD con nuevos retornos."""
    ts    = timestamp or datetime.now().isoformat()
    state = _load_state()
    bocpd = state["bocpd"]

    # Añadir a ventana deslizante
    bocpd["returns_window"].extend(returns)
    bocpd["returns_window"] = bocpd["returns_window"][-BOCPD_WINDOW:]
    bocpd["last_updated"]   = ts

    prob = _bocpd_probability(bocpd["returns_window"])
    bocpd["last_prob"] = round(prob, 4)

    level = "NONE"
    if prob > 0.7:
        level = "CHANGE_POINT"
        event = {"timestamp": ts, "probability": round(prob, 4), "level": level}
        bocpd["change_points"].append(event)
        bocpd["change_points"] = bocpd["change_points"][-50:]
        print(f"[BOCPD] CHANGE_POINT detectado (prob={prob:.3f}) — re-validar estrategias activas")
        _notify_telegram(f"BOCPD CHANGE_POINT prob={prob:.3f} — re-validar estrategias")
    elif prob > 0.5:
        level = "WARNING"
        print(f"[BOCPD] WARNING (prob={prob:.3f})")
    else:
        print(f"[BOCPD] Régimen estable (prob={prob:.3f})")

    _save_state(state)
    return {"probability": round(prob, 4), "level": level}


# ─── ADDM (drift gradual por residuales PF) ───────────────────────────────────

def update_addm(expected_pf: float, actual_pf: float, strategy_id: str,
                timestamp: str | None = None) -> dict:
    """Actualiza el modelo ADDM con una nueva observación PF esperado/real."""
    ts    = timestamp or datetime.now().isoformat()
    state = _load_state()

    if strategy_id not in state["addm"]:
        state["addm"][strategy_id] = {"residuals": [], "last_updated": None, "level": "NONE"}

    addm = state["addm"][strategy_id]
    residual = expected_pf - actual_pf
    addm["residuals"].append({"ts": ts, "expected": expected_pf, "actual": actual_pf,
                               "residual": round(residual, 4)})
    addm["residuals"] = addm["residuals"][-100:]
    addm["last_updated"] = ts

    residuals = [r["residual"] for r in addm["residuals"]]
    level     = _addm_level(residuals)
    addm["level"] = level

    if level == "CRITICAL":
        print(f"[ADDM] DRIFT_DETECTED en {strategy_id} — sistema está derivando")
        _notify_telegram(f"ADDM DRIFT_DETECTED en {strategy_id} — revisar estrategia")
    elif level == "WARNING":
        print(f"[ADDM] WARNING drift en {strategy_id}")
    else:
        print(f"[ADDM] {strategy_id} estable (residual={residual:+.3f})")

    _save_state(state)
    return {"strategy_id": strategy_id, "residual": round(residual, 4), "level": level}


def _addm_level(residuals: list[float]) -> str:
    """Evalúa el nivel de drift usando media móvil y desviación estándar."""
    if len(residuals) < 10:
        return "NONE"

    n    = len(residuals)
    mean = sum(residuals) / n
    var  = sum((r - mean) ** 2 for r in residuals) / max(n - 1, 1)
    std  = math.sqrt(var) if var > 0 else 1e-10

    # Media móvil de los últimos ADDM_CONSEC_WARN periodos
    window = residuals[-ADDM_CONSEC_WARN:]
    if len(window) < ADDM_CONSEC_WARN:
        return "NONE"

    # Cuántos periodos consecutivos superan 2 std
    threshold = mean + 2 * std
    consec_above = sum(1 for r in window if r > threshold)

    if consec_above >= ADDM_CONSEC_WARN:
        return "CRITICAL"
    elif consec_above >= 2 or any(r > threshold for r in window):
        return "WARNING"
    return "NONE"


# ─── Informes ─────────────────────────────────────────────────────────────────

def get_drift_report() -> dict:
    """Estado actual de todos los detectores."""
    state  = _load_state()
    bocpd  = state["bocpd"]
    cutoff = (datetime.now() - timedelta(days=30)).isoformat()

    recent_cps = [cp for cp in bocpd.get("change_points", [])
                  if cp["timestamp"] >= cutoff]

    addm_report = {}
    for sid, data in state["addm"].items():
        residuals = [r["residual"] for r in data.get("residuals", [])]
        addm_report[sid] = {
            "level":        data.get("level", "NONE"),
            "n_obs":        len(residuals),
            "last_updated": data.get("last_updated"),
        }

    return {
        "bocpd": {
            "last_prob":        bocpd.get("last_prob", 0.0),
            "window_size":      len(bocpd.get("returns_window", [])),
            "change_points_30d": len(recent_cps),
            "last_updated":     bocpd.get("last_updated"),
        },
        "addm": addm_report,
    }


def check_regime_stability() -> dict:
    """Verifica la estabilidad del régimen actual."""
    state  = _load_state()
    bocpd  = state["bocpd"]
    prob   = bocpd.get("last_prob", 0.0)
    cutoff = (datetime.now() - timedelta(days=30)).isoformat()

    recent_cps = [cp for cp in bocpd.get("change_points", [])
                  if cp["timestamp"] >= cutoff]

    stable = len(recent_cps) == 0 and prob < 0.5
    result = {
        "stable":             stable,
        "current_prob":       prob,
        "change_points_30d":  len(recent_cps),
        "recommendation":     "OK" if stable else "Revalidar estrategias activas",
    }

    if not stable:
        print(f"[BOCPD] Régimen INESTABLE — {len(recent_cps)} cambios en 30 días, prob actual={prob:.3f}")
        print("        Recomendación: re-validar todas las estrategias activas con datos recientes")
    else:
        print(f"[BOCPD] Régimen estable — 0 cambios en 30 días, prob={prob:.3f}")

    return result


# ─── Telegram helper ──────────────────────────────────────────────────────────

def _notify_telegram(msg: str):
    import subprocess
    notifier = ROOT / "scripts" / "telegram-notifier.py"
    if not notifier.exists():
        return
    subprocess.run(
        [_PYTHON, str(notifier), "--level", "WARNING", "--message", msg],
        capture_output=True,
    )


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Concept Drift Detector — TradingLab")
    parser.add_argument("--update-bocpd", nargs="+", type=float, metavar="RET",
                        help="Actualizar BOCPD con lista de retornos")
    parser.add_argument("--update-addm", nargs=3,
                        metavar=("STRATEGY_ID", "EXPECTED_PF", "ACTUAL_PF"),
                        help="Actualizar ADDM con par esperado/real")
    parser.add_argument("--report",  action="store_true", help="Ver reporte de drift")
    parser.add_argument("--check",   action="store_true", help="Verificar estabilidad actual")
    args = parser.parse_args()

    if args.update_bocpd:
        result = update_bocpd(args.update_bocpd)
        print(f"Probabilidad cambio: {result['probability']:.3f}  Nivel: {result['level']}")

    elif args.update_addm:
        sid, exp, act = args.update_addm[0], float(args.update_addm[1]), float(args.update_addm[2])
        result = update_addm(exp, act, sid)
        print(f"Residual: {result['residual']:+.3f}  Nivel drift: {result['level']}")

    elif args.report:
        report = get_drift_report()
        print("\nREPORTE DE DRIFT")
        print("-" * 50)
        b = report["bocpd"]
        print(f"BOCPD  prob={b['last_prob']:.3f}  window={b['window_size']}  "
              f"cambios_30d={b['change_points_30d']}  updated={b['last_updated'] or 'nunca'}")
        print("\nADDM por estrategia:")
        for sid, a in report["addm"].items():
            print(f"  {sid:<20} nivel={a['level']:<10} obs={a['n_obs']}")

    elif args.check:
        check_regime_stability()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
