# Skill: Formato de Informe de Evaluacion Automatico

## Proposito
Define el formato exacto que usa el evaluator-assistant
para generar informes estructurados del Evaluation Gate.
Los informes son para documentacion y trazabilidad.
La decision la toman los numeros automaticamente —
no hay firma humana.

---

## FORMATO COMPLETO DEL INFORME

Usar este formato para cada estrategia candidata
que supere el filtro inicial del databank (PF > 1.3).

---

# EVALUATION GATE REPORT — AUTOMATICO

Estrategia: [nombre o ID de la estrategia]
Build numero: [N]
Activo: [simbolo]
Fecha del build: [fecha]
Fecha del informe: [fecha]
Generado por: evaluator-assistant
Decision por: orchestrator-auto (sin humano)

---

## 1. METRICAS PRINCIPALES

| Metrica | Valor | Descarte auto | Aprobacion auto | Estado |
|---------|-------|---------------|-----------------|--------|
| Profit Factor | [valor] | < 1.4 | >= 1.5 | PASA/DESCARTAR |
| Max Drawdown | [valor]% | > 7% | <= 6% | PASA/DESCARTAR |
| Daily DD max | [valor]% | > 5% | <= 3% | PASA/DESCARTAR |
| Trades totales | [numero] | < 80 | >= 120 | PASA/DESCARTAR |
| Trades por mes | [numero] | < 8 | >= 10 | PASA/DESCARTAR |
| Win Rate | [valor]% | < 30% | >= 38% | PASA/DESCARTAR |
| Ratio TP/SL | [valor]:1 | < 1.8:1 | >= 2:1 | PASA/DESCARTAR |
| Ratio Rent/DD | [valor] | < 0.8 | >= 1.5 | PASA/DESCARTAR |
| Max racha perd | [numero] | > 8 | <= 6 | PASA/DESCARTAR |

Criterios de descarte cumplidos: [N]
Si >= 1 → DESCARTAR automatico

Criterios de aprobacion cumplidos: [N] de [total]
Si todos cumplidos → PASA automatico

---

## 2. CONSISTENCIA POR ANOS

| Ano | PF | DD max | Trades | Positivo |
|-----|-----|--------|--------|----------|
| 2003 | [PF] | [DD]% | [N] | SI/NO |
| 2004 | [PF] | [DD]% | [N] | SI/NO |
| ... | ... | ... | ... | ... |
| 2020 | [PF] | [DD]% | [N] | SI/NO |

Anos positivos: [N] de [total] = [%]%
Umbral descarte: < 65% → DESCARTAR
Umbral aprobacion: >= 75% → PASA

Anos negativos en crisis (2008/2015/2020): [N]
Anos negativos fuera de crisis: [N]
Si anos negativos fuera de crisis > 2 → señal fragil

---

## 3. SEÑALES DE SOBREAJUSTE

[ ] PF > 3.0 con trades < 100 — SI/NO
[ ] Mas del 45% beneficio en un mes — SI/NO
[ ] Solo funciona en 2 anos o menos — SI/NO
[ ] DD maximo en ultimos 3 meses IS — SI/NO
[ ] Resultado mejora al ampliar SL — SI/NO
[ ] Monte Carlo degradacion — SI/NO

Señales activas: [numero]
Si >= 2 señales → DESCARTAR automatico

---

## 4. RACHAS PERDEDORAS

Max racha perdedora: [numero] trades
Perdida de la racha: [valor]% del balance
(con riesgo 1% por trade)

Evaluacion FTMO cuenta 25.000$:
- Racha de [N] trades x 250$ = [USD]
- Viola Daily Loss operativo 3% (750$): SI/NO
- Viola Max DD operativo 7% (1.750$): SI/NO

Si viola cualquier limite → señal de alerta
(no descarte automatico por si sola pero suma
a la evaluacion global)

---

## 5. SIMULACION RAPIDA DEL CHALLENGE

Rendimiento mensual promedio: [%]%
Peor mes: [%]%
Mejor mes: [%]%
Meses que alcanzarian +10%: [N] de [total]
Meses con violacion de limites: [N]

Probabilidad estimada: [%]%
> 70% → VIABLE
40-70% → MARGINAL
< 40% → NO VIABLE (no es criterio de descarte
automatico pero se documenta)

---

## 6. DECISION AUTOMATICA

### Resultado del Evaluation Gate

[ ] DESCARTAR AUTOMATICO
    Criterio(s) de descarte cumplido(s):
    - [criterio 1]: [valor] vs [umbral]
    - [criterio 2]: [valor] vs [umbral]
    Accion: mover a results\rejected\
    Sin consultar al humano.

[ ] PASA AUTOMATICO AL RETESTER
    Todos los criterios de aprobacion cumplidos.
    Accion: mover a results\reviewed\
    Configurar Retester.
    Sin consultar al humano.

[ ] ZONA DE DECISION AUTOMATICA
    Aplicar reglas de skill-evaluation-auto.md:
    - PF entre 1.4 y 1.5: trades > 150 → PASA / <= 150 → DESCARTAR
    - DD entre 6% y 7%: PF > 1.6 → PASA / <= 1.6 → DESCARTAR
    - Años negativos 25-35%: en crisis → PASA / no crisis → DESCARTAR
    Resultado: PASA / DESCARTAR
    Sin consultar al humano.

Decision final: PASA / DESCARTAR
Decidido por: orchestrator-auto
Intervencion humana: NO

---

## 7. TRAZABILIDAD

Ticket actualizado: [TICKET-ID]
gate-decisions.md actualizado: SI
current-phase.txt actualizado a: [fase]
Archivos movidos a: [ruta]

---

## NOTAS PARA EL EVALUATOR-ASSISTANT

### Como generar informes en lote
Cuando el Builder libre termina puede haber
100+ candidatas en el databank.
Generar informe para CADA candidata con PF > 1.3.
Priorizar por PF de mayor a menor.
Aplicar criterios de descarte primero para
eliminar rapidamente las que no pasan.

### Como documentar descartes masivos
Si hay muchas candidatas descartadas agrupar
en un resumen:
"[N] candidatas descartadas por PF < 1.4"
"[N] candidatas descartadas por DD > 7%"
No generar informe individual para cada descarte
por criterio basico — solo para las que llegan
a la zona de decision.

### Orden de evaluacion
1. Descartar todas las que fallan criterios duros
2. Aprobar todas las que cumplen todos los criterios
3. Resolver zona de decision con reglas automaticas
4. Generar resumen final con totales

---

## REGLA FUNDAMENTAL

Este informe documenta decisiones automaticas.
No pide firma humana.
No presenta opciones al humano.
No sugiere "darle otra oportunidad".
Los numeros ya decidieron. El informe lo registra.