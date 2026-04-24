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

## Pendiente de Hardware

| Tarea | Requiere | Fase |
|-------|----------|------|
| Instalar Ollama | alber encendido | Fase 3 |
| Instalar ChromaDB | alber encendido | Fase 3 |
| Relanzar Build 10 con spread 60 pips | SQ en alber | Inmediato |
| Reparar repo alber | alber encendido | Inmediato |
| Contratar VPS MT5 | Tarjeta de crédito | Fase 5 |
| Crear bot Telegram | Cuenta Telegram | Fase 4 |
| Instalar N8N | alber + 5 estrategias | Fase 6 |
