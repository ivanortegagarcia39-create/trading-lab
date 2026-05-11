#!/usr/bin/env python3
"""
daily-loss-guard.py — Proteccion FTMO de Daily Loss Limit en tiempo real

Lee el balance/equity de MT5 via archivo de estado y aplica los limites
dinamicos de FTMO recalculados cada medianoche hora Praga.

Uso:
    python scripts/daily-loss-guard.py --capital 25000 --check
    python scripts/daily-loss-guard.py --capital 25000 --check --dry-run

Requiere: results/mt5-state.json (escrito por el EA de MT5)
    {
        "balance": 25100.50,
        "equity": 24980.25,
        "open_trades": 2,
        "timestamp": "2026-05-11T10:30:00"
    }

Constantes FTMO:
    Daily Loss Limit : 5% del capital inicial
    Margen operativo : 3% (alerta WARNING)
    Zona critica     : 4.5% (cierre automatico + CRITICAL)
    Timezone         : Europe/Prague
"""

import argparse
import io
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    import pytz
except ImportError:
    print("ERROR: pytz no instalado. Ejecuta: pip install pytz")
    sys.exit(1)

ROOT          = Path(__file__).parent.parent
MT5_STATE     = ROOT / "results" / "mt5-state.json"
GUARD_STATE   = ROOT / "results" / "daily-loss-guard-state.json"
CLOSE_TRIGGER = ROOT / "results" / "close-all-trigger.json"

PRAGUE_TZ    = pytz.timezone("Europe/Prague")
DD_LIMIT_PCT = 0.05   # 5%  — FTMO Daily Loss Limit
DD_WARNING   = 0.03   # 3%  — margen operativo: alerta
DD_CRITICAL  = 0.045  # 4.5% — zona critica: cierre automatico


# ─── I/O ──────────────────────────────────────────────────────────────────────

def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_mt5_state() -> dict:
    state = _load_json(MT5_STATE)
    if not state:
        print(f"ERROR: {MT5_STATE} no existe o esta vacio.")
        print("El EA de MT5 debe escribir este archivo con balance, equity, open_trades, timestamp.")
        sys.exit(1)
    required = {"balance", "equity", "timestamp"}
    missing = required - state.keys()
    if missing:
        print(f"ERROR: mt5-state.json no tiene campos: {missing}")
        sys.exit(1)
    return state


# ─── Logica de estado diario ──────────────────────────────────────────────────

def _prague_today() -> str:
    return datetime.now(PRAGUE_TZ).strftime("%Y-%m-%d")


def _get_guard_state(initial_capital: float) -> dict:
    """Carga o inicializa el estado del guard."""
    state = _load_json(GUARD_STATE)
    today = _prague_today()

    if not state or state.get("prev_day_date") != today:
        # Nuevo dia Praga: actualizar balance de medianoche
        mt5 = _load_mt5_state()
        prev_balance = state.get("balance_at_midnight", initial_capital)

        # Si es el primer arranque del dia, el balance de medianoche es el balance actual
        new_state = {
            "initial_capital":    initial_capital,
            "prev_day_date":      today,
            "balance_at_midnight": prev_balance if state else mt5["balance"],
            "daily_low_equity":   mt5["equity"],
            "close_triggered":    False,
        }
        _save_json(GUARD_STATE, new_state)
        return new_state

    # Mismo dia: actualizar solo si este capital inicial cambio
    if state.get("initial_capital") != initial_capital:
        state["initial_capital"] = initial_capital
        _save_json(GUARD_STATE, state)

    return state


def _update_daily_low(guard: dict, equity: float):
    if equity < guard.get("daily_low_equity", equity):
        guard["daily_low_equity"] = equity
        _save_json(GUARD_STATE, guard)


# ─── Calculo DD diario ────────────────────────────────────────────────────────

def calculate_daily_loss(balance_midnight: float, current_equity: float, initial_capital: float) -> dict:
    """
    FTMO Daily Loss Limit dinamico:
        limite = balance_medianoche - 5% del capital_inicial
        (pero nunca puede ir por encima del balance de medianoche)
    """
    dd_limit_usd   = initial_capital * DD_LIMIT_PCT
    limit_equity   = balance_midnight - dd_limit_usd
    current_loss   = balance_midnight - current_equity
    current_pct    = current_loss / balance_midnight if balance_midnight else 0.0

    return {
        "balance_midnight": round(balance_midnight, 2),
        "current_equity":   round(current_equity,   2),
        "loss_usd":         round(current_loss,     2),
        "loss_pct":         round(current_pct * 100, 4),
        "limit_usd":        round(dd_limit_usd,     2),
        "limit_equity":     round(limit_equity,     2),
        "warning":          current_pct >= DD_WARNING,
        "critical":         current_pct >= DD_CRITICAL,
        "ok":               current_pct < DD_WARNING,
    }


# ─── Notificaciones ───────────────────────────────────────────────────────────

def _send_alert(level: str, message: str, dry_run: bool = False):
    notifier = ROOT / "scripts" / "telegram-notifier.py"
    if dry_run:
        print(f"[DRY-RUN] [{level}] {message}")
        return
    if not notifier.exists():
        print(f"[{level}] {message}")
        return
    subprocess.run(
        [sys.executable, str(notifier), "--level", level, "--message", message],
        check=False, capture_output=True,
    )


