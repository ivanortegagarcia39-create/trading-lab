# Skill: Monte Carlo en TradingLab

## Proposito
Monte Carlo aleatoriza el orden y/o los valores de los trades
para verificar que la estrategia no depende de una secuencia
especifica de eventos.
Una estrategia robusta debe mantener su edge independientemente
del orden en que ocurran los trades.

---

## TRES USOS EN EL PROYECTO

### 1. Monte Carlo en SQ (Retester)
**Cuando:** Paso 12b — analisis OOS, despues del EvalGate.
**Que hace:** SQ aleatoriza el orden de los trades del backtest
en el periodo IS para verificar estabilidad estadistica.
**No usar en el Builder** — ralentiza demasiado la generacion
de candidatas y no tiene sentido con datos parciales.

Configuracion en SQ Retester:
- Simulaciones: 200
- Nivel de confianza: 95%
- Aleatorizar: orden de trades (no los PnLs individuales)
- Resultado: curva de equidad en percentiles 5/50/95

**Criterio de aprobacion:**
La estrategia debe mantener PF > 1.0 en al menos el 95%
de las simulaciones. Si el percentil 5 tiene PF < 1.0,
la estrategia es estadisticamente fragil — DESCARTAR.

### 2. Monte Carlo pre-challenge (challenge-simulator.py)
**Cuando:** Antes de comprar el challenge, despues del forward test.
**Que hace:** Simula 1000 variaciones del challenge completo
usando los trades del forward test con orden aleatorio.
Aplica las reglas FTMO exactas (DD diario 5%, DD total 10%,
objetivo 10%, minimo 4 dias de trading).

```bash
python scripts/challenge-simulator.py \
    --strategy-csv forward-test-trades.csv \
    --capital 25000 \
    --simulations 1000
```

Output: `results/challenge-simulation-[ID].json`

**Criterio de aprobacion:**
- Probabilidad de exito >= 70% → PROCEDER con el challenge
- Probabilidad 50-70% → REVISION — ajustar tamaño de cuenta
- Probabilidad < 50% → NO PROCEDER — forward test insuficiente

La cuenta recomendada es la que maximiza la probabilidad de exito.
Generalmente una cuenta mayor (50k) da mas margen de DD absoluto.

### 3. Monte Carlo de correlacion (escenario de crisis)
**Cuando:** Revision mensual del portfolio en produccion.
**Que hace:** Simula el escenario extremo en que todas las
correlaciones del portfolio colapsan a 1.0 — el peor caso posible
donde todas las estrategias pierden al mismo tiempo.

Calculo:
```
dd_individual_max = mayor DD registrado en OOS de cada estrategia
dd_crisis_simulado = suma(dd_individual_max) para todas las activas
```

**Criterio de aprobacion:**
DD simulado en crisis < 20% del capital.
Si supera el 20%, reducir numero de estrategias o revisar
la diversificacion por activo (skill-correlation-analysis.md).

---

## CUANDO NO USAR MONTE CARLO

| Momento | Razon |
|---------|-------|
| En el Builder | Ralentiza x10 la generacion — no tiene sentido con candidatas no evaluadas |
| En el EvalGate Python | Sin modelo completo de trades no hay significacion estadistica |
| En la seleccion de portfolio | La correlacion ya captura la dependencia — MC no añade informacion adicional |
| Con menos de 30 trades | Muestra insuficiente — el resultado no es estadisticamente significativo |

---

## INTERPRETACION DE RESULTADOS SQ

### Distribucion de resultados Monte Carlo en SQ

| Percentil | Interpretacion |
|-----------|---------------|
| P95 (mejor 5%) | Escenario favorable — no planificar sobre este |
| P50 (mediana) | Expectativa realista de la estrategia |
| P5 (peor 5%) | Escenario adverso — verificar que PF > 1.0 aqui |

Una estrategia robusta tiene la mediana (P50) con PF similar
al backtest original. Si P50 cae mas del 15% respecto al PF
del backtest, el edge puede ser fragil.

### Señales de alerta en Monte Carlo SQ

- **P5 con PF < 1.0:** estrategia estadisticamente fragil — DESCARTAR
- **Diferencia P95 - P5 > 0.5 en PF:** alta varianza — el resultado
  depende demasiado de la secuencia de trades
- **Mediana PF < 80% del PF del backtest:** el backtest puede estar
  sobreajustado a una secuencia especifica de eventos

---

## INTERPRETACION DE RESULTADOS challenge-simulator.py

### Campos del output JSON

```json
{
  "probabilidad_exito_pct": 78.5,
  "dias_estimados": 12,
  "trades_peligrosos": [...],
  "cuenta_recomendada": "25000",
  "cuenta_recomendada_prob": 82.1,
  "cuenta_por_tamaño": {
    "10000": 71.3,
    "25000": 82.1,
    "50000": 85.4,
    "100000": 87.2
  }
}
```

### Logica de recomendacion de cuenta

Una cuenta mayor da mas margen absoluto en USD para el DD diario
y total, lo que reduce la probabilidad de violar los limites FTMO.
Sin embargo, el coste del challenge tambien es mayor.

La cuenta optima es aquella donde el incremento marginal
de probabilidad ya no justifica el coste adicional del challenge.
Regla practica: si la diferencia entre 25k y 50k es < 5 puntos
de probabilidad, usar 25k.

---

## RELACION CON OTROS SKILLS

- `skill-evaluation-auto.md` — define cuando activar Monte Carlo SQ
- `skill-retester.md` — configuracion de Monte Carlo en SQ Retester
- `skill-stress-test.md` — complemento: test en periodos de crisis reales
- `skill-portfolio-selection.md` — Monte Carlo de correlacion en crisis
- `skill-ftmo-rules.md` — reglas exactas que simula challenge-simulator.py
