# Project Status — TradingLab
Ultima actualizacion: 2026-04-21

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
| 3 | Portfolio por correlacion automatica | No por preferencia ni intuicion del humano |
| 4 | Unica intervencion humana: forward test demo | En ningun otro momento el humano decide nada |

### Lo que SQ decide (logica de entrada)
- Que indicadores usar de la paleta completa
- Cuantas condiciones de entrada (1 a 3)
- Que combinaciones de señales
- Que parametros dentro de los rangos
- Direccion de operaciones (long, short o ambas)

### Lo que el humano define UNICAMENTE (restricciones de riesgo)
- Comisiones reales de la prop firm objetivo
- Ratio TP/SL minimo 2:1
- Riesgo 1% por trade
- Max 2 trades por dia
- Sesion 08:00 a 20:00

### Lo que el pipeline filtra (todo automatico)
- Sobreajuste — via Retester, paso 12b y WFO
- Redundancia — via correlation-analyst
- Incompatibilidad de portfolio — via DD combinado y correlacion

---

## 2. ESTADO ACTUAL

**Fecha:** 2026-04-27
**Situacion:** Build 10 completado (4+ dias corriendo en alber).
Build 11 pendiente de lanzar en alber con spread corregido a 60 pips.
Scripts Python operativos y probados en ivano.
Telegram bot activo (@tradinglab_monitor_bot).
ChromaDB indexado con 90 chunks.
Planning maestro: ~145/156 tareas completadas.
Proxima accion: lanzar Build 11 en alber con spread 60 pips.

### Planning Maestro

| Metrica | Valor |
|---------|-------|
| Total tareas | 156 |
| Completadas | ~145 |
| Fase 0 | COMPLETA |
| Fases 1-2 | COMPLETAS |
| Fases 3-4 | EN CURSO |
| Fases 5-6 | PENDIENTES (requieren VPS + estrategia aprobada) |
| Fase 7 | COMPLETA |
| Fase 10 | EN CURSO |

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
**Tickets activos:** 1 — TICKET-002-BUILD-9-XAUUSD en fase build-pending
**Portfolio actual:** 0 estrategias (objetivo minimo: 3)

---

## 3. AGENTES ACTIVOS (11)

| # | Agente | Rol actual |
|---|--------|------------|
| 1 | market-selector | Prioriza activos por scoring numerico automatico — 30+ activos disponibles |
| 2 | market-analyst | Configura parametros del Builder libre — NO genera hipotesis (ROL REDISEÑADO) |
| 3 | propfirm-analyst | Analiza y compara prop firms por activo y estrategia automaticamente |
| 4 | funding-specialist | Evalua compatibilidad con reglas de la prop firm elegida |
| 5 | sq-specialist | Configura SQ Builder, Retester y Optimizer |
| 6 | evaluator-assistant | Genera informes estructurados del Evaluation Gate |
| 7 | correlation-analyst | Gestiona automaticamente la composicion del portfolio (ACTIVADO) |
| 8 | export-specialist | Exporta estrategias aprobadas de SQ a MQL5/MT5 |
| 9 | performance-monitor | Monitorea EAs en produccion y alerta sobre riesgo |
| 10 | data-manager | Verifica y gestiona datos historicos en SQ para todos los activos |
| 11 | orchestrator | Coordina el pipeline y aplica criterios automaticos — nunca intuicion |

### Cambios del rediseño 2026-04-11

- **market-analyst rediseñado:** antes generaba hipotesis manuales (causa de los 8 builds fallidos). Ahora solo configura el terreno de busqueda. NUNCA propone logicas de entrada.
- **correlation-analyst activado:** antes era un agente planificado. Ahora es operativo y gestiona el portfolio automaticamente.
- **market-selector expandido:** ahora cubre 30+ activos con scoring numerico. El humano no elige el activo.
- **11 agentes activos** (antes 10).

### Agentes planificados (post Capa 1)
- risk-manager — gestion de riesgo avanzada del portfolio
- news-researcher — contexto macro y deteccion de periodos anomalos

