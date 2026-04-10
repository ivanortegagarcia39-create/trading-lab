# SQ Workflow — Pipeline Automatico de Estrategias

## Principio fundamental
Ninguna decision del pipeline depende de un humano.
Los criterios numericos de skill-evaluation-auto.md
deciden que avanza y que se descarta automaticamente.
SQ decide la logica de las estrategias.
El pipeline de validacion filtra el sobreajuste.

---

## Fase A — Datos

### Objetivo
Tener datos historicos de calidad verificados
por el data-manager antes de lanzar cualquier build.

### Mercados activos
- EUR/USD — Forex spot
- XAU/USD — Oro spot

### Temporalidad
- H1 unicamente

### Minimo requerido
- 17 anos de datos historicos por mercado
- Periodo IS: 2003.05.05 a 2020.12.31
- Periodo OOS: 2021.01.01 a fecha actual

### Fuentes
- Dukascopy: datos M1 disponibles en SQ

### Configuracion estandar de comisiones
EUR/USD:
- Spread: 0.5 pips
- Comision: 7 USD por lote
- Slippage: 0.5 pips

XAU/USD:
- Spread: 30 pips
- Comision: 7 USD por lote
- Slippage: 2 pips

### Puerta automatica
data-manager verifica datos automaticamente.
Si datos OK → continuar.
Si datos incompletos → actualizar antes de continuar.
Sin decision humana.

---

## Fase B — Configuracion de Busqueda

### Objetivo
Configurar el Builder libre con paleta completa
de bloques sin restriccion de logica.

### Quien configura
market-analyst (configurador de busqueda)
siguiendo exactamente skill-builder-libre.md

### Lo que se configura
- Activo y temporalidad (confirmado por market-selector)
- Comisiones reales FTMO
- Restricciones de riesgo (ratio 2:1, 1% riesgo, etc)
- Paleta COMPLETA de bloques activada
- Modo continuo 24-48 horas
- Monte Carlo activado

### Lo que NO se configura
- Indicadores especificos
- Logica de entrada
- Hipotesis de mercado
- Tipo de estrategia (trend/mean reversion)

SQ decide todo esto libremente.

### Puerta automatica
Verificar que la paleta esta completa y las
comisiones son correctas. Sin decision humana.

---

## Fase C — Builder Libre

### Objetivo
Explorar el mayor espacio de busqueda posible
con +100 indicadores y millones de combinaciones.
SQ genera candidatas sin restriccion de logica.

### Configuracion
Ver docs\skills\skill-builder-libre.md

### Modo de operacion
- Modo continuo: ACTIVADO
- 30 generaciones por ciclo, 100 por isla, 4 islas
- Corre 24-48 horas minimo
- El humano lo para cuando el PF maximo
  no suba durante 6 horas consecutivas

### Donde guardar resultados
El databank de SQ almacena hasta 1000 candidatas
automaticamente reemplazando las peores.

### Puerta automatica
El Builder genera candidatas continuamente.
No hay decision humana sobre que genera.

---

## Fase D — Evaluation Gate Automatico

### Objetivo
Filtrar las candidatas del Builder aplicando
criterios numericos 100% automaticos.
Sin firma humana. Sin zona gris.

### Quien ejecuta
evaluator-assistant genera informes.
orchestrator aplica criterios de
skill-evaluation-auto.md automaticamente.

### Criterios de descarte automatico
Si cumple CUALQUIERA → DESCARTAR sin consultar:
- PF IS < 1.4
- Max DD IS > 7%
- Trades < 80
- Trades/mes < 8
- Win Rate < 30%
- Ratio TP/SL < 1.8:1
- Años negativos > 35%
- Mas del 45% beneficio en un mes
- DD maximo en ultimos 3 meses IS
- Max racha perdedora > 8 trades

### Criterios de aprobacion automatica
Si cumple TODOS → PASA al Retester sin consultar:
- PF IS >= 1.5
- Max DD IS <= 6%
- Trades >= 120
- Trades/mes >= 10
- Win Rate >= 38%
- Ratio TP/SL >= 2:1
- Años positivos >= 75%
- Ningun mes > 40% beneficio total
- DD maximo NO en ultimos 3 meses
- Max racha perdedora <= 6

### Resultado esperado
De ~1000 candidatas: ~200-300 pasan al Retester

