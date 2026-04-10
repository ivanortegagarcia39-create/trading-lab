# Project Status — TradingLab
Ultima actualizacion: 2026-04-10

---

## 1. FILOSOFIA DEL PROYECTO

**Principio rector:** El mercado no sabe lo que el humano piensa que deberia funcionar.
Los Builds 1-8 fallaron porque el humano restringia el espacio de busqueda.
Con el enfoque actual SQ decide la logica. Los numeros deciden que avanza.

### Los 4 principios fundamentales

| # | Principio | Significado practico |
|---|-----------|----------------------|
| 1 | SQ decide la logica de entrada | Paleta completa +100 indicadores — sin hipotesis humana |
| 2 | Los numeros deciden que avanza | Criterios automaticos en cada puerta del pipeline |
| 3 | Portfolio por correlacion | No por preferencia ni intuicion del humano |
| 4 | Unica intervencion humana: forward test demo | En ningun otro momento el humano decide nada |

### Lo que el humano define (restricciones de riesgo)
- Activo y temporalidad
- Comisiones reales FTMO
- Ratio TP/SL minimo 2:1
- Riesgo 1% por trade
- Max 2 trades por dia
- Sesion 08:00 a 20:00

### Lo que SQ decide (logica de entrada)
- Que indicadores usar de la paleta completa
- Cuantas condiciones de entrada (1 a 3)
- Que combinaciones de señales
- Que parametros dentro de los rangos
- Direccion de operaciones (long, short o ambas)

### Lo que el pipeline filtra
- Sobreajuste — via Retester, paso 12b y WFO
- Redundancia — via correlation-analyst
- Todo automaticamente. Sin subjetividad.

---

## 2. ESTADO ACTUAL

**Fecha:** 2026-04-10
**Situacion:** Pipeline rediseñado. Build 8 corriendo con enfoque anterior (ultimo build con hipotesis humana). Build 9 sera el primero con Builder libre sin sesgo humano.

### Documentacion base

| Archivo | Contenido |
|---------|-----------|
| CLAUDE.md | Constitucion del proyecto |
| docs\funding-rules.md | Reglas FTMO completas |
| docs\sq-workflow.md | Flujo de trabajo en SQ |
| docs\decision-rules.md | Reglas de decision del pipeline |
| docs\roadmap-v2.md | Roadmap por capas |
| docs\project-status.md | Este archivo |

**Agentes activos:** 11
**Skills operativas:** 22 en docs\skills\
**Tickets activos:** 1 — TICKET-001 en fase build-running (Build 8)

---

## 3. AGENTES ACTIVOS (11)

| # | Agente | Rol actual |
|---|--------|------------|
| 1 | market-selector | Selecciona el activo optimo antes de cada ciclo de busqueda |
| 2 | market-analyst | Configura parametros del Builder libre — NO genera hipotesis (ROL REDISEÑADO) |
| 3 | propfirm-analyst | Analiza y compara prop firms por activo y estrategia |
| 4 | funding-specialist | Evalua compatibilidad con reglas de la prop firm elegida |
| 5 | sq-specialist | Configura SQ Builder, Retester y Optimizer |
| 6 | evaluator-assistant | Genera informes estructurados del Evaluation Gate |
| 7 | correlation-analyst | Gestiona automaticamente la composicion del portfolio (ACTIVADO) |
| 8 | export-specialist | Exporta estrategias aprobadas de SQ a MQL5/MT5 |
| 9 | performance-monitor | Monitorea EAs en produccion y alerta sobre riesgo |
| 10 | data-manager | Verifica y gestiona datos historicos en SQ |
| 11 | orchestrator | Coordina el pipeline y aplica criterios automaticos |

### Cambios respecto al estado anterior

- **market-analyst rediseñado:** antes generaba hipotesis manuales (causa de los 8 builds fallidos). Ahora solo configura el terrain de busqueda. NUNCA propone logicas de entrada.
- **correlation-analyst activado:** antes era un agente planificado. Ahora es operativo y gestiona el portfolio automaticamente.
- **11 agentes activos** (antes 10).

