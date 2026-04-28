"""
kg-importer.py — Importa el historial existente del proyecto al Knowledge Graph.

Importa:
  1. Builds del historial (docs/project-status.md)
  2. Estrategias del registry (results/strategies-registry.json)
  3. Lecciones de lessons-learned.md
  4. Decisiones del audit-trail.log
  5. Config del Build activo (config/build-10-config.json si existe)

Uso:
    python scripts/kg-importer.py
    python scripts/kg-importer.py --repo-path /ruta/al/repo
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent

import importlib.util as _ilu
_kg_spec = _ilu.spec_from_file_location(
    "knowledge_graph",
    Path(__file__).parent / "knowledge-graph.py"
)
kg = _ilu.module_from_spec(_kg_spec)
_kg_spec.loader.exec_module(kg)


# ─── Parsers ───────────────────────────────────────────────────────────────────

_BUILD_RE = re.compile(
    r"Build\s+(\d+)[^\n]*\n.*?Activo[:\s]+([A-Z/]+).*?\n",
    re.IGNORECASE | re.DOTALL
)
_LESSON_HEADER_RE = re.compile(r"^###\s+(LECCION-\d+):\s*(.+)$", re.MULTILINE)
_LESSON_FIELD_RE  = re.compile(r"^(Estado|Ocurrencias confirmadas):\s*(.+)$", re.MULTILINE)

_AUDIT_DECISION_RE = re.compile(
    r"DECISION:\s*(\S+).*?ESTRATEGIA:\s*(\S+).*?FASE:\s*(\S+)",
    re.DOTALL
)


def parse_builds_from_project_status(text: str) -> list[dict]:
    """Extrae builds del project-status.md con regex tolerante."""
    builds = []
    # Busca patrones como "Build N" seguidos de info
    for m in re.finditer(r"Build\s+(\d+)", text, re.IGNORECASE):
        bid = f"B{m.group(1).zfill(2)}"
        # Evitar duplicados
        if any(b["build_id"] == bid for b in builds):
            continue

        # Intentar extraer activo del contexto cercano
        snippet = text[m.start():m.start() + 300]
        activo_m = re.search(r"(XAUUSD|EURUSD|GBPUSD|USDJPY|AUDUSD|NZDUSD|USDCHF|USDCAD|XAGUSD)", snippet)
        activo = activo_m.group(1) if activo_m else "DESCONOCIDO"

        estado_m = re.search(r"(COMPLETADO|ACTIVO|FALLIDO|PENDIENTE|EN_CURSO)", snippet, re.IGNORECASE)
        estado = estado_m.group(1).upper() if estado_m else "COMPLETADO"

        builds.append({
            "build_id":  bid,
            "activo":    activo,
            "timeframe": "H1",
            "fecha":     datetime.now().strftime("%Y-%m-%d"),
            "spread":    0.0,
            "estado":    estado,
        })

    return builds


def parse_strategies_from_registry(registry: dict) -> list[dict]:
    """Transforma el registry al formato del KG.

    Formato real de strategies-registry.json:
    {
      "XAUUSD-B10-1114": {
        "versiones": {"v1": {"metricas": {}, "estado": "standby", ...}},
        "version_activa": "v1"
      }, ...
    }
    """
    strategies = []
    for strategy_id, strategy_data in registry.items():
        version_activa = strategy_data.get("version_activa", "v1")
        versiones = strategy_data.get("versiones", {})
        version_data = versiones.get(version_activa, {})
        estado   = version_data.get("estado", "standby")
        metricas = version_data.get("metricas", {})

        # Inferir build_id desde el nombre (ej: XAUUSD-B10-1114 → B10)
        bid_match = re.search(r"-B(\d+)-", strategy_id)
        bid = f"B{bid_match.group(1).zfill(2)}" if bid_match else "B00"

        strategies.append({
            "strategy_id": strategy_id,
            "build_id":    bid,
            "pf":          float(metricas.get("pf", 0.0)),
            "dd":          float(metricas.get("dd", 0.0)),
            "trades":      int(metricas.get("trades", 0)),
            "win_rate":    float(metricas.get("win_rate", 0.0)),
            "sharpe":      float(metricas.get("sharpe", 0.0)),
            "estado":      str(estado).upper(),
        })
    return strategies


def parse_lessons(text: str) -> list[dict]:
    """Extrae lecciones de lessons-learned.md."""
    lessons = []
    headers = list(_LESSON_HEADER_RE.finditer(text))
    for i, match in enumerate(headers):
        lid    = match.group(1)
        titulo = match.group(2).strip()
        start  = match.start()
        end    = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        body   = text[start:end]

        estado      = "TENTATIVA"
        ocurrencias = 1
        for m in _LESSON_FIELD_RE.finditer(body):
            if m.group(1) == "Estado":
                estado = m.group(2).strip().split()[0].upper()
            elif m.group(1) == "Ocurrencias confirmadas":
                try:
                    ocurrencias = int(m.group(2).strip().split()[0])
                except ValueError:
                    pass

        lessons.append({
            "lesson_id":   lid,
            "titulo":      titulo,
            "estado":      estado,
            "ocurrencias": ocurrencias,
            "fecha":       datetime.now().strftime("%Y-%m-%d"),
        })
    return lessons


def parse_audit_decisions(text: str) -> list[dict]:
    """Extrae decisiones relevantes del audit trail."""
    decisions = []
    # Formato simple: cada linea puede tener DECISION | ESTRATEGIA | GATE
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Buscar patron: PASA|DESCARTAR con estrategia y gate
        d_m = re.search(r"(PASA|DESCARTAR|ESPERA)", line, re.IGNORECASE)
        s_m = re.search(r"([A-Z]{2,8}_B\d+_S\d+)", line)
        g_m = re.search(r"(EvalGate|Retester|WFO|Paso12b|Portfolio)", line, re.IGNORECASE)

        if d_m and s_m:
            decisions.append({
                "resultado":   d_m.group(1).upper(),
                "strategy_id": s_m.group(1),
                "gate_name":   g_m.group(1) if g_m else "DESCONOCIDA",
            })
    return decisions


# ─── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="KG Importer — TradingLab")
    parser.add_argument("--repo-path", default=".", help="Ruta al repo (default: .)")
    args = parser.parse_args()

    repo = Path(args.repo_path).resolve()
    db_path = repo / ".kuzu" / "tradinglab.db"

    print("\nKG Importer — TradingLab")
    print("=" * 50)

    # Inicializar grafo
    print("\n[1] Inicializando Knowledge Graph...")
    kg.init_graph(db_path)

    nodes_created = 0
    rels_created  = 0

    # ── 1. Builds desde project-status.md ────────────────────────────────────
    print("\n[2] Importando builds desde project-status.md...")
    ps_file = repo / "docs" / "project-status.md"
    builds = []
    if ps_file.exists():
        builds = parse_builds_from_project_status(
            ps_file.read_text(encoding="utf-8", errors="replace")
        )
        for b in builds:
            try:
                kg.add_build(b, db_path)
                nodes_created += 1
            except Exception as e:
                print(f"  WARN: build {b['build_id']}: {e}")
        print(f"  {len(builds)} builds importados.")
    else:
        print(f"  WARN: {ps_file} no encontrado — saltando.")

    # ── 2. Estrategias desde strategies-registry.json ────────────────────────
    print("\n[3] Importando estrategias desde strategies-registry.json...")
    registry_file = repo / "results" / "strategies-registry.json"
    strategies = []
    if registry_file.exists():
        try:
            raw = json.loads(registry_file.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                print(f"  WARN: formato inesperado en registry — se esperaba dict, got {type(raw).__name__}")
                raw = {}
            # Desenvolver envelope {"strategies": {...}} si existe
            if "strategies" in raw and isinstance(raw["strategies"], dict):
                raw = raw["strategies"]
            strategies = parse_strategies_from_registry(raw)
            for s in strategies:
                try:
                    kg.add_strategy(s, db_path)
                    nodes_created += 1
                    rels_created  += 1  # PRODUCED
                except Exception as e:
                    print(f"  WARN: strategy {s['strategy_id']}: {e}")
            print(f"  {len(strategies)} estrategias importadas.")
        except Exception as e:
            print(f"  WARN: error leyendo registry: {e}")
    else:
        print(f"  WARN: {registry_file} no encontrado — saltando.")

    # ── 3. Lecciones desde lessons-learned.md ────────────────────────────────
    print("\n[4] Importando lecciones desde lessons-learned.md...")
    lessons_file = repo / "docs" / "lessons-learned.md"
    lessons = []
    if lessons_file.exists():
        lessons = parse_lessons(
            lessons_file.read_text(encoding="utf-8", errors="replace")
        )
        for l in lessons:
            try:
                kg.add_lesson(l, db_path)
                nodes_created += 1
            except Exception as e:
                print(f"  WARN: lesson {l['lesson_id']}: {e}")
        print(f"  {len(lessons)} lecciones importadas.")
    else:
        print(f"  WARN: {lessons_file} no encontrado — saltando.")

    # ── 4. Decisiones desde audit-trail.log ──────────────────────────────────
    print("\n[5] Importando decisiones desde audit-trail.log...")
    audit_file = repo / "results" / "audit-trail.log"
    gate_decisions = []
    if audit_file.exists():
        audit_text = audit_file.read_text(encoding="utf-8", errors="replace")
        gate_decisions = parse_audit_decisions(audit_text)
        gate_map = {"EvalGate": 1, "Retester": 2, "Paso12b": 3, "WFO": 4, "Portfolio": 5}
        for d in gate_decisions:
            gnum = gate_map.get(d["gate_name"], 0)
            try:
                kg.add_gate_decision(
                    strategy_id=d["strategy_id"],
                    gate_num=gnum,
                    gate_name=d["gate_name"],
                    resultado=d["resultado"],
                    criterio="",
                    db_path=db_path,
                )
                nodes_created += 1
                rels_created  += 1  # VALIDATED_BY
            except Exception as e:
                print(f"  WARN: gate decision {d['strategy_id']}: {e}")
        print(f"  {len(gate_decisions)} decisiones importadas.")
    else:
        print(f"  WARN: {audit_file} no encontrado — saltando.")

    # ── 5. Config del build activo ────────────────────────────────────────────
    print("\n[6] Buscando config del build activo...")
    imported_config = False
    for config_file in sorted(repo.glob("config/build-*-config.json")):
        try:
            cfg = json.loads(config_file.read_text(encoding="utf-8"))
            bid_raw = re.search(r"build-(\d+)", config_file.name)
            if bid_raw:
                build_data = {
                    "build_id":  f"B{bid_raw.group(1).zfill(2)}",
                    "activo":    cfg.get("activo", "DESCONOCIDO"),
                    "timeframe": cfg.get("timeframe", "H1"),
                    "fecha":     cfg.get("fecha", datetime.now().strftime("%Y-%m-%d")),
                    "spread":    float(cfg.get("spread", 0.0)),
                    "estado":    "ACTIVO",
                }
                kg.add_build(build_data, db_path)
                nodes_created += 1
                imported_config = True
                print(f"  Config {config_file.name} importada.")
        except Exception as e:
            print(f"  WARN: {config_file.name}: {e}")
    if not imported_config:
        print("  No se encontraron configs de build — saltando.")

    # ── Informe final ─────────────────────────────────────────────────────────
    stats = kg.get_stats(db_path)
    print("\n" + "=" * 50)
    print("Importacion completada.")
    print(f"  Nodos creados aprox.:  {nodes_created}")
    print(f"  Aristas creadas aprox.:{rels_created}")
    print("\nEstado del grafo:")
    for k, v in stats.items():
        print(f"  {k:30s}: {v}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
