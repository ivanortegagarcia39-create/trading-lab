# Skill: Escalado de Cuentas y Estrategias

## Proposito
Define los criterios numericos para decidir
cuando y como escalar una estrategia a cuentas
mas grandes o a multiples prop firms.
Escalar demasiado rapido destruye el capital.
Escalar demasiado lento limita el crecimiento.
Los numeros deciden el momento exacto.

---

## Estados de una estrategia

Una estrategia pasa por estos estados en orden:
APROBADA → CHALLENGE → FUNDED → SCALING → CONSOLIDADA

### APROBADA
Ha pasado EvalGate + 12b + WFO + Portfolio.
Pendiente de lanzar challenge.

### CHALLENGE
Challenge activo en curso en prop firm.
No se lanza challenge en segunda prop firm
hasta que el primero este resuelto.

### FUNDED
Challenge passed. Cuenta financiada activa.
Periodo de observacion minimo: 4 semanas.
Durante este periodo: no escalar, solo monitorear.

### SCALING
Ha cumplido criterios de escalado (ver abajo).
Se puede lanzar en cuenta mayor o segunda prop firm.

### CONSOLIDADA
3+ meses en produccion con resultados consistentes.
Candidata a Capa 1 del roadmap.

---

## Criterios de escalado — de 10k a 25k

Para pasar de cuenta 10k a cuenta 25k
en la misma prop firm, todos estos criterios
deben cumplirse simultaneamente:

Criterio 1 — Tiempo minimo en produccion
Minimo 8 semanas desde que la cuenta fue funded.
No hay excepcion a este criterio.

Criterio 2 — Drawdown en produccion
DD maximo registrado en las 8 semanas: <= 4%
Si el DD llego a 4-6%: esperar 4 semanas mas
y reevaluar.
Si el DD supero 6%: no escalar. Revisar estrategia.

Criterio 3 — Profit factor en produccion
PF de las 8 semanas en produccion: >= 1.4
Calculado con comisiones reales incluidas.
Si PF esta entre 1.2-1.4: esperar 4 semanas mas.
Si PF < 1.2: no escalar. Revisar estrategia.

Criterio 4 — Consistencia de resultados
Semanas con resultado positivo: >= 6 de 8
No puede haber 2 semanas negativas consecutivas.
Si hay 2 semanas negativas consecutivas:
reiniciar contador de 8 semanas desde ese punto.

Criterio 5 — Presupuesto disponible
El precio del challenge 25k debe estar disponible
en el presupuesto activo (no en reserva).
No usar reserva de emergencia para escalar.

Decision: si los 5 criterios se cumplen → ESCALAR
Si falla cualquier criterio → ESPERAR y reevaluar
en 4 semanas.

---

## Criterios de escalado — segunda prop firm

Para lanzar la misma estrategia en una segunda
prop firm (diversificacion), todos estos criterios
deben cumplirse:

Criterio 1 — Tiempo minimo en produccion
Minimo 12 semanas desde funded en primera prop firm.

Criterio 2 — Resultados en primera prop firm
Los mismos criterios 2, 3 y 4 del escalado 10k→25k
pero evaluados en 12 semanas completas.

Criterio 3 — Portfolio no saturado
El portfolio tiene espacio para la estrategia
en la segunda prop firm sin violar:
- Correlacion < 0.5 con otras estrategias activas
- DD combinado del portfolio < 12%

Criterio 4 — Segunda prop firm pre-evaluada
La segunda prop firm debe tener score >= 70
en skill-propfirms-comparison.md.
No lanzar en prop firm no evaluada previamente.

Criterio 5 — Presupuesto disponible
Mismo criterio que en escalado 10k→25k.

---

## Criterios de NO escalado — señales de stop

Parar el escalado y revisar la estrategia si:

Señal 1 — DD en produccion > 6%
Aunque todos los demas criterios se cumplan.
Accion: pausar nuevos challenges de esta estrategia.
Revisar si las condiciones de mercado han cambiado.

Señal 2 — 3 semanas negativas en las ultimas 6
La estrategia esta perdiendo consistencia.
Accion: no escalar. Monitorear 4 semanas mas.
Si continua: retirar del portfolio activo.

Señal 3 — PF en produccion cae por debajo de 1.0
durante 2 semanas consecutivas
La estrategia puede estar degradandose.
Accion: pausar. Evaluar si el mercado cambio
de regimen y la estrategia ya no es valida.

