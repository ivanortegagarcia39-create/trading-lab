# Informe de Evaluacion de Compatibilidad FTMO
Estrategia evaluada: TrendFollowing-EURUSD-H1-EMA50-ADX
Fecha: 2026-04-10
Evaluada por: funding-specialist
Momento del pipeline: Momento 1 — evaluacion teorica pre-build
Ticket: TICKET-001
Prop firm objetivo: FTMO 2-Step — cuenta 25.000 USD

NOTA: Esta evaluacion es teorica. No hay datos de backtest todavia.
Objetivo: confirmar que el diseño de la hipotesis no tiene
incompatibilidades estructurales con las reglas FTMO antes de gastar
tiempo de Builder. La evaluacion completa con simulacion se realizara
en Momento 2 tras el Retester y el Optimizer.

---

## FASE 1 — VERIFICACION DE REGLAS BASICAS

| Criterio FTMO                      | Hipotesis         | Resultado  |
|------------------------------------|-------------------|------------|
| No es HFT                          | H1, 6-12 t/mes    | CUMPLE     |
| No es tick scalping                | H1 (>2 minutos)   | CUMPLE     |
| No usa martingala                  | Lote fijo 1%      | CUMPLE     |
| SL definido en todas las ops       | ATR(14) x 2.0     | CUMPLE     |
| TP definido en todas las ops       | ATR(14) x 4.5     | CUMPLE     |
| Temporalidad >= H1                 | H1                | CUMPLE     |
| Tipo de estrategia permitido       | Trend Following   | CUMPLE     |
| Logica simetrica (no solo largo)   | Long y Short       | CUMPLE     |

**Resultado Fase 1: PASA — ninguna incompatibilidad estructural detectada.**

---

## FASE 2 — VERIFICACION TEORICA DE METRICAS

Sin datos de backtest, la evaluacion usa los rangos esperados
definidos en la hipotesis y el calculo teorico de EV.

### Metricas verificables antes del build

| Metrica             | Valor hipotesis      | Minimo requerido | Estado       |
|---------------------|----------------------|------------------|--------------|
| Ratio TP/SL         | 2.25:1               | >= 2:1           | CUMPLE       |
| Riesgo por trade    | 1% (250 USD en 25k)  | 1% fijo          | CUMPLE       |
| Max trades/dia      | 2                    | <= 2 en H1       | CUMPLE       |
| Ventana de sesion   | 08:00-20:00          | >= 6 horas       | CUMPLE       |
| Temporalidad        | H1                   | H1               | CUMPLE       |
| SL y TP definidos   | ATR-based            | Obligatorio      | CUMPLE       |

### Calculo de EV teorico (con parametros de diseño)

Asumiendo parametros moderados (win rate 40%, ratio 2.25:1):
EV por trade = 250 x (0.40 x 2.25 - 0.60) = 250 x (0.90 - 0.60) = 250 x 0.30 = 75 USD/trade

Trades necesarios para objetivo 2.500 USD:
2.500 / 75 = 33 trades → a 6 trades/mes = 5.5 meses | a 12 trades/mes = 2.8 meses
Sin limite de tiempo en FTMO Challenge — VIABLE.

Asumiendo win rate 45%, ratio 2.25:1:
EV = 250 x (0.45 x 2.25 - 0.55) = 250 x (1.0125 - 0.55) = 250 x 0.4625 = 115.6 USD/trade
Trades necesarios: 2.500 / 115.6 = 21 trades → menos de 2 meses a 12 trades/mes.

### Analisis del Daily Loss Limit (3% operativo = 750 USD)

Con riesgo 1% por trade y max 2 trades/dia H1:
Peor caso del dia: 2 trades perdedores = 2 x 250 USD = 500 USD = 2.0%
Margen adicional sobre limite operativo: 750 - 500 = 250 USD
Conclusion: el diseño es SEGURO para el Daily Loss en condiciones normales.

Riesgo residual: posicion overnight con swap negativo + perdida del dia siguiente.
Mitigacion: salida al final del dia activada — minimiza el riesgo de swap adverso.

### Analisis del Max Drawdown (7% operativo = 1.750 USD)

DD esperado IS segun hipotesis: 4-8%
Margen operativo FTMO: 7%
Racha maxima segura: 7 trades x 250 USD = 1.750 USD = 7% → en el limite exacto

Escenario adverso (DD IS = 8%): supera el 7% operativo.
Accion: si el Builder produce candidatas con DD IS > 7% se deben filtrar
en el Evaluation Gate. No son necesariamente un bloqueador ahora
pero si una señal de alerta prioritaria.

Con racha de 6 trades perdedores: 1.500 USD = 6% → DENTRO del margen.
Conclusion: el diseño tiene margen suficiente si el DD IS se mantiene <= 6%.

### Alerta sobre frecuencia de trades

| Metrica             | Esperado hipotesis | Recomendado funding-specialist | Estado    |
|---------------------|-------------------|-------------------------------|-----------|
| Trades totales (IS) | ~1.200-2.400      | >= 100                        | CUMPLE    |
| Trades por mes      | 6-12              | >= 20 (recomendado)           | ALERTA    |
| Dias con trades/mes | 3-6               | >= 4 (FTMO minimo)            | MARGINAL  |

