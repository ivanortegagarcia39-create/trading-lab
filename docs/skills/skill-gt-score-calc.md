# Skill: GT-Score — Metrica Avanzada de Calidad

## Proposito
Calcula el GT-Score, una metrica compuesta que reemplaza
al PF como criterio principal de evaluacion cuando hay
suficiente historial de produccion real.
El PF puede ser engañoso en muestras cortas y con distribucion
desigual de trades. El GT-Score incorpora cuatro dimensiones
que el PF ignora: estabilidad temporal, robustez parametrica,
validacion multiactivo y calidad de ejecucion real.

Activo a partir de: Capa 3 del roadmap.
Antes de Capa 3: usar PF y criterios de skill-evaluation-auto.md.

---

## CUANDO ACTIVAR EL GT-SCORE

Requisitos para poder calcular el GT-Score:
- Al menos 3 estrategias con produccion real
- Cada estrategia con minimo 3 meses de produccion real
- Al menos 50 trades en produccion real por estrategia

Antes de cumplir estos requisitos usar el pipeline estandar
(EvalGate + Retester + WFO) sin GT-Score.
El GT-Score no reemplaza el pipeline — lo complementa
como capa adicional de validacion en produccion.

---

## LOS 4 COMPONENTES (25 puntos cada uno)

### Componente 1 — Consistencia Temporal (25 pts)

Mide si el PF es estable a lo largo de todos los años del IS.
Un PF promedio alto que esconde años muy malos es una señal
de sobreajuste a un regimen especifico.

Calculo:
  pf_anual = lista de PF por año en el IS
  consistencia = 1 - (desv_estandar(pf_anual) / media(pf_anual))
  score_1 = consistencia * 25

Penalizacion:
  Si algun año tiene PF < 1.0 → score_1 = min(score_1, 15)
  Razon: un año perdedor en el IS es señal de fragidad extrema.

Rango: 0-25 puntos. Ideal: >= 20 puntos.

### Componente 2 — Robustez Parametrica (25 pts)

Mide si la estrategia mantiene el edge cuando sus
parametros se perturban ligeramente (SPP ±10%).
Una estrategia robusta no colapsa con pequeñas variaciones.

Calculo:
  caida_media = media de las caidas de PF en las permutaciones
  score_2 = (1 - caida_media / 0.20) * 25
  (normalizado sobre una caida maxima aceptable del 20%)

Penalizacion:
  Si alguna permutacion individual cae > 30% → score_2 = min(score_2, 10)
  Razon: un parametro que destruye el sistema al cambiarse un 10%
  indica que la estrategia esta optimizada sobre ruido, no sobre edge.

Rango: 0-25 puntos. Ideal: >= 18 puntos.

Referencia: ver docs/skills/skill-spp-validation.md

### Componente 3 — Robustez Multiactivo (25 pts)

Mide si la estrategia funciona en activos correlacionados.
Si solo funciona en XAUUSD pero no en XAGUSD ni en indices,
puede ser que el edge sea especifico al ruido del XAUUSD
en el periodo IS.

Calculo:
  activos_probados = lista de activos donde se probo el backtest
  activos_con_pf_positivo = activos donde PF > 1.0
  score_3 = (activos_con_pf_positivo / activos_probados) * 25

Activos minimos a probar para calcular este componente:
  Si estrategia es en XAUUSD → probar tambien: XAGUSD, EUR/USD, GBP/USD
  Si estrategia es en Forex → probar tambien: 2 pares correlacionados

Rango: 0-25 puntos. Ideal: >= 15 puntos.
Si solo se probo en 1 activo: score_3 = 0 (sin datos suficientes).

### Componente 4 — Calidad de Ejecucion (25 pts)

Mide si la ejecucion real coincide con el backtest.
Un backtest excelente con ejecucion real terrible indica
que el modelo de backtest no era realista (slippage subestimado,
fill assumptions incorrectas).

En produccion real (Capa 3+):
  ratio_ejecucion = PF_produccion / PF_OOS_backtest
  score_4 = min(ratio_ejecucion, 1.0) * 25

En Capa 0-2 (sin historial de produccion suficiente):
  Usar estimacion basada en inflation-diagnostic.py:
  si inflation_score < 1.2 → score_4 estimado = 20 puntos
  si inflation_score 1.2-1.4 → score_4 estimado = 12 puntos
  si inflation_score > 1.4 → score_4 estimado = 5 puntos

Rango: 0-25 puntos. Ideal: >= 18 puntos.

---

## FORMULA FINAL

GT-Score = score_1 + score_2 + score_3 + score_4

Rango total: 0-100 puntos.

---

## UMBRAL DE APROBACION

| GT-Score | Clasificacion | Accion |
|----------|---------------|--------|
| >= 65    | ROBUSTO       | Continuar en portfolio activo |
| 50-64    | ACEPTABLE     | Revision en proxima sesion — monitoreo intensivo |
| < 50     | FRAGIL        | Descarte automatico del portfolio |

La misma logica de decision del pipeline aplica:
Si GT-Score < 50 → DESCARTAR sin consultar al humano.
Si GT-Score 50-64 → no descartar, pero aumentar frecuencia de revision.
Si GT-Score >= 65 → sin accion especial, continuar monitoreando.

---

## REGISTRO DEL GT-SCORE

Al calcular el GT-Score de una estrategia, registrar en
results/approved/[ID]-gt-score.json:

```json
{
  "estrategia_id": "XAUUSD-B10-1024-v1",
  "timestamp": "ISO-8601",
  "score_total": 72,
  "componentes": {
    "consistencia_temporal": 20,
    "robustez_parametrica": 18,
    "robustez_multiactivo": 15,
    "calidad_ejecucion": 19
  },
  "clasificacion": "ROBUSTO",
  "decision": "CONTINUAR"
}
```

---

## COMPARACION GT-SCORE vs PF

| Dimension | PF | GT-Score |
|-----------|-------|---------|
| Estabilidad temporal | No | Si |
| Robustez a perturbaciones | No | Si |
| Validacion en otros activos | No | Si |
| Calidad de ejecucion real | No | Si |
| Calculable desde Capa 0 | Si | Parcialmente |
| Requiere produccion real | No | Para comp. 4 |

El PF sigue siendo el criterio principal en Capa 0-2.
El GT-Score entra en Capa 3 como criterio complementario.
Nunca reemplaza el pipeline — lo refuerza.

---

## LO QUE ESTA SKILL NUNCA HACE

NUNCA usa el GT-Score para relajar los criterios del EvalGate.
NUNCA aprueba una estrategia con GT-Score < 50 aunque el PF sea alto.
NUNCA omite el componente 3 por falta de datos — asigna 0 puntos.
NUNCA aplica el GT-Score antes de tener 3 meses de produccion real
  para el componente 4 de produccion (usa estimacion, no dato real).
