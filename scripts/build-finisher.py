#!/usr/bin/env python3
"""
build-finisher.py — Coordina todo el pipeline post-build automaticamente.
Se ejecuta cuando un build termina en SQ y los CSVs han sido exportados.

Uso:
    python scripts/build-finisher.py --build 11 --activo XAUUSD --results-folder results/
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT    = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"


def _run_quiet(cmd: list) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def _notify(level: str, msg: str) -> None:
    notifier = SCRIPTS / "telegram-notifier.py"
    if not notifier.exists():
        return
    subprocess.run(
        [sys.executable, str(notifier), "--level", level, "--message", msg],
        capture_output=True
    )


def _header(text: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def _step(n: int, text: str) -> None:
    print(f"\n[{n}] {text}")


def _ok(text: str) -> None:
    print(f"    OK  {text}")


def _warn(text: str) -> None:
    print(f"    WARN  {text}")


def check_csv_files(results_folder: Path) -> list:
    csvs = sorted(results_folder.rglob("Strategy*.csv"))
    return csvs


def run_evaluator(results_folder: Path) -> dict:
    evaluator = SCRIPTS / "evaluator-assistant.py"
    if not evaluator.exists():
        _warn("evaluator-assistant.py no encontrado")
        return {}
    result = _run_quiet([sys.executable, str(evaluator),
                         "--results-folder", str(results_folder)])
    # Leer resultados del JSON generado
    gate_file = ROOT / "results" / "evaluation-gate-results.json"
    if gate_file.exists():
        try:
            return json.loads(gate_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def run_build_analyzer(build_n: int, activo: str, results_folder: Path) -> None:
    analyzer = SCRIPTS / "build-analyzer.py"
    if not analyzer.exists():
        _warn("build-analyzer.py no encontrado — saltando analisis")
        return
    _run_quiet([sys.executable, str(analyzer),
                "--build", str(build_n),
                "--activo", activo,
                "--results-folder", str(results_folder)])
    _ok(f"Analisis guardado en results/build-{build_n}-analysis.md")


def update_queue(activo: str) -> None:
    qm = SCRIPTS / "build-queue-manager.py"
    if not qm.exists():
        _warn("build-queue-manager.py no encontrado")
        return
    _run_quiet([sys.executable, str(qm), "complete", activo])
    _ok(f"Cola actualizada — {activo} marcado como COMPLETADO")


def run_strategy_versioning(results_folder: Path) -> None:
    sv = SCRIPTS / "strategy-versioning.py"
    if not sv.exists():
        _warn("strategy-versioning.py no encontrado")
        return
    gate_file = ROOT / "results" / "evaluation-gate-results.json"
    if not gate_file.exists():
        _warn("evaluation-gate-results.json no encontrado — saltando versioning")
        return
    _run_quiet([sys.executable, str(sv), "--register",
                "--gate-results", str(gate_file)])
    _ok("Estrategias aprobadas registradas en strategies-registry.json")


def run_knowledge_reindex() -> None:
    kb = SCRIPTS / "knowledge-base.py"
    if not kb.exists():
        _warn("knowledge-base.py no encontrado")
        return
    _run_quiet([sys.executable, str(kb), "re-index"])
    _ok("ChromaDB re-indexado con nuevos resultados")


def run_kg_integration(build_n: int, activo: str, gate_results: dict) -> None:
    """Inserta build y estrategias aprobadas en el Knowledge Graph."""
    kg_script = SCRIPTS / "knowledge-graph.py"
    if not kg_script.exists():
        _warn("knowledge-graph.py no encontrado — saltando KG")
        return

    # Inicializar KG si no existe
    _run_quiet([sys.executable, str(kg_script), "--mode", "init"])

    # Insertar el build
    build_data = json.dumps({
        "build_id":  f"B{str(build_n).zfill(2)}",
        "activo":    activo,
        "timeframe": "H1",
        "fecha":     datetime.now().strftime("%Y-%m-%d"),
        "spread":    0.0,
        "estado":    "COMPLETADO",
    })
    _run_quiet([sys.executable, str(kg_script), "--mode", "add-build", "--data", build_data])

    # Insertar estrategias que pasaron el EvalGate
    strategies = gate_results.get("strategies", [])
    inserted = 0
    for s in strategies:
        if str(s.get("resultado", "")).upper() != "PASA":
            continue
        sid = str(s.get("id", s.get("strategy_id", "")))
        if not sid:
            continue
        s_data = json.dumps({
            "strategy_id": sid,
            "build_id":    f"B{str(build_n).zfill(2)}",
            "pf":          float(s.get("pf", 0.0)),
            "dd":          float(s.get("dd", 0.0)),
            "trades":      int(s.get("trades", 0)),
            "win_rate":    float(s.get("win_rate", 0.0)),
            "sharpe":      float(s.get("sharpe", 0.0)),
            "estado":      "APROBADA",
        })
        _run_quiet([sys.executable, str(kg_script), "--mode", "add-strategy", "--data", s_data])

        # Registrar decisión de EvalGate
        gate_args = [
            sys.executable, str(kg_script), "--mode", "add-build",  # reused via python import
        ]
        # Llamar directamente via import para la gate decision
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("knowledge_graph", str(kg_script))
            kg_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(kg_mod)
            kg_mod.add_gate_decision(
                strategy_id=sid,
                gate_num=1,
                gate_name="EvalGate",
                resultado="PASA",
                criterio=str(s.get("criterio", "")),
            )
        except Exception:
            pass
        inserted += 1

    _ok(f"KG: build B{str(build_n).zfill(2)} y {inserted} estrategias insertados")


def run_thompson_sampling(activo: str, pasan: int) -> None:
    ts = SCRIPTS / "thompson-sampling.py"
    if not ts.exists():
        _warn("thompson-sampling.py no encontrado — saltando")
        return
    success = "1" if pasan >= 1 else "0"
    try:
        _run_quiet([sys.executable, str(ts), "--update-asset", activo, "H1", success])
        _ok(f"Thompson Sampling actualizado — {activo} H1 success={success}")
    except Exception as e:
        _warn(f"Thompson Sampling fallo: {e}")


def run_lessons_analyzer() -> None:
    la = SCRIPTS / "lessons-analyzer.py"
    if not la.exists():
        _warn("lessons-analyzer.py no encontrado — saltando")
        return
    try:
        _run_quiet([sys.executable, str(la), "--no-ollama"])
        _ok("Lessons Analyzer ejecutado")
    except Exception as e:
        _warn(f"Lessons Analyzer fallo: {e}")


def run_concept_drift() -> None:
    cd = SCRIPTS / "concept-drift-detector.py"
    if not cd.exists():
        _warn("concept-drift-detector.py no encontrado — saltando")
        return
    try:
        _run_quiet([sys.executable, str(cd), "--check"])
        _ok("Concept Drift check ejecutado")
    except Exception as e:
        _warn(f"Concept Drift fallo: {e}")


def run_champion_challenger(build_n: int, activo: str, pasan: int) -> None:
    cc = SCRIPTS / "champion-challenger.py"
    if not cc.exists():
        _warn("champion-challenger.py no encontrado — saltando")
        return
    try:
        _run_quiet([sys.executable, str(cc),
                    "--update-build", str(build_n), activo, str(pasan)])
        _ok(f"Champion Challenger actualizado — build {build_n} {activo} aprobadas={pasan}")
    except Exception as e:
        _warn(f"Champion Challenger fallo: {e}")


OBSIDIAN_DECISIONS = Path(r"C:\Users\ivano\Documents\TradingLab\TradingLab\06_Decisions")


def run_obsidian_report(build_n: int, activo: str, gate: dict) -> None:
    if not OBSIDIAN_DECISIONS.exists():
        _warn(f"Carpeta Obsidian no encontrada: {OBSIDIAN_DECISIONS} — saltando nota")
        return

    try:
        pasan = gate.get("pasan", 0)
        total = gate.get("total", 0)
        strategies = gate.get("strategies", [])
        aprobadas = [s for s in strategies if str(s.get("resultado", "")).upper() == "PASA"]

        pf_avg = round(sum(float(s.get("pf", 0)) for s in aprobadas) / len(aprobadas), 2) if aprobadas else 0.0
        dd_avg = round(sum(float(s.get("dd", 0)) for s in aprobadas) / len(aprobadas), 2) if aprobadas else 0.0
        trades_avg = round(sum(int(s.get("trades", 0)) for s in aprobadas) / len(aprobadas)) if aprobadas else 0

        decision = "PASA_RETESTER" if pasan > 0 else "DESCARTADO"
        siguiente = (
            f"Abrir SQ → Retester → cargar las {pasan} estrategias aprobadas"
            if pasan > 0
            else "Revisar criterios del EvalGate o relanzar build con diferente configuracion"
        )
        fecha = datetime.now().strftime("%Y-%m-%d")

        contenido = f"""---
