# CLAUDE.md — Constitucion del Proyecto TradingLab

## Proposito del proyecto
Desarrollar estrategias de trading algoritmico robustas
y compatibles con empresas de fondeo (prop firms),
usando StrategyQuant X y un sistema de agentes
basado en Claude Code.
Objetivo final: automatizacion total del pipeline
desde el analisis de mercados hasta la operacion
autonoma en cuentas de fondeo de multiples prop firms.

## Definicion de robustez
Una estrategia es robusta si:
- Supera el Retester con datos fuera de muestra
- Pasa el WFO con WFE >= 50%
- Pasa los filtros de fondeo de docs\funding-rules.md
- Tiene ratio TP/SL >= 2:1 con comisiones reales
- No esta sobreajustada — riesgo BAJO segun
  skill-avoiding-overfitting.md
- No depende de un periodo historico concreto

## Rol de Claude en este proyecto
Claude actua como asistente tecnico y orquestador.
NO toma decisiones finales de trading.
Claude puede: analizar, sugerir, organizar, coordinar.
Claude NO puede: aprobar estrategias sin decision humana.

## Universo inicial de prueba (Fase 1)
Mercados activos:
- EUR/USD (Forex spot — datos disponibles en SQ)
- XAU/USD (Oro spot — datos disponibles en SQ)

Mercados pendientes de datos:
- GBP/USD — descargar cuando haya 3 estrategias aprobadas
- USD/JPY — descargar cuando haya 3 estrategias aprobadas
- GC (Gold Futures CME) — pendiente fuente de datos
- NQ (Nasdaq Futures CME) — pendiente fuente de datos

Temporalidad principal: H1
M15 descartado tras Builds 1-6. Las comisiones
reales FTMO eliminan el edge en M15 con baja
frecuencia de trades.

## Sistema de agentes (10 activos)
1. market-selector — selecciona activo optimo
2. market-analyst — genera hipotesis anti-sobreajuste
3. propfirm-analyst — analiza y compara prop firms
4. funding-specialist — evalua compatibilidad FTMO
5. sq-specialist — configura SQ y genera informes tecnicos
6. evaluator-assistant — genera informes Evaluation Gate
7. export-specialist — exporta estrategias a MT5
8. performance-monitor — monitorea EAs en produccion
9. data-manager — gestiona datos historicos en SQ
10. orchestrator — coordina y decide

Agentes planificados para Capa 1 (tras 3 estrategias):
- technical-analyst
- correlation-analyst
- risk-manager
- news-researcher

## Sistema de tickets
Cada hipotesis tiene un ticket en:
research\active-tickets\[TICKET-ID]-[nombre]\

Estructura de cada ticket:
- hypothesis.md — hipotesis original
- evaluation-log.md — log de observaciones
- gate-decisions.md — decisiones del pipeline
- current-phase.txt — fase actual

El orchestrator escanea los tickets al inicio
de cada sesion y clasifica en:
ACTIVO / STALE (>48h sin actividad) / BLOQUEADO

## Pipeline completo (22 pasos)
Ver docs\sq-workflow.md para el detalle completo.

Fases principales:
1. Preparacion: data-manager → market-selector →
   market-analyst → propfirm-analyst →
   funding-specialist → sq-specialist
2. Build: humano lanza → evaluator-assistant →
   humano firma Evaluation Gate
3. Validacion: Retester → paso 12b analisis OOS →
   WFO → dictamen WFO
4. Aprobacion: propfirm-analyst → funding-specialist
   → decision humana final
5. Produccion: export-specialist → challenge →
   performance-monitor

## Prop firm principal
FTMO Challenge 2-Step — cuenta 25.000 USD
Ver docs\funding-rules.md para reglas completas.

Puntos criticos FTMO 2-Step:
- Daily Loss 5% DINAMICO — recalculo medianoche Praga
- Max DD 10% DINAMICO — solo sube nunca baja
- Min 4 dias con posiciones INICIADAS
- Sin Regla del Mejor Dia en 2-Step
- Margenes operativos: 3% daily, 7% max DD

## Foco actual
SOLO trabajamos en: preparacion → hipotesis → Builder.
No expandimos a automatizacion avanzada hasta tener
3+ estrategias aprobadas.

## Roadmap futuro
Ver docs\roadmap-v2.md para el detalle completo.
Capa 0: pipeline manual — estado actual
Capa 1: expansion tras 3 estrategias aprobadas
Capa 2: N8N + Claude API — orquestador autonomo
Capa 3: automatizacion total con MT5
Capa 4: escalado multi-prop firm

## Configuracion estandar de backtest FTMO
Obligatoria en TODOS los builds y retests:

EUR/USD:
- Spread: 0.5 pips
- Comision: 7 USD por lote
- Slippage: 0.5 pips

XAU/USD:
- Spread: 30 pips
- Comision: 7 USD por lote
- Slippage: 2 pips
- NOTA: 1 pip XAU/USD = 0.01 USD/oz
  Verificar pip size en SQ antes de cada build

Periodo in-sample: 2003.05.05 a 2020.12.31
Periodo OOS: 2021.01.01 a fecha actual
Esta configuracion NO se puede cambiar sin consenso.

## Reglas inquebrantables
1. Nunca usar datos OOS (2021-actual) en Builder
2. Comisiones reales FTMO en todos los builds
3. H1 como temporalidad principal siempre
4. Ratio TP/SL minimo 2:1 siempre
5. Riesgo 1% por trade siempre
6. Max 2 trades por dia en H1
7. Decision humana en Evaluation Gate y Aprobacion
8. market-selector antes de cualquier hipotesis nueva
9. data-manager verifica datos antes de cada build
10. Nunca lanzar WFO sin completar el paso 12b
11. Mismas comisiones en Builder y Retester siempre
12. CLAUDE.md no se modifica sin consenso

## Historial de builds (dispositivo anterior)
Build 1-2: LARB M15 — logica asiatica no nativa en SQ
Build 3: EMACross-ADX M15 — filtros mal configurados
Build 4: EMACross-ADX M15 sin comisiones — 6 candidatas
         PF 1.53-1.70 pero Retester negativo
Build 5: EMACross-ADX M15 con comisiones — PF max 1.27
         DESCARTADO
Build 6: NBARBreakout-RSI M15 — PF max 1.18
         REVISADO — cambio a H1
Build 7: NBARBreakout-RSI H1 — resultado desconocido
         (build en dispositivo anterior)

## Workflow operativo
Ver: docs\sq-workflow.md

## Reglas de decision
Ver: docs\decision-rules.md