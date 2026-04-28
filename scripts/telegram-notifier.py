#!/usr/bin/env python3
"""
telegram-notifier.py — Notificaciones Telegram centralizadas del sistema

Uso:
    python telegram-notifier.py --level INFO --message "Texto"
    python telegram-notifier.py --daily-report metrics.json
    python telegram-notifier.py --challenge strategy.json
    python telegram-notifier.py --dry-run --level WARNING --message "Test"

Config requerida: config/telegram-config.json
    {
        "token": "123456:ABC-DEF...",
        "chat_id": "-100123456789"
    }
"""

import argparse
import io
import json
import sys
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

CONFIG_PATH = Path(__file__).parent.parent / "config" / "telegram-config.json"

EMOJI = {"INFO": "✅", "WARNING": "⚠️", "CRITICAL": "🔴"}


def _load_config():
    if not CONFIG_PATH.exists():
        print(f"ERROR: {CONFIG_PATH} no existe.")
        print("Crea el archivo con este contenido:")
        print(json.dumps({"token": "TU_BOT_TOKEN", "chat_id": "TU_CHAT_ID"}, indent=4))
        sys.exit(1)
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def _send(text, dry_run=False):
    if dry_run:
        print("[DRY-RUN] Mensaje que se enviaría:")
        print(text)
        return True
    import requests
    config = _load_config()
    url = f"https://api.telegram.org/bot{config['token']}/sendMessage"
    resp = requests.post(url, json={"chat_id": config["chat_id"], "text": text}, timeout=10)
    resp.raise_for_status()
    return True


def send_info(message, dry_run=False):
    return _send(f"✅ {message}", dry_run)


def send_warning(message, dry_run=False):
    return _send(f"⚠️ {message}", dry_run)


def send_critical(message, dry_run=False):
    return _send(f"🔴 {message}", dry_run)


def send_challenge_request(strategy_data, dry_run=False):
    d = strategy_data
    text = (
        "🎯 CHALLENGE REQUEST\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"Estrategia : {d.get('name', 'N/A')}\n"
        f"Activo     : {d.get('symbol', 'N/A')}  H1\n"
        f"Build      : {d.get('build', 'N/A')}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"Net Profit : {d.get('net_profit', 'N/A')}%\n"
        f"Max DD     : {d.get('max_dd', 'N/A')}%\n"
        f"Profit F.  : {d.get('profit_factor', 'N/A')}\n"
        f"Win Rate   : {d.get('win_rate', 'N/A')}%\n"
        f"Sharpe     : {d.get('sharpe', 'N/A')}\n"
        f"WFO OOS    : {d.get('wfo_oos', 'N/A')}%\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"Prop Firm  : {d.get('prop_firm', 'N/A')}\n"
        f"Cuenta     : {d.get('account_size', 'N/A')}\n"
        f"Demo       : {d.get('demo_weeks', 'N/A')} semanas ✓\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Acción requerida: inicia el challenge manualmente."
    )
    return _send(text, dry_run)


def send_daily_report(metrics, dry_run=False):
    m = metrics
    date_str = datetime.now().strftime("%Y-%m-%d")
    text = (
        f"📊 REPORTE DIARIO — {date_str}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"Build activo   : {m.get('active_build', 'N/A')}\n"
        f"Pipeline       : {m.get('pipeline_status', 'N/A')}\n"
        f"Estrategias    : {m.get('strategies_count', 0)} en evaluación\n"
        f"En demo        : {m.get('demo_count', 0)}\n"
        f"En challenge   : {m.get('challenge_count', 0)}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"Portfolio DD   : {m.get('portfolio_dd', 'N/A')}%\n"
        f"Profit total   : {m.get('total_profit', 'N/A')}%\n"
        f"Correlación max: {m.get('max_correlation', 'N/A')}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"Próximo hito   : {m.get('next_milestone', 'N/A')}"
    )
    return _send(text, dry_run)


def main():
    parser = argparse.ArgumentParser(description="Telegram Notifier — TradingLab")
    parser.add_argument("--dry-run", action="store_true", help="Imprime sin enviar")
    parser.add_argument("--level", choices=["INFO", "WARNING", "CRITICAL"], help="Nivel de notificación")
    parser.add_argument("--message", help="Texto del mensaje")
    parser.add_argument("--challenge", metavar="JSON_FILE", help="JSON con strategy_data")
    parser.add_argument("--daily-report", metavar="JSON_FILE", help="JSON con métricas")
    args = parser.parse_args()

    if args.challenge:
        data = json.loads(Path(args.challenge).read_text(encoding="utf-8"))
        send_challenge_request(data, dry_run=args.dry_run)
    elif args.daily_report:
        data = json.loads(Path(args.daily_report).read_text(encoding="utf-8"))
        send_daily_report(data, dry_run=args.dry_run)
    elif args.level and args.message:
        fn = {"INFO": send_info, "WARNING": send_warning, "CRITICAL": send_critical}[args.level]
        fn(args.message, dry_run=args.dry_run)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
