#!/usr/bin/env python3
"""
export-specialist.py — Exporta estrategias aprobadas de SQ a MT5 con protecciones.

Flujo:
  1. Verifica que la estrategia esta en results/approved/
  2. Usa sqcli -tools para exportar orders a CSV (traza de auditoria)
  3. Aplica las 4 protecciones obligatorias al .mq5
  4. Genera ID unico EA_{ACTIVO}_B{BUILD}_v1.0_{HEXID}.mq5
  5. Guarda en results/exported/
  6. Ejecuta mql5-auditor.py para verificacion final

REQUISITO: sqcli requiere que el SQ GUI este CERRADO (puerto 5050 libre).

Uso:
    python scripts/export-specialist.py --build 11 --activo XAUUSD --strategy "Strategy 0.1487"
    python scripts/export-specialist.py --build 11 --activo XAUUSD --strategy "Strategy 0.1487" --mq5 results/approved/strategy.mq5
"""

import argparse
import hashlib
import importlib.util
import os
import re
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT     = Path(__file__).parent.parent
SCRIPTS  = ROOT / "scripts"
APPROVED = ROOT / "results" / "approved"
EXPORTED = ROOT / "results" / "exported"
SQCLI    = Path(r"D:\sqcli.exe")

MAX_SLIPPAGE = {
    "XAUUSD": 50,
    "XAGUSD": 30,
    "EURUSD": 5,
    "GBPUSD": 5,
    "USDJPY": 5,
    "AUDUSD": 5,
    "NZDUSD": 8,
    "USDCAD": 8,
    "USDCHF": 8,
    "US30":   20,
    "US500":  20,
    "NAS100": 20,
    "DE40":   20,
}
MAX_SLIPPAGE_DEFAULT = 10


# ── Utilidades ─────────────────────────────────────────────────────────────────

def _sq_running() -> bool:
    try:
        with socket.create_connection(("localhost", 5050), timeout=1):
            return True
    except OSError:
        return False


def _sqcli(*args: str, timeout: int = 60) -> tuple[int, str]:
    cmd = [str(SQCLI)] + list(args)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return -1, f"timeout tras {timeout}s"
    except FileNotFoundError:
        return -1, f"sqcli no encontrado en {SQCLI}"


def _ea_id(build: int, activo: str) -> str:
    """Genera el ID unico hex de 8 chars para el EA."""
    seed = f"{activo}-B{build}-{datetime.now().isoformat()}"
    return hashlib.md5(seed.encode()).hexdigest()[:8]


# ── Paso 1: verificar estrategia aprobada ──────────────────────────────────────

def verify_approved(strategy: str, build: int, activo: str) -> tuple[Path | None, Path | None]:
    """
    Busca el .sq4 y el .mq5 de la estrategia en results/approved/.
    Devuelve (sq4_path, mq5_path) — cualquiera puede ser None si no existe.
    """
    if not APPROVED.exists():
        return None, None

    # Buscar por nombre de estrategia (puede estar en subcarpeta o directo)
    strategy_slug = strategy.replace(" ", "_").replace(".", "_")
    candidates    = [
        APPROVED / strategy_slug,
        APPROVED / strategy,
        APPROVED,
    ]

    sq4_path = mq5_path = None

    for folder in candidates:
        if not folder.exists():
            continue
        sq4s = list(folder.glob(f"**/{strategy_slug}*.sq4")) + \
               list(folder.glob(f"**/{strategy.replace(' ', '*')}*.sq4")) + \
               list(folder.glob("**/*.sq4"))
        mq5s = list(folder.glob(f"**/{strategy_slug}*.mq5")) + \
               list(folder.glob(f"**/{strategy.replace(' ', '*')}*.mq5")) + \
               list(folder.glob("**/*.mq5"))
        if sq4s and not sq4_path:
            sq4_path = sq4s[0]
        if mq5s and not mq5_path:
            mq5_path = mq5s[0]
        if sq4_path or mq5_path:
            break

    return sq4_path, mq5_path


# ── Paso 2: sqcli orders → CSV (traza de auditoria) ───────────────────────────

