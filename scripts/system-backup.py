#!/usr/bin/env python3
"""
system-backup.py — Backup completo del sistema TradingLab.

Hace backup de KG, ChromaDB, configs criticos y results importantes.
Retiene los últimos 7 backups de cada tipo.

Uso:
    python scripts/system-backup.py --full
    python scripts/system-backup.py --kg
    python scripts/system-backup.py --chromadb
    python scripts/system-backup.py --configs
    python scripts/system-backup.py --results
    python scripts/system-backup.py --list
    python scripts/system-backup.py --restore 2026-04-29
"""

import argparse
import io
import json
import shutil
import subprocess
import sys
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT     = Path(__file__).parent.parent
BACKUPS  = ROOT / "backups"
_PYTHON  = sys.executable
MAX_KEEP = 7

CONFIG_FILES = [
    "config/pipeline-config.json",
    "config/build-defaults.json",
    "config/bayesian-criteria.json",
    "config/propfirm-rules.json",
    "config/api-keys.json.template",
]

RESULTS_FILES = [
    "results/strategies-registry.json",
    "results/audit-trail.log",
    "results/champion-challenger.json",
    "results/thompson-state.json",
    "results/drift-detection.json",
    "results/build-queue.json",
]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _date_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _prune(folder: Path, prefix: str, suffix: str):
    """Elimina backups más antiguos dejando solo MAX_KEEP."""
    files = sorted(folder.glob(f"{prefix}*{suffix}"))
    for old in files[:-MAX_KEEP]:
        old.unlink(missing_ok=True)
        print(f"  Eliminado: {old.name}")


def _verify(path: Path) -> bool:
    """Verifica que el archivo existe y tiene tamaño > 0."""
    return path.exists() and path.stat().st_size > 0


def _notify_telegram(msg: str):
    notifier = ROOT / "scripts" / "telegram-notifier.py"
    if not notifier.exists():
        return
    subprocess.run(
        [_PYTHON, str(notifier), "--level", "INFO", "--message", msg],
        capture_output=True,
    )


def _human_size(path: Path) -> str:
    size = path.stat().st_size if path.exists() else 0
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


# ─── Backups individuales ──────────────────────────────────────────────────────

def backup_kg() -> Path | None:
    """Backup .kuzu/ → backups/kg/tradinglab-kg-[fecha].tar.gz"""
    src = ROOT / ".kuzu"
    if not src.exists():
        print("  [SKIP] .kuzu/ no existe — KG no inicializado")
        return None

    out_dir = BACKUPS / "kg"
    out_dir.mkdir(parents=True, exist_ok=True)
    date   = _date_str()
    out    = out_dir / f"tradinglab-kg-{date}.tar.gz"

    print(f"  Empaquetando .kuzu/ → {out.name} ...")
    with tarfile.open(out, "w:gz") as tar:
        tar.add(src, arcname=".kuzu")

    if _verify(out):
        print(f"  OK — {_human_size(out)}")
        _prune(out_dir, "tradinglab-kg-", ".tar.gz")
        return out
    else:
        print("  ERROR — archivo vacio o no creado")
        return None


def backup_chromadb() -> Path | None:
    """Backup .chromadb/ → backups/chromadb/chromadb-[fecha].tar.gz"""
    src = ROOT / ".chromadb"
    if not src.exists():
        print("  [SKIP] .chromadb/ no existe")
        return None

    out_dir = BACKUPS / "chromadb"
    out_dir.mkdir(parents=True, exist_ok=True)
    date = _date_str()
    out  = out_dir / f"chromadb-{date}.tar.gz"

    print(f"  Empaquetando .chromadb/ → {out.name} ...")
    with tarfile.open(out, "w:gz") as tar:
        tar.add(src, arcname=".chromadb")

    if _verify(out):
        print(f"  OK — {_human_size(out)}")
        _prune(out_dir, "chromadb-", ".tar.gz")
        return out
    else:
        print("  ERROR — archivo vacio o no creado")
        return None


def backup_configs() -> Path | None:
    """Backup configs criticos → backups/config/config-[fecha].zip"""
    out_dir = BACKUPS / "config"
    out_dir.mkdir(parents=True, exist_ok=True)
    date = _date_str()
    out  = out_dir / f"config-{date}.zip"

    included = 0
    print(f"  Empaquetando configs → {out.name} ...")
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in CONFIG_FILES:
            src = ROOT / rel
            if src.exists():
                zf.write(src, rel)
                included += 1
            else:
                print(f"    [SKIP] {rel} no existe")

    if included > 0 and _verify(out):
        print(f"  OK — {included} archivos, {_human_size(out)}")
        _prune(out_dir, "config-", ".zip")
        return out
    else:
        print("  ERROR — ningun archivo incluido")
        return None