---

## Fase E — Retester + Paso 12b Automatico

### Objetivo
Verificar que las estrategias funcionan con
datos fuera de muestra (2021-fecha actual)
y descartar automaticamente las que no.

### Configuracion Retester
- Periodo OOS: 2021.01.01 a fecha actual
- Comisiones IDENTICAS al Builder
- Filtros de clasificacion DESACTIVADOS
- Ver configuracion-estandar-retester.md

### Paso 12b — Analisis de degradacion OOS
Criterios de descarte automatico:
- PF OOS < 1.2 → DESCARTAR
- Caida PF > 25% → DESCARTAR
- DD OOS > 7% → DESCARTAR
- Frecuencia OOS cae > 50% → DESCARTAR

Todo dentro de limites → PASA al WFO

Sin decision humana en ningun punto.

### Resultado esperado
De ~200-300 retestadas: ~100-150 pasan al WFO

---

## Fase F — Optimizer WFO Automatico

### Objetivo
Verificar robustez con Walk-Forward Optimization.
Confirmar que los parametros son estables y
el edge se mantiene en multiples ventanas OOS.

### Configuracion
- Metodo: Walk-Forward Rolling
- Ventanas: minimo 5, recomendado 8
- OOS por ventana: 25-30%
- Max 3 parametros a optimizar
- Rangos estrechos centrados en valores del Builder

### Dictamen automatico
Criterios de descarte:
- WFE < 40% → DESCARTAR
- 2 ventanas negativas consecutivas → DESCARTAR
- DD OOS > 7.5% en cualquier ventana → DESCARTAR
- PF OOS < 1.0 en ultima ventana → DESCARTAR
- Parametros desviacion > 35% → DESCARTAR

Criterios de aprobacion:
- WFE >= 50%
- Max 1 ventana negativa aislada
- DD OOS <= 7% todas las ventanas
- PF OOS ultima ventana >= 1.1
- Parametros desviacion < 25%
- PF OOS promedio >= 1.25

Sin decision humana.

### Resultado esperado
De ~100-150 optimizadas: ~5-15 aprobadas

---

## Fase G — Portfolio Automatico

### Objetivo
Seleccionar automaticamente las combinaciones
de estrategias que maximicen la diversificacion
y minimicen el DD combinado del portfolio.

### Quien ejecuta
correlation-analyst aplica criterios de
skill-portfolio-selection.md automaticamente.

### Criterios de inclusion
- Score individual >= 55/100
- Correlacion con cada activa < 0.5
- DD combinado < 12%
- Max 2 estrategias por activo
- Max 3 estrategias por estilo

### Decisiones posibles
INCLUIR → entra en el portfolio automaticamente
ESPERA → va a cola hasta que haya espacio
DESCARTAR → correlacion > 0.7 con 2+ activas

Sin decision humana.

### Resultado esperado
De ~5-15 aprobadas: ~3-10 incluidas en portfolio

---

## Fase H — Produccion

### Objetivo
Desplegar las estrategias aprobadas en cuentas
de prop firms y monitorear automaticamente.

### Proceso
1. export-specialist exporta EA a MT5
2. Forward test en demo 2 semanas
   (UNICA intervencion humana del pipeline)
3. Comprar challenge en prop firm
4. performance-monitor monitorea 24/5

### Mantenimiento automatico
- Reportes semanales del performance-monitor
- Rebalanceo mensual del correlation-analyst
- Si deterioro → reemplazo automatico
- Si portfolio incompleto → nuevo ciclo Builder

---

## Resumen visual del pipeline

Datos → Configuracion Busqueda → Builder Libre 24-48h
→ Evaluation Gate AUTO → Retester → Paso 12b AUTO
→ WFO → Dictamen AUTO → Portfolio AUTO
→ Export → Demo (humano) → Challenge → Monitor

Cada flecha es una puerta AUTOMATICA.
Solo la flecha Demo→Challenge requiere humano.

---

## Aprendizajes criticos

Builds 1-8: hipotesis manual + firma humana = 0 aprobadas
Build 9+: Builder libre + evaluacion automatica

La leccion: el humano no debe decidir la logica
ni filtrar las estrategias. SQ genera, los numeros
filtran, el portfolio se construye por matematica.