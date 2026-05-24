# Skill: Evaluation Gate Automatico — Sin Intervencion Humana

## Proposito
Define los criterios numericos exactos que el
orchestrator y el evaluator-assistant aplican
de forma 100% automatica para aprobar o descartar
estrategias en cada puerta del pipeline.
Ninguna decision subjetiva. Solo numeros.

---

## FILOSOFIA DE LA EVALUACION AUTOMATICA

El sesgo humano en la seleccion de estrategias
fue la causa principal de los 8 builds fallidos.
Frases como "esta parece prometedora" o "le damos
otra oportunidad" no existen en este sistema.

Una estrategia cumple los numeros o no los cumple.
No hay zona gris salvo casos estadisticamente
excepcionales que representan menos del 5%
de las candidatas.

---

## FASE 1 — FILTRO DEL BUILDER (automatico en SQ)

Estas estrategias nunca llegan al Evaluation Gate
porque SQ las descarta internamente:

- PF < 1.1 → no entra en el databank
- Trades/mes > 0 (sin limite minimo)
- Ret/DD > 0 (sin limite minimo)

Solo las estrategias que superan estos filtros
aparecen en el databank para ser evaluadas.

---

## FASE 2 — EVALUATION GATE (automatico por orchestrator)

### Criterios de DESCARTE AUTOMATICO
Si cumple CUALQUIERA de estos → DESCARTAR
sin consultar al humano:

- PF in-sample < 1.8
- Max DD in-sample > 4%
- Trades totales < 300
- Trades por mes < 15
- Win Rate < 35%
- Avg Trade < 7 pips
- Ratio TP/SL efectivo < 1.8:1
- Años con PF < 1.0 superan el 35% del total
- Mas del 45% del beneficio en un solo mes
- DD maximo ocurre en los ultimos 3 meses del IS
- Max racha perdedora > 8 trades consecutivos
- Algun año individual en IS con DD > 8%
  (un solo año malo puede destruir el challenge)
- Triple swap miercoles > 15% del beneficio neto
  (estrategia demasiado sensible a costes de financiacion)
- PF post-swaps < 80% del PF pre-swaps
  (los swaps overnight eliminan el edge)

### Criterios de APROBACION AUTOMATICA para Retester
Si cumple TODOS estos → PASA al Retester
sin consultar al humano:

- PF in-sample >= 1.8
- Max DD in-sample <= 4%
- Trades totales >= 300
- Trades por mes >= 15
- Win Rate >= 40%
- Avg Trade >= 7 pips
- Ratio TP/SL efectivo >= 2:1
- Años positivos >= 75% del total
- PF ultimos 3 años >= 1.2
- Ningun mes con mas del 40% del beneficio total
- DD maximo NO en los ultimos 3 meses del IS
- Max racha perdedora <= 6 trades consecutivos
- Monte Carlo: sin degradacion significativa

### Zona de revision automatica
Si no cae en descarte ni en aprobacion el
orchestrator clasifica como REVISION PENDIENTE.

Criterios de revision automatica:
- PF entre 1.8 y 2.0 → revisar si trades > 350
  Si trades > 350 → PASA (mayor muestra compensa)
  Si trades <= 350 → DESCARTAR
- DD entre 3.5% y 4% → revisar si PF > 2.0
  Si PF > 2.0 → PASA (alto PF compensa DD marginal)
  Si PF <= 2.0 → DESCARTAR
- Años negativos entre 25% y 35% → revisar si
  los años negativos coinciden con crisis conocidas
  (2008, 2015, 2020) → PASA
  Si no coinciden con crisis → DESCARTAR

CRITICO: Estas reglas de revision tambien son
automaticas. El orchestrator las aplica sin
consultar al humano. No hay zona gris real.

---

## FASE 3 — ANALISIS OOS PASO 12b (automatico)

### Criterios de DESCARTE AUTOMATICO
Si cumple CUALQUIERA → DESCARTAR sin consultar:

