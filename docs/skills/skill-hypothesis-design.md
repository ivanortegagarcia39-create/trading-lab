# Skill: Diseño de Hipotesis para SQ Builder

## Proposito
Guia para el market-analyst y el sq-specialist.
Define como estructurar hipotesis que sean directamente
implementables en SQ Builder sin modificaciones.

---

## ANTES DE DISEÑAR UNA HIPOTESIS

### Verificaciones obligatorias
1. Leer skill-sq-builder.md completo
2. Confirmar que el mercado tiene datos en SQ
3. Confirmar que la temporalidad es H1
4. Confirmar que la logica no depende de rango
   de sesion asiatica ni elementos no nativos de SQ
5. Confirmar ratio TP/SL minimo 2:1

---

## ESTRUCTURA OBLIGATORIA DE HIPOTESIS

### Campo 1: Nombre
Formato: [Estilo]-[Mercado]-[Timeframe]-[ElementoClave]
Ejemplo: TrendFollowing-EURUSD-H1-EMA50-ADX

### Campo 2: Logica en una frase
Debe poder explicarse en una sola frase simple.

Ejemplo correcto:
"Entrar largo cuando el precio rompe el maximo de
las ultimas 20 velas y el RSI confirma momentum."

Ejemplo incorrecto:
"Entrar cuando el precio supera el maximo del rango
asiatico calculado entre las 00:00 y las 07:45 UTC."

### Campo 3: Condiciones de entrada (maximo 2-3)
Cada condicion debe ser implementable en SQ Builder.
Verificar contra skill-sq-builder.md.

Formato:
Condicion 1: [indicador] [operador] [nivel]
Condicion 2: [indicador] [operador] [nivel]
Condicion 3: (opcional)

### Campo 4: Stop Loss
Debe ser ATR-based:
- ATR multiplicador minimo: 1.5x
- Periodo ATR: 10-20

### Campo 5: Take Profit
Debe ser ATR-based con ratio minimo 2:1:
- TP = minimo 2x el SL
- Ejemplo: SL = 1.5 ATR → TP = 3.0 ATR minimo

### Campo 6: Filtro de sesion
Solo estos filtros son nativos en SQ:
- Hora de inicio y fin (minimo 6 horas de ventana)
- No operar fines de semana
- Salida al final del dia
- Salida el viernes

### Campo 7: Compatibilidad FTMO
- Tipo de estrategia permitido: SI/NO
- SL definido: SI/NO
- TP definido: SI/NO
- Ratio TP/SL >= 2:1: SI/NO
- Timeframe H1: SI/NO

---

## HIPOTESIS TIPO RECOMENDADAS PARA H1

### Tipo 1 — NBAR Breakout con RSI
Nombre: NBARBreakout-EURUSD-H1-RSI
Logica: entrar cuando el precio rompe el maximo
o minimo de las ultimas N velas con confirmacion RSI.

Condicion Long:
1. Precio cierra por encima de Highest High (N velas)
2. RSI > 50

Condicion Short:
1. Precio cierra por debajo de Lowest Low (N velas)
2. RSI < 50

SL: 1.5 x ATR(14)
TP: 3.0 x ATR(14) — ratio 2:1
Sesion: 08:00 a 20:00
Max trades: 2 por dia
Compatible SQ Builder: 100%
Compatible FTMO: SI

### Tipo 2 — Trend Following EMA y ADX
Nombre: TrendFollowing-EURUSD-H1-EMA50-ADX
Logica: entrar en la direccion de la tendencia
cuando EMA confirma y ADX mide fuerza.

Condicion Long:
1. Precio > EMA(50) H1
2. ADX(14) > 20

Condicion Short:
1. Precio < EMA(50) H1
2. ADX(14) > 20

SL: 1.5 x ATR(14)
TP: 3.0 x ATR(14) — ratio 2:1
Sesion: 08:00 a 20:00
Max trades: 2 por dia
Compatible SQ Builder: 100%
Compatible FTMO: SI

### Tipo 3 — Mean Reversion RSI extremos
Nombre: MeanReversion-EURUSD-H1-RSI
Logica: entrar contra la tendencia a corto plazo
cuando RSI alcanza niveles extremos.

Condicion Long:
1. RSI(14) < 30
2. Precio > EMA(200) H1

Condicion Short:
1. RSI(14) > 70
2. Precio < EMA(200) H1

SL: 1.5 x ATR(14)
TP: 3.0 x ATR(14) — ratio 2:1
Sesion: 08:00 a 20:00
Max trades: 2 por dia
Compatible SQ Builder: 100%
Compatible FTMO: SI

---

## ERRORES COMUNES A EVITAR

1. HIPOTESIS DEMASIADO COMPLEJA
   Mas de 3 condiciones = sobreajuste probable.
   Simplificar siempre antes de añadir condiciones.

2. LOGICA NO NATIVA EN SQ
   Leer skill-sq-builder.md antes de proponer.
   Si hay duda → asumir que NO es nativo.

3. RATIO TP/SL INSUFICIENTE
   TP menor de 2x el SL = edge insuficiente
   para cubrir comisiones reales FTMO.
   Minimo 2:1, recomendado 2.5:1 o 3:1.

4. VENTANA DE SESION DEMASIADO CORTA
   Menos de 6 horas = muy pocos trades en H1.
   Minimo 08:00 a 14:00, recomendado 08:00 a 20:00.

5. NO VERIFICAR CONTRA SKILL-SQ-BUILDER
   Antes de entregar al sq-specialist confirmar:
   "Verificado contra skill-sq-builder.md — compatible."

---

## CONFIRMACION OBLIGATORIA AL FINAL

Toda hipotesis debe terminar con esta linea:
"Verificado contra skill-sq-builder.md — compatible."

Si no aparece esta confirmacion → devolver
al market-analyst para verificacion.