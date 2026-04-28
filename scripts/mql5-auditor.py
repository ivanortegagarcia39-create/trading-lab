"""
mql5-auditor.py
Audita codigo MQL5 exportado desde SQ antes de cualquier deploy a MT5.

Dos capas de auditoria:
  1. Auditoria ESTATICA  — patrones de riesgo detectados por regex/AST
  2. Auditoria SEMANTICA — analisis via Ollama local (DeepSeek-Coder)

Resultado: APPROVE / REVIEW / REJECT
  REJECT  → abortar export automaticamente
  REVIEW  → continuar pero registrar en audit trail
  APPROVE → deploy autorizado

Uso:
    python mql5-auditor.py --mql5-file ruta/estrategia.mq5
    python mql5-auditor.py --mql5-file ruta/estrategia.mq5 --ollama-url http://localhost:11434
    python mql5-auditor.py --mql5-file ruta/estrategia.mq5 --no-ollama
"""

import argparse
import importlib.util
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import urllib.request
    import urllib.error
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False

# Importación dinámica del model-router (nombre con guión)
_router_path = Path(__file__).parent / "model-router.py"
if _router_path.exists():
    _router_spec = importlib.util.spec_from_file_location("model_router", _router_path)
    _model_router = importlib.util.module_from_spec(_router_spec)
    _router_spec.loader.exec_module(_model_router)
else:
    _model_router = None


# ─── Estructuras de datos ─────────────────────────────────────────────────────

@dataclass
class Finding:
    severity: str   # CRITICAL / WARNING / INFO
    category: str
    line: int
    description: str
    snippet: str = ""


@dataclass
class AuditResult:
    verdict: str        # APPROVE / REVIEW / REJECT
    findings: list[Finding] = field(default_factory=list)
    ollama_used: bool = False
    ollama_risk_level: str = ""
    ollama_issues: list[str] = field(default_factory=list)
    ollama_recommendation: str = ""

    def has_critical(self) -> bool:
        return any(f.severity == "CRITICAL" for f in self.findings)

    def has_warnings(self) -> bool:
        return any(f.severity == "WARNING" for f in self.findings)


# ─── Auditoria estatica ───────────────────────────────────────────────────────

