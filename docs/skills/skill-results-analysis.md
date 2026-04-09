# Skill: Analisis de Resultados de Builder

## Proposito
Guia para el orchestrator y el sq-specialist.
Define como interpretar las metricas del Builder
y tomar decisiones correctas en el Evaluation Gate.

---

## METRICAS PRINCIPALES Y SU SIGNIFICADO

### Profit Factor (PF)
Formula: ganancias brutas / perdidas brutas

Interpretacion:
PF < 1.0 → pierde dinero. Descartar siempre.
PF 1.0-1.3 → marginal. Solo revisar si logica es solida.
PF 1.3-1.5 → aceptable para Retester con cautela.
PF 1.5-2.0 → bueno. Avanzar al Retester.
PF > 2.0 → muy bueno. Prioridad en Retester.
PF > 3.0 → sospechoso de curve-fitting. Revisar.

SEÑAL DE ALERTA:
PF > 3 con trades < 100 = casi seguro curve-fitting.

### Max Drawdown
Interpretacion para FTMO (cuenta 25.000$):
DD > 7% → zona de peligro. Revisar.
DD > 10% → viola limite FTMO. Descartar siempre.
DD 5-7% → aceptable con cautela.
DD < 5% → muy bueno.

SEÑAL DE ALERTA:
DD bajo con PF alto puede indicar que el periodo
no incluye momentos de crisis (2008, 2015, 2020).

### Numero de Trades
< 50 trades → insuficiente. Descartar siempre.
50-100 trades → marginal. Solo avanzar si PF > 1.8.
100-200 trades → aceptable.
> 200 trades → bueno.
> 500 trades → muy bueno para estadistica.

### Trades por mes
< 8 trades/mes → muy pocos para H1. Revisar sesion.
8-20 trades/mes → aceptable.
> 20 trades/mes → bueno para objetivo FTMO.

### Win Rate
Win Rate bajo (35-45%) con PF alto →
estrategia de tendencia. Normal y valido en H1.

Win Rate alto (60-80%) con PF bajo →
SL grande y TP pequeño. Peligrosa para FTMO.

Combinacion ideal para FTMO:
Win Rate 40-55% con PF > 1.5 y ratio TP/SL >= 2:1

### Ratio Rentabilidad / Reduccion
RR < 1 → arriesga mas de lo que gana. Revisar.
RR 1-2 → aceptable.
RR > 2 → bueno.
RR > 5 → muy bueno.

---

## SEÑALES DE CURVE-FITTING

1. PF > 3 con trades < 100
2. Todo el beneficio concentrado en un mes o trimestre
3. Funciona perfectamente en un periodo y muy mal resto
4. Parametros muy especificos (EMA de 47 en vez de 50)
5. DD maximo en los ultimos meses — se esta deteriorando
6. Resultado mejora drasticamente al ampliar el SL

---

## PROTOCOLO DE EVALUATION GATE

### Paso 1: Filtro rapido
Eliminar inmediatamente:
- PF < 1.3 con comisiones reales
- Trades < 80
- DD > 8%

### Paso 2: Revision de consistencia
Para las que quedan verificar:
- Tiene anos con PF negativo?
  Si mas del 30% de anos negativos → DESCARTAR
- El beneficio viene de un solo trimestre? → REVISAR
- DD maximo en los ultimos 2 anos? → SEÑAL DE ALERTA

### Paso 3: Verificacion FTMO
- DD simulado < 7% → OK
- Daily DD simulado < 3% → OK
- Ratio TP/SL >= 2:1 → OK
- SL y TP definidos → OK
- Trades por mes >= 20 → OK

### Paso 4: Decision final
PASA → PF >= 1.5, DD < 7%, Trades >= 100,
       consistencia por anos > 70%, ratio >= 2:1
REVISAR → PF 1.3-1.5 con logica solida
SIMPLIFICAR → PF bueno pero demasiadas condiciones
DESCARTAR → cualquier otro caso

---

## DIAGNOSTICO RAPIDO DE BUILDS FALLIDOS

Build termina en menos de 2 horas con > 200 estrategias:
→ Datos no cubren el periodo completo
→ Verificar fechas en Gestor de datos

Build termina en tiempo normal pero 0 aceptadas:
→ Filtros demasiado estrictos
→ Relajar filtros en Clasificacion

Build genera estrategias pero PF maximo < 1.2:
→ Hipotesis no funciona con comisiones reales
→ SIMPLIFICAR o nueva hipotesis

PF maximo 1.2-1.5 pero 0 en databank:
→ Filtros cortando candidatas validas
→ Bajar umbral PF a 0.7 en Clasificacion

---

## APRENDIZAJES DE BUILDS ANTERIORES

Build 1-2 (LARB M15):
Logica de rango asiatico no nativa en SQ.
PF maximo: no medido — descartado antes.

Build 3 (EMACross-ADX M15):
Filtros demasiado estrictos. 0 aceptadas.
Solucion: relajar filtros y opciones geneticas.

Build 4 (EMACross-ADX M15 sin comisiones):
6 candidatas con PF 1.53-1.70.
Problema: sin comisiones reales — resultados irreales.

Build 5 (EMACross-ADX M15 con comisiones):
PF maximo 1.27. Edge insuficiente en M15.
Decision: DESCARTAR hipotesis.

Build 6 (NBARBreakout-RSI M15 con comisiones):
PF maximo 1.18. DD hasta 68% en algunos casos.
Decision: REVISAR — cambiar a H1.

Build 7 (NBARBreakout-RSI H1 con comisiones):
En curso en el momento de crear este archivo.
Primer build con H1 y comisiones reales correctas.