Señal 4 — Cambio de reglas en prop firm
Ver skill-propfirm-rule-changes.md.
No escalar durante revision de cambio de reglas.

---

## Proceso de decision de escalado

El performance-monitor ejecuta este proceso
automaticamente cada 4 semanas por estrategia:

Paso 1 — Verificar estado actual
¿La estrategia esta en estado FUNDED?
¿Han pasado al menos 8 semanas?
Si no: no continuar. Registrar fecha de proxima
evaluacion.

Paso 2 — Evaluar criterios numericos
Calcular DD maximo, PF, semanas positivas
del periodo de produccion.
Comparar contra umbrales definidos arriba.

Paso 3 — Verificar presupuesto y portfolio
Confirmar presupuesto disponible.
Recalcular correlaciones y DD combinado
si se añade esta estrategia al escalado.

Paso 4 — Emitir decision automatica
ESCALAR: todos los criterios cumplidos.
ESPERAR: uno o mas criterios no cumplidos,
  con fecha de proxima evaluacion en 4 semanas.
REVISAR: alguna señal de stop activa.
RETIRAR: degradacion confirmada.

Paso 5 — Registrar en scaling-log.md
Formato:
Fecha: [fecha]
Estrategia: [ID]
Estado actual: [FUNDED/SCALING/CONSOLIDADA]
Semanas en produccion: [N]
DD maximo produccion: [%]
PF produccion: [valor]
Semanas positivas: [N]/[total]
Decision: ESCALAR / ESPERAR / REVISAR / RETIRAR
Proxima evaluacion: [fecha]
Accion tomada: [descripcion]

---

## Criterios de retiro de una estrategia

Una estrategia se retira del portfolio activo si:

Retiro automatico:
- PF en produccion < 1.0 durante 4 semanas
  consecutivas
- DD en produccion supera el 80% del limite
  de la prop firm en cualquier momento
- La prop firm la descalifica por cualquier motivo

Retiro por revision humana:
- Cambio de regimen de mercado confirmado
  (mercado estructuralmente diferente al periodo IS)
- Correlacion con otras estrategias del portfolio
  sube por encima de 0.7 de forma sostenida

Al retirar una estrategia: libera su slot en
el portfolio. El correlation-analyst evalua
automaticamente si hay una estrategia aprobada
en espera que pueda ocupar el slot.

---

## KELLY FRACCIONADO PARA SIZING

Formula: f = (p*b - q) / b
donde p = win rate, b = ratio TP/SL, q = 1-p
Kelly fraccionado: usar 25% del Kelly completo
para reducir volatilidad de la cuenta.

Ejemplo con PF=1.5, WR=45%, ratio 2:1:
Kelly = (0.45*2 - 0.55) / 2 = 0.175 = 17.5%
Kelly fraccionado = 17.5% * 0.25 = 4.4%
Pero limitado por reglas FTMO: maximo 1% por trade
→ Usar el minimo entre Kelly fraccionado y 1%

---

## CRITERIOS DE RETIRO POR DECAY

Una estrategia se retira del portfolio cuando:
- PF produccion < 85% PF OOS durante 4 semanas
- Z-Score PF <= -2.0 durante 4 semanas
- DD produccion supera DD OOS + 30%
- Correlacion con otra estrategia > 0.7 durante
  2 semanas (una de las dos se retira)

Al retirar: registrar en lessons-learned.md
con contexto completo del fallo.

---

## PLAN DE SCALING FTMO

Mes 1-4: cuenta 10k, riesgo 1% por trade
Si profit >= 5% en 4 meses → solicitar scaling
Mes 5-8: cuenta 12.5k (+25%)
Mes 9-12: cuenta 15.6k (+25%)
Ano 2: cuenta potencial 25k-50k
Ano 4: cuenta potencial hasta 200k+

El scaling-manager gestiona esto automaticamente.

Criterio de scaling automatico FTMO:
- Profit acumulado >= 5% en periodo de 4 meses
- Sin violacion de DD durante el periodo
- Solicitar scaling en la plataforma FTMO

---

## Lo que esta skill NUNCA hace

NUNCA escala por momentum o porque la estrategia
"va muy bien esta semana".
NUNCA ignora una señal de stop aunque los
otros criterios sean positivos.
NUNCA escala si el presupuesto requiere usar
la reserva de emergencia.
NUNCA retira una estrategia por una semana
mala aislada — los patrones deciden.

El tiempo y los numeros deciden cuando escalar.
La paciencia es parte del sistema.