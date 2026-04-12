# INFORME COMPARATIVO IS vs OOS — Paso 12b

## Metadatos
Estrategia: [ID generado por SQ]
Activo: [simbolo]
Build numero: [N]
Ticket: [TICKET-ID]
Fecha del Retester: [fecha]
Fecha del informe: [fecha]
Generado por: sq-specialist
Solicitado por: orchestrator (paso 12b automatico)

---

## 1. CONFIGURACION VERIFICADA

### Builder (In-Sample)
Simbolo: [simbolo]
Temporalidad: H1
Periodo IS: 2003.05.05 a 2020.12.31
Comisiones: [segun activo — verificadas en CLAUDE.md]

### Retester (Out-of-Sample)
Simbolo: [mismo que Builder]
Temporalidad: H1
Periodo OOS: 2021.01.01 a [fecha actual]
Comisiones: [IDENTICAS al Builder]

Comisiones identicas Builder vs Retester: SI / NO
Si NO → INVALIDO — corregir antes de continuar

---

## 2. TABLA COMPARATIVA IS vs OOS

| Metrica | IS 2003-2020 | OOS 2021-actual | Variacion |
|---------|-------------|-----------------|-----------|
| Profit Factor | [valor] | [valor] | [%]% |
| Max Drawdown | [valor]% | [valor]% | [%]% |
| Trades totales | [numero] | [numero] | — |
| Trades por mes | [numero] | [numero] | [%]% |
| Win Rate | [valor]% | [valor]% | [%]% |
| Beneficio neto | [USD] | [USD] | [%]% |
| Ratio Rent/DD | [valor] | [valor] | [%]% |

---

## 3. CALCULO DE CAIDA DE PF

PF In-Sample: [valor]
PF Out-of-Sample: [valor]

Caida absoluta: [diferencia]
Caida porcentual: [%]%

Umbral de aprobacion: caida <= 20%
Umbral de descarte: PF OOS < 1.2

---

## 4. ANALISIS DE DD OOS

DD In-Sample: [valor]%
DD Out-of-Sample: [valor]%

Umbral de aprobacion: DD OOS <= 6.5%
Umbral de descarte: DD OOS > 7%

---

## 5. ANALISIS DE FRECUENCIA OOS

Trades/mes IS: [numero]
Trades/mes OOS: [numero]
Caida frecuencia: [%]%

Umbral de aprobacion: caida <= 40%
Umbral de descarte: caida > 50%

---

## 6. SEÑALES DE SOBREAJUSTE EN OOS

[ ] PF IS muy alto (>2.5) pero OOS muy bajo (<1.2) — SI/NO
[ ] Muchos trades IS pero muy pocos OOS — SI/NO
[ ] DD OOS mucho mayor que IS (>50% mas) — SI/NO
[ ] Comportamiento completamente distinto IS vs OOS — SI/NO

Señales activas: [numero]

---

## 7. DECISION AUTOMATICA PASO 12b

### Criterios aplicados

| Criterio | Valor | Umbral descarte | Umbral aprobacion | Resultado |
|----------|-------|-----------------|-------------------|-----------|
| PF OOS | [valor] | < 1.2 | >= 1.3 | PASA/DESCARTAR |
| Caida PF | [%]% | > 25% | <= 20% | PASA/DESCARTAR |
| DD OOS | [%]% | > 7% | <= 6.5% | PASA/DESCARTAR |
| Trades/mes OOS | [N] | < 5 | >= 6 | PASA/DESCARTAR |
| Caida frecuencia | [%]% | > 50% | <= 40% | PASA/DESCARTAR |

Criterios de descarte cumplidos: [N]
Si >= 1 → DESCARTAR automatico

Decision: CONTINUAR AL WFO / DESCARTAR

En el paso 12b NO hay zona intermedia.
O cumple → WFO. O no cumple → DESCARTAR.

Decidido por: orchestrator-auto
Intervencion humana: NO

---

## 8. ACCION SIGUIENTE

Si CONTINUAR:
- Actualizar ticket current-phase.txt a "optimizer-pending"
- sq-specialist configura WFO segun skill-optimizer.md
- Rangos estrechos centrados en valores del Builder

Si DESCARTAR:
- Mover estrategia a results\rejected\
- Documentar criterio exacto en gate-decisions.md
- Actualizar ticket a "rejected"

---

Informe guardado en:
strategyquant\retester\[ID]-IS-vs-OOS-report.md