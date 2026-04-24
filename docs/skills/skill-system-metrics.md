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

## Meta-Monitor de Tasa de Aprobacion

El sistema registra cuantas estrategias pasan
cada puerta del pipeline por semana y detecta
cuando el pipeline se esta atascando.

### Calculo semanal
Al final de cada semana el orchestrator registra:
  estrategias_aprobadas_semana = total que llegan a Portfolio filter
  tasa_semanal = estrategias_aprobadas_semana / semana_numero

### Umbral de alerta
Si tasa_semanal < 0.5 estrategias/semana durante
2 semanas consecutivas:

Accion:
  1. Registrar en docs/lessons-learned.md automaticamente:
     "Tasa de aprobacion critica: [X] semanas con < 0.5/semana"
  2. Generar alerta para el humano (CASO 2 del orchestrator):
     "Tasa de aprobacion critica.
      Tasa actual: [X] estrategias/semana (minimo: 0.5)
      Semanas consecutivas por debajo del umbral: [N]
      Considerar recalibracion de umbrales.
      Ver Bucle de Recalibracion Estacional en skill-system-metrics.md"

La alerta es informativa — no paraliza el pipeline.
El humano decide si ajustar umbrales o continuar esperando.

---

## Bucle de Recalibracion Estacional

Si el meta-monitor detecta tasa critica, revisar estos
umbrales en orden de menor a mayor impacto.
NUNCA relajar los umbrales marcados como INTOCABLE.

### Umbrales ajustables (en este orden)

1. Triple swap miercoles: 15% → 20%
   Justificacion: periodo de altos swaps por tipos de interes altos
   Impacto en riesgo: bajo — el edge sigue siendo real

2. PF post-swaps ratio: 80% → 75%
   Justificacion: mercado con alta volatilidad de spreads
   Impacto en riesgo: medio — aceptable con spread documentado

3. Multimarket PF minimo: 1.0 → 0.9
   Justificacion: activos muy especificos con baja correlacion externa
   Impacto en riesgo: medio — puede aumentar riesgo de activo-especificidad

### Umbrales INTOCABLE — no relajar nunca

- PF minimo (1.4 EvalGate, 1.3 OOS, 1.25 WFO promedio)
- DD maximo (7% EvalGate, 7.5% WFO, 10% Catastrophic Veto)
- WFE minimo (50% aprobacion, 40% descarte)
- Sharpe OOS minimo (0.5)
- Catastrophic Veto WFO (PF < 0.8 o DD > 10% en cualquier ventana)

Razon: relajar estos umbrales aumenta directamente el riesgo
de poner capital real en estrategias sobreajustadas.
Es mejor esperar mas ciclos que bajar la barra de calidad.

### Procedimiento de ajuste
1. Documentar el ajuste en docs/lessons-learned.md con fecha
2. Aplicar solo al proximo ciclo — reevaluar despues
3. Si la tasa mejora → mantener o revertir al original
4. Si la tasa no mejora → investigar causa raiz del pipeline

---

## Cadena de Aprobacion Completa — Ratios Esperados

Documento de referencia para detectar cuellos de botella.

| Puerta | Input | Output esperado | Ratio esperado |
|--------|-------|-----------------|---------------|
| Builder | — | 1000 candidatas | — |
| EvalGate | 1000 | ~200 pasan | ~20% |
| SPP Validation | 200 | ~100 pasan | ~50% |
| WFO | 100 | ~40 pasan | ~40% |
| Multimarket | 40 | ~20 pasan | ~50% |
| Portfolio filter | 20 | ~10 pasan | ~50% |
| Forward Test | 10 | ~5 aprobadas | ~50% |

Ratio global esperado: ~0.5% de candidatas iniciales llegan a produccion.
Si una puerta tiene un ratio muy por debajo del esperado durante
2+ ciclos consecutivos → esa puerta es el cuello de botella.

La respuesta al cuello de botella NO es relajar el criterio.
Es investigar si los datos, la configuracion del Builder,
o el activo elegido son los responsables.

---

## Dashboard de salud del sistema

Panel de estado global del proyecto. Distinto del dashboard
de metricas de pipeline — este mide la salud operativa
del sistema completo, no solo las tasas de aprobacion.

Archivo: results\health-dashboard.md
Actualizar al inicio de cada sesion de trabajo.

### Metricas de pipeline (semana actual)

| Metrica | Valor | Referencia |
|---------|-------|------------|
| Tasa aprobacion EvalGate (semana) | [%] | 5-15% |
| Tasa aprobacion WFO (semana) | [%] | 30-60% |
| Tiempo medio de build | [h] | 24-48h |
| Builds completados (mes) | [N] | >= 2/mes |
| Ratio databank IS/OOS | [ratio] | 70/30 |

