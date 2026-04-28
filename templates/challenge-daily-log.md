---
fecha: {{date:YYYY-MM-DD}}
challenge_id: ""
prop_firm: FTMO
capital: 25000
dia_numero: 1
balance_inicio_dia: 25000
balance_actual: 25000
profit_acumulado_pct: 0.00
dd_diario_pct: 0.00
dd_total_pct: 0.00
trades_hoy: 0
estado: VERDE
---

# Challenge Log — {{date:YYYY-MM-DD}}

## Métricas del Día

| Campo | Valor | Referencia |
|-------|-------|------------|
| Capital inicial | ${{capital}} | — |
| Balance inicio de día | ${{balance_inicio_dia}} | Medianoche Prague |
| Balance actual | ${{balance_actual}} | Al cierre |
| Profit acumulado | $`=round((this.balance_actual - this.capital), 2)` | Objetivo: $`=this.capital * 0.10` |
| Progreso objetivo | `=round((this.balance_actual - this.capital) / (this.capital * 0.10) * 100, 1)`% | Meta: 100% |
| DD diario hoy | {{dd_diario_pct}}% | Límite: 5% — Alerta: 3% |
| DD total actual | {{dd_total_pct}}% | Límite: 10% — Alerta: 7% |
| Días trading | {{dia_numero}} | Mínimo: 4 |
| Trades hoy | {{trades_hoy}} | — |

### Cálculos de límites

- **Límite diario hoy:** $`=round(this.balance_inicio_dia * 0.95, 2)` (5% de ${{balance_inicio_dia}})
- **Margen restante diario:** $`=round(this.balance_actual - this.balance_inicio_dia * 0.95, 2)`
- **Pico de equity hist.:** _actualizar manualmente_
- **Límite total:** $`=round(this.capital * 0.90, 2)` (base — ver pico real)

---

## Trades Ejecutados

| # | Hora (Prague) | Par | Dir | Lotes | Entrada | Salida | P&L |
|---|---------------|-----|-----|-------|---------|--------|-----|
| 1 | | | | | | | |
| 2 | | | | | | | |
| 3 | | | | | | | |

**P&L total del día:** $___

---

## Semáforo de Estado

**Estado actual:** {{estado}}

- [ ] 🟢 VERDE — DD diario < 3% y DD total < 5% y profit en progreso
- [ ] 🟡 AMARILLO — DD diario 3-4.5% OR DD total 5-7.5% OR profit < 50% objetivo a mitad de tiempo
- [ ] 🔴 ROJO — DD diario >= 4.5% OR DD total >= 7.5% OR equity < $300 del límite diario

### Si AMARILLO — acciones tomadas
_Describir aquí qué se verificó_

### Si ROJO — acciones tomadas
_Describir aquí qué decisiones se tomaron_

---

## Notas

_Observaciones del día: comportamiento del EA, sesiones de mercado, noticias relevantes, slippage observado_

---

## Próximos Pasos

- [ ] Verificar DD al inicio de la próxima sesión con `ftmo-dd-calculator.py --mode verify`
- [ ] Actualizar balance_inicio_dia mañana con el cierre de hoy
- [ ] Si objetivo alcanzado y días >= 4 → detener EA y notificar al orchestrator
