---
fecha: {{date:YYYY-MM-DD}}
challenge_id: ""
prop_firm: FTMO
tipo_cuenta: 2-Step
capital: 25000
objetivo_fase1_pct: 10
dd_diario_limite_pct: 5
dd_total_limite_pct: 10
dia_numero: 1
dias_minimos: 4
balance_pico: 25000
balance_inicio_dia: 25000
balance_cierre: 25000
profit_acumulado_usd: 0
profit_acumulado_pct: 0.00
dd_diario_pct: 0.00
dd_total_pct: 0.00
trades_hoy: 0
trades_acumulados: 0
estado: VERDE
---

# Challenge Log — {{date:YYYY-MM-DD}}
**{{challenge_id}}** | {{prop_firm}} | Día {{dia_numero}}

---

## Semáforo de Estado

> [!success] 🟢 VERDE — Sistema operativo normal
> DD diario < 3% | DD total < 5% | Progreso en línea

Actualizar según estado real del día:
- 🟢 **VERDE** — DD diario < 3% AND DD total < 5% AND profit progresando
- 🟡 **AMARILLO** — DD diario 3–4.5% OR DD total 5–7.5% OR progreso lento
- 🔴 **ROJO** — DD diario ≥ 4.5% OR DD total ≥ 7.5% OR equity cerca del límite

**Estado actual:** `=this.estado`

---

## Métricas del Día

| Campo | Valor | Referencia |
|-------|-------|------------|
| Capital inicial cuenta | $`=this.capital` | Base del challenge |
| Balance inicio de día | $`=this.balance_inicio_dia` | Medianoche Prague |
| Balance cierre de hoy | $`=this.balance_cierre` | Actualizar al cerrar |
| Profit acumulado ($) | $`=this.profit_acumulado_usd` | Objetivo: $`=this.capital * this.objetivo_fase1_pct / 100` |
| Profit acumulado (%) | `=this.profit_acumulado_pct`% | Objetivo: `=this.objetivo_fase1_pct`% |
| DD diario hoy | `=this.dd_diario_pct`% | Límite: `=this.dd_diario_limite_pct`% — Alerta: 3% |
| DD total actual | `=this.dd_total_pct`% | Límite: `=this.dd_total_limite_pct`% — Alerta: 7% |
| Día de trading | `=this.dia_numero` | Mínimo: `=this.dias_minimos` |
| Trades hoy | `=this.trades_hoy` | — |
| Trades acumulados | `=this.trades_acumulados` | — |

### Límites de riesgo calculados

- **Límite DD diario hoy:** $`=round(this.balance_inicio_dia * (1 - this.dd_diario_limite_pct / 100), 2)`
- **Margen restante hoy:** $`=round(this.balance_cierre - this.balance_inicio_dia * (1 - this.dd_diario_limite_pct / 100), 2)`
- **Pico de equity:** $`=this.balance_pico` _(actualizar si sube)_
- **Límite DD total:** $`=round(this.balance_pico * (1 - this.dd_total_limite_pct / 100), 2)`
- **Margen restante total:** $`=round(this.balance_cierre - this.balance_pico * (1 - this.dd_total_limite_pct / 100), 2)`

---

## Progreso hacia el Objetivo

```
Objetivo Fase 1: +10% = ${{capital * 0.10}} USD
Profit actual:   +{{profit_acumulado_pct}}% = ${{profit_acumulado_usd}} USD

Progreso visual (actualizar manualmente):
░░░░░░░░░░  0%
████░░░░░░  40%
████████░░  80%
██████████  100% ← OBJETIVO ALCANZADO

Días completados: {{dia_numero}} / mín. {{dias_minimos}}
```

_Reemplazar la barra con el nivel real: cada █ = 10% del objetivo._

### Cuándo parar voluntariamente

Parar el EA y notificar al orchestrator cuando **AMBAS** condiciones:
1. Profit acumulado ≥ 10% del capital
2. Días de trading ≥ 4

No es necesario esperar más días — el objetivo está cumplido.

---

## Trades Ejecutados Hoy

| # | Hora (Prague) | Activo | Dir | Lotes | Entrada | Salida | P&L ($) | Resultado |
|---|---------------|--------|-----|-------|---------|--------|---------|-----------|
| 1 | | | | | | | | |
| 2 | | | | | | | | |
| 3 | | | | | | | | |

**P&L total del día:** $___
**Comisiones pagadas:** $___
**P&L neto:** $___

---

## Estado del EA

- [ ] EA activo en MT5 — sin errores en el log
- [ ] Conexión al broker estable
- [ ] Slippage dentro de lo esperado (< 3 pips en XAUUSD)
- [ ] No hay órdenes pendientes abiertas sin SL

---

## Si estado es 🟡 AMARILLO

_Describir qué se verificó y qué acción se tomó:_

---

## Si estado es 🔴 ROJO

_Describir la decisión tomada (parar EA, cerrar posiciones, contactar soporte):_

---

## Notas del Día

_Observaciones: comportamiento del EA, sesiones de mercado activas, noticias relevantes, slippage observado, anomalías._

---

## Próximas Acciones

- [ ] Verificar DD al inicio de mañana con `python scripts/ftmo-dd-calculator.py --mode verify`
- [ ] Actualizar `balance_inicio_dia` con el cierre de hoy
- [ ] Actualizar `balance_pico` si el equity subió a un nuevo máximo
- [ ] Si profit ≥ 10% AND días ≥ 4 → parar EA y abrir Fase 2
