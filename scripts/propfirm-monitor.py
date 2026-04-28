#!/usr/bin/env python3
"""
propfirm-monitor.py — Monitoreo de cambios en T&C de prop firms.

Detecta automáticamente cuando una prop firm cambia sus reglas
antes de que afecte a estrategias en producción.

Uso:
    python scripts/propfirm-monitor.py --check
    python scripts/propfirm-monitor.py --history
    python scripts/propfirm-monitor.py --force
    python scripts/propfirm-monitor.py --dry-run --check
"""

import argparse
import hashlib
import io
import json
import sys
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT        = Path(__file__).parent.parent
HASHES_PATH = ROOT / "results" / "propfirm-hashes.json"
LOG_PATH    = ROOT / "results" / "propfirm-changes-log.json"

PROPFIRM_URLS = {
    "ftmo":         "https://ftmo.com/en/trading-rules/",
    "e8_funding":   "https://e8funding.com/rules/",
    "brightfunded": "https://brightfunded.com/trading-rules/",
}

CRITICAL_KEYWORDS  = ["prohibited", "banned", "ea ", "automated", "drawdown", "daily loss",
                       "prohibido", "prohibida", "drawdown diario"]
IMPORTANT_KEYWORDS = ["minimum", "trading days", "profit split", "mínimo", "días de trading"]

_PYTHON = sys.executable


# ─── I/O ──────────────────────────────────────────────────────────────────────

def _load_hashes() -> dict:
    if not HASHES_PATH.exists():
        return {}
    with open(HASHES_PATH, encoding="utf-8") as f:
        return json.load(f)


def _save_hashes(hashes: dict):
    HASHES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(HASHES_PATH, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=2, ensure_ascii=False)


def _load_log() -> list:
    if not LOG_PATH.exists():
        return []
    with open(LOG_PATH, encoding="utf-8") as f:
        return json.load(f)


def _save_log(log: list):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


# ─── Descarga y hash ──────────────────────────────────────────────────────────

def _fetch_content(url: str) -> tuple[str, str] | tuple[None, str]:
    """Descarga una URL. Devuelve (contenido_texto, error_msg)."""
    try:
        import urllib.request
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 TradingLab-Monitor/1.0"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
        # Intentar decodificar con charset de la cabecera
        charset = "utf-8"
        ct = resp.headers.get("Content-Type", "")
        if "charset=" in ct:
            charset = ct.split("charset=")[-1].strip().split(";")[0]
        text = raw.decode(charset, errors="replace")
        return text, ""
    except Exception as e:
        return None, str(e)


def _extract_text(html: str) -> str:
    """Extrae texto relevante del HTML. Usa BeautifulSoup si está disponible."""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return " ".join(soup.get_text(separator=" ").split())
    except ImportError:
        # Fallback básico: eliminar tags HTML
        import re
        text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>",  " ", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        return " ".join(text.split())


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ─── Clasificación de cambios ─────────────────────────────────────────────────

def _classify_change(old_text: str, new_text: str) -> tuple[str, list[str]]:
    """Clasifica el cambio como CRÍTICO/IMPORTANTE/INFORMATIVO."""
    # Buscar en las palabras nuevas (diferencia aproximada)
    old_words = set(old_text.lower().split())
    new_words = set(new_text.lower().split())
    added = " ".join(new_words - old_words)

    found_critical  = [kw for kw in CRITICAL_KEYWORDS  if kw in added]
    found_important = [kw for kw in IMPORTANT_KEYWORDS if kw in added]

    if found_critical:
        return "CRÍTICO", found_critical
    if found_important:
        return "IMPORTANTE", found_important
    return "INFORMATIVO", []


# ─── Notificación ─────────────────────────────────────────────────────────────

def _notify(level: str, firm: str, keywords: list, dry_run: bool):
    import subprocess
    msg = f"PropFirm {firm} cambió T&C [{level}] — keywords: {', '.join(keywords) or 'contenido general'}"
    print(f"  [{level}] {msg}")

    notifier = ROOT / "scripts" / "telegram-notifier.py"
    if not notifier.exists() or dry_run:
        return

    tg_level = "CRITICAL" if level == "CRÍTICO" else "WARNING" if level == "IMPORTANTE" else "INFO"
    subprocess.run(
        [_PYTHON, str(notifier), "--level", tg_level, "--message", msg],
        capture_output=True,
    )


# ─── Funciones principales ────────────────────────────────────────────────────

def check_propfirm_changes(dry_run: bool = False, force: bool = False) -> list:
    """Verifica cambios en T&C de todas las prop firms."""
    hashes = _load_hashes()
    log    = _load_log()
    events = []

    for firm, url in PROPFIRM_URLS.items():
        print(f"\nVerificando {firm}...")
        html, err = _fetch_content(url)

        if html is None:
            print(f"  ERROR al descargar {url}: {err}")
            events.append({"firm": firm, "status": "error", "error": err,
                            "timestamp": datetime.now().isoformat()})
            continue

        text     = _extract_text(html)
        new_hash = _sha256(text)
        old_entry = hashes.get(firm, {})
        old_hash  = old_entry.get("hash", "")

        if new_hash == old_hash and not force:
            print(f"  Sin cambios (hash={new_hash[:12]}...)")
            continue

        if old_hash and new_hash != old_hash:
            old_text = old_entry.get("text_sample", "")
            level, keywords = _classify_change(old_text, text)
            event = {
                "firm":      firm,
                "url":       url,
                "level":     level,
                "keywords":  keywords,
                "old_hash":  old_hash,
                "new_hash":  new_hash,
                "timestamp": datetime.now().isoformat(),
                "status":    "changed",
            }
            events.append(event)
            log.append(event)
            _notify(level, firm, keywords, dry_run)
        elif not old_hash:
            print(f"  Primer registro de {firm} (hash={new_hash[:12]}...)")
            events.append({"firm": firm, "status": "first_record",
                            "timestamp": datetime.now().isoformat()})

        if not dry_run:
            hashes[firm] = {
                "hash":        new_hash,
                "last_check":  datetime.now().isoformat(),
                "url":         url,
                "text_sample": text[:500],
            }

    if not dry_run:
        _save_hashes(hashes)
        _save_log(log)

    return events


def show_history(n: int = 20):
    """Muestra el historial de cambios detectados."""
    log = _load_log()
    if not log:
        print("Sin cambios registrados.")
        return
    print(f"\nHistorial de cambios prop firms ({len(log)} total):")
    print("-" * 60)
    for entry in log[-n:]:
        ts    = entry.get("timestamp", "?")[:10]
        firm  = entry.get("firm", "?")
        level = entry.get("level", "?")
        kws   = ", ".join(entry.get("keywords", []))
        print(f"  {ts}  {firm:<15} [{level:<12}]  {kws}")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PropFirm Monitor — TradingLab")
    parser.add_argument("--check",   action="store_true", help="Verificar cambios ahora")
    parser.add_argument("--history", action="store_true", help="Ver historial de cambios")
    parser.add_argument("--force",   action="store_true", help="Forzar actualización de hashes")
    parser.add_argument("--dry-run", action="store_true", help="Simular sin guardar")
    args = parser.parse_args()

    if args.check or args.force:
        events = check_propfirm_changes(dry_run=args.dry_run, force=args.force)
        changed = [e for e in events if e.get("status") == "changed"]
        print(f"\nResumen: {len(changed)} cambios detectados de {len(PROPFIRM_URLS)} firms.")
    elif args.history:
        show_history()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
