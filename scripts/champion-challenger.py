#!/usr/bin/env python3
"""
champion-challenger.py — Sistema Champion-Challenger con Shadow Mode.

Champion: estrategia activa con capital real.
Challenger: estrategia nueva en paper trading durante 4 semanas.
Si el challenger supera al champion en 2 de 3 métricas → PROMOTION.

Uso:
    python scripts/champion-challenger.py --status
    python scripts/champion-challenger.py --register-champion STRAT001 '{"pf":1.8,"dd":5.2,"sharpe":0.9}'
    python scripts/champion-challenger.py --register-challenger STRAT002 '{"pf":2.1,"dd":4.8,"sharpe":1.1}'
    python scripts/champion-challenger.py --evaluate STRAT002
    python scripts/champion-challenger.py --promote STRAT002
"""

import argparse
import io
import json
import math
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT       = Path(__file__).parent.parent
STATE_PATH = ROOT / "results" / "champion-challenger.json"
AUDIT_PATH = ROOT / "config" / "cc-audit-trail.jsonl"

SHADOW_WEEKS    = 4
PROMOTE_METRICS = 2  # ganar en 2 de 3 métricas para ascender

_PYTHON = sys.executable


# ─── I/O de estado ────────────────────────────────────────────────────────────

def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {"champions": {}, "challengers": {}}
    with open(STATE_PATH) as f:
        return json.load(f)


