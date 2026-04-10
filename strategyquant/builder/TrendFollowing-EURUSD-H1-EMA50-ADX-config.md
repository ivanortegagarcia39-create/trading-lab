# Configuracion Builder — Build 8
Hipotesis de origen: TrendFollowing-EURUSD-H1-EMA50-ADX
Ticket: TICKET-001
Fecha generada: 2026-04-10
Generada por: sq-specialist
Mercado: EUR/USD
Temporalidad: H1
Tipo: Simple strategy
Verificado contra skill-sq-builder.md: SI
Checklist pre-build completado: SI
Datos verificados por data-manager: SI (sesion 2026-04-10)
Funding-specialist ha confirmado compatibilidad FTMO: SI

---

## VERIFICACION DE HIPOTESIS

Condicion Long 1: Close is above EMA(50) — nativo en SQ (precio por encima de indicador) ✓
Condicion Long 2: ADX(14) is above level 20 — nativo en SQ (indicador por encima de nivel) ✓
Condicion Short 1: Close is below EMA(50) — nativo en SQ ✓
Condicion Short 2: ADX(14) is above level 20 — nativo en SQ ✓
Sin logica de sesion asiatica ✓
Sin logica de noticias ✓
Sin logica de dias de la semana ✓
Riesgo sobreajuste: BAJO (2 indicadores, parametros estandar, logica simetrica) ✓

---

## CHECKLIST PRE-BUILD COMPLETO

### BLOQUE 1 — VERIFICACION DE DATOS
[x] Los datos del mercado estan importados en SQ
[x] El simbolo correcto: EURUSD_M1_dukas
[x] La fecha de inicio del build: 2003.05.05
[x] La fecha de fin es 2020.12.31 — datos OOS fuera
[x] Los datos 2021-2026 NO incluidos en el build
[x] El periodo cubre 17 anos de datos (2003-2020)
[x] La temporalidad M1 disponible para conversion a H1

### BLOQUE 2 — VERIFICACION DE HIPOTESIS
[x] La hipotesis tiene todos los campos obligatorios
[x] La logica se explica en una frase: "Entrar en tendencia cuando precio > EMA(50) y ADX > 20"
[x] Cada condicion verificada contra skill-sq-builder.md — todas nativas
[x] No hay logica de rango de sesion asiatica
[x] No hay logica de noticias economicas
[x] No hay logica de dias de la semana en entradas
[x] SL es ATR-based (ATR x 2.0, rango 1.8-2.2)
[x] TP es ATR-based con ratio 2.25:1 sobre el SL (ATR x 4.5, rango 4.0-5.0)
[x] Ventana de sesion: 08:00-20:00 = 12 horas (cumple minimo 6h)
[x] Temporalidad H1 confirmada
[x] Funding-specialist ha confirmado compatibilidad FTMO

### BLOQUE 3 — CONFIGURACION EN SQ (verificar antes de clicar Inicio)

#### Tab: Datos
[x] Motor: MetaTrader5 (netted)
[x] Simbolo: EURUSD_M1_dukas
[x] Temporalidad: H1
[x] Fecha inicio: 2003.05.05
[x] Fecha fin: 2020.12.31
[x] Precision: 1 minute data tick simulation
[x] Partes del intervalo: bloque 50/20/30
[x] Spread: 0.5 pips
[x] Comision: 7 USD por lote
[x] Slippage: 0.5 pips

#### Tab: Que construir
[x] Tipo: Simple strategy
[x] Stop Loss required: ACTIVADO — ATR-based
     Min multiplicador: 1.8
     Max multiplicador: 2.2
     Periodo ATR: 14
[x] Take Profit required: ACTIVADO — ATR-based
     Min multiplicador: 4.0
     Max multiplicador: 5.0
     Periodo ATR: 14 (mismo que SL)
[x] Ratio minimo TP/SL: 2.25:1 — cumple >= 2:1
[x] Direcciones: Long y Short habilitados
[x] Numero de condiciones: Min 1, Max 2

NOTA CRITICA sobre Max condiciones:
Fijar Max en 2 (no en 3) para forzar logica simple.
La hipotesis tiene exactamente 2 condiciones por direccion.
Limitar a 2 evita que el Builder añada ruido adicional.

#### Tab: Opciones geneticas
[x] Max Generations: 20
[x] Population Size: 50 por isla
[x] Islands: 4
[x] Start again when finished: DESACTIVADO
[x] Filter initial population: sin filtro

#### Tab: Opciones de negociacion
[x] Limitar intervalo de tiempo: ACTIVADO
[x] Rango desde: 08:00
[x] Rango hasta: 20:00
[x] Maximo trades por dia: 2
[x] Salida al final del dia: ACTIVADO
[x] No comercie fines de semana: ACTIVADO
[x] Salida el viernes: ACTIVADO

#### Tab: Gestion del dinero
[x] Capital inicial: 25.000 USD
[x] Metodo: Riesgo fijo en % de la cuenta
[x] Riesgo por trade: 1%

#### Tab: Bloques de construccion

Signals — activar SOLO estos 2:
[x] Precio de cierre por encima del indicador (Close above indicator)
[x] El ADX supera el nivel (ADX above level)
DESACTIVAR todos los demas signals

Indicadores — activar SOLO:
[x] EMA — Media movil exponencial (periodo 50 como punto de partida)
[x] ATR — Rango medio real (periodo 14)
DESACTIVAR todos los demas indicadores

Operators — activar:
[x] (>) Mayor que
[x] (<) Menor que
[x] (>=) Mayor o igual
[x] (<=) Menor o igual

