#!/usr/bin/env python3
"""
lessons-auto-updater.py — Sincroniza lecciones entre el Knowledge Graph y lessons-learned.md.

Proceso:
  1. Leer lecciones del KG
  2. Comparar con lessons-learned.md
  3. Añadir lecciones nuevas del KG al MD
  4. Promover TENTATIVA con 3+ ocurrencias a ESTRUCTURAL
  5. Registrar cambios en audit trail

Uso:
    python scripts/lessons-auto-updater.py --check
    python scripts/lessons-auto-updater.py --update
    python scripts/lessons-auto-updater.py --dry-run
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT    = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"
LESSONS = ROOT / "docs" / "lessons-learned.md"

PROMOTE_THRESHOLD = 3   # ocurrencias para promover TENTATIVA → ESTRUCTURAL


def _run(cmd: list, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _log_audit(description: str) -> None:
    logger = SCRIPTS / "hash-logger.py"
    if not logger.exists():
        return
    subprocess.run(
        [sys.executable, str(logger),
         "--event", "LESSONS_UPDATE",
         "--description", description],
        capture_output=True,
    )


def _get_kg_lessons() -> list:
    """Obtener todas las lecciones almacenadas en el Knowledge Graph."""
    kg_script = SCRIPTS / "knowledge-graph.py"
    if not kg_script.exists():
        return []
    try:
        r = _run([sys.executable, str(kg_script), "query",
                  "--type", "lesson", "--all"], timeout=30)
        if r.returncode != 0:
            return []
        lessons = []
        # Parsear salida del KG — formato esperado: JSON array o lineas
        try:
            data = json.loads(r.stdout)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass
        # Parsear lineas con formato "LECCION-XXX | descripcion | tipo | ocurrencias"
        for line in r.stdout.splitlines():
            m = re.match(
                r"(LECCION-\d+)\s*\|?\s*(.+?)\s*\|?\s*(TENTATIVA|ESTRUCTURAL|PERMANENTE)?"
                r"\s*\|?\s*(\d+)?",
                line.strip(), re.IGNORECASE
            )
            if m:
                lessons.append({
                    "id":          m.group(1),
                    "descripcion": m.group(2).strip(),
                    "tipo":        (m.group(3) or "TENTATIVA").upper(),
                    "ocurrencias": int(m.group(4) or 1),
                })
        return lessons
    except Exception:
        return []


def _parse_md_lessons(text: str) -> dict:
    """
    Parsear lessons-learned.md y devolver dict {id: {tipo, ocurrencias, linea_inicio}}.
    """
    lessons = {}
    lines   = text.splitlines()
    i       = 0
    while i < len(lines):
        m = re.match(r"###\s*(LECCION-\d+)", lines[i].strip())
        if m:
            lesson_id = m.group(1)
            tipo      = "TENTATIVA"
            ocurr     = 1
            for j in range(i + 1, min(i + 30, len(lines))):
                line_lower = lines[j].lower()
                if "ocurrencias confirmadas:" in line_lower:
                    val = lines[j].split(":", 1)[-1].strip().upper()
                    if "ESTRUCTURAL" in val or "PERMANENTE" in val:
                        tipo = val.split()[0]
                    else:
                        try:
                            ocurr = int(re.search(r"\d+", val).group())
                        except (AttributeError, ValueError):
                            pass
                if "tipo:" in line_lower:
                    val = lines[j].split(":", 1)[-1].strip().upper()
                    if val in ("TENTATIVA", "ESTRUCTURAL", "PERMANENTE"):
                        tipo = val
            lessons[lesson_id] = {
                "tipo":       tipo,
                "ocurrencias": ocurr,
                "linea":       i,
            }
        i += 1
    return lessons


def _next_lesson_id(existing: dict) -> str:
    nums = [int(re.search(r"\d+", k).group()) for k in existing if re.search(r"\d+", k)]
    n    = max(nums, default=0) + 1
    return f"LECCION-{n:03d}"


def _lesson_block(lesson: dict, lesson_id: str) -> str:
    """Generar bloque Markdown para una lección nueva."""
    today = datetime.now().strftime("%Y-%m-%d")
    tipo  = lesson.get("tipo", "TENTATIVA")
    desc  = lesson.get("descripcion", "Sin descripcion")
    return (
        f"\n### {lesson_id}\n"
        f"**Descripcion:** {desc}\n"
        f"**Tipo:** {tipo}\n"
        f"**Fecha:** {today}\n"
        f"**Ocurrencias confirmadas:** 1\n"
        f"**Fuente:** Knowledge Graph (auto-import)\n"
    )


def check(verbose: bool = True) -> dict:
    """Verificar si hay lecciones nuevas o para promover. No modifica nada."""
    if not LESSONS.exists():
        if verbose:
            print("  lessons-learned.md no encontrado")
        return {"nuevas": [], "para_promover": []}

    text      = LESSONS.read_text(encoding="utf-8")
    md_lessons = _parse_md_lessons(text)
    kg_lessons = _get_kg_lessons()

    nuevas       = []
    para_promover = []

    # Lecciones en KG que no están en MD
    md_ids = {lid.upper() for lid in md_lessons}
    for kl in kg_lessons:
        kid = kl.get("id", "").upper()
        if kid and kid not in md_ids:
            nuevas.append(kl)

    # Lecciones TENTATIVA en MD con 3+ ocurrencias
    for lid, info in md_lessons.items():
        if info["tipo"] == "TENTATIVA" and info["ocurrencias"] >= PROMOTE_THRESHOLD:
            para_promover.append(lid)

    if verbose:
        if nuevas:
            print(f"  Lecciones nuevas en KG: {len(nuevas)}")
            for l in nuevas:
                print(f"    + {l.get('id')} — {l.get('descripcion', '')[:60]}")
        else:
            print("  Sin lecciones nuevas en KG")

        if para_promover:
            print(f"  Para promover TENTATIVA→ESTRUCTURAL: {len(para_promover)}")
            for lid in para_promover:
                print(f"    ^ {lid}")
        else:
            print("  Sin lecciones para promover")

    return {"nuevas": nuevas, "para_promover": para_promover}


def update(dry_run: bool = False) -> int:
    """Aplicar actualizaciones al MD. Retorna número de cambios."""
    if not LESSONS.exists():
        print("  lessons-learned.md no encontrado — nada que actualizar")
        return 0

    result    = check(verbose=False)
    nuevas    = result["nuevas"]
    para_prom = result["para_promover"]
    cambios   = 0

    text      = LESSONS.read_text(encoding="utf-8")

    # 1. Añadir lecciones nuevas
    if nuevas:
        md_lessons = _parse_md_lessons(text)
        for kl in nuevas:
            new_id = kl.get("id") or _next_lesson_id(md_lessons)
            block  = _lesson_block(kl, new_id)
            if dry_run:
                print(f"  [DRY-RUN] Añadiria {new_id}: {kl.get('descripcion', '')[:60]}")
            else:
                # Insertar antes del cierre del historial o al final del documento
                if "## HISTORIAL DE LECCIONES" in text:
                    text = text + block
                else:
                    text = text + f"\n## HISTORIAL DE LECCIONES\n{block}"
                md_lessons[new_id] = {"tipo": kl.get("tipo", "TENTATIVA"),
                                      "ocurrencias": 1, "linea": -1}
                print(f"  Añadida {new_id}: {kl.get('descripcion', '')[:60]}")
            cambios += 1

    # 2. Promover TENTATIVA → ESTRUCTURAL
    if para_prom:
        for lid in para_prom:
            patron = re.compile(
                rf"(###\s*{re.escape(lid)}.*?)(Ocurrencias confirmadas:\s*\d+)",
                re.IGNORECASE | re.DOTALL,
            )
            if dry_run:
                print(f"  [DRY-RUN] Promoveria {lid} a ESTRUCTURAL")
            else:
                new_text = re.sub(
                    rf"(###\s*{re.escape(lid)}[^\n]*\n(?:.*\n){{0,5}})"
                    rf"(\*\*Tipo:\*\*\s*)TENTATIVA",
                    r"\1\2ESTRUCTURAL",
                    text, flags=re.IGNORECASE
                )
                if new_text != text:
                    text = new_text
                    print(f"  Promovida {lid}: TENTATIVA → ESTRUCTURAL")
                else:
                    print(f"  No se pudo promover {lid} (patron no encontrado)")
            cambios += 1

    if not dry_run and cambios > 0:
        LESSONS.write_text(text, encoding="utf-8")
        _log_audit(
            f"lessons-auto-updater: {len(nuevas)} nuevas, {len(para_prom)} promovidas"
        )

    if cambios == 0:
        print("  Sin cambios necesarios")
    elif not dry_run:
        print(f"  {cambios} cambio(s) aplicados en {LESSONS.name}")

    return cambios


def main() -> int:
    parser = argparse.ArgumentParser(description="Lessons Auto-Updater — TradingLab")
    parser.add_argument("--check",   action="store_true", help="Verificar sin modificar")
    parser.add_argument("--update",  action="store_true", help="Aplicar actualizaciones")
    parser.add_argument("--dry-run", action="store_true", help="Mostrar cambios sin aplicar")
    args = parser.parse_args()

    if args.check:
        result = check()
        total = len(result["nuevas"]) + len(result["para_promover"])
        return 0 if total == 0 else 1

    if args.update or args.dry_run:
        cambios = update(dry_run=args.dry_run)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
