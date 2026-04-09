# Skill: Configuracion del Retester

## Proposito
Guia para el sq-specialist y el orchestrator.
Define como configurar y ejecutar el Retester en SQ
para validar estrategias fuera de muestra (OOS).

---

## QUE ES EL RETESTER Y PARA QUE SIRVE

El Retester prueba una estrategia ya generada por el
Builder usando datos que NO se usaron en la construccion.
Es la prueba mas importante del pipeline.

Regla fundamental:
Los datos 2021-2026 estan reservados exclusivamente
para el Retester. NUNCA usarlos en el Builder.

---

## CUANDO USAR EL RETESTER

Solo despues de que una estrategia pase el Evaluation Gate.
Nunca retestear estrategias que no han pasado el Gate.

Orden correcto:
Builder → Evaluation Gate → Retester → Optimizer → Aprobacion

---

## CONFIGURACION DEL RETESTER EN SQ

### Paso 1: Abrir el Retester
SQ → clic en Retester en el menu lateral.

### Paso 2: Cargar la estrategia
Cargar desde results\reviewed\ usando el boton
de carga — NO desde el databank por defecto
que puede tener estrategias de otras sesiones.

### Paso 3: Configurar Tab Datos
Motor: MetaTrader5 (netted)
Simbolo: mismo que en el Builder
Temporalidad: H1
Fecha inicio: 2021.01.01
Fecha fin: fecha actual
Precision: 1 minute data tick simulation
Sin division de intervalo — periodo OOS completo

Comisiones EUR/USD:
- Spread: 0.5 pips
- Comision: 7 USD por lote
- Slippage: 0.5 pips

Comisiones XAU/USD:
- Spread: 30 pips
- Comision: 7 USD por lote
- Slippage: 2 pips

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
El Retester es mas rapido que el Builder —
5-30 minutos por estrategia.

---

## INTERPRETACION DE RESULTADOS

### Comparacion in-sample vs out-of-sample

PASA el Retester si:
- PF out-of-sample >= 1.3
- PF no cae mas del 30% respecto al in-sample
- DD out-of-sample <= 7%
- Trades proporcionales al periodo
- Consistencia por trimestres

Calculo de caida maxima permitida:
PF in-sample: 1.8
Caida maxima: 30% de 1.8 = 0.54
PF minimo OOS: 1.8 - 0.54 = 1.26
Si PF OOS = 1.35 → PASA
Si PF OOS = 1.15 → NO PASA (cayo mas del 30%)

REVISAR si:
- PF cae entre 20% y 30%
- Un trimestre muy malo pero el resto consistente

DESCARTAR si:
- PF OOS cae mas del 30%
- DD OOS supera el 7%
- Comportamiento completamente distinto al in-sample
- Muy pocos trades en el periodo OOS

### Señales de curve-fitting en Retester
- PF in-sample muy alto (>2.5) pero OOS muy bajo (<1.2)
- Muchos trades in-sample pero muy pocos OOS
- DD OOS mucho mayor que in-sample

---

## PROTOCOLO POST-RETESTER

### Si PASA
1. Mover archivo a results\reviewed\ con sufijo -retested
2. Documentar en log del orchestrator
3. Notificar al orchestrator para avanzar al Optimizer

### Si NO PASA
1. Mover a results\rejected\ con sufijo -retester-fail
2. Documentar razon exacta del descarte
3. Actualizar log del orchestrator

---

## ORDEN DE RETESTEO

Cuando hay varios candidatos retestear en orden:
1. Primero: mayor PF in-sample
2. Segundo: menor drawdown
3. Tercero: mas trades

No retestear todos a la vez — retestear uno,
revisar y decidir si continuar con los siguientes.

---

## ARCHIVO DE CONFIGURACION

Guardar cada Retester ejecutado en:
strategyquant\retester\[nombre]-retester-config.md

Formato:
Estrategia: [nombre]
Fecha: [fecha]
Periodo OOS: 2021.01.01 a [fecha actual]
Simbolo: [simbolo]
Temporalidad: H1
PF in-sample: [valor del Builder]
PF out-of-sample: [valor del Retester]
Caida del PF: [porcentaje]
DD out-of-sample: [valor]
Trades OOS: [numero]
Decision: PASA / NO PASA
Razon: [explicacion]