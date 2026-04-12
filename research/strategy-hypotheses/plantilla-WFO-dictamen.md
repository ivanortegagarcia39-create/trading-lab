# DICTAMEN WFO — Walk-Forward Optimization

## Metadatos
Estrategia: [ID generado por SQ]
Activo: [simbolo]
Build numero: [N]
Ticket: [TICKET-ID]
Fecha del WFO: [fecha]
Fecha del dictamen: [fecha]
Generado por: sq-specialist
Decision por: orchestrator-auto (sin humano)

---

## 1. CONFIGURACION DEL WFO

Metodo: Walk-Forward Optimization
Tipo de ventana: Rolling (deslizante)
Numero de ventanas: [numero] (minimo 5)
Porcentaje OOS por ventana: [%]%

Parametros optimizados (maximo 3):
- Parametro 1: [nombre] — rango [min-max], paso [x]
  Valor del Builder: [valor original]
- Parametro 2: [nombre] — rango [min-max], paso [x]
  Valor del Builder: [valor original]
- Parametro 3: [nombre] — rango [min-max], paso [x]
  Valor del Builder: [valor original]

Metrica de optimizacion: Profit Factor
Metrica secundaria: Max Drawdown

---

## 2. RESULTADOS POR VENTANA

| Ventana | IS PF | IS DD% | OOS PF | OOS DD% | Param1 | Param2 | OOS OK |
|---------|-------|--------|--------|---------|--------|--------|--------|
| 1 | | | | | | | SI/NO |
| 2 | | | | | | | SI/NO |
| 3 | | | | | | | SI/NO |
| 4 | | | | | | | SI/NO |
| 5 | | | | | | | SI/NO |
| 6 | | | | | | | SI/NO |
| 7 | | | | | | | SI/NO |
| 8 | | | | | | | SI/NO |
| MEDIA | | | | | — | — | — |

OOS OK = PF OOS >= 1.0 Y DD OOS <= 7%

---

## 3. CALCULO DE WFE

PF IS promedio: [valor]
PF OOS promedio: [valor]

WFE = (PF OOS promedio / PF IS promedio) x 100
WFE = [%]%

Umbral descarte: < 40%
Umbral aprobacion: >= 50%

---

## 4. ESTABILIDAD DE PARAMETROS

### Parametro 1: [nombre]
Valores por ventana: [v1], [v2], [v3], [v4], [v5], ...
Media: [valor]
Desviacion estandar: [valor]
Desviacion como % de la media: [%]%
Resultado: ESTABLE (<25%) / PRECAUCION (25-35%) / INESTABLE (>35%)

### Parametro 2: [nombre]
Valores por ventana: [v1], [v2], [v3], [v4], [v5], ...
Media: [valor]
Desviacion estandar: [valor]
Desviacion como % de la media: [%]%
Resultado: ESTABLE / PRECAUCION / INESTABLE

Conclusion estabilidad: ESTABLE / PRECAUCION / INESTABLE
Umbral descarte: desviacion > 35% en cualquier parametro

---

## 5. VENTANAS NEGATIVAS

Ventanas con PF OOS < 1.0: [numero]
Son consecutivas: SI / NO

Umbral descarte: 2 consecutivas
Umbral aprobacion: max 1 aislada

Ventanas con DD OOS > 7%: [numero]
Umbral descarte: > 7.5% en cualquier ventana

---

## 6. ULTIMA VENTANA

PF OOS ultima ventana: [valor]
PF OOS promedio: [valor]
Ratio ultima/promedio: [%]%

Umbral descarte: PF OOS ultima < 1.0
Umbral aprobacion: PF OOS ultima >= 1.1

DD OOS ultima ventana: [valor]%
Umbral: <= 7%

---

## 7. CRITERIOS AUTOMATICOS APLICADOS

| Criterio | Valor | Descarte | Aprobacion | Resultado |
|----------|-------|----------|------------|-----------|
| WFE | [%]% | < 40% | >= 50% | PASA/DESCARTAR |
| Ventanas negativas | [N] | 2 consec | Max 1 aisl | PASA/DESCARTAR |
| DD OOS max ventana | [%]% | > 7.5% | <= 7% | PASA/DESCARTAR |
| PF OOS ultima | [valor] | < 1.0 | >= 1.1 | PASA/DESCARTAR |
| Desv parametros | [%]% | > 35% | < 25% | PASA/DESCARTAR |
| PF OOS promedio | [valor] | < 1.1 | >= 1.25 | PASA/DESCARTAR |

Criterios de descarte cumplidos: [N]
Si >= 1 → DESCARTAR automatico

Criterios de aprobacion cumplidos: [N] de [total]
Si todos → APROBADA automatico

---

## 8. DICTAMEN FINAL

[ ] APROBADA
    Todos los criterios de aprobacion cumplidos.
    Accion: pasa al correlation-analyst para
    evaluacion de inclusion en portfolio.

[ ] DESCARTAR
    Criterio(s) de descarte cumplido(s):
    - [criterio]: [valor] vs [umbral]
    Accion: mover a results\rejected\
    Cerrar ticket.

Dictamen: APROBADA / DESCARTAR
Decidido por: orchestrator-auto
Intervencion humana: NO

---

## 9. PARAMETROS FINALES (solo si APROBADA)

Parametros optimizados para produccion:
- Parametro 1: [nombre] = [valor optimo]
- Parametro 2: [nombre] = [valor optimo]
- Parametro 3: [nombre] = [valor optimo]

Estos parametros se usaran en la exportacion
a MT5 por el export-specialist.

---

## 10. ACCION SIGUIENTE

Si APROBADA:
- Actualizar ticket a "portfolio-evaluation"
- correlation-analyst evalua inclusion automatica
- propfirm-analyst recomienda prop firm por scoring
- funding-specialist simula challenge dia a dia

Si DESCARTAR:
- Mover a results\rejected\ con sufijo -wfo-fail
- Documentar en gate-decisions.md del ticket
- Actualizar ticket a "rejected"
- NO intentar con otros parametros

---

Informe guardado en:
strategyquant\optimizer\[ID]-WFO-dictamen.md