### Agentes planificados (post Capa 1)
- risk-manager — gestion de riesgo avanzada del portfolio
- news-researcher — contexto macro y deteccion de periodos anomalos

---

## 4. SKILLS OPERATIVAS (22)

| Skill | Proposito |
|-------|-----------|
| skill-builder-libre.md | Configuracion completa del Builder libre sin hipotesis |
| skill-evaluation-auto.md | Criterios automaticos del Evaluation Gate completo |
| skill-portfolio-selection.md | Seleccion y gestion automatica del portfolio |
| skill-portfolio-correlation.md | Correlaciones entre activos del portfolio |
| skill-evaluation-report.md | Formato estandar de informes de evaluacion |
| skill-wfo-interpretation.md | Interpretacion del Walk Forward Optimization |
| skill-avoiding-overfitting.md | Deteccion y prevencion de sobreajuste |
| skill-retester.md | Configuracion y uso del Retester |
| skill-optimizer.md | Configuracion del Optimizer y WFO |
| skill-sq-builder.md | Configuracion del Builder en SQ |
| skill-results-analysis.md | Analisis de resultados del Builder |
| skill-precbuild-checklist.md | Checklist obligatorio antes de lanzar Builder |
| skill-ftmo-rules.md | Reglas FTMO resumidas para consulta rapida |
| skill-ftmo-simulation.md | Simulacion de challenge FTMO |
| skill-market-context.md | Analisis de contexto de mercado |
| skill-propfirms-comparison.md | Comparativa detallada de prop firms |
| skill-sq-export-mt5.md | Exportacion de estrategias de SQ a MT5/MQL5 |
| skill-pipeline-errors.md | Diagnostico y resolucion de errores del pipeline |
| skill-data-management.md | Gestion de datos historicos en SQ |
| skill-propfirm-challenge-execution.md | Proceso de ejecucion de challenges |
| skill-claude-sessions.md | Gestion de sesiones con Claude Code |
| skill-ticket-system.md | Sistema de tickets de seguimiento |
| skill-hypothesis-design.md | OBSOLETA — referencia historica solamente |

---

## 5. HISTORIAL DE BUILDS

| Build | Enfoque | Config | Resultado | Decision |
|-------|---------|--------|-----------|----------|
| Build 1-2 | Hipotesis humana | LARB M15 | Logica asiatica no nativa en SQ | DESCARTADO |
| Build 3 | Hipotesis humana | EMACross-ADX M15 | Filtros mal configurados | DESCARTADO |
| Build 4 | Hipotesis humana | EMACross-ADX M15 sin comisiones | 6 candidatas PF 1.53-1.70 — Retester negativo | DESCARTADO |
| Build 5 | Hipotesis humana | EMACross-ADX M15 con comisiones | PF max 1.27 — edge insuficiente en M15 | DESCARTADO |
| Build 6 | Hipotesis humana | NBARBreakout-RSI M15 | PF max 1.18 — M15 con comisiones inviable | DESCARTADO |
| Build 7 | Hipotesis humana | NBARBreakout-RSI H1 | Resultado desconocido — dispositivo anterior | PENDIENTE |
| Build 8 | Hipotesis humana | TrendFollowing EURUSD H1 EMA50+ADX | EN EJECUCION — ultimo build con sesgo humano | EN CURSO |
| Build 9+ | Builder libre | Paleta completa +100 indicadores | PENDIENTE — primer build sin sesgo humano | PENDIENTE |

### Aprendizajes acumulados

- **M15 descartado formalmente:** comisiones reales FTMO eliminan el edge en M15
- **Hipotesis humana descartada:** 8 builds fallidos por restriccion del espacio de busqueda
- **H1 adoptado** como temporalidad principal
- **Builder libre es el camino:** SQ explora lo que el humano nunca consideraria

---

## 6. CONFIGURACION BUILDER LIBRE (Build 9+)

### Filosofia
SQ tiene libertad total para explorar millones de combinaciones.
El humano solo define las restricciones de riesgo.
El pipeline filtra el sobreajuste automaticamente.

