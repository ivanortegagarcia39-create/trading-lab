# Skill: Flujo Completo del Pipeline

## Proposito

Define cada puerta del pipeline con sus criterios exactos,
herramientas y ratios esperados. Es la referencia de verdad
cuando hay dudas sobre que puerta aplica un criterio.

Cada puerta tiene un criterio de PASA y un criterio de DESCARTE.
No hay zona intermedia salvo donde se especifica explicitamente.

---

## Cadena completa estimada

```
Builder (1000+) → [P1] → 50 → [P2] → 20 → [P3] → 8
→ [P4] → 4 → [P5] → 2 → [P6] → 1-2 → [P7] → 1
→ [P8] → 1 portfolio → [P9] → challenge
```

Ratio global esperado: ~0.1% de candidatas llegan a produccion.
Si una puerta tiene un ratio muy por debajo del esperado
durante 2+ ciclos → es el cuello de botella del pipeline.

---

## PUERTA 1 — BUILDER FILTER (SQ)

**Herramienta:** SQ Builder — filtros de poblacion
**Cuando:** Durante el build, en tiempo real
**Quien:** SQ de forma automatica

Criterios de supervivencia en SQ:
- PF > 1.3
- Trades/mes > 6
- Ret/DD > 0.8 (Retorno anualizado / Drawdown maximo)

**Ratio esperado:** ~5% pasan (50 de 1000)

Nota: estos filtros son permisivos por diseno.
SQ filtra solo lo mas evidente — el resto lo filtra el pipeline Python.
Ajustar solo si la tasa es < 1% (demasiado restrictivo) o > 20% (muy laxo).

---

## PUERTA 2 — EVALUATION GATE (Python)

**Herramienta:** scripts/evaluator-assistant.py
**Cuando:** Despues del build — automatico
**Quien:** orchestrator via pipeline-runner.py

Criterios — todos deben cumplirse:

| Criterio | Valor | Timeframe |
|----------|-------|-----------|
| Total trades | >= 120 | H1 |
| Total trades | >= 50 | H4 |
| Total trades | >= 180 | M30 |
| Total trades | >= 300 | M15 |
| Win Rate | >= 38% | todos |
| DD maximo IS | <= 7% | todos |
| Sharpe estimado IS | >= 0.5 | todos |
| DD maximo en año individual | <= 8% | todos |
| PF post-swaps | >= 80% del PF pre-swaps | todos |
| Triple swap miercoles | <= 15% del profit total | todos |

Descarte automatico si cualquier criterio falla.
Sin consultar al humano. Sin segunda oportunidad.

**Ratio esperado:** ~40% de los que pasan puerta 1 (~20 de 50)

---

## PUERTA 3 — RETESTER + PASO 12B (SQ + Python)

**Herramienta:** SQ Retester (manual) + orchestrator Python
**Cuando:** Despues del EvalGate — lote completo
**Quien:** sq-specialist ejecuta Retester, orchestrator aplica paso 12b

Configuracion del Retester:
- Datos OOS: 2021-01-01 a fecha actual
- Comisiones: identicas al Builder
- Precision: 1 minute data tick simulation
- Ver skill-retester.md para configuracion completa

Criterios PASO 12B — todos deben cumplirse:
- PF OOS >= 1.3
- Caida PF IS→OOS <= 20%
- DD OOS <= 6.5%
- Trades/mes OOS >= 6
- Caida frecuencia IS→OOS <= 40%

Descarte automatico si cualquier criterio falla.

**Ratio esperado:** ~40% de puerta 2 (~8 de 20)

---

## PUERTA 4 — SPP VALIDATION (SQ / Python)

**Herramienta:** SQ System Parameter Permutation o script Python
**Cuando:** Despues del paso 12b, antes del WFO
**Quien:** sq-specialist

Prueba la sensibilidad a variaciones de parametros ±10%.
Una estrategia robusta no colapsa cuando sus parametros
cambian ligeramente — si colapsa, la "robustez" es ilusoria.

Criterio de descarte:
PF cae > 30% en alguna permutacion de parametros → DESCARTE.

La estrategia depende de parametros exactos que no son
reproducibles en produccion real (slippage, spread variable).

**Ratio esperado:** ~50% de puerta 3 (~4 de 8)

---

## PUERTA 5 — WFO MATRIX (SQ)

**Herramienta:** SQ Walk-Forward Optimization
**Cuando:** Despues del SPP
**Quien:** sq-specialist

Configuracion WFO:
- Minimo 5 ventanas temporales
- IS/OOS ratio: 70/30 tipicamente
- Ver skill-wfo-anchored.md para configuracion

Criterios de APROBACION:
- WFE (Walk-Forward Efficiency) >= 50%
- >= 3 de 5 configuraciones muestran PF > 1.0 en OOS

