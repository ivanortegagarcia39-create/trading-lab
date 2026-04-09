# CLAUDE.md — Constitucion del Proyecto TradingLab

## Proposito del proyecto
Desarrollar estrategias de trading algoritmico robustas y compatibles
con empresas de fondeo (prop firms), usando StrategyQuant y un sistema
de agentes basado en Claude Code.

## Definicion de robustez
Una estrategia es robusta si:
- Supera el Retester con datos fuera de muestra
- Pasa los filtros de fondeo definidos en docs\funding-rules.md
- Tiene ratio riesgo/recompensa coherente y drawdown controlado
- No esta sobreoptimizada para un periodo concreto

## Rol de Claude en este proyecto
Claude actua como asistente tecnico y orquestador.
NO toma decisiones finales de trading — esas las tomamos nosotros.
Claude puede: analizar, sugerir, organizar, automatizar tareas.
Claude NO puede: aceptar estrategias sin revision humana.

## Universo inicial de prueba (Fase 1)
- Mercados:
  EUR/USD (Forex spot — datos disponibles en SQ)
  XAU/USD (Oro spot — datos disponibles en SQ)
  GC (Gold Futures CME — pendiente de datos)
  NQ (Nasdaq Futures CME — pendiente de datos)
- Temporalidades: H1 principal, M15 descartado
- Estilos: Trend-following, Mean Reversion

## Nota sobre temporalidades
M15 descartado como temporalidad principal tras Builds 1-6.
Las comisiones reales FTMO (0.5 pips + 7 USD/lote + 0.5 pip)
eliminan el edge en estrategias de baja frecuencia en M15.
H1 adoptado como temporalidad principal.
Si en el futuro se prueba M15 de nuevo, debe ser con hipotesis
de alta frecuencia (15+ trades al mes minimo).

## Nota sobre activos de futuros
GC y NQ requieren datos de futuros CME que aun no tenemos
importados en SQ. Trabajar con EUR/USD y XAU/USD hasta
tener los datos de futuros correctamente configurados.
XAU/USD (spot) es compatible con FTMO aunque es distinto
a GC futuros — verificar reglas especificas en
docs\funding-rules.md antes de aprobar estrategias en oro.

## Foco actual
SOLO trabajamos en: investigacion → hipotesis → Builder.
No expandimos a automatizacion avanzada hasta tener
3+ estrategias aprobadas.

## Roadmap futuro (NO el foco ahora)
- Automatizacion profunda
- Control remoto con N8N + Discord/Telegram
- Multi-proyecto
- Expansion a GC y NQ cuando tengamos datos

## Workflow operativo
Ver: docs\sq-workflow.md

## Reglas de decision
Ver: docs\decision-rules.md

## Configuracion estandar de backtest FTMO
Obligatoria en TODOS los builds y retests sin excepcion:

### EUR/USD y pares Forex
- Desviacion (spread): 0.5 pips
- Comision: 7 USD por lote completo (round turn)
- Deslizamiento: 0.5 pips

### XAU/USD (Oro spot)
- Desviacion (spread): 30 pips
- Comision: 7 USD por lote completo (round turn)
- Deslizamiento: 2 pips
- NOTA: 1 pip en XAU/USD = 0.01 USD/oz
  El spread real de FTMO en oro es aprox 30 USD/lote.
  Esta configuracion es CRITICA — sin ella los
  resultados del Builder seran completamente irreales.

Basada en condiciones reales de brokers FTMO
(Eightcap, Purple Trading).
Esta configuracion no se puede cambiar sin consenso.