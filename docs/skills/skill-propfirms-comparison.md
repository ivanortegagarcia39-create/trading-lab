# Skill: Comparacion de Prop Firms

## Proposito
Base de conocimiento para el agente propfirm-analyst.
Permite comparar las principales prop firms del mercado
y determinar cual es la mas compatible con cada activo
y tipo de estrategia.

---

## PROP FIRMS ANALIZADAS

### 1. FTMO
Web: ftmo.com
Modelo: Challenge 2-Step
Mercados: Forex, Indices, Metales, Criptos, Acciones
Apalancamiento: hasta 1:100 Forex, 1:50 Indices

Reglas clave:
- Challenge: +10% objetivo, 5% daily loss, 10% max DD
- Verification: +5% objetivo, mismos limites DD
- Daily Loss: DINAMICO — recalculo medianoche Praga
- Max DD: DINAMICO — solo sube
- Dias minimos: 4 con posiciones iniciadas
- Sin Regla del Mejor Dia en 2-Step
- EAs: permitidos — no HFT, no martingala
- Noticias: permitido operar en Challenge

Profit split: 80% base, hasta 90% con scaling
Precio challenge 10k: ~155 EUR
Precio challenge 25k: ~250 EUR
Precio challenge 50k: ~345 EUR

Mejor para:
- Trend following H1 en EUR/USD y GBP/USD
- Estrategias de baja frecuencia (2-4 trades/dia)
- Traders que quieren escalar gradualmente

---

### 2. MyFundedFutures (MFF)
Web: myfundedfutures.com
Modelo: 1-Step y 2-Step
Mercados: Futuros CME (ES, NQ, CL, GC, 6E)
Apalancamiento: segun margen de futuros CME

Reglas clave:
- Objetivo: +8% (1-Step) / +6% (2-Step)
- Daily Loss: fijo segun cuenta
- Max DD: trailing drawdown (sube con ganancias)
- Sin dias minimos en algunos modelos
- EAs: totalmente permitidos
- Operacion 24/5

Profit split: 80-90%
Mejor para:
- Estrategias en futuros (ES, NQ, GC)
- Alta frecuencia de trades
- EAs completamente automatizados

---

### 3. TopStep
Web: topstep.com
Modelo: Trading Combine (1 fase)
Mercados: Futuros CME exclusivamente
Apalancamiento: segun margen CME

Reglas clave:
- Objetivo: +6% en Trading Combine
- Daily Loss: fijo 2% (muy estricto)
- Max DD: trailing drawdown
- Dias minimos: sin requisito
- EAs: permitidos con restricciones
- No operar durante noticias importantes

Profit split: 90% primeros 10k, 80% resto
Mejor para:
- Futuros ES y NQ
- Estrategias intraday
- Traders con disciplina de riesgo estricta

---

### 4. The Funded Trader (TFT)
Web: thefundedtrader.com
Modelo: Standard, Rapid, Royal
Mercados: Forex, Metales, Indices, Criptos
Apalancamiento: hasta 1:200

Reglas clave:
- Standard: +8% fase 1, +5% fase 2
- Daily Loss: 5% fijo
- Max DD: 10% trailing
- Dias minimos: 5 dias
- EAs: permitidos
- Regla de consistencia: mejor dia < 50% total

Profit split: 80% base, hasta 90%
Mejor para:
- Forex y metales
- Estrategias con consistencia diaria
- Traders que quieren mayor apalancamiento

---

### 5. Apex Trader Funding
Web: apextraderfunding.com
Modelo: 1 fase
Mercados: Futuros CME exclusivamente
Apalancamiento: segun margen CME

Reglas clave:
- Objetivo: +6% o fijo segun cuenta
- Daily Loss: trailing desde balance inicial
- Max DD: trailing
- Sin dias minimos
- EAs: totalmente permitidos
- Una de las mas flexibles del mercado

Profit split: 100% primeros 25k luego 90%
Mejor para:
- Futuros con EAs completamente automatizados
- Alta frecuencia
- Maxima flexibilidad operativa

---

### 6. E8 Funding
Web: e8funding.com
Modelo: 2-Step
Mercados: Forex, Metales, Indices, Criptos
Apalancamiento: hasta 1:100

