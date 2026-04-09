# Project Status — TradingLab
Ultima actualizacion: 2026-04-09

---

## 1. RESUMEN DEL PROYECTO

**Objetivo final:** Automatizacion total del pipeline de trading algoritmico —
desde el analisis de mercados hasta la operacion autonoma en cuentas de fondeo
de multiples prop firms.

**Vision:** Multi-prop firm, multi-activo, multi-cuenta.
Sistema capaz de operar en paralelo en FTMO (Forex), Apex/MFF/TopStep (Futuros)
con gestion de portfolio consolidada, reporting automatico y alertas en tiempo real.

**Stack de herramientas:**

| Herramienta      | Rol                                              |
|------------------|--------------------------------------------------|
| StrategyQuant X  | Generar, testar y optimizar estrategias          |
| Claude Code      | Agentes, orquestacion, organizacion y docs       |
| Obsidian         | Base de conocimiento y journal de decisiones     |
| Git              | Control de versiones del proyecto                |
| N8N (futuro)     | Automatizacion del pipeline — Capa 2             |
| Telegram/Discord | Notificaciones y control remoto — Capa 2         |
| MT5              | Ejecucion de EAs en cuentas de fondeo — Capa 3   |
| Google Sheets    | Reporting consolidado — Capa 2/3                 |

**Prop firm principal:** FTMO 2-Step — cuenta objetivo 25.000$
- Fase 1: +10% (2.500$) sin violar limites de riesgo
- Fase 2: +5% (1.250$) con mismos limites
- Fondeada: 80% profit split, escalable al 90%

---

## 2. ESTADO ACTUAL

**Situacion:** Reconstruccion completa en nuevo dispositivo completada.
El sistema de agentes y skills esta operativo y listo para el primer ciclo completo.

**Documentacion base:**
- CLAUDE.md — constitucion del proyecto
- docs\funding-rules.md
- docs\sq-workflow.md
- docs\decision-rules.md
- docs\project-constitution.md
- docs\roadmap-v2.md
- docs\project-status.md (este archivo)

**Agentes activos: 6**
- market-selector
- market-analyst
- propfirm-analyst
- funding-specialist
- sq-specialist
- orchestrator

**Skills operativas: 11** (en docs\skills\)

**Pipeline:** Completamente documentado y listo para ejecutar.

**Siguiente paso inmediato:** Verificar datos en SQ y lanzar
el primer ciclo completo de agentes para primer build H1.

---

## 3. HISTORIAL DE BUILDS (dispositivo anterior)

| Build     | Config                              | Resultado                                              | Decision              |
|-----------|-------------------------------------|--------------------------------------------------------|-----------------------|
| Build 1-2 | LARB M15                            | Logica asiatica no nativa en SQ                        | DESCARTADO            |
| Build 3   | EMACross-ADX M15                    | Filtros mal configurados                               | DESCARTADO            |
| Build 4   | EMACross-ADX M15 sin comisiones     | 6 candidatas PF 1.53-1.70 — Retester negativo          | DESCARTADO            |
| Build 5   | EMACross-ADX M15 con comisiones     | PF max 1.27 — edge insuficiente en M15                 | DESCARTADO            |
| Build 6   | NBARBreakout-RSI M15 con comisiones | PF max 1.18 — M15 con comisiones inviable              | REVISAR — cambio a H1 |
| Build 7   | NBARBreakout-RSI H1                 | Resultado desconocido — build en dispositivo anterior  | PENDIENTE             |

**Aprendizaje clave:** M15 descartado como temporalidad principal.
Las comisiones reales FTMO (0.5 pips + 7 USD/lote + 0.5 pip) eliminan
el edge en estrategias de baja frecuencia en M15.
H1 adoptado formalmente como temporalidad principal.
Si se prueba M15 en el futuro: minimo 15+ trades/mes como hipotesis.

---

## 4. CONFIGURACION TECNICA ESTANDAR

**Tipo de estrategia:** Simple strategy
**Temporalidad principal:** H1
**Mercados activos:** EUR/USD y XAU/USD

### Comisiones obligatorias (en TODOS los builds y retests)

**EUR/USD y pares Forex:**
- Desviacion (spread): 0.5 pips
- Comision: 7 USD por lote completo (round turn)
- Deslizamiento: 0.5 pips

**XAU/USD (Oro spot):**
- Desviacion (spread): 30 pips
- Comision: 7 USD por lote completo (round turn)
- Deslizamiento: 2 pips
- NOTA: 1 pip en XAU/USD = 0.01 USD/oz — spread real FTMO aprox 30 USD/lote

