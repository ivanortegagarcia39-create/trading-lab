#!/usr/bin/env python3
"""
portfolio-rebalancer.py — Rebalancea el portfolio cuando una estrategia entra en decay

Lee:
    results/portfolio-selected.json   — estrategias activas
    results/strategies-registry.json  — metricas actuales y cola de espera

Uso:
    python scripts/portfolio-rebalancer.py
    python scripts/portfolio-rebalancer.py --dry-run
"""

import argparse
import json
import math
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
RESULTS_DIR = ROOT / "results"
PORTFOLIO_PATH = RESULTS_DIR / "portfolio-selected.json"
REGISTRY_PATH  = RESULTS_DIR / "strategies-registry.json"

# Umbrales de decay desde config
try:
    _cfg = json.loads((ROOT / "config" / "pipeline-config.json").read_text(encoding="utf-8"))
    CORR_MAX       = _cfg["portfolio"]["correlacion_maxima"]
    DD_MAX_COMBINED = _cfg["portfolio"]["dd_combinado_maximo"]
    PF_DECAY_MIN   = _cfg["retester_12b"]["pf_oos_minimo"]
except Exception:
    CORR_MAX        = 0.5
    DD_MAX_COMBINED = 12.0
    PF_DECAY_MIN    = 1.3

ZSCORE_DECAY_THRESHOLD = -2.0


def _load(path: Path) -> dict | list:
    if not path.exists():
        print(f"ERROR: {path} no encontrado.")
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data: dict | list, dry_run: bool):
    if dry_run:
        print(f"  [DRY-RUN] No se escribe: {path}")
        return
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Guardado: {path}")


def _is_in_decay(strategy: dict) -> tuple[bool, str]:
    metrics = strategy.get("metrics", {})
    status  = strategy.get("status", "active")

    if status == "decay":
        return True, "marcada como decay"

    pf_rolling = metrics.get("pf_rolling_4w", metrics.get("pf", 0))
    zscore     = metrics.get("zscore_pf", 0)

    if pf_rolling < PF_DECAY_MIN:
        return True, f"PF rolling {pf_rolling:.2f} < {PF_DECAY_MIN}"
    if zscore <= ZSCORE_DECAY_THRESHOLD:
        return True, f"Z-Score PF {zscore:.2f} <= {ZSCORE_DECAY_THRESHOLD}"

    return False, ""


def _pearson(a: list[float], b: list[float]) -> float:
    n = len(a)
    if n < 2:
        return 0.0
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da  = math.sqrt(sum((x - ma) ** 2 for x in a))
    db  = math.sqrt(sum((y - mb) ** 2 for y in b))
    return num / (da * db) if da * db > 0 else 0.0


def _check_correlation(candidate: dict, active_portfolio: list[dict]) -> tuple[bool, float]:
    """Devuelve (ok, max_corr). Usa daily_pnl si disponible, si no retorna ok=True."""
    cand_returns = candidate.get("daily_pnl", [])
    if not cand_returns or not active_portfolio:
        return True, 0.0

    max_corr = 0.0
    for s in active_portfolio:
        other_returns = s.get("daily_pnl", [])
        if not other_returns:
            continue
        # Alinear por longitud minima
        n = min(len(cand_returns), len(other_returns))
        if n < 5:
            continue
        corr = abs(_pearson(cand_returns[-n:], other_returns[-n:]))
        max_corr = max(max_corr, corr)

    return max_corr <= CORR_MAX, round(max_corr, 4)


def _check_dollar_monoculture(candidate: dict, active_portfolio: list[dict]) -> bool:
    """Verifica que no haya mas de max_activos_factor_dolar activos con USD como base/quote."""
    try:
        _cfg = json.loads((ROOT / "config" / "pipeline-config.json").read_text(encoding="utf-8"))
        max_usd = _cfg["portfolio"]["max_activos_factor_dolar"]
    except Exception:
        max_usd = 2

    cand_symbol = candidate.get("symbol", "")
    if "USD" not in cand_symbol.upper():
        return True

    usd_count = sum(
        1 for s in active_portfolio
        if "USD" in s.get("symbol", "").upper()
    )
    return usd_count < max_usd


def _hrp_weights(strategies: list[dict]) -> dict[str, float]:
    """Pesos HRP simplificado (1/volatilidad normalizado)."""
    vols = {}
    for s in strategies:
        sid = s.get("id", s.get("file", "?"))
        returns = s.get("daily_pnl", [])
        if len(returns) >= 2:
            mean = sum(returns) / len(returns)
            vol = math.sqrt(sum((x - mean) ** 2 for x in returns) / (len(returns) - 1))
            vols[sid] = vol if vol > 0 else 1.0
        else:
            vols[sid] = 1.0

    inv_vol = {k: 1.0 / v for k, v in vols.items()}
    total   = sum(inv_vol.values())
    return {k: round(v / total, 4) for k, v in inv_vol.items()}


def _send_telegram(message: str, level: str = "INFO", dry_run: bool = False):
    notifier = ROOT / "scripts" / "telegram-notifier.py"
    if not notifier.exists():
        print(f"  [{level}] {message}")
        return
    cmd = [sys.executable, str(notifier), "--level", level, "--message", message]
    if dry_run:
        cmd.append("--dry-run")
    subprocess.run(cmd, capture_output=True)