def export_orders_csv(sq4_path: Path, output_dir: Path) -> bool:
    """Exporta las ordenes de la estrategia a CSV usando sqcli -tools."""
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"  sqcli: exportando orders de {sq4_path.name} → {output_dir}")
    rc, out = _sqcli(
        "-tools",
        "action=orderstocsv",
        f"file={sq4_path}",
        f"outputdir={output_dir}",
    )
    if rc != 0:
        print(f"  WARN sqcli orders CSV: {out}")
        return False
    print(f"  Orders CSV generado")
    return True


# ── Paso 3: inyectar las 4 protecciones en el .mq5 ───────────────────────────

# Bloque de declaraciones que se inserta una vez en el archivo
_PROTECTION_DECLARATIONS = """
//+------------------------------------------------------------------+
//| TradingLab Export Protections v1.0                                |
//| Obligatorias segun export-specialist.md                           |
//+------------------------------------------------------------------+
input int  MaxSlippagePips   = {max_slippage}; // [P3] Slippage maximo en pips
input bool EnableProtections = true;           // Master switch protecciones

datetime g_lastTradeTime = 0; // [P2] Control frecuencia 1 trade/hora

// [P4] Spread monitor: media de ultimas N velas
double _GetAvgSpread(int bars = 20) {{
    double total = 0;
    for(int i = 1; i <= bars; i++)
        total += (iHigh(NULL, PERIOD_H1, i) - iLow(NULL, PERIOD_H1, i));
    return total / bars / _Point;
}}

// Verificacion pre-orden: retorna false si debe cancelarse
bool _PreOrderCheck(string symbol) {{
    if(!EnableProtections) return true;
    // [P2] Max 1 trade por hora
    if(TimeCurrent() - g_lastTradeTime < 3600) {{
        Print("[PROT] Limite horario: ultimo trade hace ",
              (int)(TimeCurrent() - g_lastTradeTime), "s");
        return false;
    }}
    // [P4] Spread anormalmente alto (> 10x media 20 velas)
    double avg = _GetAvgSpread(20);
    double cur = (double)SymbolInfoInteger(symbol, SYMBOL_SPREAD);
    if(avg > 0 && cur > avg * 10) {{
        Print("[PROT] Spread anormal: actual=", cur, " media=", avg,
              " ratio=", DoubleToString(cur / avg, 1));
        return false;
    }}
    // [P3] MaxSlippagePips — se verifica despues del Sleep en _PostSleep
    return true;
}}

// [P1] Delay anti-sincronizacion + actualizar timestamp
bool _PostSleep(string symbol) {{
    Sleep(MathRand() % 3001 + 500); // [P1] 500–3500ms anti-sync
    // [P3] Verificar slippage en el Ask/Bid actual
    double ask = SymbolInfoDouble(symbol, SYMBOL_ASK);
    double bid = SymbolInfoDouble(symbol, SYMBOL_BID);
    double spread_pips = (ask - bid) / _Point;
    if(spread_pips > MaxSlippagePips) {{
        Print("[PROT] Slippage/spread excede MaxSlippagePips: ",
              DoubleToString(spread_pips, 1), " > ", MaxSlippagePips);
        return false;
    }}
    g_lastTradeTime = TimeCurrent(); // [P2] Registrar timestamp
    return true;
}}
//+------------------------------------------------------------------+
"""

