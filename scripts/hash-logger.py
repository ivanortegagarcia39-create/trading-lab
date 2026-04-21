"""
hash-logger.py
Genera un audit trail inmutable con hashes SHA-256 encadenados.
Cada entrada incluye el hash de la entrada anterior — si alguien
modifica una entrada pasada, todos los hashes posteriores invalidan.

Uso:
    from scripts.hash_logger import log_decision, verify_chain

    log_decision(
        decision="DESCARTAR",
        criterio="PF OOS < 1.2",
        resultado="PF OOS = 1.08 — estrategia ID-4521"
    )

    ok, broken_at = verify_chain()

Archivo de salida: results/audit-trail.log
Formato de cada linea:
    TIMESTAMP|DECISION|CRITERIO|RESULTADO|HASH_PREV|HASH_ACTUAL
"""

import hashlib
import os
import sys
from datetime import datetime, timezone

AUDIT_LOG = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "results",
    "audit-trail.log",
)

GENESIS_HASH = "0" * 64  # hash inicial de la cadena (bloque genesis)


def _read_last_hash() -> str:
    """Lee el hash de la ultima entrada del audit trail."""
    if not os.path.exists(AUDIT_LOG):
        return GENESIS_HASH
    with open(AUDIT_LOG, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines:
        return GENESIS_HASH
    last = lines[-1]
    parts = last.split("|")
    if len(parts) < 6:
        return GENESIS_HASH
    return parts[5]  # HASH_ACTUAL es el campo 6


def _compute_hash(timestamp: str, decision: str, criterio: str,
                  resultado: str, hash_prev: str) -> str:
    """Calcula SHA-256 de los campos concatenados."""
    content = f"{timestamp}|{decision}|{criterio}|{resultado}|{hash_prev}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def log_decision(decision: str, criterio: str, resultado: str) -> str:
    """
    Registra una decision en el audit trail inmutable.

    Args:
        decision:  Tipo de decision (PASA, DESCARTAR, ESPERA,
                   CHALLENGE-AUTORIZADO, FORWARD-TEST-OK, etc.)
        criterio:  Criterio numerico o regla que motiva la decision
        resultado: Descripcion del resultado observado con metricas

    Returns:
        El hash SHA-256 de la nueva entrada.
    """
    # Sanitizar campos para evitar inyeccion de separador
    decision = decision.replace("|", "/")
    criterio = criterio.replace("|", "/")
    resultado = resultado.replace("|", "/")

    os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    hash_prev = _read_last_hash()
    hash_actual = _compute_hash(timestamp, decision, criterio, resultado, hash_prev)

    line = f"{timestamp}|{decision}|{criterio}|{resultado}|{hash_prev}|{hash_actual}\n"

    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(line)

    return hash_actual


def verify_chain() -> tuple[bool, int | None]:
    """
    Verifica la integridad de toda la cadena de audit trail.

    Returns:
        (True, None)    si la cadena esta intacta
        (False, linea)  si la cadena esta rota — linea donde falla (1-indexed)
    """
    if not os.path.exists(AUDIT_LOG):
        return True, None

    with open(AUDIT_LOG, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        return True, None

    prev_hash = GENESIS_HASH

    for i, line in enumerate(lines, start=1):
        parts = line.split("|")
        if len(parts) != 6:
            print(f"ERROR: linea {i} tiene formato incorrecto: {line}")
            return False, i

        timestamp, decision, criterio, resultado, hash_prev_stored, hash_actual_stored = parts

        # Verificar que el hash_prev coincide con el hash anterior en la cadena
        if hash_prev_stored != prev_hash:
            print(f"ERROR: cadena rota en linea {i}")
            print(f"  hash_prev almacenado: {hash_prev_stored}")
            print(f"  hash_prev esperado:   {prev_hash}")
            return False, i

        # Recalcular el hash de esta entrada
        expected_hash = _compute_hash(
            timestamp, decision, criterio, resultado, hash_prev_stored
        )
        if expected_hash != hash_actual_stored:
            print(f"ERROR: hash incorrecto en linea {i} — posible manipulacion")
            print(f"  hash almacenado:  {hash_actual_stored}")
            print(f"  hash recalculado: {expected_hash}")
            return False, i

        prev_hash = hash_actual_stored

    return True, None


def print_trail(last_n: int = 20) -> None:
    """Imprime las ultimas N entradas del audit trail en formato legible."""
    if not os.path.exists(AUDIT_LOG):
        print("Audit trail vacio.")
        return

    with open(AUDIT_LOG, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        print("Audit trail vacio.")
        return

    print(f"Audit trail — ultimas {min(last_n, len(lines))} entradas:")
    print("-" * 80)
    for line in lines[-last_n:]:
        parts = line.split("|")
        if len(parts) == 6:
            ts, dec, crit, res, _, h = parts
            print(f"[{ts}] {dec}")
            print(f"  Criterio: {crit}")
            print(f"  Resultado: {res}")
            print(f"  Hash: {h[:16]}...")
            print()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Audit trail inmutable para decisiones del pipeline TradingLab."
    )
    subparsers = parser.add_subparsers(dest="command")

    # Comando: log
    log_p = subparsers.add_parser("log", help="Registrar una decision")
    log_p.add_argument("--decision", required=True)
    log_p.add_argument("--criterio", required=True)
    log_p.add_argument("--resultado", required=True)

    # Comando: verify
    subparsers.add_parser("verify", help="Verificar integridad de la cadena")

    # Comando: print
    print_p = subparsers.add_parser("print", help="Mostrar entradas recientes")
    print_p.add_argument("--last", type=int, default=20)

    args = parser.parse_args()

    if args.command == "log":
        h = log_decision(args.decision, args.criterio, args.resultado)
        print(f"Entrada registrada. Hash: {h[:16]}...")

    elif args.command == "verify":
        ok, broken_at = verify_chain()
        if ok:
            print("PASS — cadena de audit trail integra.")
            sys.exit(0)
        else:
            print(f"FAIL — cadena rota en linea {broken_at}. ALERTA DE MANIPULACION.")
            sys.exit(1)

    elif args.command == "print":
        print_trail(args.last)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
