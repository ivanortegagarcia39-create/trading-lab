# Skill: Checklist de Puertas del Pipeline

## Proposito
Referencia rapida durante sesiones de trabajo.
Marca cada puerta a medida que avanza la estrategia.

Los criterios completos estan en `docs/skills/skill-evaluation-auto.md`.
Los umbrales numericos exactos estan en `config/pipeline-config.json`.

---

## Checklist de las 9 Puertas

| # | Puerta | Herramienta | Criterio clave | Estado |
|---|--------|-------------|----------------|--------|
| 1 | **Builder Filter** | SQ (automatico) | PF > 1.3 \| Trades/mes > 6 | [ ] |
| 2 | **Evaluation Gate** | evaluator-assistant.py | PF ≥ 1.5 \| DD ≤ 7% \| Trades ≥ 120 \| WR ≥ 38% | [ ] |
| 3 | **Retester OOS (12b)** | SQ Retester | PF OOS ≥ 1.3 \| Caida PF ≤ 20% | [ ] |
| 4 | **SPP** | SQ / Python | Robustez con params ±10% — PF no colapsa | [ ] |
| 5 | **WFO Matrix** | SQ Optimizer | WFE ≥ 50% \| 0 ventanas PF < 0.9 | [ ] |
| 6 | **Stress Test** | SQ Retester | DD < 8% en los 5 periodos criticos | [ ] |
| 7 | **Multimarket Test** | SQ Retester | PF > 1.0 en al menos 2 activos correlacionados | [ ] |
| 8 | **Portfolio Selection** | portfolio-builder.py | Correlacion < 0.5 \| DD combinado < 12% | [ ] |
| 9 | **Forward Test Demo** | MT5 demo | PF demo ≥ 70% del PF OOS \| 2 semanas | [ ] |

---

## Puerta 1 — Builder Filter

Automatico dentro de SQ. No requiere accion manual.

- [ ] PF > 1.3
- [ ] Trades/mes > 6
- [ ] Ratio Ret/DD > 0.8
- [ ] Monte Carlo activado en Builder

**Herramienta:** SQ Builder (filtros internos)
**Resultado:** Candidatas en el databank

---

## Puerta 2 — Evaluation Gate

```bash
python scripts/evaluator-assistant.py --results-folder results/
```

- [ ] PF IS ≥ 1.5
- [ ] Max DD IS ≤ 7%
- [ ] Trades totales ≥ 120
- [ ] Trades/mes ≥ 8
- [ ] Win Rate ≥ 38%
- [ ] Ratio TP/SL efectivo ≥ 2:1
- [ ] Anos positivos ≥ 75%
- [ ] Beneficio en un solo mes ≤ 45%
- [ ] Sin DD maximo en ultimos 3 meses del IS

**Resultado:** `results/evaluation-gate-results.json`

---

## Puerta 3 — Retester OOS (Paso 12b)

Lanzar SQ Retester con los CSVs aprobados en Puerta 2.

- [ ] PF OOS ≥ 1.3
- [ ] Caida PF IS→OOS ≤ 20%
- [ ] DD OOS ≤ 6.5%
- [ ] Trades/mes OOS ≥ 6

**Veto automatico si:** PF OOS < 1.2 OR caida > 25% OR DD OOS > 7%

---

## Puerta 4 — SPP (Sensitivity to Parameter Perturbation)

Lanzar SQ Optimizer con perturbacion de parametros ±10%.

- [ ] PF no colapsa con variacion de parametros
- [ ] Logica de entrada sigue siendo positiva
- [ ] Sin estrategias con PF que depende de 1 parametro exacto

---

## Puerta 5 — WFO Matrix

Lanzar SQ Optimizer en modo Walk Forward.

- [ ] WFE ≥ 50%
- [ ] 0 ventanas OOS con PF < 0.9
- [ ] 0 ventanas OOS negativas consecutivas
- [ ] DD OOS ≤ 7% en todas las ventanas
- [ ] PF OOS ultima ventana ≥ 1.1
- [ ] Parametros estables (desviacion < 25%)

**Veto si:** WFE < 40% OR 2+ ventanas PF < 1.0

---

## Puerta 6 — Stress Test

Lanzar SQ Retester en los 5 periodos criticos.

| Periodo | Evento |
|---------|--------|
| 2008-2009 | Crisis financiera global |
| 2011-2012 | Crisis deuda europea |
| 2014-2015 | Flash crash EUR/CHF |
| 2020 Q1 | COVID-19 crash |
| 2022 | Inflacion + subida de tasas |

- [ ] DD < 8% en cada periodo
- [ ] PF > 1.0 en al menos 3 de 5 periodos

---

## Puerta 7 — Multimarket Test

Lanzar Retester con datos del activo correlacionado.

- [ ] PF > 1.0 en al menos un activo diferente al IS
- [ ] Logica no esta sobreajustada a un unico activo

---

## Puerta 8 — Portfolio Selection

```bash
python scripts/portfolio-builder.py
```

- [ ] Correlacion con otras estrategias < 0.5
- [ ] DD combinado del portfolio < 12%
- [ ] Al menos 3 estrategias no correlacionadas
- [ ] Max 2 estrategias por activo
- [ ] Diversificacion de estilos (trend + mean-reversion)

**Resultado:** `results/portfolio-selected.json`

---

## Puerta 9 — Forward Test Demo

Unica intervencion humana. Cargar EA en MT5 demo.

- [ ] EA compilado y cargado en MT5 demo
- [ ] 2 semanas de forward test completadas
- [ ] PF demo ≥ 70% del PF OOS
- [ ] DD demo < DD OOS maximo
- [ ] Sin errores de ejecucion en MT5

**Si pasa:** comprar challenge en prop firm
**Si falla:** volver a Puerta 2 con ajustes de parametros

---

## Flujo de descarte

Cada puerta que falla → estrategia va a `results/rejected/` con criterio de descarte documentado.
Sin segunda oportunidad para estrategias descartadas (Regla inquebrantable #4).

---

## Referencias

- Criterios completos: `docs/skills/skill-evaluation-auto.md`
- Umbrales numericos: `config/pipeline-config.json`
- WFO detallado: `docs/skills/skill-wfo-matrix.md`
- Stress test: `docs/skills/skill-stress-test.md`
- Portfolio: `docs/skills/skill-portfolio-selection.md`
