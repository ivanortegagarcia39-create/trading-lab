# Skill: Fuentes de Datos

## Proposito
Documenta todas las fuentes de datos usadas en TradingLab:
backtesting, especificaciones de broker y filtro de noticias.
Verificar siempre la fuente antes de lanzar un nuevo build.

---

## 1. DUKASCOPY — Datos historicos M1 (principal)

**Uso:** backtesting en StrategyQuant

**URL de descarga manual:**
`https://www.dukascopy.com/swiss/english/marketwatch/historical/`

**Como descargar en SQ:**
SQ → Data Manager → Download → seleccionar símbolo → seleccionar período → Download

### Cobertura disponible

| Tipo de activo | Período disponible | Calidad |
|---------------|-------------------|---------|
| Forex Majors | M1 desde 2003 | Alta |
| Forex Crosses | M1 desde 2003 | Alta |
| XAU/USD (Oro) | M1 desde 2003 | Media-Alta |
| XAG/USD (Plata) | M1 desde 2003 | Media |
| Índices (US30, NAS100, etc.) | M1 variable | Media |
| Cripto (BTC, ETH) | M1 desde 2017-2018 | Media |

### Formato de los datos

- Formato: OHLCV en CSV comprimido (.bi5)
- SQ los importa automáticamente desde el Data Manager
- Resolución mínima: 1 minuto (M1)
- Zonas horarias: UTC+0 en los datos brutos

### Limitaciones conocidas

| Activo | Limitación | Impacto | Acción |
|--------|-----------|---------|--------|
| XAUUSD | Gaps ~2.6% — normales por mercado OTC | Bajo | Usar gap_threshold 5% en data-quality-checker.py |
| Forex (general) | Gaps en fines de semana (mercado cerrado) | Ninguno | Normal — no son gaps reales |
| Índices | Datos pueden tener huecos en horas fuera de sesión | Medio | Verificar con data-quality-checker.py |
| Cripto | Datos desde 2017 solamente — menos IS disponible | Medio | Usar IS reducido: 2017-2020 |

### Verificación de calidad

```bash
python scripts/data-quality-checker.py --activo XAUUSD --data-path data/XAUUSD/
```

Criterios de aceptación:
- Gap rate < 5% para metales
- Gap rate < 0.5% para Forex majors
- Sin outliers de precio > 10x el precio normal

---

## 2. FTMO INSTRUMENT SPECS — Especificaciones reales del broker

**Uso:** configurar comisiones y spreads en SQ para backtesting realista
**Fuente:** verificación manual en cuenta FTMO demo

### Especificaciones verificadas (2026-04)

| Instrumento | Spread | Comisión | Slippage | Swap largo | Swap corto |
|------------|--------|----------|----------|-----------|-----------|
| XAU/USD | 30 pips | 7 USD/lote | 2 pips | -50.63 USD/lote/noche | +17.67 USD/lote/noche |
| XAG/USD | 3 pips | 7 USD/lote | 1 pip | — | — |
| EUR/USD | 0.5 pips | 7 USD/lote | 0.5 pips | — | — |
| GBP/USD | 0.8 pips | 7 USD/lote | 0.5 pips | — | — |
| USD/JPY | 0.5 pips | 7 USD/lote | 0.5 pips | — | — |
| USD/CHF | 0.8 pips | 7 USD/lote | 0.5 pips | — | — |
| AUD/USD | 0.6 pips | 7 USD/lote | 0.5 pips | — | — |
| NZD/USD | 1.0 pips | 7 USD/lote | 0.5 pips | — | — |
| USD/CAD | 0.8 pips | 7 USD/lote | 0.5 pips | — | — |

**Regla critica:** verificar spreads y swaps ANTES de cada build.
Los swaps de XAUUSD pueden eliminar el edge en estrategias con muchas noches abiertas.

### Triple swap miercoles XAUUSD

El swap de miercoles a jueves cuenta por 3 dias (viernes + sabado + domingo).
Un trade largo abierto el miercoles paga: -50.63 × 3 = **-151.89 USD/lote**.
Estrategias con posiciones abiertas de noche deben superar este coste.

**Verificacion automatica:**
```bash
python scripts/strategy-analyzer.py --file results/raw/Strategy.csv --activo XAUUSD
```
Criterio: impacto triple swap < 15% del profit total.

### Como verificar specs actualizadas

1. Abrir cuenta FTMO demo en MetaTrader 5
2. Click derecho en el simbolo → Especificaciones
3. Verificar spread, comision y swap
4. Actualizar `config/build-defaults.json` si hay cambios

---

## 3. FOREXFACTORY — Calendario de noticias

**Uso:** filtro de noticias en EAs exportados
**URL:** `https://www.forexfactory.com/calendar.php`

### Formato de datos

- API no oficial: JSON via URL con parámetros de fecha
- Campos: fecha, moneda, impacto (High/Medium/Low/Holiday), evento, actual, previo, forecast
- Actualización: en tiempo real durante la semana de trading

### Uso en el pipeline

Los EAs exportados desde SQ pueden incluir un filtro de noticias.
El skill-export-mt5.md documenta cómo integrar el filtro.

**Eventos que afectan a XAUUSD:**
- USD: NFP, CPI, FOMC, GDP, Retail Sales (impacto HIGH)
- Global: decisiones de tipos de interés de todos los bancos centrales
- Geopolítico: no predecible via API

**Criterio:** no operar en ventana ±30 minutos de noticias HIGH impact USD.

---

## 4. METAQUOTES (MT5) — Datos en tiempo real

**Uso:** forward test y producción — NO para backtesting
**Acceso:** via MT5 conectado al broker (FTMO demo o cuenta funded)

### Cuándo se usa

| Momento | Fuente de datos |
|---------|----------------|
| Backtesting (Builder, Retester, WFO) | Dukascopy M1 en SQ |
| Forward test demo (2 semanas) | MT5 conectado a broker |
| Producción (challenge / funded) | MT5 conectado a broker |

**Nunca mezclar fuentes:** los datos de MT5 no son históricos — solo tiempo real.
El backtesting siempre usa Dukascopy desde SQ.

---

## REGLAS CRITICAS

1. **Verificar spreads antes de cada build** — pueden cambiar con actualizaciones de FTMO
2. **No usar datos de MT5 en backtesting** — sesgo de datos y supervivencia
3. **Comprobar gaps con data-quality-checker.py** antes de lanzar un build
4. **Los swaps de XAUUSD son asimétricos** — largos negativos, cortos positivos
5. **Datos cripto disponibles solo desde 2017** — reducir IS si se usa cripto

---

## Verificacion pre-build completa

```bash
# 1. Verificar calidad de datos
python scripts/data-quality-checker.py --activo XAUUSD

# 2. Verificar config del build (spreads)
python scripts/pre-build-checklist.py --activo XAUUSD --spread 60

# 3. Lanzar build con configuracion verificada
python scripts/build-launcher.py --build 11 --activo XAUUSD --spread-real 30
```

---

## Referencias

- `config/build-defaults.json` — spreads y comisiones por activo
- `scripts/data-quality-checker.py` — verificacion de gaps y outliers
- `scripts/strategy-analyzer.py` — calculo de impacto de swaps
- `docs/skills/skill-builder-libre.md` — configuracion del Builder con spreads correctos
