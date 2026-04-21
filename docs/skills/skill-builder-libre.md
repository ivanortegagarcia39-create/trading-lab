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
- Spread: 3 pips (pip size confirmado = 0.1)
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

Opciones geneticas avanzadas:
Crossover Probability: 93%
Mutation Probability: 30%

Islands options:
Migrate every Xth generation: 10
Population migration rate: 6%

NOTA: Migrate every 10 generaciones permite
que las 4 islas intercambien material genetico
3 veces por ciclo de 30 generaciones.
Valores por debajo de 5 aceleran convergencia
prematura. Valores por encima de 15 reducen
diversidad entre islas.

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

#### Filtros disponibles en SQ Build 143

Disponibles y configurados en el Builder:
- Transacciones medias al mes (trades/mes)
- Factor de beneficio (PF)
- Ratio Ret/DD

NO disponibles en el Builder (SQ Build 143):
- Total Trades (numero total de operaciones)
- Win Rate (porcentaje de operaciones ganadoras)
- Max Drawdown % (maximo drawdown porcentual)

Estos tres filtros se aplican en Python post-build
a traves del evaluator-assistant procesando los CSVs
exportados del databank. No es un problema — el
Evaluation Gate los aplica automaticamente.

Ranking: Aptitud ponderada
- Profit Factor: Maximice, Peso 3
- Max Drawdown %: Minimizar, Peso 2
- Number of Trades: Maximice, Peso 1

---

### Tab Comprobaciones cruzadas

Mayor precision de las pruebas: ACTIVADO
Monte Carlo gestion de operaciones: DESACTIVADO
Todo lo demas: DESACTIVADO

NOTA: Monte Carlo se aplica en el Retester, no en el Builder.
Activarlo en el Builder ralentiza la generacion sin beneficio
adicional ya que el Retester lo aplicara sobre candidatas
ya filtradas.

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
[ ] Monte Carlo en Builder: DESACTIVADO (se aplica en Retester)
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
| Monte Carlo en Builder | Desactivado | Desactivado (se aplica en Retester) |
| Sesgo humano | En la logica | Solo en el riesgo |

---

## CONFIGURACION H4 (Fase 9 — Produccion Core)

Activa cuando market-selector elija H4 como temporalidad optima.
Los parametros H1 son validos salvo estas diferencias:

| Parametro | H1 | H4 |
|-----------|----|----|
| Trades minimos | 120 | 50 |
| Trades/mes minimos | 8 | 3 |
| Tiempo de build minimo | 48h | 72h |
| Periodo OOS minimo | 5 años (2021-actual) | 3 años (2023-actual) |
| Generaciones por ciclo | 30 | 30 |

Razon del OOS de 3 años en H4:
Con H4 hay menos velas en el mismo periodo de tiempo.
Un OOS de 5 años en H4 tiene ~2.500 velas H4 frente
a ~10.000 velas H1. Con 3 años ya hay suficiente muestra
para el Retester y el WFO.

Razon de 72h de build minimo:
Una vela H4 dura 4 horas. El Builder necesita mas
tiempo para generar y evaluar el mismo numero de
candidatas porque hay menos velas disponibles por
hora de calculo.

---

## CONFIGURACION M30 (Incubadora Tactica)

Solo para I+D — nunca va directo a produccion.
Siempre pasa por validacion adicional antes del portfolio.

### Diferencias respecto a H1

| Parametro | H1 | M30 |
|-----------|----|----|
| ATR SL multiplicador | 1.5-3.0 | 1.0-2.0 (mas ajustado) |
| ATR TP multiplicador | 3.0-6.0 | 2.0-4.0 |
| Trades minimos | 120 | 180 |
| Trades/mes minimos | 8 | 15 |
| Test Estres Velocidad | No requerido | OBLIGATORIO |
| Max slippage config | +0.5 pips extra | +0.5 pips extra |

### Test de Estres de Velocidad obligatorio para M30
Antes de pasar el WFO, ejecutar en 2 años completos
aunque el build usara ventana IS de 6 meses.
PF > 1.2 en cada uno de los 2 años.
Ver skill-evaluation-auto.md — seccion Test de Estres.

