# Skill: Configuracion del Optimizer y Walk-Forward

## Proposito
Guia para el sq-specialist.
Define como configurar y ejecutar el Optimizer WFO
en SQ para estrategias que pasaron el paso 12b.
Las decisiones del WFO son 100% automaticas
segun skill-evaluation-auto.md.

---

## QUE ES EL OPTIMIZER Y PARA QUE SIRVE

El Optimizer ajusta los parametros de una estrategia
que ya funciona para verificar que el edge es
robusto en multiples ventanas de datos.

La herramienta clave es el Walk-Forward Optimization
(WFO) — divide los datos en ventanas repetidas de
in-sample y out-of-sample para verificar robustez.

Regla fundamental:
El Optimizer NO sirve para arreglar estrategias.
Solo verifica robustez de las que ya pasaron el 12b.
Si el WFO falla → DESCARTAR automatico.
No intentar con otros parametros.

---

## CUANDO USAR EL OPTIMIZER

Usar SOLO si la estrategia paso el paso 12b:
- PF OOS >= 1.3
- Caida PF IS→OOS <= 25%
- DD OOS <= 7%
- Aprobada automaticamente por el orchestrator

NO usar si:
- La estrategia no paso el paso 12b
- PF OOS < 1.3
- El objetivo es mejorar una estrategia mediocre

No hay decision humana sobre si lanzar el WFO.
Si paso el 12b → se lanza automaticamente.
Si no paso el 12b → se descarta automaticamente.

---

## CONFIGURACION DEL OPTIMIZER EN SQ

### Paso 1: Abrir el Optimizer
SQ → clic en Optimizador en el menu lateral.

### Paso 2: Cargar la estrategia
Cargar desde results\reviewed\ — las candidatas
que pasaron el paso 12b.

### Paso 3: Seleccionar metodo
Metodo: Walk-Forward Optimization
Tipo de ventana: Rolling (deslizante)
Numero de ventanas: minimo 5, recomendado 8
Porcentaje OOS por ventana: 25-30%

### Paso 4: Seleccionar parametros
MAXIMO 3 parametros simultaneamente.
Mas de 3 = sobreoptimizacion garantizada.

CRITICO: Los parametros a optimizar dependen
de la estrategia que SQ genero libremente.
NO hay parametros predefinidos como EMA o RSI.
Identificar los parametros principales de la
estrategia concreta y centrar los rangos en
los valores que el Builder encontro.

Ejemplo:
Si el Builder encontro ATR multiplicador = 2.3
→ rango WFO: 2.0 a 2.6, paso 0.1

Si el Builder encontro un periodo de indicador = 18
→ rango WFO: 14 a 22, paso 2

Regla: rango estrecho centrado en el valor del Builder.
NO rangos amplios como 1.0 a 5.0.

Parametros que NUNCA se optimizan:
- Riesgo por trade (siempre segun portfolio)
- Max trades por dia (siempre 2)
- Capital inicial
- Horario de sesion

### Paso 5: Configurar metrica
Metrica principal: Profit Factor
Metrica secundaria: Max Drawdown

### Paso 6: Ejecutar
Clic en Inicio y esperar.
El WFO tarda 2-6 horas segun numero de ventanas
y parametros. Lanzar en horario nocturno.

---

## INTERPRETACION DE RESULTADOS

La interpretacion completa esta en:
docs\skills\skill-wfo-interpretation.md

Los criterios automaticos de aprobacion y descarte
estan en: docs\skills\skill-evaluation-auto.md

### Referencia rapida de umbrales

Descarte automatico (sin consultar humano):
- WFE < 40%
- 2 ventanas OOS negativas consecutivas
- DD OOS > 7.5% en cualquier ventana
- PF OOS < 1.0 en la ultima ventana
- Parametros con desviacion > 35% entre ventanas

Aprobacion automatica (sin consultar humano):
- WFE >= 50%
- Max 1 ventana negativa aislada
- DD OOS <= 7% en todas las ventanas
- PF OOS ultima ventana >= 1.1
- Parametros con desviacion < 25%
- PF OOS promedio >= 1.25

No hay zona gris. No hay REVISAR.
Cumple los criterios → APROBADA.
No cumple → DESCARTAR.

---

## PROTOCOLO POST-OPTIMIZER

### Si PASA el WFO (automatico)
1. Guardar con sufijo -optimized
2. sq-specialist genera dictamen WFO completo
   usando plantilla-WFO-dictamen.md
3. Documentar parametros finales optimizados
4. El orchestrator aprueba automaticamente
5. Pasa al correlation-analyst para inclusion
   en el portfolio

### Si NO PASA el WFO (automatico)
1. Mover a results\rejected\ con sufijo -wfo-fail
2. Documentar criterio exacto de descarte
3. NO intentar con otros parametros
4. NO intentar con rangos diferentes
5. WFO falla = estrategia no robusta = DESCARTAR
6. Cerrar ticket automaticamente

---

## ARCHIVO DE CONFIGURACION

Guardar en:
strategyquant\optimizer\[ID]-wfo-config.md

Formato:
Estrategia: [ID]
Activo: [simbolo]
Fecha: [fecha]
Metodo: Walk-Forward Optimization
Ventanas: [numero]
Porcentaje OOS: [%]
Parametros optimizados:
  - [param 1]: rango [min-max], paso [x], optimo [valor]
  - [param 2]: rango [min-max], paso [x], optimo [valor]
  - [param 3]: rango [min-max], paso [x], optimo [valor]
WFE: [%]
PF promedio IS: [valor]
PF promedio OOS: [valor]
Estabilidad parametros: [desviacion %]
Ventanas negativas: [numero]
DD OOS maximo: [%]
PF OOS ultima ventana: [valor]
Dictamen: APROBADA / DESCARTAR
Criterio aplicado: [referencia a skill-evaluation-auto.md]
Decidido por: orchestrator-auto
Intervencion humana: NO

---

## REGLA FUNDAMENTAL

La robustez no se puede crear con optimizacion.
O esta en la logica desde el principio o no esta.
Si el WFO falla la solucion NO es optimizar mas.
Es generar nuevas candidatas con el Builder libre.
Los numeros deciden. Sin excepciones.