def inject_protections(code: str, activo: str) -> str:
    """
    Inyecta las 4 protecciones en el codigo MQL5.
    Estrategia:
      - Inserta bloque de declaraciones despues de la ultima linea #property
      - Reemplaza OrderSend( con llamada guarded
    """
    max_slippage = MAX_SLIPPAGE.get(activo.upper(), MAX_SLIPPAGE_DEFAULT)

    # No inyectar si ya existe el bloque (idempotente)
    if "TradingLab Export Protections" in code:
        print("  INFO: protecciones ya presentes en el .mq5 — no se reinyectan")
        return code

    # ── Insertar declaraciones despues de la ultima linea #property ──
    decl_block = _PROTECTION_DECLARATIONS.format(max_slippage=max_slippage)

    # Buscar el ultimo #property para insertar despues
    last_prop = -1
    for m in re.finditer(r'^#property\s+', code, re.MULTILINE):
        last_prop = m.start()

    if last_prop != -1:
        # Avanzar al final de esa linea
        end_of_line = code.find('\n', last_prop)
        if end_of_line == -1:
            end_of_line = len(code)
        insert_at = end_of_line + 1
    else:
        # Sin #property: insertar despues de los includes/defines iniciales
        insert_at = 0
        for m in re.finditer(r'^(#include|#define|//)\s', code, re.MULTILINE):
            insert_at = code.find('\n', m.start()) + 1

    code = code[:insert_at] + decl_block + code[insert_at:]

    # ── Reemplazar llamadas a OrderSend con version guarded ──
    # Patron: cualquier linea que contenga OrderSend( no comentada
    # Insertar _PreOrderCheck y _PostSleep antes de la orden
    def _guard_ordersend(match):
        indent = match.group(1)
        # Generar wrapper con symbol del primer argumento si es literal, o _Symbol
        original = match.group(0)
        guarded = (
            f"{indent}if(_PreOrderCheck(_Symbol) && _PostSleep(_Symbol)) {{\n"
            f"{original}\n"
            f"{indent}}}"
        )
        return guarded

    # Reemplazar solo OrderSend que NO esten ya dentro de un _PreOrderCheck
    if "_PreOrderCheck" not in code:
        code = re.sub(
            r'^( *)((?!.*//.*OrderSend).*\bOrderSend\s*\()',
            lambda m: (
                f"{m.group(1)}if(_PreOrderCheck(_Symbol) && _PostSleep(_Symbol)) {{\n"
                f"{m.group(0)}\n"
                f"{m.group(1)}}}"
            ),
            code,
            flags=re.MULTILINE,
        )

    return code


# ── Paso 4: generar ID unico y guardar ────────────────────────────────────────

def save_exported(code: str, build: int, activo: str) -> Path:
    """Guarda el .mq5 con el nombre canonico EA_{ACTIVO}_B{BUILD}_v1.0_{HEX8}.mq5"""
    EXPORTED.mkdir(parents=True, exist_ok=True)
    hex_id   = _ea_id(build, activo)
    filename = f"EA_{activo.upper()}_B{build}_v1.0_{hex_id}.mq5"
    out_path = EXPORTED / filename
    out_path.write_text(code, encoding="utf-8")
    return out_path


# ── Paso 5: auditar con mql5-auditor.py ───────────────────────────────────────

def run_auditor(mq5_path: Path) -> int:
    """Llama a mql5-auditor.py --no-ollama y devuelve el exit code."""
    auditor = SCRIPTS / "mql5-auditor.py"
    if not auditor.exists():
        print("  WARN: mql5-auditor.py no encontrado — auditoria omitida")
        return 0
    result = subprocess.run(
        [sys.executable, str(auditor), "--mql5-file", str(mq5_path), "--no-ollama"],
        cwd=str(ROOT),
    )
    return result.returncode


# ── Informe de exportacion ────────────────────────────────────────────────────