### Ruta al portfolio para M30
M30 aprobada por pipeline → skill-timeframe-selector.md
confirma viabilidad → portfolio secundario.
No va al mismo portfolio que las H1 de produccion principal
hasta que el portfolio H1 este completo (3+ estrategias).

---

## SLIPPAGE VARIABLE POR HORARIO

El slippage real no es constante durante el dia.
Las comisiones fijas del Builder no capturan esta variacion.
Compensar en la configuracion del simbolo en SQ Data Manager.

| Sesion | Horario (CEST) | Factor slippage | Slippage EURUSD | Slippage XAUUSD |
|--------|---------------|----------------|-----------------|-----------------|
| Asiatica | 00:00-08:00 | 3x | 1.5 pips | 6 pips |
| Apertura Londres | 08:00-09:00 | 2x | 1.0 pip | 4 pips |
| Sesion normal (core) | 09:00-13:00 | 1x (base) | 0.5 pips | 2 pips |
| Overlap Londres-NY | 13:00-17:00 | 1x (base) | 0.5 pips | 2 pips |
| Tarde NY | 17:00-20:00 | 1x (base) | 0.5 pips | 2 pips |
| Cierre NY | 20:00-22:00 | 2x | 1.0 pip | 4 pips |

El Builder opera en la sesion 08:00-20:00 por configuracion.
Los peores momentos dentro de la sesion son la apertura
de Londres y el cierre NY. El slippage configurado en SQ
(0.5 pips EURUSD, 2 pips XAUUSD) es el valor del core.

Para builds sobre activos con alta sensibilidad al horario
(indices principalmente) usar el factor 2x como base.

---

## SWAP OVERNIGHT — VALORES FTMO ACTUALES

Los swaps afectan directamente la rentabilidad de
estrategias que mantienen posiciones overnight.
Verificar en el simbolo [ACTIVO]_ftmo antes de lanzar el Builder.

### Valores FTMO vigentes (verificar antes de cada build)

| Activo | Swap Long (USD/lote/noche) | Swap Short (USD/lote/noche) |
|--------|--------------------------|----------------------------|
| XAUUSD | -50.63 | +17.67 |
| EURUSD | -8.05 | +2.18 |
| GBPUSD | (verificar en FTMO) | (verificar en FTMO) |
| USDJPY | (verificar en FTMO) | (verificar en FTMO) |

**Triple swap miercoles:** multiplicar x3 el valor de la noche.
Ejemplo XAUUSD long miercoles: -50.63 * 3 = -151.89 USD/lote

### Como configurar en SQ
SQ → Data Manager → Simbolo [ACTIVO]_ftmo → Propiedades
→ Swap Long / Swap Short
→ Tipo de swap: en puntos o USD/lote segun el broker

### Impacto en la evaluacion
Ver skill-evaluation-auto.md:
  - Triple swap miercoles > 15% del beneficio neto → DESCARTAR
  - PF post-swaps < 80% del PF pre-swaps → DESCARTAR

Si el swap long del activo es muy negativo (como XAUUSD),
las estrategias Long-only tienen una desventaja estructural.
El Builder libre lo detectara y generara mas estrategias Short
o mixtas — dejar que SQ decida.

---

## BACKTEST SUCIO — SPREAD DOBLE OBLIGATORIO

Todos los builds deben configurar el spread en SQ como el
DOBLE del spread real de FTMO. Esto garantiza que las
estrategias aprobadas son robustas incluso si el spread
se amplia momentaneamente durante eventos de liquidez.

Una estrategia que solo funciona con el spread justo
del broker real falla en produccion al primer evento
de baja liquidez. El backtest sucio filtra estas
estrategias fragiles antes de que lleguen al WFO.

### Spreads configurados en SQ (backtest sucio)