### Parametros geneticos

| Parametro | Antes (Builds 1-8) | Ahora (Build 9+) |
|-----------|-------------------|-----------------|
| Generaciones | 20 | 30 por ciclo continuo |
| Poblacion por isla | 50 | 100 |
| Islas | 4 | 4 |
| Modo | Se paraba solo | Corre indefinido |
| Max estrategias | 500 | 1000 |
| Stop generation | Auto | Never |

### Paleta de bloques — COMPLETA
- Todos los grupos activados: tendencia, momentum, volatilidad, precio puro
- Todos los operadores activados
- Señales predefinidas: cruces, niveles, rupturas, tendencia
- Indicadores: EMA, SMA, DEMA, HMA, ADX, Aroon, SAR, RSI, Stochastic,
  CCI, MACD, Williams %R, Momentum, ROC, DeMarker, ATR, Bollinger,
  Keltner, Donchian, Standard Deviation, High, Low, Close, Open, HL2, HLC3,
  Highest, Lowest, Range — mas de 100 combinaciones posibles
- Sin restriccion de indicadores: NINGUNA
- Sin hipotesis previa: NINGUNA

### Filtros del Builder (mejorados)

| Filtro | Antes | Ahora |
|--------|-------|-------|
| PF minimo | 0.8 | 1.3 |
| Trades/mes minimo | cualquier | 6 |
| Ratio Ret/DD minimo | 0.5 | 0.8 |
| Monte Carlo | Desactivado | Activado |

### Restricciones de riesgo (invariables)
- Comisiones reales FTMO obligatorias
- Riesgo: 1% por trade, capital 25.000 USD
- Max 2 trades por dia, sesion 08:00-20:00
- SL: ATR-based 1.5x a 3.0x
- TP: ATR-based 3.0x a 6.0x, ratio minimo 2:1 sobre SL

### Tiempo de build recomendado
- Minimo: 24 horas
- Optimo: 48 horas
- Parar cuando: PF maximo no sube en 6+ horas consecutivas

Configuracion completa en: docs\skills\skill-builder-libre.md

---

## 7. CRITERIOS AUTOMATICOS DEL PIPELINE

Todo el pipeline opera sin intervencion humana.
Los criterios son numericos y no negociables.

### Fase 1 — Filtro del Builder (automatico en SQ)

| Criterio | Umbral | Accion |
|----------|--------|--------|
| PF | < 1.3 | No entra en databank |
| Trades/mes | < 6 | No entra en databank |
| Ratio Ret/DD | < 0.8 | No entra en databank |

### Fase 2 — Evaluation Gate (automatico por orchestrator)

**Descarte automatico** si cualquiera de:
- PF IS < 1.4
- Max DD IS > 7%
- Trades totales < 80
- Trades/mes < 8
- Win Rate < 30%
- Ratio TP/SL efectivo < 1.8:1
- Años negativos > 35%
- Beneficio en un solo mes > 45%
- DD maximo en ultimos 3 meses del IS

**Aprobacion automatica** para Retester si todos:
- PF IS >= 1.5
- Max DD IS <= 6%
- Trades totales >= 120
- Trades/mes >= 10
- Win Rate >= 38%
- Ratio TP/SL efectivo >= 2:1
- Años positivos >= 75%
- Monte Carlo sin degradacion

### Fase 3 — Paso 12b OOS (automatico)

**Descarte automatico** si cualquiera de:
- PF OOS < 1.2
- Caida PF IS→OOS > 25%
- DD OOS > 7%
- Trades/mes OOS < 5

**Aprobacion para WFO** si todos:
- PF OOS >= 1.3
- Caida PF <= 20%
- DD OOS <= 6.5%
- Trades/mes OOS >= 6

### Fase 4 — Dictamen WFO (automatico)

**Descarte automatico** si cualquiera de:
- WFE < 40%
- 2+ ventanas OOS con PF < 1.0
- 2 ventanas OOS negativas consecutivas
- DD OOS > 7.5% en cualquier ventana