---

## 4. SKILLS OPERATIVAS (24)

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
| skill-gt-score-calc.md | GT-Score: metrica avanzada de calidad (Capa 3+) |
| skill-reactive-sim.md | Market Impact Simulator — escalabilidad de lotes |
| skill-hypothesis-design.md | OBSOLETA — referencia historica solamente |

## 4b. AGENTES ADICIONALES (Fase 4)

| Agente | Proposito |
|--------|-----------|
| propfirm-regulatory-watcher.md | Monitoreo semanal de cambios en T&C de prop firms |
| account-recovery-manager.md | Recuperacion adaptativa en drawdown (2 niveles) |
| scaling-manager.md | Gestion del scaling FTMO +25% cada 4 meses |
| multi-account-orchestrator.md | Coordinacion de multiples cuentas (Capa 4) |

## 4c. SCRIPTS PYTHON

| Script | Proposito |
|--------|-----------|
| build-analyzer.py | Resumen ejecutivo post-build con Ollama |
| knowledge-base.py | Indexacion ChromaDB para consultas semanticas |
| lessons-analyzer.py | Analisis de lecciones con Ollama + reflexion diaria |
| inflation-diagnostic.py | Deteccion de sobreajuste IS/OOS post-WFO |
| strategy-versioning.py | Ciclo de vida y versioning de estrategias |
| vps-health-monitor.py | Monitoreo de salud del VPS en produccion |

## 4d. LIBRERIAS MQL5

| Archivo | Proposito |
|---------|-----------|
| scripts/ftmo-timezone-sync.mq5 | Sincronizacion timezone Prague para EAs |
| include/ConnectionMonitor.mqh | Monitoreo de conexion reutilizable en EAs |

## 4e. CI/CD (GitHub Actions)

| Workflow | Proposito |
|----------|-----------|
| validate-skills.yml | Verificacion de formato de docs y agentes en cada push |
| pipeline-check.yml | Alerta si los criterios numericos se relajan en documentacion |

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
| Build 8 | Hipotesis humana | TrendFollowing EURUSD H1 EMA50+ADX | EN EJECUCION en dispositivo alber — ultimo build con sesgo humano | EN CURSO |
| Build 9 | Builder libre | XAUUSD H1 — Paleta completa — Comisiones FTMO reales | EN CURSO — Ciclo 1 iniciado 2026-04-15 — TICKET-002 | EN CURSO |
| Build 10 | Builder libre | XAUUSD H1 — datos corregidos, instrumentos FTMO reales | EN CURSO desde 2026-04-20 — Primer build con configuracion validada Fase 0 | EN CURSO |

### Aprendizajes acumulados

- **M15 descartado formalmente:** comisiones reales FTMO eliminan el edge en M15
- **Hipotesis humana descartada:** 8 builds fallidos por restriccion del espacio de busqueda
- **H1 adoptado** como temporalidad principal para todos los activos
- **Builder libre es el camino:** SQ explora lo que el humano nunca consideraria
- **Multi-activo desde Build 9:** market-selector decide el activo por scoring, no el humano

---

## 6. UNIVERSO DE MERCADOS (30+ activos)

El market-selector prioriza todos los activos por scoring numerico.
El humano no elige el activo — los numeros deciden.

### Forex Majors (Dukascopy M1 desde 2003)

| Activo | Spread FTMO | Comision | Slippage | Estado |
|--------|-------------|----------|----------|--------|
| EUR/USD | 0.5 pips | 7 USD/lote | 0.5 pips | ACTIVO |
| GBP/USD | 0.8 pips | 7 USD/lote | 0.5 pips | PENDIENTE |
| USD/JPY | 0.5 pips | 7 USD/lote | 0.5 pips | PENDIENTE |
| USD/CHF | 0.8 pips | 7 USD/lote | 0.5 pips | PENDIENTE |
| AUD/USD | 0.6 pips | 7 USD/lote | 0.5 pips | PENDIENTE |
| NZD/USD | 1.0 pips | 7 USD/lote | 0.5 pips | PENDIENTE |
| USD/CAD | 0.8 pips | 7 USD/lote | 0.5 pips | PENDIENTE |

