# Skill: Configuracion del Retester

## Proposito
Guia para el sq-specialist.
Define como configurar y ejecutar el Retester en SQ
para validar estrategias fuera de muestra (OOS).
El Retester se ejecuta en lote para TODAS las
candidatas que pasaron el Evaluation Gate.
Las decisiones post-Retester son automaticas
segun el paso 12b de skill-evaluation-auto.md.

---

## QUE ES EL RETESTER Y PARA QUE SIRVE

El Retester prueba estrategias generadas por el
Builder libre usando datos que NO se usaron
en la construccion (2021 a fecha actual).

Regla fundamental:
Los datos 2021-actual estan reservados exclusivamente
para el Retester. NUNCA usarlos en el Builder.

---

## CUANDO USAR EL RETESTER

Solo despues de que el orchestrator apruebe
automaticamente candidatas en el Evaluation Gate.
Retestear TODAS las aprobadas en lote.
No seleccionar manualmente — no hay sesgo.

Orden correcto:
Builder libre → Evaluation Gate AUTO →
Retester (todas en lote) → Paso 12b AUTO →
WFO → Dictamen AUTO → Portfolio AUTO

---

## CONFIGURACION DEL RETESTER EN SQ

### Paso 1: Abrir el Retester
SQ → clic en Retester en el menu lateral.

### Paso 2: Cargar las estrategias
Cargar TODAS las candidatas aprobadas desde
results\reviewed\ usando el boton de carga.
NO desde el databank por defecto.
NO seleccionar individualmente — cargar todas.

### Paso 3: Configurar Tab Datos
Motor: MetaTrader5 (netted)
Simbolo: mismo que en el Builder
Temporalidad: H1
Fecha inicio: 2021.01.01
Fecha fin: fecha actual
Precision: 1 minute data tick simulation
Sin division de intervalo — periodo OOS completo

Comisiones: IDENTICAS al Builder.
Verificar en CLAUDE.md las comisiones exactas
del activo seleccionado.

CRITICO: Las comisiones del Retester deben ser
exactamente iguales a las del Builder.
Si son diferentes los resultados no son comparables.
Verificar SIEMPRE antes de lanzar.

Ver tambien:
strategyquant\retester\configuracion-estandar-retester.md

### Paso 4: Configurar Tab Opciones de negociacion
Mismos ajustes que en el Builder:
- Sesion: 08:00 a 20:00
- Max trades por dia: 2
- Salida al final del dia: ACTIVADO
- No fines de semana: ACTIVADO
- Salida el viernes: ACTIVADO

### Paso 5: Configurar Tab Gestion del dinero
- Metodo: Riesgo fijo en % de la cuenta
- Riesgo: 1%
- Capital: 25.000$

### Paso 6: Configurar Tab Clasificacion
- Filtros personalizados: TODOS DESACTIVADOS
- Queremos ver resultados reales sin filtros
- Ranking: Aptitud ponderada

### Paso 7: Configurar Tab Comprobaciones cruzadas
- Mayor precision: ACTIVADO
- Todo lo demas: DESACTIVADO

### Paso 8: Ejecutar
Clic en Inicio y esperar.
El Retester procesa todas las candidatas en lote.
Tiempo: 5-30 minutos por estrategia.
Para 300 candidatas: 1-4 horas aproximadamente.

---

## INTERPRETACION DE RESULTADOS

La interpretacion la hace el paso 12b
automaticamente segun skill-evaluation-auto.md.

### Criterios automaticos del paso 12b

Descarte automatico (sin consultar humano):
- PF OOS < 1.2
- Caida PF IS→OOS > 25%
- DD OOS > 7%
- Trades/mes OOS < 5
- Caida frecuencia > 50%

Aprobacion automatica para WFO:
- PF OOS >= 1.3
- Caida PF <= 20%
- DD OOS <= 6.5%
- Trades/mes OOS >= 6
- Caida frecuencia <= 40%

En el paso 12b NO hay zona intermedia.
O cumple → WFO. O no cumple → DESCARTAR.
No hay REVISAR. No hay segunda oportunidad.

### Señales de sobreajuste en OOS
- PF IS muy alto (>2.5) pero OOS muy bajo (<1.2)
- Muchos trades IS pero muy pocos OOS
- DD OOS mucho mayor que IS (>50% mas)
- Comportamiento completamente distinto IS vs OOS

---

## PROTOCOLO POST-RETESTER (automatico)

### Las que PASAN el paso 12b
1. Mover a results\reviewed\ con sufijo -retested
2. Documentar en gate-decisions.md del ticket
3. El orchestrator configura WFO automaticamente
4. Sin consultar al humano

### Las que NO PASAN el paso 12b
1. Mover a results\rejected\ con sufijo -retester-fail
2. Documentar criterio exacto de descarte
3. Sin consultar al humano
4. Sin segunda oportunidad

---

## ORDEN DE RETESTEO

Retestear TODAS las candidatas aprobadas en lote.
No seleccionar manualmente.
No retestear "una por una para ver".
El paso 12b descarta automaticamente las que
no cumplen — no hay necesidad de elegir.

Prioridad de procesamiento post-Retester:
1. Mayor PF OOS — procesadas primero en el WFO
2. Menor DD OOS
3. Mayor numero de trades

---

## ARCHIVO DE CONFIGURACION

Guardar en:
strategyquant\retester\build-[N]-retester-config.md

Formato:
Build numero: [N]
Activo: [simbolo]
Fecha: [fecha]
Periodo OOS: 2021.01.01 a [fecha actual]
Temporalidad: H1
Comisiones: [segun activo — verificadas]
Candidatas retestadas: [numero]
Aprobadas paso 12b: [numero]
Descartadas paso 12b: [numero]
Decidido por: orchestrator-auto
Intervencion humana: NO

---

## REGLA FUNDAMENTAL

El Retester verifica. El paso 12b decide.
Todo automatico. Sin firma humana.
Sin seleccion manual de candidatas.
Sin REVISAR. Sin segunda oportunidad.
Los numeros deciden que pasa al WFO.