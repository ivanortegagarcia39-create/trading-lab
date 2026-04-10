# Skill: Comparacion de Prop Firms — Multi-Activo

## Proposito
Base de conocimiento para el propfirm-analyst
y el market-selector. Permite comparar las
principales prop firms del mercado y determinar
cual es la mas compatible con cada activo.
El scoring numerico decide — no la preferencia.

---

## PROP FIRMS ANALIZADAS

### 1. FTMO
Web: ftmo.com
Modelo: Challenge 2-Step
Mercados: Forex, Indices, Metales, Criptos
Apalancamiento: hasta 1:100 Forex, 1:50 Indices

Reglas clave:
- Challenge: +10% objetivo, 5% daily loss dinamico,
  10% max DD dinamico
- Verification: +5% objetivo, mismos limites
- Dias minimos: 4 con posiciones iniciadas
- Sin Regla del Mejor Dia en 2-Step
- EAs: permitidos — no HFT, no martingala

Profit split: 80% base, hasta 90% con scaling
Precios: 10k ~155€, 25k ~250€, 50k ~345€

Activos compatibles:
- Forex Majors: TODOS ✓
- Forex Crosses: TODOS ✓
- XAU/USD: SI ✓
- XAG/USD: SI ✓
- US30, US500, NAS100: SI ✓
- DE40, UK100, JP225: SI ✓
- BTC/USD, ETH/USD: SI ✓

---

### 2. E8 Funding
Web: e8funding.com
Modelo: 2-Step
Mercados: Forex, Metales, Indices, Criptos
Apalancamiento: hasta 1:100

Reglas clave:
- Objetivo: +8% fase 1, +5% fase 2
- Daily Loss: 5% fijo
- Max DD: 8% fijo (menor que FTMO)
- Dias minimos: 3 dias
- EAs: permitidos
- Sin restricciones de noticias

Profit split: 80% base

Activos compatibles:
- Forex Majors: TODOS ✓
- Forex Crosses: MAYORIA ✓
- XAU/USD: SI ✓
- XAG/USD: SI ✓
- Indices: SI ✓
- Cripto: SI ✓

---

### 3. The Funded Trader (TFT)
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

ALERTA: Max DD trailing es mas peligroso que
el DD dinamico de FTMO para EAs con drawdown
inicial antes de recuperarse.

Activos compatibles:
- Forex: TODOS ✓
- Metales: SI ✓
- Indices: SI ✓
- Cripto: SI ✓

---

### 4. MyFundedFutures (MFF)
Web: myfundedfutures.com
Modelo: 1-Step y 2-Step
Mercados: Futuros CME exclusivamente
Apalancamiento: segun margen CME

Reglas clave:
- Objetivo: +8% (1-Step) / +6% (2-Step)
- Daily Loss: fijo segun cuenta
- Max DD: trailing drawdown
- Sin dias minimos en algunos modelos
- EAs: totalmente permitidos

Profit split: 80-90%

Activos compatibles:
- Forex spot: NO ✗
- Metales spot: NO ✗
- ES (S&P futures): SI ✓
- NQ (Nasdaq futures): SI ✓
- GC (Gold futures): SI ✓
- CL (Oil futures): SI ✓
- 6E (Euro futures): SI ✓

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
- Maxima flexibilidad del mercado

Profit split: 100% primeros 25k luego 90%

Activos compatibles:
- Forex spot: NO ✗
- Metales spot: NO ✗
- ES, NQ, GC, CL, 6E: SI ✓

---

### 6. TopStep
Web: topstep.com
Modelo: Trading Combine (1 fase)
Mercados: Futuros CME exclusivamente
Apalancamiento: segun margen CME

Reglas clave:
- Objetivo: +6% en Trading Combine
- Daily Loss: 2% fijo (MUY estricto)
- Max DD: trailing
- Sin dias minimos
- EAs: permitidos con restricciones
- No operar durante noticias importantes

Profit split: 90% primeros 10k, 80% resto