### Forex Crosses (Dukascopy M1 desde 2003)

| Activo | Spread FTMO | Comision | Slippage | Estado |
|--------|-------------|----------|----------|--------|
| EUR/GBP | 0.8 pips | 7 USD/lote | 0.8 pips | PENDIENTE |
| EUR/JPY | 1.0 pips | 7 USD/lote | 0.8 pips | PENDIENTE |
| GBP/JPY | 1.5 pips | 7 USD/lote | 0.8 pips | PENDIENTE |
| EUR/AUD | 1.5 pips | 7 USD/lote | 0.8 pips | PENDIENTE |
| EUR/CHF | 1.0 pips | 7 USD/lote | 0.8 pips | PENDIENTE |
| AUD/JPY | 1.0 pips | 7 USD/lote | 0.8 pips | PENDIENTE |
| GBP/AUD | 2.0 pips | 7 USD/lote | 0.8 pips | PENDIENTE |
| CAD/JPY | 1.2 pips | 7 USD/lote | 0.8 pips | PENDIENTE |
| NZD/JPY | 1.5 pips | 7 USD/lote | 0.8 pips | PENDIENTE |

### Metales (Dukascopy M1 desde 2003)

| Activo | Spread FTMO | Comision | Slippage | Estado |
|--------|-------------|----------|----------|--------|
| XAU/USD | 30 pips | 7 USD/lote | 2 pips | ACTIVO |
| XAG/USD | 3 pips | 7 USD/lote | 1 pip | PENDIENTE |

### Indices (Dukascopy M1 disponible)

| Activo | Spread FTMO | Estado |
|--------|-------------|--------|
| US30 (Dow) | 2.0 pts | PENDIENTE — verificar comisiones |
| US500 (S&P) | 0.5 pts | PENDIENTE — verificar comisiones |
| NAS100 (Nasdaq) | 1.5 pts | PENDIENTE — verificar comisiones |
| DE40 (DAX) | 1.5 pts | PENDIENTE — verificar comisiones |
| UK100 (FTSE) | 1.5 pts | PENDIENTE — verificar comisiones |
| JP225 (Nikkei) | 10 pts | PENDIENTE — verificar comisiones |

### Cripto (datos desde 2017-2018)

| Activo | Spread FTMO | Estado |
|--------|-------------|--------|
| BTC/USD | ~20 USD | PENDIENTE — mercado 24/7 |
| ETH/USD | ~2 USD | PENDIENTE — mercado 24/7 |

**CRITICO:** Para indices y cripto verificar comisiones exactas con propfirm-analyst antes de cada build.

### Scoring del market-selector (5 criterios)

| Criterio | Peso | Descripcion |
|----------|------|-------------|
| Compatibilidad prop firms | 25% | Cuantas prop firms permiten el activo |
| Calidad de datos en SQ | 20% | Periodo y completitud de los datos M1 |
| Coste de transaccion | 20% | Spread + comision + slippage vs ATR H1 |
| Volatilidad y oportunidad | 15% | ATR H1 suficiente para ratio 2:1 |
| Diversificacion del portfolio | 20% | Correlacion con activos ya activos |

Prioridad alta: score >= 70 — lanzar Builder inmediatamente
Prioridad media: score 50-69 — lanzar cuando alta prioridad este en pipeline
Prioridad baja: score < 50 — posponer

---

## 7. BUILDER LIBRE (Build 9+)

### Filosofia
SQ tiene libertad total para explorar millones de combinaciones.
El humano solo define restricciones de riesgo.
El pipeline filtra el sobreajuste automaticamente.
SQ decide la logica. El humano no.

### Parametros geneticos

