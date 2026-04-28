# Skill: Guia de Ejecucion del Pipeline

## Proposito
Referencia practica para ejecutar el pipeline completo en una sesion real.
Cada fase indica: comando exacto → accion humana → accion automatica del sistema.

---

## Antes de empezar — Inicio de sesion

```bash
# En ivano (documentacion, scripts)
git pull origin main
python scripts/session-starter.py

# En alber (SQ, builds)
git pull origin main
python scripts/system-health-check.py
```

- **Humano:** revisar alertas del health check
- **Sistema:** verifica dependencias, ChromaDB, Telegram, scripts

---

## Fase 1 — Builder Libre (24-48h)

### Preparacion (ivano)
```bash
python scripts/build-queue-manager.py next
python scripts/build-launcher.py --build 11 --activo XAUUSD --spread-real 30
```
- **Humano:** confirmar configuracion, verificar SQ segun instrucciones
- **Sistema:** pre-build-checklist, sqx-build-config, notificacion Telegram

### Lanzar en alber
- **Humano:** abrir SQ → Builder → Start (Start again when finished ACTIVADO)
- **Sistema:** nada (SQ corre autonomamente 24-48h)

### Monitoreo durante el build
```bash
python scripts/sq-watchdog.py --monitor --interval 1800
```
- **Humano:** vigilar temperatura CPU (< 80C), verificar que SQ sigue corriendo
- **Sistema:** backup horario automatico, alerta Telegram si SQ se congela

### Cuando SQ termina
- **Humano:** SQ → Databank → Seleccionar todo → Export → CSV → guardar en results/raw/
- **Sistema:** nada (exportacion manual obligatoria)

---

## Fase 2 — EvalGate (automatico)

```bash
python scripts/build-finisher.py --build 11 --activo XAUUSD --results-folder results/
```
- **Humano:** ejecutar el script y revisar el resumen
- **Sistema:** EvalGate, build-analyzer, actualiza cola, re-index ChromaDB, Telegram

**Resultado esperado:** X estrategias pasan de Y totales (~10-20%)
**Archivos generados:**
- `results/evaluation-gate-results.json`
- `results/build-11-analysis.md`

---

## Fase 3 — Retester / Paso 12b (SQ manual)

```bash
python scripts/retester-helper.py
```
- **Humano:** leer las instrucciones, abrir SQ → Retester, cargar estrategias aprobadas
- **Sistema:** genera checklist `results/retester-checklist-[fecha].md`

**Configuracion en SQ:**
- Datos OOS: 2021-01-01 → 2026-04-01
- Monte Carlo: SI, 200 simulaciones, 95% confianza
- NO modificar parametros

**Humano despues del Retester:**
1. Rellenar checklist con resultados (PF OOS, DD OOS, Trades/mes)
2. Marcar con [x] las que pasan el Paso 12b
3. Criterio: PF OOS ≥ 1.3, caida ≤ 20%, DD OOS ≤ 6.5%, trades/mes ≥ 6

---

## Fase 4 — WFO Matrix (SQ manual)

```bash
python scripts/wfo-helper.py
```
- **Humano:** leer instrucciones, abrir SQ → Optimizer → Walk Forward
- **Sistema:** genera checklist `results/wfo-checklist-[fecha].md`

**Configuracion en SQ:**
- IS split: 70% | OOS split: 30% | Ventanas: 5
- WF Matrix: ACTIVADO | Catastrophic Veto: ACTIVADO
- Parametros: mismo rango que el Builder original

**Humano despues del WFO:**
1. Rellenar checklist (WFE%, PF OOS por ventana, DD OOS)
2. Marcar con [x] las que aprueban
3. Criterio: WFE ≥ 50%, ninguna ventana PF < 0.9, DD ≤ 7%

---

## Fase 5 — Stress Test historico (SQ manual)

```bash
python scripts/stress-tester.py
```
- **Humano:** leer instrucciones, ejecutar Retester en cada uno de los 5 periodos criticos
- **Sistema:** genera tabla `results/stress-test-results-[fecha].md`

**5 periodos criticos:**

