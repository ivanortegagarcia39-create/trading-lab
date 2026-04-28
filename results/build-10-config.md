# Build 10 — XAUUSD — Configuracion SQ

## Identificacion

| Campo | Valor |
|-------|-------|
| Build | 10 |
| Fecha | 2026-04-27 |
| Activo | XAUUSD |
| Simbolo SQ | XAUUSD_M1_dukas |
| Timeframe | H1 |
| Periodo IS | 2003-2020 |
| Periodo OOS | 2021-actual |

## Costes y Ejecucion

| Campo | Valor | Estado |
|-------|-------|--------|
| Spread real FTMO | 30.0 pips | — |
| Spread backtest sucio | 60.0 pips | OK |
| Slippage | 2 pips | — |
| Comision | 7 USD/lote | — |

## Gestion de Riesgo

| Campo | Valor |
|-------|-------|
| Riesgo por trade | 1% |
| Capital inicial | 25000 USD |
| Max trades/dia | 2 |
| Sesion | 08:00 – 20:00 CEST |

## Configuracion Genetica

| Campo | Valor |
|-------|-------|
| Generaciones | 30 |
| Poblacion/isla | 100 |
| Islas | 4 |
| Modo continuo | True |
| Max estrategias | 1000 |

## Filtros Activos

### Filtros SQ (en Builder)
- PF minimo: 1.3
- Trades/mes minimo: 6
- Ret/DD minimo: 0.8

### Filtros Python (evaluator-assistant.py)
- Total trades: 120
- Win Rate: 38%
- DD maximo: 7%

## Notas

Spread incorrecto - 30 pips en lugar de 60. Primer build con datos corregidos Fase 0.