- PF OOS < 1.2
- Caida de PF (IS → OOS) > 25%
- DD OOS > 7%
- Trades/mes OOS < 5
- Frecuencia OOS cae mas del 50% respecto al IS
- Sharpe ratio OOS < 0.5
  (PF puede ser enganoso con pocas operaciones —
  Sharpe normaliza por la volatilidad de los retornos)

### Criterios de APROBACION para WFO
Si cumple TODOS → PASA al WFO sin consultar:

- PF OOS >= 1.3
- Caida de PF <= 20%
- DD OOS <= 6.5%
- Trades/mes OOS >= 6
- Frecuencia OOS no cae mas del 40% respecto al IS
- Sharpe ratio OOS >= 0.5

### Revision automatica paso 12b
- PF OOS entre 1.2 y 1.3 → DESCARTAR
  (no llegara al umbral necesario en WFO)
- Caida PF entre 20% y 25% → DESCARTAR
  (sobreajuste probable)
- DD OOS entre 6.5% y 7% → DESCARTAR
  (margen insuficiente para FTMO)

En el paso 12b NO hay zona gris.
O pasa o se descarta. El WFO es demasiado
costoso en tiempo para lanzarlo con dudas.

---

## FASE 4 — DICTAMEN WFO (automatico)

### Criterios de DESCARTE AUTOMATICO
Si cumple CUALQUIERA → DESCARTAR sin consultar:

- WFE < 40%
- 2 o mas ventanas OOS con PF < 1.0
- 2 ventanas OOS negativas consecutivas
- DD OOS > 7.5% en cualquier ventana
- PF OOS < 1.0 en la ultima ventana
- Parametros optimos con desviacion > 35%
  entre ventanas
- CATASTROPHIC VETO: CUALQUIER ventana individual
  con PF < 0.8 O DD > 10% → DESCARTAR
  independientemente del promedio general
  (una ventana catastrofica revela fragilidad
  estructural que el promedio puede ocultar)

### Criterios de APROBACION AUTOMATICA FINAL
Si cumple TODOS → ESTRATEGIA APROBADA
sin consultar al humano:

- WFE >= 50%
- 0 ventanas OOS con PF < 0.9
- Maximo 1 ventana OOS con PF entre 0.9 y 1.0
  y debe ser aislada (no consecutiva)
- DD OOS <= 7% en todas las ventanas
- PF OOS ultima ventana >= 1.1
- Parametros optimos con desviacion < 25%
- PF OOS promedio >= 1.25

### Revision automatica WFO
- WFE entre 40% y 50% → DESCARTAR
  (robustez insuficiente para produccion)
- 1 ventana negativa aislada con WFE > 50%
  → PASA si PF OOS promedio >= 1.3
  → DESCARTAR si PF OOS promedio < 1.3

---

## FASE 5 — VALIDACION DE PORTFOLIO (automatico)

Despues de la aprobacion WFO el correlation-analyst
aplica estos criterios automaticamente:

### Criterios de INCLUSION en portfolio
Si cumple TODOS → se incluye automaticamente:

- Correlacion con cada estrategia activa < 0.5
- DD combinado estimado con portfolio < 12%
- No mas de 2 estrategias del mismo estilo
  (trend-following o mean-reversion) activas
- No mas de 2 estrategias en el mismo activo

### Criterios de ESPERA
Si no cumple inclusion pero la estrategia es valida:

- Correlacion > 0.5 con alguna activa → ESPERA
  Queda en cola hasta que la activa se retire
- DD combinado > 12% → ESPERA
  Queda en cola hasta que el DD del portfolio baje

### Criterios de DESCARTE de portfolio
- Correlacion > 0.7 con 2 o mas activas → DESCARTAR
  Demasiado redundante para el portfolio

---

## FASE 6 — FORWARD TEST EN DEMO (automatico)

El forward test es evaluado automaticamente por
performance-monitor. No requiere decision humana.
Ver agents/performance-monitor.md para el protocolo completo.

### Criterios automaticos (los 3 deben cumplirse)