ALERTA: Daily Loss del 2% es extremadamente
restrictivo para EAs. Considerar solo para
estrategias con DD diario < 1%.

Activos compatibles:
- Solo futuros CME ✓

---

## TABLA COMPARATIVA RAPIDA

| Prop Firm | Forex | Metales | Indices | Cripto | Futuros | DD tipo | Split |
|-----------|-------|---------|---------|--------|---------|---------|-------|
| FTMO | SI | SI | SI | SI | NO | Dinamico | 80-90% |
| E8 | SI | SI | SI | SI | NO | Fijo 8% | 80% |
| TFT | SI | SI | SI | SI | NO | Trail 10% | 80-90% |
| MFF | NO | NO | NO | NO | SI | Trail | 80-90% |
| Apex | NO | NO | NO | NO | SI | Trail | 100%/90% |
| TopStep | NO | NO | NO | NO | SI | 2% fijo | 90%/80% |

---

## COMPATIBILIDAD POR ACTIVO

### Forex Majors (EUR/USD, GBP/USD, USD/JPY, etc)
- FTMO: EXCELENTE — mercado principal
- E8: MUY BUENO — DD fijo 8% es ventaja
- TFT: BUENO — trailing DD es riesgo
- MFF, Apex, TopStep: NO COMPATIBLE

Mejor opcion Forex: FTMO (DD dinamico favorable)
Alternativa: E8 (DD fijo menor)

### Metales (XAU/USD, XAG/USD)
- FTMO: BUENO — spreads mas altos
- E8: BUENO — sin restricciones noticias
- TFT: ACEPTABLE — trailing DD con oro es riesgo
- MFF, Apex, TopStep: NO (solo futuros GC/SI)

Mejor opcion metales spot: FTMO
Para futuros GC: Apex (100% profit split)

### Indices spot (US30, US500, NAS100, DE40)
- FTMO: BUENO — indices como CFD
- E8: BUENO
- TFT: ACEPTABLE
- MFF, Apex, TopStep: NO (solo futuros ES, NQ)

Mejor opcion indices spot: FTMO
Para futuros indices: Apex o MFF

### Cripto (BTC/USD, ETH/USD)
- FTMO: ACEPTABLE — spreads altos
- E8: ACEPTABLE
- TFT: ACEPTABLE
- MFF, Apex, TopStep: NO

Mejor opcion cripto: E8 (sin restricciones noticias)
ALERTA: Spreads cripto muy altos — verificar
que el edge sobrevive a las comisiones.

---

## SELECCION AUTOMATICA DE PROP FIRM POR ACTIVO

El propfirm-analyst aplica estos criterios
automaticamente sin preferencia humana:

### Paso 1: Filtrar prop firms compatibles
Eliminar las que no permiten el activo.

### Paso 2: Comparar DD tipo
- DD dinamico (FTMO): mejor para EAs con DD inicial
- DD fijo (E8): predecible y seguro
- DD trailing (TFT, Apex): peligroso para EAs
  con drawdown antes de recuperarse

### Paso 3: Comparar coste del challenge
Menor coste = menor riesgo financiero para probar.

### Paso 4: Comparar profit split
Mayor split = mayor beneficio a largo plazo.

### Paso 5: Scoring automatico
Calcular score por prop firm para ese activo:
- Compatibilidad DD con la estrategia: peso 35%
- Profit split: peso 25%
- Coste del challenge: peso 20%
- Reputacion y estabilidad: peso 20%

La prop firm con mayor score se recomienda
automaticamente. Sin preferencia humana.

---

## NOTAS IMPORTANTES

- Las reglas de las prop firms cambian frecuentemente
- El propfirm-analyst debe verificar reglas actuales
  en la web oficial antes de recomendar
- El trailing DD es significativamente mas peligroso
  que el DD dinamico o fijo para EAs
- Los spreads de cripto e indices pueden ser
  mucho mayores que Forex — verificar siempre
- Algunas prop firms tienen descuentos periodicos
- FTMO es la mas establecida y regulada
- Apex tiene la politica mas flexible para EAs