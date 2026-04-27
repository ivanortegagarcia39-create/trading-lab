#!/usr/bin/env python3
"""
system-health-check.py — Verificacion completa del sistema TradingLab

Uso:
    python scripts/system-health-check.py
    python scripts/system-health-check.py --fix
"""

import argparse
import importlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
RESULTS_DIR = ROOT / "results"

REQUIRED_DIRS = ["agents", "docs/skills", "scripts", "config", "results", "templates"]
CRITICAL_FILES = ["CLAUDE.md", "config/pipeline-config.json", "config/build-defaults.json"]
REQUIRED_PACKAGES = ["pandas", "numpy", "pytz", "requests"]
OPTIONAL_PACKAGES = ["chromadb"]

STATUS = {"OK": "OK  ", "WARN": "WARN", "FAIL": "FAIL"}
_results: list[dict] = []


def _record(check: str, status: str, detail: str = ""):
    _results.append({"check": check, "status": status, "detail": detail})
    icon = {"OK": "✓", "WARN": "!", "FAIL": "✗"}.get(status, "?")
    line = f"  [{icon}] {check:<45} {STATUS[status]}"
    if detail:
        line += f"  — {detail}"
    print(line)


# ─── 1. Python y dependencias ──────────────────────────────────────────────

def check_dependencies():
    print("\n[1] Dependencias Python")
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
            _record(f"  {pkg}", "OK")
        except ImportError:
            _record(f"  {pkg}", "FAIL", "pip install " + pkg)

    for pkg in OPTIONAL_PACKAGES:
        try:
            importlib.import_module(pkg)
            _record(f"  {pkg} (opcional)", "OK")
        except ImportError:
            _record(f"  {pkg} (opcional)", "WARN", "pip install " + pkg + " para ChromaDB")


def fix_dependencies():
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
        except ImportError:
            print(f"  Instalando {pkg}...")
            subprocess.run([sys.executable, "-m", "pip", "install", pkg, "-q"], check=False)


# ─── 2. Estructura del repo ────────────────────────────────────────────────

def check_structure():
    print("\n[2] Estructura del repositorio")
    for d in REQUIRED_DIRS:
        path = ROOT / d
        if path.exists() and path.is_dir():
            _record(f"  {d}/", "OK")
        else:
            _record(f"  {d}/", "FAIL", "carpeta faltante")


def fix_structure():
    for d in REQUIRED_DIRS:
        path = ROOT / d
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"  Creado: {d}/")


# ─── 3. Archivos criticos ──────────────────────────────────────────────────

def check_critical_files():
    print("\n[3] Archivos criticos")
    for f in CRITICAL_FILES:
        path = ROOT / f
        if path.exists():
            _record(f"  {f}", "OK")
        else:
            _record(f"  {f}", "FAIL", "archivo requerido no encontrado")


# ─── 4. Telegram ───────────────────────────────────────────────────────────

def check_telegram():
    print("\n[4] Telegram")
    cfg_path = ROOT / "config" / "telegram-config.json"
    if not cfg_path.exists():
        _record("  config/telegram-config.json", "WARN", "bot no configurado aun")
        return

    _record("  config/telegram-config.json", "OK")
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        token = cfg.get("token", "")
        if not token or "TU_BOT" in token:
            _record("  token configurado", "WARN", "token aun es placeholder")
            return

        import urllib.request
        url = f"https://api.telegram.org/bot{token}/getMe"
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if data.get("ok"):
                username = data["result"].get("username", "?")
                _record("  bot responde ping", "OK", f"@{username}")
            else:
                _record("  bot responde ping", "FAIL", "token invalido")
    except Exception as e:
        _record("  bot responde ping", "WARN", f"sin conexion o timeout: {e}")


# ─── 5. ChromaDB ───────────────────────────────────────────────────────────

def check_chromadb():
    print("\n[5] ChromaDB")
    chroma_path = ROOT / ".chromadb"
    if not chroma_path.exists():
        _record("  .chromadb/", "WARN", "no existe — ejecutar knowledge-base.py primero")
        return

    _record("  .chromadb/", "OK")
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(chroma_path))
        collections = client.list_collections()
        total_chunks = sum(c.count() for c in collections)
        _record("  datos indexados", "OK" if total_chunks > 0 else "WARN",
                f"{total_chunks} chunks en {len(collections)} colecciones")
    except Exception as e:
        _record("  chromadb accesible", "WARN", str(e))


# ─── 6. Pipeline lock ──────────────────────────────────────────────────────

