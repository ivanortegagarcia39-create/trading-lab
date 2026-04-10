# Informe de Evaluacion de Prop Firms
Estrategia evaluada: TrendFollowing-EURUSD-H1-EMA50-ADX
Activo: EUR/USD
Temporalidad: H1
Estilo: Trend Following
Ticket: TICKET-001
Fecha: 2026-04-10
Evaluada por: propfirm-analyst
Momento del pipeline: Momento 1 — antes del Builder

---

## PARAMETROS DE LA HIPOTESIS (para evaluar contra prop firms)

| Parametro               | Valor hipotesis          |
|-------------------------|--------------------------|
| Activo                  | EUR/USD (Forex spot)     |
| Temporalidad            | H1                       |
| Estilo                  | Trend Following          |
| SL                      | 2.0 x ATR(14)            |
| TP                      | 4.5 x ATR(14)            |
| Ratio TP/SL             | 2.25:1                   |
| Max trades/dia          | 2                        |
| Riesgo por trade        | 1% del balance           |
| Trades/mes esperados    | 6-12                     |
| DD esperado IS          | 4-8%                     |

---

## PROP FIRMS ANALIZADAS

### Prop firms que permiten EUR/USD spot: FTMO, E8, TFT
### Prop firms NO compatibles con EUR/USD: MFF, TopStep, Apex (solo futuros CME)

---

## ANALISIS DE COMPATIBILIDAD

| Prop Firm | Daily DD | Max DD  | Objetivo | Dias min | Precio  | Split | EA OK | Compatible |
|-----------|----------|---------|----------|----------|---------|-------|-------|------------|
| FTMO      | 5% din   | 10% din | 10%+5%   | 4 dias   | ~250 EUR| 80%   | SI    | **SI**     |
| E8        | 5% fijo  | 8% fijo | 8%+5%    | 3 dias   | ~100 EUR| 80%   | SI    | SI         |
| TFT       | 5% fijo  | 10% tr  | 8%+5%    | 5 dias   | ~120 EUR| 80%   | SI    | SI*        |

*TFT tiene trailing DD en max drawdown — ver alerta abajo.

---

## ANALISIS DETALLADO POR PROP FIRM

### FTMO 2-Step — cuenta 25.000 USD

**Compatibilidad con la estrategia: EXCELENTE**

Puntos a favor:
- EUR/USD es el activo estrella de FTMO — spreads mas competitivos del mercado
- DD dinamico sube con las ganancias — protege el cushion progresivamente
- Sin Regla del Mejor Dia en 2-Step — ventaja para dias de tendencia fuerte
- Los dias de trading: con 6-12 trades/mes en H1 se superan facilmente los 4 dias minimos
  Ejemplo: 8 trades/mes = 4 dias minimos asumiendo 2 trades en dias distintos
- Daily Loss dinamico: con riesgo 1% y 2 trades/dia, peor dia = 2% < 3% operativo
- Objetivo 10%: con EV positivo y 20 trades → 125 USD x 20 = 2.500 USD = 10% exacto
- Trailing DD: NO aplica en FTMO — es DD sobre balance maximo, no trailing

**Analisis de seguridad DD:**
- DD esperado IS: 4-8%
- Margen operativo recomendado: 7% (de CLAUDE.md)
- DD esperado 4-8% vs limite operativo 7%: DENTRO del margen en el escenario tipico
  Alerta: si el DD IS supera el 7% habra que revisar el SL multiplicador
- Daily Loss: 3% operativo = 750 USD en cuenta 25k
  Peor caso (2 trades perdedores): 2 x 250 USD = 500 USD = 2% — DENTRO

**Conclusion FTMO:** RECOMENDADA como prop firm principal.

---

### E8 Funding 2-Step — cuenta 25.000 USD

**Compatibilidad con la estrategia: BUENA**

Puntos a favor:
- Max DD 8% fijo (vs 10% FTMO) — limite mas estricto pero mas predecible
- Daily Loss 5% fijo — no cambia durante el challenge
- Sin restricciones de noticias — favorable para trend following
- Precio mas bajo (~100 EUR vs ~250 EUR FTMO) — menor riesgo economico inicial

Puntos de atencion:
- Max DD 8% fijo: DD esperado IS de 4-8% tiene poco margen con limite de 8%
  Si el DD IS llega a 7.5% en backtest, el challenge con E8 es arriesgado
