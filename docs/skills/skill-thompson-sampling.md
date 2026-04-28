# Skill: Thompson Sampling

## Propósito

En lugar de elegir el próximo activo a buildear manualmente o por un scoring
fijo, el sistema aprende qué activos y timeframes producen las mejores
estrategias y los prioriza automáticamente.

---

## Cómo funciona

Cada par (activo, timeframe) tiene una distribución **Beta(α, β)** que
representa la "creencia" del sistema sobre la calidad del activo.

```
α = número de builds exitosos (≥1 estrategia con PF > 1.5 en WFO)
β = número de builds fallidos
```

Con cada build:
- Sale bien → α += 1 → el activo sube en el ranking
- Sale mal  → β += 1 → el activo baja en el ranking

Al principio (sin datos): todos los activos tienen Beta(1, 1) = uniforme
→ exploración amplia, todos son igualmente probables.

Con datos: los activos con mejor track record tienen media posterior mayor
→ el sistema los prioriza sin que el humano decida.

---

## Balance Exploración / Explotación

Thompson Sampling resuelve automáticamente el dilema:

- **Explorar**: probar activos nuevos o poco conocidos
- **Explotar**: repetir lo que ya funciona

No es necesario decidir manualmente cuándo explorar vs explotar.
El muestreo aleatorio de la distribución Beta hace que activos
con alta incertidumbre (pocos builds) sigan siendo elegibles,
pero los activos con buen track record son elegidos más a menudo.

---

## Selección del próximo activo

En cada llamada a `--next-asset`:
1. Para cada activo disponible, se muestrea un valor de su Beta(α, β)
2. El activo con mayor muestra gana
3. Si hay menos de 3 builds en cualquier activo → modo FIFO (sin Thompson aún)

```bash
# Sugerir próximo activo
python scripts/thompson-sampling.py --next-asset

# Excluir activos en curso
python scripts/thompson-sampling.py --next-asset --exclude XAUUSD EURUSD
```

---

## Allocation de portfolio

Las mismas distribuciones Beta se usan para las estrategias activas:

```
α = semanas con PF >= PF_OOS_backtest
β = semanas con PF <  PF_OOS_backtest
```

El peso de cada estrategia en el portfolio es proporcional a su muestra Beta.
Las estrategias que cumplen consistentemente sus expectativas reciben más peso.

```bash
# Ver allocations sugeridas
python scripts/thompson-sampling.py --allocations STRAT001 STRAT002 STRAT003
```

---

## Rankings y comandos

```bash
# Ver ranking de todos los activos por media posterior
python scripts/thompson-sampling.py --rankings

# Actualizar después de un build
python scripts/thompson-sampling.py --update-asset XAUUSD H1 true   # build exitoso
python scripts/thompson-sampling.py --update-asset EURUSD H1 false  # build fallido

# Actualizar resultado semanal de estrategia
python scripts/thompson-sampling.py --update-strategy STRAT001 true
```

---

## Integración con el pipeline

### Build Queue Manager
Cuando se ejecuta `python scripts/build-queue-manager.py next`:
- Si hay >= 3 builds por algún activo → usa Thompson para sugerir el próximo
- Si hay < 3 builds → usa el orden FIFO de la cola

### Self-Improvement Engine (paso 2f)
Cada semana el ciclo de autoaprendizaje actualiza Thompson con los builds
completados en la semana. Esto mantiene el modelo al día automáticamente.

### Criterio de éxito de un build
Un build se considera **exitoso** si produce al menos 1 estrategia que:
- PF > 1.5 en WFO OOS
- DD < 7% en WFO OOS
- Pasa el Evaluation Gate automático

---

## Estado y archivos

| Archivo | Contenido |
|---|---|
| `results/thompson-state.json` | α y β por activo y por estrategia |

El archivo se crea automáticamente en el primer uso.
Contiene los 24 activos del universo de TradingLab, todos inicializados
con Beta(1, 1) — prior no informativo (todos igualmente probables).

---

## Garantías

- Con menos de 3 builds no cambia el orden de la cola (sin sesgo prematuro)
- El prior Beta(1, 1) garantiza que todos los activos son explorados
- Los activos con muchos fallos tienen β alto pero siguen siendo elegibles
  ocasionalmente (exploración garantizada)
- El humano puede seguir añadiendo activos a la cola manualmente;
  Thompson solo reordena la sugerencia, no bloquea ninguna elección