ANALISIS DE LA ALERTA:
Los 20 trades/mes son una recomendacion del funding-specialist para
validez estadistica del backtest, NO un requisito de FTMO.
El requisito real de FTMO son 4 dias con posiciones iniciadas.
Con 6-12 trades/mes distribuidos en dias distintos el requisito FTMO se cumple,
pero el margen es ajustado si el mercado pasa dias sin condiciones (ADX < 20).

Riesgo real: si en un periodo de 30 dias hay menos de 4 dias con trades
(mercado lateral prolongado sin ADX > 20) podria no cumplir el minimo FTMO.

Mitigacion en el Builder: verificar que en los resultados del backtest
no haya periodos de mas de 2 semanas sin ninguna operacion.
Si se detectan → revisar el umbral ADX (bajar de 20 a 18 como rango minimo).

---

## VERIFICACION DE REGLAS PROHIBIDAS FTMO

| Regla prohibida                    | Hipotesis         | Estado     |
|------------------------------------|-------------------|------------|
| HFT                                | No aplica — H1    | LIBRE      |
| Latency arbitrage                  | No aplica         | LIBRE      |
| Tick scalping < 1 minuto           | No aplica — H1    | LIBRE      |
| Martingala o aumento tras perdida  | Lote fijo 1%      | LIBRE      |
| Copiar señales otras cuentas FTMO  | EA propio         | LIBRE      |

---

## CALCULO DE VIABILIDAD COMPLETO — CUENTA 25.000 USD

### Fase 1 Challenge (+10% = 2.500 USD)

Escenario conservador (WR 40%, ratio 2.25:1, 6 trades/mes):
- EV = 75 USD/trade
- Trades para objetivo: 33
- Tiempo estimado: 33/6 = 5.5 meses
- Dias minimos FTMO: con 6 trades/mes en dias distintos → 6 dias/mes → CUMPLE

Escenario base (WR 45%, ratio 2.25:1, 10 trades/mes):
- EV = 115.6 USD/trade
- Trades para objetivo: 21
- Tiempo estimado: 21/10 = 2.1 meses
- Dias minimos FTMO: cumple con margen

### Fase 2 Verification (+5% = 1.250 USD)

Mismos parametros — objetivo la mitad:
- Conservador: ~17 trades → 2.8 meses adicionales
- Base: ~11 trades → 1.1 mes adicional

### Resumen total del proceso

Tiempo total estimado Challenge + Verification:
- Escenario conservador: ~8-9 meses
- Escenario base: ~3-4 meses
Sin limite de tiempo → ambos escenarios son viables.

---

## ALERTAS FORMALES

ALERTA 1 — Frecuencia baja de trades:
Riesgo: en periodos de mercado lateral prolongado (ADX < 20 consistente)
la estrategia puede no generar suficientes trades para cumplir
los 4 dias minimos de FTMO en un mes dado.
Accion en el Evaluation Gate: verificar que no hay gaps de
mas de 14 dias sin operaciones en el backtest IS.

ALERTA 2 — DD marginal en escenario adverso:
Riesgo: DD esperado IS de 4-8% deja poco margen si llega a 7-8%.
Accion en el Evaluation Gate: solo avanzar candidatas con DD IS <= 6.5%.
Si el DD IS supera 6.5% → REVISAR multiplicador SL (reducir de 2.0 a 1.8).

ALERTA 3 — Verificar trades/mes en resultados del Builder:
Contar explicitamente el numero de meses con menos de 4 dias de trading.
Si mas del 20% de los meses tienen < 4 dias con trades → ajustar hipotesis.

---

## DECISION

[x] COMPATIBLE CON FTMO — puede avanzar al Builder
    Condiciones: las alertas 1, 2 y 3 se verifican en el Evaluation Gate.
    No son bloqueadores pre-build.

[ ] COMPATIBLE CON AJUSTES — no aplica en este momento
[ ] NO COMPATIBLE — no aplica

---

## INSTRUCCIONES PARA EL EVALUATION GATE

Cuando el Builder termine verificar en los resultados:
1. DD IS de las candidatas <= 6.5% (alerta 2)
2. Trades por mes promedio (alerta 1 y 3)
3. Meses con < 4 dias de trading (alerta 3)
4. Ratio TP/SL real de las candidatas >= 2:1

Si alguna candidata viola las alertas 1-3 → marcar como REVISAR,
no descartar automaticamente.
La decision final sobre alertas es del humano en el Evaluation Gate.

---

## CHECKLIST PRE-CHALLENGE (rellenar en Momento 2 — tras Retester y Optimizer)

[ ] PF out-of-sample >= 1.5 con comisiones reales
[ ] Max Drawdown out-of-sample < 7%
[ ] Daily Drawdown out-of-sample < 3% en ningun dia
[ ] Trades totales OOS >= 100
[ ] Trades por mes OOS >= 6 con al menos 4 dias/mes
[ ] Ratio TP/SL efectivo >= 2:1
[ ] WFE del Optimizer >= 50%
[ ] Sin gaps de mas de 14 dias sin operaciones
[ ] Max racha perdedora <= 6 trades consecutivos
[ ] Decision humana final: SI

Informe completo guardado en:
results/reviewed/TrendFollowing-EURUSD-H1-EMA50-ADX-funding-eval.md
