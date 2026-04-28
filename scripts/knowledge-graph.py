"""
knowledge-graph.py — Knowledge Graph de TradingLab usando Kùzu.
Base de datos de grafos embebida: sin servidor, sin ops.

Uso:
    python scripts/knowledge-graph.py --mode init
    python scripts/knowledge-graph.py --mode add-build --data '{"build_id":"B10",...}'
    python scripts/knowledge-graph.py --mode query --query "similar_builds" --activo XAUUSD
    python scripts/knowledge-graph.py --mode stats
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT    = Path(__file__).parent.parent
DB_PATH = ROOT / ".kuzu" / "tradinglab.db"

try:
    import kuzu
    KUZU_AVAILABLE = True
except ImportError:
    KUZU_AVAILABLE = False


# ─── Init ─────────────────────────────────────────────────────────────────────

def _get_db(db_path: Path = DB_PATH) -> "kuzu.Database":
    if not KUZU_AVAILABLE:
        raise RuntimeError("kuzu no instalado. Ejecuta: pip install kuzu")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return kuzu.Database(str(db_path))


def init_graph(db_path: Path = DB_PATH) -> None:
    """Crea la base de datos Kùzu con todos los nodos y aristas del esquema."""
    db   = _get_db(db_path)
    conn = kuzu.Connection(db)

    # Nodos
    conn.execute("""
        CREATE NODE TABLE IF NOT EXISTS Build(
            build_id     STRING PRIMARY KEY,
            activo       STRING,
            timeframe    STRING,
            fecha        STRING,
            spread       DOUBLE,
            estado       STRING
        )
    """)
    conn.execute("""
        CREATE NODE TABLE IF NOT EXISTS Strategy(
            strategy_id  STRING PRIMARY KEY,
            build_id     STRING,
            pf           DOUBLE,
            dd           DOUBLE,
            trades       INT64,
            win_rate     DOUBLE,
            sharpe       DOUBLE,
            estado       STRING
        )
    """)
    conn.execute("""
        CREATE NODE TABLE IF NOT EXISTS MarketRegime(
            nombre       STRING PRIMARY KEY,
            adx_min      DOUBLE,
            adx_max      DOUBLE,
            atr_ratio    DOUBLE,
            descripcion  STRING
        )
    """)
    conn.execute("""
        CREATE NODE TABLE IF NOT EXISTS GateDecision(
            decision_id  STRING PRIMARY KEY,
            strategy_id  STRING,
            gate_num     INT64,
            gate_name    STRING,
            resultado    STRING,
            criterio     STRING,
            fecha        STRING
        )
    """)
    conn.execute("""
        CREATE NODE TABLE IF NOT EXISTS Lesson(
            lesson_id    STRING PRIMARY KEY,
            titulo       STRING,
            estado       STRING,
            ocurrencias  INT64,
            fecha        STRING
        )
    """)
    conn.execute("""
        CREATE NODE TABLE IF NOT EXISTS LiveOutcome(
            outcome_id       STRING PRIMARY KEY,
            strategy_id      STRING,
            pf_produccion    DOUBLE,
            dd_produccion    DOUBLE,
            duracion_dias    INT64,
            veredicto        STRING
        )
    """)
    conn.execute("""
        CREATE NODE TABLE IF NOT EXISTS Criterion(
            criterion_id         STRING PRIMARY KEY,
            nombre               STRING,
            umbral_actual        DOUBLE,
            umbral_inicial       DOUBLE,
            ultima_actualizacion STRING
        )
    """)

    # Aristas
    conn.execute("CREATE REL TABLE IF NOT EXISTS PRODUCED(FROM Build TO Strategy)")
    conn.execute("CREATE REL TABLE IF NOT EXISTS VALIDATED_BY(FROM Strategy TO GateDecision)")
    conn.execute("CREATE REL TABLE IF NOT EXISTS TRADED_IN(FROM Strategy TO MarketRegime)")
    conn.execute("CREATE REL TABLE IF NOT EXISTS TRIGGERED(FROM GateDecision TO Lesson)")
    conn.execute("CREATE REL TABLE IF NOT EXISTS CAUSED_ADJUSTMENT(FROM Lesson TO Criterion)")
    conn.execute("CREATE REL TABLE IF NOT EXISTS HAD_OUTCOME(FROM Strategy TO LiveOutcome)")
    conn.execute("CREATE REL TABLE IF NOT EXISTS UPDATED(FROM LiveOutcome TO Criterion)")

    # Seed de los 4 regímenes de mercado
    _seed_market_regimes(conn)

    print(f"Knowledge Graph inicializado en: {db_path}")


def _seed_market_regimes(conn: "kuzu.Connection") -> None:
    """Inserta los 4 regímenes de mercado estándar si no existen."""
    regimes = [
        {
            "nombre":      "tendencia-altavol",
            "adx_min":     25.0,
            "adx_max":     100.0,
            "atr_ratio":   1.2,
            "descripcion": "Mercado en tendencia con volatilidad alta. ADX>25, ATR>1.2x promedio.",
        },
        {
            "nombre":      "tendencia-bajovol",
            "adx_min":     25.0,
            "adx_max":     100.0,
            "atr_ratio":   0.8,
            "descripcion": "Mercado en tendencia con volatilidad baja. ADX>25, ATR<=1.2x promedio.",
        },
        {
            "nombre":      "rango-altavol",
            "adx_min":     0.0,
            "adx_max":     25.0,
            "atr_ratio":   1.2,
            "descripcion": "Mercado en rango con volatilidad alta. ADX<=25, ATR>1.2x promedio.",
        },
        {
            "nombre":      "rango-bajovol",
            "adx_min":     0.0,
            "adx_max":     25.0,
            "atr_ratio":   0.8,
            "descripcion": "Mercado en rango con volatilidad baja. ADX<=25, ATR<=1.2x promedio.",
        },
    ]
    for r in regimes:
        try:
            conn.execute(
                "CREATE (:MarketRegime {nombre: $nombre, adx_min: $adx_min, "
                "adx_max: $adx_max, atr_ratio: $atr_ratio, descripcion: $descripcion})",
                {"nombre": r["nombre"], "adx_min": r["adx_min"],
                 "adx_max": r["adx_max"], "atr_ratio": r["atr_ratio"],
                 "descripcion": r["descripcion"]}
            )
        except Exception:
            pass  # Ya existe, ignorar


# ─── Escritura ─────────────────────────────────────────────────────────────────

def _node_exists(conn: "kuzu.Connection", table: str, pk_field: str, pk_value: str) -> bool:
    r = conn.execute(
        f"MATCH (n:{table} {{{pk_field}: $val}}) RETURN count(n)",
        {"val": pk_value}
    )
    return r.has_next() and r.get_next()[0] > 0


def add_build(build_data: dict, db_path: Path = DB_PATH) -> None:
    db   = _get_db(db_path)
    conn = kuzu.Connection(db)
    params = {
        "build_id":  str(build_data.get("build_id", "")),
        "activo":    str(build_data.get("activo", "")),
        "timeframe": str(build_data.get("timeframe", "H1")),
        "fecha":     str(build_data.get("fecha", datetime.now().strftime("%Y-%m-%d"))),
        "spread":    float(build_data.get("spread", 0.0)),
        "estado":    str(build_data.get("estado", "COMPLETADO")),
    }
    try:
        conn.execute(
            "CREATE (:Build {build_id: $build_id, activo: $activo, "
            "timeframe: $timeframe, fecha: $fecha, spread: $spread, estado: $estado})",
            params
        )
    except Exception:
        conn.execute(
            "MATCH (b:Build {build_id: $build_id}) "
            "SET b.activo=$activo, b.timeframe=$timeframe, "
            "b.fecha=$fecha, b.spread=$spread, b.estado=$estado",
            params
        )


def add_strategy(strategy_data: dict, db_path: Path = DB_PATH) -> None:
    db   = _get_db(db_path)
    conn = kuzu.Connection(db)

    sid = str(strategy_data.get("strategy_id", ""))
    bid = str(strategy_data.get("build_id", ""))

    params = {
        "sid":      sid,
        "build_id": bid,
        "pf":       float(strategy_data.get("pf", 0.0)),
        "dd":       float(strategy_data.get("dd", 0.0)),
        "trades":   int(strategy_data.get("trades", 0)),
        "win_rate": float(strategy_data.get("win_rate", 0.0)),
        "sharpe":   float(strategy_data.get("sharpe", 0.0)),
        "estado":   str(strategy_data.get("estado", "APROBADA")),
    }
    try:
        conn.execute(
            "CREATE (:Strategy {strategy_id: $sid, build_id: $build_id, "
            "pf: $pf, dd: $dd, trades: $trades, win_rate: $win_rate, "
            "sharpe: $sharpe, estado: $estado})",
            params
        )
    except Exception:
        conn.execute(
            "MATCH (s:Strategy {strategy_id: $sid}) "
            "SET s.build_id=$build_id, s.pf=$pf, s.dd=$dd, "
            "s.trades=$trades, s.win_rate=$win_rate, s.sharpe=$sharpe, s.estado=$estado",
            params
        )

    # Conectar Build → Strategy con CREATE (solo si el Build existe)
    try:
        conn.execute(
            "MATCH (b:Build {build_id: $bid}), (s:Strategy {strategy_id: $sid}) "
            "CREATE (b)-[:PRODUCED]->(s)",
            {"bid": bid, "sid": sid}
        )
    except Exception:
        pass  # Edge ya existe o Build no encontrado


def add_gate_decision(strategy_id: str, gate_num: int, gate_name: str,
                      resultado: str, criterio: str,
                      db_path: Path = DB_PATH) -> None:
    db   = _get_db(db_path)
    conn = kuzu.Connection(db)

    fecha       = datetime.now().strftime("%Y-%m-%d")
    decision_id = f"{strategy_id}-G{gate_num}-{fecha}"

    params = {
        "did":   decision_id,
        "sid":   strategy_id,
        "gnum":  gate_num,
        "gname": gate_name,
        "res":   resultado,
        "crit":  criterio,
        "fecha": fecha,
    }
    try:
        conn.execute(
            "CREATE (:GateDecision {decision_id: $did, strategy_id: $sid, "
            "gate_num: $gnum, gate_name: $gname, resultado: $res, "
            "criterio: $crit, fecha: $fecha})",
            params
        )
    except Exception:
        conn.execute(
            "MATCH (g:GateDecision {decision_id: $did}) "
            "SET g.resultado=$res, g.criterio=$crit",
            params
        )

    # Conectar Strategy → GateDecision
    try:
        conn.execute(
            "MATCH (s:Strategy {strategy_id: $sid}), "
            "(g:GateDecision {decision_id: $did}) "
            "CREATE (s)-[:VALIDATED_BY]->(g)",
            {"sid": strategy_id, "did": decision_id}
        )
    except Exception:
        pass


def add_lesson(lesson_data: dict, db_path: Path = DB_PATH) -> None:
    db   = _get_db(db_path)
    conn = kuzu.Connection(db)

    lid    = str(lesson_data.get("lesson_id", ""))
    params = {
        "lid":         lid,
        "titulo":      str(lesson_data.get("titulo", "")),
        "estado":      str(lesson_data.get("estado", "TENTATIVA")),
        "ocurrencias": int(lesson_data.get("ocurrencias", 1)),
        "fecha":       str(lesson_data.get("fecha", datetime.now().strftime("%Y-%m-%d"))),
    }
    try:
        conn.execute(
            "CREATE (:Lesson {lesson_id: $lid, titulo: $titulo, "
            "estado: $estado, ocurrencias: $ocurrencias, fecha: $fecha})",
            params
        )
    except Exception:
        conn.execute(
            "MATCH (l:Lesson {lesson_id: $lid}) "
            "SET l.titulo=$titulo, l.estado=$estado, "
            "l.ocurrencias=$ocurrencias, l.fecha=$fecha",
            params
        )


def add_live_outcome(strategy_id: str, outcome_data: dict,
                     db_path: Path = DB_PATH) -> None:
    db   = _get_db(db_path)
    conn = kuzu.Connection(db)

    fecha      = datetime.now().strftime("%Y-%m-%d")
    outcome_id = f"{strategy_id}-OUT-{fecha}"

    params = {
        "oid":  outcome_id,
        "sid":  strategy_id,
        "pf":   float(outcome_data.get("pf_produccion", 0.0)),
        "dd":   float(outcome_data.get("dd_produccion", 0.0)),
        "dias": int(outcome_data.get("duracion_dias", 0)),
        "ver":  str(outcome_data.get("veredicto", "")),
    }
    try:
        conn.execute(
            "CREATE (:LiveOutcome {outcome_id: $oid, strategy_id: $sid, "
            "pf_produccion: $pf, dd_produccion: $dd, "
            "duracion_dias: $dias, veredicto: $ver})",
            params
        )
    except Exception:
        conn.execute(
            "MATCH (o:LiveOutcome {outcome_id: $oid}) "
            "SET o.pf_produccion=$pf, o.dd_produccion=$dd, "
            "o.duracion_dias=$dias, o.veredicto=$ver",
            params
        )

    try:
        conn.execute(
            "MATCH (s:Strategy {strategy_id: $sid}), "
            "(o:LiveOutcome {outcome_id: $oid}) "
            "CREATE (s)-[:HAD_OUTCOME]->(o)",
            {"sid": strategy_id, "oid": outcome_id}
        )
    except Exception:
        pass


# ─── Consultas ─────────────────────────────────────────────────────────────────

def query_similar_builds(activo: str, timeframe: str = "H1",
                         regime: str = "",
                         db_path: Path = DB_PATH) -> list[dict]:
    """Busca builds anteriores similares y sus resultados (top 5)."""
    db   = _get_db(db_path)
    conn = kuzu.Connection(db)

    result = conn.execute(
        "MATCH (b:Build)-[:PRODUCED]->(s:Strategy) "
        "WHERE b.activo = $activo AND b.timeframe = $tf "
        "RETURN b.build_id, b.fecha, b.spread, b.estado, "
        "s.strategy_id, s.pf, s.dd, s.trades, s.win_rate, s.estado "
        "ORDER BY s.pf DESC LIMIT 5",
        {"activo": activo, "tf": timeframe}
    )

    rows = []
    while result.has_next():
        row = result.get_next()
        rows.append({
            "build_id":    row[0],
            "fecha":       row[1],
            "spread":      row[2],
            "build_estado": row[3],
            "strategy_id": row[4],
            "pf":          row[5],
            "dd":          row[6],
            "trades":      row[7],
            "win_rate":    row[8],
            "estado":      row[9],
        })
    return rows


def query_lessons_for_gate(gate_num: int, db_path: Path = DB_PATH) -> list[dict]:
    """Busca lecciones relacionadas con una puerta específica del pipeline."""
    db   = _get_db(db_path)
    conn = kuzu.Connection(db)

    result = conn.execute(
        "MATCH (g:GateDecision)-[:TRIGGERED]->(l:Lesson) "
        "WHERE g.gate_num = $gnum "
        "RETURN l.lesson_id, l.titulo, l.estado, l.ocurrencias "
        "ORDER BY l.ocurrencias DESC",
        {"gnum": gate_num}
    )

    rows = []
    while result.has_next():
        row = result.get_next()
        rows.append({
            "lesson_id":   row[0],
            "titulo":      row[1],
            "estado":      row[2],
            "ocurrencias": row[3],
        })
    return rows


def query_strategy_lineage(strategy_id: str, db_path: Path = DB_PATH) -> dict:
    """Traza el linaje completo: Build → Gates → Regime → Outcome → Lessons."""
    db   = _get_db(db_path)
    conn = kuzu.Connection(db)

    lineage: dict = {"strategy_id": strategy_id}

    # Build de origen
    r = conn.execute(
        "MATCH (b:Build)-[:PRODUCED]->(s:Strategy {strategy_id: $sid}) "
        "RETURN b.build_id, b.activo, b.timeframe, b.fecha",
        {"sid": strategy_id}
    )
    if r.has_next():
        row = r.get_next()
        lineage["build"] = {"build_id": row[0], "activo": row[1],
                            "timeframe": row[2], "fecha": row[3]}

    # Gates superadas
    r = conn.execute(
        "MATCH (s:Strategy {strategy_id: $sid})-[:VALIDATED_BY]->(g:GateDecision) "
        "RETURN g.gate_num, g.gate_name, g.resultado, g.criterio "
        "ORDER BY g.gate_num",
        {"sid": strategy_id}
    )
    gates = []
    while r.has_next():
        row = r.get_next()
        gates.append({"gate_num": row[0], "gate_name": row[1],
                      "resultado": row[2], "criterio": row[3]})
    lineage["gates"] = gates

    # Regimen de mercado
    r = conn.execute(
        "MATCH (s:Strategy {strategy_id: $sid})-[:TRADED_IN]->(m:MarketRegime) "
        "RETURN m.nombre, m.descripcion",
        {"sid": strategy_id}
    )
    if r.has_next():
        row = r.get_next()
        lineage["regime"] = {"nombre": row[0], "descripcion": row[1]}

    # Outcome en produccion
    r = conn.execute(
        "MATCH (s:Strategy {strategy_id: $sid})-[:HAD_OUTCOME]->(o:LiveOutcome) "
        "RETURN o.pf_produccion, o.dd_produccion, o.duracion_dias, o.veredicto",
        {"sid": strategy_id}
    )
    if r.has_next():
        row = r.get_next()
        lineage["outcome"] = {"pf_produccion": row[0], "dd_produccion": row[1],
                              "duracion_dias": row[2], "veredicto": row[3]}

    return lineage


def get_stats(db_path: Path = DB_PATH) -> dict:
    """Estadisticas del grafo."""
    db   = _get_db(db_path)
    conn = kuzu.Connection(db)

    stats = {}
    for table in ["Build", "Strategy", "MarketRegime", "GateDecision",
                  "Lesson", "LiveOutcome", "Criterion"]:
        r = conn.execute(f"MATCH (n:{table}) RETURN count(n)")
        if r.has_next():
            stats[table] = r.get_next()[0]

    for rel in ["PRODUCED", "VALIDATED_BY", "TRADED_IN", "TRIGGERED",
                "CAUSED_ADJUSTMENT", "HAD_OUTCOME", "UPDATED"]:
        r = conn.execute(f"MATCH ()-[e:{rel}]->() RETURN count(e)")
        if r.has_next():
            stats[f"rel_{rel}"] = r.get_next()[0]

    return stats


# ─── CLI ───────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Knowledge Graph — TradingLab")
    parser.add_argument("--mode", required=True,
                        choices=["init", "add-build", "add-strategy",
                                 "add-lesson", "add-outcome", "query", "stats"],
                        help="Modo de operacion")
    parser.add_argument("--data",   help="JSON con datos del nodo a insertar")
    parser.add_argument("--query",  help="Tipo de query: similar_builds, lessons_for_gate, lineage")
    parser.add_argument("--activo", help="Activo (para similar_builds)")
    parser.add_argument("--gate",   type=int, help="Numero de gate (para lessons_for_gate)")
    parser.add_argument("--strategy-id", help="ID estrategia (para lineage)")
    parser.add_argument("--db-path", default=str(DB_PATH), help="Ruta de la BD Kùzu")
    args = parser.parse_args()

    db_path = Path(args.db_path)

    if args.mode == "init":
        init_graph(db_path)

    elif args.mode == "add-build":
        data = json.loads(args.data or "{}")
        add_build(data, db_path)
        print(f"Build {data.get('build_id')} añadido al KG.")

    elif args.mode == "add-strategy":
        data = json.loads(args.data or "{}")
        add_strategy(data, db_path)
        print(f"Strategy {data.get('strategy_id')} añadida al KG.")

    elif args.mode == "add-lesson":
        data = json.loads(args.data or "{}")
        add_lesson(data, db_path)
        print(f"Lesson {data.get('lesson_id')} añadida al KG.")

    elif args.mode == "add-outcome":
        data   = json.loads(args.data or "{}")
        sid    = data.pop("strategy_id", args.strategy_id or "")
        add_live_outcome(sid, data, db_path)
        print(f"Outcome de {sid} añadido al KG.")

    elif args.mode == "query":
        q = args.query or ""
        parts = q.split()
        qtype = parts[0] if parts else ""

        if qtype == "builds":
            db   = _get_db(db_path)
            conn = kuzu.Connection(db)
            r = conn.execute(
                "MATCH (b:Build) "
                "RETURN b.build_id, b.activo, b.timeframe, b.estado "
                "ORDER BY b.build_id"
            )
            print(f"\n{'BUILD':12s}  {'ACTIVO':10s}  {'TF':4s}  ESTADO")
            print("-" * 48)
            while r.has_next():
                row = r.get_next()
                print(f"  {row[0]:10s}  {row[1]:10s}  {row[2]:4s}  {row[3]}")

        elif qtype == "lessons":
            db   = _get_db(db_path)
            conn = kuzu.Connection(db)
            r = conn.execute(
                "MATCH (l:Lesson) "
                "RETURN l.lesson_id, l.titulo, l.estado, l.ocurrencias "
                "ORDER BY l.ocurrencias DESC"
            )
            print(f"\n{'ID':14s}  {'ESTADO':12s}  {'OCC':4s}  TITULO")
            print("-" * 72)
            while r.has_next():
                row = r.get_next()
                titulo = str(row[1])[:40]
                print(f"  {row[0]:12s}  {row[2]:12s}  {row[3]:4}  {titulo}")

        elif qtype == "strategies":
            db   = _get_db(db_path)
            conn = kuzu.Connection(db)
            r = conn.execute(
                "MATCH (b:Build)-[:PRODUCED]->(s:Strategy) "
                "RETURN s.strategy_id, b.activo, s.pf, s.estado "
                "ORDER BY s.pf DESC"
            )
            print(f"\n{'STRATEGY_ID':28s}  {'ACTIVO':8s}  {'PF':6s}  ESTADO")
            print("-" * 64)
            while r.has_next():
                row = r.get_next()
                print(f"  {str(row[0]):26s}  {str(row[1]):8s}  {row[2]:6.3f}  {row[3]}")

        elif qtype == "lineage":
            sid = parts[1] if len(parts) > 1 else (args.strategy_id or "")
            data = query_strategy_lineage(sid, db_path=db_path)
            print(json.dumps(data, indent=2, ensure_ascii=False))

        elif qtype == "similar":
            activo = parts[1] if len(parts) > 1 else (args.activo or "")
            tf     = parts[2] if len(parts) > 2 else "H1"
            rows   = query_similar_builds(activo, timeframe=tf, db_path=db_path)
            print(json.dumps(rows, indent=2, ensure_ascii=False))

        elif qtype == "similar_builds":
            rows = query_similar_builds(args.activo or "", db_path=db_path)
            print(json.dumps(rows, indent=2, ensure_ascii=False))

        elif qtype == "lessons_for_gate":
            rows = query_lessons_for_gate(args.gate or 0, db_path=db_path)
            print(json.dumps(rows, indent=2, ensure_ascii=False))

        else:
            print("Queries disponibles:")
            print("  --query builds")
            print("  --query lessons")
            print("  --query strategies")
            print("  --query 'lineage STRATEGY_ID'")
            print("  --query 'similar ACTIVO [TIMEFRAME]'")
            return 1

    elif args.mode == "stats":
        stats = get_stats(db_path)
        print("\nKnowledge Graph — Estadisticas")
        print("=" * 40)
        for k, v in stats.items():
            print(f"  {k:30s}: {v}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