### Metricas de portfolio

| Metrica | Valor | Referencia |
|---------|-------|------------|
| Estrategias activas | [N] | objetivo 3-5 |
| DD combinado actual | [%] | < 12% |
| Correlacion media entre pares | [valor] | < 0.5 |
| PF medio en produccion | [valor] | >= 1.3 |
| Semanas sin deterioro detectado | [N] | continuo |

### Metricas de sistema

| Metrica | Valor | Estado |
|---------|-------|--------|
| Ultimo commit | [fecha] | verde si < 7 dias |
| Build activo en SQ | SI/NO | — |
| Ultimo backup SQ | [fecha] | verde si < 3 dias |
| VPS MT5 activo | SI/NO | verde si SI |
| ChromaDB indexado | [N entradas] | — |
| Ollama disponible | SI/NO | — |

### Alertas del meta-monitor

El orchestrator evalua estas condiciones al inicio de cada semana.
Si se cumple alguna condicion → alerta inmediata al humano.

**Build posiblemente estancado:**
  Condicion: build activo > 72 horas y 0 estrategias generadas.
  Mensaje: "Build [N] lleva [X]h sin generar candidatas.
    Verificar SQ: posible congelacion o recursos insuficientes."

**Portfolio perdiendo diversificacion:**
  Condicion: correlacion media del portfolio > 0.6 durante 1 semana.
  Mensaje: "Correlacion media del portfolio: [X] (maximo: 0.5).
    El portfolio esta convergiendo — revisar diversificacion de activos."

**Sistema posiblemente abandonado:**
  Condicion: sin commit en el repositorio durante > 7 dias.
  Mensaje: "Sin actividad en 7 dias.
    Estado del pipeline: desconocido.
    Verificar si hay trabajo en curso no registrado."

**Degradacion de produccion:**
  Condicion: PF medio de produccion < 85% del PF OOS backtest
    durante 4 semanas consecutivas.
  Mensaje: "Degradacion detectada en produccion.
    Ver account-recovery-manager para protocolo de reoptimizacion."

---

## Entropia de Shannon sobre Equity

Indicador adelantado de fatiga de estrategia.
Complementa el Z-Score del PF con una perspectiva
diferente: la variedad de los retornos, no solo su magnitud.

### Intuicion del indicador

Una curva de equity saludable tiene alta entropia:
  los retornos son variados, impredecibles en magnitud
  pero positivos en promedio. El EA sigue encontrando
  oportunidades en condiciones distintas.

Una curva de equity en fatiga tiene baja entropia:
  los retornos se vuelven muy uniformes (todos pequeños
  o todos identicos) o la curva se aplana.
  El EA puede haber perdido su edge sin que el PF
  lo indique todavia de forma clara.

### Calculo simplificado

```
1. Dividir la curva de equity en ventanas de 20 trades
2. Para cada ventana: calcular distribucion de retornos
   (bins: <-1%, -1 a 0%, 0 a 0.5%, 0.5 a 1%, >1%)
3. Calcular entropia de Shannon:
   H = -Σ p(x) * log2(p(x))
   donde p(x) es la proporcion de retornos en cada bin
4. Si H de las ultimas 4 ventanas < H_promedio_historico * 0.7
   → señal de fatiga adelantada
5. Combinar con Z-Score del PF para confirmacion:
   Fatiga confirmada si: H < 0.7 * H_media Y Z-Score PF < -1.5
```

El valor de H varia entre 0 (todos los retornos identicos)
y log2(N_bins) — maximo cuando todos los bins son equiprobables.
Para 5 bins: H_max = log2(5) ≈ 2.32 bits.

### Uso practico

Esta metrica es complementaria — nunca exclusiva.
Un solo periodo de baja entropia puede ser ruido normal.
La señal es relevante solo si persiste 4+ ventanas consecutivas
Y se confirma con deterioro del Z-Score del PF.

Accion si se confirma fatiga:
  Notificar al orchestrator → account-recovery-manager evalua.
  No desactivar el EA de forma automatica solo por entropia baja.

### Cuando implementar

Fase 10 — requiere al menos 200 trades en produccion real
para tener historial suficiente de ventanas H.
En Capa 0-2: usar solo el Z-Score del PF como indicador primario.

---

## Lo que esta skill NUNCA hace

NUNCA ajusta criterios de aprobacion para
mejorar las metricas artificialmente.
NUNCA ignora una tendencia negativa sostenida.
NUNCA compara tasas entre activos distintos
sin controlar el periodo de datos.
NUNCA relaja umbrales INTOCABLE bajo ninguna circunstancia.

Las metricas describen la realidad.
No se manipulan para que parezca mejor.