| Parametro | Antes (Builds 1-8) | Ahora (Build 9+) |
|-----------|-------------------|-----------------|
| Generaciones | 20 | 30 por ciclo continuo |
| Poblacion por isla | 50 | 100 |
| Islas | 4 | 4 |
| Modo | Se paraba solo | Corre indefinido (Start again when finished) |
| Max estrategias | 500 | 1000 |
| Stop generation | Auto | Never |

### Paleta de bloques — COMPLETA SIN RESTRICCIONES

- Todos los grupos activados: tendencia, momentum, volatilidad, precio puro
- Todos los operadores activados
- Indicadores: EMA, SMA, DEMA, HMA, ADX, Aroon, SAR, RSI, Stochastic,
  CCI, MACD, Williams %R, Momentum, ROC, DeMarker, ATR, Bollinger,
  Keltner, Donchian, Standard Deviation, High, Low, Close, Open, HL2, HLC3,
  Highest, Lowest, Range — mas de 100 combinaciones posibles
- Señales predefinidas: cruces, niveles, rupturas, tendencia
- Sin restriccion de indicadores: NINGUNA
- Sin hipotesis previa: NINGUNA

### Filtros del Builder (clasificacion)

| Filtro | Valor |
|--------|-------|
| PF minimo | 1.3 |
| Trades/mes minimo | 6 |
| Ratio Ret/DD minimo | 0.8 |
| Monte Carlo | ACTIVADO |

### Restricciones de riesgo (invariables)

- Comisiones reales de la prop firm objetivo — verificadas antes de cada build
- Riesgo: 1% por trade, capital 25.000 USD
- Max 2 trades por dia, sesion 08:00-20:00
- SL: ATR-based 1.5x a 3.0x
- TP: ATR-based 3.0x a 6.0x, ratio minimo 2:1 sobre SL

### Tiempo de build

- Minimo: 24 horas
- Optimo: 48 horas
- Parar cuando: PF maximo no sube en 6+ horas consecutivas

Configuracion completa en: docs\skills\skill-builder-libre.md

---

## 8. CRITERIOS AUTOMATICOS DEL PIPELINE

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

## 9. OBJETIVO DE PORTFOLIO

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

### Proceso de seleccion (automatico — correlation-analyst)
1. Scoring individual de cada candidata (formula en skill-portfolio-selection.md)
2. Score minimo para considerar: 55/100
3. Algoritmo greedy por score descendente
4. Verificacion de correlacion, DD combinado y diversificacion
5. INCLUIR / ESPERA / DESCARTAR — todo automatico

Criterios completos en: docs\skills\skill-portfolio-selection.md

---

## 10. PROP FIRMS OBJETIVO

| Prop Firm | Tipo | Activos | Estado |
|-----------|------|---------|--------|
| FTMO 2-Step | Forex + Metales + Indices | DD 10% din. | PRINCIPAL |
| E8 Funding | Forex + Metales | DD 8% est. | ALTERNATIVA |
| TFT | Forex + Metales + Indices | DD 6% din. | ALTERNATIVA |
| Apex | Futuros CME | Variable | PENDIENTE datos CME |
| MFF | Futuros CME | Variable | PENDIENTE datos CME |

El propfirm-analyst decide automaticamente que prop firm es optima para cada estrategia y activo. Sin preferencia humana.

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

---

## 11. PIPELINE COMPLETO SIN INTERVENCION HUMANA