Catastrophic Veto — descarte si en cualquier ventana:
- PF OOS < 0.8 (estrategia pierde dinero en ese periodo)
- DD OOS > 10%

Criterio de DESCARTE adicional:
- WFE < 40% → descarte directo

Zona gris (40-50% WFE): revisar manualmente con el orchestrator.

**Ratio esperado:** ~50% de puerta 4 (~2 de 4)

---

## PUERTA 6 — STRESS TEST HISTORICO (SQ Retester)

**Herramienta:** SQ Retester con fechas especificas
**Cuando:** Despues del WFO
**Quien:** sq-specialist

Los 5 periodos criticos (skill-stress-test.md):
1. Crisis financiera 2008: 2008-09-01 a 2008-10-31
2. Flash crash CHF 2015: 2015-01-13 a 2015-02-28
3. COVID crash 2020: 2020-02-15 a 2020-04-15
4. Inflacion 2022: 2022-01-01 a 2022-06-30
5. Crisis SVB 2023: 2023-03-01 a 2023-03-31

Criterio: DD < 8% en CADA periodo individual.
Si cualquier periodo supera 8% → DESCARTE AUTOMATICO.

**Ratio esperado:** ~60% de puerta 5 (~1-2 de 2)

---

## PUERTA 7 — MULTIMARKET VALIDATION (SQ Retester)

**Herramienta:** SQ Retester en activos correlacionados
**Cuando:** Despues del Stress Test
**Quien:** sq-specialist

Verifica que la estrategia funciona en al menos un activo
correlacionado con el original — no es un artefacto especifico
de los datos historicos de ese activo en ese periodo.

Activos correlacionados de referencia:
- XAUUSD → probar en XAGUSD o EURUSD (Factor Dolar)
- EURUSD → probar en GBPUSD o AUDUSD
- US500 → probar en US30 o NAS100

Criterio de APROBACION:
PF > 1.0 en al menos 1 de los 2 activos correlacionados probados.

Criterio de DESCARTE:
PF <= 1.0 en todos los activos correlacionados probados.

**Ratio esperado:** ~70% de puerta 6

---

## PUERTA 8 — PORTFOLIO FILTER (Python)

**Herramienta:** scripts/portfolio-builder.py
**Cuando:** Despues de la validacion multimarket
**Quien:** orchestrator automatico

Algoritmo greedy de seleccion:
1. Ordenar por score individual (PF*30 + Sharpe*20 + DD*25 + WR*25)
2. Anadir estrategia de mayor score
3. Verificar: correlacion < 0.5 con las ya incluidas
4. Verificar: DD combinado estimado < 12%
5. Verificar: anti-monocultivo USD (max 2 activos Factor Dolar)
6. Si pasa todo → INCLUIR. Si no → lista de espera.
7. Parar cuando portfolio tiene 3-8 estrategias.

Pesos: HRP simplificado (1/volatilidad proporcional)

**Resultado esperado:** 3-5 estrategias seleccionadas

Ver skill-portfolio-selection.md para criterios completos.

---

## PUERTA 9 — FORWARD TEST (MT5 Demo)

**Herramienta:** MT5 en cuenta demo de la prop firm
**Cuando:** Despues del portfolio y export a MT5
**Quien:** humano (solo verificacion tecnica) + orchestrator (decision)

Duracion: minimo 20 trades ejecutados (sin limite de tiempo).
Ver skill-forward-test.md para criterios numericos completos.

Criterios de PASA — los 3 deben cumplirse:
1. PF demo >= 70% del PF OOS del backtest
2. DD demo <= DD OOS + 30%
3. Minimo 20 trades ejecutados

Criterio de FALLA: cualquiera de los 3 falla → cola de reemplazo.
Decision automatica del orchestrator — no el humano.

**Ratio esperado:** ~70% de las seleccionadas

---

## REFERENCIAS DE CADA PUERTA

| Puerta | Skill de referencia |
|--------|---------------------|
| P1 Builder | skill-builder-libre.md |
| P2 EvalGate | skill-evaluation-auto.md |
| P3 Retester | skill-retester.md |
| P4 SPP | skill-spp-validation.md |
| P5 WFO | skill-wfo-anchored.md |
| P6 Stress Test | skill-stress-test.md |
| P7 Multimarket | skill-evaluation-auto.md (seccion multimarket) |
| P8 Portfolio | skill-portfolio-selection.md |
| P9 Forward Test | skill-forward-test.md + skill-forward-test-protocol.md |

---

## LO QUE ESTA SKILL NUNCA HACE

NUNCA salta una puerta para "ahorrar tiempo".
NUNCA ajusta criterios entre puertas sin instruccion explicita.
NUNCA considera el orden de las puertas como opcional.
NUNCA aplica una puerta sin los datos necesarios para esa puerta.
