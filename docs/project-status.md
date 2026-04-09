# Project Status — TradingLab
Ultima actualizacion: Abril 2026

---

## 1. RESUMEN DEL PROYECTO

**Objetivo:** Desarrollar estrategias de trading algoritmico robustas
y compatibles con empresas de fondeo (prop firms), usando StrategyQuant
y un sistema de agentes basado en Claude Code.

**Stack:**
| Herramienta      | Rol                                       |
|------------------|-------------------------------------------|
| StrategyQuant X  | Generar, testar y optimizar estrategias   |
| Claude Code      | Agentes, organizacion y documentacion     |
| Antigravity      | Editor de archivos del proyecto           |
| Obsidian         | Base de conocimiento y journal            |
| Git              | Control de versiones del proyecto         |
| Windows CMD      | Terminal para comandos y Claude Code      |

**Prop firm objetivo:** FTMO 2-Step — cuenta de 25.000$
- Fase 1: ganar +10% (2.500$) sin violar limites de riesgo
- Fase 2: ganar +5% (1.250$) con mismos limites
- Cuenta fondeada: 80% profit split, escalable al 90%

---

## 2. ESTADO ACTUAL

- Reconstruccion completa en nuevo dispositivo
- Todos los archivos base creados:
  - CLAUDE.md (constitucion del proyecto)
  - docs\funding-rules.md
  - docs\sq-workflow.md
  - docs\decision-rules.md
  - docs\project-constitution.md
  - docs\roadmap-v2.md
  - 4 agentes en agents\
  - 10 skills en docs\skills\
- **Siguiente paso:** generar primera hipotesis
  y lanzar primer build H1 con comisiones reales

---

## 3. HISTORIAL DE BUILDS (dispositivo anterior)

| Build   | Config                        | Resultado                                      | Decision   |
|---------|-------------------------------|------------------------------------------------|------------|
| Build 1-2 | LARB M15               | Logica asiatica no nativa en SQ                | DESCARTADO |
| Build 3   | EMACross-ADX M15       | Filtros mal configurados                       | DESCARTADO |
| Build 4   | EMACross-ADX M15 sin comisiones | 6 candidatas PF 1.53-1.70 — Retester negativo con comisiones | DESCARTADO |
| Build 5   | EMACross-ADX M15 con comisiones | PF max 1.27 — edge insuficiente en M15     | DESCARTADO |
| Build 6   | NBARBreakout-RSI M15 con comisiones | PF max 1.18 — M15 con comisiones inviable | REVISAR — cambio a H1 |
| Build 7   | NBARBreakout-RSI H1    | Resultado desconocido (build en curso en dispositivo anterior) | PENDIENTE |

**Aprendizaje clave:** M15 descartado como temporalidad principal.
Las comisiones reales FTMO eliminan el edge en estrategias de baja
frecuencia en M15. H1 adoptado como temporalidad principal.

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
- NOTA: 1 pip en XAU/USD = 0.01 USD/oz

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

---

## 5. REGLAS FTMO 2-STEP CRITICAS

| Regla                    | Valor oficial | Margen operativo recomendado |
|--------------------------|---------------|------------------------------|
| Daily Loss Limit         | 5% dinamico   | 3% (750$ en cuenta 25k)      |
| Max Drawdown             | 10% dinamico  | 7% (1.750$ en cuenta 25k)    |
| Dias minimos de trading  | 4 dias        | No hay maximo                |
| Objetivo Fase 1          | +10%          | 2.500$ en cuenta 25k         |
| Objetivo Fase 2          | +5%           | 1.250$ en cuenta 25k         |

**Puntos criticos:**
- Daily Loss Limit es DINAMICO — se recalcula cada medianoche (hora Praga)
- Max Drawdown es DINAMICO y SOLO SUBE (nunca baja)
- Daily Loss incluye posiciones abiertas, comisiones y swaps en tiempo real
- Dias de trading: si una posicion dura 3 dias solo cuenta como 1 dia
- Sin Regla del Mejor Dia en 2-Step — ventaja para EAs con alta volatilidad puntual

---

## 6. AGENTES Y SKILLS

### 4 Agentes del sistema

| Agente              | Rol                                                      |
|---------------------|----------------------------------------------------------|
| market-analyst      | Investiga mercados y genera hipotesis                    |
| funding-specialist  | Evalua compatibilidad con FTMO 2-Step                    |
| sq-specialist       | Convierte hipotesis en configuraciones de SQ             |
| orchestrator        | Decide que avanza, mantiene documentacion actualizada    |

### 10 Skills en docs\skills\

| Skill                         | Funcion                                      |
|-------------------------------|----------------------------------------------|
| skill-claude-sessions.md      | Gestion de sesiones con Claude Code          |
| skill-ftmo-rules.md           | Reglas FTMO resumidas para consulta rapida   |
| skill-ftmo-simulation.md      | Simulacion de challenge FTMO                 |
| skill-hypothesis-design.md    | Formato y proceso de diseno de hipotesis     |
| skill-market-context.md       | Analisis de contexto de mercado              |
| skill-optimizer.md            | Configuracion del Optimizer y WFO            |
| skill-precbuild-checklist.md  | Checklist obligatorio antes de lanzar Builder|
| skill-results-analysis.md     | Analisis de resultados del Builder           |
| skill-retester.md             | Configuracion y uso del Retester             |
| skill-sq-builder.md           | Configuracion del Builder en SQ              |

---

## 7. REGLAS INQUEBRANTABLES

1. **Nunca OOS en Builder** — los datos 2021-2026 son exclusivos del Retester
2. **Decision humana** en Evaluation Gate y Aprobacion final — ningun agente aprueba solo
3. **Riesgo 1% siempre** — sin excepciones por conviccion ni por racha positiva
4. **Comisiones FTMO en todos los builds** — sin comisiones los resultados son irreales
5. **H1 como temporalidad principal** — M15 descartado formalmente tras Builds 1-6
6. **Ratio TP/SL minimo 2:1 siempre** — por debajo no supera el calculo de viabilidad FTMO
7. **Ningun build sin hipotesis previa** documentada en research\strategy-hypotheses\
8. **CLAUDE.md no se modifica sin consenso** — es la constitucion del proyecto

---

## 8. SIGUIENTE ACCION CONCRETA

En orden de ejecucion:

1. **Verificar datos EUR/USD en SQ Gestor de datos**
   - Confirmar que los datos historicos estan importados y verificados
   - Confirmar periodo disponible (minimo 2003-2020)

2. **Invocar market-analyst para primera hipotesis H1**
   - Mercado: EUR/USD
   - Temporalidad: H1
   - Estilos a explorar: Trend-following o Mean Reversion

3. **Invocar funding-specialist para validar la hipotesis**
   - Verificar compatibilidad teorica con FTMO 2-Step
   - Confirmar que el estilo no esta en la lista de prohibidos

4. **Invocar sq-specialist para configuracion del Builder**
   - Usar skill-precbuild-checklist.md obligatoriamente
   - Comisiones EUR/USD: 0.5 pips + 7 USD/lote + 0.5 pip
   - In-sample: 2003-2020 exclusivamente

5. **Lanzar primer build H1 con comisiones reales**
   - Guardar resultados en results\raw\build-results\
   - Aplicar Evaluation Gate antes de pasar a Retester
