# Skill: Configuracion del Builder Libre — Sin Sesgo Humano

## Proposito
Define la configuracion completa del Builder de SQ
en modo libre — sin hipotesis humana, sin restriccion
de indicadores, sin sesgo en la logica de entrada.
SQ decide la logica. El humano solo define las
restricciones de riesgo y las comisiones reales.

---

## FILOSOFIA DEL BUILDER LIBRE

El Builder libre se basa en un principio:
el mercado no sabe lo que el humano piensa
que deberia funcionar.

Los Builds 1-8 fallaron porque el humano restringia
el espacio de busqueda a 2-3 indicadores que
consideraba buenos. SQ solo podia encontrar
estrategias dentro de ese espacio limitado.

Con el Builder libre SQ explora millones de
combinaciones de indicadores, condiciones y
parametros que un humano nunca consideraria.
El pipeline de validacion (Retester, paso 12b, WFO)
filtra el sobreajuste automaticamente.

---

## LO QUE EL HUMANO DEFINE (restricciones de riesgo)

Estas restricciones NO se cambian sin consenso:

- Activo y temporalidad: definido por market-selector
- Comisiones reales FTMO: obligatorias siempre
- Ratio TP/SL: minimo 2:1
- Riesgo por trade: 1% del balance
- Max trades por dia: 2
- Sesion: 08:00 a 20:00
- Capital: 25.000 USD
- Periodo IS: 2003.05.05 a 2020.12.31
- Periodo OOS: 2021.01.01 a fecha actual

## LO QUE SQ DECIDE (logica de entrada)

SQ tiene libertad total para elegir:

- Que indicadores usar
- Cuantas condiciones de entrada (1 a 3)
- Que combinaciones de señales
- Que parametros dentro de los rangos
- Direccion de las operaciones (long, short o ambas)
- Tipo de salida dentro de las restricciones ATR

---

## CONFIGURACION TAB POR TAB

### Tab Datos — EUR/USD
Motor: MetaTrader5 (netted)
Simbolo: EURUSD_M1_dukas
Temporalidad: H1
Fecha inicio: 2003.05.05
Fecha fin: 2020.12.31
Precision: 1 minute data tick simulation

Comisiones (clic en engranaje):
- Spread: 0.5 pips
- Comision: 7 USD por lote
- Slippage: 0.5 pips

### Tab Datos — XAU/USD
Motor: MetaTrader5 (netted)
Simbolo: XAUUSD_M1_dukas
Temporalidad: H1
Fecha inicio: 2003.05.05
Fecha fin: 2020.12.31
Precision: 1 minute data tick simulation

Comisiones (clic en engranaje):
- Spread: 30 pips
- Comision: 7 USD por lote
- Slippage: 2 pips

VERIFICAR pip size XAU/USD en SQ antes de lanzar:
- Si pip size = 0.01 → introducir 30 pips
- Si pip size = 0.1 → introducir 3 pips

---

### Tab Que construir

Tipo: Simple strategy
Condiciones de entrada: Min 1, Max 3

Stop Loss:
- Required: ACTIVADO siempre
- Tipo: ATR-based
- Multiplicador Min: 1.5
- Multiplicador Max: 3.0
- Periodo ATR: 14

Take Profit:
- Required: ACTIVADO siempre
- Tipo: ATR-based
- Multiplicador Min: 3.0
- Multiplicador Max: 6.0
- Periodo ATR: 14
- Ratio minimo sobre SL: 200%

Direcciones: Long y Short habilitados sin simetria

NOTA: Los rangos de SL y TP son mas amplios que
en el enfoque anterior para que SQ explore mas
espacio. El ratio minimo 2:1 se garantiza con
el porcentaje minimo del 200% sobre el SL.

---

### Tab Bloques de construccion — PALETA COMPLETA

CRITICO: Activar TODOS los bloques siguientes.
No restringir la logica de entrada a indicadores
especificos. SQ decide que combinaciones funcionan.

