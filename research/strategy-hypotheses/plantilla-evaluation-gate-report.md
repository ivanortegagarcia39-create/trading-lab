# EVALUATION GATE REPORT

## Metadatos
Estrategia: [nombre o ID]
Ticket: [TICKET-ID]
Fecha del build: [fecha]
Fecha del informe: [fecha]
Generado por: evaluator-assistant
Build numero: [numero]

---

## 1. METRICAS PRINCIPALES

| Metrica | Valor | Umbral | Estado |
|---------|-------|--------|--------|
| Profit Factor | [valor] | >= 1.5 | OK / ALERTA |
| Max Drawdown | [valor]% | < 7% | OK / ALERTA |
| Daily Drawdown max | [valor]% | < 3% | OK / ALERTA |
| Trades totales | [numero] | >= 100 | OK / ALERTA |
| Trades por mes | [numero] | >= 20 | OK / ALERTA |
| Win Rate | [valor]% | >= 40% | OK / ALERTA |
| Ratio TP/SL efectivo | [valor]:1 | >= 2:1 | OK / ALERTA |
| Ratio Rent/DD | [valor] | >= 1.5 | OK / ALERTA |

---

## 2. CONSISTENCIA POR ANOS

| Ano | PF | DD max | Trades | Estado |
|-----|-----|--------|--------|--------|
| 2003 | | | | OK / MALO |
| 2004 | | | | OK / MALO |
| 2005 | | | | OK / MALO |
| 2006 | | | | OK / MALO |
| 2007 | | | | OK / MALO |
| 2008 | | | | OK / MALO |
| 2009 | | | | OK / MALO |
| 2010 | | | | OK / MALO |
| 2011 | | | | OK / MALO |
| 2012 | | | | OK / MALO |
| 2013 | | | | OK / MALO |
| 2014 | | | | OK / MALO |
| 2015 | | | | OK / MALO |
| 2016 | | | | OK / MALO |
| 2017 | | | | OK / MALO |
| 2018 | | | | OK / MALO |
| 2019 | | | | OK / MALO |
| 2020 | | | | OK / MALO |

Anos con PF < 1.0: [numero] de 18
Porcentaje de anos positivos: [%]%
Conclusion consistencia: ROBUSTA / ACEPTABLE / FRAGIL

Umbral minimo aceptable: 70% de anos positivos
Si menos del 70% → DESCARTAR automaticamente

---

## 3. SEÑALES DE SOBREAJUSTE
(basado en skill-avoiding-overfitting.md)

[ ] PF > 3.0 con trades < 100 — NO detectado
[ ] Mas del 50% del beneficio en un mes — NO detectado
[ ] Solo funciona en 2 anos o menos — NO detectado
[ ] Parametros en extremo del rango — NO detectado
[ ] DD maximo en los ultimos 3 meses — NO detectado
[ ] Resultado mejora solo al ampliar el SL — NO detectado

Señales activas: [numero]
Nivel de riesgo sobreajuste: BAJO / MEDIO / ALTO

Si ALTO → DESCARTAR automaticamente

---

## 4. ANALISIS DE RACHAS PERDEDORAS

Max racha perdedora consecutiva: [numero] trades
Perdida de la racha: [numero]% del balance
(con riesgo 1% por trade)

Evaluacion FTMO cuenta 25.000$:
- Racha de [N] trades x 250$ = [USD]
- Como % del balance: [%]%
- Viola Daily Loss operativo 3% (750$): SI / NO
- Viola Max DD operativo 7% (1.750$): SI / NO

---

## 5. SIMULACION DEL CHALLENGE

Rendimiento mensual promedio: [%]%
Peor mes del periodo: [%]%
Mejor mes del periodo: [%]%
Meses con rendimiento >= +10%: [N] de [total]
Meses con violacion de limites: [N] de [total]

Probabilidad estimada de pasar el challenge: [%]%

> 70% → VIABLE
40-70% → REVISAR position sizing
< 40% → NO viable todavia

---

## 6. COMPARATIVA CON BUILDS ANTERIORES

| Build | Hipotesis | PF | DD | Resultado |
|-------|-----------|-----|-----|-----------|
| Build 4 | EMACross M15 | 1.65 | 5.2% | Retester negativo |
| Build 5 | EMACross M15 | 1.27 | 6.1% | Descartada |
| Build 6 | NBAR M15 | 1.18 | 7.8% | Descartada |
| Build 7 | NBAR H1 | ? | ? | Desconocido |
| ESTE | [nombre] | [PF] | [DD]% | Pendiente |

Esta estrategia es [mejor/igual/peor] que
las candidatas del Build 4.

---

## 7. CRITERIOS DE DESCARTE AUTOMATICO

Si alguno de estos se cumple descartar sin
pasar al humano:

[ ] PF < 1.3 con comisiones reales → NO
[ ] DD > 8% → NO
[ ] Trades < 50 → NO
[ ] Mas del 50% beneficio en un mes → NO
[ ] DD maximo en ultimos 3 meses → NO
[ ] Menos del 70% de anos positivos → NO

Descarte automatico aplicado: SI / NO
Si SI → razon: [explicar]
Si NO → continuar con recomendacion del agente

---

## 8. RECOMENDACION DEL AGENTE

Decision recomendada: PASA / REVISAR / SIMPLIFICAR / DESCARTAR

Confianza: [X]/10

Justificacion:
[2-3 frases del razonamiento]

Observaciones criticas:
- [Observacion 1 si existe]
- [Observacion 2 si existe]

Siguiente paso recomendado:
[Accion concreta]

---

## 9. DECISION HUMANA

[ ] PASA — proceder al Retester
[ ] REVISAR — motivo: ______________________
[ ] SIMPLIFICAR — aspecto: _________________
[ ] DESCARTAR — motivo: ____________________

Firmado por: _______________
Fecha: _______________

Actualizar ticket [TICKET-ID]:
- gate-decisions.md con esta decision
- current-phase.txt a "retester-pending" si PASA