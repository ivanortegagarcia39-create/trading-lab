#!/usr/bin/env python3
"""
telegram-listener.py — Polling de comandos Telegram para N8N / TradingLab API.

Lee mensajes nuevos, filtra comandos reconocidos y actualiza el offset.

Comandos aceptados (case-insensitive):
    SI, NO, STATUS, STOP, METRICS, STRATEGIES, PORTFOLIO, BUILD

Uso:
    python scripts/telegram-listener.py --check
    → imprime JSON con el comando encontrado o null

Config: config/telegram-config.json  { "token": "...", "chat_id": "..." }
Offset: config/telegram-offset.json  { "offset": 960307506 }
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT         = Path(__file__).parent.parent
CONFIG_PATH  = ROOT / "config" / "telegram-config.json"
OFFSET_PATH  = ROOT / "config" / "telegram-offset.json"

COMMANDS = {"SI", "NO", "STATUS", "STOP", "METRICS", "STRATEGIES", "PORTFOLIO", "BUILD"}

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
    import requests
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        r = requests.get(url, params={"offset": offset, "timeout": 5, "limit": 10}, timeout=10)
        data = r.json()
        return data.get("result", []) if data.get("ok") else []
    except Exception:
        return []


def _send_telegram(token: str, chat_id: str, text: str) -> None:
    import requests
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception:
        pass


# ── Handlers de comandos ────────────────────────────────────────────────────

def _handle_metrics(token: str, chat_id: str) -> None:
    try:
        lock_path = ROOT / "results" / "pipeline.lock"
        if not lock_path.exists():
            _send_telegram(token, chat_id, "📊 METRICS\nNo hay build activo (pipeline.lock no encontrado).")
            return

        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        build  = lock.get("build", "?")
        activo = lock.get("activo", "?")
        start  = lock.get("timestamp_inicio", "")

        elapsed = ""
        if start:
            try:
                t0 = datetime.fromisoformat(start.replace("Z", "+00:00"))
                delta = datetime.now(timezone.utc) - t0
                h, rem = divmod(int(delta.total_seconds()), 3600)
                m = rem // 60
                elapsed = f"{h}h {m}m"
            except Exception:
                elapsed = start

        sqx_count = 0
        builder_results = ROOT / "Builder" / "Results"
        if builder_results.exists():
            sqx_count = len(list(builder_results.glob("*.sqx")))

        text = (
            "📊 METRICS — Build activo\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"Build      : {build}\n"
            f"Activo     : {activo}\n"
            f"Corriendo  : {elapsed}\n"
            f"Estrategias: {sqx_count} .sqx generadas"
        )
        _send_telegram(token, chat_id, text)
    except Exception:
        _send_telegram(token, chat_id, "Error al obtener datos")


def _handle_strategies(token: str, chat_id: str) -> None:
    try:
        results_path = ROOT / "evaluation-gate-results.json"
        if not results_path.exists():
            _send_telegram(token, chat_id, "📋 STRATEGIES\nSin estrategias aprobadas aún.")
            return

        data = json.loads(results_path.read_text(encoding="utf-8"))
        approved = [s for s in data if s.get("aprobada") or s.get("approved")]

        if not approved:
            _send_telegram(token, chat_id, "📋 STRATEGIES\nSin estrategias aprobadas aún.")
            return

        lines = ["📋 STRATEGIES — Aprobadas\n━━━━━━━━━━━━━━━━━━━━"]
        for s in approved:
            lines.append(
                f"• {s.get('nombre', s.get('name', 'N/A'))}\n"
                f"  PF:{s.get('profit_factor', s.get('pf', '?'))}  "
                f"DD:{s.get('max_dd', s.get('dd', '?'))}%  "
                f"Trades:{s.get('trades', '?')}"
            )
        _send_telegram(token, chat_id, "\n".join(lines))
    except Exception:
        _send_telegram(token, chat_id, "Error al obtener datos")


def _handle_portfolio(token: str, chat_id: str) -> None:
    try:
        registry_path = ROOT / "strategies-registry.json"
        if not registry_path.exists():
            _send_telegram(token, chat_id, "📁 PORTFOLIO\nPortfolio vacío — objetivo 3 estrategias.")
            return

        data = json.loads(registry_path.read_text(encoding="utf-8"))
        strategies = data if isinstance(data, list) else data.get("strategies", [])
        active = [s for s in strategies if s.get("activa") or s.get("active")]

        if not active:
            _send_telegram(token, chat_id, "📁 PORTFOLIO\nPortfolio vacío — objetivo 3 estrategias.")
            return

        combined_dd = data.get("dd_combinado", data.get("combined_dd", "N/A")) if isinstance(data, dict) else "N/A"
        lines = [f"📁 PORTFOLIO — {len(active)} estrategias activas\n━━━━━━━━━━━━━━━━━━━━"]
        for s in active:
            lines.append(f"• {s.get('nombre', s.get('name', 'N/A'))}  [{s.get('activo', s.get('symbol', '?'))}]")
        lines.append(f"━━━━━━━━━━━━━━━━━━━━\nDD combinado: {combined_dd}%")
        _send_telegram(token, chat_id, "\n".join(lines))
    except Exception:
        _send_telegram(token, chat_id, "Error al obtener datos")


def _handle_build(token: str, chat_id: str) -> None:
    try:
        lock_path = ROOT / "results" / "pipeline.lock"
        if not lock_path.exists():
            _send_telegram(token, chat_id, "🔨 BUILD\nNo hay build activo (pipeline.lock no encontrado).")
            return

        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        text = (
            "🔨 BUILD — Info actual\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"Build      : {lock.get('build', '?')}\n"
            f"Activo     : {lock.get('activo', '?')}\n"
            f"Spread     : {lock.get('spread', '?')}\n"
            f"SL         : {lock.get('sl', '?')}\n"
            f"PT         : {lock.get('pt', '?')}\n"
            f"IS period  : {lock.get('is_period', '?')}\n"
            f"Inicio     : {lock.get('timestamp_inicio', '?')}"
        )
        _send_telegram(token, chat_id, text)
    except Exception:
        _send_telegram(token, chat_id, "Error al obtener datos")


COMMAND_HANDLERS = {
    "METRICS":    _handle_metrics,
    "STRATEGIES": _handle_strategies,
    "PORTFOLIO":  _handle_portfolio,
    "BUILD":      _handle_build,
}


def check_command() -> dict:
    """
    Obtiene updates desde el offset guardado, busca el primer comando
    reconocido y actualiza el offset.
    Devuelve: {"command": str|null, "update_id": int|null}
    """
    config = _load_config()
    token   = config.get("token", "")
    chat_id = config.get("chat_id", "")
    offset  = _load_offset()

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

        word = text.lstrip("/").split()[0] if text else ""
        if word in COMMANDS and found_command is None:
            found_command = word
            found_id      = uid

    if last_update_id is not None:
        _save_offset(last_update_id + 1)

    # Ejecutar handler si el comando lo requiere
    if found_command and found_command in COMMAND_HANDLERS:
        COMMAND_HANDLERS[found_command](token, chat_id)

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
    return 0


if __name__ == "__main__":
    sys.exit(main())
