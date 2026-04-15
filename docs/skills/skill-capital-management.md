# Skill: Gestion de Capital del Proyecto

## Proposito
Define los criterios numericos para gestionar
el presupuesto de challenges, limitar perdidas
operativas y tomar decisiones de inversion
de forma automatica y sin sesgo emocional.
El capital es un recurso finito — los numeros
deciden cuando gastar, cuando parar y cuando escalar.

---

## Presupuesto base del proyecto

Presupuesto inicial asignado a challenges: definido
por el operador antes de iniciar Capa 0.
Se registra en: config\project-config.md

Estructura recomendada de asignacion:
- 60% challenges activos (en curso o planificados)
- 30% reserva de reintento (fallos esperados)
- 10% reserva de emergencia (no tocar)

Ejemplo con 600 EUR:
- 360 EUR challenges activos
- 180 EUR reintentos
- 60 EUR reserva

---

## Limites automaticos de gasto

### Limite por activo
Maximo 2 challenges fallidos consecutivos
en el mismo activo antes de pausar ese activo.
Accion automatica: mover activo a lista de
espera y priorizar siguiente activo en cola.

### Limite por ciclo de build
Un ciclo de build (un activo, un periodo)
no puede consumir mas de 20% del presupuesto
total en challenges.
Si se supera: pausar challenges de ese activo
hasta el siguiente ciclo de evaluacion.

### Limite global de drawdown financiero
Si el gasto acumulado en challenges fallidos
supera el 50% del presupuesto inicial:
PARAR. Revisar pipeline antes de continuar.
Este es un stop de emergencia del proyecto.

---

## Criterios de decision de tamaño de cuenta

Usar estos criterios en orden:

Paso 1 — Evaluar el WFE de la estrategia:
- WFE >= 70%: considerar cuenta 25k
- WFE 50-69%: empezar con cuenta 10k
- WFE < 50%: no llega a este punto (descartada)

Paso 2 — Evaluar el DD maximo historico OOS:
- DD OOS <= 4%: margen suficiente para 25k
- DD OOS 4-6%: usar 10k, mas margen de seguridad
- DD OOS > 6%: no llega (descartada en Paso 12b)

Paso 3 — Evaluar presupuesto disponible:
- Si presupuesto disponible < precio challenge: esperar
- Si hay 2+ estrategias aprobadas simultaneamente:
  priorizar la de mayor score de portfolio

Decision final: cuenta 10k o 25k segun pasos 1-3.
Nunca cuentas de 50k+ en Capa 0.

---

## Seguimiento de gasto

Registro obligatorio en: results\capital-log.md

Formato por entrada:
Fecha: [fecha]
Estrategia: [ID]
Prop firm: [nombre]
Tamaño cuenta: [10k/25k]
Precio challenge: [EUR]
Resultado: PASSED / FAILED
Gasto acumulado: [EUR]
Presupuesto restante: [EUR]
Alerta activa: SI/NO — [motivo si SI]

El orchestrator actualiza este archivo
despues de cada challenge completado.

---

## Alertas automaticas

El orchestrator emite alerta cuando:
- Gasto acumulado supera 30% del presupuesto
  (alerta temprana — no parar, solo avisar)
- Gasto acumulado supera 50% del presupuesto
  (stop de emergencia — parar challenges)
- 2 challenges fallidos consecutivos en mismo activo
  (pausar activo automaticamente)
- Presupuesto de reintentos agotado
  (escalar a reserva de emergencia solo con
  aprobacion explicita del operador)

---

## Lo que esta skill NUNCA hace

NUNCA decide gastar mas porque "la estrategia
parece muy buena" — los limites son fijos.
NUNCA ignora un stop de emergencia.
NUNCA escala a cuentas grandes sin pasar
los criterios numericos de los 3 pasos.
NUNCA usa la reserva de emergencia de forma
automatica — requiere decision humana explicita.

Los numeros deciden. El presupuesto es el limite.