class StaticAuditor:
    """
    Detecta patrones de riesgo mediante analisis de texto del codigo MQL5.
    No requiere compilador ni ejecucion — solo lectura del codigo fuente.
    """

    def audit(self, code: str, lines: list[str]) -> list[Finding]:
        findings = []
        findings.extend(self._check_martingale(code, lines))
        findings.extend(self._check_grid_trading(code, lines))
        findings.extend(self._check_missing_sl(code, lines))
        findings.extend(self._check_high_frequency(code, lines))
        findings.extend(self._check_tick_size_vs_point(code, lines))
        findings.extend(self._check_magic_number(code, lines))
        findings.extend(self._check_no_sl_check(code, lines))
        return findings

    # ── 1. Martingala oculta ──────────────────────────────────────────────────

    def _check_martingale(self, code: str, lines: list[str]) -> list[Finding]:
        """
        Detecta patrones donde el lote se multiplica o aumenta tras una perdida.
        Patrones: LotSize * factor, lots *= X, lots + increment tras OrderProfit < 0
        """
        findings = []
        # Patrones de aumento de lotes
        martingale_patterns = [
            r'lot[s_]?\s*[\*\+]=\s*[\d\.]+',        # lots *= 2.0
            r'lot[s_]?\s*=\s*lot[s_]?\s*\*\s*\d',   # lots = lots * 2
            r'lot[s_]?\s*\*\s*(\d+\.?\d*)',           # lots * 1.5
            r'(multiply|martingale|double_lot)',       # keywords directos
            r'LastProfit\s*<\s*0.*lot',               # if LastProfit < 0 → aumentar lotes
            r'OrderProfit.*<.*0.*\*.*lot',            # OrderProfit < 0 * lots
        ]
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            for pat in martingale_patterns:
                if re.search(pat, line_lower):
                    findings.append(Finding(
                        severity="CRITICAL",
                        category="MARTINGALA",
                        line=i,
                        description="Posible incremento de lotes tras perdida (martingala oculta)",
                        snippet=line.strip(),
                    ))
                    break  # Un finding por linea
        return findings

    # ── 2. Grid trading ───────────────────────────────────────────────────────

    def _check_grid_trading(self, code: str, lines: list[str]) -> list[Finding]:
        """
        Detecta bucles con OrderSend a precios equidistantes (grid).
        Patron: for/while + OrderSend + Ask/Bid +/- n*step
        """
        findings = []
        in_loop = False
        loop_start = 0
        order_sends_in_loop = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip().lower()
            # Detectar inicio de bucle
            if re.search(r'\b(for|while)\s*\(', stripped):
                in_loop = True
                loop_start = i
                order_sends_in_loop = []

            if in_loop and 'ordersend' in stripped:
                order_sends_in_loop.append(i)

            # Fin de bloque
            if in_loop and stripped == '}':
                if len(order_sends_in_loop) >= 2:
                    findings.append(Finding(
                        severity="CRITICAL",
                        category="GRID_TRADING",
                        line=loop_start,
                        description=f"Posible grid trading: {len(order_sends_in_loop)} OrderSend dentro de un bucle (lineas {order_sends_in_loop})",
                        snippet=f"Bucle desde linea {loop_start}",
                    ))
                in_loop = False
                order_sends_in_loop = []

        # Tambien buscar el patron de precio equidistante explicitamente
        grid_price_patterns = [
            r'ask\s*[\+\-]\s*\w+\s*\*\s*(step|grid|distance|gap)',
            r'bid\s*[\+\-]\s*\w+\s*\*\s*(step|grid|distance|gap)',
            r'gridstep|grid_step|step_size.*order',
        ]
        for i, line in enumerate(lines, 1):
            for pat in grid_price_patterns:
                if re.search(pat, line.lower()):
                    findings.append(Finding(
                        severity="CRITICAL",
                        category="GRID_TRADING",
                        line=i,
                        description="Patron de precio equidistante para grid trading",
                        snippet=line.strip(),
                    ))
                    break

        return findings

    # ── 3. Sin stop loss ─────────────────────────────────────────────────────

    def _check_missing_sl(self, code: str, lines: list[str]) -> list[Finding]:
        """
        Detecta OrderSend con SL = 0 o sin parametro SL.
        MQL5: OrderSend(symbol, type, volume, price, slippage, SL, TP, ...)
        """
        findings = []
        # Buscar OrderSend con sl=0 explicitamente o sl sin asignar
        sl_zero_patterns = [
            r'ordersend\s*\([^)]*,\s*0\s*,\s*[\d\.]+\s*[\),]',  # sl=0 como parametro posicional
            r'sl\s*=\s*0\b(?!\.\d)',          # sl = 0
            r'stoploss\s*=\s*0\b(?!\.\d)',
            r'm_request\.(sl|stoploss)\s*=\s*0\b',  # estructura de request
        ]
        for i, line in enumerate(lines, 1):
            for pat in sl_zero_patterns:
                if re.search(pat, line.lower()):
                    findings.append(Finding(
                        severity="CRITICAL",
                        category="SIN_STOP_LOSS",
                        line=i,
                        description="Stop Loss definido como 0 — orden sin proteccion",
                        snippet=line.strip(),
                    ))
                    break

        # Verificar que existe al menos una asignacion de SL en el archivo
        has_sl_assignment = bool(re.search(
            r'(sl|stop_loss|stoploss)\s*=\s*(?!0\b)[^\s;]+',
            code, re.IGNORECASE
        ))
        if not has_sl_assignment and 'ordersend' in code.lower():
            findings.append(Finding(
                severity="CRITICAL",
                category="SIN_STOP_LOSS",
                line=0,
                description="No se detecta ninguna asignacion de Stop Loss en el archivo",
                snippet="Revision completa del archivo requerida",
            ))

        return findings

    # ── 4. Alta frecuencia encubierta ─────────────────────────────────────────

    def _check_high_frequency(self, code: str, lines: list[str]) -> list[Finding]:
        """
        Detecta ausencia de restriccion de tiempo minimo entre trades.
        Si no hay verificacion de tiempo desde el ultimo trade → potencial HFT.
        """
        findings = []
        # Patrones de restriccion de tiempo (bueno — su presencia es positiva)
        time_restriction_patterns = [
            r'timediff|time_diff|lasttradeTime|last_trade_time',
            r'TimeCurrent\(\)\s*-\s*\w+\s*[<>]\s*\d+',  # TimeCurrent() - lastTime > X
            r'(minbars|min_bars|bars_since)',
            r'period\s*=\s*(period_m\d+|period_h\d+)',
        ]
        has_time_restriction = any(
            re.search(pat, code, re.IGNORECASE)
            for pat in time_restriction_patterns
        )

        # Contar OrderSend en el archivo
        order_send_count = len(re.findall(r'\bOrderSend\b', code, re.IGNORECASE))

        if not has_time_restriction and order_send_count > 0:
            findings.append(Finding(
                severity="WARNING",
                category="ALTA_FRECUENCIA",
                line=0,
                description=(
                    f"No se detecta restriccion de tiempo minimo entre trades. "
                    f"OrderSend aparece {order_send_count} veces. "
                    f"Verificar que no opera mas de 3 trades/hora."
                ),
                snippet="Ausencia de control TimeCurrent() entre trades",
            ))

        # Buscar trades sin barra de referencia (puede ejecutar en cada tick)
        tick_trading_patterns = [
            r'OnTick\s*\(\s*\)',   # funcion OnTick sin restriccion
        ]
        has_bar_filter = bool(re.search(
            r'(isNewBar|isnewbar|new_bar|newbar|Bars\(\))',
            code, re.IGNORECASE
        ))
        has_on_tick = bool(re.search(r'\bOnTick\s*\(', code, re.IGNORECASE))

        if has_on_tick and not has_bar_filter and order_send_count > 0:
            findings.append(Finding(
                severity="WARNING",
                category="ALTA_FRECUENCIA",
                line=0,
                description=(
                    "OnTick sin filtro de nueva barra — puede ejecutar en cada tick. "
                    "Verificar que hay control isnewbar o equivalente."
                ),
                snippet="OnTick detectado sin IsNewBar() / Bars() check",
            ))

        return findings

    # ── 5. Tick Size vs Point ─────────────────────────────────────────────────

    def _check_tick_size_vs_point(self, code: str, lines: list[str]) -> list[Finding]:
        """
        Detecta uso de _Point en calculos de lotes en lugar de
        SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE).
        Critico para pares JPY e indices.
        """
        findings = []
        # Buscar calculos de lotes que usen _Point directamente
        point_in_lot_patterns = [
            r'(lot[s_]?|volume|size)\s*=.*\bPoint\b',
            r'\bPoint\b.*\/(sl|stoploss|stop_loss)',
            r'\bPoint\b.*\*.*lot',
            r'AccountBalance\(\).*\*.*Point',
        ]
        for i, line in enumerate(lines, 1):
            for pat in point_in_lot_patterns:
                if re.search(pat, line, re.IGNORECASE):
                    findings.append(Finding(
                        severity="WARNING",
                        category="TICK_SIZE_VS_POINT",
                        line=i,
                        description=(
                            "Uso de _Point en calculo de lotes. "
                            "Para JPY e indices usar SymbolInfoDouble(sym, SYMBOL_TRADE_TICK_SIZE). "
                            "_Point puede ser incorrecto en estos instrumentos."
                        ),
                        snippet=line.strip(),
                    ))
                    break

        return findings

    # ── 6. Magic number ────────────────────────────────────────────────────────

    def _check_magic_number(self, code: str, lines: list[str]) -> list[Finding]:
        """Verifica que el EA tiene un magic number definido y no es 0."""
        findings = []
        has_magic = bool(re.search(r'(MagicNumber|magic_number|MAGIC)\s*=\s*\d+', code, re.IGNORECASE))
        magic_zero = bool(re.search(r'(MagicNumber|magic_number|MAGIC)\s*=\s*0\b', code, re.IGNORECASE))

        if not has_magic:
            findings.append(Finding(
                severity="WARNING",
                category="MAGIC_NUMBER",
                line=0,
                description="No se detecta Magic Number definido. Cada EA debe tener ID unico.",
                snippet="",
            ))
        elif magic_zero:
            findings.append(Finding(
                severity="WARNING",
                category="MAGIC_NUMBER",
                line=0,
                description="Magic Number = 0. Riesgo de colision con otros EAs en la misma cuenta.",
                snippet="",
            ))

        return findings

    # ── 7. Anti-sync delay ────────────────────────────────────────────────────

    def _check_no_sl_check(self, code: str, lines: list[str]) -> list[Finding]:
        """Verifica que el EA incluye el delay anti-sincronizacion del proyecto."""
        findings = []
        has_sleep = bool(re.search(r'\bSleep\s*\(', code, re.IGNORECASE))
        has_mathrand = bool(re.search(r'\bMathRand\s*\(', code, re.IGNORECASE))

        if not has_sleep or not has_mathrand:
            findings.append(Finding(
                severity="WARNING",
                category="ANTI_SYNC",
                line=0,
                description=(
                    "No se detecta Sleep(MathRand()...) para delay anti-sincronizacion. "
                    "Obligatorio segun protocolo export-specialist.md para evitar "
                    "deteccion de group trading por la prop firm."
                ),
                snippet="",
            ))

        return findings


