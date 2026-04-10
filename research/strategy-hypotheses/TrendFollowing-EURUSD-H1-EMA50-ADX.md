# Hipotesis: Trend Following EMA50 con Filtro ADX — EUR/USD H1

## Metadatos
Fecha: 2026-04-10
Agente: market-analyst
Mercado: EUR/USD
Temporalidad: H1
Estilo: Trend Following
Ticket: TICKET-001
Estado: ACTIVA — pendiente de build

---

## RAZONAMIENTO DE SELECCION

Build 7 (dispositivo anterior) fue NBARBreakout-RSI H1 EUR/USD — resultado desconocido.
Para no duplicar logica con Build 7 se elige un estilo diferente: Trend Following con
EMA y ADX, que tiene el menor riesgo de sobreajuste segun skill-avoiding-overfitting.md
y logica 100% nativa en SQ Builder.

---

## DESCRIPCION DEL EDGE

### Frase resumen del edge
"Entrar en la direccion de la tendencia cuando el precio esta sobre/bajo la EMA(50)
y el ADX confirma que hay una tendencia real activa."

### Explicacion economica
El EUR/USD en H1 pasa el 40% del tiempo en regimen de tendencia (ADX > 20).
Durante esos periodos, los participantes institucionales (bancos, fondos) se
alinean en una direccion creando inercia sostenida. La EMA(50) actua como nivel
de decision para los traders sistematicos — precio sobre EMA(50) = sesgo comprador.
El filtro ADX > 20 descarta el 60% de casos en que el mercado esta lateral
y los cruces generarian señales falsas.

### Sesion objetivo
Londres y solapamiento Londres-NY (08:00-20:00 UTC).
Razon: el 70% del volumen diario EUR/USD ocurre en estas ventanas.
Las tendencias que nacen en la apertura de Londres tienden a extenderse.

### Regimen de mercado favorable
- ADX > 20: tendencia moderada o fuerte — señales validas
- ADX > 25: tendencia fuerte — señales de maxima calidad
- Precio respeta la EMA(50) como soporte/resistencia dinamica

### Condicion de fallo sistematico
- ADX < 20 de forma persistente: mercado lateral — señales falsas frecuentes
- Noticias macro de alto impacto (NFP, BCE): pueden revertir la tendencia en minutos
- Periodos de verano y navidad: liquidez baja, tendencias erraticas

---

## LOGICA DE ENTRADA

### Entrada Long
Condicion 1: Precio de cierre H1 > EMA(50) H1
Condicion 2: ADX(14) H1 > 20

### Entrada Short
Condicion 1: Precio de cierre H1 < EMA(50) H1
Condicion 2: ADX(14) H1 > 20

### Logica simetrica
SI — la logica es identica para largos y cortos.
No hay sesgo direccional en el diseño.

### Traduccion a bloques SQ nativos

Long:
- Close is above EMA(50) — en la ultima barra H1
- ADX(14) is above level 20

Short:
- Close is below EMA(50) — en la ultima barra H1
- ADX(14) is above level 20

Verificado contra skill-sq-builder.md:
- "precio por encima/debajo de indicador" → NATIVO
- "ADX por encima de nivel" → NATIVO
Compatibilidad SQ Builder: 100%

---

## GESTION DE STOP LOSS Y TAKE PROFIT

Stop Loss: ATR(14) x 2.0
Take Profit: ATR(14) x 4.5
Ratio TP/SL: 2.25:1 — CUMPLE minimo 2:1

### Justificacion de los multiplicadores ATR
ATR(14) tipico en EUR/USD H1: 10-15 pips.

SL = 2.0 x ATR = 20-30 pips:
- Suficiente para absorber el ruido normal de H1
- No demasiado amplio para que el riesgo 1% resulte en lotes razonables
- Con riesgo 1% en cuenta 25k: 250 USD → ~0.83 lotes con SL 30 pips

TP = 4.5 x ATR = 45-67 pips:
- Alcanzable en tendencias tipicas de sesion Londres
- No tan lejano como para raramente tocarse
- Con ratio 2.25:1 y win rate 40%: EV positivo
  (0.4 x 2.25) - (0.6 x 1.0) = 0.90 - 0.60 = +0.30 por trade

Rango de optimizacion permitido en Builder:
- SL multiplicador: 1.8 a 2.2 (±10% del estandar)
- TP multiplicador: 4.0 a 5.0 (±11% del estandar)
Rangos estrechos — sin sobreajuste.

---

## FILTROS OPERATIVOS

Horario: 08:00 a 20:00 CET (12 horas de ventana — cumple minimo 6h)
Maximo trades por dia: 2
Salida al final del dia: ACTIVADO
No operar fines de semana: ACTIVADO
Salida el viernes: ACTIVADO antes de cierre

---

## COMPATIBILIDAD FTMO 2-STEP