Tipos de pedido:
[x] (MKT) Entrar en el mercado

Tipos de salida:
[x] Objetivo de beneficios: REQUERIDO
[x] Stop Loss: REQUERIDO
[x] Tope dinamico: DESACTIVADO
[x] Trailing: DESACTIVADO
[x] Salida por barras: DESACTIVADO

Bloques entrada parada/limite:
[x] (ATR) Rango medio real
[x] (C) Cerrar

#### Tab: Clasificacion
[x] Maximum strategies to store: 500
[x] Stop generation: Databank is full
[x] Factor de beneficio > 0.8
[x] Transacciones medias al mes > 8
[x] Ratio Ret/DD > 0.5
[x] Ranking: Aptitud ponderada
     PF: Maximice Peso 3
     Max Drawdown: Minimizar Peso 2
     Trades: Maximice Peso 1

#### Tab: Comprobaciones cruzadas
[x] Mayor precision de las pruebas: ACTIVADO
[x] Todo lo demas: DESACTIVADO

### BLOQUE 4 — VERIFICACION FINAL ANTES DE INICIO

Verificar en pestana Progreso antes de clicar Inicio:
[ ] Simbolo: EURUSD_M1_dukas
[ ] Temporalidad: H1
[ ] Fechas: 2003.05.05 a 2020.12.31
[ ] Sesion: 08:00 a 20:00
[ ] Risk: 1% of account
[ ] Max trades: 2 per day
[ ] Comisiones: 0.5 pips + 7 USD + 0.5 pip slippage

[ ] Commit de Git hecho antes de lanzar
[ ] Databank de resultados vacio antes de lanzar
[ ] Ordenador disponible durante el build
[ ] Lanzar en horario nocturno — duracion estimada 6-12 horas

---

## RESUMEN DE CONFIGURACION TAB POR TAB

### Bloque de entrada Long (bloques SQ exactos)
Condicion 1: Close[0] > EMA(50)[0]         ← precio cierra sobre EMA de 50 periodos
Condicion 2: ADX(14)[0] > 20               ← ADX de 14 periodos supera nivel 20

### Bloque de entrada Short (bloques SQ exactos)
Condicion 1: Close[0] < EMA(50)[0]         ← precio cierra bajo EMA de 50 periodos
Condicion 2: ADX(14)[0] > 20               ← ADX de 14 periodos supera nivel 20

### Gestion de riesgo
SL: ATR(14) x [1.8 a 2.2] — el Builder elige dentro del rango
TP: ATR(14) x [4.0 a 5.0] — el Builder elige dentro del rango
Ratio: minimo 2.0:1, maximo 2.78:1

---

## PARAMETROS QUE EL BUILDER PUEDE VARIAR

| Parametro         | Valor minimo | Valor maximo | Estandar |
|-------------------|-------------|-------------|---------|
| Periodo EMA       | 40          | 60          | 50      |
| Nivel ADX         | 18          | 25          | 20      |
| Multiplicador SL  | 1.8         | 2.2         | 2.0     |
| Multiplicador TP  | 4.0         | 5.0         | 4.5     |

NOTA: Los rangos son estrechos — ±20% del valor estandar.
Esto reduce el espacio de busqueda y el riesgo de sobreajuste.
Si el Builder no encuentra buenas estrategias con estos rangos
→ ampliar levemente en la siguiente iteracion, no al inicio.

---

## CRITERIOS DE EVALUACION DE RESULTADOS

Cuando el build termine buscar candidatas con:
- PF IS >= 1.5 (minimo para avanzar al Retester)
- Max DD IS <= 6.5% (alerta funding-specialist)
- Trades totales >= 100 en el periodo IS
- Trades/mes promedio >= 6
- Sin periodos de mas de 14 dias sin operaciones

Criterios de descarte automatico (orchestrator aplica sin consultar):
- PF < 1.3 con comisiones reales → DESCARTAR
- DD > 8% → DESCARTAR
- Trades < 50 → DESCARTAR
- Mas del 50% del beneficio en un solo mes → DESCARTAR
- DD maximo en los ultimos 3 meses → DESCARTAR

---

## INSTRUCCIONES PARA GUARDAR RESULTADOS

Cuando el build termine:
1. Pestana Results → Guardar → formato SQ X
   → results\raw\build-results\Build8-TrendFollowing-EURUSD-H1-EMA50-ADX.sqx
2. Pestana Last Generation → Guardar → mismo formato
   → results\raw\last-generation\Build8-LastGen.sqx
3. Anotar en el ticket: numero de estrategias generadas y PF maximo
4. Commit de Git inmediatamente

---

## TIEMPO ESTIMADO

EUR/USD H1 con 17 anos M1 (2003-2020): 6-12 horas
Recomendacion: lanzar por la noche y revisar resultados por la manana.

## SEÑALES DE QUE EL BUILD VA BIEN

A los 30 minutos:
- Estrategias generandose a 8-10 segundos por estrategia
- El contador de generacion sube progresivamente

A las 2 horas:
- "En la base de datos" empieza a subir (primeras estrategias que pasan filtros)
- Contador total de estrategias avanzando

Build terminado correctamente:
- Boton verde "Inicio" visible
- Log parado sin errores
- Estrategias visibles en Last Generation y Results

## SEÑALES DE PROBLEMA

- 0 en databank con > 500 generadas → filtros demasiado estrictos (bajar PF min a 0.5)
- Build termina en < 2 horas → verificar que las fechas cubren 2003-2020
- Error de datos en pantalla → detener, revisar simbolo EURUSD_M1_dukas en Gestor de datos