| Criterio | Umbral |
|----------|--------|
| Trades minimos ejecutados en demo | >= 20 |
| PF en demo vs PF OOS backtest | >= 70% |
| DD maximo en demo vs DD OOS backtest | <= OOS + 30% |

### Resultado automatico
Si PASA los 3 criterios:
  → orchestrator genera notificacion de challenge (CASO 1)
  → El humano autoriza con "SI" — unica intervencion

Si FALLA algún criterio:
  → estrategia a cola de reemplazo automaticamente
  → NO se consulta al humano ni se pide opinion

---

## CRITERIOS POR TIMEFRAME

Los umbrales de trades se ajustan al timeframe.
El criterio base (Trades >= 120, Trades/mes >= 8) es
para H1. Las demas temporalidades tienen sus propios umbrales.

| Timeframe | Trades totales minimos | Trades/mes minimos | Categoria |
|-----------|----------------------|-------------------|-----------|
| H4 | >= 50 | >= 3 | Produccion Core |
| H1 | >= 300 | >= 15 | Produccion Core |
| M30 | >= 300 | >= 15 | Incubadora Tactica |
| M15 | >= 300 | >= 25 | Incubadora Tactica |

Razon de los umbrales crecientes en TF menores:
Las temporalidades cortas tienen mas ruido. Para que la
muestra sea estadisticamente significativa necesitan mas trades.
El umbral H1 se endurece a 300 trades para garantizar
significancia estadistica y reducir overfit.

El evaluator-assistant detecta automaticamente el timeframe
de la estrategia desde el nombre del simbolo o la configuracion
del Builder y aplica los umbrales correspondientes.

---

## ANALISIS POR REGIMEN DE MERCADO

Scoring adicional calculado por market-regime-detector.
NO es criterio de descarte — es ajuste del score de portfolio.

Usando los regimenes del mercado durante el periodo IS,
calcular el PF de la estrategia segmentado por regimen:

| Regimen | PF calculado |
|---------|-------------|
| tendencia-altavol | [valor] |
| tendencia-bajovol | [valor] |
| rango-altavol | [valor] |
| rango-bajovol | [valor] |

### Penalizacion
Si PF < 1.0 en MAS DE 2 de los 4 regimenes:
  → Penalizacion de -15 puntos en el score de portfolio
  → No es descarte — la estrategia puede seguir en el pipeline

### Bonus
Si PF > 1.2 en los 4 regimenes:
  → Bonus de +10 puntos en el score de portfolio
  → Estrategia robusta en todos los entornos de mercado

### Como se calcula
1. Obtener historial de regimenes del periodo IS de market-regime-detector
2. Segmentar los trades de la estrategia por regimen predominante
3. Calcular PF (suma ganancias / suma perdidas) por segmento
4. Si hay pocos trades en un regimen (< 10) → marcar como "insuficiente"
   y no penalizar por ese regimen (muestra insuficiente)

---

## METRICA DE CALIDAD DE SIMULACION

Añadir al informe de evaluacion como campo informativo.
No es criterio de descarte — es nota de advertencia.

Campo: Cobertura de ticks reales vs simulados
Obtener de SQ: pestana de resultados → calidad de datos

| Cobertura | Accion |
|-----------|--------|
| >= 90% | Sin nota — calidad optima |
| 80-89% | Nota informativa en el informe |
| < 80% | ADVERTENCIA en el informe — resultados menos fiables |

Cuando cobertura < 80%:
  Añadir al informe de evaluacion:
  "ADVERTENCIA: cobertura de ticks [X]%. Los resultados
  pueden diferir de la ejecucion real. Verificar calidad
  de datos con data-manager antes de avanzar al Retester."

Esta advertencia NO bloquea automaticamente el pipeline
pero queda registrada en el audit trail del orchestrator.

---

## TEST DE ESTRES DE VELOCIDAD (M15 y M30 unicamente)

Aplicar SOLO a estrategias en M15 o M30.
Las estrategias H1/H4 no necesitan este test.

