# Skill: Obsidian Workflow — TradingLab

## Proposito
Obsidian ES el vault del repositorio trading-lab.
Todo lo que se escribe en Obsidian se sincroniza con git.
No hay separacion entre "notas" y "documentacion":
son el mismo archivo, en el mismo repo, bajo el mismo control de versiones.

---

## REGLA FUNDAMENTAL

Los archivos .md creados o editados en Obsidian
se commitean con git como cualquier otro archivo del proyecto.
Obsidian es la interfaz visual. Git es la fuente de verdad.

Flujo correcto:
1. Crear o editar nota en Obsidian
2. Guardar (Ctrl+S — se guarda automaticamente)
3. Hacer commit desde Claude Code o terminal
4. Push a GitHub

NO existe un "vault separado" — todo vive en `C:\Users\ivano\trading-lab`.

---

## FLUJO DIARIO

### Si hay challenge activo
1. Abrir `dashboard.md` — ver estado general del sistema
2. Crear log diario con template `challenge-daily-log.md`:
   - Ctrl+N → seleccionar template → rellenar frontmatter
   - Guardar en: `Trading/Challenges/[PROP-FIRM]/[CUENTA]/[FECHA].md`
   - Actualizar: balance_inicio_dia, dd_diario_pct, dd_total_pct, estado
3. Verificar DD con script:
   ```
   python scripts/ftmo-dd-calculator.py --mode verify --trades-csv trades.csv
   ```
4. Al final del dia: rellenar tabla de trades ejecutados y notas

### Si no hay challenge activo
1. Abrir `dashboard.md` — ver estado del pipeline
2. Si hay build corriendo: anotar candidatas nuevas en databank
3. Si hay estrategias en evaluacion: registrar resultados EvalGate
4. Revisar `docs/lessons-learned.md` despues de cada build completado

---

## FLUJO SEMANAL

Cada lunes (o primer dia de la semana laboral):

1. Crear nota de revision semanal con template `weekly-pipeline-review.md`:
   - Guardar en: `docs/reviews/[AÑO]/weekly-[SEMANA].md`
2. Revisar `docs/roadmap/planning-maestro-status.md`:
   - Marcar tareas completadas la semana anterior
   - Actualizar totales si aplica
3. Actualizar `docs/project-status.md`:
   - Estado actual del build activo
   - Cambios en estrategias en pipeline
4. Ejecutar reporte de portfolio si hay cuentas activas:
   ```
   python scripts/portfolio-monitor.py --mode report
   ```
5. Hacer commit semanal de toda la documentacion actualizada

---

## PLUGINS INSTALADOS Y USO

### Dataview
Permite queries SQL-like sobre el frontmatter de las notas.
Se usa en `dashboard.md` para:
- Mostrar estado del planning maestro automaticamente
- Listar agentes activos con fecha de modificacion
- Listar skills con fecha de modificacion
- Mostrar ultimas lecciones aprendidas

Sintaxis basica:
```dataview
TABLE campo1, campo2
FROM "carpeta"
WHERE condicion
SORT campo DESC
```

Para ver resultados del frontmatter de challenge logs:
```dataview
TABLE profit_acumulado_pct, dd_total_pct, estado
FROM "Trading/Challenges"
SORT fecha DESC
```

### Templater
Permite crear notas desde plantillas con variables dinamicas.
Las plantillas estan en la carpeta `templates/`.

Como crear una nota desde template:
1. Ctrl+N para nueva nota
2. Abrir Command Palette (Ctrl+P)
3. Escribir "Templater: Create new note from template"
4. Seleccionar el template deseado
5. La nota se crea con las variables `{{date:...}}` resueltas automaticamente

Variables disponibles en templates:
- `{{date:YYYY-MM-DD}}` — fecha actual
- `{{date:YYYY-[W]WW}}` — numero de semana ISO
- `{{title}}` — nombre del archivo

### Graph View
Visualiza las conexiones entre notas via `[[wikilinks]]`.
Util para ver como se relacionan agentes, skills y resultados.
No requiere configuracion — funciona con la sintaxis `[[archivo]]`.

---

## ESTRUCTURA DE CARPETAS EN OBSIDIAN

```
trading-lab/
├── dashboard.md              ← Punto de entrada diario
├── CLAUDE.md                 ← Constitucion (no editar sin consenso)
├── agents/                   ← Definicion de los 11 agentes
├── docs/
│   ├── project-status.md     ← Estado actual del proyecto
│   ├── lessons-learned.md    ← Lecciones de cada build
│   ├── skills/               ← Skills operativas del pipeline
│   ├── roadmap/              ← Planning y progreso
│   └── architecture/         ← Arquitectura del sistema
├── templates/                ← Plantillas Obsidian/Templater
├── config/                   ← Configuracion del pipeline
├── scripts/                  ← Scripts Python del sistema
└── results/                  ← Resultados de builds y evaluaciones
```

---

## CONVENCIONES DE NAMING

- Notas de challenge: `YYYY-MM-DD.md` dentro de su carpeta de challenge
- Reviews semanales: `weekly-YYYY-WNN.md`
- Reports de build: `build-[N]-report.md` en `results/`
- Lecciones: entrada nueva en `docs/lessons-learned.md`

---

## SINCRONIZACION CON GIT

Despues de trabajar en Obsidian, hacer commit de los cambios:

```bash
git add docs/ templates/ dashboard.md
git commit -m "Docs: [descripcion de lo actualizado]"
git push origin main
```

Los archivos en `config/telegram-config.json` estan en `.gitignore`
y NO se commitean. Todo lo demas es publico en el repositorio.

---

## BUSQUEDA EN EL VAULT

Para encontrar informacion en el proyecto:
- Busqueda global: Ctrl+Shift+F — busca en todos los archivos
- Quick switcher: Ctrl+O — abre archivo por nombre
- Graph view: Ctrl+G — visualiza conexiones entre notas
- Busqueda por tag: usar `#tag` en el frontmatter y buscar por tag

---

## REGLAS DE USO

1. No crear notas efimeras — solo crear si el contenido
   es relevante a largo plazo para el proyecto
2. No duplicar informacion que ya esta en otro archivo
3. Actualizar `docs/project-status.md` cuando cambie algo significativo
4. Las lecciones van en `docs/lessons-learned.md` — no en notas sueltas
5. Los criterios numericos del pipeline NO se modifican en Obsidian
   sin instruccion explicita del orchestrator
