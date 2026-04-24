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

```dataview
TABLE file.mtime as "Última modificación"
FROM "scripts"
SORT file.name ASC
```

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
