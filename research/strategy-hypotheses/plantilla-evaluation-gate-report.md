# EVALUATION GATE REPORT — AUTOMATICO

## Metadatos
Estrategia: [ID generado por SQ]
Build numero: [N]
Activo: [simbolo]
Ticket: [TICKET-ID]
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
Si todos → PASA automatico

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

---

## 3. SEÑALES DE SOBREAJUSTE

[ ] PF > 3.0 con trades < 100 — SI/NO
[ ] Mas del 45% beneficio en un mes — SI/NO
[ ] Solo funciona en 2 anos o menos — SI/NO
[ ] DD maximo en ultimos 3 meses IS — SI/NO
[ ] Resultado mejora al ampliar SL — SI/NO
[ ] Monte Carlo degradacion — SI/NO

Señales activas: [numero]
Si >= 2 → DESCARTAR automatico

---

## 4. RACHAS PERDEDORAS

Max racha perdedora: [numero] trades
Perdida de la racha: [valor]% del balance

Evaluacion FTMO cuenta 25.000$:
- Racha x 250$ = [USD]
- Viola Daily Loss operativo 3%: SI/NO
- Viola Max DD operativo 7%: SI/NO

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
< 40% → NO VIABLE

---

## 6. DECISION AUTOMATICA

[ ] DESCARTAR AUTOMATICO
    Criterio(s): [criterio exacto con valor vs umbral]
    Accion: mover a results\rejected\

[ ] PASA AUTOMATICO AL RETESTER
    Todos los criterios cumplidos.
    Accion: mover a results\reviewed\

[ ] ZONA DE DECISION AUTOMATICA
    Regla aplicada de skill-evaluation-auto.md:
    [regla concreta y resultado]

Decision final: PASA / DESCARTAR
Decidido por: orchestrator-auto
Intervencion humana: NO

---

## 7. TRAZABILIDAD

Ticket actualizado: [TICKET-ID]
gate-decisions.md actualizado: SI
current-phase.txt: [nueva fase]
Archivos movidos a: [ruta]