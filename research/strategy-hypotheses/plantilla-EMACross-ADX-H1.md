# Hipotesis: EMA Cross con Filtro ADX — H1

## Metadatos
Fecha: 2026-04-10
Agente: market-analyst
Mercado: EUR/USD
Temporalidad: H1
Estilo: Trend Following
Ticket: TICKET-001 (plantilla de referencia)
Estado: PLANTILLA — no lanzar como build real

---

## DESCRIPCION DEL EDGE

El edge de esta estrategia se basa en capturar
tendencias definidas durante las sesiones de
Londres y Nueva York.

Cuando la EMA rapida cruza por encima de la EMA lenta
el mercado ha cambiado de estructura de corto plazo.
El filtro ADX confirma que ese cambio ocurre en
un contexto de tendencia real y no en un mercado lateral.

Por que deberia funcionar:
- Los cruces de medias capturan cambios de momentum
- El ADX filtra señales falsas en mercados sin tendencia
- La sesion 08:00-20:00 concentra el volumen real
  del mercado donde el edge es mas consistente

---

## LOGICA DE ENTRADA

### Entrada Long
Condicion 1: EMA(20) cruza por encima de EMA(50)
             en la ultima barra H1
Condicion 2: ADX(14) > 25 en H1
Condicion 3: (opcional) Precio cierre > EMA(50)

### Entrada Short
Condicion 1: EMA(20) cruza por debajo de EMA(50)
             en la ultima barra H1
Condicion 2: ADX(14) > 25 en H1
Condicion 3: (opcional) Precio cierre < EMA(50)

### Traduccion a bloques SQ nativos
Long:
- EMA(20) crosses above EMA(50) — within last 1 bar
- ADX(14) is above level 25

Short:
- EMA(20) crosses below EMA(50) — within last 1 bar
- ADX(14) is above level 25

Verificado contra skill-sq-builder.md: COMPATIBLE

---

## GESTION DE STOP LOSS Y TAKE PROFIT

Stop Loss: ATR(14) x 2.0
Take Profit: ATR(14) x 4.5
Ratio TP/SL: 2.25:1 — cumple minimo 2:1

Justificacion ATR:
En EUR/USD H1 el ATR(14) tipico es 10-15 pips.
SL = 2.0 x ATR = 20-30 pips — suficiente para
no ser tocado por ruido normal del mercado.
TP = 4.5 x ATR = 45-67 pips — viable en tendencias
tipicas de las sesiones de Londres y Nueva York.

---

## FILTROS OPERATIVOS

Horario: 08:00 a 20:00 CET
Maximo trades por dia: 2
Salida al final del dia: ACTIVADO
No operar fines de semana: ACTIVADO
Salida el viernes: ACTIVADO antes de cierre

---

## CONTEXTO DE MERCADO ESPERADO

Sesion favorable: Londres y solapamiento Londres-NY
Regimen de volatilidad: Tendencia con ADX creciente
Condiciones adversas: Rango lateral con ADX < 20

Esta estrategia fallara sistematicamente en:
- Mercados laterales prolongados (ADX < 20 constante)
- Periodos de muy baja volatilidad
- Dias con noticias de alto impacto que
  revierten los cruces rapidamente

---

## CHECKLIST DE SOBREAJUSTE
(basado en skill-avoiding-overfitting.md)

[x] Numero de indicadores <= 3 (EMA + ADX = 2)
[x] Parametros estandar: EMA 20/50, ADX 14
[x] Logica simetrica para largos y cortos
[x] Edge explicable economicamente
[x] Costes de transaccion considerados en el diseño
[x] No depende de un solo año o regimen especifico

Nivel de riesgo de sobreajuste: BAJO

---

## POSIBLES FALLOS ESTRUCTURALES

Fallo 1: Demasiadas señales en mercados laterales
Mitigacion: filtro ADX > 25 reduce entradas
en periodos de rango.

Fallo 2: SL demasiado ajustado en momentos
de alta volatilidad
Mitigacion: SL basado en ATR se adapta
automaticamente a la volatilidad del momento.

Fallo 3: Dependencia de un solo indicador
Mitigacion: combinacion de dos indicadores
independientes — EMA (tendencia) y ADX (fuerza).

---

## CONFIGURACION ESTANDAR PARA EL BUILDER

Tab Que construir:
- Tipo: Simple strategy
- SL: ATR-based, Min 1.8 Max 2.2
- TP: ATR-based, Min 4.0 Max 5.0

Tab Datos:
- Simbolo: EURUSD_M1_dukas
- Temporalidad: H1
- Fechas: 2003.05.05 a 2020.12.31
- Spread: 0.5 pips
- Comision: 7 USD por lote
- Slippage: 0.5 pips

Tab Bloques:
Signals activar solo:
- EMA crosses above/below (cruce de medias)
- ADX is above level (ADX por encima de nivel)

Indicadores activar:
- EMA Media movil exponencial
- ADX

Operators activar:
- (>=) Mayor o igual
- (<=) Menor o igual

---

## RESULTADOS ESPERADOS (referencia)

Basado en hipotesis similares en EUR/USD H1:

Profit Factor esperado IS: 1.5 - 1.8
Max DD esperado: 5 - 7%
Trades esperados por mes: 8 - 15
Win Rate esperado: 40 - 50%
Ratio TP/SL efectivo: 2.0 - 2.5

Si el Builder produce resultados muy por encima
de estos rangos — especialmente PF > 2.5 —
revisar señales de sobreajuste antes de avanzar.

---

## RESULTADOS REALES (rellenar tras el build)

Build numero: ___
Fecha del build: ___
PF in-sample: ___
Max DD in-sample: ___
Trades totales: ___
Decision Evaluation Gate: ___
PF out-of-sample: ___
Decision Retester: ___
WFE Optimizer: ___
Decision final: ___

---

## VERIFICACIONES FINALES

[x] Logica 100% nativa en SQ Builder
[x] Ratio TP/SL >= 2:1
[x] Riesgo por trade: 1% del balance
[x] Comisiones reales FTMO incluidas
[x] Datos OOS no incluidos en el build
[x] Temporalidad H1
[x] Verificado contra skill-avoiding-overfitting.md

Nivel de riesgo de sobreajuste: BAJO
Compatibilidad FTMO teorica: SI

Conclusión: Verificado contra skill-sq-builder.md,
skill-hypothesis-design.md y
skill-avoiding-overfitting.md — Compatible.