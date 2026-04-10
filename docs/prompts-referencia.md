# Prompts de Referencia Rapida — TradingLab
# Enfoque: Builder Libre + Evaluacion 100% Automatica

## Proposito
Archivo de consulta rapida con todos los prompts
del pipeline listos para copiar y pegar en Claude Code.
Todas las decisiones son automaticas por numeros.
El humano solo pulsa botones en SQ y hace forward test.

---

## INICIO DE SESION

### Prompt estandar de inicio
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

## CICLO DE BUSQUEDA (BUILDER LIBRE)

### Paso 1 — Verificar datos
Actua segun agents\data-manager.md.
Lee docs\skills\skill-data-management.md.
Verifica que los datos de EUR/USD y XAU/USD
estan completos y actualizados en SQ.
Genera informe en strategyquant\databanks\


### Paso 2 — Confirmar activo
Actua segun agents\market-selector.md.
Lee docs\skills\skill-propfirms-comparison.md y
docs\skills\skill-market-context.md.
Confirma el activo optimo para el proximo ciclo
de Builder libre.


### Paso 3 — Configurar Builder libre
Actua segun agents\market-analyst.md.
Lee docs\skills\skill-builder-libre.md.
Configura los parametros de busqueda para el
Build [N] en modo Builder libre.
Paleta completa de bloques activada.
Sin hipotesis. Sin restriccion de logica.
SQ decide la estrategia.
Genera archivo de configuracion en
strategyquant\builder\build-[N]-config.md
Crea ticket TICKET-[NNN]-BUILD-[N] en
research\active-tickets\


### Paso 4 — Lanzar build
[HUMANO: Abrir SQ, configurar segun el archivo
build-[N]-config.md tab por tab, lanzar y dejar
correr 24-48 horas en modo continuo]


---

## EVALUATION GATE AUTOMATICO (tras parar el build)

### Paso 5 — Generar informes y aplicar criterios
Actua segun agents\orchestrator.md.
Lee docs\skills\skill-evaluation-auto.md y
docs\skills\skill-results-analysis.md.
El Build [N] ha terminado.
Resultados: [N] candidatas en databank,
PF maximo [X], DD minimo [Y]%.

Invoca al evaluator-assistant para generar
informes de TODAS las candidatas con PF > 1.3.

Aplica los criterios de skill-evaluation-auto.md
de forma 100% automatica:
- DESCARTE automatico si cumple cualquier
  criterio de descarte
- APROBACION automatica si cumple todos
  los criterios de aprobacion
- Zona de revision: aplicar reglas automaticas
  sin consultar al humano

Genera un resumen con:
- Total candidatas evaluadas
- Total descartadas automaticamente con razon
- Total aprobadas para Retester
- Lista de las aprobadas con metricas

Actualiza ticket con todas las decisiones.
No esperar confirmacion humana para ninguna decision.


---

## RETESTER + PASO 12b AUTOMATICO

### Paso 6 — Configurar Retester en lote
Actua segun agents\sq-specialist.md.
Lee docs\skills\skill-retester.md y
strategyquant\retester\configuracion-estandar-retester.md.
Configura el Retester para TODAS las candidatas
aprobadas en el Evaluation Gate.
Verificar que las comisiones son IDENTICAS al Builder.
Genera configuracion en strategyquant\retester\


### Paso 7 — Lanzar Retester
[HUMANO: Lanzar Retester en SQ con las
candidatas aprobadas. Esperar resultados.]


### Paso 8 — Analisis OOS automatico (paso 12b)
Actua segun agents\orchestrator.md.
Lee docs\skills\skill-evaluation-auto.md.
El Retester ha terminado.

Invoca al sq-specialist para generar informe
IS vs OOS de CADA candidata retestada.

Aplica los criterios del paso 12b de forma
100% automatica para CADA candidata:
- PF OOS < 1.2 → DESCARTAR automatico
- Caida PF > 25% → DESCARTAR automatico
- DD OOS > 7% → DESCARTAR automatico
- Frecuencia OOS cae > 50% → DESCARTAR automatico
- Todo dentro de limites → PASA al WFO

Genera resumen:
- Total retestadas
- Total descartadas con criterio exacto
- Total aprobadas para WFO
- Lista de aprobadas con metricas IS y OOS

No esperar confirmacion humana.


---

## WFO AUTOMATICO

### Paso 9 — Configurar Optimizer
Actua segun agents\sq-specialist.md.
Lee docs\skills\skill-optimizer.md y
docs\skills\skill-wfo-interpretation.md.
Configura el WFO para TODAS las candidatas
que pasaron el paso 12b.
Maximo 3 parametros por estrategia.
Rangos estrechos centrados en valores del Builder.
Genera configuracion en strategyquant\optimizer\