### Periodos de datos
- In-sample: 2003-2020
- Out-of-sample (OOS): 2021-fecha actual
- CRITICO: el periodo OOS es intocable hasta el Retester

### Opciones geneticas del Builder
- Generaciones: 20
- Por isla: 50
- Islas: 4

### Filtros del Builder
- PF > 0.8
- Trades > 8
- RatioDD > 0.5

### Gestion de riesgo
- Riesgo por trade: 1%
- Max trades por dia: 2 (H1)
- Sesion: 08:00 a 20:00
- Ratio TP/SL minimo: 2:1

---

## 5. PROP FIRMS ANALIZADAS

### Principal — Forex
| Prop Firm  | Tipo     | Activos         | DD Limite  | Objetivo    | Split | Estado     |
|------------|----------|-----------------|------------|-------------|-------|------------|
| FTMO       | 2-Step   | Forex/Oro/Idx   | 10% din.   | 10%/5%      | 80%   | PRINCIPAL  |
| E8         | 2-Step   | Forex/Oro       | 8% est.    | 8%          | 80%   | ALTERNATIVA|
| TFT        | 1-Step   | Forex/Oro       | 6% din.    | 10%         | 75%   | ALTERNATIVA|

### Futuras — Futuros CME (pendiente de datos)
| Prop Firm  | Tipo     | Activos         | Estado              |
|------------|----------|-----------------|---------------------|
| Apex       | Mensual  | NQ, GC, ES      | Pendiente datos CME |
| MFF        | Mensual  | NQ, GC, ES      | Pendiente datos CME |
| TopStep    | Mensual  | NQ, ES          | Pendiente datos CME |

**Compatibilidad de activos:**
| Activo    | FTMO | E8 | TFT | MFF | TopStep | Apex |
|-----------|------|----|-----|-----|---------|------|
| EUR/USD   | SI   | SI | SI  | NO  | NO      | NO   |
| XAU/USD   | SI   | SI | SI  | NO  | NO      | NO   |
| GC        | NO   | NO | NO  | SI  | SI      | SI   |
| NQ/US100  | SI*  | SI | SI  | SI  | SI      | SI   |

*FTMO: NQ como indice spot (US100), no como futuro CME

---

## 6. AGENTES Y SKILLS

### 6 Agentes activos

| Agente              | Rol                                                           |
|---------------------|---------------------------------------------------------------|
| market-selector     | Selecciona el activo optimo antes de cada hipotesis           |
| market-analyst      | Investiga mercados y genera hipotesis de estrategias          |
| propfirm-analyst    | Analiza y compara prop firms por activo y estrategia          |
| funding-specialist  | Evalua compatibilidad con reglas de la prop firm elegida      |
| sq-specialist       | Convierte hipotesis en configuraciones SQ (Builder/Retester)  |
| orchestrator        | Coordina el pipeline, decide y mantiene el proyecto al dia    |

### 4 Agentes planificados (Capa 1 — tras 3 estrategias aprobadas)

| Agente              | Rol                                                           |
|---------------------|---------------------------------------------------------------|
| technical-analyst   | Analisis tecnico avanzado — patrones, soportes, resistencias  |
| correlation-analyst | Correlaciones entre activos del portfolio                     |
| risk-manager        | Gestion de riesgo del portfolio completo                      |
| news-researcher     | Contexto macro y deteccion de periodos anomalos               |

### 11 Skills en docs\skills\

| Skill                         | Funcion                                          |
|-------------------------------|--------------------------------------------------|
| skill-claude-sessions.md      | Gestion de sesiones con Claude Code              |
| skill-ftmo-rules.md           | Reglas FTMO resumidas para consulta rapida       |
| skill-ftmo-simulation.md      | Simulacion de challenge FTMO                     |
| skill-hypothesis-design.md    | Formato y proceso de diseno de hipotesis         |
| skill-market-context.md       | Analisis de contexto de mercado                  |
| skill-optimizer.md            | Configuracion del Optimizer y WFO                |
| skill-precbuild-checklist.md  | Checklist obligatorio antes de lanzar Builder    |
| skill-results-analysis.md     | Analisis de resultados del Builder               |
| skill-retester.md             | Configuracion y uso del Retester                 |
| skill-sq-builder.md           | Configuracion del Builder en SQ                  |
| skill-propfirms-comparison.md | Comparativa detallada de prop firms              |

---

