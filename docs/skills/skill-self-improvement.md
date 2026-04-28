# Skill: Self-Improvement System

## Propósito

TradingLab aprende de sus propios resultados y mejora continuamente
sin intervención humana. Dos mecanismos trabajan en paralelo:

1. **DSPy Optimizer** — optimiza cómo el sistema razona y comunica
2. **Bayesian Criteria Updater** — optimiza qué umbrales numéricos usa el pipeline
3. **Self-Improvement Engine** — orquesta ambos cada semana

---

## Componentes

### 1. DSPy Optimizer (`scripts/dspy-optimizer.py`)

En lugar de prompts escritos a mano, DSPy aprende de ejemplos reales
y reescribe los prompts para que sean más efectivos.

**Módulos:**

| Módulo | Signature | Optimiza contra |
|---|---|---|
| StrategyEvaluator | strategy_metrics → evaluation_verdict | Resultados reales del EvalGate |
| LessonSynthesizer | build_failures → structural_lesson | Lecciones que resultaron válidas |
| BuildAnalyzer | build_stats → analysis_report | Análisis que fueron más útiles |

**Flujo:**
```
Resultado real → add_training_example() → acumular ≥10 → compile_module()
→ Prompt compilado guardado en config/dspy-compiled/
→ Pipeline usa prompt optimizado automáticamente
```

**Comandos:**
```bash
python scripts/dspy-optimizer.py --list               # módulos disponibles
python scripts/dspy-optimizer.py --stats              # estado de entrenamiento
python scripts/dspy-optimizer.py --compile StrategyEvaluator
python scripts/dspy-optimizer.py --add-example StrategyEvaluator '{"pf":1.8}' '{"verdict":"PASA"}' 0.9
```

**Instalación:** `pip install dspy-ai`

---

### 2. Bayesian Criteria Updater (`scripts/bayesian-criteria-updater.py`)

Cada umbral del pipeline tiene un prior Beta(α, β) que se actualiza
con cada decisión real del pipeline.

**Modelo:**
- α = veces que el criterio acertó (verdadero positivo/negativo)
- β = veces que el criterio falló (falso positivo/negativo)
- Umbral operativo = percentil 25 del posterior (conservador)

**Criterios modelados:**

| Criterio | Valor inicial | Rango permitido |
|---|---|---|
| pf_minimo_evalgate | 1.5 | [1.3, 2.0] |
| dd_maximo_evalgate | 7.0% | [5.0%, 10.0%] |
| sharpe_minimo_oos | 0.5 | [0.3, 1.5] |
| wfe_minimo | 50% | [40%, 70%] |
| pf_forward_test_ratio | 0.70 | [0.50, 0.90] |

**Outcomes posibles:**
- `true_positive` — criterio pasó la estrategia y la estrategia fue rentable
- `false_positive` — criterio pasó la estrategia pero falló en producción
- `true_negative` — criterio descartó la estrategia correctamente
- `false_negative` — criterio descartó la estrategia pero habría sido buena

**Comandos:**
```bash
python scripts/bayesian-criteria-updater.py --thresholds
python scripts/bayesian-criteria-updater.py --report
python scripts/bayesian-criteria-updater.py --update pf_minimo_evalgate true_positive
python scripts/bayesian-criteria-updater.py --reset pf_minimo_evalgate
```

---

### 3. Self-Improvement Engine (`scripts/self-improvement-engine.py`)

Orquestador semanal que ejecuta el ciclo completo.

**Ciclo (7 pasos):**
1. Leer audit trail de la última semana
2. Procesar decisiones del pipeline → updates bayesianos + ejemplos DSPy
3. Verificar estado de compilación DSPy
4. Recompilar módulos DSPy si ≥10 ejemplos
5. Verificar criterios que necesitan recalibración
6. Generar informe de mejoras aplicadas
7. Notificar via Telegram + registrar en Knowledge Graph

**Comandos:**
```bash
python scripts/self-improvement-engine.py --run       # ciclo completo
python scripts/self-improvement-engine.py --dry-run   # simular
python scripts/self-improvement-engine.py --report    # historial
```

---

## Ciclo completo de autoaprendizaje

```
Resultado real del pipeline
        ↓
┌─────────────────────────────────┐
│ Bayesian Updating               │
│ Umbral ajustado ±conservador    │
└────────────────┬────────────────┘
                 ↓
┌─────────────────────────────────┐
│ DSPy Training Example           │
│ Input + Output + Score          │
└────────────────┬────────────────┘
                 ↓ (≥10 ejemplos)
┌─────────────────────────────────┐
│ DSPy Compilation                │
│ Prompt optimizado automático    │
└────────────────┬────────────────┘
                 ↓
┌─────────────────────────────────┐
│ Pipeline mejorado               │
│ Mejores decisiones → mejores    │
│ resultados → más aprendizaje    │
└─────────────────────────────────┘
```

---

## Garantías de seguridad

**Bayesian:**
- Nunca recalibra fuera de [min_absoluto, max_absoluto]
- Nunca recalibra con menos de 5 observaciones reales
- Nunca recalibra más del 10% en una sola actualización
- Todo cambio queda en `config/bayesian-audit-trail.jsonl`

**Criterios invariables (no modelados bayesianamente):**
- PF mínimo pipeline general ≥ 1.3 (límite absoluto)
- DD máximo portfolio ≤ 12%
- Catastrophic Veto WFO (nunca se relaja)
- Ratio TP/SL mínimo 2:1
- Forward test demo obligatorio antes del challenge

**DSPy:**
- Mínimo 10 ejemplos antes de compilar
- El prompt base funciona siempre como fallback
- Los prompts compilados se versionan por módulo

---

## Estado y archivos

| Archivo | Contenido |
|---|---|
| `config/bayesian-criteria.json` | Estado actual de todos los criterios |
| `config/bayesian-audit-trail.jsonl` | Historial completo de cambios |
| `config/dspy-training/*.jsonl` | Ejemplos de entrenamiento por módulo |
| `config/dspy-compiled/*.json` | Prompts compilados por módulo |
| `config/self-improvement-log.jsonl` | Historial de ciclos semanales |

Estos archivos no se versionan en git (datos locales del sistema).
