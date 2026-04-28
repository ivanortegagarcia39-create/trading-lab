#!/usr/bin/env python3
"""
strategy-retirement-manager.py — Ciclo de vida completo de estrategias.

Gestiona las transiciones de estado desde que SQ genera una estrategia
hasta que se retira del portfolio.

Estados: standby → candidate → shadow → active → decaying → retired / failed_challenge

Uso:
    python scripts/strategy-retirement-manager.py --report
    python scripts/strategy-retirement-manager.py --check
    python scripts/strategy-retirement-manager.py --transition STRAT001 candidate "Pasó EvalGate: PF=1.8"
"""

import argparse
import io
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT          = Path(__file__).parent.parent
REGISTRY_PATH = ROOT / "results" / "strategies-registry.json"
AUDIT_PATH    = ROOT / "config" / "retirement-audit.jsonl"

VALID_STATES = {
    "standby", "candidate", "shadow", "active",
    "decaying", "retired", "failed_challenge",
}

# Tiempo máximo en cada estado antes de alerta (días)
STATE_TIMEOUTS = {
    "standby":   2,
    "candidate": 3,
    "shadow":    35,    # 4 semanas + margen
    "decaying":  30,    # 4 semanas máximo antes de decisión
}

_PYTHON = sys.executable


# ─── I/O ──────────────────────────────────────────────────────────────────────

def _load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        return {}
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("strategies", data) if "strategies" in data else data


def _save_registry(registry: dict):
    if not REGISTRY_PATH.exists():
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump({"strategies": registry}, f, indent=2, ensure_ascii=False)
        return
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    if "strategies" in raw:
        raw["strategies"] = registry
    else:
        raw = {"strategies": registry}
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2, ensure_ascii=False)


def _audit(entry: dict):
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _notify_telegram(msg: str, level: str = "INFO"):
    notifier = ROOT / "scripts" / "telegram-notifier.py"
    if not notifier.exists():
        return
    subprocess.run(
        [_PYTHON, str(notifier), "--level", level, "--message", msg],
        capture_output=True,
    )


# ─── Helpers de estado ────────────────────────────────────────────────────────

def _get_strategy_state(sid: str, registry: dict) -> str | None:
    if sid not in registry:
        return None
    sdata = registry[sid]
    version = sdata.get("version_activa", "v1")
    return str(sdata.get("versiones", {}).get(version, {}).get("estado", "standby")).lower()


def _get_state_since(sid: str, registry: dict) -> str | None:
    """Fecha desde la que la estrategia está en su estado actual."""
    if sid not in registry:
        return None
    sdata   = registry[sid]
    version = sdata.get("version_activa", "v1")
    vdata   = sdata.get("versiones", {}).get(version, {})
    return vdata.get("estado_desde") or vdata.get("fecha_evaluacion") or vdata.get("fecha")


# ─── Funciones principales ────────────────────────────────────────────────────

def transition_state(strategy_id: str, new_state: str, reason: str,
                     registry: dict | None = None,
                     save: bool = True) -> bool:
    """Cambia el estado de una estrategia y registra la transición."""
    if new_state not in VALID_STATES:
        print(f"ERROR: estado '{new_state}' no válido. Opciones: {sorted(VALID_STATES)}")
        return False

    if registry is None:
        registry = _load_registry()

    if strategy_id not in registry:
        print(f"ERROR: {strategy_id} no encontrado en el registry.")
        return False

    sdata   = registry[strategy_id]
    version = sdata.get("version_activa", "v1")
    old_state = str(sdata.get("versiones", {}).get(version, {})
                    .get("estado", "standby")).lower()

    now = datetime.now().isoformat()
    sdata["versiones"][version]["estado"]       = new_state
    sdata["versiones"][version]["estado_desde"] = now
    sdata["versiones"][version]["estado_razon"] = reason

    if save:
        _save_registry(registry)

    entry = {
        "timestamp":   now,
        "strategy_id": strategy_id,
        "from_state":  old_state,
        "to_state":    new_state,
        "reason":      reason,
    }
    _audit(entry)

    print(f"  {strategy_id}: {old_state} → {new_state}  [{reason[:60]}]")

    # Notificar estados importantes
    important = {"active", "retired", "failed_challenge", "decaying"}
    if new_state in important:
        level = "CRITICAL" if new_state in {"retired", "failed_challenge"} else "INFO"
        _notify_telegram(
            f"Estrategia {strategy_id}: {old_state} → {new_state} — {reason[:80]}",
            level=level,
        )
    return True


