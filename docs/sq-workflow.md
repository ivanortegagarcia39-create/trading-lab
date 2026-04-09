# SQ Workflow — Pipeline de Estrategias

## Principio fundamental
Ninguna estrategia avanza sin pasar la puerta de decision
de la fase anterior. Las decisiones las tomamos nosotros,
no Claude.

---

## Fase A — Datos

### Objetivo
Tener datos historicos de calidad antes de lanzar cualquier build.

### Mercados iniciales
- EUR/USD — Forex spot
- XAU/USD — Oro spot

### Temporalidades
- H1 principal

### Minimo requerido
- 10 anos de datos historicos por mercado
- 18 anos recomendado (2003-2020 in-sample)

### Fuentes
- Dukascopy: datos M1 disponibles en SQ

### Donde guardarlos
C:\Users\ivano\trading-lab\strategyquant\databanks\

### Configuracion estandar de comisiones
Usar siempre en Builder Y Retester:

EUR/USD:
- Desviacion (spread): 0.5 pips
- Comision: 7 USD por lote completo
- Deslizamiento: 0.5 pips

XAU/USD:
- Desviacion (spread): 30 pips
- Comision: 7 USD por lote completo
- Deslizamiento: 2 pips

NOTA CRITICA XAU/USD: 1 pip = 0.01 USD/oz
El numero a introducir en SQ depende de como
SQ defina el pip para ese instrumento.
Verificar siempre antes de lanzar.

Periodo OOS reservado: 2021.01.01 a 2026 (fecha actual)
Este periodo NO se usa nunca en Builder.
Solo se usa en Retester.

### Puerta de decision
Los datos estan importados y verificados en SQ
Data Manager? SI/NO — si NO no se lanza ningun build.

---

## Fase B — Hypothesis Design

### Objetivo
Tener una hipotesis clara ANTES de abrir Builder.
Builder sin hipotesis previa genera basura.

### Quien la genera
Agente market-analyst + agente funding-specialist.

### Donde se guarda
C:\Users\ivano\trading-lab\research\strategy-hypotheses\

### Formato obligatorio
Cada hipotesis debe incluir:
- Nombre
- Mercado y temporalidad
- Logica de entrada en lenguaje natural
- Sesion objetivo
- Condiciones de salida
- Invalidaciones
- Compatibilidad teorica con FTMO

### Puerta de decision
La hipotesis tiene todos los campos completos
y tiene sentido economico? SI/NO

---

## Fase C — Builder

### Objetivo
Explorar variantes dentro del espacio definido
por la hipotesis. No buscar milagros.

### Configuracion obligatoria antes de lanzar
Ver docs\skills\skill-precbuild-checklist.md

### Donde guardar resultados
C:\Users\ivano\trading-lab\results\raw\build-results\

### Puerta de decision
Hay estrategias con PF > 1.5 y DD < 7%
con comisiones reales? SI/NO

---

## Fase D — Evaluation Gate

### Objetivo
Filtrar el output del Builder antes de retestear.
No todo lo que genera Builder merece un Retester.

### Criterios de evaluacion
- PF >= 1.5 con comisiones reales
- Max Drawdown < 7%
- Numero de trades >= 100
- Consistencia por anos > 70%
- Logica tiene sentido economico

### Decisiones posibles
- PASA → pasa a Retester
- REVISAR → vuelve a Builder con ajustes
- SIMPLIFICAR → reducir complejidad
- DESCARTAR → documentar y archivar

### Donde se mueven los archivos
Las que PASAN:
C:\Users\ivano\trading-lab\results\reviewed\

Las DESCARTADAS:
C:\Users\ivano\trading-lab\results\rejected\

---

## Fase E — Retester

### Objetivo
Verificar que la estrategia funciona con datos
fuera de muestra (out-of-sample 2021-2026).

### Configuracion
- Periodo: 2021.01.01 a fecha actual
- Mismas comisiones que el Builder
- Mismo simbolo y temporalidad

### Puerta de decision
- PF out-of-sample >= 1.3
- PF no cae mas del 30% respecto al in-sample
- DD out-of-sample <= 7%

---

## Fase F — Optimizer

### Objetivo
Optimizar parametros de una estrategia que ya
merece la pena. NO para rescatar estrategias malas.

### Metodo
Walk-Forward Optimization (WFO)
- Minimo 5 ventanas
- WFE minimo aceptable: 50%

### Puerta de decision
WFE >= 50% y parametros estables entre ventanas.

---

## Fase G — Aprobacion final

### Requisitos obligatorios
- Informe de funding-specialist: COMPATIBLE CON FTMO
- Ha pasado Builder, Retester y Optimizer
- WFE >= 50%
- Decision humana final: SI

### Donde se mueve
C:\Users\ivano\trading-lab\results\approved\

---

## Resumen visual del pipeline

Datos → Hypothesis → Builder → Evaluation Gate
→ Retester → Optimizer → Aprobacion final
→ results\approved\

Cada flecha es una puerta.
Sin pasar la puerta anterior no se avanza.

---

## Aprendizajes criticos de builds anteriores

Build 1-2: logica de rango asiatico no nativa en SQ
→ Verificar siempre contra skill-sq-builder.md

Build 3: filtros demasiado estrictos y opciones
geneticas mal configuradas
→ Usar siempre 20 generaciones y 50 por isla

Build 4: sin comisiones reales — resultados irreales
→ Comisiones FTMO obligatorias desde el Builder

Build 5-6: M15 con comisiones reales — edge insuficiente
→ H1 como temporalidad principal