### Paso 10 — Lanzar Optimizer
[HUMANO: Lanzar WFO en SQ. Esperar resultados.
Puede tardar 2-6 horas por estrategia.]


### Paso 11 — Dictamen WFO automatico
Actua segun agents\orchestrator.md.
Lee docs\skills\skill-evaluation-auto.md y
docs\skills\skill-wfo-interpretation.md.
El Optimizer ha terminado.

Invoca al sq-specialist para generar dictamen
WFO de CADA candidata optimizada.

Aplica los criterios WFO de forma 100% automatica:
- WFE < 40% → DESCARTAR automatico
- 2 ventanas negativas consecutivas → DESCARTAR
- DD OOS > 7.5% en cualquier ventana → DESCARTAR
- PF OOS < 1.0 en ultima ventana → DESCARTAR
- Parametros desviacion > 35% → DESCARTAR
- Cumple todos los criterios → APROBADA

Genera resumen:
- Total evaluadas en WFO
- Total descartadas con criterio exacto
- Total APROBADAS definitivamente
- Lista de aprobadas con WFE y metricas

No esperar confirmacion humana.


---

## PORTFOLIO AUTOMATICO

### Paso 12 — Inclusion en portfolio
Actua segun agents\correlation-analyst.md.
Lee docs\skills\skill-portfolio-selection.md y
docs\skills\skill-evaluation-auto.md.

Para CADA estrategia aprobada por el WFO:
1. Calcular score individual (formula de la skill)
2. Calcular correlacion con cada estrategia activa
3. Calcular DD combinado estimado
4. Verificar reglas de diversificacion
5. Decision automatica: INCLUIR / ESPERA / DESCARTAR

Si INCLUIR:
- Invocar propfirm-analyst para prop firm optima
- Invocar funding-specialist para simulacion FTMO
- Invocar export-specialist para exportar EA a MT5
- Ajustar riesgo por estrategia segun tamaño portfolio

Genera informe de portfolio completo.
No esperar confirmacion humana.


---

## PRODUCCION (UNICA INTERVENCION HUMANA)

### Paso 13 — Forward test en demo
[HUMANO: Activar EA en cuenta demo de la prop
firm durante minimo 2 semanas.
Verificar que opera correctamente.
Si funciona bien → comprar challenge.
Si hay problemas → revisar exportacion.]


### Paso 14 — Activar monitoreo
Actua segun agents\performance-monitor.md.
El EA [nombre] esta activo en [prop firm].
Inicia el monitoreo automatico.
Genera reportes diarios y semanales.
Aplica alertas automaticas segun niveles
definidos en el agente.


---

## CIERRE DE SESION

### Prompt estandar de cierre
Actua segun agents\orchestrator.md.
Resume lo que se ha hecho en esta sesion.
Actualiza docs\project-status.md.
Actualiza todos los tickets activos.
Lista todas las decisiones automaticas tomadas
con el criterio numerico aplicado en cada una.
Dime el commit exacto que debo ejecutar.


---

## DIAGNOSTICO

### Cuando un build no genera candidatas suficientes
Actua segun agents\orchestrator.md.
Lee docs\skills\skill-pipeline-errors.md y
docs\skills\skill-builder-libre.md.
El Build [N] ha corrido [X] horas y tiene
[N] candidatas con PF > 1.3 en el databank.
Diagnostica si es normal o hay un problema.
Si hay problema propone solucion sin restringir
la paleta de bloques — la solucion NUNCA es
limitar los indicadores.


### Estado completo del sistema
Actua segun agents\orchestrator.md.
Lee docs\skills\skill-evaluation-auto.md y
docs\skills\skill-portfolio-selection.md.
Dame el estado completo:
1. Tickets activos y fase
2. Portfolio activo con correlaciones
3. Cola de espera con scores
4. Estrategias en produccion con rendimiento
5. Proxima accion automatica del sistema


### Cuando el portfolio necesita reemplazo
Actua segun agents\correlation-analyst.md.
Lee docs\skills\skill-portfolio-selection.md.
El performance-monitor ha detectado deterioro
en la estrategia [nombre].
Ejecuta el protocolo de reemplazo automatico:
1. Buscar candidata en cola de espera
2. Si hay candidata compatible → reemplazar
3. Si no hay → lanzar nuevo ciclo de Builder
Todo automatico sin consultar al humano.


---

## REGLA QUE APLICA A TODOS LOS PROMPTS

En ningun prompt se pide confirmacion humana
para decisiones del pipeline.
En ningun prompt se espera una firma humana.
En ningun prompt se presenta opciones al humano
para que elija entre estrategias.

Los numeros deciden. El humano solo ejecuta
acciones fisicas en SQ y hace forward test.