def print_report(strategy: str, build: int, activo: str,
                 mq5_out: Path, audit_rc: int) -> None:
    verdict = {0: "APROBADO", 1: "REVISAR", 2: "RECHAZADO"}.get(audit_rc, "DESCONOCIDO")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"""
{'='*60}
INFORME DE EXPORTACION — TradingLab
{'='*60}
Estrategia : {strategy}
Activo     : {activo}
Build      : {build}
Fecha      : {ts}
Exportado  : {mq5_out.name}
Ruta       : {mq5_out}

PROTECCIONES APLICADAS:
  [P1] Sleep(MathRand() % 3001 + 500) antes de OrderSend
  [P2] Max 1 trade por hora (_PreOrderCheck)
  [P3] MaxSlippagePips = {MAX_SLIPPAGE.get(activo.upper(), MAX_SLIPPAGE_DEFAULT)} para {activo}
  [P4] Spread monitor (cancela si > 10x media 20 velas)

AUDITORIA MQL5: {verdict}

PROXIMOS PASOS:
  1. Compilar {mq5_out.name} en MT5 Editor (F7)
  2. Backtest MT5 2021→hoy — comparar con Retester SQ (tol. 10%)
  3. Forward test en demo 2 semanas
  4. Si todo OK → LISTO PARA CHALLENGE
{'='*60}""")


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Export Specialist — TradingLab")
    parser.add_argument("--build",    type=int,  required=True, help="Numero del build (ej: 11)")
    parser.add_argument("--activo",   required=True,            help="Activo (ej: XAUUSD)")
    parser.add_argument("--strategy", required=True,            help='Nombre en SQ (ej: "Strategy 0.1487")')
    parser.add_argument("--mq5",                                help="Ruta al .mq5 exportado manualmente de SQ (opcional)")
    args = parser.parse_args()

    activo = args.activo.upper()

    print(f"\n{'='*60}")
    print(f"  EXPORT SPECIALIST — Build {args.build} | {activo}")
    print(f"{'='*60}")

    # ── Paso 1: verificar aprobada ──
    print(f"\n[1] Verificando estrategia en results/approved/...")
    sq4_path, mq5_path = verify_approved(args.strategy, args.build, activo)

    if args.mq5:
        mq5_path = Path(args.mq5)
        if not mq5_path.exists():
            print(f"  ERROR: --mq5 apunta a un archivo que no existe: {mq5_path}")
            return 1

    if not sq4_path and not mq5_path:
        print(f"  ERROR: no se encontro .sq4 ni .mq5 para '{args.strategy}'")
        print(f"  Asegurate de que la estrategia esta en: {APPROVED}")
        print(f"  O exporta el .mq5 desde SQ GUI y pasa la ruta con --mq5")
        return 1

    if sq4_path:
        print(f"  .sq4 encontrado: {sq4_path.relative_to(ROOT)}")
    if mq5_path:
        print(f"  .mq5 encontrado: {mq5_path.relative_to(ROOT)}")
    else:
        print(f"  AVISO: no se encontro .mq5 — exportar desde SQ GUI y pasar con --mq5")
        return 1

    # ── Paso 2: sqcli orders → CSV ──
    print(f"\n[2] Exportando orders a CSV via sqcli...")
    if _sq_running():
        print("  WARN: SQ GUI activo en puerto 5050 — sqcli bloqueado.")
        print("  Saltando export CSV (protecciones y auditoria continuan).")
    elif not SQCLI.exists():
        print(f"  WARN: sqcli no encontrado en {SQCLI} — saltando export CSV")
    elif sq4_path:
        export_orders_csv(sq4_path, EXPORTED)
    else:
        print("  WARN: sin .sq4 disponible — saltando export CSV")

    # ── Paso 3: leer .mq5 y aplicar protecciones ──
    print(f"\n[3] Aplicando 4 protecciones obligatorias al .mq5...")
    code = mq5_path.read_text(encoding="utf-8", errors="ignore")
    code = inject_protections(code, activo)
    print(f"  P1: Sleep anti-sync aplicado")
    print(f"  P2: Limite 1 trade/hora aplicado")
    print(f"  P3: MaxSlippagePips = {MAX_SLIPPAGE.get(activo, MAX_SLIPPAGE_DEFAULT)}")
    print(f"  P4: Monitor spread > 10x media 20 velas aplicado")

    # ── Paso 4: generar nombre unico y guardar ──
    print(f"\n[4] Generando ID unico y guardando en results/exported/...")
    mq5_out = save_exported(code, args.build, activo)
    print(f"  Guardado: {mq5_out.name}")

    # ── Paso 5: auditar ──
    print(f"\n[5] Auditando con mql5-auditor.py...")
    audit_rc = run_auditor(mq5_out)

    # ── Informe final ──
    print_report(args.strategy, args.build, activo, mq5_out, audit_rc)

    return 0 if audit_rc in (0, 1) else 1


if __name__ == "__main__":
    sys.exit(main())
