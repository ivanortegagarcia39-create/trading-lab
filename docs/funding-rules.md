# Funding Rules — FTMO Challenge 2-Step

## Modalidad elegida
FTMO Challenge 2-Step — modalidad estandar de 2 fases.
NO usar el 1-Step — el Daily Loss Limit del 3% es
demasiado restrictivo para EAs de baja frecuencia.

---

## FASE 1 — FTMO Challenge

### Objetivo de ganancias
- Minimo: +10% del capital inicial
- Cuenta 25.000$: necesitais ganar 2.500$
- Plazo: ilimitado
- Todas las posiciones deben estar cerradas
  antes de que se evalúe el objetivo

### Daily Loss Limit (5% — DINAMICO)
- El limite se recalcula cada medianoche hora de Praga (CEST)
- Formula: balance a medianoche del dia anterior - 5% del capital inicial
- El limite PUEDE subir y bajar segun el balance
- Cuenta 25.000$: limite inicial = 25.000$ - 1.250$ = 23.750$
- Si el balance sube a 26.000$: limite = 26.000$ - 1.250$ = 24.750$
- Si el balance baja a 24.500$: limite = 24.500$ - 1.250$ = 23.250$

CRITICO: El limite incluye posiciones abiertas,
comisiones Y swaps en tiempo real.
Un swap overnight puede acercaros al limite sin avisar.

Margen de seguridad recomendado: usar 3% como
limite operativo, no el 5% oficial.
Cuenta 25.000$: no perder mas de 750$ por dia.

### Max Drawdown (10% — DINAMICO, solo sube)
- El limite se recalcula cada medianoche hora de Praga (CEST)
- Formula: balance maximo historico - 10% del capital inicial
- El limite SOLO puede subir, nunca bajar
- Cuenta 25.000$: limite inicial = 25.000$ - 2.500$ = 22.500$
- Si el balance sube a 27.000$: limite = 27.000$ - 2.500$ = 24.500$
- El limite NUNCA vuelve a bajar aunque el balance baje

CRITICO: El limite incluye posiciones abiertas,
comisiones Y swaps en tiempo real.

Margen de seguridad recomendado: mantener DD
simulado por debajo del 7% en backtest.

### Dias minimos de trading
- Minimo: 4 dias con al menos 1 posicion INICIADA
- CRITICO: si una posicion dura 3 dias, solo cuenta
  como 1 dia de trading (el dia de apertura)
- Los dias no tienen que ser consecutivos
- No hay maximo de dias

### Sin Regla del Mejor Dia
El 2-Step NO tiene Regla del Mejor Dia.
Ventaja clave para EAs que pueden generar mucho
beneficio en un solo dia de alta volatilidad.

---

## FASE 2 — Verification

### Objetivo de ganancias
- Minimo: +5% del capital inicial
- Cuenta 25.000$: necesitais ganar 1.250$
- Plazo: ilimitado
- Mismos limites de drawdown que el Challenge

### Limites de riesgo
- Daily Loss Limit: 5% — mismas reglas dinamicas
- Max Drawdown: 10% — mismas reglas dinamicas
- Dias minimos: 4 dias con posiciones iniciadas

---

## FTMO Account (cuenta fondeada)

### Profit split
- Base: 80% para el trader, 20% para FTMO
- Escalable hasta 90% con el programa de scaling
- Retiros cada 14 dias

### Limites de riesgo en funded
- Mismos limites dinamicos que en el Challenge
- Daily Loss Limit: 5% dinamico
- Max Drawdown: 10% dinamico
- NO hay dias minimos de trading en la cuenta funded

### Noticias en funded
- En Challenge y Verification: sin restricciones
- En FTMO Account funded: se aplican restricciones
  estandar — verificar antes de operar

---

## REGLAS PARA EAs

### PERMITIDO
- Swing trading
- Trend following
- Mean reversion
- Grid trading con limites de riesgo
- Scalping con timeframe mayor de 2 minutos
- Operar en cualquier sesion
- Mantener posiciones overnight
- Mantener posiciones fin de semana
  (solo en Challenge y Verification)

### PROHIBIDO — DESCALIFICACION INMEDIATA
- HFT (High Frequency Trading)
- Latency arbitrage
- Tick scalping con timeframe menor de 1 minuto
- Martingala o aumento de lote tras perdida
- Copiar señales de otras cuentas FTMO

---

## CALCULO DE VIABILIDAD — CUENTA 25.000$

Objetivo: ganar 2.500$ (10%)
Riesgo por trade: 250$ (1%)
Con ratio TP/SL 2:1 y win rate 50%:
Rendimiento por trade: 250$ x (0.5 x 2 - 0.5) = 125$
Trades necesarios: 20 trades minimo

Con 2 trades por dia en H1:
Dias necesarios: 10 dias — cumple los 4 minimos con margen.

Riesgo violacion Daily Loss (3% operativo = 750$):
Peor caso 2 trades perdedores: 500$ = 2% — DENTRO

Riesgo violacion Max Drawdown (7% operativo = 1.750$):
Max racha perdedora segura: 6 trades consecutivos

---

## CHECKLIST PRE-CHALLENGE

[ ] PF out-of-sample >= 1.5 con comisiones reales
[ ] Max Drawdown simulado < 7%
[ ] Daily Drawdown simulado < 3% por dia
[ ] Minimo 20 trades por mes
[ ] Ratio TP/SL >= 2:1
[ ] Max racha perdedora <= 6 trades consecutivos
[ ] SL definido en todas las operaciones
[ ] TP definido en todas las operaciones
[ ] No usa martingala ni aumenta lotes
[ ] Tipo de estrategia permitido por FTMO
[ ] Walk-Forward Efficiency >= 50%
[ ] Decision humana final: SI