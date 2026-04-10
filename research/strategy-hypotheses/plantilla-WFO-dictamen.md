# DICTAMEN WFO — Walk-Forward Optimization

## Metadatos
Estrategia: [nombre]
Ticket: [TICKET-ID]
Fecha del WFO: [fecha]
Fecha del dictamen: [fecha]
Generado por: sq-specialist
Leido por: orchestrator

---

## 1. CONFIGURACION DEL WFO

Metodo: Walk-Forward Optimization
Tipo de ventana: Rolling (deslizante)
Numero de ventanas: [numero] (minimo 5)
Periodo IS por ventana: [X] años
Periodo OOS por ventana: [X] año
Porcentaje OOS: [%]%

Parametros optimizados (maximo 3):
- Parametro 1: [nombre] — rango [min] a [max]
- Parametro 2: [nombre] — rango [min] a [max]
- Parametro 3: [nombre] — rango [min] a [max] (opcional)

Metrica de optimizacion: Profit Factor
Metrica secundaria: Max Drawdown

---

## 2. TABLA DE RESULTADOS POR VENTANA

| Ventana | IS PF | IS DD% | OOS PF | OOS DD% | Param1 | Param2 | OOS OK |
|---------|-------|--------|--------|---------|--------|--------|--------|
| 1 | | | | | | | SI/NO |
| 2 | | | | | | | SI/NO |
| 3 | | | | | | | SI/NO |
| 4 | | | | | | | SI/NO |
| 5 | | | | | | | SI/NO |
| 6 | | | | | | | SI/NO |
| MEDIA | | | | | - | - | - |

OOS OK = PF OOS >= 1.0 Y DD OOS <= 7%

---

## 3. CALCULO DE WFE

PF IS promedio: [valor]
PF OOS promedio: [valor]

WFE = (PF OOS promedio / PF IS promedio) x 100
WFE = ([OOS] / [IS]) x 100 = [%]%

Interpretacion:
[ ] WFE >= 70% → Excelente
[ ] WFE 50-70% → Buena — aceptable para avanzar
[ ] WFE 40-50% → Regular — considerar simplificar
[ ] WFE < 40% → Pobre — DESCARTAR o SIMPLIFICAR

---

## 4. ESTABILIDAD DE PARAMETROS

### Parametro 1: [nombre]
Valores por ventana: [v1], [v2], [v3], [v4], [v5]
Media: [valor]
Desviacion estandar: [valor]
Desviacion como % de la media: [%]%

[ ] Desviacion < 20% de la media → ESTABLE
[ ] Desviacion 20-35% de la media → PRECAUCION
[ ] Desviacion > 35% de la media → INESTABLE

### Parametro 2: [nombre]
Valores por ventana: [v1], [v2], [v3], [v4], [v5]
Media: [valor]
Desviacion estandar: [valor]
Desviacion como % de la media: [%]%

[ ] Desviacion < 20% de la media → ESTABLE
[ ] Desviacion 20-35% de la media → PRECAUCION
[ ] Desviacion > 35% de la media → INESTABLE

Conclusion estabilidad: ESTABLE / PRECAUCION / INESTABLE

---

## 5. ANALISIS DE VENTANAS NEGATIVAS

Ventanas con PF OOS < 1.0: [numero]
Son consecutivas: SI / NO
Ventanas con DD OOS > 7%: [numero]

Interpretacion:
[ ] 0 ventanas negativas → OK
[ ] 1 ventana negativa aislada → Precaucion
[ ] 2 ventanas negativas consecutivas → DESCARTAR
[ ] Alguna ventana con DD > 7% → REVISAR o DESCARTAR

---

## 6. ANALISIS DE LA ULTIMA VENTANA

Ventana mas reciente (ultima):
PF OOS ultima ventana: [valor]
PF OOS promedio: [valor]
Ratio ultima/promedio: [%]%

[ ] Ratio >= 80% → Normal — edge se mantiene
[ ] Ratio 60-80% → Precaucion — edge debilitandose
[ ] Ratio < 60% → ALERTA — edge posiblemente desapareciendo

DD OOS ultima ventana: [valor]%
[ ] DD OOS ultima <= 7% → OK
[ ] DD OOS ultima > 7% → REVISAR

---

## 7. CRITERIOS DE DESCARTE AUTOMATICO

Aplicar descarte sin pasar al humano si:

[ ] WFE < 30% → NO
[ ] 2 ventanas OOS negativas consecutivas → NO
[ ] DD OOS > 8% en alguna ventana → NO
[ ] PF OOS < 1.0 en la ultima ventana → NO

Descarte automatico aplicado: SI / NO
Si SI → razon: [explicar]

---

## 8. DICTAMEN FINAL

### Resumen de indicadores

| Indicador | Valor | Umbral | Estado |
|-----------|-------|--------|--------|
| WFE | [%]% | >= 50% | OK/ALERTA |
| Ventanas negativas | [N] | 0-1 | OK/ALERTA |
| DD OOS maximo | [%]% | <= 7% | OK/ALERTA |
| Estabilidad params | [nivel] | ESTABLE | OK/ALERTA |
| Ultima ventana | [%]% ratio | >= 80% | OK/ALERTA |

### Dictamen

[ ] ROBUSTA → PASA a aprobacion final
    WFE >= 50%, sin ventanas negativas,
    DD controlado, parametros estables.

[ ] ACEPTABLE CON RESERVAS → REVISAR
    WFE 40-50% o 1 ventana negativa aislada.
    Accion: reducir parametros optimizados
    y repetir WFO con rango mas estrecho.

[ ] INESTABLE → SIMPLIFICAR
    WFE < 40% o parametros erraticos.
    Accion: volver al Builder con hipotesis
    simplificada — menos condiciones.

[ ] DESCARTAR
    Criterios de descarte automatico cumplidos.
    Decision definitiva — cerrar ticket.

Dictamen seleccionado: [ROBUSTA/ACEPTABLE/INESTABLE/DESCARTAR]

Confianza: [X]/10

Justificacion:
[2-3 frases explicando el razonamiento]

---

## 9. ACCION SIGUIENTE

Si ROBUSTA o ACEPTABLE:
- Actualizar ticket current-phase.txt a
  "approval-pending"
- Invocar propfirm-analyst para recomendacion final
- Invocar funding-specialist para evaluacion final

Si INESTABLE o DESCARTAR:
- Documentar razon en gate-decisions.md del ticket
- Si INESTABLE: actualizar a "build-pending"
  y simplificar hipotesis con market-analyst
- Si DESCARTAR: mover ticket a archived\
  y estrategia a results\rejected\

---

## 10. PARAMETROS FINALES RECOMENDADOS

Si el dictamen es ROBUSTA o ACEPTABLE
documentar aqui los parametros optimos
para usar en produccion:

Parametro 1: [nombre] = [valor optimo]
Parametro 2: [nombre] = [valor optimo]
Parametro 3: [nombre] = [valor optimo] (si aplica)

Estos son los parametros que se exportaran
al EA de MT5 cuando se apruebe la estrategia.

---

Informe guardado en:
strategyquant\optimizer\[nombre]-WFO-dictamen.md