**Aprobacion final** si todos:
- WFE >= 50%
- 0 ventanas OOS con PF < 0.9
- DD OOS <= 7% en todas las ventanas
- PF OOS ultima ventana >= 1.1
- Parametros estables (desviacion < 25%)
- PF OOS promedio >= 1.25

Criterios completos en: docs\skills\skill-evaluation-auto.md

---

## 8. OBJETIVO DE PORTFOLIO

### Estructura objetivo

| Tipo | Estrategias | Correlacion max | DD combinado |
|------|-------------|-----------------|--------------|
| Minimo viable | 3 | < 0.5 | < 10% |
| Optimo | 5 | < 0.4 | < 8% |
| Maximo | 8 | < 0.5 | < 12% |

### Reglas de diversificacion
- Max 2 estrategias por activo
- Max 3 estrategias por estilo (trend-following o mean-reversion)
- Min 1 estrategia de cada estilo
- Correlacion entre cualquier par < 0.5
- DD combinado maximo del portfolio: 12%

### Ajuste de riesgo por tamaño del portfolio

| Estrategias | Riesgo por trade | Riesgo max dia |
|-------------|-----------------|----------------|
| 3 | 1.0% | 3% |
| 4 | 0.9% | 3.6% |
| 5 | 0.8% | 4% |
| 6+ | 0.6% | 3.6% |
| 8 | 0.5% | 4% |

### Proceso de seleccion (automatico)
1. Scoring individual de cada candidata (formula en skill-portfolio-selection.md)
2. Score minimo para considerar: 55/100
3. Algoritmo greedy por score descendente
4. Verificacion de correlacion, DD combinado y diversificacion
5. INCLUIR / ESPERA / DESCARTAR — todo automatico

Criterios completos en: docs\skills\skill-portfolio-selection.md

---

## 9. CONFIGURACION TECNICA ESTANDAR

### Comisiones obligatorias en TODOS los builds y retests

| Activo | Spread | Comision | Slippage |
|--------|--------|----------|---------|
| EUR/USD | 0.5 pips | 7 USD/lote | 0.5 pips |
| XAU/USD | 30 pips | 7 USD/lote | 2 pips |

### Periodos de datos

| Periodo | Fechas | Uso |
|---------|--------|-----|
| In-Sample (IS) | 2003.05.05 a 2020.12.31 | Builder y Evaluation Gate |
| Out-of-Sample (OOS) | 2021.01.01 a fecha actual | Retester, paso 12b, WFO |

CRITICO: Los datos OOS son intocables hasta el Retester.
Nunca usar datos OOS en el Builder.

### Reglas de riesgo invariables
- Riesgo por trade: 1% (ajustable por portfolio)
- Max trades por dia: 2
- Sesion: 08:00 a 20:00
- Ratio TP/SL minimo: 2:1
- Capital: 25.000 USD

---

## 10. PROP FIRM PRINCIPAL Y ALTERNATIVAS

### FTMO 2-Step (principal)

| Regla | Valor oficial | Margen operativo |
|-------|---------------|-----------------|
| Daily Loss Limit | 5% dinamico | 3% (750$ en cuenta 25k) |
| Max Drawdown | 10% dinamico | 7% (1.750$ en cuenta 25k) |
| Dias minimos | 4 dias | Sin maximo |
| Objetivo Fase 1 | +10% | 2.500$ |
| Objetivo Fase 2 | +5% | 1.250$ |

Puntos criticos:
- Daily Loss DINAMICO — recalculo medianoche hora Praga
- Max DD DINAMICO y SOLO SUBE (nunca baja)
- Sin Regla del Mejor Dia en 2-Step
- Dias de trading: posicion de 3 dias = 1 dia contado

### Alternativas

| Prop Firm | Tipo | DD | Split | Estado |
|-----------|------|----|-------|--------|
| E8 | 2-Step | 8% est. | 80% | Alternativa Forex |
| TFT | 1-Step | 6% din. | 75% | Alternativa Forex |
| Apex | Futuros | Variable | Variable | Pendiente datos CME |
| MFF | Futuros | Variable | Variable | Pendiente datos CME |

---

