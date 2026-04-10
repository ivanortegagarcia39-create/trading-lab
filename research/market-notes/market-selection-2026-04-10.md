# Informe de Seleccion de Mercado
Fecha: 2026-04-10
Generado por: market-selector
Sesion: inicio de Capa 0 — primer build H1

---

## INVENTARIO DE DATOS EN SQ

| Activo  | Simbolo SQ           | Periodo         | Registros | Estado    |
|---------|----------------------|-----------------|-----------|-----------|
| EUR/USD | EURUSD_M1_dukas      | 2003-2026-04-10 | ~8.6M     | ACTIVO    |
| XAU/USD | XAUUSD_M1_dukas      | 2003-2026-04-10 | ~8.6M     | ACTIVO    |
| GBP/USD | —                    | —               | —         | PENDIENTE |
| USD/JPY | —                    | —               | —         | PENDIENTE |
| GC      | —                    | —               | —         | PENDIENTE |
| NQ      | —                    | —               | —         | PENDIENTE |

Verificacion: datos confirmados por data-manager en sesion 2026-04-10.
Sin gaps detectados. Actualizados.

---

## COMPATIBILIDAD CON PROP FIRMS

| Activo  | FTMO | E8 | TFT | MFF | TopStep | Apex |
|---------|------|----|-----|-----|---------|------|
| EUR/USD | SI   | SI | SI  | NO  | NO      | NO   |
| XAU/USD | SI   | SI | SI  | NO* | NO*     | NO*  |
| GBP/USD | SI   | SI | SI  | NO  | NO      | NO   |
| GC      | NO   | NO | NO  | SI  | SI      | SI   |
| NQ/US100| SI** | SI | SI  | SI  | SI      | SI   |

*MFF/TopStep/Apex solo aceptan GC futuros CME, no XAU/USD spot
**FTMO lo acepta como US100 (indice spot), no como futuro CME

---

## ANALISIS DE CONDICIONES DE TRADING

### EUR/USD H1
- Volatilidad tipica H1: moderada-alta en sesion Londres/NY
- Spread FTMO: 0.5 pips (muy bajo — favorece rentabilidad)
- Comision: 7 USD/lote round turn
- Slippage estimado: 0.5 pips
- Coste total por lote: ~15 USD (0.5+0.5 pips + 7 USD comision)
- Sesiones optimas: Londres (08-16 UTC) y solapamiento Londres-NY (13-16 UTC)
- Regimenes historicos IS (2003-2020): alternancia tendencia / lateral
  - ADX > 25 aprox 40% del tiempo (favorece trend following)
  - ADX < 20 aprox 35% del tiempo (favorece mean reversion)
- Liquidez: maxima del mercado Forex — ejecucion sin problemas
- Riesgo noticias: NFP, CPI, Fed a las 13:30 UTC — gestionable con SL
- Comportamiento en crisis (2008, 2020): tendencias fuertes — trend following funciona

### XAU/USD H1
- Volatilidad tipica H1: alta — movimientos de 100-200 pips frecuentes
- Spread FTMO: ~30 pips (= 30 USD/lote — coste 10x mayor que EUR/USD)
- Comision: 7 USD/lote round turn
- Slippage estimado: 2 pips
- Coste total por lote: ~39 USD (~60 USD si se considera spread completo)
- Sesiones optimas: Nueva York (13-22 UTC) — reacciona a USD
- Regimenes historicos IS (2003-2020):
  - Tendencias largas y claras (2008-2012 alcista, 2013-2018 lateral)
  - Breakouts fuertes pero con whipsaws frecuentes
- CRITICO: el spread de 30 pips en SQ es obligatorio — verificar pip size
- Riesgo: mayor DD en estrategias de baja frecuencia por coste de spread

---

## SCORING DE COMPATIBILIDAD (pesos segun market-selector.md)

