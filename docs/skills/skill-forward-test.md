# Skill: Forward Test — Criterios Numericos Automaticos

## Proposito

Ultima validacion numerica antes del challenge real.
Verifica que la estrategia funciona en condiciones
de mercado actuales, no solo historicas.

Este skill define los criterios AUTOMATICOS del forward test.
El sistema decide si pasa o falla — no el humano.
La intervencion humana en el forward test es solo tecnica:
verificar que el EA ejecuta correctamente.
Ver skill-forward-test-protocol.md para la parte tecnica.

---

## DURACION

No hay limite de tiempo — hay limite de trades.
Minimo: 20 trades ejecutados en cuenta demo.
Sin ese minimo la muestra no es estadisticamente
suficiente para aplicar los 3 criterios.

Tiempo tipico para 20 trades en H1:
  Estrategia con 8 trades/mes → ~2.5 meses
  Estrategia con 15 trades/mes → ~1.5 meses
  Estrategia con 25 trades/mes → ~1 mes

No fijar un plazo de semanas — esperar los 20 trades.

---

## CRITERIOS DE PASA (los 3 deben cumplirse)

### Criterio 1 — PF produccion relativo

PF_demo >= 70% del PF_OOS del backtest

Ejemplo:
  PF OOS backtest: 1.50
  PF minimo en demo: 1.50 * 0.70 = 1.05

Razon del 70%: el mercado actual puede diferir del
periodo OOS. Una caida de hasta el 30% es aceptable
dado el ruido normal de una muestra pequena (20 trades).
Una caida mayor del 30% indica que el edge se ha
deteriorado o que el mercado ha cambiado estructuralmente.

### Criterio 2 — DD maximo en demo

DD_demo <= DD_OOS_backtest + 30%

Ejemplo:
  DD OOS backtest: 5.0%
  DD maximo aceptable en demo: 5.0% + 30% de 5.0% = 6.5%

Razon: el DD en produccion siempre es algo mayor que en
backtest debido a slippage real y spread variable.
Un DD hasta un 30% mayor es normal y esperado.
Un DD mas del 30% mayor indica condiciones adversas
o problema tecnico de ejecucion.

### Criterio 3 — Minimo de trades

Minimo 20 trades ejecutados en demo.

Sin este minimo los criterios 1 y 2 no son validos
estadisticamente. Esperar hasta los 20 trades antes
de aplicar los otros criterios.

---

## CRITERIO DE FALLA AUTOMATICA

Si cualquiera de los 3 criterios falla:
  1. La estrategia pasa a cola de reemplazo automaticamente.
  2. No se consulta al humano.
  3. No hay segunda oportunidad.
  4. El orchestrator registra el fallo en el audit trail.
  5. lessons-analyzer.py analiza el contexto del fallo.

El humano NO toma la decision de pasar/fallar.
Los numeros deciden.

---

## ACCOUNT INACTIVITY PROTECTION

Si la estrategia no genera trades en 15 dias consecutivos:
  → El performance-monitor genera una micro-verificacion.
  → Se verifica que el EA sigue activo y conectado.
  → Si el EA esta activo pero sin trades: mercado en baja
    volatilidad o sesion sin oportunidades. Normal.
  → Si el EA no esta activo: problema tecnico. CASO 2 al humano.

No se descarta la estrategia por inactividad — la inactividad
puede ser correcta si las condiciones de entrada no se dan.
Se descarta solo si los criterios numericos fallan.

---

## TRAS PASAR EL FORWARD TEST

El orchestrator ejecuta automaticamente los 5 pasos
del pre-challenge (skill-propfirm-challenge-execution.md):

1. Verificacion de compliance (propfirm-compliance-officer)
2. Score de salud de la firma (propfirm-health-monitor)
3. Verificacion de T&C (propfirm-regulatory-watcher)
4. Deteccion de conflictos (coordination-detector)
5. Generacion de la notificacion de compra con datos completos

Solo entonces se envia la solicitud de autorizacion al humano.
El humano solo responde SI o NO a la compra del challenge.

---

## REGISTRO DEL FORWARD TEST

Guardar en: results/approved/[ID]-forward-test-numericos.json

```json
{
  "estrategia_id": "[ID]",
  "fecha_inicio": "ISO-8601",
  "fecha_evaluacion": "ISO-8601",
  "trades_ejecutados": 20,
  "pf_demo": 1.12,
  "pf_oos_backtest": 1.50,
  "criterio_pf_70pct": 1.05,
  "criterio_1_pasa": true,
  "dd_demo": 5.8,
  "dd_oos_backtest": 5.0,
  "criterio_dd_max": 6.5,
  "criterio_2_pasa": true,
  "criterio_3_trades_pasa": true,
  "resultado": "PASA",
  "accion": "NOTIFICACION_CHALLENGE_GENERADA"
}
```

---

## LO QUE ESTA SKILL NUNCA HACE

NUNCA evalua si la estrategia gana o pierde dinero
  durante el forward test — eso ya lo decidio el pipeline.
NUNCA permite al humano decidir si pasa o falla
  basandose en el resultado economico del periodo demo.
NUNCA avanza con menos de 20 trades ejecutados.
NUNCA relaja los umbrales (70%, +30%) por "buen aspecto".
NUNCA descarta la estrategia por inactividad tecnica
  sin verificar que el EA sigue funcionando.
