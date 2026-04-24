# Configuración de Obsidian para TradingLab

El vault de Obsidian ES el repo trading-lab.
Abrir la carpeta trading-lab como vault en Obsidian.

---

## Templater

1. Settings → Community Plugins → Templater → Options
2. Template folder location: `templates`
3. Trigger Templater on new file creation: ON
4. Automatic jump to cursor: ON (opcional)

### Uso
- Crear nuevo build report: `Ctrl+N` → seleccionar `build-report`
- Crear evaluación de estrategia: `Ctrl+N` → seleccionar `strategy-evaluation`
- Crear revisión semanal: `Ctrl+N` → seleccionar `daily-review`

---

## Dataview

1. Settings → Community Plugins → Dataview → Options
2. Enable JavaScript Queries: ON
3. Inline Query Prefix: `=`
4. Refresh Interval: 5000 ms

### Queries usadas en el dashboard
- `FROM "agents"` — lista todos los archivos en agents/
- `FROM "docs/skills"` — lista todos los skills
- `FROM "scripts"` — lista todos los scripts
- `FROM "docs/roadmap"` — lee el planning maestro

---

## Uso del Dashboard

1. Abrir `dashboard.md` en la raíz del vault
2. Las tablas Dataview se actualizan automáticamente
3. Los enlaces `[[...]]` navegan directamente a los archivos

---

## Estructura de carpetas en el vault

```
trading-lab/
├── dashboard.md          ← punto de entrada
├── CLAUDE.md             ← constitución del proyecto
├── agents/               ← definición de agentes
├── docs/
│   ├── skills/           ← skills del pipeline
│   ├── roadmap/          ← planning maestro
│   ├── project-status.md
│   ├── lessons-learned.md
│   └── obsidian-setup.md ← este archivo
├── templates/            ← plantillas Templater
│   ├── build-report.md
│   ├── strategy-evaluation.md
│   └── daily-review.md
├── results/              ← outputs del pipeline
│   └── build-10-report.md
└── scripts/              ← scripts Python y MQL5
```

---

## Notas

- Los archivos `.obsidian/` están en .gitignore — no se commitean.
- Las plantillas en `templates/` sí están versionadas en git.
- El dashboard usa Dataview — requiere el plugin instalado y activo.
