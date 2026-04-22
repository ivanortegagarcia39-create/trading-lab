"""
knowledge-base.py
Indexa el historial del proyecto en ChromaDB para consultas semanticas.

Indexa documentos clave del repo y resultados historicos con metadata
de fecha, tipo, activo y build. Aplica un factor de relevancia temporal
que da mas peso a los documentos recientes.

Uso:
    python knowledge-base.py index
    python knowledge-base.py index --repo-path .
    python knowledge-base.py query "estrategias XAUUSD que pasaron WFO"
    python knowledge-base.py query "lecciones sobre comisiones" --n-results 10

Requisitos:
    pip install chromadb

La base de datos se persiste en .chromadb/ (ignorado por git).
"""

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


# ─── Verificar ChromaDB ───────────────────────────────────────────────────────

try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False


# ─── Configuracion ────────────────────────────────────────────────────────────

CHROMA_PATH = ".chromadb"
COLLECTION_NAME = "tradinglab-knowledge"
CHUNK_SIZE = 800        # caracteres por chunk
CHUNK_OVERLAP = 100     # solapamiento entre chunks

# Documentos a indexar
INDEX_PATHS = [
    "docs/lessons-learned.md",
    "docs/project-status.md",
    "docs/Fase-0-verificacion.md",
]

# Patrones para buscar en subcarpetas
INDEX_PATTERNS = [
    ("results", "*.md"),
    ("results", "*.csv"),
]

# Metadata por tipo de archivo
TYPE_MAP = {
    "lessons-learned.md": "leccion",
    "project-status.md":  "estado",
    "Fase-0-verificacion.md": "verificacion",
}


# ─── Factor de relevancia temporal ───────────────────────────────────────────

