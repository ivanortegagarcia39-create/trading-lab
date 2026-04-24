"""
strategy-versioning.py
Gestiona el ciclo de vida completo de cada estrategia con versioning semantico.

Formato de ID:
  [ACTIVO]-[BUILD]-[ID-SQ]-[vN]
  Ejemplo: XAUUSD-B10-1024-v1

Uso:
  python strategy-versioning.py register XAUUSD B10 1024
  python strategy-versioning.py update XAUUSD-B10-1024-v1 --pf 1.52 --dd 4.1
  python strategy-versioning.py new-version XAUUSD-B10-1024-v1 --reason "reoptimizacion ATR"
  python strategy-versioning.py rollback XAUUSD-B10-1024-v2
  python strategy-versioning.py list
  python strategy-versioning.py list --estado activa
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

REGISTRY_FILE = Path("results/strategies-registry.json")


# ─── Registry I/O ────────────────────────────────────────────────────────────

def load_registry() -> dict:
    if REGISTRY_FILE.exists():
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    return {"strategies": {}}


def save_registry(data: dict) -> None:
    REGISTRY_FILE.parent.mkdir(exist_ok=True)
    REGISTRY_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ─── Funciones principales ────────────────────────────────────────────────────

def register_strategy(activo: str, build: str, id_sq: str) -> str:
    """
    Crea nueva entrada en el registry.
    Asigna v1 automaticamente.
    Devuelve el ID completo: ACTIVO-BUILD-IDSQ-v1
    """
    base_id = f"{activo.upper()}-{build.upper()}-{id_sq}"
    full_id = f"{base_id}-v1"

    registry = load_registry()

    if base_id in registry["strategies"]:
        existing = registry["strategies"][base_id]
        active_v = existing["version_activa"]
        print(f"[WARN] Estrategia {base_id} ya existe. Version activa: {active_v}")
        print(f"  Usa 'new-version' para crear una nueva version.")
        return f"{base_id}-{active_v}"

    registry["strategies"][base_id] = {
        "id": base_id,
        "activo": activo.upper(),
        "build": build.upper(),
        "id_sq": id_sq,
        "versiones": {
            "v1": {
                "timestamp": now_iso(),
                "metricas": {},
                "estado": "standby",
                "razon_creacion": "build inicial",
            }
        },
        "version_activa": "v1",
    }

    save_registry(registry)
    print(f"Registrada: {full_id}")
    return full_id


def update_metrics(strategy_full_id: str, metrics: dict) -> None:
    """
    Actualiza las metricas de la version activa de una estrategia.
    strategy_full_id puede ser con o sin version: XAUUSD-B10-1024-v1
    """
    base_id, version = _split_id(strategy_full_id)
    registry = load_registry()

    if base_id not in registry["strategies"]:
        print(f"[ERROR] Estrategia no encontrada: {base_id}")
        sys.exit(1)

    entry = registry["strategies"][base_id]
    if version is None:
        version = entry["version_activa"]

    if version not in entry["versiones"]:
        print(f"[ERROR] Version {version} no encontrada en {base_id}")
        sys.exit(1)

    metrics["fecha_actualizacion"] = now_iso()
    entry["versiones"][version]["metricas"].update(metrics)

    save_registry(registry)
    print(f"Metricas actualizadas: {base_id}-{version}")
    for k, v in metrics.items():
        if k != "fecha_actualizacion":
            print(f"  {k}: {v}")


def create_new_version(strategy_full_id: str, reason: str) -> str:
    """
    Incrementa la version (v1→v2, v2→v3...).
    Copia metricas de la version anterior como baseline.
    Devuelve el nuevo ID completo.
    """
    base_id, _ = _split_id(strategy_full_id)
    registry = load_registry()

    if base_id not in registry["strategies"]:
        print(f"[ERROR] Estrategia no encontrada: {base_id}")
        sys.exit(1)

    entry = registry["strategies"][base_id]
    current_v = entry["version_activa"]
    current_num = int(current_v.lstrip("v"))
    new_v = f"v{current_num + 1}"

    # Copiar metricas de version anterior como baseline
    prev_metrics = entry["versiones"][current_v].get("metricas", {}).copy()
    prev_metrics["baseline_desde"] = current_v

    entry["versiones"][new_v] = {
        "timestamp": now_iso(),
        "metricas": prev_metrics,
        "estado": "standby",
        "razon_creacion": reason,
        "version_anterior": current_v,
    }
    # Marcar version anterior como reemplazada
    entry["versiones"][current_v]["estado"] = "reemplazada"
    entry["version_activa"] = new_v

    save_registry(registry)
    new_full_id = f"{base_id}-{new_v}"
    print(f"Nueva version creada: {base_id}-{current_v} → {new_full_id}")
    print(f"  Razon: {reason}")
    return new_full_id


def rollback(strategy_full_id: str) -> None:
    """
    Vuelve a la version anterior.
    Registra el rollback y notifica con el formato estandar.
    """
    base_id, _ = _split_id(strategy_full_id)
    registry = load_registry()

    if base_id not in registry["strategies"]:
        print(f"[ERROR] Estrategia no encontrada: {base_id}")
        sys.exit(1)

    entry = registry["strategies"][base_id]
    current_v = entry["version_activa"]
    current_data = entry["versiones"][current_v]

    prev_v = current_data.get("version_anterior")
    if prev_v is None:
        print(f"[ERROR] {base_id}-{current_v} no tiene version anterior. No se puede hacer rollback.")
        sys.exit(1)

    if prev_v not in entry["versiones"]:
        print(f"[ERROR] Version anterior {prev_v} no encontrada en el registry.")
        sys.exit(1)

    # Marcar version actual como descartada
    entry["versiones"][current_v]["estado"] = "descartada"
    entry["versiones"][current_v]["rollback_timestamp"] = now_iso()

    # Restaurar version anterior
    entry["versiones"][prev_v]["estado"] = "activa"
    entry["version_activa"] = prev_v

    save_registry(registry)

    msg = f"Rollback: {base_id}-{current_v}→{prev_v}"
    print(msg)

    # Intentar registrar en hash-logger si esta disponible
    try:
        import subprocess
        subprocess.run(
            ["python", "scripts/hash-logger.py", "--event", msg],
            capture_output=True,
        )
    except Exception:
        pass  # hash-logger es opcional


def list_strategies(estado: str | None = None) -> None:
    """
    Lista todas las estrategias del registry.
    Filtro opcional por estado.
    """
    registry = load_registry()
    strategies = registry.get("strategies", {})

    if not strategies:
        print("Registry vacio. Usa 'register' para añadir estrategias.")
        return

    print(f"\n{'='*70}")
    print(f"{'ID':40} {'Version':8} {'Estado':15} {'PF':6}")
    print(f"{'─'*40} {'─'*8} {'─'*15} {'─'*6}")

    count = 0
    for base_id, entry in sorted(strategies.items()):
        active_v = entry["version_activa"]
        version_data = entry["versiones"][active_v]
        current_estado = version_data.get("estado", "?")

        if estado and current_estado != estado:
            continue

        metricas = version_data.get("metricas", {})
        pf_str = f"{metricas['PF']:.2f}" if "PF" in metricas else "—"

        print(f"{base_id+'-'+active_v:40} {active_v:8} {current_estado:15} {pf_str:6}")
        count += 1

    print(f"{'─'*70}")
    filter_msg = f" (estado={estado})" if estado else ""
    print(f"Total: {count} estrategia(s){filter_msg}")


def set_estado(strategy_full_id: str, nuevo_estado: str) -> None:
    """Cambia el estado de la version activa."""
    base_id, version = _split_id(strategy_full_id)
    registry = load_registry()

    if base_id not in registry["strategies"]:
        print(f"[ERROR] Estrategia no encontrada: {base_id}")
        sys.exit(1)

    entry = registry["strategies"][base_id]
    if version is None:
        version = entry["version_activa"]

    entry["versiones"][version]["estado"] = nuevo_estado
    save_registry(registry)
    print(f"Estado actualizado: {base_id}-{version} → {nuevo_estado}")


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _split_id(full_id: str) -> tuple[str, str | None]:
    """
    Separa 'XAUUSD-B10-1024-v1' en ('XAUUSD-B10-1024', 'v1').
    Si no hay version → devuelve (full_id, None).
    """
    parts = full_id.rsplit("-", 1)
    if len(parts) == 2 and parts[1].startswith("v") and parts[1][1:].isdigit():
        return parts[0], parts[1]
    return full_id, None


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Strategy Versioning — TradingLab")
    sub = parser.add_subparsers(dest="command", required=True)

    # register
    p_reg = sub.add_parser("register", help="Registrar nueva estrategia (v1)")
    p_reg.add_argument("activo", help="Activo: XAUUSD, EURUSD...")
    p_reg.add_argument("build",  help="Build: B10, B11...")
    p_reg.add_argument("id_sq",  help="ID de SQ: 1024, 0233...")

    # update
    p_upd = sub.add_parser("update", help="Actualizar metricas de una version")
    p_upd.add_argument("strategy_id", help="ID completo: XAUUSD-B10-1024-v1")
    p_upd.add_argument("--pf",       type=float)
    p_upd.add_argument("--dd",       type=float, dest="DD")
    p_upd.add_argument("--trades",   type=int)
    p_upd.add_argument("--win-rate", type=float, dest="win_rate")
    p_upd.add_argument("--sharpe",   type=float)
    p_upd.add_argument("--estado",   help="activa/standby/challenge/retirada")

    # new-version
    p_nv = sub.add_parser("new-version", help="Crear nueva version de una estrategia")
    p_nv.add_argument("strategy_id", help="ID actual: XAUUSD-B10-1024-v1")
    p_nv.add_argument("--reason", default="reoptimizacion", help="Razon del cambio")

    # rollback
    p_rb = sub.add_parser("rollback", help="Volver a la version anterior")
    p_rb.add_argument("strategy_id", help="ID de la version actual: XAUUSD-B10-1024-v2")

    # list
    p_ls = sub.add_parser("list", help="Listar estrategias del registry")
    p_ls.add_argument("--estado", help="Filtrar por estado")

    # set-estado
    p_se = sub.add_parser("set-estado", help="Cambiar estado de una estrategia")
    p_se.add_argument("strategy_id")
    p_se.add_argument("estado", choices=["activa", "standby", "challenge", "retirada", "recuperacion"])

    args = parser.parse_args()

    if args.command == "register":
        register_strategy(args.activo, args.build, args.id_sq)

    elif args.command == "update":
        metrics = {}
        if args.pf       is not None: metrics["PF"]       = args.pf
        if args.DD       is not None: metrics["DD"]       = args.DD
        if args.trades   is not None: metrics["trades"]   = args.trades
        if args.win_rate is not None: metrics["win_rate"] = args.win_rate
        if args.sharpe   is not None: metrics["sharpe"]   = args.sharpe
        if args.estado   is not None: metrics["estado"]   = args.estado
        if not metrics:
            print("[ERROR] Especifica al menos una metrica (--pf, --dd, --trades...)")
            return 1
        update_metrics(args.strategy_id, metrics)

    elif args.command == "new-version":
        create_new_version(args.strategy_id, args.reason)

    elif args.command == "rollback":
        rollback(args.strategy_id)

    elif args.command == "list":
        list_strategies(getattr(args, "estado", None))

    elif args.command == "set-estado":
        set_estado(args.strategy_id, args.estado)

    return 0


if __name__ == "__main__":
    sys.exit(main())
