# Skill: Gestion de Sesiones de Claude Code

## Proposito
Guia para el orchestrator y para los usuarios.
Define como gestionar correctamente las sesiones
de Claude Code en el sistema automatico.

---

## COMO FUNCIONA LA MEMORIA EN CLAUDE CODE

Claude Code NO recuerda conversaciones anteriores
entre sesiones distintas. Cada vez que ejecutais
claude en CMD es una sesion nueva.

Lo que SI persiste entre sesiones:
- El contenido de CLAUDE.md (carga automatica)
- Los archivos del proyecto
- El historial de Git

Lo que NO persiste entre sesiones:
- Las conversaciones anteriores
- Decisiones tomadas verbalmente sin documentar
- El contexto de lo que se estaba haciendo

Conclusion: todo lo importante debe estar en archivos.
Si no esta escrito → no existe para Claude Code.

---

## PROTOCOLO DE INICIO DE SESION

### Paso 1: Abrir desde la carpeta correcta
cd C:\Users\ivano\trading-lab
claude

(En el dispositivo de alber: cd C:\Users\alber\trading-lab)

### Paso 2: Pegar prompt de inicio
Copiar desde docs\prompts-referencia.md el
prompt estandar de inicio y pegarlo.

El orchestrator leera CLAUDE.md, project-status.md,
escaneara tickets y dara el estado del sistema
con la siguiente accion automatica.

### Paso 3: Seguir las instrucciones del orchestrator
El orchestrator indica que hacer.
No tomar decisiones propias sobre el pipeline.
Los numeros deciden.

---

## PROTOCOLO DE CIERRE DE SESION

### Paso 1: Pegar prompt de cierre
Copiar desde docs\prompts-referencia.md el
prompt estandar de cierre y pegarlo.

El orchestrator actualizara project-status.md,
tickets activos y dara el commit exacto.

### Paso 2: Ejecutar commit y push
git add .
git commit -m "[mensaje que indica el orchestrator]"
git push origin main

### Paso 3: Anotar en Obsidian (opcional)
Crear nota con fecha y siguiente paso.

---

## COMO INVOCAR AGENTES

Todos los prompts estan en docs\prompts-referencia.md.
Copiar y pegar directamente — no improvisar prompts.

Formato general:
"Actua segun agents\[nombre-agente].md.
Lee [skills relevantes].
[Tarea concreta].
Guarda resultado en [ruta exacta]."

---

## PROMPT DE INICIO RAPIDO

Lee CLAUDE.md y docs\project-status.md.
Actua segun agents\orchestrator.md.
Lee docs\skills\skill-ticket-system.md y
docs\skills\skill-evaluation-auto.md.
Dame el estado del sistema:
1. Tickets activos con fase actual
2. Portfolio: estrategias activas y objetivo
3. Cola de espera
4. Siguiente accion automatica

---

## GESTION DEL CONTEXTO EN SESIONES LARGAS

Señales de que Claude Code ha perdido contexto:
- Repite preguntas ya respondidas
- Propone acciones ya hechas
- No recuerda decisiones de la misma sesion

Como recuperar el contexto:
"Antes de continuar lee estos archivos:
- CLAUDE.md
- docs\project-status.md
- [archivos relevantes de la sesion actual]"

---

## ERRORES COMUNES Y COMO EVITARLOS

ERROR 1: Empezar sin usar el prompt de inicio
→ Siempre pegar el prompt de docs\prompts-referencia.md

ERROR 2: No hacer commit antes de cerrar
→ Commit y push obligatorio siempre

ERROR 3: Improvisar prompts en vez de usar los estandar
→ Siempre usar docs\prompts-referencia.md

ERROR 4: No guardar el output en un archivo
→ Siempre pedir guardar en ruta concreta

ERROR 5: Intentar tomar decisiones del pipeline
→ Los numeros deciden. El humano solo pulsa botones
  en SQ y hace forward test.

ERROR 6: Abrir Obsidian en vez de trading-lab
→ Verificar siempre que la carpeta correcta
  esta abierta en Antigravity