| Activo | Spread real FTMO | Spread SQ (x2) | Como verificar |
|--------|-----------------|----------------|----------------|
| XAUUSD | 30 pips | 60 pips | pip size = 0.01 → introducir 60 |
| EURUSD | 0.5 pips | 1.0 pip | pip size = 0.0001 → introducir 1.0 |
| GBPUSD | 0.8 pips | 1.6 pips | pip size = 0.0001 → introducir 1.6 |
| USDJPY | 0.5 pips | 1.0 pip | pip size = 0.01 → introducir 1.0 |
| AUDUSD | 0.6 pips | 1.2 pips | pip size = 0.0001 → introducir 1.2 |
| NZDUSD | 0.8 pips | 1.6 pips | pip size = 0.0001 → introducir 1.6 |
| USDCAD | 0.7 pips | 1.4 pips | pip size = 0.0001 → introducir 1.4 |
| USDCHF | 0.7 pips | 1.4 pips | pip size = 0.0001 → introducir 1.4 |
| XAGUSD | 3 pips | 6 pips | verificar pip size antes |

Para activos no listados: multiplicar el spread real x2.
Verificar SIEMPRE el pip size del simbolo en SQ antes
de introducir el valor. El mismo numero tiene distinto
impacto segun si el pip size es 0.01 o 0.0001.

### Configuracion en SQ

SQ → Tab Datos → clic en engranaje del simbolo → Spread
Introducir el valor de la columna "Spread SQ (x2)".

La comision y el slippage NO se doblan — son costes
fijos que ya estan correctamente calibrados con los
valores reales de FTMO.

---

## METRICA DE CALIDAD DE SIMULACION

La calidad del backtest depende del porcentaje de ticks
reales disponibles vs ticks simulados por SQ.
Un backtest con muchos ticks simulados puede tener
resultados irreproducibles en produccion.

### Como comprobar en SQ

SQ → Tab Progreso → Seccion "Simulation statistics"
→ Campo "Modelling quality" o "Tick coverage"

El valor se muestra como porcentaje al finalizar el build.

### Criterios de calidad

| Cobertura de ticks | Calidad | Accion |
|-------------------|---------|--------|
| >= 80% | Aceptable | Sin accion |
| 60-79% | Baja | Advertencia en informe post-build |
| < 60% | Inaceptable | ADVERTENCIA CRITICA — resultados no fiables |

### Formato de la advertencia en el informe post-build

Si cobertura < 80%:

```
ADVERTENCIA: Calidad de simulacion baja.
Cobertura de ticks: [valor]%
Umbral minimo: 80%
Causa probable: datos M1 con huecos o periodo fuera
del rango disponible en Dukascopy.
Accion: verificar calidad de datos en data-manager.
Las metricas de este build pueden ser menos fiables.
```

Si cobertura < 60%, ademas:

```
ADVERTENCIA CRITICA: Cobertura de ticks < 60%.
Los resultados de este build NO son fiables.
Detener el proceso — no avanzar al Evaluation Gate
hasta resolver la calidad de los datos.
```

### Quien registra la advertencia

El evaluator-assistant lee el informe post-build del
orchestrator que incluye la cobertura de ticks.
Si cobertura < 80% → incluir la advertencia en el
informe del Evaluation Gate para cada estrategia
del build afectado.

---

## ESTANDAR DE TERMINAL DEL PROYECTO

Para todas las operaciones con datos de SQ y scripts
de validacion, el proyecto usa los siguientes estandares:

| Herramienta | Cuando usar |
|-------------|-------------|
| PowerShell / CMD | Comandos de sistema, git, instalar software |
| Python directo | Manipulacion de datos SQ — SIEMPRE Python, nunca PowerShell |

**Separador CSV de SQ:** punto y coma (;) — no coma

**Razon critica:** PowerShell corrompe los CSVs de SQ cuando
el separador es punto y coma y los numeros usan coma decimal
(formato europeo). Python maneja este formato correctamente
con csv.DictReader(delimiter=";") y el parse_european_number
que los scripts de este proyecto implementan.

Ejemplo incorrecto (PowerShell):
  Import-Csv archivo.csv  ← asume coma como separador

Ejemplo correcto (Python):
  python validate-sqx-build.py --baseline a.csv --new b.csv

---

## REGLA FUNDAMENTAL

El humano define las restricciones de riesgo.
SQ decide la logica de entrada.
El pipeline de validacion filtra el sobreajuste.
Nadie interviene en la seleccion de estrategias.