# Carpeta results/ — Guia de Archivos

Todos los outputs del pipeline se guardan aqui.
Los archivos se generan automaticamente por los scripts
y agentes del sistema. No editar manualmente.

---

## Archivos Generados Automaticamente

| Archivo | Generado por | Contenido |
|---------|-------------|-----------|
| `build-[N]-report.md` | Manual / template | Resultados del build con observaciones |
| `build-[N]-config.json` | sqx-build-config.py | Configuracion exacta del build |
| `build-[N]-config.md` | sqx-build-config.py | Config legible en Markdown |
| `build-[N]-analysis.md` | build-analyzer.py + Ollama | Resumen ejecutivo del build |
| `evaluation-gate-results.json` | evaluator-assistant.py | Estrategias que pasan / descartan |
| `portfolio-selected.json` | portfolio-builder.py | Portfolio seleccionado con pesos HRP |
| `portfolio-weights.json` | hrp-portfolio.py | Pesos HRP del portfolio |
| `audit-trail.log` | hash-logger.py | Decisiones con SHA-256 inmutable (3 entradas activas) |
| `build-regime-snapshot.json` | market-regime-snapshot.py | Foto de regimen inicio/fin del build |
| `pre-build-check.json` | pre-build-checklist.py | Verificacion pre-build |
| `pipeline-report-[fecha].md` | pipeline-runner.py | Informe completo del pipeline |
| `criteria-proposals.json` | lessons-analyzer.py | Propuestas de ajuste de criterios |
| `strategies-registry.json` | strategy-versioning.py | Registro de 24 estrategias con metadata y hashes |
| `accounts-inventory.json` | multi-account-orchestrator | Inventario de cuentas activas |
| `scaling-history.json` | scaling-manager | Historial de scaling de cuentas |
| `session-memory.json` | orchestrator | Memoria de corto plazo (se borra en inicio) |
| `regime-history.json` | market-regime-detector | Historial diario de regimenes |
| `recovery-log.json` | account-recovery-manager | Log de activaciones de recuperacion |
| `health-dashboard.md` | orchestrator (semanal) | Dashboard de salud del sistema |
| `pipeline-metrics.md` | orchestrator (por ciclo) | Metricas de aprobacion por puerta |
| `weekly-report-[fecha].md` | auto-reporter.py | Informe semanal automatico del proyecto |
| `build-queue.json` | build-queue-manager.py | Cola de builds con activos, scores y estado |
| `session-log.json` | session-starter.py | Log de sesiones iniciadas por dispositivo |
| `system-health.json` | system-health-check.py | Resultado de los 8 health checks del sistema |

---

## Subcarpetas

| Carpeta | Contenido |
|---------|-----------|
| `approved/` | Estrategias aprobadas listas para export |
| `rejected/` | Estrategias descartadas con criterio de descarte |
| `reviewed/` | Estrategias en revision intermedia (post-retester) |
| `production-logs/` | Logs de EAs en produccion real |
| `compliance/` | Hashes de T&C de prop firms |
| `build-10-sqx/` | 23 archivos .sqx del Build 10 (XAUUSD H1) — binarios irremplazables |
| `raw/` | CSVs exportados del databank de SQ antes del pipeline |

---

## Archivos que NO van al repo (.gitignore)

- `session-memory.json` — se borra al inicio de cada sesion
- `*.log` — pueden contener datos sensibles de cuentas
- `backups/sq_configs/` — binarios grandes de SQ
- `production-logs/` — datos de produccion en tiempo real

**Excepcion:** `build-10-sqx/*.sqx` SI va al repo — son irremplazables y no contienen datos sensibles.

---

## Flujo de archivos por etapa del pipeline

```
[SQ Builder]
    → Strategy*.csv (exportar databank manualmente)

[evaluator-assistant.py]
    → evaluation-gate-results.json

[portfolio-builder.py]
    → portfolio-selected.json

[pipeline-runner.py]
    → pipeline-report-[fecha].md
    → (llama a los scripts anteriores)

[sqx-build-config.py]
    → build-[N]-config.json
    → build-[N]-config.md

[market-regime-snapshot.py]
    → build-regime-snapshot.json

[build-analyzer.py]
    → build-[N]-analysis.md

[hash-logger.py]
    → audit-trail.log
```
