# Configuracion Estandar del Retester — TradingLab

## Proposito
Referencia rapida con la configuracion exacta
del Retester de StrategyQuant para todos los
tests out-of-sample del proyecto.
Las comisiones deben ser IDENTICAS al Builder.

---

## REGLA CRITICA ANTES DE EMPEZAR

Verificar que las comisiones son exactamente
iguales a las del Builder antes de lanzar.
Si son diferentes los resultados no son
comparables y la seleccion de candidatas
es erronea.

---

## COMO CARGAR LAS ESTRATEGIAS

NO usar el databank por defecto del Retester.
Puede tener estrategias de otras sesiones.

Metodo correcto:
1. En Retester → boton Carga en barra superior
2. Navegar a results\reviewed\
3. Seleccionar los archivos .sqx correctos
4. Verificar que aparecen en la tabla del Retester

---

## CONFIGURACION TAB POR TAB

### Tab Datos — EUR/USD
Motor: MetaTrader5 (netted)
Simbolo: EURUSD_M1_dukas
Temporalidad: H1
Fecha inicio: 2021.01.01
Fecha fin: fecha actual
Precision: 1 minute data tick simulation
Sin division de intervalo — periodo OOS completo

Comisiones (clic en engranaje):
- Spread: 0.5 pips
- Comision: 7 USD por lote
- Slippage: 0.5 pips

### Tab Datos — XAU/USD
Motor: MetaTrader5 (netted)
Simbolo: XAUUSD_M1_dukas
Temporalidad: H1
Fecha inicio: 2021.01.01
Fecha fin: fecha actual
Precision: 1 minute data tick simulation
Sin division de intervalo

Comisiones (clic en engranaje):
- Spread: 30 pips
- Comision: 7 USD por lote
- Slippage: 2 pips

VERIFICAR pip size del XAU/USD en SQ antes
de introducir el spread:
- Si pip size = 0.01 → introducir 30 pips
- Si pip size = 0.1 → introducir 3 pips

---

### Tab Opciones de negociacion
Mismos ajustes que en el Builder:
- Limitar intervalo de tiempo: ACTIVADO
- Rango: 08:00 a 20:00
- Max trades por dia: 2
- Salida al final del dia: ACTIVADO
- No comercie fines de semana: ACTIVADO
- Salida el viernes: ACTIVADO

---

### Tab Gestion del dinero
- Metodo: Riesgo fijo en % de la cuenta
- Riesgo: 1%
- Capital: 25.000$

---

### Tab Clasificacion
- Filtros personalizados: TODOS DESACTIVADOS
  No filtrar en el Retester — queremos ver
  los resultados reales de todas las candidatas
- Ranking: Aptitud ponderada
  PF: Maximice Peso 3
  Max Drawdown: Minimizar Peso 2
  Trades: Maximice Peso 1

---

### Tab Comprobaciones cruzadas
- Mayor precision: ACTIVADO
- Todo lo demas: DESACTIVADO

---

## VERIFICACION FINAL ANTES DE LANZAR

[ ] Simbolo correcto — mismo que en el Builder
[ ] Temporalidad H1 — mismo que en el Builder
[ ] Fechas OOS: 2021.01.01 a fecha actual
[ ] Comisiones IDENTICAS al Builder
[ ] Sin division de intervalo de datos
[ ] Estrategias cargadas desde results\reviewed\
[ ] Filtros de clasificacion DESACTIVADOS
[ ] Capital 25.000$ y riesgo 1%

---

## TIEMPO ESTIMADO

El Retester es mas rapido que el Builder.
Por estrategia individual:
- EUR/USD H1 periodo 2021-2026: 5-15 minutos
- XAU/USD H1 periodo 2021-2026: 5-15 minutos

Para 6 candidatas: 30-90 minutos aproximadamente.

---

## ORDEN DE RETESTEO

Cuando hay varios candidatos retestear en orden
de prioridad — no todos a la vez:

1. Primero: mayor PF in-sample
2. Segundo: menor drawdown
3. Tercero: mas trades

Retestear uno, revisar resultado y decidir
si continuar con los siguientes.
Si el primero falla el paso 12b analizar
si tiene sentido retestear los demas.

---

## INTERPRETACION DE RESULTADOS

### PASA el Retester si
- PF OOS >= 1.3
- PF no cae mas del 30% respecto al IS
- DD OOS <= 7%
- Trades proporcionales al periodo
- Consistencia por trimestres

### Caida maxima permitida del PF
Formula: PF IS x 0.70 = PF minimo OOS

Ejemplo:
PF IS: 1.8
PF minimo OOS: 1.8 x 0.70 = 1.26
Si PF OOS = 1.35 → PASA
Si PF OOS = 1.15 → NO PASA

### REVISAR si
- PF cae entre 20% y 30%
- Un trimestre muy malo pero el resto consistente

### DESCARTAR si
- PF OOS < 1.3
- PF cae mas del 30%
- DD OOS > 7%
- Comportamiento completamente distinto al IS

---

## DONDE GUARDAR LOS RESULTADOS

Estrategias que PASAN:
results\reviewed\ con sufijo -retested
Ejemplo: NBAR-001-retested.sqx

Estrategias que NO PASAN:
results\rejected\ con sufijo -retester-fail
Ejemplo: NBAR-001-retester-fail.sqx

Configuracion del Retester ejecutado:
strategyquant\retester\[nombre]-retester-config.md

Informe IS vs OOS para paso 12b:
strategyquant\retester\[nombre]-IS-vs-OOS-report.md

---

## APRENDIZAJES CRITICOS

Build 4: Retester negativo porque el Builder
se lanzo sin comisiones reales.
→ Siempre comisiones reales desde el Builder.

Build 5-6: Retester con comisiones correctas
mostro PF insuficiente en M15.
→ H1 como temporalidad principal desde Build 7.

Regla fundamental:
Si el Builder se lanzo sin comisiones reales
o con comisiones incorrectas el Retester
no servira para comparar resultados.
Relanzar el Builder con comisiones correctas.