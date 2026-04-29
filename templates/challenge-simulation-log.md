---
fecha: YYYY-MM-DD
estrategia_id: STRAT-XXX
propfirm: FTMO | E8 | BrightFunded
capital: 10000 | 25000 | 50000 | 100000
fase1_resultado: PASS | FAIL | EN_CURSO
fase1_dias: 0
fase1_profit_pct: 0.00
fase1_dd_max_dia: 0.00
fase1_dd_max_total: 0.00
fase1_pf: 0.00
fase2_resultado: PASS | FAIL | EN_CURSO | PENDIENTE
fase2_dias: 0
fase2_profit_pct: 0.00
fase2_dd_max_dia: 0.00
fase2_dd_max_total: 0.00
fase2_pf: 0.00
veredicto_final: PASS | FAIL | REVISAR
score_final: 0
notas: ""
---

# Challenge Simulation Log — {{estrategia_id}}

## Configuración de la Simulación

| Campo | Valor |
|-------|-------|
| Estrategia | {{estrategia_id}} |
| PropFirm | {{propfirm}} |
| Capital simulado | ${{capital}} |
| Fecha simulación | {{fecha}} |
| Simulaciones Monte Carlo | 1000 |
| Seed | aleatorio |

**Parámetros de la estrategia:**
- Activo: 
- Timeframe: H1
- Comisiones incluidas: sí
- Spread usado: 

---

## Resultados Fase 1 (Challenge)

| Métrica | Objetivo | Resultado | Estado |
|---------|----------|-----------|--------|
| Profit target | +10% | {{fase1_profit_pct}}% | |
| DD máximo diario | < 5% | {{fase1_dd_max_dia}}% | |
| DD máximo total | < 10% | {{fase1_dd_max_total}}% | |
| Profit Factor | > 1.0 | {{fase1_pf}} | |
| Días utilizados | ≤ 30 | {{fase1_dias}} | |

**Veredicto Fase 1:** {{fase1_resultado}}

Notas de la fase 1:
- 

---

## Resultados Fase 2 (Verification)

| Métrica | Objetivo | Resultado | Estado |
|---------|----------|-----------|--------|
| Profit target | +5% | {{fase2_profit_pct}}% | |
| DD máximo diario | < 5% | {{fase2_dd_max_dia}}% | |
| DD máximo total | < 10% | {{fase2_dd_max_total}}% | |
| Profit Factor | > 1.0 | {{fase2_pf}} | |
| Días utilizados | ≤ 60 | {{fase2_dias}} | |

**Veredicto Fase 2:** {{fase2_resultado}}

Notas de la fase 2:
- 

---

## Análisis del Crítico Interno

**Score final de la simulación:** {{score_final}} / 100

| Aspecto | Evaluación |
|---------|------------|
| Consistencia día a día | |
| Comportamiento en épocas de estrés | |
| Ratio riesgo/recompensa | |
| Probabilidad de fallo DD diario | |
| Probabilidad de fallo DD total | |

**Hipótesis de fallo (si aplica):**
- 

**Recomendación del crítico:**
> 

---

## Decisión Final y Próximos Pasos

**Veredicto:** {{veredicto_final}}

| Condición | Acción |
|-----------|--------|
| PASS ambas fases | Proceder a forward test demo → challenge real |
| PASS Fase 1, FAIL Fase 2 | Revisar sizing, reducir riesgo por operación |
| FAIL Fase 1 | Revisar estrategia, no pasar a challenge |
| REVISAR | Ejecutar más simulaciones con diferentes seeds |

**Próximo paso:**
- [ ] 

**Notas adicionales:**
{{notas}}