## 7. REGLAS INQUEBRANTABLES

1. **Nunca OOS en Builder** — los datos 2021-2026 son exclusivos del Retester
2. **Decision humana** en Evaluation Gate y Aprobacion final — ningun agente aprueba solo
3. **Riesgo 1% siempre** — sin excepciones por conviccion ni por racha positiva
4. **Comisiones FTMO en todos los builds** — sin comisiones los resultados son irreales
5. **H1 como temporalidad principal** — M15 descartado formalmente tras Builds 1-6
6. **Ratio TP/SL minimo 2:1 siempre** — por debajo no supera el calculo de viabilidad FTMO
7. **market-selector antes de cualquier hipotesis nueva** — sin excepcion
8. **Ningun build sin hipotesis previa** documentada en research\strategy-hypotheses\
9. **CLAUDE.md no se modifica sin consenso** — es la constitucion del proyecto

---

## 8. REGLAS FTMO 2-STEP CRITICAS

| Regla                    | Valor oficial | Margen operativo recomendado |
|--------------------------|---------------|------------------------------|
| Daily Loss Limit         | 5% dinamico   | 3% (750$ en cuenta 25k)      |
| Max Drawdown             | 10% dinamico  | 7% (1.750$ en cuenta 25k)    |
| Dias minimos de trading  | 4 dias        | No hay maximo                |
| Objetivo Fase 1          | +10%          | 2.500$ en cuenta 25k         |
| Objetivo Fase 2          | +5%           | 1.250$ en cuenta 25k         |

**Puntos criticos:**
- Daily Loss Limit es DINAMICO — se recalcula cada medianoche hora Praga
- Max Drawdown es DINAMICO y SOLO SUBE (nunca baja)
- Daily Loss incluye posiciones abiertas, comisiones y swaps en tiempo real
- Dias de trading: si una posicion dura 3 dias solo cuenta como 1 dia
- Sin Regla del Mejor Dia en 2-Step — ventaja para EAs con alta volatilidad puntual

---

## 9. ROADMAP POR CAPAS

| Capa | Estado     | Criterio de entrada              | Descripcion                            |
|------|------------|----------------------------------|----------------------------------------|
| 0    | EN CURSO   | —                                | Pipeline manual, primer build H1       |
| 1    | PENDIENTE  | 3 estrategias aprobadas          | 4 nuevos agentes, GBP/USD y USD/JPY   |
| 2    | PENDIENTE  | 5+ estrategias aprobadas         | N8N + API Anthropic + semi-autonomo   |
| 3    | PENDIENTE  | Sistema estable                  | SQ Remote Control + MT5 + multi-firm  |
| 4    | PENDIENTE  | Sistema maduro                   | Portfolio 10+ estrategias, escalado   |

**Regla fundamental:** Nunca expandir antes de tener el proceso anterior estable.
La automatizacion sin estrategias validadas = automatizar perdidas.

---

## 10. SIGUIENTE ACCION CONCRETA

En orden estricto de ejecucion:

1. **Verificar datos EUR/USD en SQ — Gestor de datos**
   - Confirmar datos historicos importados: EUR/USD M1 desde 2003
   - Confirmar que el periodo 2003-2020 esta completo y sin huecos
   - Confirmar que el periodo 2021-2026 esta disponible para OOS

2. **Invocar market-selector para analisis inicial**
   - Confirmar EUR/USD como activo principal
   - Confirmar XAU/USD como activo secundario
   - Actualizar scoring si hay cambios en datos o reglas de prop firms

3. **Invocar market-analyst para primera hipotesis H1**
   - Mercado: EUR/USD
   - Temporalidad: H1
   - Estilos a explorar: Trend-following o Mean Reversion

4. **Invocar propfirm-analyst para prop firm optima**
   - Evaluar hipotesis vs FTMO, E8 y TFT
   - Confirmar prop firm principal para este build

5. **Invocar funding-specialist para validacion**
   - Verificar compatibilidad teorica con FTMO 2-Step
   - Confirmar que el estilo no esta en lista de prohibidos

6. **Invocar sq-specialist para configuracion del Builder**
   - Usar skill-precbuild-checklist.md obligatoriamente
   - Comisiones EUR/USD: 0.5 pips + 7 USD/lote + 0.5 pip
   - In-sample: 2003-2020 exclusivamente

7. **Lanzar primer build H1 con comisiones reales**
   - Guardar resultados en results\raw\build-results\
   - Aplicar Evaluation Gate antes de pasar al Retester
