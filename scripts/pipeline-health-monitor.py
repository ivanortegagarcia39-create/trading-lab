#!/usr/bin/env python3
"""
pipeline-health-monitor.py — Monitor de salud del pipeline completo.

Detecta si el pipeline está funcionando correctamente o si hay señales
de degradación. Dashboard ASCII con semáforo por métrica.

Uso:
    python scripts/pipeline-health-monitor.py --report
    python scripts/pipeline-health-monitor.py --watch
    python scripts/pipeline-health-monitor.py --fix
"""

import argparse
import io
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT       = Path(__file__).parent.parent
AUDIT_PATH = ROOT / "config" / "bayesian-audit-trail.jsonl"
QUEUE_PATH = ROOT / "results" / "build-queue.json"
KG_DB_PATH = ROOT / ".kuzu" / "tradinglab.db"

GREEN  = "OK   "
YELLOW = "WARN "
RED    = "ALERT"

_PYTHON = sys.executable


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _semaforo(level: str) -> str:
    symbols = {GREEN: "[OK]   ", YELLOW: "[WARN] ", RED: "[ALERT]"}
    return symbols.get(level, "[?]    ")


def _read_audit(n_days: int = 28) -> list:
    if not AUDIT_PATH.exists():
        return []
    cutoff = (datetime.now() - timedelta(days=n_days)).isoformat()
    entries = []
    with open(AUDIT_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
                if e.get("timestamp", "") >= cutoff:
                    entries.append(e)
            except json.JSONDecodeError:
                pass
    return entries


def _read_queue() -> list:
    if not QUEUE_PATH.exists():
        return []
    try:
        with open(QUEUE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


# ─── Métricas ────────────────────────────────────────────────────────────────

def _check_approval_rate() -> dict:
    """
    Tasa de aprobación por puerta (últimas 4 semanas vs histórico).
    Si tasa_reciente < 50% de tasa_historica → WARNING.
    """
    recent  = _read_audit(n_days=28)
    all_ent = _read_audit(n_days=365)

    def approval_rate(entries):
        decisions = [e for e in entries if e.get("action") in
                     ("recalibrated", "recalibrated_clipped", "registered_no_recalibration")]
        if not decisions:
            return None
        positive = [e for e in decisions if e.get("outcome") in ("true_positive", "true_negative")]
        return len(positive) / len(decisions)

    rate_recent = approval_rate(recent)
    rate_all    = approval_rate(all_ent)

    if rate_recent is None or rate_all is None:
        return {"metric": "approval_rate", "level": GREEN,
                "message": "Sin datos suficientes de decisiones de puertas",
                "value": None}

    if rate_recent < rate_all * 0.5:
        level = RED
        msg   = f"Tasa reciente {rate_recent:.1%} < 50% de histórica {rate_all:.1%}"
    elif rate_recent < rate_all * 0.75:
        level = YELLOW
        msg   = f"Tasa reciente {rate_recent:.1%} vs histórica {rate_all:.1%}"
    else:
        level = GREEN
        msg   = f"Tasa de aprobación OK: {rate_recent:.1%}"

    return {"metric": "approval_rate", "level": level, "message": msg,
            "value": rate_recent}


def _check_consecutive_failed_builds() -> dict:
    """Si > 2 builds consecutivos sin pasar EvalGate → ALERTA."""
    queue = _read_queue()
    completed = [q for q in queue if q.get("estado") == "COMPLETADO"]

    # Contar builds recientes sin estrategias (proxy: builds completados
    # para los que no hay estrategias en el registry)
    registry_path = ROOT / "results" / "strategies-registry.json"
    if not registry_path.exists():
        return {"metric": "consecutive_failures", "level": GREEN,
                "message": "Sin registry — no se puede evaluar", "value": 0}

    try:
        with open(registry_path, encoding="utf-8") as f:
            registry = json.load(f)
        if "strategies" in registry:
            registry = registry["strategies"]
    except Exception:
        return {"metric": "consecutive_failures", "level": GREEN,
                "message": "Error leyendo registry", "value": 0}

    # Builds completados más recientes
    recent_builds = sorted(completed, key=lambda x: x.get("fecha_completado", ""),
                           reverse=True)[:5]
    consecutive_no_result = 0
    for build in recent_builds:
        bid = build.get("build")
        has_strategies = any(
            f"B{bid}-" in sid or f"B{str(bid).zfill(2)}-" in sid
            for sid in registry
        ) if bid else False
        if not has_strategies:
            consecutive_no_result += 1
        else:
            break

    if consecutive_no_result > 2:
        level = RED
        msg   = f"{consecutive_no_result} builds consecutivos sin estrategias válidas"
    elif consecutive_no_result == 2:
        level = YELLOW
        msg   = f"2 builds consecutivos sin resultados — monitorear"
    else:
        level = GREEN
        msg   = f"Builds con resultados: OK ({consecutive_no_result} sin resultado)"

    return {"metric": "consecutive_failures", "level": level,
            "message": msg, "value": consecutive_no_result}


def _check_bayesian_drift() -> dict:
    """Si algún criterio cambió > 15% respecto al valor inicial → revisar."""
    criteria_path = ROOT / "config" / "bayesian-criteria.json"
    if not criteria_path.exists():
        return {"metric": "bayesian_drift", "level": GREEN,
                "message": "bayesian-criteria.json no encontrado", "value": None}

    try:
        with open(criteria_path, encoding="utf-8") as f:
            criteria = json.load(f)
    except Exception:
        return {"metric": "bayesian_drift", "level": GREEN,
                "message": "Error leyendo criterios", "value": None}

    drifted = []
    for name, c in criteria.items():
        inicial = float(c.get("valor_inicial", 0))
        actual  = float(c.get("valor_actual", inicial))
        if inicial == 0:
            continue
        pct_change = abs(actual - inicial) / inicial
        if pct_change > 0.15:
            drifted.append((name, round(pct_change * 100, 1)))

    if drifted:
        level = YELLOW
        items = ", ".join(f"{n}({p}%)" for n, p in drifted)
        msg   = f"Criterios con drift > 15%: {items}"
    else:
        level = GREEN
        msg   = "Todos los criterios dentro del rango esperado"

    return {"metric": "bayesian_drift", "level": level, "message": msg,
            "value": len(drifted)}


def _check_kg_freshness() -> dict:
    """Si el KG no tiene actualizaciones en > 7 días → WARNING."""
    if not KG_DB_PATH.exists():
        return {"metric": "kg_freshness", "level": YELLOW,
                "message": "Knowledge Graph no inicializado", "value": None}

    import os
    mtime     = os.path.getmtime(str(KG_DB_PATH))
    days_old  = (datetime.now().timestamp() - mtime) / 86400

    if days_old > 7:
        level = YELLOW
        msg   = f"KG sin actualizaciones desde hace {days_old:.1f} días"
    else:
        level = GREEN
        msg   = f"KG actualizado hace {days_old:.1f} días"

    return {"metric": "kg_freshness", "level": level,
            "message": msg, "value": round(days_old, 1)}


def _check_drift_detector() -> dict:
    """Estado del concept-drift-detector."""
    drift_path = ROOT / "results" / "drift-detection.json"
    if not drift_path.exists():
        return {"metric": "drift_detector", "level": GREEN,
                "message": "Sin datos de drift (normal si no hay datos de producción)"}

    try:
        with open(drift_path, encoding="utf-8") as f:
            state = json.load(f)
        prob = state.get("bocpd", {}).get("last_prob", 0.0)
        cps  = state.get("bocpd", {}).get("change_points", [])
        recent_cps = [cp for cp in cps
                      if cp.get("timestamp", "") >= (datetime.now() - timedelta(days=30)).isoformat()]
        addm_critical = [sid for sid, d in state.get("addm", {}).items()
                         if d.get("level") == "CRITICAL"]

        if addm_critical or prob > 0.7:
            level = RED
            msg   = f"CHANGE_POINT prob={prob:.3f} o DRIFT en: {addm_critical}"
        elif len(recent_cps) > 0 or prob > 0.5:
            level = YELLOW
            msg   = f"Señales de drift: {len(recent_cps)} cambios/30d, prob={prob:.3f}"
        else:
            level = GREEN
            msg   = f"Régimen estable (prob={prob:.3f}, {len(recent_cps)} cambios/30d)"
    except Exception:
        level = GREEN
        msg   = "Error leyendo estado drift"

    return {"metric": "drift_detector", "level": level, "message": msg}


# ─── Dashboard ────────────────────────────────────────────────────────────────

def generate_report() -> dict:
    """Genera el reporte completo con dashboard ASCII."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    checks = [
        _check_approval_rate(),
        _check_consecutive_failed_builds(),
        _check_bayesian_drift(),
        _check_kg_freshness(),
        _check_drift_detector(),
    ]

    labels = {
        "approval_rate":        "Tasa aprobación puertas",
        "consecutive_failures": "Builds consecutivos sin resultado",
        "bayesian_drift":       "Drift criterios bayesianos",
        "kg_freshness":         "Knowledge Graph actualizado",
        "drift_detector":       "Concept Drift / Régimen",
    }

    red_count    = sum(1 for c in checks if c["level"] == RED)
    yellow_count = sum(1 for c in checks if c["level"] == YELLOW)

    print(f"\nPIPELINE HEALTH MONITOR — {now}")
    print("=" * 65)

    for c in checks:
        sem   = _semaforo(c["level"])
        label = labels.get(c["metric"], c["metric"])
        print(f"  {sem} {label:<35} {c['message'][:30]}")

    print("=" * 65)
    if red_count:
        print(f"  ESTADO: ACCION INMEDIATA — {red_count} metrica(s) en ROJO")
    elif yellow_count:
        print(f"  ESTADO: REVISAR — {yellow_count} metrica(s) en AMARILLO")
    else:
        print("  ESTADO: Pipeline funcionando correctamente")
    print()

    return {
        "timestamp":   now,
        "checks":      checks,
        "red_count":   red_count,
        "yellow_count": yellow_count,
        "overall":     "RED" if red_count else "YELLOW" if yellow_count else "GREEN",
    }


def run_watch(interval_minutes: int = 60):
    """Modo continuo — actualiza cada `interval_minutes` minutos."""
    print(f"Modo watch — actualizando cada {interval_minutes} min. Ctrl+C para salir.")
    while True:
        generate_report()
        time.sleep(interval_minutes * 60)


def run_fix():
    """Intenta autocorrecciones menores en el pipeline."""
    print("\nAutofix — verificando problemas corregibles...")

    # 1. Re-index ChromaDB si hace > 7 días
    chromadb_path = ROOT / ".chromadb"
    if chromadb_path.exists():
        import os
        age = (datetime.now().timestamp() - os.path.getmtime(str(chromadb_path))) / 86400
        if age > 7:
            print(f"  ChromaDB tiene {age:.0f} días — re-indexando...")
            kb = ROOT / "scripts" / "knowledge-base.py"
            if kb.exists():
                subprocess.run([_PYTHON, str(kb), "re-index"], capture_output=True)
                print("  ChromaDB re-indexado.")

    # 2. Verificar que bayesian-criteria.json existe
    criteria_path = ROOT / "config" / "bayesian-criteria.json"
    if not criteria_path.exists():
        print("  bayesian-criteria.json no existe — inicializando...")
        bu = ROOT / "scripts" / "bayesian-criteria-updater.py"
        if bu.exists():
            subprocess.run([_PYTHON, str(bu), "--thresholds"], capture_output=True)

    print("  Autofix completado.")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Pipeline Health Monitor — TradingLab")
    parser.add_argument("--report", action="store_true", help="Generar reporte completo")
    parser.add_argument("--watch",  action="store_true", help="Modo continuo (cada hora)")
    parser.add_argument("--fix",    action="store_true", help="Intentar autocorrecciones")
    args = parser.parse_args()

    if args.report:
        generate_report()
    elif args.watch:
        run_watch()
    elif args.fix:
        run_fix()
    else:
        generate_report()


if __name__ == "__main__":
    main()
