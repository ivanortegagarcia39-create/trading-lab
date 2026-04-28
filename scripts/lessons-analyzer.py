"""
lessons-analyzer.py
Analiza lessons-learned.md con Ollama y propone ajustes a criterios del pipeline.

Dos modos:
  - Modo estandar: analiza lecciones ESTRUCTURALES y propone ajustes
  - Modo --daily: analiza las ultimas decisiones del orchestrator
    desde results/audit-trail.log

Uso:
    python lessons-analyzer.py
    python lessons-analyzer.py --lessons-file docs/lessons-learned.md
    python lessons-analyzer.py --daily
    python lessons-analyzer.py --no-ollama
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path


# ─── Configuracion ────────────────────────────────────────────────────────────

OLLAMA_URL   = "http://localhost:11434"
OLLAMA_MODEL = "deepseek-r1:7b"
OLLAMA_TIMEOUT = 180

LESSONS_FILE   = Path("docs/lessons-learned.md")
AUDIT_LOG      = Path("results/audit-trail.log")
OUTPUT_FILE    = Path("results/criteria-proposals.json")
DAILY_LINES    = 10   # Ultimas N decisiones del orchestrator


# ─── Parseo de lessons-learned.md ────────────────────────────────────────────

_LESSON_HEADER_RE = re.compile(r"^###\s+(LECCION-\d+):\s*(.+)$", re.MULTILINE)
_FIELD_RE = re.compile(r"^(Estado|Ocurrencias confirmadas):\s*(.+)$", re.MULTILINE)


def parse_lessons(lessons_text: str) -> list[dict]:
    """
    Extrae todas las lecciones del documento.
    Devuelve lista de dicts con id, titulo, texto completo y estado.
    """
    lessons = []
    headers = list(_LESSON_HEADER_RE.finditer(lessons_text))

    for i, match in enumerate(headers):
        lesson_id = match.group(1)
        titulo    = match.group(2).strip()
        start     = match.start()
        end       = headers[i + 1].start() if i + 1 < len(headers) else len(lessons_text)
        body      = lessons_text[start:end]

        # Extraer estado y ocurrencias
        estado = "TENTATIVA"
        ocurrencias = 1
        for m in _FIELD_RE.finditer(body):
            if m.group(1) == "Estado":
                estado = m.group(2).strip().split()[0].upper()
            elif m.group(1) == "Ocurrencias confirmadas":
                try:
                    ocurrencias = int(m.group(2).strip().split()[0])
                except ValueError:
                    pass

        lessons.append({
            "id":          lesson_id,
            "titulo":      titulo,
            "estado":      estado,
            "ocurrencias": ocurrencias,
            "texto":       body.strip(),
        })

    return lessons


def filter_structural(lessons: list[dict]) -> list[dict]:
    """Filtra solo lecciones con estado ESTRUCTURAL (>=3 ocurrencias)."""
    return [l for l in lessons if l["estado"] == "ESTRUCTURAL" or l["ocurrencias"] >= 3]


# ─── Lectura de audit trail ───────────────────────────────────────────────────

def load_recent_decisions(audit_log: Path, n: int = DAILY_LINES) -> list[str]:
    """Carga las ultimas N lineas del audit trail del orchestrator."""
    if not audit_log.exists():
        return []
    lines = audit_log.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[-n:]


# ─── Ollama ───────────────────────────────────────────────────────────────────

def ollama_available(base_url: str = OLLAMA_URL) -> bool:
    try:
        req = urllib.request.urlopen(f"{base_url}/api/tags", timeout=5)
        return req.status == 200
    except Exception:
        return False


def ollama_call(prompt: str, base_url: str = OLLAMA_URL) -> str:
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }).encode()

    req = urllib.request.Request(
        f"{base_url}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
            data = json.loads(resp.read())
            return data.get("response", "").strip()
    except Exception as e:
        return f"[Error Ollama: {e}]"


def analyze_lessons_with_ollama(structural_lessons: list[dict], base_url: str) -> list[dict]:
    """
    Envia lecciones estructurales a Ollama y devuelve propuestas en JSON.
    El resultado es una lista de dicts con los campos definidos en el planning.
    """
    if not structural_lessons:
        return []

    lessons_text = "\n\n---\n\n".join(
        f"ID: {l['id']}\nTitulo: {l['titulo']}\n\n{l['texto'][:600]}"
        for l in structural_lessons
    )

    prompt = (
        "Eres el knowledge-synthesizer de TradingLab. "
        "Analiza estas lecciones aprendidas del sistema de trading algoritmico. "
        "Para cada leccion:\n"
        "1. Confirma si sigue siendo valida\n"
        "2. Propone ajuste especifico a criterios del pipeline\n"
        "3. Identifica si hay contradicciones entre lecciones\n"
        "Responde SOLO en JSON valido (sin markdown, sin explicaciones adicionales) "
        "con un array de objetos con campos:\n"
        "lesson_id (string), still_valid (bool), "
        "proposed_adjustment (string), confidence (float 0-1)\n\n"
        "Lecciones a analizar:\n\n"
        + lessons_text
    )

    raw = ollama_call(prompt, base_url)

    # Intentar parsear JSON de la respuesta
    # Buscar el primer [ o { en la respuesta
    json_start = raw.find("[")
    if json_start == -1:
        json_start = raw.find("{")
    if json_start != -1:
        raw_json = raw[json_start:]
        # Encontrar el final
        json_end = raw_json.rfind("]") + 1 or raw_json.rfind("}") + 1
        raw_json = raw_json[:json_end]
        try:
            parsed = json.loads(raw_json)
            if isinstance(parsed, dict):
                parsed = [parsed]
            return parsed
        except json.JSONDecodeError:
            pass

    # Si no se pudo parsear, devolver como texto
    return [{"lesson_id": "N/A", "raw_response": raw, "parse_error": True}]


def analyze_daily_with_ollama(decisions: list[str], base_url: str) -> str:
    """Analiza las ultimas decisiones del orchestrator y propone refinamientos."""
    if not decisions:
        return "No hay decisiones recientes en el audit trail."

    decisions_text = "\n".join(decisions)

    prompt = (
        "Eres el knowledge-synthesizer de TradingLab. "
        "Analiza estas ultimas decisiones del orchestrator del pipeline de trading algoritmico:\n\n"
        + decisions_text
        + "\n\nPropone hasta 3 refinamientos concretos para mejorar el pipeline "
        "en el dia de manana. Responde en espanol, maximo 150 palabras. "
        "Sé especifico: nombra criterios o umbrales concretos si es posible."
    )

    return ollama_call(prompt, base_url)


# ─── Salida sin Ollama ────────────────────────────────────────────────────────

def static_analysis(structural_lessons: list[dict]) -> list[dict]:
    """Analisis estatico cuando Ollama no esta disponible."""
    proposals = []
    for l in structural_lessons:
        proposals.append({
            "lesson_id":           l["id"],
            "still_valid":         None,   # No determinable sin LLM
            "proposed_adjustment": "Revisar manualmente — Ollama no disponible.",
            "confidence":          0.0,
            "ocurrencias":         l["ocurrencias"],
        })
    return proposals


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Lessons Analyzer — TradingLab")
    parser.add_argument(
        "--lessons-file",
        type=Path,
        default=LESSONS_FILE,
        help=f"Ruta a lessons-learned.md (default: {LESSONS_FILE})",
    )
    parser.add_argument(
        "--daily",
        action="store_true",
        help="Modo reflexion diaria — analizar ultimas decisiones del orchestrator",
    )
    parser.add_argument(
        "--no-ollama",
        action="store_true",
        help="Desactivar integracion con Ollama",
    )
    parser.add_argument(
        "--ollama-url",
        default=OLLAMA_URL,
        help=f"URL de Ollama (default: {OLLAMA_URL})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_FILE,
        help=f"Archivo de salida JSON (default: {OUTPUT_FILE})",
    )
    args = parser.parse_args()

    print(f"\nLessons Analyzer — TradingLab")
    print(f"{'='*60}")

    # Modo reflexion diaria
    if args.daily:
        print(f"Modo: reflexion diaria — {DAILY_LINES} ultimas decisiones")
        decisions = load_recent_decisions(AUDIT_LOG)
        if not decisions:
            print(f"[WARN] Audit trail vacio o no encontrado: {AUDIT_LOG}")

        daily_output = ""
        if not args.no_ollama and ollama_available(args.ollama_url):
            print(f"Ollama disponible. Analizando...")
            daily_output = analyze_daily_with_ollama(decisions, args.ollama_url)
        else:
            print("Ollama no disponible. Listando decisiones recientes.")
            daily_output = "\n".join(decisions) if decisions else "Sin decisiones registradas."

        # Guardar resultado diario
        daily_path = Path("results") / f"daily-reflection-{datetime.now().strftime('%Y%m%d')}.md"
        daily_path.parent.mkdir(exist_ok=True)
        content = f"# Reflexion diaria — {datetime.now().strftime('%Y-%m-%d')}\n\n"
        content += f"## Ultimas {DAILY_LINES} decisiones\n\n"
        content += "\n".join(decisions) + "\n\n"
        content += "## Refinamientos propuestos\n\n"
        content += daily_output + "\n"
        daily_path.write_text(content, encoding="utf-8")
        print(f"\nReflexion guardada: {daily_path}")
        print(f"\n{daily_output[:400]}")
        return 0

    # Modo estandar — analisis de lecciones
    if not args.lessons_file.exists():
        print(f"[ERROR] Archivo no encontrado: {args.lessons_file}")
        return 1

    print(f"Leyendo: {args.lessons_file}")
    lessons_text = args.lessons_file.read_text(encoding="utf-8", errors="replace")
    all_lessons = parse_lessons(lessons_text)
    structural  = filter_structural(all_lessons)

    print(f"  Total lecciones: {len(all_lessons)}")
    print(f"  Lecciones ESTRUCTURALES: {len(structural)}")

    if not structural:
        print("No hay lecciones ESTRUCTURALES para analizar.")
        print("(Se necesitan >= 3 ocurrencias confirmadas en contextos diferentes)")
        return 0

    for l in structural:
        print(f"  → {l['id']}: {l['titulo']} ({l['ocurrencias']} ocurrencias)")

    # Analisis
    proposals = []
    if not args.no_ollama and ollama_available(args.ollama_url):
        print(f"\nOllama disponible ({args.ollama_url}). Analizando con {OLLAMA_MODEL}...")
        proposals = analyze_lessons_with_ollama(structural, args.ollama_url)
        print(f"  {len(proposals)} propuestas generadas.")
    else:
        print("\nOllama no disponible. Generando analisis estatico.")
        proposals = static_analysis(structural)

    # Guardar propuestas
    output = {
        "timestamp":    datetime.now().isoformat(timespec="seconds"),
        "total_structural_lessons": len(structural),
        "ollama_used":  not args.no_ollama and ollama_available(args.ollama_url),
        "proposals":    proposals,
        "nota":         "El humano revisa estas propuestas antes de aplicar cambios a criterios.",
    }

    args.output.parent.mkdir(exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nPropuestas guardadas en: {args.output}")
    print(f"\n[IMPORTANTE] Revision humana requerida antes de aplicar cambios.")

    # Mostrar resumen
    print(f"\n--- Propuestas ---")
    for p in proposals[:5]:
        lid = p.get("lesson_id", "?")
        adj = p.get("proposed_adjustment", p.get("raw_response", "?"))[:120]
        conf = p.get("confidence", "?")
        valid = p.get("still_valid", "?")
        print(f"  {lid}: valida={valid}, confianza={conf}")
        print(f"    {adj}")

    # Insertar lecciones ESTRUCTURALES en el Knowledge Graph
    _insert_structural_lessons_to_kg(structural)

    return 0


def _insert_structural_lessons_to_kg(structural: list[dict]) -> None:
    """Inserta lecciones ESTRUCTURALES en el Knowledge Graph via subprocess."""
    import subprocess
    kg_script = Path(__file__).parent / "knowledge-graph.py"
    if not kg_script.exists():
        print("[WARN] knowledge-graph.py no encontrado — saltando KG")
        return
    if not structural:
        return

    print(f"\n[KG] Insertando {len(structural)} lecciones ESTRUCTURALES en el Knowledge Graph...")
    inserted = 0
    for l in structural:
        data = json.dumps({
            "lesson_id":   l["id"],
            "titulo":      l["titulo"],
            "estado":      l["estado"],
            "ocurrencias": l["ocurrencias"],
            "fecha":       datetime.now().strftime("%Y-%m-%d"),
        })
        result = subprocess.run(
            [sys.executable, str(kg_script), "--mode", "add-lesson", "--data", data],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            inserted += 1
        else:
            print(f"  WARN: {l['id']}: {result.stderr.strip()[:80]}")

    print(f"  {inserted}/{len(structural)} lecciones insertadas en el KG.")


if __name__ == "__main__":
    sys.exit(main())
