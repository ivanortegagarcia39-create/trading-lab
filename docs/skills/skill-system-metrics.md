# Skill: Metricas del Sistema y Pipeline

## Proposito
Define como medir el rendimiento del pipeline
de forma cuantitativa a lo largo del tiempo.
Sin metricas no hay forma de saber si el sistema
mejora, empeora o tiene un cuello de botella.
Los numeros del pipeline son tan importantes
como los numeros de las estrategias.

---

## Metricas por puerta del pipeline

Registrar despues de cada ciclo de build completo.

### Puerta 1 — EvalGate
Candidatas generadas por Builder libre: [N]
Candidatas que pasan EvalGate: [N]
Tasa de aprobacion EvalGate: [%]

Referencia saludable: 5-15%
Si < 5%: Builder libre demasiado restrictivo
  o datos historicos insuficientes.
Si > 30%: criterios EvalGate demasiado laxos,
  revisar umbrales.

### Puerta 2 — Paso 12b (Retester OOS)
Candidatas que entran: [N]
Candidatas que pasan 12b: [N]
Tasa de aprobacion 12b: [%]

Referencia saludable: 40-70%
Si < 40%: posible sobreajuste en IS.
  Revisar longitud IS en Builder libre.
Si > 80%: OOS demasiado corto o criterios laxos.

### Puerta 3 — WFO
Candidatas que entran: [N]
Candidatas que pasan WFO: [N]
Tasa de aprobacion WFO: [%]

Referencia saludable: 30-60%
Si < 30%: estrategias no robustas en tiempo.
  Revisar configuracion WFO (ventanas, paso).
Si > 70%: WFO demasiado permisivo.

### Puerta 4 — Portfolio
Candidatas que entran: [N]
Candidatas aceptadas en portfolio: [N]
Candidatas rechazadas por correlacion: [N]
Candidatas rechazadas por score: [N]

---

## Metricas globales del proyecto

Registrar en: results\pipeline-metrics.md

### Por ciclo de build
Ciclo: [numero]
Activo: [simbolo]
Fecha inicio: [fecha]
Fecha fin: [fecha]
Duracion build: [horas]
Candidatas EvalGate: [N]
Candidatas 12b: [N]
Candidatas WFO: [N]
Aceptadas portfolio: [N]
Tasa global IS->Portfolio: [%]

### Acumulado del proyecto
Total ciclos completados: [N]
Total estrategias en portfolio: [N]
Tasa media de aprobacion global: [%]
Activo con mayor tasa de aprobacion: [simbolo]
Activo con menor tasa de aprobacion: [simbolo]
Ciclo mas productivo: [numero] — [N] estrategias

---

## Tendencias a vigilar

El orchestrator calcula estas tendencias
cada 3 ciclos completados:

### Tendencia de aprobacion
Comparar tasa global de los ultimos 3 ciclos
vs los 3 anteriores.
Si cae mas de 10 puntos porcentuales: alerta.
Posibles causas: overfitting acumulado,
datos historicos degradados, criterios mal
calibrados.

### Tendencia de duracion de build
Si los builds tardan mas de lo esperado
de forma consistente: revisar configuracion
de SQ (poblacion, generaciones, recursos).

### Cuello de botella del pipeline
La puerta con menor tasa de aprobacion
es el cuello de botella actual.
No ajustar criterios para mejorar el numero
— investigar la causa raiz.

---

## Dashboard de metricas

Archivo de resumen: results\metrics-dashboard.md
Actualizar al final de cada ciclo.

Formato:
========================================
TRADINGLAB — DASHBOARD DE METRICAS
Actualizado: [fecha]
========================================
Ciclos completados: [N]
Estrategias en portfolio: [N] / objetivo 3-5
Presupuesto challenges gastado: [EUR]
Challenges passed: [N]
Challenges failed: [N]

TASAS DE APROBACION (ultimo ciclo):
EvalGate:  [%]  | referencia 5-15%
Paso 12b:  [%]  | referencia 40-70%
WFO:       [%]  | referencia 30-60%
Portfolio: [%]  | acumulado

ALERTAS ACTIVAS: [N]
[lista de alertas si las hay]
========================================

---

## Lo que esta skill NUNCA hace

NUNCA ajusta criterios de aprobacion para
mejorar las metricas artificialmente.
NUNCA ignora una tendencia negativa sostenida.
NUNCA compara tasas entre activos distintos
sin controlar el periodo de datos.

Las metricas describen la realidad.
No se manipulan para que parezca mejor.