Reglas clave:
- Objetivo: +8% fase 1, +5% fase 2
- Daily Loss: 5% fijo
- Max DD: 8% fijo
- Dias minimos: 3 dias
- EAs: permitidos
- Sin restricciones de noticias

Profit split: 80% base
Mejor para:
- Forex y metales con EAs
- Estrategias con DD controlado
- Traders que buscan menor DD maximo

---

## TABLA COMPARATIVA RAPIDA

| Prop Firm | Mercados      | Objetivo | Daily DD | Max DD | EAs  | Split |
|-----------|---------------|----------|----------|--------|------|-------|
| FTMO      | Forex+Indices | 10%+5%   | 5% din   | 10%din | SI   | 80-90%|
| MFF       | Futuros CME   | 8%+6%    | Fijo     | Trail  | SI   | 80-90%|
| TopStep   | Futuros CME   | 6%       | 2% fijo  | Trail  | SI*  | 90%   |
| TFT       | Forex+Indices | 8%+5%    | 5% fijo  | 10%tr  | SI   | 80-90%|
| Apex      | Futuros CME   | 6%       | Trail    | Trail  | SI   | 100%  |
| E8        | Forex+Indices | 8%+5%    | 5% fijo  | 8%fijo | SI   | 80%   |

---

## COMPATIBILIDAD POR ACTIVO

### EUR/USD (Forex spot)
Prop firms compatibles:
- FTMO: excelente — mercado principal
- TFT: muy bueno — alto apalancamiento
- E8: bueno — sin restricciones noticias
- MFF: NO — solo futuros CME
- TopStep: NO — solo futuros CME
- Apex: NO — solo futuros CME

Mejor opcion: FTMO para empezar
Segunda opcion: E8 o TFT

### XAU/USD (Oro spot)
Prop firms compatibles:
- FTMO: bueno — permite metales
- TFT: bueno
- E8: bueno
- MFF: SI pero como GC futuros — diferente instrumento
- TopStep: SI pero como GC futuros
- Apex: SI pero como GC futuros

Mejor opcion: FTMO
Nota: XAU/USD spot y GC futuros tienen spreads
y comportamiento diferente — no son equivalentes

### NQ (Nasdaq Futures)
Prop firms compatibles:
- MFF: excelente — mercado principal
- TopStep: excelente
- Apex: excelente — 100% profit split
- FTMO: SI pero como indice spot (US100)
- TFT: SI como indice
- E8: SI como indice

Mejor opcion: Apex o MFF para futuros puros
Segunda opcion: FTMO para indice spot

### GC (Gold Futures CME)
Prop firms compatibles:
- MFF: excelente
- TopStep: bueno
- Apex: excelente
- FTMO: NO directamente — usa XAU/USD spot
- TFT: NO directamente

Mejor opcion: Apex o MFF

---

## CRITERIOS DE SELECCION DE PROP FIRM

### Para estrategias Forex (EUR/USD, GBP/USD)
1. FTMO — mejor ecosistema y reputacion
2. E8 — menor max DD (8% vs 10%)
3. TFT — mayor apalancamiento disponible

### Para estrategias en Futuros (NQ, GC, ES)
1. Apex — 100% profit split primeros 25k
2. MFF — muy flexible con EAs
3. TopStep — mayor reputacion en futuros

### Para automatizacion total con EAs
1. Apex — maxima flexibilidad
2. MFF — sin restricciones para EAs
3. FTMO — bueno pero mas regulado

---

## PROCESO DE SELECCION RECOMENDADO

Paso 1: Identificar el activo principal de la estrategia
Paso 2: Filtrar prop firms compatibles con ese activo
Paso 3: Comparar Daily Loss Limit y Max DD
Paso 4: Verificar compatibilidad con EAs
Paso 5: Considerar precio del challenge y profit split
Paso 6: Seleccionar la prop firm optima

---

## NOTAS IMPORTANTES

- Las reglas de las prop firms cambian frecuentemente
- Verificar siempre en la web oficial antes de comprar
- Algunas prop firms tienen descuentos periodicos
- El trailing drawdown es mas peligroso que el estatico
  para EAs con drawdown inicial antes de recuperarse
- FTMO es la mas establecida y regulada del mercado
- Apex tiene la politica mas flexible para EAs