def main():
    parser = argparse.ArgumentParser(description="Portfolio Rebalancer — TradingLab")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simular sin aplicar cambios ni escribir archivos")
    args = parser.parse_args()

    dry_run = args.dry_run
    if dry_run:
        print("[DRY-RUN] Simulacion — no se modificara ningun archivo\n")

    portfolio_data = _load(PORTFOLIO_PATH)
    registry_data  = _load(REGISTRY_PATH)

    # Normalizar estructura
    if isinstance(portfolio_data, dict):
        active_portfolio = portfolio_data.get("portfolio", [])
    else:
        active_portfolio = portfolio_data

    if isinstance(registry_data, dict):
        all_strategies = registry_data.get("strategies", registry_data.get("registry", []))
        waiting_queue  = registry_data.get("waiting_queue", [])
    else:
        all_strategies = registry_data
        waiting_queue  = []

    print(f"Portfolio activo : {len(active_portfolio)} estrategias")
    print(f"Cola de espera   : {len(waiting_queue)} candidatas")
    print(f"Registry total   : {len(all_strategies)} estrategias\n")

    # ── Detectar estrategias en decay ─────────────────────────────────────
    decayed = []
    healthy = []
    for s in active_portfolio:
        in_decay, reason = _is_in_decay(s)
        if in_decay:
            decayed.append((s, reason))
        else:
            healthy.append(s)

    if not decayed:
        print("No hay estrategias en decay. Portfolio saludable.")
        _send_telegram("Portfolio rebalancer: sin cambios — todas las estrategias saludables",
                       dry_run=dry_run)
        return

    print(f"Estrategias en decay: {len(decayed)}")
    for s, reason in decayed:
        print(f"  - {s.get('id', '?')} ({s.get('symbol', '?')}): {reason}")

    changes = []

    # ── Procesar cada estrategia en decay ─────────────────────────────────
    for decayed_s, decay_reason in decayed:
        sid = decayed_s.get("id", "?")
        print(f"\nProcesando decay: {sid}")

        # Marcar como retirada en el registry
        for s in all_strategies:
            if s.get("id") == sid:
                s["status"] = "retirada"
                s["retired_at"] = datetime.now().isoformat()
                s["retire_reason"] = decay_reason
                break

        # Buscar candidata en cola de espera
        replacement_found = False
        for candidate in sorted(waiting_queue, key=lambda x: x.get("score", 0), reverse=True):
            cid = candidate.get("id", "?")

            # Verificar correlacion
            corr_ok, max_corr = _check_correlation(candidate, healthy)
            if not corr_ok:
                print(f"  Candidata {cid}: descartada (corr {max_corr:.2f} > {CORR_MAX})")
                continue

            # Verificar monocultura USD
            if not _check_dollar_monoculture(candidate, healthy):
                print(f"  Candidata {cid}: descartada (monocultura USD)")
                continue

            # Candidata valida
            candidate["status"] = "active"
            candidate["added_at"] = datetime.now().isoformat()
            candidate["replaces"] = sid
            healthy.append(candidate)
            waiting_queue.remove(candidate)
            replacement_found = True

            changes.append({
                "action": "replace",
                "retired": sid,
                "added": cid,
                "reason": decay_reason,
                "max_corr": max_corr,
            })
            print(f"  Reemplazada por: {cid} (corr max {max_corr:.2f})")
            break

        if not replacement_found:
            changes.append({
                "action": "slot_vacant",
                "retired": sid,
                "reason": decay_reason,
                "note": "sin candidatas validas en cola de espera",
            })
            print(f"  Sin candidata valida — slot marcado como VACANTE")

    # ── Recalcular pesos HRP ───────────────────────────────────────────────
    weights = _hrp_weights(healthy)
    for s in healthy:
        sid = s.get("id", s.get("file", "?"))
        s["peso_hrp"] = weights.get(sid, round(1.0 / max(len(healthy), 1), 4))

    # ── Guardar portfolio actualizado ──────────────────────────────────────
    new_portfolio = {
        "updated_at": datetime.now().isoformat(),
        "portfolio": healthy,
        "metricas_portfolio": {
            "estrategias": len(healthy),
        },
        "changes": changes,
    }

    _save(PORTFOLIO_PATH, new_portfolio, dry_run)
    _save(REGISTRY_PATH, {"strategies": all_strategies, "waiting_queue": waiting_queue}, dry_run)

    # ── Notificar via Telegram ─────────────────────────────────────────────
    retiradas = [c["retired"] for c in changes]
    añadidas  = [c["added"] for c in changes if c["action"] == "replace"]
    vacantes  = [c["retired"] for c in changes if c["action"] == "slot_vacant"]

    msg_parts = [f"Portfolio rebalanceado."]
    if retiradas:
        msg_parts.append(f"Retiradas: {', '.join(retiradas)}.")
    if añadidas:
        msg_parts.append(f"Añadidas: {', '.join(añadidas)}.")
    if vacantes:
        msg_parts.append(f"Slots vacantes: {len(vacantes)} — revisar queue.")

    level = "WARNING" if vacantes else "INFO"
    _send_telegram(" ".join(msg_parts), level=level, dry_run=dry_run)

    # ── Resumen ────────────────────────────────────────────────────────────
    print(f"\n{'='*50}")
    print(f"Rebalanceo completado")
    print(f"  Portfolio activo : {len(healthy)} estrategias")
    print(f"  Reemplazos       : {len(añadidas)}")
    print(f"  Slots vacantes   : {len(vacantes)}")
    for c in changes:
        if c["action"] == "replace":
            print(f"  {c['retired']} → {c['added']}")
        else:
            print(f"  {c['retired']} → VACANTE ({c['note']})")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