def temporal_weight(file_path: Path) -> float:
    """
    Calcula el peso temporal de un documento.
    peso = 1.0 / (1 + dias_desde_creacion / 90)
    Un chunk de hace 90 dias vale 0.5 vs uno de hoy (1.0).
    """
    try:
        mtime = file_path.stat().st_mtime
        file_date = datetime.fromtimestamp(mtime, tz=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        days_old = (now - file_date).days
        return 1.0 / (1.0 + days_old / 90.0)
    except Exception:
        return 0.5


# ─── Extraccion de metadata desde contenido ───────────────────────────────────

_ACTIVO_RE = re.compile(r"\b(XAUUSD|EURUSD|GBPUSD|USDJPY|USDCHF|AUDUSD|NZDUSD|"
                         r"USDCAD|XAGUSD|NAS100|US500|US30|DE40|UK100|JP225|"
                         r"BTCUSD|ETHUSD)\b", re.IGNORECASE)

_BUILD_RE  = re.compile(r"\b[Bb]uild[\s-]?(\d+)\b")

_FASE_RE   = re.compile(r"\bCapa[\s]?(\d)\b", re.IGNORECASE)


def extract_metadata(text: str, file_path: Path) -> dict:
    activos = list(set(_ACTIVO_RE.findall(text)))
    builds  = [int(m) for m in _BUILD_RE.findall(text)]
    fases   = [int(m) for m in _FASE_RE.findall(text)]

    tipo = TYPE_MAP.get(file_path.name, "documento")
    if "results" in str(file_path) and file_path.suffix == ".csv":
        tipo = "metrica"
    elif "results" in str(file_path):
        tipo = "resultado"

    return {
        "tipo":   tipo,
        "activo": ",".join(activos[:3]) if activos else "N/A",
        "build":  str(max(builds)) if builds else "0",
        "fase":   str(max(fases)) if fases else "0",
        "fecha":  datetime.now().isoformat(timespec="seconds"),
        "fuente": str(file_path),
        "peso_temporal": str(round(temporal_weight(file_path), 4)),
    }


# ─── Chunking ─────────────────────────────────────────────────────────────────

def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Divide el texto en chunks con solapamiento."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += size - overlap
    return chunks


# ─── Carga de documentos ──────────────────────────────────────────────────────

def load_documents(repo_path: Path) -> list[tuple[str, dict, Path]]:
    """
    Devuelve lista de (texto_chunk, metadata, file_path).
    """
    docs = []

    # Documentos fijos
    for rel_path in INDEX_PATHS:
        fp = repo_path / rel_path
        if fp.exists():
            text = fp.read_text(encoding="utf-8", errors="replace")
            meta = extract_metadata(text, fp)
            for chunk in chunk_text(text):
                docs.append((chunk, meta.copy(), fp))
        else:
            print(f"  [SKIP] No encontrado: {fp}")

    # Patrones en subcarpetas
    for folder, pattern in INDEX_PATTERNS:
        folder_path = repo_path / folder
        if not folder_path.exists():
            continue
        for fp in folder_path.rglob(pattern):
            try:
                text = fp.read_text(encoding="utf-8", errors="replace")
                if len(text.strip()) < 50:
                    continue  # Ignorar archivos casi vacios
                meta = extract_metadata(text, fp)
                for chunk in chunk_text(text):
                    docs.append((chunk, meta.copy(), fp))
            except Exception as e:
                print(f"  [WARN] No se pudo leer {fp}: {e}")

    return docs


# ─── Indexacion ───────────────────────────────────────────────────────────────

def get_collection(repo_path: Path):
    db_path = str(repo_path / CHROMA_PATH)
    client = chromadb.PersistentClient(
        path=db_path,
        settings=Settings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def index_project(repo_path: Path) -> int:
    """
    Indexa todos los documentos del proyecto en ChromaDB.
    Devuelve el numero de chunks indexados.
    """
    print(f"Indexando proyecto en: {repo_path.resolve()}")
    docs = load_documents(repo_path)
    print(f"  {len(docs)} chunks encontrados en {len(INDEX_PATHS) + len(INDEX_PATTERNS)} fuentes")

    collection = get_collection(repo_path)

    # Cargar en lotes de 50
    batch_size = 50
    indexed = 0
    for i in range(0, len(docs), batch_size):
        batch = docs[i:i + batch_size]
        ids       = [f"chunk-{i + j}" for j in range(len(batch))]
        texts     = [item[0] for item in batch]
        metadatas = [item[1] for item in batch]

        collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
        )
        indexed += len(batch)

    print(f"  Indexacion completada: {indexed} chunks en {repo_path / CHROMA_PATH}")
    return indexed


# ─── Consulta ─────────────────────────────────────────────────────────────────

def query(pregunta: str, repo_path: Path, n_results: int = 5) -> list[dict]:
    """
    Consulta la base de datos con una pregunta en lenguaje natural.
    Devuelve los N chunks mas relevantes con score y metadata.
    """
    collection = get_collection(repo_path)
    results = collection.query(
        query_texts=[pregunta],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    output = []
    docs      = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(docs, metadatas, distances):
        # Distancia coseno → similitud (1 = identico, 0 = nada parecido)
        similarity = round(1.0 - dist, 4)
        output.append({
            "score":    similarity,
            "fuente":   meta.get("fuente", "?"),
            "tipo":     meta.get("tipo", "?"),
            "activo":   meta.get("activo", "?"),
            "build":    meta.get("build", "?"),
            "fragment": doc[:300] + ("..." if len(doc) > 300 else ""),
        })

    return output


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    if not HAS_CHROMADB:
        print("[ERROR] ChromaDB no esta instalado.")
        print("Instalar con:  pip install chromadb")
        return 1

    parser = argparse.ArgumentParser(description="Knowledge Base — TradingLab")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcomando index
    p_index = subparsers.add_parser("index", help="Indexar documentos del proyecto")
    p_index.add_argument(
        "--repo-path",
        type=Path,
        default=Path("."),
        help="Ruta raiz del repo (default: .)",
    )

    # Subcomando query
    p_query = subparsers.add_parser("query", help="Consultar la base de datos")
    p_query.add_argument("pregunta", help="Pregunta en lenguaje natural")
    p_query.add_argument(
        "--n-results",
        type=int,
        default=5,
        help="Numero de resultados (default: 5)",
    )
    p_query.add_argument(
        "--repo-path",
        type=Path,
        default=Path("."),
        help="Ruta raiz del repo (default: .)",
    )

    args = parser.parse_args()

    if args.command == "index":
        indexed = index_project(args.repo_path)
        print(f"Indexacion completada: {indexed} chunks.")
        return 0

    if args.command == "query":
        results = query(args.pregunta, args.repo_path, args.n_results)
        if not results:
            print("Sin resultados. Ejecuta primero: python knowledge-base.py index")
            return 0

        print(f'\nResultados para: "{args.pregunta}"\n{"="*60}')
        for i, r in enumerate(results, 1):
            print(f"\n[{i}] Score: {r['score']} | {r['tipo']} | activo: {r['activo']} | build: {r['build']}")
            print(f"    Fuente: {r['fuente']}")
            print(f"    {r['fragment']}")

        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