def backup_results() -> Path | None:
    """Backup results importantes → backups/results/results-[fecha].zip"""
    out_dir = BACKUPS / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    date = _date_str()
    out  = out_dir / f"results-{date}.zip"

    included = 0
    print(f"  Empaquetando results → {out.name} ...")
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in RESULTS_FILES:
            src = ROOT / rel
            if src.exists():
                zf.write(src, rel)
                included += 1
            else:
                print(f"    [SKIP] {rel} no existe")

    if included > 0 and _verify(out):
        print(f"  OK — {included} archivos, {_human_size(out)}")
        _prune(out_dir, "results-", ".zip")
        return out
    else:
        print("  ERROR — ningun archivo incluido")
        return None


# ─── Operaciones principales ───────────────────────────────────────────────────

def run_full():
    print("\nBackup completo — TradingLab")
    print("=" * 55)
    created = []

    print("\n[1/4] Knowledge Graph")
    p = backup_kg()
    if p:
        created.append(p)

    print("\n[2/4] ChromaDB")
    p = backup_chromadb()
    if p:
        created.append(p)

    print("\n[3/4] Configs criticos")
    p = backup_configs()
    if p:
        created.append(p)

    print("\n[4/4] Results importantes")
    p = backup_results()
    if p:
        created.append(p)

    total_size = sum(f.stat().st_size for f in created if f.exists())
    size_str   = f"{total_size / (1024*1024):.1f} MB" if total_size > 0 else "0 B"
    print("\n" + "=" * 55)
    print(f"  Backup completado: {len(created)}/4 exitosos, {size_str} total")
    print(f"  Directorio: backups/")
    _notify_telegram(
        f"Backup TradingLab completado: {len(created)}/4 componentes, {size_str}"
    )


def list_backups():
    print("\nBackups existentes:")
    print("=" * 55)
    total = 0
    for sub in ("kg", "chromadb", "config", "results"):
        folder = BACKUPS / sub
        if not folder.exists():
            continue
        files = sorted(folder.iterdir())
        if not files:
            continue
        print(f"\n  {sub}/")
        for f in files:
            size = _human_size(f)
            print(f"    {f.name:<45} {size:>8}")
            total += f.stat().st_size
    print(f"\n  Total: {total / (1024*1024):.1f} MB")


def restore_backup(date_str: str):
    """Restaura todos los backups de una fecha dada."""
    print(f"\nRestaurando backups de {date_str}...")
    print("=" * 55)

    # KG
    kg_file = BACKUPS / "kg" / f"tradinglab-kg-{date_str}.tar.gz"
    if kg_file.exists():
        dest = ROOT / ".kuzu"
        if dest.exists():
            shutil.rmtree(dest)
        with tarfile.open(kg_file, "r:gz") as tar:
            tar.extractall(ROOT)
        print(f"  KG restaurado desde {kg_file.name}")
    else:
        print(f"  [SKIP] KG — no encontrado: {kg_file.name}")

    # ChromaDB
    chroma_file = BACKUPS / "chromadb" / f"chromadb-{date_str}.tar.gz"
    if chroma_file.exists():
        dest = ROOT / ".chromadb"
        if dest.exists():
            shutil.rmtree(dest)
        with tarfile.open(chroma_file, "r:gz") as tar:
            tar.extractall(ROOT)
        print(f"  ChromaDB restaurado desde {chroma_file.name}")
    else:
        print(f"  [SKIP] ChromaDB — no encontrado: {chroma_file.name}")

    # Configs
    cfg_file = BACKUPS / "config" / f"config-{date_str}.zip"
    if cfg_file.exists():
        with zipfile.ZipFile(cfg_file, "r") as zf:
            zf.extractall(ROOT)
        print(f"  Configs restaurados desde {cfg_file.name}")
    else:
        print(f"  [SKIP] Configs — no encontrado: {cfg_file.name}")

    # Results
    res_file = BACKUPS / "results" / f"results-{date_str}.zip"
    if res_file.exists():
        with zipfile.ZipFile(res_file, "r") as zf:
            zf.extractall(ROOT)
        print(f"  Results restaurados desde {res_file.name}")
    else:
        print(f"  [SKIP] Results — no encontrado: {res_file.name}")

    print("\n  Restauracion completada.")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="System Backup — TradingLab")
    parser.add_argument("--full",     action="store_true", help="Backup completo de todo")
    parser.add_argument("--kg",       action="store_true", help="Solo Knowledge Graph")
    parser.add_argument("--chromadb", action="store_true", help="Solo ChromaDB")
    parser.add_argument("--configs",  action="store_true", help="Solo configuraciones")
    parser.add_argument("--results",  action="store_true", help="Solo results importantes")
    parser.add_argument("--list",     action="store_true", help="Listar backups existentes")
    parser.add_argument("--restore",  metavar="DATE",
                        help="Restaurar backup de una fecha (YYYY-MM-DD)")
    args = parser.parse_args()

    if args.restore:
        restore_backup(args.restore)
    elif args.list:
        list_backups()
    elif args.kg:
        print("\n[KG] Knowledge Graph backup")
        backup_kg()
    elif args.chromadb:
        print("\n[ChromaDB] ChromaDB backup")
        backup_chromadb()
    elif args.configs:
        print("\n[Configs] Configuraciones backup")
        backup_configs()
    elif args.results:
        print("\n[Results] Results backup")
        backup_results()
    else:
        run_full()


if __name__ == "__main__":
    main()