def _save_state(state: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def _audit(entry: dict):
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


# ─── Helpers estadísticos ─────────────────────────────────────────────────────

def _t_test_two_sample(a: list[float], b: list[float]) -> float:
    """t-test de dos muestras independientes. Devuelve p-valor aproximado."""
    na, nb = len(a), len(b)
    if na < 3 or nb < 3:
        return 1.0

    ma   = sum(a) / na
    mb   = sum(b) / nb
    sa2  = sum((x - ma) ** 2 for x in a) / (na - 1)
    sb2  = sum((x - mb) ** 2 for x in b) / (nb - 1)
    se   = math.sqrt(sa2 / na + sb2 / nb)
    if se < 1e-10:
        return 0.0 if ma != mb else 1.0

    t    = abs(ma - mb) / se
    # Grados de libertad Welch
    df   = (sa2 / na + sb2 / nb) ** 2 / (
               (sa2 / na) ** 2 / (na - 1) + (sb2 / nb) ** 2 / (nb - 1)
           )
    # Aproximación p-valor: para df > 20 y t grande, p ≈ exp(-t²/2)*sqrt(2/π)
    if df > 20:
        p = math.exp(-min(t, 10) ** 2 / 2) * math.sqrt(2 / math.pi)
    else:
        p = 1.0 / (1.0 + t / math.sqrt(df))
    return min(1.0, p)


def _metrics_better(challenger: dict, champion: dict) -> tuple[int, list[str]]:
    """
    Compara métricas challenger vs champion.
    Devuelve (n_wins, descripción por métrica).
    """
    wins  = 0
    lines = []
    # PF: challenger mayor es mejor
    cpf = challenger.get("pf", 0)
    hpf = champion.get("pf", 0)
    if cpf > hpf:
        wins += 1
        lines.append(f"PF: {cpf:.2f} > {hpf:.2f} [WIN]")
    else:
        lines.append(f"PF: {cpf:.2f} <= {hpf:.2f} [LOSE]")

    # DD: challenger menor es mejor
    cdd = challenger.get("dd", 100)
    hdd = champion.get("dd", 100)
    if cdd < hdd:
        wins += 1
        lines.append(f"DD: {cdd:.2f}% < {hdd:.2f}% [WIN]")
    else:
        lines.append(f"DD: {cdd:.2f}% >= {hdd:.2f}% [LOSE]")

    # Sharpe: challenger mayor es mejor
    cs = challenger.get("sharpe", 0)
    hs = champion.get("sharpe", 0)
    if cs > hs:
        wins += 1
        lines.append(f"Sharpe: {cs:.3f} > {hs:.3f} [WIN]")
    else:
        lines.append(f"Sharpe: {cs:.3f} <= {hs:.3f} [LOSE]")

    return wins, lines


# ─── Funciones principales ────────────────────────────────────────────────────

def register_champion(strategy_id: str, metrics: dict):
    """Registra una estrategia como champion activo."""
    state = _load_state()
    entry = {
        "strategy_id": strategy_id,
        "metrics":     metrics,
        "status":      "CHAMPION",
        "registered":  datetime.now().isoformat(),
    }
    state["champions"][strategy_id] = entry
    _save_state(state)
    _audit({"timestamp": datetime.now().isoformat(), "action": "register_champion",
             "strategy_id": strategy_id, "metrics": metrics})
    print(f"Champion registrado: {strategy_id}  PF={metrics.get('pf')} DD={metrics.get('dd')}%")


def register_challenger(strategy_id: str, metrics: dict):
    """Registra una estrategia como challenger en shadow mode."""
    state = _load_state()

    if not state["champions"]:
        # Sin champion → se convierte en champion directo
        print(f"Sin champion activo. {strategy_id} se convierte en champion directo.")
        register_champion(strategy_id, metrics)
        return

    entry = {
        "strategy_id":   strategy_id,
        "metrics_start": metrics,
        "metrics_live":  metrics.copy(),
        "status":        "SHADOW",
        "registered":    datetime.now().isoformat(),
        "eval_after":    (datetime.now() + timedelta(weeks=SHADOW_WEEKS)).isoformat(),
        "updates":       [],
    }
    state["challengers"][strategy_id] = entry
    _save_state(state)
    _audit({"timestamp": datetime.now().isoformat(), "action": "register_challenger",
             "strategy_id": strategy_id, "metrics": metrics})
    eval_date = entry["eval_after"][:10]
    print(f"Challenger registrado: {strategy_id} — shadow mode hasta {eval_date}")


def update_challenger_metrics(strategy_id: str, new_metrics: dict):
    """Actualiza métricas del challenger con datos recientes."""
    state = _load_state()
    if strategy_id not in state["challengers"]:
        print(f"ERROR: {strategy_id} no es un challenger activo.")
        sys.exit(1)

    ch = state["challengers"][strategy_id]
    ch["metrics_live"] = new_metrics
    ch["updates"].append({"timestamp": datetime.now().isoformat(), "metrics": new_metrics})
    _save_state(state)
    print(f"Métricas actualizadas para {strategy_id}: PF={new_metrics.get('pf')} DD={new_metrics.get('dd')}%")


def evaluate_challenger(strategy_id: str) -> dict:
    """Compara challenger vs champion. Devuelve veredicto PROMOTE/REJECT/CONTINUE."""
    state = _load_state()
    if strategy_id not in state["challengers"]:
        print(f"ERROR: {strategy_id} no es un challenger activo.")
        sys.exit(1)

    ch      = state["challengers"][strategy_id]
    ch_live = ch["metrics_live"]

    # Elegir el champion con métricas más relevantes
    if not state["champions"]:
        print("Sin champion activo. Promover directamente.")
        return {"verdict": "PROMOTE", "reason": "no_champion"}

    # Tomar el champion más reciente
    champion = sorted(state["champions"].values(), key=lambda x: x["registered"])[-1]
    hm       = champion["metrics"]

    # Comparar métricas
    wins, lines = _metrics_better(ch_live, hm)

    # Verificar si el período de shadow está completo
    eval_after  = ch.get("eval_after", datetime.now().isoformat())
    period_done = datetime.now().isoformat() >= eval_after

    if not period_done:
        remaining = (datetime.fromisoformat(eval_after) - datetime.now()).days
        verdict   = "CONTINUE"
        reason    = f"Shadow period en curso ({remaining} días restantes)"
    elif wins >= PROMOTE_METRICS:
        verdict = "PROMOTE"
        reason  = f"Challenger gana en {wins}/3 métricas"
    else:
        verdict = "REJECT"
        reason  = f"Challenger gana solo en {wins}/3 métricas"

    print(f"\nEvaluación {strategy_id} vs {champion['strategy_id']}:")
    print(f"  Período completo: {'SÍ' if period_done else 'NO'}")
    for line in lines:
        print(f"  {line}")
    print(f"  Veredicto: {verdict} — {reason}")

    _audit({"timestamp": datetime.now().isoformat(), "action": "evaluate",
             "strategy_id": strategy_id, "wins": wins, "verdict": verdict, "reason": reason})
    return {"verdict": verdict, "wins": wins, "reason": reason, "metric_lines": lines}


def promote_challenger(strategy_id: str):
    """Promueve el challenger a champion, retirando el anterior."""
    state = _load_state()
    if strategy_id not in state["challengers"]:
        print(f"ERROR: {strategy_id} no es un challenger activo.")
        sys.exit(1)

    ch = state["challengers"].pop(strategy_id)
    ch["status"]   = "CHAMPION"
    ch["promoted"] = datetime.now().isoformat()
    metrics        = ch["metrics_live"]

    # Retirar champions anteriores
    for sid in list(state["champions"]):
        state["champions"][sid]["status"]  = "RETIRED"
        state["champions"][sid]["retired"] = datetime.now().isoformat()

    state["champions"][strategy_id] = {
        "strategy_id": strategy_id,
        "metrics":     metrics,
        "status":      "CHAMPION",
        "registered":  ch["promoted"],
        "promoted_from_challenger": True,
    }
    _save_state(state)

    msg = f"PROMOTION: {strategy_id} es el nuevo champion (PF={metrics.get('pf')} DD={metrics.get('dd')}%)"
    print(msg)
    _audit({"timestamp": datetime.now().isoformat(), "action": "promote",
             "strategy_id": strategy_id, "metrics": metrics})
    _notify_telegram(msg)


def get_status() -> dict:
    """Estado actual de todos los champions y challengers."""
    state     = _load_state()
    champions = {sid: c for sid, c in state["champions"].items()
                 if c.get("status") == "CHAMPION"}
    return {"champions": champions, "challengers": state["challengers"]}


def _notify_telegram(msg: str):
    notifier = ROOT / "scripts" / "telegram-notifier.py"
    if not notifier.exists():
        return
    subprocess.run(
        [_PYTHON, str(notifier), "--level", "INFO", "--message", msg],
        capture_output=True,
    )


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Champion-Challenger — TradingLab")
    parser.add_argument("--register-champion",  nargs=2,
                        metavar=("STRATEGY_ID", "METRICS_JSON"))
    parser.add_argument("--register-challenger", nargs=2,
                        metavar=("STRATEGY_ID", "METRICS_JSON"))
    parser.add_argument("--update-metrics",     nargs=2,
                        metavar=("STRATEGY_ID", "METRICS_JSON"))
    parser.add_argument("--evaluate",  metavar="STRATEGY_ID")
    parser.add_argument("--promote",   metavar="STRATEGY_ID")
    parser.add_argument("--status",    action="store_true")
    args = parser.parse_args()

    if args.register_champion:
        sid, mj = args.register_champion
        register_champion(sid, json.loads(mj))

    elif args.register_challenger:
        sid, mj = args.register_challenger
        register_challenger(sid, json.loads(mj))

    elif args.update_metrics:
        sid, mj = args.update_metrics
        update_challenger_metrics(sid, json.loads(mj))

    elif args.evaluate:
        evaluate_challenger(args.evaluate)

    elif args.promote:
        promote_challenger(args.promote)

    elif args.status:
        status = get_status()
        print("\nCHAMPIONS activos:")
        for sid, c in status["champions"].items():
            m = c.get("metrics", {})
            print(f"  {sid}  PF={m.get('pf')} DD={m.get('dd')}% Sharpe={m.get('sharpe')}")
        print("\nCHALLENGERS en shadow mode:")
        if not status["challengers"]:
            print("  (ninguno)")
        for sid, ch in status["challengers"].items():
            m = ch.get("metrics_live", {})
            eval_after = ch.get("eval_after", "?")[:10]
            print(f"  {sid}  PF={m.get('pf')} DD={m.get('dd')}%  eval_after={eval_after}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