| Criterio                      | Peso | EUR/USD | XAU/USD |
|-------------------------------|------|---------|---------|
| Compatibilidad con prop firms | 40%  | 9.0     | 7.0     |
| Calidad de datos en SQ        | 20%  | 10.0    | 10.0    |
| Condiciones de trading        | 20%  | 8.5     | 6.0     |
| Potencial de diversificacion  | 20%  | 7.0     | 9.0     |

**Scores ponderados:**
- EUR/USD: (9.0x0.4) + (10.0x0.2) + (8.5x0.2) + (7.0x0.2) = 3.60 + 2.00 + 1.70 + 1.40 = **8.70**
- XAU/USD: (7.0x0.4) + (10.0x0.2) + (6.0x0.2) + (9.0x0.2) = 2.80 + 2.00 + 1.20 + 1.80 = **7.80**

---

## ANALISIS DE RIESGO ESPECIFICO FTMO 2-STEP

### EUR/USD + FTMO
- Daily Loss 5% dinamico: 750 USD operativo (3%)
  → Con riesgo 1% por trade (250 USD), hasta 3 trades perdedores/dia sin violar limite
  → 2 trades/dia H1: max perdida posible = 500 USD = 2% — DENTRO del margen operativo
- Max DD 10% dinamico: 1.750 USD operativo (7%)
  → Con riesgo 1% y ratio 2:1: racha de 6 trades perdedores = 1.500 USD — DENTRO
- Spread bajo minimiza friccion en backtests y en produccion
- Estrategia PERMITIDA: trend following y mean reversion
- SIN regla del mejor dia en 2-Step — ventaja para dias de tendencia fuerte

### XAU/USD + FTMO
- Mismos limites FTMO que EUR/USD
- Mayor volatilidad = DD potencial mas alto por operacion
- Spread de 30 pips + 7 USD comision + 2 pips slippage = ~39 USD/lote
  → Requiere mayor desplazamiento favorable para ser rentable
  → En H1 esto es alcanzable pero reduce el margen de error
- Recomendado como activo SECUNDARIO — no primero en el pipeline

---

## RECOMENDACION FINAL

### Activo principal: EUR/USD
**Score: 8.70 / 10**

Justificacion:
1. Mayor compatibilidad con FTMO y alternativas Forex (E8, TFT)
2. Spread mas bajo del mercado — menor friccion en backtest y produccion
3. Datos completos y verificados en SQ desde 2003
4. Regimenes historicos variados en IS (2003-2020) — el Builder puede encontrar
   logicas robustas tanto trend following como mean reversion
5. Liquidez maxima — ejecucion real sin sorpresas de slippage
6. Builds anteriores (Build 6-7) usaron EUR/USD H1 — hay aprendizaje acumulado

### Activo secundario: XAU/USD
**Score: 7.80 / 10**

Justificacion:
- Excelente diversificacion respecto a EUR/USD (baja correlacion)
- Datos disponibles y verificados
- Compatible con FTMO
- Alta volatilidad puede generar strategies con alto PF si spread esta bien configurado
- Incorporar al pipeline despues de validar primera estrategia en EUR/USD

### Activos pendientes (Capa 1)
- GBP/USD: descargar datos cuando haya 3 estrategias aprobadas
- USD/JPY: descargar datos cuando haya 3 estrategias aprobadas
- NQ/GC futuros: pendiente fuente de datos CME

---

## DECISION

[x] Proceder con EUR/USD como activo principal del primer build H1
[x] Configuracion obligatoria: spread 0.5 pips + 7 USD/lote + 0.5 pip slippage
[x] Incluir XAU/USD como activo secundario — segundo build tras validar EUR/USD
[x] Posponer GBP/USD, USD/JPY, NQ y GC hasta criterios de Capa 1

---

## SIGUIENTE PASO

Invocar market-analyst para generar TICKET-001.
Activo: EUR/USD | Temporalidad: H1
Estilos a explorar: Trend Following o Mean Reversion
Leer skill-avoiding-overfitting.md obligatoriamente antes de generar hipotesis.
