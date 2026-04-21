# Skill: Reglas FTMO 2-Step con Ejemplos Practicos

## Proposito
Guia de referencia rapida para el funding-specialist
y el orchestrator. Incluye ejemplos concretos de
cumplimiento e incumplimiento de cada regla.

---

## REGLAS ACTUALIZADAS FTMO 2026

Fuente: FTMO Terms & Conditions vigentes en 2026.
Verificar en ftmo.com antes de cada challenge — las reglas
pueden cambiar. propfirm-compliance-officer hace hash
check diario para detectar cambios.

### Reglas de drawdown (sin cambios respecto a 2024)
- DD diario: 5% dinamico — calculado desde 00:00 CET/CEST hora Praga
- DD total: 10% dinamico trailing — solo sube, nunca baja
- Dias minimos: 4 dias de trading
- Sin limite de tiempo maximo para el challenge

### Scaling plan FTMO 2026
+25% de capital cada 4 meses si profit >= 5% en ese periodo.
Sin limite superior — cuenta puede crecer indefinidamente.
El sistema de performance-monitor trackea automaticamente
el progreso hacia el siguiente scaling.

### Prohibiciones 2026 — actualizadas
- HFT: definido como multiples trades en segundos
  (FTMO tiene un algoritmo de deteccion automatica)
- Tick scalping: trades con holding < 2 minutos
- Copy trading detectable: patron de ejecucion identico
  a otras cuentas (group trading detection)
- Latency arbitrage: cualquier forma de arbitraje de latencia
- Martingala o position sizing creciente tras perdida
- Copiar señales de otras cuentas FTMO

NUEVO 2026: FTMO ha reforzado la deteccion de group trading.
Ver seccion "Delay Aleatorio Anti-Sincronizacion" en
agents/export-specialist.md — implementacion obligatoria.

---

## MIDNIGHT RESET BUG — CRITICO

### El problema
El DD diario de FTMO se recalcula a las 00:00 hora de Praga
(Europe/Prague — CEST en verano UTC+2, CET en invierno UTC+1).
Si el VPS o el broker usan otra zona horaria, el EA puede
calcular incorrectamente cuando "empieza el nuevo dia".

### Consecuencia del bug
Si el EA cree que el dia empieza a medianoche UTC pero
FTMO usa medianoche Praga (UTC+1 en invierno):
  → El EA acumula perdidas en la ultima hora antes de medianoche Praga
  → FTMO ya cuenta esa hora como "nuevo dia"
  → El EA no sabe que ha empezado un nuevo periodo de computo
  → Puede violar el Daily Loss Limit sin saberlo

### Solucion obligatoria
Usar siempre la zona horaria Europe/Prague para calcular
el limite del dia en el EA.
No usar hora del broker ni hora del servidor VPS directamente.

Implementacion en MQL5:
  // Convertir hora del servidor al timezone de Praga
  // Europe/Prague = UTC+2 CEST (verano) o UTC+1 CET (invierno)
  // El cambio horario es el ultimo domingo de marzo y octubre
  // Ver scripts/ftmo-midnight-sync.mq5 para implementacion completa

Verificar en el forward test:
  [ ] El EA registra el inicio del nuevo dia a las 00:00 Praga
  [ ] No a las 00:00 UTC
  [ ] No a la hora del servidor MT5

---

## POR QUE EL 2-STEP Y NO EL 1-STEP

El 1-Step tiene Daily Loss Limit del 3% — demasiado
restrictivo para EAs de baja frecuencia.
El 2-Step tiene Daily Loss Limit del 5% — casi el
doble de margen de seguridad.
El 2-Step NO tiene Regla del Mejor Dia — ventaja
clave para EAs que pueden ganar mucho en un dia
de alta volatilidad.

---

## REGLAS DEL CHALLENGE FTMO 2-Step (FASE 1)

### Objetivo de beneficio
Regla: alcanzar +10% del capital inicial.
Cuenta 25.000$: necesitais ganar 2.500$.
Plazo: ilimitado.

EJEMPLO CUMPLE:
Balance inicial: 25.000$
Balance final: 27.600$
Beneficio: 2.600$ = 10.4% → PASA

EJEMPLO NO CUMPLE:
Balance inicial: 25.000$
Balance final: 27.400$
Beneficio: 2.400$ = 9.6% → NO PASA