```
Fase 1 — Preparacion (automatica):
data-manager (verifica datos de todos los activos)
→ market-selector (scoring numerico — decide activo)
→ market-analyst (configura Builder libre — sin hipotesis)

Fase 2 — Build (humano lanza y para en SQ):
SQ Builder libre — paleta completa +100 indicadores
24-48 horas modo continuo
→ 1000+ candidatas en databank

Fase 3 — Evaluation Gate (automatico):
evaluator-assistant + orchestrator
Criterios numericos — descarte y aprobacion automaticos
→ ~200-300 candidatas pasan

Fase 4 — Validacion (humano lanza en SQ):
sq-specialist (Retester) — humano pulsa inicio
→ orchestrator (paso 12b automatico)
→ sq-specialist (WFO) — humano pulsa inicio
→ orchestrator (dictamen WFO automatico)
→ ~5-15 estrategias aprobadas

Fase 5 — Portfolio (automatico):
correlation-analyst
→ ~3-10 incluidas en portfolio activo

Fase 6 — Produccion:
export-specialist (exporta a MT5)
→ FORWARD TEST EN DEMO (UNICA INTERVENCION HUMANA — 2 semanas)
→ Challenge en prop firm
→ performance-monitor (monitoreo continuo)

Mantenimiento (automatico):
performance-monitor → reportes semanales
correlation-analyst → rebalanceo mensual
Si deterioro → reemplazo automatico
Si portfolio incompleto → nuevo ciclo Builder
```

---

## 12. REGLAS INQUEBRANTABLES

1. SQ decide la logica de entrada — nunca el humano
2. Los numeros deciden — nunca la intuicion
3. Los activos se priorizan por score — no por gusto
4. Sin segunda oportunidad para estrategias descartadas
5. Comisiones reales verificadas antes de cada build
6. H1 como temporalidad para todos los activos — M15 descartado
7. Ratio TP/SL minimo 2:1 en todos los builds
8. Riesgo 1% por trade (ajustable por portfolio)
9. Max 2 trades por dia por estrategia
10. Datos OOS nunca en el Builder
11. Forward test demo obligatorio antes de challenge
12. Portfolio por correlacion y diversificacion — no por preferencia
13. CLAUDE.md no se modifica sin consenso

---

## 13. ROADMAP POR CAPAS

| Capa | Estado | Criterio de entrada | Descripcion |
|------|--------|---------------------|-------------|
| 0 | EN CURSO | — | Pipeline automatico multi-activo, Builder libre, primer build H1 |
| 1 | PENDIENTE | 3 estrategias aprobadas | 2 agentes nuevos, expansion mercados |
| 2 | PENDIENTE | 5+ estrategias aprobadas | N8N + API Anthropic + semi-autonomo |
| 3 | PENDIENTE | Sistema estable | SQ Remote Control + MT5 + multi-firm |
| 4 | PENDIENTE | Sistema maduro | Portfolio 10+ estrategias, escalado |

Detalle en: docs\roadmap-v2.md

---

## 14. SIGUIENTE ACCION CONCRETA

**Estado:** Build 10 completado. Build 11 pendiente con spread corregido a 60 pips.
**Proximo hito:** Lanzar Build 11 en alber (XAUUSD H1, spread 60 pips). Dejar correr 48 horas.

### Paso 1 — Verificar datos disponibles en SQ
1. data-manager verifica que activos tienen datos M1 disponibles en SQ
2. Confirmar periodo: 2003-2020 para IS, 2021-actual para OOS
3. Actualizar inventario de datos por activo

### Paso 2 — market-selector prioriza activos por scoring
1. Aplicar los 5 criterios a todos los activos disponibles
2. Ordenar de mayor a menor score
3. El activo con mayor score recibe el primer ciclo de Builder libre
4. Generar plan de ciclos para los siguientes activos

### Paso 3 — market-analyst configura Builder libre
1. Confirmar activo elegido por market-selector
2. Verificar comisiones exactas con propfirm-analyst
3. Configurar Builder segun skill-builder-libre.md
4. Verificar paleta completa activada, Monte Carlo activado
5. Crear archivo strategyquant\builder\build-9-config.md

### Paso 4 — Lanzar Build 9 en modo continuo
1. Lanzar en SQ con Start again when finished ACTIVADO
2. Dejar correr minimo 48 horas
3. Parar cuando PF maximo no sube en 6+ horas consecutivas
4. orchestrator aplica Evaluation Gate automatico

**Objetivo de Build 9:** generar las primeras candidatas del nuevo enfoque sin sesgo humano.
El portfolio minimo requiere 3 estrategias no correlacionadas aprobadas por el WFO.
El market-selector decide el activo — no el humano.
