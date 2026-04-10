# INFORME COMPARATIVO IS vs OOS — Paso 12b

## Metadatos
Estrategia: [nombre]
Ticket: [TICKET-ID]
Fecha del Retester: [fecha]
Fecha del informe: [fecha]
Generado por: sq-specialist
Solicitado por: orchestrator (paso 12b)

---

## 1. CONFIGURACION VERIFICADA

### Builder (In-Sample)
Simbolo: [simbolo]
Temporalidad: H1
Periodo IS: 2003.05.05 a 2020.12.31
Spread: 0.5 pips (EUR/USD) / 30 pips (XAU/USD)
Comision: 7 USD por lote
Slippage: 0.5 pips (EUR/USD) / 2 pips (XAU/USD)

### Retester (Out-of-Sample)
Simbolo: [mismo que Builder]
Temporalidad: H1
Periodo OOS: 2021.01.01 a [fecha actual]
Spread: [mismo que Builder]
Comision: [mismo que Builder]
Slippage: [mismo que Builder]

Comisiones identicas Builder vs Retester: SI / NO
Si NO → corregir antes de continuar

---

## 2. TABLA COMPARATIVA IS vs OOS

| Metrica | IS 2003-2020 | OOS 2021-actual | Variacion |
|---------|-------------|-----------------|-----------|
| Profit Factor | [valor] | [valor] | [%]% |
| Max Drawdown | [valor]% | [valor]% | [%]% |
| Trades totales | [numero] | [numero] | - |
| Trades por mes | [numero] | [numero] | [%]% |
| Win Rate | [valor]% | [valor]% | [%]% |
| Beneficio neto | [USD] | [USD] | [%]% |
| Ratio Rent/DD | [valor] | [valor] | [%]% |

---

## 3. CALCULO DE CAIDA DE PF

PF In-Sample: [valor]
PF Out-of-Sample: [valor]

Caida absoluta: [PF IS] - [PF OOS] = [diferencia]
Caida porcentual: ([diferencia] / [PF IS]) x 100 = [%]%

Umbral critico: 20% de caida
Umbral de descarte: PF OOS < 1.3

Resultado:
[ ] Caida <= 20% y PF OOS >= 1.3 → CONTINUAR al WFO
[ ] Caida > 20% → REVISAR (posible sobreajuste)
[ ] PF OOS < 1.3 → DESCARTAR automatico

---

## 4. ANALISIS DE DD OOS

DD In-Sample: [valor]%
DD Out-of-Sample: [valor]%

Variacion DD: [%]%
Umbral operativo DD OOS: 7%
Umbral de revision: 6.5%

Resultado:
[ ] DD OOS <= 6.5% → DENTRO del limite operativo
[ ] DD OOS entre 6.5% y 7% → REVISAR con cautela
[ ] DD OOS > 7% → REVISAR obligatorio
[ ] DD OOS > 8% → DESCARTAR automatico

---

## 5. ANALISIS DE CONSISTENCIA OOS

Trades generados en periodo OOS: [numero]
Periodo OOS cubre: [X] meses aproximadamente
Trades por mes en OOS: [numero]

Comparativa frecuencia IS vs OOS:
Trades/mes IS: [numero]
Trades/mes OOS: [numero]
Diferencia: [%]%

Si la frecuencia cae mas del 50% en OOS
la estrategia puede no generar suficientes
trades para cumplir los dias minimos de FTMO.

[ ] Frecuencia OOS aceptable (>= 10 trades/mes)
[ ] Frecuencia OOS baja (5-10 trades/mes) — precaucion
[ ] Frecuencia OOS muy baja (< 5 trades/mes) — REVISAR

---

## 6. SEÑALES DE CURVE-FITTING EN OOS

[ ] PF IS muy alto (>2.5) pero OOS muy bajo (<1.2)
    → NO detectado
[ ] Muchos trades IS pero muy pocos OOS
    → NO detectado
[ ] DD OOS mucho mayor que IS (>50% mas)
    → NO detectado
[ ] Comportamiento completamente distinto IS vs OOS
    → NO detectado

Señales activas: [numero]
Si 2 o mas señales → probable sobreajuste

---

## 7. DECISION DEL PASO 12b

### Criterios automaticos aplicados

PF OOS: [valor]
Caida de PF: [%]%
DD OOS: [valor]%

[ ] PF OOS < 1.3 → DESCARTAR automatico
    (no necesita confirmacion humana)

[ ] Caida PF > 20% → REVISAR
    Accion: simplificar hipotesis y relanzar Builder

[ ] DD OOS > 6.5% → REVISAR
    Accion: revisar gestion del dinero o SL

[ ] Todo dentro de limites → CONTINUAR al WFO

### Decision final del paso 12b

Decision: CONTINUAR / REVISAR / DESCARTAR

Razon: [explicacion breve]

Decidido por: orchestrator-auto / humano

---

## 8. ACCION SIGUIENTE

Si CONTINUAR:
- Actualizar ticket current-phase.txt a
  "optimizer-pending"
- El sq-specialist configura el WFO
- Leer skill-wfo-interpretation.md antes del WFO

Si REVISAR:
- Documentar que aspecto revisar concretamente
- Actualizar ticket current-phase.txt a
  "build-pending"
- Invocar market-analyst o sq-specialist segun
  si el problema es la hipotesis o la configuracion

Si DESCARTAR:
- Mover estrategia a results\rejected\
- Documentar razon en gate-decisions.md del ticket
- Mover ticket a research\active-tickets\archived\
- Actualizar current-phase.txt a "rejected"

---

Informe guardado en:
strategyquant\retester\[nombre]-IS-vs-OOS-report.md