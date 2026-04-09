# Skill: Limitaciones Tecnicas de SQ Builder

## Proposito
Este documento debe leerse ANTES de diseñar cualquier
configuracion de Builder. Evita proponer logicas que
SQ no puede implementar nativamente.

---

## LO QUE SQ BUILDER PUEDE HACER

### Indicadores nativos disponibles
- EMA, SMA, WMA (medias moviles)
- RSI, Stochastic, CCI (osciladores)
- ADX, DMI (fuerza de tendencia)
- ATR (volatilidad)
- MACD (convergencia/divergencia)
- Bandas de Bollinger
- Momentum, ROC
- Precios OHLC de velas anteriores
- Maximos y minimos de N velas anteriores
  (Highest High, Lowest Low)

### Condiciones de entrada que SQ puede construir
- Cruce de indicadores entre si
- Indicador por encima o por debajo de nivel
- Indicador subiendo o bajando
- Precio por encima o por debajo de indicador
- Comparacion entre dos indicadores
- Condiciones basadas en velas anteriores (lookback)
- Precio rompe maximo o minimo de N velas

### Condiciones de tiempo que SQ puede construir
- Filtro de hora de inicio y fin de sesion
- No operar fines de semana
- Salida al final del dia
- Salida el viernes
- Maximo de trades por dia

### Gestion del dinero que SQ puede hacer
- Lote fijo
- Riesgo fijo en % de la cuenta
- Stop Loss fijo en pips o porcentaje
- Take Profit fijo en pips o porcentaje
- ATR-based Stop Loss y Take Profit
- Trailing Stop

---

## LO QUE SQ BUILDER NO PUEDE HACER

### Logicas NO nativas en SQ Builder
Si una hipotesis depende de estas logicas debe
rediseñarse o construirse en AlgoWizard primero.

1. RANGO DE SESION ASIATICA
   SQ no puede calcular el maximo y minimo de un
   rango de horas especifico (ej: 00:00-07:45 UTC).
   Alternativa: usar Highest[N] y Lowest[N].

2. RUPTURA DE RANGO DINAMICO
   SQ no puede detectar ruptura de nivel calculado
   dinamicamente en la misma sesion.
   Alternativa: usar High[N] y Low[N] de velas anteriores.

3. CONDICIONES MULTIPLES DEPENDIENTES
   SQ no puede encadenar condiciones donde el resultado
   de una afecta a la siguiente en tiempo real.
   Alternativa: simplificar a condiciones independientes.

4. INDICADORES DE SESION ESPECIFICA
   SQ no puede calcular indicadores solo sobre velas
   de una sesion concreta.
   Alternativa: usar indicadores globales.

5. LOGICA DE DIAS DE LA SEMANA EN ENTRADAS
   SQ no puede diferenciar entre lunes y viernes
   para logicas de entrada — solo para salidas.

6. NOTICIAS ECONOMICAS
   SQ no tiene filtro nativo de calendario economico.

---

## SEÑALES DE ALERTA EN UNA HIPOTESIS

Si una hipotesis incluye estas palabras revisar
contra este documento antes de configurar Builder:

- "rango de sesion" → probablemente NO nativo
- "ruptura de apertura" → probablemente NO nativo
- "nivel dinamico" → probablemente NO nativo
- "filtro de noticias" → NO nativo
- "solo en determinado dia" → NO nativo para entradas
- "indicador de una sesion especifica" → NO nativo

---

## HIPOTESIS 100% COMPATIBLES CON SQ BUILDER

### Trend Following con EMA y ADX
Entrada Long: precio > EMA(50) H1 + ADX > 20
SL: 1.5 x ATR / TP: 3.0 x ATR
Compatible: 100%

### Cruce de Medias
Entrada: EMA(20) cruza por encima de EMA(50)
Condicion: RSI > 50
SL y TP: ATR-based
Compatible: 100%

### Ruptura de Maximo de N Velas (NBAR Breakout)
Entrada Long: precio supera Highest High de N velas
Condicion: RSI confirma
SL: Lowest Low de N velas / TP: 2x el SL
Compatible: 100%

### Mean Reversion con RSI
Entrada Long: RSI < 30
Condicion: precio > EMA(200)
SL y TP: ATR-based
Compatible: 100%

---

## REGLA DE ORO

Antes de generar cualquier configuracion de Builder
verificar que CADA condicion de la hipotesis aparece
en la lista de LO QUE SQ BUILDER PUEDE HACER.

Si alguna condicion no aparece → rediseñar la hipotesis
antes de configurar Builder.