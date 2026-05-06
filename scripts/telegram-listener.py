#!/usr/bin/env python3
"""
telegram-listener.py — Polling de comandos Telegram para N8N / TradingLab API.

Lee mensajes nuevos, filtra comandos reconocidos y actualiza el offset.

Comandos aceptados (case-insensitive):
    SI, NO, STATUS, STOP

Uso:
    python scripts/telegram-listener.py --check
    → imprime JSON con el comando encontrado o null

Config: config/telegram-config.json  { "token": "...", "chat_id": "..." }
Offset: config/telegram-offset.json  { "offset": 960307506 }
"""

import argparse
import json
import sys
from pathlib import Path

ROOT         = Path(__file__).parent.parent
CONFIG_PATH  = ROOT / "config" / "telegram-config.json"
OFFSET_PATH  = ROOT / "config" / "telegram-offset.json"

COMMANDS = {"SI", "NO", "STATUS", "STOP"}

# Offset inicial conocido (último update_id visto + 1)
OFFSET_INITIAL = 960307506


def _load_config() -> dict:
    if not CONFIG_PATH.exists():
        print(json.dumps({"error": f"Config no encontrada: {CONFIG_PATH}"}))
        sys.exit(1)
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def _load_offset() -> int:
    if OFFSET_PATH.exists():
        try:
            return json.loads(OFFSET_PATH.read_text(encoding="utf-8")).get("offset", OFFSET_INITIAL)
        except Exception:
            pass
    return OFFSET_INITIAL


def _save_offset(offset: int) -> None:
    OFFSET_PATH.write_text(json.dumps({"offset": offset}, indent=2), encoding="utf-8")


def _get_updates(token: str, offset: int) -> list:
    import urllib.request
    import urllib.error
    url = f"https://api.telegram.org/bot{token}/getUpdates?offset={offset}&timeout=5&limit=10"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
            return data.get("result", []) if data.get("ok") else []
    except (urllib.error.URLError, OSError):
        return []


def check_command() -> dict:
    """
    Obtiene updates desde el offset guardado, busca el primer comando
    reconocido y actualiza el offset.
    Devuelve: {"command": "SI"|"NO"|"STATUS"|"STOP"|null, "update_id": int|null}
    """
    config = _load_config()
    token  = config.get("token", "")
    offset = _load_offset()

    updates = _get_updates(token, offset)

    found_command  = None
    found_id       = None
    last_update_id = None

    for upd in updates:
        uid  = upd.get("update_id", 0)
        last_update_id = uid

        text = (
            upd.get("message", {}).get("text")
            or upd.get("channel_post", {}).get("text")
            or ""
        ).strip().upper()

        # Buscar primer comando reconocido (puede venir con / o sin /)
        word = text.lstrip("/").split()[0] if text else ""
        if word in COMMANDS and found_command is None:
            found_command = word
            found_id      = uid

    # Actualizar offset al siguiente del último procesado
    if last_update_id is not None:
        _save_offset(last_update_id + 1)

    return {
        "command":   found_command,
        "update_id": found_id,
        "processed": len(updates),
        "new_offset": (last_update_id + 1) if last_update_id is not None else offset,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Telegram Listener — TradingLab")
    parser.add_argument("--check", action="store_true",
                        help="Lee updates y devuelve el comando encontrado como JSON")
    args = parser.parse_args()

    if not args.check:
        parser.print_help()
        return 1

    result = check_command()
    print(json.dumps(result))
    return 0 if result["command"] is not None else 0


if __name__ == "__main__":
    sys.exit(main())
