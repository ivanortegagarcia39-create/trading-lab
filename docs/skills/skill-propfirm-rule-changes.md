# Skill: Protocolo de Cambios de Reglas en Prop Firms

## Proposito
Define como detectar, evaluar y responder
cuando una prop firm cambia sus reglas.
Un cambio de reglas no detectado puede invalidar
estrategias en produccion de un dia para otro.
La respuesta debe ser automatica y numerica,
no reactiva ni emocional.

---

## Tipos de cambios y nivel de impacto

### Nivel 1 — Critico (accion inmediata)
Cambios que invalidan estrategias en produccion:
- DD cambia de estatico a trailing
- DD maximo reducido por debajo del DD historico
  de alguna estrategia activa
- Prohibicion de EAs o trading algoritmico
- Cambio en horario de trading que afecta H1
- Suspension temporal o cierre de la prop firm

Accion: pausar challenges activos ese mismo dia.
Reevaluar todas las estrategias contra nuevas reglas.

### Nivel 2 — Moderado (accion en 48h)
Cambios que afectan el scoring pero no invalidan:
- Cambio en profit split (> 5 puntos)
- Cambio en precio de challenge (> 20%)
- Cambio en objetivo de profit
- Nuevas restricciones de instrumentos
- Cambio en dias minimos de trading

Accion: recalcular scoring de prop firms afectadas.
Actualizar skill-propfirms-comparison.md.
Verificar si la prop firm principal sigue siendo
la recomendada por scoring.

### Nivel 3 — Menor (accion en proximo ciclo)
Cambios que no afectan estrategias actuales:
- Cambios en plan de scaling (no en Capa 0)
- Nuevos tipos de cuenta no usados
- Cambios en soporte o plataforma
- Actualizaciones de terminos legales menores

Accion: registrar el cambio. Actualizar documentacion
en el proximo ciclo de mantenimiento.

---

## Proceso de deteccion

### Verificacion periodica
Frecuencia minima: una vez por semana.
Fuentes a revisar en orden:
1. Pagina oficial de la prop firm (reglas/FAQ)
2. Email de comunicaciones de la prop firm
3. Foro oficial o Discord de la prop firm
4. Comunidades de trading algoritmico

El orchestrator registra la fecha de cada
verificacion en: results\propfirm-changelog.md

### Señales de alerta temprana
Prestar atencion especial si:
- La prop firm anuncia "actualizacion de terminos"
- Hay quejas masivas en comunidades de traders
- La prop firm cambia de plataforma tecnologica
- Hay noticias sobre problemas financieros
  de la prop firm

---

## Proceso de evaluacion tras deteccion

Cuando se detecta un cambio:

Paso 1 — Clasificar el nivel de impacto
Usar la tabla de tipos de cambios de arriba.
Si hay duda: asumir nivel superior (mas critico).

Paso 2 — Evaluar estrategias en produccion
Para cada estrategia activa en challenge o funded:
- DD historico OOS vs nuevo limite de DD
- Frecuencia de trades vs nuevos dias minimos
- Instrumentos usados vs nuevas restricciones
Resultado: COMPATIBLE / INCOMPATIBLE / REVISAR

Paso 3 — Evaluar estrategias aprobadas en espera
Misma evaluacion que paso 2.
Si son incompatibles: no lanzar challenge
hasta reevaluar con nuevas reglas.

Paso 4 — Recalcular scoring de prop firms
Si el cambio afecta al scoring:
Actualizar skill-propfirms-comparison.md.
Recalcular prop firm recomendada.
Si la prop firm principal pierde el primer puesto:
registrar nueva recomendacion con fecha.

Paso 5 — Registrar en changelog
Formato obligatorio:
Fecha deteccion: [fecha]
Prop firm: [nombre]
Tipo de cambio: [descripcion breve]
Nivel de impacto: 1 / 2 / 3
Estrategias afectadas: [IDs o "ninguna"]
Accion tomada: [descripcion]
Documentacion actualizada: SI/NO

---

## Protocolo de emergencia — Nivel 1

Si se detecta cambio de nivel 1:

1. Pausar inmediatamente cualquier challenge
   activo en esa prop firm.
2. Notificar al operador con resumen del cambio
   y estrategias afectadas.
3. No lanzar nuevos challenges hasta revision.
4. Evaluar si otras prop firms del portfolio
   pueden absorber las estrategias afectadas.
5. Si ninguna prop firm es viable:
   las estrategias vuelven a estado "aprobada-espera"
   hasta que el mercado de prop firms se estabilice.

El operador toma la decision final en nivel 1.
En niveles 2 y 3 el sistema actua de forma autonoma.

---

## Prop firms alternativas pre-evaluadas

Mantener siempre una lista actualizada de
al menos 3 prop firms alternativas viables
por si la principal queda invalidada.

Lista base del proyecto:
- FTMO (principal)
- E8 Funding
- The Funded Trader
- Apex Trader Funding
- My Forex Funds (verificar estado operativo)

Si una prop firm cierra o queda invalidada:
activar la siguiente de la lista por scoring.
No esperar — tener la alternativa lista antes
de que sea necesaria.

---

## Lo que esta skill NUNCA hace

NUNCA ignora un cambio de reglas porque
"probablemente no afecte a nuestras estrategias".
NUNCA continua challenges activos tras
detectar un cambio de nivel 1 sin revision.
NUNCA asume que las reglas son permanentes.
NUNCA toma decision de nivel 1 de forma
autonoma — siempre notifica al operador.

Las reglas cambian. El sistema se adapta.
Los numeros siguen decidiendo.