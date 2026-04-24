---
fecha: {{date:YYYY-MM-DD}}
estrategia_id: 
build: 
activo: 
pf_is: 
dd_is: 
trades_totales: 
win_rate: 
sharpe: 
decision: PASA
criterio_decision: 
---

# Evaluación — {{estrategia_id}}

## Métricas IS
| Métrica | Valor | Umbral | Estado |
|---------|-------|--------|--------|
| PF | {{pf_is}} | >= 1.5 | |
| DD máximo | {{dd_is}}% | <= 6% | |
| Trades totales | {{trades_totales}} | >= 120 | |
| Win Rate | {{win_rate}}% | >= 38% | |
| Sharpe | {{sharpe}} | >= 0.5 | |

## Decisión
**{{decision}}** — {{criterio_decision}}

## Notas
[Observaciones adicionales]