| # | Periodo | Fechas |
|---|---------|--------|
| 1 | Crisis Financiera 2008 | 2007-10-01 → 2009-03-31 |
| 2 | Flash CHF 2015 | 2015-01-01 → 2015-03-31 |
| 3 | COVID-19 2020 | 2020-02-01 → 2020-05-31 |
| 4 | Inflacion 2022 | 2022-01-01 → 2022-12-31 |
| 5 | SVB 2023 | 2023-02-01 → 2023-06-30 |

**Criterio:** DD < 8% en cada periodo. Superar al menos 3/5.

**Humano despues del stress test:**
1. Rellenar tabla con DD max y PF de cada periodo
2. Marcar con [x] las que pasan al Multimarket Test

---

## Fase 5b — Multimarket Test (SQ manual)

Sin script dedicado — ejecutar manualmente en SQ Retester.

- **Humano:** Retester en 1-2 activos correlacionados al activo principal
- **Criterio:** PF > 1.0 en al menos un activo diferente al IS
- **Objetivo:** confirmar que la logica no esta sobreajustada a un unico activo

---

## Fase 6 — Portfolio Selection (automatico)

```bash
python scripts/portfolio-builder.py
```
- **Humano:** revisar el portfolio sugerido y confirmar
- **Sistema:** HRP weights, correlacion, DD combinado, seleccion automatica

**Criterios:**
- Correlacion entre estrategias < 0.5
- DD combinado < 12%
- Al menos 3 estrategias no correlacionadas

**Archivos generados:**
- `results/portfolio-selected.json`
- `results/portfolio-weights.json`

---

## Fase 7 — Forward Test Demo (MT5)

Sin script — intervencion humana completa.

1. **Humano:** ejecutar `export-specialist.md` para generar el EA en MQL5
2. **Humano:** compilar EA en MetaEditor
3. **Humano:** cargar EA en MT5 demo durante 2 semanas
4. **Humano:** verificar al finalizar:
   - PF demo ≥ 70% del PF OOS
   - DD demo < DD OOS maximo
   - Sin errores de ejecucion

```bash
# Log diario del forward test (Obsidian)
# Usar template: templates/challenge-daily-log.md
```

---

## Fase 8 — Autorizacion del Challenge

Cuando el forward test pasa:

```bash
python scripts/hash-logger.py --event FORWARD_TEST_PASS \
  --description "Estrategia [ID] — PF demo: X.XX — 2 semanas OK"
```

**Humano:** comprar el challenge en FTMO (u otra prop firm).
**Sistema:** performance-monitor.md queda en standby para monitoreo.

Notificacion automatica via Telegram cuando se configure el EA en VPS.

---

## Fin de sesion — Cierre

```bash
# En ivano
git add .
git commit -m "Sesion [fecha]: [descripcion de lo trabajado]"
git push origin main

# En alber (si hubo resultados)
git add results/
git commit -m "Build [N]: [descripcion]"
git push origin main
```

**Regla:** nunca cerrar sesion sin hacer push.
**Regla:** si alber tiene resultados sin pushear → perder esos resultados si se apaga.

---

## Comandos de referencia rapida

```bash
# Cola de builds
python scripts/build-queue-manager.py list

# Pre-build (antes de lanzar SQ)
python scripts/build-launcher.py --build N --activo XAUUSD --spread-real 30

# Post-build (cuando SQ termina)
python scripts/build-finisher.py --build N --activo XAUUSD --results-folder results/

# Retester
python scripts/retester-helper.py

# WFO
python scripts/wfo-helper.py

# Stress Test
python scripts/stress-tester.py

# Portfolio
python scripts/portfolio-builder.py

# Informe semanal
python scripts/auto-reporter.py --no-ollama

# Health check
python scripts/system-health-check.py
```

---

## Referencias

- Criterios numericos: `config/pipeline-config.json`
- Checklist de puertas: `docs/skills/skill-pipeline-gates-checklist.md`
- Diagrama del pipeline: `docs/architecture/pipeline-diagram.md`
- Criterios completos: `docs/skills/skill-evaluation-auto.md`