### Cuando se ejecuta
Despues del paso 12b, antes del WFO.
Solo si el timeframe de la estrategia es M15 o M30.

### Metodo
Ejecutar la estrategia en un periodo de 2 años completos
aunque el build original haya usado una ventana IS de 6 meses.
Objetivo: verificar que el edge no es especifico de un
regimen de 6 meses sino que persiste en el tiempo.

### Criterio
PF > 1.2 en CADA uno de los 2 años de test.
Si PF <= 1.2 en alguno de los 2 años → DESCARTAR.

### Razon
M15 y M30 son la "Incubadora Tactica" (ver skill-timeframe-selector.md).
Pueden llegar a produccion si pasan todos los filtros adicionales.
Este test garantiza que el edge no es un artefacto de
los ultimos 6 meses del ciclo actual.

---

## CALCULO DEL TRIPLE SWAP Y POST-SWAPS

### Triple swap miercoles
FTMO (y la mayoria de brokers) aplican el triple swap
el miercoles para compensar el fin de semana.
Para estrategias con posiciones overnight esto representa
un coste real que puede no estar bien modelado en SQ.

Calculo:
  swap_total_periodo = suma de todos los swaps del backtest
  swap_miercoles = swap_total_periodo * (3/7) * factor_broker
  pct_sobre_beneficio = swap_miercoles / beneficio_neto_total * 100

  Si pct_sobre_beneficio > 15% → DESCARTAR
  Razon: mas del 15% del beneficio va a pagar financiacion →
  el edge real de la estrategia es mucho menor del aparente

### PF post-swaps
Recalcular el PF incluyendo los costes de swap reales:
  beneficio_neto_post_swap = beneficio_neto - coste_swap_total
  perdidas_totales_post_swap = perdidas_totales + coste_swap_total
  PF_post_swap = beneficio_neto_post_swap / perdidas_totales_post_swap

  Si PF_post_swap < PF_pre_swap * 0.80 → DESCARTAR
  Razon: los swaps consumen mas del 20% del edge →
  estrategia no viable con costes reales de financiacion

Nota: SQ incluye opciones de swap en la configuracion del simbolo.
Verificar que el simbolo [ACTIVO]_ftmo tiene los swaps configurados
correctamente ANTES de lanzar el Builder.

---

## RESUMEN DE TASAS DE DESCARTE ESPERADAS

Con el Builder libre generando 1000+ candidatas:

Builder → Evaluation Gate: ~60-70% descartadas
Evaluation Gate → Retester: ~20-30% pasan
Retester → paso 12b: ~40-50% descartadas
Paso 12b → WFO: ~50-60% pasan
WFO → Aprobacion: ~30-40% pasan
Portfolio → Inclusion: ~60-80% incluidas

Resultado esperado de 1000 candidatas:
~5-15 estrategias aprobadas por el WFO
~3-10 incluidas en el portfolio

Esto es NORMAL. Un ratio del 1% de candidatas
que llegan a produccion es estandar en la industria.

---

## FLUJO COMPLETO SIN INTERVENCION HUMANA

SQ Builder libre corriendo 24-48h
        ↓
1000+ candidatas en databank
        ↓
Evaluation Gate automatico (orchestrator)
~200-300 pasan
        ↓
Retester automatico (sq-specialist)
        ↓
Paso 12b automatico (orchestrator)
~100-150 pasan
        ↓
WFO automatico (sq-specialist)
        ↓
Dictamen WFO automatico (orchestrator)
~5-15 aprobadas
        ↓
Portfolio automatico (correlation-analyst)
~3-10 incluidas
        ↓
Export a MT5 (export-specialist)
        ↓
Forward test en demo (UNICA intervencion humana)
        ↓
Challenge en prop firm
        ↓
Performance monitor automatico

---

## REGLA FUNDAMENTAL

Los numeros deciden. No las personas.
Si cumple los umbrales → avanza.
Si no cumple → se descarta.
Sin excepciones. Sin segunda oportunidad.
Sin "parece prometedora".