# ─── Auditoria semantica (Ollama) ─────────────────────────────────────────────

OLLAMA_PROMPT = """Analiza este codigo MQL5 de trading. Identifica:
1. Errores de logica de trading
2. Gestion de lotes incorrecta
3. Uso incorrecto de funciones de trading
4. Riesgos no controlados

Responde UNICAMENTE en formato JSON con exactamente estos campos:
{
  "risk_level": "low" | "medium" | "high",
  "issues": ["descripcion del problema 1", "descripcion del problema 2"],
  "recommendation": "approve" | "review" | "reject"
}

No añadas texto fuera del JSON. Solo el objeto JSON.

Codigo MQL5 a analizar:
"""


def query_ollama(code: str, ollama_url: str, model: str = "deepseek-coder") -> dict | None:
    """
    Envia el codigo al model-router (task: mql5_audit) y devuelve resultado JSON.
    Fallback a Ollama directo si el router no está disponible.
    """
    prompt = OLLAMA_PROMPT + code[:8000]

    # Usar model-router si está disponible
    if _model_router is not None:
        try:
            response_text = _model_router.route("mql5_audit", prompt)
            # Intentar extraer JSON de la respuesta
            start = response_text.find("{")
            if start != -1:
                end = response_text.rfind("}") + 1
                return json.loads(response_text[start:end])
        except Exception:
            pass  # Fallback a Ollama directo

    # Fallback: llamada directa a Ollama
    if not HAS_URLLIB:
        return None

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }
    data = json.dumps(payload).encode("utf-8")

    try:
        req = urllib.request.Request(
            f"{ollama_url}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            response_text = result.get("response", "")
            return json.loads(response_text)
    except (urllib.error.URLError, json.JSONDecodeError, KeyError, TimeoutError):
        return None


# ─── Determinacion del veredicto ─────────────────────────────────────────────

def determine_verdict(result: AuditResult) -> str:
    """
    REJECT:  cualquier finding CRITICAL en auditoria estatica
             O recommendation = reject de Ollama
    REVIEW:  uno o mas findings WARNING (sin CRITICAL)
             O risk_level = high de Ollama
    APPROVE: sin findings o solo INFO
             Y (Ollama no disponible O recommendation = approve)
    """
    if result.has_critical():
        return "REJECT"

    if result.ollama_used and result.ollama_recommendation == "reject":
        return "REJECT"

    if result.has_warnings():
        return "REVIEW"

    if result.ollama_used and result.ollama_risk_level == "high":
        return "REVIEW"

    return "APPROVE"


# ─── Entrada principal ────────────────────────────────────────────────────────

def audit_file(mql5_path: str, ollama_url: str | None) -> AuditResult:
    code = Path(mql5_path).read_text(encoding="utf-8", errors="ignore")
    lines = code.splitlines()

    static = StaticAuditor()
    findings = static.audit(code, lines)

    result = AuditResult(verdict="", findings=findings)

    # Auditoria semantica via Ollama
    if ollama_url:
        ollama_data = query_ollama(code, ollama_url)
        if ollama_data:
            result.ollama_used = True
            result.ollama_risk_level = ollama_data.get("risk_level", "")
            result.ollama_issues = ollama_data.get("issues", [])
            result.ollama_recommendation = ollama_data.get("recommendation", "")

            # Convertir issues de Ollama en findings INFO/WARNING
            for issue in result.ollama_issues:
                severity = "WARNING" if result.ollama_risk_level in ("medium", "high") else "INFO"
                findings.append(Finding(
                    severity=severity,
                    category="OLLAMA_SEMANTICO",
                    line=0,
                    description=issue,
                    snippet="",
                ))

    result.verdict = determine_verdict(result)
    return result


def print_report(result: AuditResult, mql5_path: str) -> None:
    print("=" * 60)
    print("MQL5 AUDITOR — TradingLab")
    print(f"Archivo: {mql5_path}")
    print("=" * 60)

    severity_icons = {"CRITICAL": "CRITICO", "WARNING": "AVISO", "INFO": "INFO"}
    static_findings = [f for f in result.findings if f.category != "OLLAMA_SEMANTICO"]
    ollama_findings = [f for f in result.findings if f.category == "OLLAMA_SEMANTICO"]

    if static_findings:
        print("\n--- AUDITORIA ESTATICA ---")
        for f in static_findings:
            tag = severity_icons.get(f.severity, f.severity)
            loc = f"linea {f.line}" if f.line > 0 else "global"
            print(f"[{tag}] {f.category} ({loc})")
            print(f"  {f.description}")
            if f.snippet:
                print(f"  Codigo: {f.snippet[:80]}")
    else:
        print("\n--- AUDITORIA ESTATICA: sin hallazgos ---")

    if result.ollama_used:
        print("\n--- AUDITORIA SEMANTICA (Ollama) ---")
        print(f"  Nivel de riesgo: {result.ollama_risk_level.upper()}")
        print(f"  Recomendacion:   {result.ollama_recommendation.upper()}")
        if ollama_findings:
            for f in ollama_findings:
                print(f"  - {f.description}")
    else:
        print("\n--- AUDITORIA SEMANTICA: Ollama no disponible (solo estatica) ---")

    print()
    verdict_icons = {
        "APPROVE": "APROBADO",
        "REVIEW":  "REVISAR",
        "REJECT":  "RECHAZADO",
    }
    print(f"VEREDICTO: {verdict_icons.get(result.verdict, result.verdict)}")
    if result.verdict == "REJECT":
        print("  → Deploy BLOQUEADO automaticamente")
        print("  → Corregir los errores CRITICOS antes de exportar")
    elif result.verdict == "REVIEW":
        print("  → Deploy permitido con advertencias")
        print("  → Registrado en audit trail para seguimiento")
    else:
        print("  → Deploy autorizado")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Auditor de codigo MQL5 exportado desde SQ — TradingLab"
    )
    parser.add_argument("--mql5-file", required=True, help="Ruta al archivo .mq5")
    parser.add_argument(
        "--ollama-url",
        default="http://localhost:11434",
        help="URL de Ollama local (default: http://localhost:11434)"
    )
    parser.add_argument(
        "--no-ollama",
        action="store_true",
        help="Desactivar auditoria semantica aunque Ollama este disponible"
    )
    parser.add_argument(
        "--output-json",
        help="Guardar resultado en JSON (opcional)"
    )
    args = parser.parse_args()

    ollama_url = None if args.no_ollama else args.ollama_url
    result = audit_file(args.mql5_file, ollama_url)
    print_report(result, args.mql5_file)

    if args.output_json:
        output = {
            "verdict": result.verdict,
            "mql5_file": args.mql5_file,
            "findings": [
                {
                    "severity": f.severity,
                    "category": f.category,
                    "line": f.line,
                    "description": f.description,
                }
                for f in result.findings
            ],
            "ollama_used": result.ollama_used,
            "ollama_risk_level": result.ollama_risk_level,
            "ollama_recommendation": result.ollama_recommendation,
        }
        Path(args.output_json).write_text(
            json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"\nResultado JSON guardado en: {args.output_json}")

    # Codigo de salida para integracion en pipeline
    exit_codes = {"APPROVE": 0, "REVIEW": 1, "REJECT": 2}
    sys.exit(exit_codes.get(result.verdict, 3))


if __name__ == "__main__":
    main()