#### Señales predefinidas — ACTIVAR TODAS
Grupo de cruces:
- EMA cruza por encima/debajo de otra EMA
- SMA cruza por encima/debajo de otra SMA
- Precio cruza por encima/debajo de indicador
- MACD cruza la linea de señal
- Stochastic cruza niveles

Grupo de niveles:
- RSI por encima/debajo de nivel
- ADX por encima/debajo de nivel
- CCI por encima/debajo de nivel
- Williams %R por encima/debajo de nivel
- Stochastic por encima/debajo de nivel

Grupo de rupturas:
- Precio rompe Highest High de N velas
- Precio rompe Lowest Low de N velas
- Precio rompe banda superior/inferior de Bollinger
- Precio rompe canal de Donchian
- Precio rompe canal de Keltner

Grupo de tendencia:
- Precio por encima/debajo de EMA
- Precio por encima/debajo de SMA
- ADX subiendo/bajando
- Aroon subiendo/bajando
- Parabolic SAR por encima/debajo del precio

#### Indicadores — ACTIVAR TODOS LOS GRUPOS

Grupo tendencia:
- EMA (Media movil exponencial)
- SMA (Media movil simple)
- DEMA (Media movil exponencial doble)
- HMA (Media movil Hull)
- ADX (Indice direccional medio)
- Aroon
- Parabolic SAR

Grupo momentum:
- RSI (Indice de fuerza relativa)
- Stochastic (Estocastico)
- CCI (Indice de canal de commodities)
- MACD (Convergencia/divergencia de medias)
- Williams %R
- Momentum
- ROC (Rate of Change)
- DeMarker

Grupo volatilidad:
- ATR (Rango medio real)
- Bollinger Bands (Bandas de Bollinger)
- Keltner Channel
- Donchian Channel
- Standard Deviation

Grupo precio puro:
- High (Maximo)
- Low (Minimo)
- Close (Cierre)
- Open (Apertura)
- HL2 (Media High-Low)
- HLC3 (Media High-Low-Close)
- Highest (Maximo de N velas)
- Lowest (Minimo de N velas)
- Range (Rango de la vela)

#### Operators — ACTIVAR TODOS
- > Mayor que
- < Menor que
- >= Mayor o igual
- <= Menor o igual
- == Igual
- Cruza por encima (crosses above)
- Cruza por debajo (crosses below)
- Esta subiendo (is rising)
- Esta bajando (is falling)

#### Tipos de pedido
- MKT Entrar en el mercado

#### Tipos de salida
- Objetivo de beneficios: REQUERIDO (ATR-based)
- Stop Loss: REQUERIDO (ATR-based)
- Tope dinamico: DESACTIVADO
- Trailing: DESACTIVADO
- Salida por barras: DESACTIVADO

#### Bloques de entrada parada/limite
- ATR — Rango medio real
- C — Cerrar (precio de cierre)
- H — Alto
- L — Bajo

---

### Tab Opciones geneticas — MODO CONTINUO

Max Generations: 30
Population Size: 100 por isla
Islands: 4
Start again when finished: ACTIVADO
Filter initial population: sin filtro

CRITICO: Start again when finished ACTIVADO.
El Builder corre indefinidamente en ciclos.
Cada ciclo nuevo explora combinaciones diferentes.
Dejar correr minimo 24-48 horas.
El humano lo para manualmente cuando quiera.

Diferencia con el enfoque anterior:
- Antes: 20 generaciones, 50 por isla, se paraba solo
- Ahora: 30 generaciones, 100 por isla, corre indefinido
- Resultado: espacio de busqueda 6x mayor como minimo

---

### Tab Opciones de negociacion

Limitar intervalo de tiempo: ACTIVADO
Rango desde: 08:00
Rango hasta: 20:00
Maximo trades por dia: 2
Salida al final del dia: ACTIVADO
No comercie fines de semana: ACTIVADO
Salida el viernes: ACTIVADO

