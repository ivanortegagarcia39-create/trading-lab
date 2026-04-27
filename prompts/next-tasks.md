Lee CLAUDE.md y todos los archivos en agents/ y docs/skills/.

Continuamos desde ivano. Crea los siguientes archivos.

TAREA 1 - Crear templates/challenge-daily-log.md
Plantilla Obsidian para registro diario de un challenge FTMO:
Frontmatter: fecha, challenge_id, prop_firm, capital, dia_numero, balance_inicio_dia, balance_actual, profit_acumulado_pct, dd_diario_pct, dd_total_pct, trades_hoy, estado (VERDE/AMARILLO/ROJO)
Secciones: Métricas del Día, Trades Ejecutados (tabla), Semáforo de Estado, Notas, Próximos Pasos.
Incluir fórmulas para calcular automáticamente el progreso hacia el objetivo.

TAREA 2 - Crear templates/weekly-pipeline-review.md
Plantilla para revisión semanal del pipeline completo:
Frontmatter: semana, builds_activos, estrategias_databank, estrategias_en_evaluacion, estrategias_aprobadas, portfolio_size, accounts_active
Secciones: Estado del Pipeline, Builds Esta Semana, Estrategias en Proceso, Portfolio Actual, Alertas de la Semana, Ajustes de Criterios Propuestos, Próxima Semana.

TAREA 3 - Actualizar dashboard.md
Lee el dashboard actual. Añade al final una nueva sección:
## 📋 Archivos de Configuración
| Archivo | Propósito |
|---------|-----------|
| config/build-defaults.json | Spreads, slippage, swaps por activo |
| config/pipeline-config.json | Umbrales numéricos de todas las puertas |
| config/telegram-config.json | Credenciales Telegram (no en git) |

## 🗓️ Templates Disponibles
| Template | Uso |
|----------|-----|
| templates/build-report.md | Resultado de cada build SQ |
| templates/strategy-evaluation.md | Evaluación individual de estrategia |
| templates/daily-review.md | Revisión semanal del sistema |
| templates/challenge-daily-log.md | Log diario de challenge FTMO |
| templates/weekly-pipeline-review.md | Revisión semanal del pipeline |

TAREA 4 - Crear docs/skills/skill-obsidian-workflow.md
Documenta cómo usar Obsidian en el proyecto TradingLab:
Propósito: Obsidian ES el vault del repo trading-lab. Todo lo que se escribe aquí se sincroniza con git.
Flujo diario: abrir dashboard.md para ver estado, crear log diario con template challenge-daily-log si hay challenge activo, revisar lessons-learned después de cada build.
Flujo semanal: crear weekly-pipeline-review con template, revisar planning-maestro-status, actualizar project-status.md.
Plugins instalados y su uso: Dataview (queries automáticas en dashboard), Templater (crear notas desde templates).
Cómo crear una nota desde template: Ctrl+N, seleccionar template, rellenar frontmatter.
Regla importante: los archivos .md creados en Obsidian se commitean con git como cualquier otro archivo del proyecto.

TAREA 5 - Actualizar docs/roadmap/planning-maestro-status.md
Lee el archivo actual. Actualiza con las tareas completadas hoy:
- scripts/ftmo-dd-calculator.py creado
- scripts/strategy-analyzer.py creado
- scripts/portfolio-monitor.py creado
- scripts/telegram-notifier.py creado
- docs/skills/skill-challenge-tracker.md creado
- config/pipeline-config.json creado
- docs/skills/skill-mql5-coding.md creado
- docs/skills/skill-vps-setup.md creado
- docs/skills/skill-telegram-setup.md creado
- templates/challenge-daily-log.md creado
- templates/weekly-pipeline-review.md creado
Actualizar el total y porcentaje de completitud.

Al terminar:
git add .
git commit -m "Templates challenge y pipeline review. Obsidian workflow. Dashboard config section. Planning status final"
git push origin main
Confirma con tabla de archivos creados.