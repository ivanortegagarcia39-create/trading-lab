# Skill: Sistema de Tickets por Hipotesis

## Proposito
Define como crear y gestionar tickets de seguimiento
para cada hipotesis a lo largo del pipeline.
Resuelve el problema de perdida de contexto entre
sesiones cuando pasan dias entre una fase y la siguiente.

---

## POR QUE EXISTE EL SISTEMA DE TICKETS

Sin tickets, cuando el orchestrator retoma una
hipotesis despues de varios dias no sabe:
- En que fase exacta quedo la hipotesis
- Que decisiones se tomaron y por que
- Que observaciones hicieron los agentes
- Si habia algo pendiente de revisar

Con tickets, el orchestrator lee el ticket y
en 30 segundos sabe exactamente donde retomar.

---

## ESTRUCTURA DE UN TICKET

Cada hipotesis tiene su propia carpeta en:
research\active-tickets\[TICKET-ID]-[nombre]\

Contenido de la carpeta:

### hypothesis.md
La hipotesis original generada por market-analyst.
No se modifica — es el documento de referencia.

### evaluation-log.md
Registro cronologico de todas las opiniones
y observaciones de los agentes sobre esta hipotesis.
Cada entrada incluye fecha, agente y contenido.
Se va añadiendo — nunca se borra.

### gate-decisions.md
Registro de todas las decisiones del Evaluation Gate.
Formato: fecha, fase, decision, razon, quien decidio.
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
- optimizer-pending
- optimizer-running
- approved
- rejected
- stale

---

## FORMATO DE CADA ARCHIVO

### evaluation-log.md

# Evaluation Log — [nombre hipotesis]

## [FECHA] — [AGENTE]
[Observacion o analisis del agente]
---

## [FECHA] — [AGENTE]
[Siguiente entrada]
---

### gate-decisions.md

# Gate Decisions — [nombre hipotesis]

## Decision [NUMERO]
Fecha: [fecha]
Fase: [Builder / Retester / Optimizer / Aprobacion]
Decision: [PASA / REVISAR / SIMPLIFICAR / DESCARTAR]
Razon: [explicacion]
Decidido por: [humano / orchestrator-auto]
Siguiente accion: [que pasa ahora]
---

### current-phase.txt
build-running

---

## CICLO DE VIDA DE UN TICKET

### Creacion del ticket
Se crea cuando market-analyst genera una hipotesis.
El orchestrator crea la carpeta y los archivos vacios.

Comando para crear ticket nuevo:
mkdir research\active-tickets\TICKET-001-[nombre]
Crear los 4 archivos en esa carpeta.
Copiar la hipotesis a hypothesis.md.
Escribir "preparacion" en current-phase.txt.

### Actualizacion del ticket
Cada vez que un agente analiza la hipotesis
añade una entrada a evaluation-log.md.
Cada vez que se toma una decision de gate
añade una entrada a gate-decisions.md.
Cada vez que cambia la fase
actualizar current-phase.txt.

### Cierre del ticket
Si la hipotesis es APROBADA:
- Mover carpeta a research\active-tickets\archived\
- Cambiar current-phase.txt a "approved"
- El archivo de estrategia va a results\approved\

Si la hipotesis es DESCARTADA:
- Mover carpeta a research\active-tickets\archived\
- Cambiar current-phase.txt a "rejected"
- Documentar la razon en gate-decisions.md

---

## PROTOCOLO DE INICIO DE SESION CON TICKETS

Al inicio de cada sesion de Claude Code el
orchestrator debe ejecutar este protocolo:

Paso 1: Leer project-status.md
Paso 2: Escanear research\active-tickets\
Paso 3: Para cada ticket activo verificar:
  - Que fase indica current-phase.txt
  - Cuanto tiempo lleva en esa fase
  - Si hay algo pendiente segun gate-decisions.md

Paso 4: Clasificar tickets por estado:
  - ACTIVO: tiene actividad reciente (< 48 horas)
  - STALE: sin actividad en mas de 48 horas
  - BLOQUEADO: esperando accion humana

Paso 5: Informar al usuario:
  "Tickets activos: [lista]
   Tickets STALE: [lista] — requieren confirmacion
   Tickets bloqueados: [lista] — esperan tu accion"

---

## ETIQUETA STALE

Un ticket se marca como STALE cuando lleva
mas de 48 horas en la misma fase sin actividad.

Esto puede significar:
- El build esta corriendo (normal)
- Se olvido retomar la hipotesis
- Hay un bloqueo no documentado

Cuando el orchestrator detecta un ticket STALE:
1. Notificar al usuario con el tiempo transcurrido
2. Preguntar si continuar, pausar o descartar
3. NO continuar automaticamente sin confirmacion

Añadir al evaluation-log.md:
## [FECHA] — orchestrator
STALE detectado. [X] horas sin actividad en fase [fase].
Esperando confirmacion humana para continuar.

---

## NOMENCLATURA DE TICKETS

Formato: TICKET-[NNN]-[nombre-hipotesis]
Ejemplo: TICKET-001-NBARBreakout-H1-EURUSD

El numero es secuencial — TICKET-001, TICKET-002, etc.
El nombre es el mismo que el archivo de hipotesis.

---

## EJEMPLO DE TICKET COMPLETO

research\active-tickets\TICKET-001-NBARBreakout-H1\
  hypothesis.md          → copia de la hipotesis original
  current-phase.txt      → "build-running"
  evaluation-log.md      → entradas de market-analyst,
                           funding-specialist, sq-specialist
  gate-decisions.md      → decision PASA del Evaluation Gate
                           si ya se aplico

---

## INTEGRACION CON EL ORCHESTRATOR

El orchestrator debe referenciar los tickets
en cada decision que tome:

Al invocar market-analyst:
"Genera hipotesis y cuando este lista
el orchestrator creara el TICKET correspondiente."

Al aplicar Evaluation Gate:
"Lee el ticket TICKET-[NNN] completo antes
de tomar la decision. Añade la decision a
gate-decisions.md y actualiza current-phase.txt."

Al detectar STALE:
"El TICKET-[NNN] lleva [X] horas en fase [fase].
Notificar al usuario y esperar confirmacion."