- Objetivo 8% en lugar de 10% — mas facil de alcanzar teoricamente
- 3 dias minimos: con 6-12 trades/mes se supera sin problema

**Conclusion E8:** ALTERNATIVA valida. Usar si el DD IS backtest se mantiene por debajo de 5%.
  Si DD IS > 6% preferable FTMO por su limite del 10%.

---

### The Funded Trader (TFT) Standard

**Compatibilidad con la estrategia: ACEPTABLE con reservas**

Puntos a favor:
- Mayor apalancamiento disponible (hasta 1:200)
- Objetivo 8% — mas facil que FTMO
- 5 dias minimos: con 6-12 trades/mes se supera

ALERTA — Trailing DD:
TFT usa trailing drawdown en el Max DD (10% trailing).
Esto significa que si la cuenta sube a 26.000 USD y luego baja,
el limite de DD se calcula desde el pico alcanzado.
Para una estrategia de trend following que puede tener drawdown
despues de un buen periodo, el trailing DD ES MAS PELIGROSO
que el DD dinamico de FTMO (que solo sube nunca baja).
Ejemplo: si ganamos 2.000 USD y luego tenemos racha negativa,
el limite trailing nos da menos margen que FTMO.

Regla de consistencia TFT: mejor dia < 50% del beneficio total.
Esto puede ser un problema si hay un dia de tendencia fuerte
con beneficio concentrado. Trend following en H1 puede generar
dias de alto beneficio en periodos de tendencia clara.

**Conclusion TFT:** NO RECOMENDADA como primera opcion para esta estrategia.
  Usar solo si FTMO y E8 no estan disponibles.

---

## RECOMENDACION PRINCIPAL

**Prop firm: FTMO 2-Step**
**Tamaño de cuenta recomendado: 25.000 USD**

Justificacion:
1. EUR/USD es el mercado principal de FTMO — mejor ejecucion y spreads
2. DD dinamico (solo sube) es el modelo mas favorable para trend following:
   si la estrategia empieza bien y luego tiene drawdown, el cushion es mayor
3. Sin Regla del Mejor Dia — dias de tendencia fuerte no penalizan
4. El calculo de viabilidad cuadra exactamente:
   - Con 1% riesgo, ratio 2.25:1 y win rate 40%:
     EV por trade = (0.4 x 562 USD) - (0.6 x 250 USD) = 225 - 150 = 75 USD/trade
   - Para 2.500 USD objetivo: 2.500 / 75 = ~33 trades → ~3 meses a ritmo 12/mes
   - Para 4 dias minimos: cumplido desde el primer mes
5. Precio razonable (~250 EUR) para la cuenta de 25k

**Riesgo principal identificado:**
Si el DD IS en el backtest supera el 7% habra que revisar antes de comprar challenge.
El margen entre DD esperado (4-8%) y limite operativo (7%) es ajustado en el escenario adverso.
Esto se verificara en el Evaluation Gate y el Retester.

---

## ALTERNATIVA

**Prop firm: E8 Funding**
**Cuando usar:** si el precio del challenge FTMO no esta disponible o si se quiere
reducir el coste inicial mientras se valida la estrategia en produccion.
**Condicion:** DD IS en backtest debe ser <= 5% para tener margen suficiente
frente al limite de Max DD del 8% de E8.

---

## INCOMPATIBILIDADES DETECTADAS

| Prop Firm | Razon de incompatibilidad |
|-----------|--------------------------|
| MFF       | Solo futuros CME — EUR/USD spot no disponible |
| TopStep   | Solo futuros CME — EUR/USD spot no disponible |
| Apex      | Solo futuros CME — EUR/USD spot no disponible |
| TFT       | Trailing DD peligroso para trend following + regla consistencia diaria |

---

## ALERTAS DE TRAILING DD

FTMO: NO usa trailing DD clasico. El limite solo sube con el balance — SEGURO.
E8: DD fijo estatico — el limite no cambia nunca — PREDECIBLE.
TFT: Trailing DD sobre el maximo alcanzado — PELIGROSO para trend following
     con potencial de drawdown post-pico.

---

## DECISION

[x] LISTO PARA EVALUACION DE FUNDING — prop firm recomendada: FTMO 2-Step 25k
[ ] REVISAR ESTRATEGIA — no aplica
[ ] NO COMPATIBLE — no aplica

Siguiente paso: invocar funding-specialist para verificacion detallada
de compatibilidad con reglas FTMO 2-Step.
