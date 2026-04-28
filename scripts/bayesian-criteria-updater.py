#!/usr/bin/env python3
"""
bayesian-criteria-updater.py — Actualización bayesiana de umbrales del pipeline.

Cada criterio tiene un prior Beta(α, β) que se actualiza con resultados reales.
El umbral operativo es el percentil 25 del posterior (conservador).

Uso:
    python scripts/bayesian-criteria-updater.py --thresholds
    python scripts/bayesian-criteria-updater.py --report
    python scripts/bayesian-criteria-updater.py --update pf_minimo_evalgate true_positive
    python scripts/bayesian-criteria-updater.py --reset pf_minimo_evalgate
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT          = Path(__file__).parent.parent
CRITERIA_PATH = ROOT / "config" / "bayesian-criteria.json"
AUDIT_PATH    = ROOT / "config" / "bayesian-audit-trail.jsonl"

OUTCOMES = {"true_positive", "false_positive", "true_negative", "false_negative"}

# ─── Inicialización de criterios ──────────────────────────────────────────────

DEFAULT_CRITERIA = {
    "pf_minimo_evalgate": {
        "valor_inicial": 1.5,
        "alpha": 1, "beta": 1,
        "min_absoluto": 1.3,
        "max_absoluto": 2.0,
        "descripcion": "PF mínimo en EvalGate",
    },
    "dd_maximo_evalgate": {
        "valor_inicial": 7.0,
        "alpha": 1, "beta": 1,
        "min_absoluto": 5.0,
        "max_absoluto": 10.0,
        "descripcion": "DD máximo en EvalGate",
    },
    "sharpe_minimo_oos": {
        "valor_inicial": 0.5,
        "alpha": 1, "beta": 1,
        "min_absoluto": 0.3,
        "max_absoluto": 1.5,
        "descripcion": "Sharpe mínimo en OOS",
    },
    "wfe_minimo": {
        "valor_inicial": 50.0,
        "alpha": 1, "beta": 1,
        "min_absoluto": 40.0,
        "max_absoluto": 70.0,
        "descripcion": "WFE mínimo en WFO",
    },
    "pf_forward_test_ratio": {
        "valor_inicial": 0.70,
        "alpha": 1, "beta": 1,
        "min_absoluto": 0.50,
        "max_absoluto": 0.90,
        "descripcion": "Ratio PF forward test vs backtest",
    },
}


# ─── I/O de estado ────────────────────────────────────────────────────────────

def _load_criteria() -> dict:
    if not CRITERIA_PATH.exists():
        return {k: dict(v) for k, v in DEFAULT_CRITERIA.items()}
    with open(CRITERIA_PATH) as f:
        return json.load(f)


def _save_criteria(criteria: dict):
    CRITERIA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CRITERIA_PATH, "w") as f:
        json.dump(criteria, f, indent=2)


def _audit(entry: dict):
    CRITERIA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


# ─── Beta distribution helpers (sin scipy) ────────────────────────────────────

def _beta_mean(alpha: float, beta: float) -> float:
    return alpha / (alpha + beta)


def _beta_p25(alpha: float, beta: float) -> float:
    """Aproximación del percentil 25 de Beta(α, β) via método de Wilson."""
    # Approx: usando cuantil normal de la transformación logit de la media
    # Para α, β > 0: p25 ≈ mean - 0.674 * std
    mean = alpha / (alpha + beta)
    var  = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1))
    std  = var ** 0.5
    p25  = mean - 0.674 * std
    return max(0.0, min(1.0, p25))


def _operational_threshold(criterion: dict) -> float:
    """Calcula el umbral operativo escalado al rango [min_absoluto, max_absoluto]."""
    p25  = _beta_p25(criterion["alpha"], criterion["beta"])
    lo   = criterion["min_absoluto"]
    hi   = criterion["max_absoluto"]
    return lo + p25 * (hi - lo)


# ─── Funciones principales ────────────────────────────────────────────────────

def update_criterion(criterion_name: str, outcome: str) -> dict:
    """Actualiza α o β según el outcome y recalcula el umbral operativo."""
    if outcome not in OUTCOMES:
        print(f"ERROR: outcome debe ser uno de {OUTCOMES}")
        sys.exit(1)

    criteria = _load_criteria()
    if criterion_name not in criteria:
        print(f"ERROR: criterio '{criterion_name}' no existe.")
        print(f"Disponibles: {list(criteria)}")
        sys.exit(1)

    c = criteria[criterion_name]
    n_obs = c["alpha"] + c["beta"] - 2  # observaciones reales (prior = 1,1)

    if n_obs < 5:
        print(f"AVISO: solo {n_obs} observaciones. Se necesitan ≥5 para recalibrar.")
        print("Registrando observación sin recalibrar umbral.")
        # Solo actualizamos α/β pero no el umbral todavía
        if outcome in ("true_positive", "true_negative"):
            c["alpha"] += 1
        else:
            c["beta"] += 1
        _save_criteria(criteria)
        _audit({"timestamp": datetime.now().isoformat(), "criterion": criterion_name,
                "outcome": outcome, "action": "registered_no_recalibration",
                "alpha": c["alpha"], "beta": c["beta"]})
        return c

    # Calcular umbral antes del cambio
    threshold_before = _operational_threshold(c)

    # Actualizar α o β
    if outcome in ("true_positive", "true_negative"):
        c["alpha"] += 1
    else:
        c["beta"] += 1

    threshold_after = _operational_threshold(c)
    pct_change = abs(threshold_after - threshold_before) / threshold_before * 100

    # Reglas de seguridad: máximo 10% de cambio por actualización
    confidence = c["alpha"] + c["beta"]
    if confidence <= 50 and pct_change < 5:
        action = "recalibrated"
    elif confidence > 50 and pct_change < 2:
        action = "recalibrated"
    elif pct_change >= 10:
        # Clipear al 10% máximo de cambio
        max_delta = threshold_before * 0.10
        direction = 1 if threshold_after > threshold_before else -1
        threshold_after = threshold_before + direction * max_delta
        threshold_after = max(c["min_absoluto"], min(c["max_absoluto"], threshold_after))
        action = "recalibrated_clipped"
    else:
        action = "recalibrated"

    # Verificar límites absolutos
    threshold_after = max(c["min_absoluto"], min(c["max_absoluto"], threshold_after))
    c["valor_actual"] = round(threshold_after, 4)

    _save_criteria(criteria)
    _audit({
        "timestamp":         datetime.now().isoformat(),
        "criterion":         criterion_name,
        "outcome":           outcome,
        "action":            action,
        "threshold_before":  round(threshold_before, 4),
        "threshold_after":   round(threshold_after, 4),
        "pct_change":        round(pct_change, 2),
        "alpha":             c["alpha"],
        "beta":              c["beta"],
        "confidence":        confidence,
    })

    direction = "más estricto" if threshold_after > threshold_before else "más permisivo"
    print(f"{criterion_name}: {threshold_before:.4f} → {threshold_after:.4f} ({direction}, {action})")
    return c


def get_current_thresholds() -> dict:
    """Devuelve todos los umbrales actuales con metadatos."""
    criteria  = _load_criteria()
    result    = {}
    for name, c in criteria.items():
        current = c.get("valor_actual", _operational_threshold(c))
        result[name] = {
            "valor_inicial":  c["valor_inicial"],
            "valor_actual":   round(current, 4),
            "confianza":      c["alpha"] + c["beta"],
            "alpha":          c["alpha"],
            "beta":           c["beta"],
            "descripcion":    c["descripcion"],
        }
    return result


def check_for_recalibration() -> list:
    """Devuelve criterios que necesitan atención."""
    criteria = _load_criteria()
    alerts   = []
    for name, c in criteria.items():
        conf = c["alpha"] + c["beta"]
        if conf < 10:
            alerts.append({"criterion": name, "status": "datos_insuficientes", "confidence": conf})
        elif conf < 50:
            alerts.append({"criterion": name, "status": "confianza_media", "confidence": conf})
        else:
            alerts.append({"criterion": name, "status": "alta_confianza", "confidence": conf})
    return alerts


def reset_criterion(criterion_name: str):
    """Resetea un criterio al valor inicial."""
    criteria = _load_criteria()
    if criterion_name not in criteria:
        print(f"ERROR: criterio '{criterion_name}' no existe.")
        sys.exit(1)
    default = DEFAULT_CRITERIA[criterion_name]
    criteria[criterion_name].update({
        "alpha": default["alpha"],
        "beta":  default["beta"],
        "valor_actual": default["valor_inicial"],
    })
    _save_criteria(criteria)
    _audit({
        "timestamp": datetime.now().isoformat(),
        "criterion": criterion_name,
        "action":    "reset",
    })
    print(f"{criterion_name} reseteado a valor inicial: {default['valor_inicial']}")


def generate_calibration_report():
    """Genera informe completo de calibración."""
    criteria   = _load_criteria()
    thresholds = get_current_thresholds()
    print("\nINFORME DE CALIBRACIÓN BAYESIANA")
    print("=" * 65)
    for name, t in thresholds.items():
        c         = criteria[name]
        current   = t["valor_actual"]
        initial   = t["valor_inicial"]
        delta     = current - initial
        direction = "→ más estricto" if delta > 0 else "→ más permisivo" if delta < 0 else "→ sin cambio"
        conf      = t["confianza"]
        nivel     = "ALTA" if conf > 50 else "MEDIA" if conf >= 10 else "BAJA"
        print(f"\n{name}")
        print(f"  Descripción:   {t['descripcion']}")
        print(f"  Inicial:       {initial}")
        print(f"  Actual:        {current}  {direction}")
        print(f"  Observaciones: {conf - 2} reales  (α={t['alpha']}, β={t['beta']})")
        print(f"  Confianza:     {nivel} ({conf})")
    print()


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Bayesian Criteria Updater — TradingLab")
    parser.add_argument("--update",     nargs=2, metavar=("CRITERIO", "OUTCOME"),
                        help="Actualizar criterio con outcome")
    parser.add_argument("--report",     action="store_true", help="Ver reporte de calibración")
    parser.add_argument("--thresholds", action="store_true", help="Ver umbrales actuales")
    parser.add_argument("--reset",      metavar="CRITERIO", help="Resetear criterio al valor inicial")
    args = parser.parse_args()

    if args.update:
        update_criterion(args.update[0], args.update[1])

    elif args.report:
        generate_calibration_report()

    elif args.thresholds:
        thresholds = get_current_thresholds()
        print("\nUmbrales actuales del pipeline:")
        print("-" * 65)
        for name, t in thresholds.items():
            print(f"  {name:<30} {t['valor_actual']:<8}  "
                  f"(inicial={t['valor_inicial']}, conf={t['confianza']})")

    elif args.reset:
        reset_criterion(args.reset)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