fecha: {fecha}
ticket: Build-{build_n}
estrategia: {activo} H1
fase: EvalGate
decision: {decision}
---

# Decision: {decision}

## Contexto
Estrategia: {activo} H1
Ticket: Build-{build_n}
Fase del pipeline: EvalGate
Fecha: {fecha}

## Metricas en este momento
- Estrategias generadas: {total}
- Estrategias aprobadas: {pasan}
- Tasa de aprobacion: {round(pasan / total * 100, 1) if total > 0 else 0}%
- PF promedio (aprobadas): {pf_avg}
- DD promedio (aprobadas): {dd_avg}%
- Trades promedio (aprobadas): {trades_avg}

## Razon de la decision
{"EvalGate: " + str(pasan) + " de " + str(total) + " estrategias cumplen criterios numericos." if pasan > 0 else "Ninguna estrategia supero los criterios del EvalGate."}

## Decidido por
[ ] Humano
[x] Orchestrator automatico

## Siguiente accion
{siguiente}

## Archivos afectados
- results/evaluation-gate-results.json
- results/build-{build_n}-analysis.md
"""
        nombre = f"Build-{build_n}-{activo}-{fecha}.md"
        out = OBSIDIAN_DECISIONS / nombre
        out.write_text(contenido, encoding="utf-8")
        _ok(f"Nota Obsidian generada: {out.name}")
    except Exception as e:
        _warn(f"Error generando nota Obsidian: {e}")


def run_notion_report(build_n: int, activo: str, gate: dict) -> None:
    try:
        import requests
    except ImportError:
        _warn("requests no instalado — saltando Notion report")
        return

    token = os.environ.get("NOTION_API_KEY", "")
    if not token:
        _warn("NOTION_TOKEN no definido — saltando Notion report")
        return

    config_path = ROOT / "config" / "notion-config.json"
    if not config_path.exists():
        _warn("notion-config.json no encontrado — saltando Notion report")
        return

    try:
        notion_cfg = json.loads(config_path.read_text(encoding="utf-8"))
        builds_page_id = notion_cfg["pages"]["builds"]
    except Exception as e:
        _warn(f"Error leyendo notion-config.json: {e}")
        return

    pasan     = gate.get("pasan", 0)
    total     = gate.get("total", 0)
    aprobadas = [s for s in gate.get("strategies", []) if str(s.get("resultado", "")).upper() == "PASA"]
    pf_avg    = round(sum(float(s.get("pf", 0)) for s in aprobadas) / len(aprobadas), 2) if aprobadas else 0.0
    dd_avg    = round(sum(float(s.get("dd", 0)) for s in aprobadas) / len(aprobadas), 2) if aprobadas else 0.0
    decision  = "PASA_RETESTER" if pasan > 0 else "DESCARTADO"
    causa     = "" if pasan > 0 else gate.get("causa", "Ninguna estrategia superó el EvalGate")
    fecha     = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    titulo    = f"Build {build_n} — {activo} — {fecha}"

    def _p(content):
        return {"object": "block", "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]}}

    def _h2(content):
        return {"object": "block", "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": content}}]}}

    children = [
        _h2("Resumen del Build"),
        _p(f"Build: {build_n}"),
        _p(f"Activo: {activo}"),
        _h2("EvalGate"),
        _p(f"Total estrategias generadas: {total}"),
        _p(f"Estrategias que pasan EvalGate: {pasan}"),
        _p(f"PF promedio (aprobadas): {pf_avg}"),
        _p(f"DD promedio (aprobadas): {dd_avg}%"),
        _h2("Decisión"),
        _p(f"Decisión: {decision}"),
    ]
    if causa:
        children.append(_p(f"Causa: {causa}"))
    children += [_h2("Timestamp"), _p(timestamp)]

    payload = {
        "parent": {"page_id": builds_page_id},
        "properties": {"title": {"title": [{"type": "text", "text": {"content": titulo}}]}},
        "children": children,
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    try:
        resp = requests.post("https://api.notion.com/v1/pages",
                             headers=headers, json=payload, timeout=15)
        if resp.status_code == 200:
            url = resp.json().get("url", "")
            _ok(f"Página Notion creada: {titulo}")
            if url:
                _ok(f"URL: {url}")
        else:
            _warn(f"Notion API {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        _warn(f"Error creando página Notion: {e}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Finisher — TradingLab")
    parser.add_argument("--build",          type=int, required=True, help="Numero del build (ej: 11)")
    parser.add_argument("--activo",         required=True,           help="Activo (ej: XAUUSD)")
    parser.add_argument("--results-folder", default="results",       help="Carpeta con los CSVs (default: results/)")
    args = parser.parse_args()

    activo         = args.activo.upper()
    results_folder = ROOT / args.results_folder

    _header(f"BUILD FINISHER — Build {args.build} | {activo}")

    # Paso 1: verificar CSVs
    _step(1, "Verificando archivos CSV exportados desde SQ...")
    csvs = check_csv_files(results_folder)
    if not csvs:
        print(f"\n  No se encontraron archivos Strategy*.csv en {results_folder}")
        print("  ¿Exportaste los CSVs desde SQ?")
        print("  SQ → Databank → Seleccionar todo → Export → CSV")
        return 1
    _ok(f"{len(csvs)} archivos CSV encontrados")

    # Paso 2: EvalGate
    _step(3, "Ejecutando EvalGate (evaluator-assistant.py)...")
    gate = run_evaluator(results_folder)
    pasan = gate.get("pasan", 0)
    total = gate.get("total", len(csvs))

    # Paso 3: resumen EvalGate
    _step(4, "Resumen EvalGate")
    print(f"    Total estrategias:  {total}")
    print(f"    Pasan EvalGate:     {pasan}")
    print(f"    Descartadas:        {total - pasan}")
    if total > 0:
        tasa = round(pasan / total * 100, 1)
        print(f"    Tasa de aprobacion: {tasa}%")
    if pasan == 0:
        _warn("Ninguna estrategia paso el EvalGate. Revisar criterios o relanzar build.")

    # Paso 4: build-analyzer
    _step(5, "Ejecutando build-analyzer.py...")
    run_build_analyzer(args.build, activo, results_folder)

    # Paso 5: actualizar cola
    _step(6, "Actualizando build-queue-manager...")
    update_queue(activo)

    # Paso 6: strategy-versioning
    _step(7, "Registrando estrategias aprobadas (strategy-versioning.py)...")
    run_strategy_versioning(results_folder)

    # Paso 7: re-index ChromaDB
    _step(8, "Re-indexando ChromaDB (knowledge-base.py)...")
    run_knowledge_reindex()

    # Paso 7b: Knowledge Graph
    _step(8, "Insertando en Knowledge Graph (knowledge-graph.py)...")
    run_kg_integration(args.build, activo, gate)

    # Paso 8b: Thompson Sampling
    _step(9, "Thompson Sampling — actualizando resultado del build...")
    run_thompson_sampling(activo, pasan)

    # Paso 8c: Lessons Analyzer
    _step(10, "Lessons Analyzer — analizando lecciones del build...")
    run_lessons_analyzer()

    # Paso 8d: Concept Drift
    _step(11, "Concept Drift — registrando metricas del build...")
    run_concept_drift()

    # Paso 8e: Champion Challenger
    _step(12, "Champion Challenger — actualizando estado...")
    run_champion_challenger(args.build, activo, pasan)

    # Paso 9: informe Telegram
    _step(13, "Enviando informe Telegram...")
    nivel = "INFO" if pasan > 0 else "WARNING"
    msg = (
        f"Build {args.build} completado — {activo}. "
        f"EvalGate: {pasan}/{total} estrategias pasan. "
        f"{'→ Proceder al Retester.' if pasan > 0 else '→ Revisar criterios.'}"
    )
    _notify(nivel, msg)
    _ok("Telegram notificado")

    # Paso 13b: página Notion
    _step(14, "Creando página Notion en Builds...")
    run_notion_report(args.build, activo, gate)

    # Paso 13c: nota Obsidian
    _step(15, "Generando nota Obsidian en 06_Decisions...")
    run_obsidian_report(args.build, activo, gate)

    # Paso 9: proxima accion
    _header("Pipeline post-build completado")
    print(f"  Build     : {args.build}")
    print(f"  Activo    : {activo}")
    print(f"  EvalGate  : {pasan}/{total} estrategias")
    print()
    if pasan > 0:
        print(f"  PROXIMA ACCION:")
        print(f"  Abrir SQ → Retester → cargar las {pasan} estrategias aprobadas")
        print(f"  Ver resultados en: results/evaluation-gate-results.json")
        print(f"  Ver analisis en:   results/build-{args.build}-analysis.md")
    else:
        print(f"  PROXIMA ACCION:")
        print(f"  Revisar criterios del EvalGate en config/pipeline-config.json")
        print(f"  O relanzar Build con diferente configuracion")

    return 0


if __name__ == "__main__":
    sys.exit(main())
