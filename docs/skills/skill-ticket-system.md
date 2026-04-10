# Skill: Sistema de Tickets por Ciclo de Builder

## Proposito
Define como crear y gestionar tickets de seguimiento
para cada ciclo de Builder libre a lo largo del pipeline.
Resuelve el problema de perdida de contexto entre
sesiones cuando pasan dias entre una fase y la siguiente.

---

## POR QUE EXISTE EL SISTEMA DE TICKETS

Sin tickets, cuando el orchestrator retoma un
ciclo despues de varios dias no sabe:
- En que fase exacta quedo el ciclo
- Que decisiones automaticas se tomaron
- Cuantas candidatas pasaron cada puerta
- Si hay algo pendiente de ejecutar en SQ

Con tickets, el orchestrator lee el ticket y
en 30 segundos sabe exactamente donde retomar.

---

## ESTRUCTURA DE UN TICKET

Cada ciclo de Builder tiene su propia carpeta en:
research\active-tickets\[TICKET-ID]\

Contenido de la carpeta:

### build-config.md
La configuracion del Builder libre generada por
el market-analyst (configurador de busqueda).
No se modifica — es el documento de referencia.

### evaluation-log.md
Registro cronologico de todas las acciones
automaticas del pipeline sobre este ciclo.
Cada entrada incluye fecha, agente y resultado.
Se va añadiendo — nunca se borra.

### gate-decisions.md
Registro de todas las decisiones automaticas
del Evaluation Gate, paso 12b y WFO.
Formato: fecha, fase, decision, criterio numerico.
Se va añadiendo — nunca se borra.

### current-phase.txt
Una sola palabra o frase que indica la fase actual.
Valores posibles:
- preparacion
- build-pending
- build-running
- evaluation-gate
- retester-pending
- retester-running
- paso-12b
- optimizer-pending
- optimizer-running
- wfo-dictamen
- portfolio-evaluation
- export-pending
- demo-testing
- challenge-active
- approved
- rejected
- stale

---

## FORMATO DE CADA ARCHIVO

### evaluation-log.md

# Evaluation Log — BUILD-[N] [activo]

## [FECHA] — [AGENTE]
[Accion realizada y resultado]
---

## [FECHA] — [AGENTE]
[Siguiente entrada]
---

### gate-decisions.md

# Gate Decisions — BUILD-[N] [activo]

## Decision [NUMERO]
Fecha: [fecha]
Fase: [EvalGate / 12b / WFO / Portfolio]
Candidatas evaluadas: [numero]
Descartadas automaticamente: [numero]
Aprobadas automaticamente: [numero]
Criterio principal de descarte: [criterio numerico]
Decidido por: orchestrator-auto
Intervencion humana: NO
---

### current-phase.txt
build-running

---

## CICLO DE VIDA DE UN TICKET

### Creacion del ticket
Se crea cuando el market-analyst configura
un nuevo ciclo de Builder libre.
El orchestrator crea la carpeta y los archivos.

Nomenclatura: TICKET-[NNN]-BUILD-[N]-[activo]
Ejemplo: TICKET-002-BUILD-9-EURUSD

Comando para crear:
mkdir research\active-tickets\TICKET-[NNN]-BUILD-[N]-[activo]
Crear los 4 archivos en esa carpeta.
Copiar la configuracion a build-config.md.
Escribir "preparacion" en current-phase.txt.

### Actualizacion del ticket
Cada vez que un agente ejecuta una accion
añade una entrada a evaluation-log.md.
Cada vez que se toman decisiones automaticas
añade una entrada a gate-decisions.md.
Cada vez que cambia la fase
actualizar current-phase.txt.

### Cierre del ticket
Cuando todas las candidatas del ciclo han sido
procesadas (aprobadas, descartadas o en espera):
- Mover carpeta a research\active-tickets\archived\
- Cambiar current-phase.txt a "completed"
- Las estrategias aprobadas estan en results\approved\
- Las descartadas estan en results\rejected\

---

## PROTOCOLO DE INICIO DE SESION CON TICKETS

Al inicio de cada sesion el orchestrator:

Paso 1: Leer project-status.md
Paso 2: Escanear research\active-tickets\
Paso 3: Para cada ticket activo verificar:
  - Que fase indica current-phase.txt
  - Cuanto tiempo lleva en esa fase
  - Cuantas candidatas quedan pendientes

Paso 4: Clasificar tickets por estado:
  - ACTIVO: actividad reciente (< 48 horas)
  - STALE: sin actividad (> 48 horas)
  - BLOQUEADO: esperando accion en SQ

Paso 5: Informar:
  "Tickets activos: [lista con fase]
   Tickets STALE: [lista]
   Tickets bloqueados: [lista]
   Siguiente accion automatica: [accion]"

---

## ETIQUETA STALE

Un ticket se marca como STALE cuando lleva
mas de 48 horas en la misma fase sin actividad.

Posibles causas:
- Build corriendo en SQ (normal si < 72h)
- WFO corriendo en SQ (normal si < 24h)
- Se olvido continuar el pipeline
- Bloqueo tecnico no documentado

Cuando el orchestrator detecta STALE:
1. Verificar si hay un proceso corriendo en SQ
   (build o WFO que tarda mas de lo esperado)
2. Si no hay proceso → notificar al usuario
3. Añadir al evaluation-log.md:
   "[FECHA] — orchestrator
   STALE detectado. [X] horas en fase [fase].
   Causa: [build corriendo / pendiente accion SQ]"

---

## EJEMPLO DE TICKET COMPLETO

research\active-tickets\TICKET-002-BUILD-9-EURUSD\
  build-config.md      → configuracion Builder libre
  current-phase.txt    → "retester-running"
  evaluation-log.md    → entradas de data-manager,
                         market-selector, market-analyst,
                         evaluator-assistant, orchestrator
  gate-decisions.md    → decisiones automaticas del
                         Evaluation Gate con numeros

---

## INTEGRACION CON EL ORCHESTRATOR

El orchestrator referencia los tickets en cada accion:

Al configurar Builder:
"Crear TICKET-[NNN]-BUILD-[N]-[activo].
Copiar configuracion a build-config.md.
Fase: build-pending."

Al aplicar Evaluation Gate automatico:
"Leer ticket completo.
Aplicar criterios de skill-evaluation-auto.md.
Documentar decisiones en gate-decisions.md.
Actualizar current-phase.txt."

Al detectar STALE:
"TICKET-[NNN] lleva [X] horas en fase [fase].
Verificar si hay proceso activo en SQ."

---

## REGLA FUNDAMENTAL

Los tickets documentan el progreso automatico
del pipeline. No documentan decisiones humanas
porque no hay decisiones humanas en el pipeline.
Solo documentan que numeros se aplicaron y
que resultado dieron automaticamente.