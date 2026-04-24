# Skill: Market Impact Simulator — Reactive Simulation

## Proposito
Validar que una estrategia aprobada es escalable a los
lotes reales de una cuenta fondeada sin que el impacto
de mercado destruya el edge.

El problema central: los backtests asumen ejecucion perfecta
al precio exacto. En realidad, los lotes grandes mueven el
precio en contra del trader antes de que la orden se ejecute.
Una estrategia con 0.01 lotes puede ser excelente.
La misma estrategia con 1.0 lote puede ser perdedora.

Este simulador recalcula el PF con el slippage adicional
derivado del tamaño real de los lotes en produccion.

---

## EL PROBLEMA DEL MARKET IMPACT

### Por que el backtest miente a escala

En un backtest con 0.01 lotes (cuenta de demo o test):
  - El EA compra XAUUSD a exactamente el precio de mercado.
  - No hay competencia con otros ordenes.
  - El fill es instantaneo al precio exacto.

En produccion con 1.0 lote (cuenta de 25k USD):
  - La orden entra al mercado y mueve el precio ligeramente.
  - El slippage adicional es proporcional al tamaño de la orden.
  - En momentos de baja liquidez el efecto se amplifica.

Ejemplo:
  Estrategia en XAUUSD con 500 trades en backtest.
  Cada trade: entry + exit = 2 eventos de ejecucion.
  Con 1.0 lote: +0.5 pips por evento = +1.0 pip por trade.
  Sobre 500 trades en cuenta de 25k: slippage adicional = 500 USD.
  Si el profit bruto del backtest era 2.000 USD → queda 1.500 USD.
  PF original: 1.50 → PF ajustado: ~1.30 (caida del 13%).

---

## FACTORES DE IMPACTO POR ACTIVO

El factor de impacto mide los pips adicionales de slippage
por cada 0.1 lote por encima del lote base de referencia (0.1).

| Activo | Factor impacto | Unidad | Nota |
|--------|---------------|--------|------|
| XAUUSD | 0.5 pips / 0.1 lote adicional | pips (0.01 USD/oz) | Alta liquidez pero spread amplio |
| XAGUSD | 0.8 pips / 0.1 lote adicional | pips | Menos liquido que Oro |
| EURUSD | 0.2 pips / 0.1 lote adicional | pips | Mayor liquidez FX |
| GBPUSD | 0.3 pips / 0.1 lote adicional | pips | |
| USDJPY | 0.2 pips / 0.1 lote adicional | pips | |
| Otros Forex Majors | 0.3 pips / 0.1 lote | pips | Usar como referencia |
| Forex Crosses | 0.5 pips / 0.1 lote | pips | Menor liquidez |
| US30 (Dow) | 1.0 pto / 0.1 lote | puntos del indice | |
| US500 (S&P) | 0.5 pto / 0.1 lote | puntos del indice | |
| NAS100 | 1.5 pto / 0.1 lote | puntos del indice | Volatilidad alta |
| BTC/USD | 5.0 USD / 0.1 lote | USD | Spread y liquidez variables |

Nota: estos factores son estimaciones conservadoras basadas en
condiciones normales de mercado. En apertura de sesion o noticias
el impacto puede ser 2-3x mayor.

---

## CALCULO DEL MARKET IMPACT

Para cada trade del backtest:

```
lote_real = capital * (riesgo_pct / 100) / (SL_pips * valor_pip)
lotes_adicionales = max(0, lote_real - 0.1) / 0.1
slippage_adicional_pips = lotes_adicionales * factor_impacto

nuevo_entry = entry + slippage_adicional_pips  (para buy)
nuevo_entry = entry - slippage_adicional_pips  (para sell)
nuevo_exit  = exit  - slippage_adicional_pips  (para buy)
nuevo_exit  = exit  + slippage_adicional_pips  (para sell)
```

Recalcular el profit de cada trade con los nuevos precios.
Recalcular PF total como suma(profits positivos) / suma(losses absolutos).

---

## CRITERIOS DE EVALUACION

| Caida de PF | Clasificacion | Accion |
|-------------|---------------|--------|
| < 5%        | ESCALABLE     | Sin restriccion — estrategia robusta a escala |
| 5-15%       | ADVERTENCIA   | Nota en informe de exportacion — monitorear slippage real |
| > 15%       | DESCARTE      | No lanzar challenge con esta estrategia en cuenta grande |

### Logica de la penalizacion del 15%

Si el PF cae mas del 15% al simular con lotes reales:
el edge que el backtest mostrava no sobrevive a la ejecucion real.
Esto indica que la estrategia depende de fills perfectos que
no son reproducibles en produccion.

Una caida del 5-15% es normal y esperada — ningun backtest
es perfecto. Una caida > 15% es señal de que el modelo
de costes del Builder estaba subestimando el impacto real.

---

## CUANDO EJECUTAR

Ejecutar la simulacion antes del primer challenge real:
- Despues de que la estrategia pase el WFO.
- Antes de que export-specialist prepare el EA para MT5.
- Una vez por estrategia — no necesario repetir en cada revision.

Si la cuenta escala (de 10k a 12.5k a 25k...):
repetir la simulacion con el nuevo lote real para verificar
que el impact sigue siendo < 15%.

---

## INTEGRACION CON EL PIPELINE

El export-specialist ejecuta esta simulacion como
Paso 0c (despues del Paso 0b — test unitario en MT5):

```
Paso 0a: mql5-auditor.py → APPROVE/REJECT
Paso 0b: backtest de verificacion 1 mes MT5
Paso 0c: Market Impact Simulation → ESCALABLE/ADVERTENCIA/DESCARTE
Paso 1+: configuracion y forward test en demo
```

Si el resultado es DESCARTE: la estrategia no avanza.
Se registra en el audit trail con los valores exactos de caida de PF.

Si el resultado es ADVERTENCIA: avanza con nota en el informe.
El export-specialist documenta la caida esperada en el informe de exportacion.

---

## REGISTRO DE LA SIMULACION

Guardar en results/approved/[ID]-market-impact.json:

```json
{
  "estrategia_id": "XAUUSD-B10-1024-v1",
  "timestamp": "ISO-8601",
  "capital_simulado": 25000,
  "lote_real_estimado": 0.5,
  "pf_original": 1.52,
  "pf_ajustado": 1.41,
  "caida_pct": 7.2,
  "clasificacion": "ADVERTENCIA",
  "factor_impacto_usado": 0.5,
  "activo": "XAUUSD",
  "accion": "AVANZA con nota — monitorear slippage real en forward test"
}
```

---

## LO QUE ESTA SKILL NUNCA HACE

NUNCA omite esta simulacion en cuentas >= 25k.
NUNCA acepta una caida > 15% como "dentro de lo normal".
NUNCA usa factores de impacto menores a los definidos en la tabla.
NUNCA ejecuta esta simulacion con datos OOS — solo con datos del IS backtest.
NUNCA reemplaza el forward test demo — lo complementa como filtro previo.
