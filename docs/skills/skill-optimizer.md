# Skill: Configuracion del Optimizer y Walk-Forward

## Proposito
Guia para el sq-specialist y el orchestrator.
Define como configurar y ejecutar el Optimizer en SQ
para optimizar estrategias que ya pasaron el Retester.

---

## QUE ES EL OPTIMIZER Y PARA QUE SIRVE

El Optimizer ajusta los parametros de una estrategia
que ya funciona para mejorar sus metricas sin
sobreoptimizarla.

La herramienta mas importante es el Walk-Forward
Optimization (WFO) — divide los datos en ventanas
repetidas de in-sample y out-of-sample para verificar
que la optimizacion es robusta.

Regla fundamental:
El Optimizer NO sirve para arreglar estrategias rotas.
Solo se usa en estrategias que ya pasaron el Retester.

---

## CUANDO USAR EL OPTIMIZER

Usar SOLO si:
- La estrategia paso el Builder con PF >= 1.5
- La estrategia paso el Retester con caida < 30%
- PF out-of-sample >= 1.3
- Decision humana es continuar

NO usar si:
- La estrategia no paso el Retester
- PF in-sample < 1.5
- Menos de 100 trades
- El objetivo es arreglar una estrategia mala

---

## CONFIGURACION DEL OPTIMIZER EN SQ

### Paso 1: Abrir el Optimizer
SQ → clic en Optimizador en el menu lateral.

### Paso 2: Cargar la estrategia
Cargar desde results\reviewed\ con sufijo -retested.

### Paso 3: Seleccionar metodo
Metodo: Walk-Forward Optimization

Configuracion del WFO:
- Numero de ventanas: minimo 5, recomendado 8-10
- Porcentaje OOS por ventana: 20-30%
- Tipo de ventana: Rolling (deslizante)

### Paso 4: Seleccionar parametros
MAXIMO 3 parametros simultaneamente.
Mas de 3 = sobreoptimizacion garantizada.

Parametros recomendados para optimizar:
1. Periodo de la EMA o N de velas (rango: 10-50, paso: 5)
2. Umbral del RSI o ADX (rango: 18-35, paso: 2)
3. Multiplicador del TP en ATR (rango: 2.0-4.0, paso: 0.5)

Parametros que NUNCA se optimizan:
- Riesgo por trade (siempre 1%)
- Max trades por dia (siempre 2)
- Capital inicial

### Paso 5: Configurar metrica
Metrica principal: Profit Factor
Metrica secundaria: Max Drawdown

### Paso 6: Ejecutar
Clic en Inicio y esperar.
El WFO es lento — 2-6 horas segun ventanas.
Lanzar en horario nocturno.

---

## INTERPRETACION DE RESULTADOS DEL WFO

### Walk-Forward Efficiency (WFE)
Mide que tan bien se trasladan los resultados
in-sample a out-of-sample en cada ventana.

WFE > 70% → excelente robustez
WFE 50-70% → buena robustez. Aceptable para aprobar.
WFE 40-50% → robustez marginal. Revisar.
WFE < 40% → sobreoptimizada. DESCARTAR.

### Señales de sobreoptimizacion
1. Parametros optimos en extremos del rango
   Ejemplo: N optimo = 50 y el rango era 10-50
   → busco el extremo, no hay robustez

2. WFE < 40%

3. Cada ventana WFO da parametros muy diferentes
   → la estrategia no tiene parametros estables

4. PF in-sample muy alto pero OOS muy bajo

### Señales de robustez
- WFE > 50%
- Parametros optimos similares entre ventanas
- PF OOS consistente entre ventanas
- Sin ventanas con perdidas grandes y aisladas

---

## PROTOCOLO POST-OPTIMIZER

### Si PASA el WFO
1. Guardar con sufijo -optimized
2. Documentar parametros finales:
   - Parametros originales del Builder
   - Parametros optimizados por WFO
   - WFE obtenido
3. Notificar al orchestrator para Aprobacion final

### Si NO PASA el WFO
1. Mover a results\rejected\ con sufijo -wfo-fail
2. Documentar razon exacta
3. NO intentar con otros parametros
   WFO falla = estrategia no robusta = DESCARTAR

---

## ARCHIVO DE CONFIGURACION

Guardar en:
strategyquant\optimizer\[nombre]-wfo-config.md

Formato:
Estrategia: [nombre]
Fecha: [fecha]
Metodo: Walk-Forward Optimization
Ventanas: [numero]
Porcentaje OOS: [%]
Parametros optimizados:
  - [param 1]: rango [min-max], paso [x], optimo [valor]
  - [param 2]: rango [min-max], paso [x], optimo [valor]
  - [param 3]: rango [min-max], paso [x], optimo [valor]
WFE: [%]
PF promedio in-sample: [valor]
PF promedio OOS: [valor]
Decision: PASA / NO PASA
Razon: [explicacion]

---

## REGLA DE ORO DEL OPTIMIZER

Si hay duda sobre si una estrategia es robusta
despues del WFO → DESCARTAR.

La robustez no se puede crear con optimizacion.
O esta en la logica desde el principio o no esta.