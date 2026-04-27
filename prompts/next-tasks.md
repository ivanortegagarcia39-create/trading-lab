Lee CLAUDE.md y todos los archivos en agents/ y docs/skills/.

Continuamos desde ivano. Crea los siguientes archivos.

TAREA 1 - Crear scripts/system-health-check.py
Script que verifica el estado completo del sistema TradingLab en un solo comando. Útil para ejecutar al inicio de cada sesión de trabajo.

Verificaciones que realiza:
1. Python y dependencias: verificar que pandas, numpy, pytz, chromadb, requests están instalados
2. Estructura del repo: verificar que existen las carpetas agents/, docs/skills/, scripts/, config/, results/, templates/
3. Archivos críticos: verificar que existen CLAUDE.md, config/pipeline-config.json, config/build-defaults.json
4. Telegram: verificar que existe config/telegram-config.json y que el bot responde (test ping)
5. ChromaDB: verificar que .chromadb/ existe y tiene datos indexados
6. Pipeline lock: verificar que no hay results/pipeline.lock activo
7. Git status: verificar que el repo está sincronizado con origin/main
8. Scripts: verificar que todos los scripts en scripts/ son importables sin error

Output: tabla de estado con OK/WARN/FAIL por cada verificación
Resultado final: SISTEMA LISTO / ADVERTENCIAS / SISTEMA CON ERRORES
Guardar en results/system-health.json
Argumento: --fix (intenta corregir problemas menores automáticamente)

TAREA 2 - Crear scripts/session-starter.py
Script que se ejecuta al inicio de cada sesión de trabajo para preparar el entorno.

Acciones que realiza:
1. Ejecutar system-health-check.py automáticamente
2. Mostrar estado del Build activo (si hay results/pipeline.lock)
3. Mostrar número de estrategias en results/ (Strategy*.csv)
4. Mostrar última entrada del audit trail (hash-logger)
5. Mostrar las 2 lecciones estructurales del proyecto
6. Recordar la próxima acción según docs/project-status.md
7. Enviar notificación Telegram: "Sesión iniciada en [dispositivo]. Sistema: [estado]"
8. Crear entrada en results/session-log.json con timestamp de inicio

Argumento: --device (ivano o alber, default: auto-detectar por hostname)

TAREA 3 - Actualizar docs/project-status.md
Actualizar con estado real actual:
- Fecha: 2026-04-27
- Build activo: Build 10 completado (4+ días). Build 11 pendiente de lanzar en alber con spread 60 pips.
- Scripts Python: todos operativos y probados en ivano
- Telegram bot: activo (@tradinglab_monitor_bot)
- ChromaDB: indexado con 90 chunks
- Planning maestro: ~145/156 tareas completadas
- Próxima acción: lanzar Build 11 en alber con spread corregido a 60 pips

TAREA 4 - Actualizar dashboard.md
Añadir sección al final:

## ✅ Estado de Scripts Python
Todos los scripts probados y operativos en ivano (2026-04-27):
| Script | Estado | Dependencias |
|--------|--------|-------------|
| pre-build-checklist.py | ✅ OK | pandas, pytz |
| evaluator-assistant.py | ✅ OK | pandas |
| portfolio-builder.py | ✅ OK | pandas, numpy |
| pipeline-runner.py | ✅ OK | pandas |
| build-analyzer.py | ✅ OK | pandas |
| hash-logger.py | ✅ OK | hashlib |
| strategy-versioning.py | ✅ OK | json |
| knowledge-base.py | ✅ OK | chromadb |
| telegram-notifier.py | ✅ OK | requests |
| lessons-analyzer.py | ✅ OK | re |
| hrp-portfolio.py | ✅ OK | numpy |
| strategy-fingerprint.py | ✅ OK | xml, hashlib |
| inflation-diagnostic.py | ✅ OK | pandas |
| coordination-detector.py | ✅ OK | json |
| sqx-build-config.py | ✅ OK | json, pytz |
| market-regime-snapshot.py | ✅ OK | pandas, numpy |
| validate-sqx-folder.py | ✅ OK | pandas |
| mql5-auditor.py | ✅ OK | re |
| sq-watchdog.py | ✅ OK | subprocess |
| vps-health-monitor.py | ✅ OK | subprocess |
| ftmo-dd-calculator.py | ✅ OK | pandas, pytz |
| strategy-analyzer.py | ✅ OK | pandas |
| portfolio-monitor.py | ✅ OK | pandas |

## 🤖 Telegram Bot
- Bot: @tradinglab_monitor_bot
- Estado: ✅ Activo
- Notificaciones: INFO / WARNING / CRITICAL

TAREA 5 - Crear docs/skills/skill-session-workflow.md
Documenta el flujo de trabajo estándar de cada sesión:

INICIO DE SESIÓN (siempre):
1. python scripts/session-starter.py --device ivano (o alber)
2. git pull origin main
3. Revisar dashboard.md en Obsidian
4. Ver próxima acción en project-status.md

DURANTE LA SESIÓN:
- Si hay build corriendo en alber: revisar progreso en SQ cada 2-4 horas
- Usar prompts/next-tasks.md para tareas largas de Claude Code
- Commitear al final de cada bloque de trabajo completado
- No cerrar sin commitear

FIN DE SESIÓN (siempre):
1. git add . && git commit -m "descripción" && git push
2. python scripts/telegram-notifier.py --level INFO --message "Sesión cerrada. Commits: X"
3. Si hay build corriendo: anotar estado en results/build-10-report.md

REGLAS DE TRABAJO EN PARALELO (ivano + alber):
- Siempre git pull antes de empezar en cualquier dispositivo
- Nunca editar el mismo archivo en los dos dispositivos sin sincronizar
- alber: solo SQ, scripts de análisis y git pull/push
- ivano: documentación, Claude Code, scripts Python y git

Al terminar:
git add .
git commit -m "Scripts: system-health-check, session-starter. Docs: project-status actualizado, dashboard scripts, session-workflow"
git push origin main
Confirma con tabla de archivos creados.