Sin cambios respecto al enfoque anterior.
Estas son restricciones de riesgo, no de logica.

---

### Tab Gestion del dinero

Capital inicial: 25.000 USD
Metodo: Riesgo fijo en % de la cuenta
Riesgo por trade: 1%

Sin cambios. Nunca modificar esto.

---

### Tab Clasificacion — FILTROS AJUSTADOS

Maximum strategies to store: 1000
Stop generation: Never

CRITICO: Stop generation en Never.
El Builder corre indefinidamente.
Las mejores 1000 estrategias van al databank
reemplazando las peores continuamente.

Filtros personalizados:
- Factor de beneficio > 1.3
  (subimos de 0.8 para filtrar mas en el Builder)
- Transacciones medias al mes > 6
- Ratio Ret/DD > 0.8
  (subimos de 0.5 para mayor calidad)

Ranking: Aptitud ponderada
- Profit Factor: Maximice, Peso 3
- Max Drawdown %: Minimizar, Peso 2
- Number of Trades: Maximice, Peso 1

---

### Tab Comprobaciones cruzadas

Mayor precision de las pruebas: ACTIVADO
Monte Carlo gestion de operaciones: ACTIVADO
Todo lo demas: DESACTIVADO

NUEVO: Monte Carlo gestion de operaciones añade
robustez al filtrado. Descarta estrategias que
dependen de un orden especifico de las operaciones.

---

## VERIFICACION FINAL EN PESTANA PROGRESO

Antes de lanzar verificar que muestra:
[ ] Simbolo correcto
[ ] Temporalidad H1
[ ] Fechas 2003.05.05 a 2020.12.31
[ ] Sesion 08:00 a 20:00
[ ] Risk 1% of account
[ ] Max 2 trades por dia
[ ] Comisiones aplicadas
[ ] Start again when finished: ACTIVADO
[ ] Stop generation: Never
[ ] Monte Carlo: ACTIVADO
[ ] Max strategies: 1000

---

## TIEMPO ESTIMADO DE BUILD

Modo continuo 24 horas: ~2000-4000 estrategias evaluadas
Modo continuo 48 horas: ~4000-8000 estrategias evaluadas
Modo continuo 72 horas: ~6000-12000 estrategias evaluadas

Recomendacion: dejar correr minimo 48 horas.
Parar cuando el PF maximo del databank no suba
durante 4-6 horas consecutivas — eso indica que
el espacio de busqueda esta agotandose.

---

## CUANDO PARAR EL BUILD

Señales de que es momento de parar:

1. PF maximo en databank no mejora en 6+ horas
2. Se han completado mas de 5 ciclos completos
3. Hay mas de 50 estrategias con PF > 1.5
4. Han pasado 72 horas

Señales de que hay que seguir:

1. PF maximo sigue subiendo cada hora
2. El databank se esta llenando rapidamente
3. Hay pocas estrategias con PF > 1.5

---

## DIFERENCIAS CON EL ENFOQUE ANTERIOR

| Aspecto | Antes | Ahora |
|---------|-------|-------|
| Indicadores activos | 2-3 | Todos (+100) |
| Hipotesis previa | Obligatoria | Ninguna |
| Generaciones | 20 | 30 por ciclo continuo |
| Poblacion por isla | 50 | 100 |
| Modo | Se para solo | Corre indefinido |
| Max estrategias | 500 | 1000 |
| PF minimo filtro | 0.8 | 1.3 |
| Monte Carlo | Desactivado | Activado |
| Sesgo humano | En la logica | Solo en el riesgo |

---

## REGLA FUNDAMENTAL

El humano define las restricciones de riesgo.
SQ define la logica de entrada.
El pipeline de validacion filtra el sobreajuste.
Nadie interviene en la seleccion de estrategias.