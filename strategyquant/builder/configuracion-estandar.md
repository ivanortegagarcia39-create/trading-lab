# Configuracion Estandar del Builder — TradingLab

## Proposito
Referencia rapida con la configuracion exacta tab por tab
para el Builder de StrategyQuant.
Usar en todos los builds sin excepcion.
Basada en los aprendizajes de los Builds 1-7.

---

## TAB: QUE CONSTRUIR

Tipo de estrategia: Simple strategy (default)
NO usar Multi-TF — genera errores de subfichas duplicadas

Stop Loss:
- Required: ACTIVADO siempre
- Tipo: ATR-based
- Multiplicador Min: 1.5
- Multiplicador Max: 2.5
- Periodo ATR: 10-20

Take Profit:
- Required: ACTIVADO siempre
- Tipo: ATR-based
- Multiplicador Min: 3.0 (ratio minimo 2:1 sobre SL)
- Multiplicador Max: 5.0
- Periodo ATR: 10-20

Direcciones: Ambos (Long y Short) sin simetria
Numero de condiciones: Min 1, Max 3

---

## TAB: DATOS

### EUR/USD
Motor: MetaTrader5 (netted)
Simbolo: EURUSD_M1_dukas
Temporalidad: H1
Fecha inicio: 2003.05.05
Fecha fin: 2020.12.31
Precision: 1 minute data tick simulation
Partes del intervalo: bloque 50/20/30

Comisiones (clic en engranaje):
- Spread: 0.5 pips
- Comision: 7 USD por lote
- Slippage: 0.5 pips

### XAU/USD
Motor: MetaTrader5 (netted)
Simbolo: XAUUSD_M1_dukas
Temporalidad: H1
Fecha inicio: 2003.05.05
Fecha fin: 2020.12.31
Precision: 1 minute data tick simulation
Partes del intervalo: bloque 50/20/30

Comisiones (clic en engranaje):
- Spread: 30 pips
- Comision: 7 USD por lote
- Slippage: 2 pips

CRITICO XAU/USD: verificar pip size en SQ antes de lanzar
Si pip size = 0.01 → introducir 30 pips (correcto)
Si pip size = 0.1 → introducir 3 pips

---

## TAB: OPCIONES GENETICAS

Max Generations: 20
Population Size: 50 por isla
Islands: 4
Start again when finished: DESACTIVADO
Filter initial population: sin filtro

NUNCA usar 100 generaciones — el build duraria 88+ horas.
NUNCA activar Start again — el build nunca terminaria.

---

## TAB: OPCIONES DE NEGOCIACION

Limitar intervalo de tiempo: ACTIVADO
Rango desde: 08:00
Rango hasta: 20:00
Maximo trades por dia: 2
Salida al final del dia: ACTIVADO
No comercie fines de semana: ACTIVADO
Salida el viernes: ACTIVADO

---

## TAB: GESTION DEL DINERO

Capital inicial: 25.000$
Metodo: Riesgo fijo en % de la cuenta
Riesgo por trade: 1%

NUNCA usar tamaño fijo de lote.
NUNCA usar riesgo mayor del 1%.

---

## TAB: BLOQUES DE CONSTRUCCION

### Para hipotesis NBARBreakout-RSI
Signals activar solo:
- RSI esta por encima del nivel
- RSI esta por debajo del nivel

Indicadores activar:
- RSI
- Highest High
- Lowest Low
- ATR

Operators activar:
- (>=) Mayor o igual
- (<=) Menor o igual

Tipos de pedido:
- (MKT) Entrar en el mercado

Tipos de salida:
- Objetivo de beneficios: requerido
- Stop Loss: requerido
- Tope dinamico: DESACTIVADO
- Trailing: DESACTIVADO
- Salida por barras: DESACTIVADO

Bloques entrada parada/limite:
- (ATR) Rango medio real
- (MTATR) Rango real medio
- (H) Alto
- (L) Bajo
- (C) Cerrar

### Para hipotesis TrendFollowing EMA-ADX
Signals activar solo:
- El ADX supera el nivel
- ADX esta por encima del nivel
- ADX esta por debajo del nivel

Indicadores activar:
- EMA Media movil exponencial
- ATR

Operators activar:
- (>=) Mayor o igual
- (<=) Menor o igual

Tipos de pedido y salida: igual que arriba

### Para hipotesis MeanReversion RSI
Signals activar solo:
- RSI esta por encima del nivel
- RSI esta por debajo del nivel

Indicadores activar:
- RSI
- EMA Media movil exponencial
- ATR

Operators activar:
- (>=) Mayor o igual
- (<=) Menor o igual

Tipos de pedido y salida: igual que arriba

---

## TAB: CLASIFICACION

Maximum strategies to store: 500
Stop generation: Databank is full
Strategy Quality ranking: Aptitud ponderada

Metricas de ranking:
- Profit Factor: Maximice, Peso 3
- Max Drawdown %: Minimizar, Peso 2
- Number of Trades: Maximice, Peso 1

Filtros personalizados:
- Factor de beneficio > 0.8
- Transacciones medias al mes > 8
- Ratio Ret/DD > 0.5

---

## TAB: COMPROBACIONES CRUZADAS

Mayor precision de las pruebas: ACTIVADO
Todo lo demas: DESACTIVADO

---

## VERIFICACION FINAL EN PESTANA PROGRESO

Antes de clicar Inicio verificar que el resumen muestra:
[ ] Simbolo correcto
[ ] Temporalidad H1
[ ] Fechas 2003.05.05 a 2020.12.31
[ ] Sesion 08:00 a 20:00
[ ] Risk 1% of account
[ ] Max 2 trades por dia
[ ] Comisiones aplicadas

---

## TIEMPO ESTIMADO DE BUILD

EUR/USD H1 con 18 anos de datos: 6-12 horas
XAU/USD H1 con 18 anos de datos: 6-12 horas
Lanzar siempre en horario nocturno.

---

## SEÑALES DE QUE EL BUILD VA BIEN

A los 30 minutos:
- Estrategias generandose a 8-10 segundos por estrategia
- "En la base de datos" empieza a subir despues
  de las primeras 200 estrategias generadas

A las 2 horas:
- Contador de estrategias sigue subiendo
- Algunas estrategias en databank

Build terminado correctamente:
- Boton verde "Inicio" visible
- Log parado
- Estrategias en Last Generation y Results

---

## COMO GUARDAR RESULTADOS AL TERMINAR

1. Pestana Results → Guardar → Guardar en formato SQ X
   → navegar a results\raw\build-results\

2. Pestana Last Generation → Guardar → mismo formato
   → navegar a results\raw\last-generation\

3. Hacer commit de Git inmediatamente despues