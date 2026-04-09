# Skill: Contexto de Mercado

## Proposito
Guia para el market-analyst.
Define cuando usar cada estilo de estrategia segun
las condiciones del mercado y el activo analizado.

---

## ESTILOS DE ESTRATEGIA Y CUANDO USARLOS

### Trend Following
Logica: entrar en la direccion de la tendencia
y mantener hasta que cambia.

CUANDO FUNCIONA BIEN:
- ADX por encima de 25 de forma consistente
- Precio respeta claramente las medias moviles
- Sesiones de alta liquidez (Londres, Nueva York)
- Periodos de expansion economica o crisis prolongada

CUANDO NO FUNCIONA:
- Mercado lateral o en rango
- ADX por debajo de 20 de forma consistente
- Muchos falsos breakouts
- Periodos de baja volatilidad

INDICADORES CLAVE:
- ADX > 25: tendencia fuerte
- ADX 20-25: tendencia moderada
- ADX < 20: mercado lateral, evitar trend following
- EMA(50) H1: direccion de tendencia principal
- EMA(200) H1: tendencia de largo plazo

### Mean Reversion
Logica: entrar contra la tendencia a corto plazo
esperando que el precio vuelva a la media.

CUANDO FUNCIONA BIEN:
- ADX por debajo de 20
- Precio oscila entre soportes y resistencias claros
- Sesiones de baja volatilidad
- Periodos de estabilidad economica

CUANDO NO FUNCIONA:
- Mercado en tendencia fuerte (ADX > 30)
- Despues de noticias de alto impacto
- En periodos de crisis

INDICADORES CLAVE:
- ADX < 20: bueno para mean reversion
- RSI < 30 o > 70: señal de entrada
- Bandas de Bollinger: precio en extremos

---

## SESIONES DE MERCADO

### Sesion de Asia (00:00 - 08:00 UTC)
Caracter: baja volatilidad, movimientos pequeños.
Mejor para: mean reversion, estrategias de rango.
EUR/USD: muy poco movimiento.

### Sesion de Londres (08:00 - 16:00 UTC)
Caracter: alta volatilidad, tendencias claras.
Mejor para: trend following, breakouts.
Pares mas activos: EUR/USD, GBP/USD.

### Sesion de Nueva York (13:00 - 22:00 UTC)
Caracter: alta volatilidad 13:00-17:00 UTC.
Mejor para: trend following, continuacion de tendencia.
Noticias clave: NFP, CPI, Fed — siempre 13:30 UTC.

### Solapamiento Londres-NY (13:00 - 16:00 UTC)
Caracter: maxima liquidez del dia.
Mejor para: trend following con ADX alto.

---

## REGIMENES DE MERCADO EUR/USD

### Regimen de tendencia (ADX > 25)
Anos historicos tipicos: 2014-2015, 2017, 2022.
Estrategia recomendada: trend following H1.
Config Builder: EMA + ADX, ventana Londres-NY.

### Regimen lateral (ADX < 20)
Anos historicos tipicos: 2011-2013, 2019.
Estrategia recomendada: mean reversion RSI.
Config Builder: RSI extremos, ventana amplia.

### Regimen de alta volatilidad (crisis)
Anos tipicos: 2008-2009, 2020, 2022.
Riesgo: drawdown puede dispararse.
Accion: reducir tamaño de posicion.

---

## CARACTERISTICAS DE XAU/USD

### Diferencias con EUR/USD
- Mayor volatilidad intradía
- Spreads mucho mas altos (30 pips vs 0.5 pips)
- Reacciona fuertemente a noticias macro
- Correlacion inversa con USD en tendencias largas
- Opera bien en sesion de Nueva York

### Configuracion recomendada para XAU/USD
- Ventana de sesion: 08:00 a 20:00
- Ratio TP/SL: minimo 2.5:1 por mayor volatilidad
- SL: minimo 2.0 x ATR (mas amplio que EUR/USD)
- TP: minimo 4.0 x ATR
- Max trades por dia: 2

### CRITICO: Spread en SQ para XAU/USD
1 pip en XAU/USD = 0.01 USD/oz
Spread real FTMO en oro = aprox 30 USD/lote
En SQ introducir: 30 pips (NO 0.5 como en EUR/USD)
Si pip size en SQ = 0.1 → introducir 3 pips
Verificar siempre antes de lanzar.

---

## COMBINACIONES RECOMENDADAS PARA H1

### Combinacion 1 — NBAR Breakout con RSI (EUR/USD)
Estilo: Trend Following
Sesion: 08:00 a 20:00
Indicadores: Highest High / Lowest Low + RSI
SL/TP: ATR-based, ratio 2:1 minimo
Razon: logica simple, 100% nativa en SQ,
probada en builds anteriores

### Combinacion 2 — Trend Following EMA y ADX (EUR/USD)
Estilo: Trend Following
Sesion: 08:00 a 20:00
Indicadores: EMA(50) + ADX(14)
SL/TP: ATR-based, ratio 2:1 minimo
Razon: logica clasica con edge probado en H1

### Combinacion 3 — Mean Reversion RSI (EUR/USD o XAU/USD)
Estilo: Mean Reversion
Sesion: 08:00 a 20:00
Indicadores: RSI(14) extremos + EMA(200)
SL/TP: ATR-based, ratio 2:1 minimo
Razon: funciona bien en periodos de baja volatilidad

### Combinacion 4 — NBAR Breakout (XAU/USD)
Estilo: Trend Following
Sesion: 08:00 a 20:00
Indicadores: Highest High / Lowest Low + RSI
SL: 2.0 x ATR / TP: 4.0 x ATR
Spread en SQ: 30 pips
Razon: alta volatilidad del oro favorece breakouts

---

## COMO ELEGIR EL ESTILO PARA UNA HIPOTESIS

Paso 1: Verificar ADX historico del mercado
- Mas del 50% del tiempo ADX > 20 → trend following
- Menos del 50% del tiempo ADX > 20 → mean reversion

Paso 2: Elegir sesion objetivo
- Trend following → Londres o solapamiento Londres-NY
- Mean reversion → apertura Londres o sesion amplia

Paso 3: Verificar contra skill-sq-builder.md
Confirmar que la logica es implementable en SQ.

Paso 4: Verificar ratio TP/SL
Minimo 2:1. Recomendado 2.5:1 o 3:1.