def _build_warning_msg(dd: dict, capital: float) -> str:
    return (
        f"FTMO Daily Loss ALERTA\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Capital inicial : ${capital:,.2f}\n"
        f"Balance medianoche: ${dd['balance_midnight']:,.2f}\n"
        f"Equity actual   : ${dd['current_equity']:,.2f}\n"
        f"Perdida del dia : ${dd['loss_usd']:,.2f} ({dd['loss_pct']:.2f}%)\n"
        f"Limite diario   : ${dd['limit_usd']:,.2f} (5% = ${dd['limit_equity']:,.2f})\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Nivel: MARGEN OPERATIVO (>3%) — Supervisar!"
    )


def _build_critical_msg(dd: dict, capital: float) -> str:
    return (
        f"FTMO Daily Loss CRITICO — CERRANDO TRADES\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Capital inicial : ${capital:,.2f}\n"
        f"Balance medianoche: ${dd['balance_midnight']:,.2f}\n"
        f"Equity actual   : ${dd['current_equity']:,.2f}\n"
        f"Perdida del dia : ${dd['loss_usd']:,.2f} ({dd['loss_pct']:.2f}%)\n"
        f"Limite diario   : ${dd['limit_usd']:,.2f} (5% = ${dd['limit_equity']:,.2f})\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Nivel: ZONA CRITICA (>4.5%) — Cierre automatico activado!"
    )


# ─── Cierre de trades ─────────────────────────────────────────────────────────

def trigger_close_all(dd: dict, dry_run: bool = False):
    """
    Escribe el archivo de trigger que el EA de MT5 debe leer para cerrar todos los trades.
    El EA debe monitorear results/close-all-trigger.json y actuar cuando trigger=true.
    """
    payload = {
        "trigger":    True,
        "reason":     f"FTMO Daily Loss {dd['loss_pct']:.2f}% supera zona critica 4.5%",
        "loss_usd":   dd["loss_usd"],
        "loss_pct":   dd["loss_pct"],
        "timestamp":  datetime.now(PRAGUE_TZ).isoformat(),
    }
    if dry_run:
        print(f"[DRY-RUN] Trigger close-all: {payload}")
        return
    _save_json(CLOSE_TRIGGER, payload)
    print(f"  TRIGGER escrito: {CLOSE_TRIGGER}")


# ─── Check principal ──────────────────────────────────────────────────────────

def run_check(initial_capital: float, dry_run: bool = False):
    now_prague = datetime.now(PRAGUE_TZ).strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{now_prague} Prague] Daily Loss Guard — capital ${initial_capital:,.2f}")

    mt5    = _load_mt5_state()
    guard  = _get_guard_state(initial_capital)
    equity = mt5["equity"]

    _update_daily_low(guard, equity)

    balance_midnight = guard["balance_at_midnight"]
    dd = calculate_daily_loss(balance_midnight, equity, initial_capital)

    print(f"  Balance medianoche : ${dd['balance_midnight']:,.2f}")
    print(f"  Equity actual      : ${dd['current_equity']:,.2f}")
    print(f"  Perdida del dia    : ${dd['loss_usd']:,.2f} ({dd['loss_pct']:.2f}%)")
    print(f"  Limite FTMO        : ${dd['limit_usd']:,.2f} (equity minima ${dd['limit_equity']:,.2f})")

    if dd["critical"]:
        print("  ESTADO: ZONA CRITICA — cierre automatico")
        if not guard.get("close_triggered"):
            trigger_close_all(dd, dry_run)
            _send_alert("CRITICAL", _build_critical_msg(dd, initial_capital), dry_run)
            guard["close_triggered"] = True
            _save_json(GUARD_STATE, guard)
        else:
            print("  (cierre ya disparado hoy — no duplicar alerta)")

    elif dd["warning"]:
        print("  ESTADO: MARGEN OPERATIVO — alerta enviada")
        _send_alert("WARNING", _build_warning_msg(dd, initial_capital), dry_run)

    else:
        pct_remaining = (DD_LIMIT_PCT - dd["loss_pct"] / 100) * 100
        print(f"  ESTADO: OK — margen restante {pct_remaining * initial_capital / 100:.2f} USD")

    return dd


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Daily Loss Guard FTMO — TradingLab")
    parser.add_argument("--capital", type=float, required=True,
                        help="Capital inicial del challenge (ej: 25000)")
    parser.add_argument("--check",   action="store_true",
                        help="Ejecutar una verificacion ahora (llamar cada 5 min via scheduler)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simular sin enviar alertas ni escribir trigger")
    parser.add_argument("--status",  action="store_true",
                        help="Mostrar estado actual del guard sin verificar MT5")
    args = parser.parse_args()

    if args.status:
        state = _load_json(GUARD_STATE)
        if not state:
            print("Sin estado guardado. Ejecuta --check primero.")
        else:
            print(json.dumps(state, indent=2, ensure_ascii=False))
        return

    if args.check:
        run_check(args.capital, dry_run=args.dry_run)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
