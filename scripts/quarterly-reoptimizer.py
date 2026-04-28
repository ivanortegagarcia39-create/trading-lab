#!/usr/bin/env python3
"""
quarterly-reoptimizer.py — Protocolo de reoptimización trimestral de estrategias.

Cada 3 meses verifica si las estrategias activas siguen siendo rentables.
Si detecta decay confirmado, genera alerta y marca para reoptimización SQ.

REGLA CRÍTICA: solo se pueden tocar parámetros numéricos (multiplicadores ATR,
períodos de indicadores). NUNCA la lógica de entrada — eso viola Builder libre.

Uso:
    python scripts/quarterly-reoptimizer.py --run
    python scripts/quarterly-reoptimizer.py --dry-run
    python scripts/quarterly-reoptimizer.py --report
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

ROOT             = Path(__file__).parent.parent
PORTFOLIO_PATH   = ROOT / "results" / "portfolio-selected.json"
VERSIONING_PATH  = ROOT / "results" / "strategies-registry.json"
REPORTS_DIR      = ROOT / "results"
DECAY_LOG        = ROOT / "results" / "decay-log.jsonl"

DECAY_THRESHOLD    = 0.85   # PF_real < 85% de PF_OOS → posible decay
DECAY_WEEKS_MIN    = 4      # semanas consecutivas bajo el umbral para confirmar
QUARTERLY_DAYS     = 91     # ~3 meses

_PYTHON = sys.executable


# ─── I/O ──────────────────────────────────────────────────────────────────────

def _load_portfolio() -> list:
    if not PORTFOLIO_PATH.exists():
        return []
    with open(PORTFOLIO_PATH, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    return data.get("strategies", [])


def _load_registry() -> dict:
    if not VERSIONING_PATH.exists():
        return {}
    with open(VERSIONING_PATH, encoding="utf-8") as f:
        data = json.load(f)
    if "strategies" in data:
        return data["strategies"]
    return data


def _save_registry(registry: dict):
    if not VERSIONING_PATH.exists():
        return
    with open(VERSIONING_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    if "strategies" in raw:
        raw["strategies"] = registry
    else:
        raw = registry
    with open(VERSIONING_PATH, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2, ensure_ascii=False)


def _log_decay(entry: dict):
    DECAY_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(DECAY_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ─── Análisis de decay ────────────────────────────────────────────────────────

def _check_decay(strategy_id: str, strategy_data: dict) -> dict:
    """
    Evalúa si una estrategia muestra decay.
    Busca el historial de PF en producción de los últimos 3 meses.
    """
    version_activa = strategy_data.get("version_activa", "v1")
    versiones      = strategy_data.get("versiones", {})
    vdata          = versiones.get(version_activa, {})
    metricas       = vdata.get("metricas", {})
    pf_oos         = float(metricas.get("pf", 0.0))

    # Historial de producción: lista de {"fecha": ..., "pf": ...}
    produccion = vdata.get("produccion_history", [])

    if not produccion or pf_oos == 0:
        return {"strategy_id": strategy_id, "status": "SIN_DATOS", "pf_oos": pf_oos}

    # Filtrar últimos QUARTERLY_DAYS días
    cutoff  = (datetime.now() - timedelta(days=QUARTERLY_DAYS)).strftime("%Y-%m-%d")
    recent  = [p for p in produccion if p.get("fecha", "") >= cutoff]

    if len(recent) < DECAY_WEEKS_MIN:
        return {
            "strategy_id": strategy_id,
            "status":      "DATOS_INSUFICIENTES",
            "pf_oos":      pf_oos,
            "semanas":     len(recent),
        }

    # Semanas bajo el umbral
    threshold     = pf_oos * DECAY_THRESHOLD
    weeks_below   = [p for p in recent if float(p.get("pf", 999)) < threshold]
    decay_pct     = len(weeks_below) / len(recent)

    if len(weeks_below) >= DECAY_WEEKS_MIN:
        pf_avg = sum(float(p.get("pf", 0)) for p in recent) / len(recent)
        return {
            "strategy_id":    strategy_id,
            "status":         "DECAY",
            "pf_oos":         pf_oos,
            "pf_promedio_3m": round(pf_avg, 3),
            "threshold":      round(threshold, 3),
            "semanas_below":  len(weeks_below),
            "semanas_total":  len(recent),
            "decay_pct":      round(decay_pct, 2),
        }

    pf_avg = sum(float(p.get("pf", 0)) for p in recent) / len(recent)
    return {
        "strategy_id":    strategy_id,
        "status":         "OK",
        "pf_oos":         pf_oos,
        "pf_promedio_3m": round(pf_avg, 3),
        "semanas_total":  len(recent),
    }


# ─── Acciones ante decay ──────────────────────────────────────────────────────

def _mark_for_reoptimization(strategy_id: str, decay_info: dict,
                              registry: dict, dry_run: bool) -> bool:
    """Marca la estrategia para reoptimización en el registry."""
    if strategy_id not in registry:
        return False

    nota = (
        f"DECAY detectado {datetime.now().strftime('%Y-%m-%d')}: "
        f"PF_OOS={decay_info['pf_oos']:.3f} "
        f"PF_3m={decay_info.get('pf_promedio_3m', '?')} "
        f"({decay_info.get('semanas_below', '?')} semanas bajo umbral {decay_info.get('threshold', '?')}). "
        "Pendiente de reoptimización SQ (solo parámetros numéricos)."
    )

    if not dry_run:
        version_activa = registry[strategy_id].get("version_activa", "v1")
        registry[strategy_id]["versiones"][version_activa]["estado"] = "REOPTIMIZACION_PENDIENTE"
        registry[strategy_id]["versiones"][version_activa]["decay_nota"] = nota
        _save_registry(registry)

    return True


def _notify_telegram(msg: str, level: str = "WARNING", dry_run: bool = False):
    notifier = ROOT / "scripts" / "telegram-notifier.py"
    if not notifier.exists() or dry_run:
        print(f"  [Telegram {level}] {msg}")
        return
    subprocess.run(
        [_PYTHON, str(notifier), "--level", level, "--message", msg],
        capture_output=True,
    )


def _register_kg(strategy_id: str, decay_info: dict, dry_run: bool):
    kg = ROOT / "scripts" / "knowledge-graph.py"
    if not kg.exists() or dry_run:
        return
    data = json.dumps({
        "event":       "decay_detected",
        "strategy_id": strategy_id,
        "decay_info":  decay_info,
        "date":        datetime.now().isoformat(),
    })
    subprocess.run(
        [_PYTHON, str(kg), "--mode", "add-build", "--data", data],
        capture_output=True,
    )


# ─── Generación de informe ────────────────────────────────────────────────────

def _generate_report(results: list, date_str: str, dry_run: bool) -> Path:
    lines = [
        f"# Informe Trimestral de Reoptimización — {date_str}",
        "",
        f"Período analizado: últimos {QUARTERLY_DAYS} días  ",
        f"Umbral de decay: PF_real < {DECAY_THRESHOLD:.0%} de PF_OOS durante {DECAY_WEEKS_MIN}+ semanas  ",
        "",
        "## Resumen",
        "",
    ]

    decay_list  = [r for r in results if r["status"] == "DECAY"]
    ok_list     = [r for r in results if r["status"] == "OK"]
    nodata_list = [r for r in results if r["status"] in ("SIN_DATOS", "DATOS_INSUFICIENTES")]

    lines.append(f"| Estado | Count |")
    lines.append(f"|---|---|")
    lines.append(f"| OK (sin decay) | {len(ok_list)} |")
    lines.append(f"| DECAY confirmado | {len(decay_list)} |")
    lines.append(f"| Sin datos suficientes | {len(nodata_list)} |")
    lines.append("")

    if decay_list:
        lines.append("## Estrategias con DECAY confirmado")
        lines.append("")
        for r in decay_list:
            lines.append(f"### {r['strategy_id']}")
            lines.append(f"- PF OOS backtest: {r['pf_oos']:.3f}")
            lines.append(f"- PF promedio 3m:  {r.get('pf_promedio_3m', '?')}")
            lines.append(f"- Umbral (85%):    {r.get('threshold', '?')}")
            lines.append(f"- Semanas bajo:    {r.get('semanas_below', '?')} / {r.get('semanas_total', '?')}")
            lines.append(f"- Acción:          Reoptimización SQ (solo parámetros numéricos)")
            lines.append(f"- **REGLA**: no cambiar la lógica de entrada — solo ATR multiplier, períodos")
            lines.append("")

    if ok_list:
        lines.append("## Estrategias OK")
        lines.append("")
        for r in ok_list:
            lines.append(f"- {r['strategy_id']}  PF_3m={r.get('pf_promedio_3m', '?')}  "
                          f"vs OOS={r['pf_oos']:.3f}")
        lines.append("")

    report_path = REPORTS_DIR / f"quarterly-report-{date_str}.md"
    if not dry_run:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(lines), encoding="utf-8")

    return report_path


# ─── Proceso principal ────────────────────────────────────────────────────────

def run_review(dry_run: bool = False) -> list:
    """Ejecuta la revisión trimestral completa."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{'[DRY-RUN] ' if dry_run else ''}REVISION TRIMESTRAL — {date_str}")
    print("=" * 55)

    portfolio = _load_portfolio()
    registry  = _load_registry()

    if not portfolio and not registry:
        print("Sin estrategias activas en el portfolio — nada que revisar.")
        return []

    # Usar portfolio si existe, sino estrategias en registry con estado activo
    if portfolio:
        strategy_ids = [s.get("strategy_id", s) if isinstance(s, dict) else s
                        for s in portfolio]
    else:
        strategy_ids = [sid for sid, sd in registry.items()
                        if str(sd.get("versiones", {}).get(
                            sd.get("version_activa", "v1"), {}).get("estado", "")
                        ).upper() in ("ACTIVO", "PRODUCCION", "FUNDED")]

    print(f"\n{len(strategy_ids)} estrategias en portfolio activo.")

    results  = []
    decaying = []

    for sid in strategy_ids:
        sdata  = registry.get(sid, {})
        result = _check_decay(sid, sdata)
        results.append(result)

        status = result["status"]
        pf_str = f"PF_OOS={result.get('pf_oos', '?'):.3f}" if result.get("pf_oos") else ""
        print(f"  {sid:<25} [{status}]  {pf_str}")

        if status == "DECAY":
            decaying.append(result)
            _log_decay({"timestamp": datetime.now().isoformat(), **result})
            _mark_for_reoptimization(sid, result, registry, dry_run)
            msg = (f"Decay confirmado en {sid}: "
                   f"PF_3m={result.get('pf_promedio_3m', '?')} vs "
                   f"PF_OOS={result.get('pf_oos', '?'):.3f} "
                   f"({result.get('semanas_below', '?')} semanas bajo {DECAY_THRESHOLD:.0%})")
            _notify_telegram(msg, level="WARNING", dry_run=dry_run)
            _register_kg(sid, result, dry_run)

    # Generar informe
    report_path = _generate_report(results, date_str, dry_run)

    print(f"\nResumen: {len(decaying)} con DECAY / {len(results)} analizadas")
    if decaying:
        print(f"  Acción: reoptimizar parámetros en SQ (sin cambiar lógica de entrada)")
    print(f"  Informe: {report_path}")

    return results


def show_last_report():
    """Muestra el último informe trimestral disponible."""
    reports = sorted(REPORTS_DIR.glob("quarterly-report-*.md"), reverse=True)
    if not reports:
        print("Sin informes trimestrales disponibles.")
        return
    last = reports[0]
    print(f"\nÚltimo informe: {last.name}")
    print("-" * 55)
    print(last.read_text(encoding="utf-8")[:2000])


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Quarterly Reoptimizer — TradingLab")
    parser.add_argument("--run",     action="store_true", help="Ejecutar revisión trimestral")
    parser.add_argument("--dry-run", action="store_true", help="Simular sin aplicar cambios")
    parser.add_argument("--report",  action="store_true", help="Ver último informe trimestral")
    args = parser.parse_args()

    if args.run:
        run_review(dry_run=False)
    elif args.dry_run:
        run_review(dry_run=True)
    elif args.report:
        show_last_report()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
