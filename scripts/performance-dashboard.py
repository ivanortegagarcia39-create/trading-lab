#!/usr/bin/env python3
"""
performance-dashboard.py — Dashboard completo del sistema TradingLab en tiempo real.

Uso:
    python scripts/performance-dashboard.py
    python scripts/performance-dashboard.py --watch
    python scripts/performance-dashboard.py --watch --interval 30
    python scripts/performance-dashboard.py --compact
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT    = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"
RESULTS = ROOT / "results"
CONFIG  = ROOT / "config"


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _fmt_date(path: Path) -> str:
    if not path.exists():
        return "—"
    try:
        return datetime.fromtimestamp(os.path.getmtime(str(path))).strftime("%Y-%m-%d")
    except Exception:
        return "—"


# ── Recolectores de datos ──────────────────────────────────────────────────

def _pipeline_info() -> dict:
    lock     = RESULTS / "pipeline.lock"
    build    = lock.read_text(encoding="utf-8").strip() if lock.exists() else "ninguno"
    # Cola de builds
    queue_script = SCRIPTS / "build-queue-manager.py"
    cola = []
    if queue_script.exists():
        try:
            r = subprocess.run(
                [sys.executable, str(queue_script), "list"],
                capture_output=True, text=True, timeout=10,
            )
            for line in r.stdout.splitlines()[:5]:
                if line.strip() and not line.startswith("#"):
                    cola.append(line.strip())
        except Exception:
            pass
    # Ultimo build
    reports = sorted(RESULTS.glob("build-*-report.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    ultimo  = reports[0].stem if reports else "—"
    return {"build": build, "cola": cola, "ultimo": ultimo}


def _portfolio_info() -> dict:
    port = _read_json(RESULTS / "portfolio-selected.json")
    if not port:
        return {"estrategias": 0, "dd": "—", "pf": "—", "semaforo": "GRIS"}
    metricas = port.get("metricas_portfolio", {})
    dd  = metricas.get("dd_combinado", "—")
    pf  = metricas.get("pf_medio",     "—")
    n   = metricas.get("estrategias",  len(port.get("portfolio", [])))

    # Semaforo
    semaforo = "VERDE"
    try:
        if float(dd) > 10:
            semaforo = "ROJO"
        elif float(dd) > 7:
            semaforo = "AMARILLO"
    except (TypeError, ValueError):
        semaforo = "GRIS"

    return {"estrategias": n, "dd": dd, "pf": pf, "semaforo": semaforo}


def _autoaprendizaje_info() -> dict:
    result = {}

    # KG
    kg_db = ROOT / ".kuzu" / "tradinglab.db"
    if kg_db.exists():
        kg_script = SCRIPTS / "knowledge-graph.py"
        builds = strategies = 0
        if kg_script.exists():
            try:
                r = subprocess.run(
                    [sys.executable, str(kg_script), "stats"],
                    capture_output=True, text=True, timeout=15,
                )
                for line in (r.stdout + r.stderr).splitlines():
                    m = re.search(r"build\w*\s*[:\-]?\s*(\d+)", line, re.IGNORECASE)
                    if m:
                        builds = int(m.group(1))
                    m = re.search(r"strateg\w*\s*[:\-]?\s*(\d+)", line, re.IGNORECASE)
                    if m:
                        strategies = int(m.group(1))
            except Exception:
                pass
        result["kg"] = f"{builds} builds, {strategies} estrategias"
    else:
        result["kg"] = "no inicializado"

    # Bayesian
    bc = CONFIG / "bayesian-criteria.json"
    result["bayesian"] = _fmt_date(bc) if bc.exists() else "—"

    # Drift
    drift = _read_json(RESULTS / "drift-detection.json")
    if drift:
        prob = drift.get("bocpd", {}).get("last_prob", 0.0)
        result["drift"] = f"BOCPD {float(prob):.3f}"
    else:
        result["drift"] = "sin datos"

    # Champion-Challenger
    cc = _read_json(RESULTS / "champion-challenger.json")
    if cc:
        result["cc"] = f"{len(cc.get('champions', {}))} champions, {len(cc.get('challengers', {}))} challengers"
    else:
        result["cc"] = "sin datos"

    # Self-improvement ultimo ciclo
    si_log = CONFIG / "self-improvement-log.jsonl"
    if si_log.exists():
        try:
            lines = [l for l in si_log.read_text(encoding="utf-8").splitlines() if l.strip()]
            if lines:
                last = json.loads(lines[-1])
                result["si"] = last.get("timestamp", "—")[:10]
            else:
                result["si"] = "sin registros"
        except Exception:
            result["si"] = "—"
    else:
        result["si"] = "nunca"

    return result


def _sistema_info() -> dict:
    # Scripts operativos
    n_scripts = len(list((ROOT / "scripts").glob("*.py")))

    # ChromaDB chunks
    chromadb_n = "—"
    chroma_dir = ROOT / ".chromadb"
    if chroma_dir.exists():
        chromadb_n = "909+"  # ultimo recuento conocido

    # Telegram
    tg_script = SCRIPTS / "telegram-notifier.py"
    telegram = "activo" if tg_script.exists() else "inactivo"

    # SQ
    sq_running = "—"
    try:
        r = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq StrategyQuantX.exe"],
            capture_output=True, text=True, timeout=5,
        )
        sq_running = "corriendo" if "StrategyQuantX.exe" in r.stdout else "parado"
    except Exception:
        pass

    return {
        "scripts":  n_scripts,
        "chromadb": chromadb_n,
        "telegram": telegram,
        "sq":       sq_running,
    }


def _alertas_activas() -> list:
    alertas = []
    health = _read_json(RESULTS / "system-health.json")
    if health:
        s = health.get("summary", {})
        if s.get("fail", 0) > 0:
            alertas.append(f"Health FAIL: {s['fail']} checks fallidos")
        if s.get("warn", 0) > 3:
            alertas.append(f"Health WARN: {s['warn']} advertencias")

    drift = _read_json(RESULTS / "drift-detection.json")
    if drift:
        crit = sum(1 for d in drift.get("addm", {}).values()
                   if d.get("level") == "CRITICAL")
        if crit:
            alertas.append(f"Drift CRITICO detectado en {crit} metrica(s)")

    port = _read_json(RESULTS / "portfolio-selected.json")
    if port:
        metricas = port.get("metricas_portfolio", {})
        try:
            if float(metricas.get("dd_combinado", 0)) > 10:
                alertas.append("DD portfolio > 10% — revisar estrategias")
        except (TypeError, ValueError):
            pass

    return alertas


# ── Render ─────────────────────────────────────────────────────────────────

_SEMAFORO = {"VERDE": "[VERDE]", "AMARILLO": "[AMARILLO]", "ROJO": "[ROJO]", "GRIS": "[GRIS]"}


def render(compact: bool = False) -> str:
    now       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pipeline  = _pipeline_info()
    portfolio = _portfolio_info()
    auto      = _autoaprendizaje_info()
    sistema   = _sistema_info()
    alertas   = _alertas_activas()

    W = 55
    sep = "=" * W

    cola_str = ", ".join(pipeline["cola"][:3]) if pipeline["cola"] else "vacia"

    sem = _SEMAFORO.get(portfolio["semaforo"], "[?]")

    if compact:
        lines = [
            sep,
            f"  TRADINGLAB Dashboard — {now}",
            sep,
            f"  Build: {pipeline['build']:<15} Cola: {cola_str}",
            f"  Portfolio: {portfolio['estrategias']} estrategias  DD:{portfolio['dd']}%  PF:{portfolio['pf']}  {sem}",
            f"  KG: {auto['kg']}  Drift: {auto['drift']}",
            f"  Scripts: {sistema['scripts']}  SQ: {sistema['sq']}  TG: {sistema['telegram']}",
        ]
        if alertas:
            lines.append(f"  ALERTAS: {len(alertas)}")
            for a in alertas:
                lines.append(f"    ! {a}")
        else:
            lines.append("  Sin alertas activas")
        lines.append(sep)
        return "\n".join(lines)

    lines = [
        sep,
        f"  TRADINGLAB — Dashboard v8.1 — {now}",
        sep,
        "",
        "PIPELINE:",
        f"  Build activo  : {pipeline['build']}",
        f"  Cola          : {cola_str}",
        f"  Ultimo build  : {pipeline['ultimo']}",
        "",
        "PORTFOLIO:",
        f"  Estrategias   : {portfolio['estrategias']}",
        f"  DD combinado  : {portfolio['dd']}%",
        f"  PF medio      : {portfolio['pf']}",
        f"  Semaforo      : {sem}",
        "",
        "AUTOAPRENDIZAJE:",
        f"  KG            : {auto['kg']}",
        f"  Bayesian      : ultimo ajuste {auto['bayesian']}",
        f"  Drift         : {auto['drift']}",
        f"  Champ-Challng : {auto['cc']}",
        f"  Self-improve  : {auto['si']}",
        "",
        "SISTEMA:",
        f"  Scripts       : {sistema['scripts']} operativos",
        f"  ChromaDB      : {sistema['chromadb']} chunks",
        f"  Telegram      : {sistema['telegram']}",
        f"  SQ            : {sistema['sq']}",
        "",
        "ALERTAS ACTIVAS:",
    ]
    if alertas:
        for a in alertas:
            lines.append(f"  ! {a}")
    else:
        lines.append("  Sin alertas")
    lines.append("")
    lines.append(sep)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Performance Dashboard — TradingLab")
    parser.add_argument("--watch",    action="store_true", help="Actualizar en bucle")
    parser.add_argument("--interval", type=int, default=60, help="Intervalo en segundos (default: 60)")
    parser.add_argument("--compact",  action="store_true", help="Vista compacta")
    args = parser.parse_args()

    if args.watch:
        try:
            while True:
                os.system("cls" if os.name == "nt" else "clear")
                print(render(args.compact))
                print(f"\n  Actualizando cada {args.interval}s — Ctrl+C para salir")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nDashboard detenido.")
    else:
        print(render(args.compact))

    return 0


if __name__ == "__main__":
    sys.exit(main())