def check_for_transitions(dry_run: bool = False) -> list:
    """
    Verifica si alguna estrategia debe transicionar de estado.
    Basado en timeouts y métricas del ADDM/champion-challenger.
    """
    registry   = _load_registry()
    drift_path = ROOT / "results" / "drift-detection.json"
    cc_path    = ROOT / "results" / "champion-challenger.json"

    transitions_made = []

    # Cargar estado ADDM para detectar drift en estrategias active/decaying
    addm_critical = set()
    addm_ok       = set()
    if drift_path.exists():
        try:
            with open(drift_path, encoding="utf-8") as f:
                drift_state = json.load(f)
            for sid, d in drift_state.get("addm", {}).items():
                if d.get("level") == "CRITICAL":
                    addm_critical.add(sid)
                elif d.get("level") == "NONE":
                    addm_ok.add(sid)
        except Exception:
            pass

    # Cargar champion-challenger para detectar promoted challengers
    promoted_challengers = set()
    if cc_path.exists():
        try:
            with open(cc_path, encoding="utf-8") as f:
                cc_data = json.load(f)
            # Champions con promoted_from_challenger = True y recientes
            cutoff = (datetime.now() - timedelta(days=7)).isoformat()
            for sid, c in cc_data.get("champions", {}).items():
                if c.get("promoted_from_challenger") and c.get("registered", "") >= cutoff:
                    promoted_challengers.add(sid)
        except Exception:
            pass

    now = datetime.now()
    for sid, sdata in registry.items():
        version   = sdata.get("version_activa", "v1")
        vdata     = sdata.get("versiones", {}).get(version, {})
        state     = str(vdata.get("estado", "standby")).lower()
        since_str = vdata.get("estado_desde")

        # ── Transición por timeout ────────────────────────────────────────────
        if state in STATE_TIMEOUTS and since_str:
            try:
                since    = datetime.fromisoformat(since_str)
                days_in  = (now - since).days
                max_days = STATE_TIMEOUTS[state]
                if days_in > max_days:
                    reason = f"Timeout: {days_in} días en estado {state} (max {max_days})"
                    if state == "decaying":
                        target = "retired"
                    elif state == "standby":
                        target = "candidate"  # Forzar evaluación
                    else:
                        target = None  # No forzar, solo alertar
                    if target and not dry_run:
                        if transition_state(sid, target, reason, registry, save=False):
                            transitions_made.append({"id": sid, "from": state, "to": target, "reason": reason})
                    elif target:
                        print(f"  [DRY-RUN] {sid}: {state} → {target}  [{reason}]")
            except (ValueError, TypeError):
                pass

        # ── Transición por ADDM: active → decaying ────────────────────────────
        if state == "active" and sid in addm_critical:
            reason = "ADDM detectó drift CRITICAL — iniciando período de observación"
            if not dry_run:
                if transition_state(sid, "decaying", reason, registry, save=False):
                    transitions_made.append({"id": sid, "from": "active", "to": "decaying", "reason": reason})
            else:
                print(f"  [DRY-RUN] {sid}: active → decaying  [{reason}]")

        # ── Transición por ADDM: decaying → active (recuperación) ─────────────
        if state == "decaying" and sid in addm_ok:
            reason = "ADDM volvió a NONE — estrategia recuperada"
            if not dry_run:
                if transition_state(sid, "active", reason, registry, save=False):
                    transitions_made.append({"id": sid, "from": "decaying", "to": "active", "reason": reason})
            else:
                print(f"  [DRY-RUN] {sid}: decaying → active  [{reason}]")

        # ── Transición shadow → active por champion-challenger ────────────────
        if state == "shadow" and sid in promoted_challengers:
            reason = "Promovida por Champion-Challenger a champion activo"
            if not dry_run:
                if transition_state(sid, "active", reason, registry, save=False):
                    transitions_made.append({"id": sid, "from": "shadow", "to": "active", "reason": reason})
            else:
                print(f"  [DRY-RUN] {sid}: shadow → active  [{reason}]")

    if transitions_made and not dry_run:
        _save_registry(registry)

    return transitions_made


def get_lifecycle_report() -> dict:
    """Resumen de todas las estrategias por estado."""
    registry = _load_registry()
    now      = datetime.now()

    by_state: dict[str, list] = {s: [] for s in VALID_STATES}

    for sid, sdata in registry.items():
        version = sdata.get("version_activa", "v1")
        vdata   = sdata.get("versiones", {}).get(version, {})
        state   = str(vdata.get("estado", "standby")).lower()
        since   = vdata.get("estado_desde", "")
        days    = None
        if since:
            try:
                days = (now - datetime.fromisoformat(since)).days
            except (ValueError, TypeError):
                pass
        by_state.setdefault(state, []).append({"id": sid, "days": days})

    print("\nCICLO DE VIDA DE ESTRATEGIAS")
    print("=" * 55)
    order = ["standby", "candidate", "shadow", "active",
             "decaying", "retired", "failed_challenge"]
    needs_attention = []

    for state in order:
        strats = by_state.get(state, [])
        if not strats:
            continue
        timeout = STATE_TIMEOUTS.get(state)
        print(f"\n  {state.upper()} ({len(strats)})")
        for s in strats:
            days_str = f"{s['days']}d" if s["days"] is not None else "?"
            alert    = ""
            if timeout and s["days"] and s["days"] > timeout:
                alert = " [!TIMEOUT]"
                needs_attention.append(s["id"])
            print(f"    {s['id']:<28} {days_str:>5}{alert}")

    if needs_attention:
        print(f"\n  Estrategias que necesitan atención: {needs_attention}")
    else:
        print("\n  Todas las estrategias dentro de sus tiempos esperados.")

    return {"by_state": {k: v for k, v in by_state.items() if v},
            "needs_attention": needs_attention}


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Strategy Retirement Manager — TradingLab")
    parser.add_argument("--report",     action="store_true",
                        help="Ver ciclo de vida de todas las estrategias")
    parser.add_argument("--check",      action="store_true",
                        help="Verificar y ejecutar transiciones pendientes")
    parser.add_argument("--dry-run",    action="store_true",
                        help="Simular transiciones sin aplicar")
    parser.add_argument("--transition", nargs=3,
                        metavar=("STRATEGY_ID", "NEW_STATE", "REASON"),
                        help="Transición manual de estado")
    args = parser.parse_args()

    if args.report:
        get_lifecycle_report()

    elif args.check:
        dry = args.dry_run
        prefix = "[DRY-RUN] " if dry else ""
        print(f"\n{prefix}Verificando transiciones pendientes...")
        transitions = check_for_transitions(dry_run=dry)
        if transitions:
            print(f"\n{len(transitions)} transición(es) ejecutada(s):")
            for t in transitions:
                print(f"  {t['id']}: {t['from']} → {t['to']}")
        else:
            print("  Sin transiciones necesarias.")

    elif args.transition:
        sid, new_state, reason = args.transition
        registry = _load_registry()
        transition_state(sid, new_state, reason, registry)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