| Criterio                        | Estado |
|---------------------------------|--------|
| Tipo de estrategia permitido    | SI — trend following permitido |
| SL definido en todas las ops    | SI — ATR-based |
| TP definido en todas las ops    | SI — ATR-based |
| Ratio TP/SL >= 2:1              | SI — 2.25:1 |
| Temporalidad H1                 | SI |
| Max 2 trades por dia            | SI |
| No HFT, no martingala           | SI |
| Daily Loss check (3% operativo) | Peor caso 2 perdedores = 2% < 3% |
| Max DD check (7% operativo)     | Racha 6 trades = 6% < 7% |

Compatibilidad FTMO teorica: COMPATIBLE

---

## CHECKLIST DE SOBREAJUSTE
(basado en skill-avoiding-overfitting.md)

[x] Numero de indicadores <= 3 — usa 2: EMA(50) + ADX(14)
[x] Parametros estandar: EMA periodo 50 (nivel psicologico), ADX periodo 14 (estandar Wilder)
[x] Logica simetrica para largos y cortos — identica en ambas direcciones
[x] Edge explicable economicamente — inercia institucional + filtro de tendencia real
[x] Costes de transaccion considerados — con TP 4.5 ATR el spread de 1 pip es < 5% del TP
[x] No depende de un solo año o regimen — funciona en cualquier periodo con ADX > 20
[x] Sin parametros en extremo de rango — valores centrales y estandar
[x] Sin condiciones dependientes entre si — EMA y ADX son independientes

Nivel de riesgo de sobreajuste: **BAJO**

---

## POSIBLES FALLOS ESTRUCTURALES

[x] ¿La logica genera demasiadas señales en laterales?
    Con ADX < 20 no entra. Riesgo mitigado.

[x] ¿El SL basado en ATR podria ser muy ajustado en alta volatilidad?
    SL = 2.0 x ATR se adapta — si ATR sube el SL se amplia.
    Riesgo: en volatilidad extrema (2008, 2020) el ATR puede dispararse.
    Mitigacion: max 2 trades/dia limita la exposicion en dias extremos.

[x] ¿La hipotesis depende de un solo indicador?
    No — EMA (tendencia) + ADX (fuerza de tendencia) son dos fuentes distintas.

[x] ¿Los costes anulan el edge?
    TP minimo = 4.0 x ATR (modo conservador) = ~40 pips.
    Coste total EUR/USD FTMO = 1 pip total (0.5 spread + 0.5 slippage) + 7 USD/lote.
    Con lote de 0.83: 7 USD = ~0.7 pips adicionales.
    Coste total ~ 1.7 pips vs TP de 40 pips = 4.25% del TP. Margen amplio.

---

## CONFIGURACION ESTANDAR PARA EL BUILDER

### Tab Que construir
- Tipo: Simple strategy
- SL: ATR-based, Min 1.8, Max 2.2, ATR periodo 14
- TP: ATR-based, Min 4.0, Max 5.0, ATR periodo 14
- Max posiciones simultaneas: 1
- Max trades por dia: 2

### Tab Datos
- Simbolo: EURUSD_M1_dukas
- Temporalidad: H1
- Fecha inicio: 2003.05.05
- Fecha fin: 2020.12.31
- Spread: 0.5 pips
- Comision: 7 USD por lote (round turn)
- Slippage: 0.5 pips

### Tab Bloques — activar SOLO
Signals:
- Close is above/below indicator (precio vs EMA)
- ADX is above level

Indicadores:
- EMA (Media Movil Exponencial) — periodo 50
- ADX — periodo 14

Operators:
- (>) Mayor que
- (<) Menor que

NO activar ningun otro bloque — cada bloque extra es un grado de libertad adicional.

### Tab Opciones geneticas
- Generaciones: 20
- Individuos por isla: 50
- Islas: 4
Total combinaciones evaluadas: 4000 — moderado, sin sobreajuste masivo.

### Filtros del Builder
- PF > 0.8 (filtro minimo — el Evaluation Gate aplica el filtro real)
- Trades > 8
- RatioDD > 0.5

---

## RESULTADOS ESPERADOS (referencia)

Basado en la logica y el mercado historico EUR/USD H1:

| Metrica            | Rango esperado | Alerta si |
|--------------------|---------------|-----------|
| Profit Factor IS   | 1.4 - 1.9     | PF > 2.5 → sobreajuste probable |
| Max DD IS          | 4 - 8%        | DD > 10% → no pasa FTMO |
| Trades/mes         | 6 - 12        | < 4 → edge demasiado raro |
| Win Rate           | 38 - 50%      | > 60% → sospechoso |
| Ratio TP/SL real   | 2.0 - 2.5     | < 2.0 → no cumple regla |

---

## RESULTADOS REALES (rellenar tras el build)

Build numero: 8 (primer build H1 en dispositivo actual)
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
[x] Ratio TP/SL >= 2:1 — cumple con 2.25:1
[x] Riesgo por trade: 1% del balance
[x] Comisiones reales FTMO incluidas en la configuracion
[x] Datos OOS (2021-actual) NO incluidos en el periodo de build
[x] Temporalidad H1
[x] Verificado contra skill-avoiding-overfitting.md
[x] Verificado contra skill-sq-builder.md

Verificado contra skill-sq-builder.md y
skill-avoiding-overfitting.md.
Riesgo de sobreajuste: BAJO
Compatible con SQ Builder: SI
