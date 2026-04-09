# Skill: Formato de Informe de Evaluacion

## Proposito
Define el formato exacto que debe usar el
evaluator-assistant para generar informes
estructurados del Evaluation Gate.
El objetivo es que el humano solo tenga que
leer el informe y firmar la decision.

---

## FORMATO COMPLETO DEL INFORME

Usar este formato exacto para cada estrategia
candidata que supere el filtro inicial (PF > 1.3).

---

# EVALUATION GATE REPORT

Estrategia: [nombre o ID de la estrategia]
Fecha del build: [fecha]
Fecha del informe: [fecha]
Generado por: evaluator-assistant

---

## 1. METRICAS PRINCIPALES

| Metrica | Valor | Umbral | Estado |
|---------|-------|--------|--------|
| Profit Factor | [valor] | >= 1.5 | OK / ALERTA |
| Max Drawdown | [valor]% | < 7% | OK / ALERTA |
| Daily Drawdown max | [valor]% | < 3% | OK / ALERTA |
| Trades totales | [numero] | >= 100 | OK / ALERTA |
| Trades por mes | [numero] | >= 20 | OK / ALERTA |
| Win Rate | [valor]% | >= 40% | OK / ALERTA |
| Ratio TP/SL | [valor]:1 | >= 2:1 | OK / ALERTA |
| Ratio Rent/DD | [valor] | >= 1.5 | OK / ALERTA |

---

## 2. ANALISIS DE CONSISTENCIA POR ANOS

| Ano | PF | DD max | Trades | Estado |
|-----|-----|--------|--------|--------|
| 2003 | [PF] | [DD]% | [N] | OK / MALO |
| 2004 | [PF] | [DD]% | [N] | OK / MALO |
| ... | ... | ... | ... | ... |
| 2020 | [PF] | [DD]% | [N] | OK / MALO |

Anos con PF < 1.0: [numero] de [total]
Porcentaje de anos positivos: [%]
Conclusion consistencia: ROBUSTA / ACEPTABLE / FRAGIL

---

## 3. ANALISIS DE CURVE-FITTING

Señales detectadas:

[ ] PF > 3.0 con trades < 100 — NO detectado
[ ] Mas del 50% del beneficio en un mes — NO detectado
[ ] Solo funciona en 2 anos o menos — NO detectado
[ ] Parametros muy especificos (ej EMA exactamente 47) — NO detectado
[ ] DD maximo en los ultimos 3 meses — NO detectado
[ ] Resultado mejora solo al ampliar el SL — NO detectado

Señales activas: [numero]
Nivel de riesgo curve-fitting: BAJO / MEDIO / ALTO

---

## 4. ANALISIS DE RACHAS PERDEDORAS

Max racha perdedora consecutiva: [numero] trades
Con riesgo 1% por trade:
Perdida maxima de la racha: [numero]% del balance

Evaluacion para FTMO 2-Step (cuenta 25.000$):
- Racha de [numero] trades x 250$ = [USD]
- Como % del balance: [%]%
- Viola Daily Loss Limit (3% operativo = 750$): SI / NO
- Viola Max DD Limit (7% operativo = 1.750$): SI / NO

---

## 5. SIMULACION DEL CHALLENGE FTMO

Basada en los resultados del periodo in-sample:

Rendimiento mensual promedio: [%]%
Peor mes del periodo: [%]%
Mejor mes del periodo: [%]%
Meses con rendimiento >= +10%: [numero] de [total]
Meses con violacion de limites: [numero] de [total]

Probabilidad estimada de pasar el challenge: [%]%
Tiempo estimado para alcanzar el objetivo: [X] dias

Evaluacion:
> 70% probabilidad → VIABLE para challenge
40-70% probabilidad → REVISAR position sizing
< 40% probabilidad → NO viable todavia

---

## 6. COMPARATIVA CON BUILDS ANTERIORES

| Build | Hipotesis | PF | DD | Resultado |
|-------|-----------|-----|-----|-----------|
| Build 4 | EMACross M15 | 1.65 | 5.2% | Retester negativo |
| Build 5 | EMACross M15 | 1.27 | 6.1% | Descartada |
| Build 6 | NBAR M15 | 1.18 | 7.8% | Descartada |
| ESTE | [nombre] | [PF] | [DD]% | [pendiente] |

Esta estrategia es [mejor / igual / peor] que
las candidatas del Build 4 (la mejor hasta ahora).

---

## 7. RECOMENDACION DEL AGENTE

Decision recomendada: PASA / REVISAR / SIMPLIFICAR / DESCARTAR

Confianza: [X]/10

Justificacion:
[Explicacion de 2-3 frases del razonamiento]

Observaciones criticas:
- [Observacion 1 si existe]
- [Observacion 2 si existe]

Siguiente paso recomendado:
[Accion concreta — ej: "Pasar al Retester priorizando
sobre otras candidatas por mayor PF y menor DD"]

---

## 8. DECISION HUMANA

Firma aqui la decision final:

[ ] PASA — proceder al Retester
[ ] REVISAR — motivo: ______________________
[ ] SIMPLIFICAR — aspecto a simplificar: ______
[ ] DESCARTAR — motivo: ____________________

Firmado por: _______________
Fecha: _______________

---

## NOTAS PARA EL EVALUATOR-ASSISTANT

### Como rellenar la seccion de consistencia por anos
Buscar en los resultados del Builder si hay
desglose por periodo. Si SQ no lo muestra
directamente, estimar basandose en las
curvas de equity del periodo in-sample.

### Como calcular la probabilidad del challenge
Usar la formula de skill-ftmo-simulation.md.
Con los datos disponibles del build calcular:
- Cuantos meses del periodo habrian alcanzado +10%
- Cuantos meses habrian violado algun limite
- Ratio de meses buenos sobre total

### Cuando descartar sin pasar al humano
Solo descartar automaticamente si se cumplen
UNO O MAS de estos criterios sin excepcion:
- PF < 1.3 con comisiones reales
- DD > 8%
- Trades < 50
- Mas del 50% del beneficio en un solo mes
- DD maximo en los ultimos 3 meses del periodo

En cualquier otro caso generar el informe
completo y dejar la decision al humano.

### Orden de prioridad cuando hay multiples candidatas
1. Mayor PF con DD < 5% — maxima prioridad
2. Mayor PF con DD 5-7% — segunda prioridad
3. Mas trades con PF > 1.5 — tercera prioridad
4. Las demas en orden de PF descendente