## 11. PIPELINE COMPLETO SIN INTERVENCION HUMANA

```
Fase 1 — Preparacion:
data-manager (verifica datos)
→ market-selector (selecciona activo)
→ market-analyst (configura Builder libre)

Fase 2 — Build (24-48 horas):
SQ Builder libre — paleta completa +100 indicadores
→ 1000+ candidatas en databank

Fase 3 — Evaluation Gate automatico:
evaluator-assistant + orchestrator
→ ~200-300 candidatas pasan

Fase 4 — Validacion automatica:
sq-specialist (Retester)
→ orchestrator (paso 12b)
→ sq-specialist (WFO)
→ orchestrator (dictamen WFO)
→ ~5-15 estrategias aprobadas

Fase 5 — Portfolio automatico:
correlation-analyst
→ ~3-10 incluidas en portfolio

Fase 6 — Produccion:
export-specialist (exporta a MT5)
→ FORWARD TEST EN DEMO (UNICA INTERVENCION HUMANA — 2 semanas)
→ Challenge en prop firm
→ performance-monitor (monitoreo continuo)
```

---

## 12. REGLAS INQUEBRANTABLES

1. SQ decide la logica de entrada — nunca el humano
2. Los numeros deciden — nunca la intuicion
3. Sin segunda oportunidad para estrategias descartadas
4. Comisiones reales FTMO en todos los builds y retests
5. H1 como temporalidad principal — M15 descartado formalmente
6. Ratio TP/SL minimo 2:1 en todos los builds
7. Riesgo 1% por trade (ajustable por portfolio)
8. Max 2 trades por dia
9. Datos OOS nunca en el Builder
10. Mismas comisiones en Builder y Retester
11. Forward test demo obligatorio antes de challenge
12. Portfolio por correlacion no por preferencia
13. CLAUDE.md no se modifica sin consenso

---

## 13. ROADMAP POR CAPAS

| Capa | Estado | Criterio de entrada | Descripcion |
|------|--------|---------------------|-------------|
| 0 | EN CURSO | — | Pipeline manual, Builder libre, primer build H1 |
| 1 | PENDIENTE | 3 estrategias aprobadas | 2 agentes nuevos, GBP/USD y USD/JPY |
| 2 | PENDIENTE | 5+ estrategias aprobadas | N8N + API Anthropic + semi-autonomo |
| 3 | PENDIENTE | Sistema estable | SQ Remote Control + MT5 + multi-firm |
| 4 | PENDIENTE | Sistema maduro | Portfolio 10+ estrategias, escalado |

Detalle en: docs\roadmap-v2.md

---

## 14. SIGUIENTE ACCION CONCRETA

**Estado:** Build 8 corriendo (enfoque anterior — referencia comparativa).
**Proximo hito:** Lanzar Build 9 con Builder libre.

### Paso 1 — Cuando Build 8 termine
1. Anotar en TICKET-001 evaluation-log.md:
   - Numero de candidatas generadas
   - PF maximo del databank
   - DD maximo del databank
   - Trades promedio por candidata
2. Invocar evaluator-assistant con los resultados
3. orchestrator aplica criterios de skill-evaluation-auto.md
4. Documentar resultado como referencia del enfoque anterior

### Paso 2 — Lanzar Build 9 (Builder libre)
1. data-manager verifica datos actualizados
2. market-selector confirma activo (EUR/USD esperado)
3. market-analyst configura Builder libre segun skill-builder-libre.md
4. Verificar paleta completa activada, Monte Carlo activado
5. Lanzar en modo continuo: Start again when finished ACTIVADO
6. Dejar correr minimo 48 horas

### Paso 3 — Evaluation Gate automatico (tras Build 9)
1. orchestrator aplica criterios de skill-evaluation-auto.md
2. Sin intervencion humana en el filtrado
3. Las candidatas que pasan van al Retester
4. Los numeros deciden — no el humano

**Objetivo de Build 9:** generar las primeras candidatas
del nuevo enfoque. El portfolio minimo requiere 3 estrategias
no correlacionadas aprobadas por el WFO.
