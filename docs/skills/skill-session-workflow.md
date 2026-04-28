# Skill: Session Workflow — Flujo Estandar de Trabajo

## Proposito
Define el protocolo de inicio, trabajo y cierre de cada sesion
en TradingLab, tanto en ivano como en alber.
Seguir este flujo garantiza sincronizacion entre dispositivos
y que no se pierde ningun estado del pipeline.

---

## INICIO DE SESION (siempre, en cualquier dispositivo)

```bash
# 1. Preparar entorno y verificar estado del sistema
python scripts/session-starter.py --device ivano   # o --device alber

# 2. Sincronizar con el repositorio remoto
git pull origin main

# 3. Revisar dashboard en Obsidian
# Abrir dashboard.md para ver estado visual del pipeline

# 4. Ver proxima accion concreta
# Revisar docs/project-status.md seccion "Siguiente Accion"
```

El `session-starter.py` ejecuta automaticamente:
- Health check del sistema
- Estado del build activo
- Numero de estrategias en results/
- Ultima entrada del audit trail
- Las 2 lecciones estructurales del proyecto
- Proxima accion segun project-status.md
- Notificacion Telegram de inicio de sesion

---

## DURANTE LA SESION

### Si hay build corriendo en alber
- Revisar progreso en SQ cada 2-4 horas
- Anotar candidatas nuevas en databank en results/build-XX-report.md
- No apagar alber ni interrumpir SQ sin anotar el estado

### Tareas largas con Claude Code
- Crear el archivo `prompts/next-tasks.md` con las tareas
- Ejecutar: leer el archivo y ejecutar todas las tareas
- Verificar resultado con tabla de archivos creados/modificados

### Commits durante la sesion
- Commitear al final de cada bloque de trabajo completado
- No acumular mas de 2-3 horas sin commitear
- Mensaje descriptivo: que se hizo y por que

```bash
git add scripts/nuevo-script.py docs/skills/nueva-skill.md
git commit -m "Scripts: descripcion. Skills: descripcion"
git push origin main
```

### Archivos a NUNCA editar sin sincronizar
- CLAUDE.md — solo modificar con consenso explicito
- config/pipeline-config.json — solo modificar con instruccion del orchestrator
- docs/skills/skill-evaluation-auto.md — criterios numericos del pipeline
- docs/roadmap/planning-maestro-status.md — fuente de verdad del progreso

---

## FIN DE SESION (siempre, en cualquier dispositivo)

```bash
# 1. Commit final de todo el trabajo de la sesion
git add .
git commit -m "descripcion breve de lo trabajado"
git push origin main

# 2. Notificar cierre de sesion
python scripts/telegram-notifier.py --level INFO --message "Sesion cerrada en [dispositivo]. Commits: X"

# 3. Si hay build corriendo en alber
# Anotar estado actual en results/build-XX-report.md:
# - Tiempo corriendo
# - Candidatas en databank
# - PF maximo observado
```

---

## REGLAS DE TRABAJO EN PARALELO (ivano + alber)

### Siempre antes de empezar
```bash
git pull origin main
```
En cualquier dispositivo, sin excepcion.

### Division de roles

| Dispositivo | Uso principal |
|-------------|---------------|
| alber | SQ Builder libre, Retester, Optimizer, git pull/push de resultados |
| ivano | Documentacion, Claude Code, scripts Python, git push de codigo |

### Lo que NO se hace
- Editar el mismo archivo en ambos dispositivos sin hacer git push/pull entre medio
- Modificar config/ en alber sin commitear y hacer pull en ivano
- Trabajar en ivano mientras alber tiene cambios sin commitear

### Resolucion de conflictos
Si git pull falla por conflicto:
1. Abrir el archivo en conflicto
2. Resolver manualmente manteniendo la version mas reciente
3. `git add archivo` + `git commit -m "Merge: resolver conflicto en archivo"`
4. `git push origin main`

---

## CHECKLIST DE SESION — MODO RAPIDO

### Al inicio (5 minutos)
- [ ] `python scripts/session-starter.py --device [dispositivo]`
- [ ] `git pull origin main`
- [ ] Revisar dashboard.md
- [ ] Identificar proxima accion

### Durante (cada bloque)
- [ ] Trabajar en una tarea concreta
- [ ] Commitear al terminar
- [ ] Push si el trabajo esta completo

### Al cierre (5 minutos)
- [ ] `git add . && git commit -m "..." && git push`
- [ ] Notificar Telegram cierre
- [ ] Anotar estado build si aplica

---

## USO DEL ARCHIVO prompts/next-tasks.md

Para sesiones de trabajo con Claude Code que involucran
multiples archivos o tareas complejas:

1. Crear `prompts/next-tasks.md` con el siguiente formato:
```
Lee CLAUDE.md y todos los archivos en agents/ y docs/skills/.

Continuamos desde [dispositivo]. Crea los siguientes archivos.

TAREA 1 - [Descripcion]
[Instrucciones detalladas]

TAREA 2 - [Descripcion]
[Instrucciones detalladas]

Al terminar:
git add .
git commit -m "mensaje"
git push origin main
Confirma con tabla de archivos creados.
```

2. En Claude Code: "Lee el archivo prompts/next-tasks.md y ejecuta todas las tareas"
3. Verificar tabla de confirmacion al final

Ventaja: Claude Code lee el contexto completo del proyecto
antes de ejecutar cada tarea, garantizando coherencia.

---

## VERIFICACION RAPIDA DEL SISTEMA

```bash
# Health check completo
python scripts/system-health-check.py

# Health check con auto-correccion de problemas menores
python scripts/system-health-check.py --fix

# Estado del portfolio
python scripts/portfolio-monitor.py --mode report

# Verificar DD actual (si hay challenge activo)
python scripts/ftmo-dd-calculator.py --trades-csv trades.csv --mode verify
```
