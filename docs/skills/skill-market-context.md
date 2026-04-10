# Skill: Contexto de Mercado — Referencia Tecnica

## Proposito
Referencia tecnica sobre las caracteristicas de
cada mercado disponible en el proyecto.
Esta skill NO se usa para decidir que indicadores
activar ni que logica proponer — SQ decide eso.
Se usa unicamente para:
1. Configurar comisiones correctas por activo
2. Verificar que el activo tiene suficiente
   volatilidad para H1
3. Informar al market-selector para el scoring

---

## SESIONES DE MERCADO

### Sesion de Asia (00:00 - 08:00 UTC)
Caracter: baja volatilidad, movimientos pequeños.
Forex: muy poco movimiento en majors.
XAU/USD: moderada actividad.

### Sesion de Londres (08:00 - 16:00 UTC)
Caracter: alta volatilidad, tendencias claras.
Pares mas activos: EUR/USD, GBP/USD, EUR/GBP.
Indices europeos: DE40, UK100.

### Sesion de Nueva York (13:00 - 22:00 UTC)
Caracter: alta volatilidad 13:00-17:00 UTC.
Pares activos: todos los USD.
Indices US: US30, US500, NAS100.
Noticias clave: NFP, CPI, Fed — 13:30 UTC.

### Solapamiento Londres-NY (13:00 - 16:00 UTC)
Maxima liquidez del dia para Forex y metales.

### Sesion 24/7 (Cripto)
BTC/USD y ETH/USD operan 24/7.
Mayor volatilidad en apertura US y Asia.

---

## CARACTERISTICAS POR TIPO DE ACTIVO

### Forex Majors
Volatilidad: moderada en H1
ATR H1 tipico: 8-15 pips (EUR/USD)
Spread FTMO: 0.5-1.0 pips
Ventaja: maxima liquidez, spreads bajos
Riesgo: edge puede ser pequeño con comisiones

Activos: EUR/USD, GBP/USD, USD/JPY, USD/CHF,
AUD/USD, NZD/USD, USD/CAD

### Forex Crosses
Volatilidad: moderada-alta en H1
ATR H1 tipico: 10-25 pips segun par
Spread FTMO: 0.8-2.0 pips
Ventaja: mas volatilidad que majors
Riesgo: spreads mas altos reducen el edge

Activos: EUR/GBP, EUR/JPY, GBP/JPY, EUR/AUD,
EUR/CHF, AUD/JPY, GBP/AUD, CAD/JPY, NZD/JPY

### Metales
XAU/USD (Oro):
- Volatilidad: alta en H1
- ATR H1 tipico: 150-300 pips (1 pip = 0.01)
- Spread FTMO: 30 pips
- Ventaja: alta volatilidad favorece H1
- Riesgo: spread alto puede consumir edge
- CRITICO: verificar pip size en SQ antes de configurar

XAG/USD (Plata):
- Volatilidad: alta en H1
- Spread FTMO: 3 pips
- Correlacion con oro: ~0.80

### Indices
Volatilidad: alta en H1
ATR H1 tipico: variable segun indice
Spread FTMO: 0.5-2.0 puntos segun indice
Ventaja: tendencias claras en sesiones activas
Riesgo: gaps overnight pueden afectar SL

Activos principales:
- US30 (Dow): spread ~2.0 pts
- US500 (S&P): spread ~0.5 pts
- NAS100 (Nasdaq): spread ~1.5 pts
- DE40 (DAX): spread ~1.5 pts
- UK100 (FTSE): spread ~1.5 pts
- JP225 (Nikkei): spread ~10 pts

### Cripto
Volatilidad: muy alta
ATR H1 tipico: variable y alto
Spread FTMO: alto y variable
Ventaja: maxima volatilidad, 24/7
Riesgo: spreads altos, comportamiento impredecible

Activos:
- BTC/USD: spread ~20 USD
- ETH/USD: spread ~2 USD
- Datos desde 2017-2018 unicamente

---

## CORRELACIONES ENTRE ACTIVOS

### Alta correlacion (> 0.7)
- EUR/USD y GBP/USD: ~0.85
- EUR/USD y EUR/GBP: ~0.70
- AUD/USD y NZD/USD: ~0.85
- XAU/USD y XAG/USD: ~0.80
- US30 y US500: ~0.95
- US500 y NAS100: ~0.85

### Correlacion moderada (0.3-0.7)
- EUR/USD y USD/JPY: ~0.50 inversa
- EUR/USD y XAU/USD: ~0.40
- GBP/USD y AUD/USD: ~0.55
- USD/JPY y US500: ~0.45

### Baja correlacion (< 0.3)
- EUR/USD y NAS100: ~0.20
- XAU/USD y NAS100: ~0.15
- GBP/JPY y XAU/USD: ~0.10
- Forex y Cripto: generalmente < 0.2

---

## GRUPOS DE DIVERSIFICACION

Para el correlation-analyst — elegir 1 activo
de cada grupo para maximizar diversificacion:

- Grupo A: EUR/USD o GBP/USD (no ambos)
- Grupo B: USD/JPY o USD/CHF
- Grupo C: XAU/USD o XAG/USD (no ambos)
- Grupo D: NAS100 o US500 (no ambos)
- Grupo E: AUD/USD o NZD/USD (no ambos)
- Grupo F: BTC/USD o ETH/USD (no ambos)
- Grupo G: Crosses (EUR/GBP, GBP/JPY, etc)

---

## COMISIONES POR ACTIVO PARA BUILDER

Verificar SIEMPRE en CLAUDE.md y con la prop firm
objetivo antes de cada build.

### Forex Majors
- Spread: segun par (0.5-1.0 pips)
- Comision: 7 USD por lote
- Slippage: 0.5 pips

### Forex Crosses
- Spread: segun par (0.8-2.0 pips)
- Comision: 7 USD por lote
- Slippage: 0.8 pips

### Metales
- XAU/USD: spread 30 pips, comision 7 USD, slippage 2 pips
- XAG/USD: spread 3 pips, comision 7 USD, slippage 1 pip

### Indices
- Spread: variable segun indice y prop firm
- Comision: variable
- VERIFICAR SIEMPRE antes de configurar

### Cripto
- Spread: alto y variable
- VERIFICAR SIEMPRE antes de configurar
- Mercado 24/7: ajustar opciones de negociacion

---

## USO DE ESTA SKILL

Esta skill se usa SOLO como referencia tecnica:
- Comisiones correctas por activo
- Volatilidad esperada en H1
- Correlaciones para diversificacion del portfolio
- Caracteristicas de cada sesion de mercado

Esta skill NO se usa para:
- Decidir que indicadores activar
- Recomendar logicas de entrada
- Proponer estilos de estrategia
- Sugerir configuraciones del Builder

SQ decide la logica. Esta skill solo informa
sobre las condiciones del mercado.