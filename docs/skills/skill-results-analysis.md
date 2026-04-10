# Skill: Analisis Automatico de Resultados

## Proposito
Guia para el evaluator-assistant y el orchestrator.
Define como interpretar las metricas del Builder
y aplicar decisiones automaticas en el Evaluation Gate.
Todas las decisiones son por numeros.
Sin firma humana. Sin REVISAR. Sin SIMPLIFICAR.

---

## METRICAS PRINCIPALES Y SU SIGNIFICADO

### Profit Factor (PF)
Formula: ganancias brutas / perdidas brutas

Umbrales automaticos:
PF < 1.4 → DESCARTAR automatico
PF 1.4-1.5 → zona de decision automatica
  (ver skill-evaluation-auto.md para reglas)
PF >= 1.5 → candidata para aprobacion
PF > 3.0 → sospechoso de sobreajuste — verificar
  con señales de curve-fitting

### Max Drawdown
Umbrales automaticos para FTMO (cuenta 25.000$):
DD > 7% → DESCARTAR automatico
DD 6-7% → zona de decision automatica
DD <= 6% → candidata para aprobacion
DD < 3% → verificar que no es por falta de trades

### Numero de Trades
< 80 trades → DESCARTAR automatico
80-120 trades → zona de decision automatica
>= 120 trades → candidata para aprobacion
> 500 trades → excelente para estadistica

### Trades por mes
< 8 trades/mes → DESCARTAR automatico
8-10 trades/mes → zona de decision automatica
>= 10 trades/mes → candidata para aprobacion

### Win Rate
< 30% → DESCARTAR automatico
30-38% → zona de decision automatica
>= 38% → candidata para aprobacion

Win Rate bajo (35-45%) con PF alto →
estrategia de tendencia. Normal en H1.

Win Rate alto (60-80%) con PF bajo →
SL grande y TP pequeno. Peligrosa para FTMO.

### Ratio TP/SL efectivo
< 1.8:1 → DESCARTAR automatico
>= 2:1 → candidata para aprobacion

### Ratio Rentabilidad / Reduccion
RR < 0.8 → DESCARTAR automatico
RR >= 1.5 → candidata para aprobacion

### Max racha perdedora
> 8 trades consecutivos → DESCARTAR automatico
<= 6 trades consecutivos → candidata para aprobacion

---

## SEÑALES DE SOBREAJUSTE (CURVE-FITTING)

Cada señal detectada aumenta el riesgo.
2 o mas señales activas → DESCARTAR automatico.

1. PF > 3.0 con trades < 100
2. Mas del 45% del beneficio en un solo mes
3. Solo funciona en 2 anos o menos
4. DD maximo en los ultimos 3 meses del IS
5. Resultado mejora drasticamente al ampliar el SL
6. Años con PF < 1.0 superan el 35%
7. Monte Carlo muestra degradacion significativa

---

## ANALISIS DE CONSISTENCIA POR ANOS

Para cada estrategia candidata verificar:

Años con PF >= 1.0: contar como positivos
Años con PF < 1.0: contar como negativos

Porcentaje de anos positivos:
< 65% → DESCARTAR automatico
65-75% → zona de decision automatica
  (ver skill-evaluation-auto.md)
>= 75% → candidata para aprobacion

Años negativos que coinciden con crisis conocidas
(2008, 2015, 2020) son aceptables.
Años negativos en periodos normales son señal
de estrategia fragil.

---

## PROTOCOLO DE EVALUATION GATE AUTOMATICO

### Paso 1: Filtro rapido automatico
Eliminar inmediatamente todas las candidatas
que cumplan CUALQUIER criterio de descarte
de skill-evaluation-auto.md.
Sin consultar al humano.

### Paso 2: Aprobacion automatica
Aprobar inmediatamente todas las candidatas
que cumplan TODOS los criterios de aprobacion
de skill-evaluation-auto.md.
Sin consultar al humano.

### Paso 3: Zona de decision automatica
Para candidatas entre descarte y aprobacion
aplicar las reglas automaticas de la zona
definidas en skill-evaluation-auto.md.
Sin consultar al humano.

### Resultado
Generar resumen con:
- Total candidatas evaluadas
- Total descartadas (con criterio exacto por cada una)
- Total aprobadas para Retester
- Lista de aprobadas ordenadas por PF

---

## DIAGNOSTICO DE BUILDS CON POCOS RESULTADOS

### Build con 0 candidatas en databank tras 24h
Causas posibles (en orden de probabilidad):
1. Comisiones incorrectas → verificar
2. Datos no cubren el periodo → verificar con data-manager
3. Filtros de clasificacion demasiado estrictos
   → verificar PF > 1.3 (no subir mas)
4. Activo con muy poco edge en H1
   → NO es culpa de la paleta de bloques
   → considerar otro activo

CRITICO: La solucion NUNCA es restringir
los bloques de construccion. Si el Builder libre
con paleta completa no encuentra nada es porque
el activo no tiene edge suficiente con las
restricciones de riesgo actuales.

### Build con candidatas pero PF maximo < 1.4
El activo puede no tener edge suficiente
en H1 con comisiones reales.
Accion: probar el siguiente activo en la lista
de prioridad del market-selector.

### Build con muchas candidatas PF > 2.0
Puede ser buena señal o señal de sobreajuste.
El pipeline de validacion (Retester, 12b, WFO)
lo filtrara automaticamente.
NO descartar por PF alto — dejar que el
pipeline decida con datos OOS.

---

## TASAS DE DESCARTE ESPERADAS

En el Evaluation Gate del Builder libre:
- ~60-70% descartadas por criterios automaticos
- ~20-30% aprobadas para Retester
- ~5-10% en zona de decision automatica

Estas tasas son NORMALES. Un Builder libre genera
muchas estrategias mediocres junto con las buenas.
El pipeline existe para separar unas de otras
automaticamente.

---

## REGLA FUNDAMENTAL

Todas las decisiones son automaticas por numeros.
No hay REVISAR — la estrategia pasa o se descarta.
No hay SIMPLIFICAR — SQ decidio la complejidad.
No hay firma humana — los criterios de
skill-evaluation-auto.md son definitivos.
No hay segunda oportunidad — es mas eficiente
generar 1000 nuevas que arreglar una dudosa.