### Daily Loss Limit (5% — DINAMICO)
Regla: no perder mas del 5% del balance
del dia anterior en un dia.
Se recalcula cada medianoche hora de Praga (CEST).
Incluye posiciones abiertas, comisiones y swaps.

Cuenta 25.000$:
Limite inicial: 25.000$ - 1.250$ = 23.750$
Si balance sube a 26.000$: 26.000$ - 1.250$ = 24.750$
Si balance baja a 24.500$: 24.500$ - 1.250$ = 23.250$

Margen operativo recomendado: usar 3% = 750$

EJEMPLO CUMPLE:
Balance dia anterior: 25.000$
Perdida maxima del dia: 700$ = 2.8% → DENTRO

EJEMPLO NO CUMPLE:
Balance dia anterior: 25.000$
Perdida maxima del dia: 1.300$ = 5.2% → VIOLA
Resultado: cuenta cancelada automaticamente.

TRAMPA COMUN:
El limite incluye swaps overnight.
Un swap negativo puede acercaros al limite sin saberlo.

### Max Drawdown (10% — DINAMICO, solo sube)
Regla: el equity nunca puede caer mas del 10%
del balance maximo historico.
El limite SOLO sube cuando el balance sube.
NUNCA vuelve a bajar.

Cuenta 25.000$:
Limite inicial: 22.500$ (10% de 25.000$)
Si balance sube a 27.000$: limite sube a 24.500$
Si luego baja a 25.000$: limite SIGUE en 24.500$

TRAMPA COMUN:
El limite incluye posiciones abiertas en tiempo real.
Equity = balance + perdida/ganancia flotante.
Si teneis posicion abierta con -3.000$ y balance
de 25.000$ → equity = 22.000$ → puede violar limite.

Margen operativo recomendado: DD simulado < 7%

### Dias minimos de trading
Regla: minimo 4 dias con al menos 1 posicion INICIADA.
CRITICO: si una posicion dura 3 dias, solo cuenta
como 1 dia de trading (el dia de apertura).

EJEMPLO CUMPLE:
Dia 1: abre 2 posiciones
Dia 5: abre 1 posicion
Dia 12: abre 3 posiciones
Dia 18: abre 1 posicion
Total: 4 dias → CUMPLE

EJEMPLO NO CUMPLE:
Dia 1: abre 10 posiciones (todo en un dia)
Resto de dias: sin posiciones
Total: 1 dia → NO CUMPLE

### Sin Regla del Mejor Dia en 2-Step
El 2-Step NO tiene esta regla.
Solo existe en el 1-Step.
Ventaja importante para EAs.

---

## REGLAS PARA EAs

### PERMITIDO
- Swing trading
- Trend following
- Mean reversion
- Scalping con timeframe mayor de 2 minutos
- Operar en cualquier sesion
- Mantener posiciones overnight
- Mantener posiciones fin de semana en Challenge

### PROHIBIDO — DESCALIFICACION INMEDIATA
- HFT (High Frequency Trading)
- Latency arbitrage
- Tick scalping con timeframe menor de 1 minuto
- Martingala o aumento de lote tras perdida
- Copiar señales de otras cuentas FTMO

---

## CHECKLIST PRE-APROBACION FTMO

[ ] PF >= 1.5 con comisiones reales
[ ] Max Drawdown simulado < 7%
[ ] Daily Drawdown simulado < 3% por dia
[ ] Minimo 100 trades en periodo de test
[ ] Minimo 20 trades por mes
[ ] Minimo 4 dias con posiciones iniciadas
[ ] Ratio TP/SL >= 2:1
[ ] SL definido en todas las operaciones
[ ] TP definido en todas las operaciones
[ ] No opera en timeframe menor de H1
[ ] No usa martingala ni aumenta lotes
[ ] Tipo de estrategia permitido por FTMO
[ ] Comisiones reales aplicadas en backtest
[ ] WFE >= 50% en Optimizer

Si alguno no se cumple → NO APROBAR.

---

## VERIFICATION FTMO (FASE 2)

Objetivo: +5% del capital inicial.
Cuenta 25.000$: ganar 1.250$.
Plazo: ilimitado.
Mismos limites de drawdown que el Challenge.
Mismos dias minimos: 4 dias con posiciones iniciadas.

---

## CUENTA FUNDED

Profit split base: 80% trader / 20% FTMO.
Escalable hasta 90% con programa de scaling.
Retiros cada 14 dias.
Mismos limites dinamicos de drawdown.
NO hay dias minimos de trading en funded.
Restricciones de noticias aplican en funded.