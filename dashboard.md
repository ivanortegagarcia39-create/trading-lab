# TradingLab — Dashboard

## Estado del Sistema

| Campo | Valor |
|-------|-------|
| Fase actual | Capa 0 |
| Build activo | Build 10 — XAUUSD H1 |
| Estrategias en producción | 0 |
| Estrategias en databank | 2 (en curso) |
| Última actualización | 2026-04-22 |

---

## Progreso del Planning Maestro

```dataview
TABLE fase, completadas, pendientes, porcentaje
FROM "docs/roadmap"
WHERE file.name = "planning-maestro-status"
```

---

## Agentes Activos

```dataview
TABLE file.mtime as "Última modificación"
FROM "agents"
SORT file.mtime DESC
```

---

## Skills Operativas

```dataview
TABLE file.mtime as "Última modificación"
FROM "docs/skills"
SORT file.mtime DESC
```

---

## Scripts Disponibles

| Script | Propósito | Fase |
|--------|-----------|------|
| validate-sqx-folder.py | Valida divergencia entre builds | Fase 0 |
| validate-sqx-build.py | Valida un único CSV de build | Fase 0 |
| verify-symbol-specs.py | Verifica specs de símbolos vs FTMO | Fase 0 |
| hash-logger.py | Audit trail inmutable SHA-256 | Fase 1 |
| hrp-portfolio.py | Optimización HRP del portfolio | Fase 1 |
| strategy-fingerprint.py | Hash único de lógica de estrategia | Fase 1 |
| coordination-detector.py | Detecta estrategias demasiado similares | Fase 1 |
| mql5-auditor.py | Audita código MQL5 antes del deploy | Fase 1 |
| inflation-diagnostic.py | Detecta sobreajuste post-WFO | Fase 1 |
| build-analyzer.py | Resumen ejecutivo post-build con Ollama | Fase 3 |
| knowledge-base.py | Indexa historial en ChromaDB | Fase 3 |
| lessons-analyzer.py | Analiza lecciones con Ollama | Fase 3 |
| vps-health-monitor.py | Monitorea salud del VPS | Fase 4 |
| ftmo-timezone-sync.mq5 | Sincroniza timezone con FTMO Prague | Fase 4 |
| sq-watchdog.py | Monitorea que SQ no se congele | Fase 5 |
| strategy-versioning.py | Gestiona versioning de estrategias | Fase 9 |

---

## Pipeline de Evaluación

| Puerta | Herramienta | Criterio Principal | Ratio |
|--------|-------------|-------------------|-------|
| 1. Builder Filter | SQ | PF > 1.3 | ~5% |
| 2. EvalGate | evaluator-assistant.py | Trades/WR/DD | ~40% |
| 3. Retester 12b | SQ + Python | OOS degradation | ~40% |
| 4. SPP | SQ/Python | Robustez ±10% | ~50% |
| 5. WFO Matrix | SQ | WFE >= 50% | ~50% |
| 6. Stress Test | SQ Retester | DD < 8% periodos | ~60% |
| 7. Multimarket | SQ Retester | PF > 1.0 correl. | ~70% |
| 8. Portfolio | portfolio-builder.py | Corr < 0.5 | 3-5 |
| 9. Forward Test | MT5 demo | PF >= 70% OOS | ~70% |

---

## Builds Históricos

| Build | Activo | TF | Estado | Databank | Mejor PF |
|-------|--------|----|--------|----------|----------|
| 1-8 | Varios | M15/H1 | DESCARTADOS | 0 | < 1.3 |
| 10 | XAUUSD | H1 | EN CURSO | 2 | 1.31 |

---

## Últimas Lecciones Aprendidas

```dataview
TABLE estado, activo, build
FROM "docs"
WHERE file.name = "lessons-learned"
```

---

## Acciones Rápidas

- [[docs/project-status|📊 Ver Project Status]]
- [[docs/lessons-learned|📖 Ver Lecciones Aprendidas]]
- [[docs/roadmap/planning-maestro-status|🗺️ Ver Planning Maestro]]
- [[agents/orchestrator|🤖 Ver Orchestrator]]
- [[results/build-10-report|📋 Ver Build 10 Report]]
- [[docs/obsidian-setup|⚙️ Configuración Obsidian]]

---

## Archivos de Configuracion

| Archivo | Proposito |
|---------|-----------|
| config/build-defaults.json | Spreads, slippage, swaps por activo |
| config/pipeline-config.json | Umbrales numericos de todas las puertas |
| config/telegram-config.json | Credenciales Telegram (no en git) |

---

## Templates Disponibles

| Template | Uso |
|----------|-----|
| templates/build-report.md | Resultado de cada build SQ |
| templates/strategy-evaluation.md | Evaluacion individual de estrategia |
| templates/daily-review.md | Revision diaria del sistema |
| templates/challenge-daily-log.md | Log diario de challenge FTMO |
| templates/weekly-pipeline-review.md | Revision semanal del pipeline |

---

## Estado de Scripts Python
Todos los scripts probados y operativos en ivano (2026-04-27):

| Script | Estado | Dependencias |
|--------|--------|-------------|
| pre-build-checklist.py | OK | pandas, pytz |
| evaluator-assistant.py | OK | pandas |
| portfolio-builder.py | OK | pandas, numpy |
| pipeline-runner.py | OK | pandas |
| build-analyzer.py | OK | pandas |
| hash-logger.py | OK | hashlib |
| strategy-versioning.py | OK | json |
| knowledge-base.py | OK | chromadb |
| telegram-notifier.py | OK | requests |
| lessons-analyzer.py | OK | re |
| hrp-portfolio.py | OK | numpy |
| strategy-fingerprint.py | OK | xml, hashlib |
| inflation-diagnostic.py | OK | pandas |
| coordination-detector.py | OK | json |
| sqx-build-config.py | OK | json, pytz |
| market-regime-snapshot.py | OK | pandas, numpy |
| validate-sqx-folder.py | OK | pandas |
| mql5-auditor.py | OK | re |
| sq-watchdog.py | OK | subprocess |
| vps-health-monitor.py | OK | subprocess |
| ftmo-dd-calculator.py | OK | pandas, pytz |
| strategy-analyzer.py | OK | pandas |
| portfolio-monitor.py | OK | pandas |
| system-health-check.py | OK | subprocess |
| session-starter.py | OK | subprocess |

---

## Telegram Bot

- Bot: @tradinglab_monitor_bot
- Estado: Activo
- Notificaciones: INFO / WARNING / CRITICAL

---

## Pendiente de Hardware

| Tarea | Requiere | Fase |
|-------|----------|------|
| Instalar Ollama | alber encendido | Fase 3 |
| Instalar ChromaDB | alber encendido | Fase 3 |
| Lanzar Build 11 con spread 60 pips | SQ en alber | Inmediato |
| Contratar VPS MT5 | Tarjeta de credito | Fase 5 |
| Instalar N8N | alber + 5 estrategias | Fase 6 |