def check_pipeline_lock():
    print("\n[6] Pipeline lock")
    lock_path = RESULTS_DIR / "pipeline.lock"
    if lock_path.exists():
        content = lock_path.read_text(encoding="utf-8").strip()
        _record("  results/pipeline.lock", "WARN", f"lock activo: {content[:60]}")
    else:
        _record("  results/pipeline.lock", "OK", "sin lock activo")


def fix_pipeline_lock():
    lock_path = RESULTS_DIR / "pipeline.lock"
    if lock_path.exists():
        lock_path.unlink()
        print("  Lock eliminado: results/pipeline.lock")


# ─── 7. Git status ─────────────────────────────────────────────────────────

def check_git():
    print("\n[7] Git")
    try:
        # Verificar que es un repo git
        result = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True,
            cwd=ROOT, timeout=15
        )
        if result.returncode != 0:
            _record("  git repo", "FAIL", "no es un repositorio git")
            return
        _record("  git repo", "OK")

        # Cambios sin commitear
        uncommitted = result.stdout.strip()
        if uncommitted:
            lines = len(uncommitted.splitlines())
            _record("  working tree", "WARN", f"{lines} archivo(s) sin commitear")
        else:
            _record("  working tree", "OK", "limpio")

        # Sincronizacion con origin
        fetch = subprocess.run(
            ["git", "fetch", "origin", "--quiet"], capture_output=True,
            cwd=ROOT, timeout=15
        )
        if fetch.returncode == 0:
            behind = subprocess.run(
                ["git", "rev-list", "HEAD..origin/main", "--count"],
                capture_output=True, text=True, cwd=ROOT, timeout=10
            )
            count = behind.stdout.strip()
            if count and int(count) > 0:
                _record("  sincronizado con origin/main", "WARN",
                        f"{count} commit(s) por detr??s — git pull recomendado")
            else:
                _record("  sincronizado con origin/main", "OK")
        else:
            _record("  sincronizado con origin/main", "WARN", "sin acceso a origin")

    except FileNotFoundError:
        _record("  git disponible", "FAIL", "git no encontrado en PATH")
    except Exception as e:
        _record("  git check", "WARN", str(e))


# ─── 8. Scripts importables ────────────────────────────────────────────────

def check_scripts():
    print("\n[8] Scripts Python (sintaxis)")
    scripts_dir = ROOT / "scripts"
    py_files = sorted(scripts_dir.glob("*.py"))
    errors = []
    for f in py_files:
        if f.name == Path(__file__).name:
            continue
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(f)],
                capture_output=True, timeout=10
            )
            if result.returncode != 0:
                errors.append(f.name)
        except Exception:
            errors.append(f.name)

    if errors:
        _record(f"  {len(py_files)} scripts", "FAIL",
                "errores de sintaxis: " + ", ".join(errors))
    else:
        _record(f"  {len(py_files)} scripts", "OK", "sin errores de sintaxis")


# ─── Resultado final ───────────────────────────────────────────────────────

def _save_results():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = {
        "timestamp": datetime.now().isoformat(),
        "checks": _results,
        "summary": {
            "ok": sum(1 for r in _results if r["status"] == "OK"),
            "warn": sum(1 for r in _results if r["status"] == "WARN"),
            "fail": sum(1 for r in _results if r["status"] == "FAIL"),
        }
    }
    (RESULTS_DIR / "system-health.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return out["summary"]


def _final_verdict(summary: dict) -> str:
    if summary["fail"] > 0:
        return "SISTEMA CON ERRORES"
    if summary["warn"] > 0:
        return "ADVERTENCIAS"
    return "SISTEMA LISTO"


def main():
    parser = argparse.ArgumentParser(description="System Health Check — TradingLab")
    parser.add_argument("--fix", action="store_true",
                        help="Intenta corregir problemas menores automaticamente")
    args = parser.parse_args()

    print("=" * 65)
    print("  TradingLab — System Health Check")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    if args.fix:
        print("\n[FIX] Intentando corregir problemas menores...")
        fix_dependencies()
        fix_structure()
        fix_pipeline_lock()

    check_dependencies()
    check_structure()
    check_critical_files()
    check_telegram()
    check_chromadb()
    check_pipeline_lock()
    check_git()
    check_scripts()

    summary = _save_results()
    verdict = _final_verdict(summary)

    print("\n" + "=" * 65)
    print(f"  OK: {summary['ok']}   WARN: {summary['warn']}   FAIL: {summary['fail']}")
    print(f"  → {verdict}")
    print(f"  Guardado en: results/system-health.json")
    print("=" * 65)

    sys.exit(1 if summary["fail"] > 0 else 0)


if __name__ == "__main__":
    main()
