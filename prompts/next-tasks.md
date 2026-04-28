Lee CLAUDE.md y todos los archivos en agents/ y docs/skills/.

Vamos a implementar P2.1 DSPy y P2.2 Bayesian Updating.
Estos dos sistemas hacen que TradingLab aprenda solo
y mejore continuamente sin intervención humana.

TAREA 1 - Crear scripts/dspy-optimizer.py
Sistema de auto-optimización de prompts con DSPy.
DSPy compila prompts automáticamente basándose en
ejemplos reales de input/output del sistema.

INSTALACIÓN: pip install dspy-ai

PROPÓSITO:
En lugar de prompts escritos a mano que nunca cambian,
DSPy aprende de los resultados reales del pipeline
y reescribe los prompts para que sean más efectivos.

MÓDULOS DSPy A IMPLEMENTAR:

Módulo 1 — StrategyEvaluator:
  Signature: strategy_metrics -> evaluation_verdict
  Input: PF, DD, trades, win_rate, sharpe, regime
  Output: PASA/DESCARTAR + justificación
  Optimizar contra: resultados reales del EvalGate

Módulo 2 — LessonSynthesizer:
  Signature: build_failures -> structural_lesson
  Input: lista de fallos con contexto
  Output: lección estructural con recomendación
  Optimizar contra: lecciones que resultaron válidas

Módulo 3 — BuildAnalyzer:
  Signature: build_stats -> analysis_report
  Input: estadísticas del build
  Output: análisis ejecutivo + próximos pasos
  Optimizar contra: análisis que fueron más útiles

FUNCIONES PRINCIPALES:

compile_module(module_name, training_examples):
  Carga el módulo DSPy correspondiente
  Usa los ejemplos de entrenamiento para compilar
  Guarda el prompt compilado en config/dspy-compiled/
  Requiere mínimo 10 ejemplos para compilar

load_compiled_module(module_name):
  Carga el prompt compilado si existe
  Si no existe → usa el prompt base por defecto

add_training_example(module_name, input_data, output_data, score):
  Añade un ejemplo al dataset de entrenamiento
  score: 0.0-1.0 (qué tan bueno fue el output real)
  Guarda en config/dspy-training/[module_name].jsonl

get_training_stats():
  Muestra cuántos ejemplos tiene cada módulo
  Cuándo fue la última compilación
  Si hay suficientes ejemplos para recompilar (>=10)

ARGUMENTOS CLI:
--compile MODULE_NAME: compilar un módulo
--stats: ver estado de entrenamiento
--add-example: añadir ejemplo manualmente
--list: listar módulos disponibles

TAREA 2 - Crear scripts/bayesian-criteria-updater.py
Sistema de actualización bayesiana de criterios del pipeline.
Cada umbral del pipeline se trata como una variable
con un prior y se actualiza con resultados reales.

MODELO BAYESIANO:
Para cada criterio del pipeline:
  Prior: distribución Beta(α, β) sobre la efectividad
  α = número de veces que el criterio acertó (verdadero positivo)
  β = número de veces que el criterio falló (falso positivo/negativo)
  Umbral operativo = percentil 25 del posterior (conservador)

CRITERIOS MODELADOS:
{
  "pf_minimo_evalgate": {
    "valor_inicial": 1.5,
    "alpha": 1, "beta": 1,
    "min_absoluto": 1.3,
    "max_absoluto": 2.0,
    "descripcion": "PF mínimo en EvalGate"
  },
  "dd_maximo_evalgate": {
    "valor_inicial": 7.0,
    "alpha": 1, "beta": 1,
    "min_absoluto": 5.0,
    "max_absoluto": 10.0,
    "descripcion": "DD máximo en EvalGate"
  },
  "sharpe_minimo_oos": {
    "valor_inicial": 0.5,
    "alpha": 1, "beta": 1,
    "min_absoluto": 0.3,
    "max_absoluto": 1.5,
    "descripcion": "Sharpe mínimo en OOS"
  },
  "wfe_minimo": {
    "valor_inicial": 50.0,
    "alpha": 1, "beta": 1,
    "min_absoluto": 40.0,
    "max_absoluto": 70.0,
    "descripcion": "WFE mínimo en WFO"
  },
  "pf_forward_test_ratio": {
    "valor_inicial": 0.70,
    "alpha": 1, "beta": 1,
    "min_absoluto": 0.50,
    "max_absoluto": 0.90,
    "descripcion": "Ratio PF forward test vs backtest"
  }
}

FUNCIONES PRINCIPALES:

update_criterion(criterion_name, outcome):
  outcome: "true_positive", "false_positive",
           "true_negative", "false_negative"
  Actualiza α o β según el outcome
  Recalcula el umbral operativo
  Registra el cambio en el audit trail

get_current_thresholds():
  Devuelve los umbrales actuales de todos los criterios
  Incluye: valor actual, valor inicial, confianza (α+β)

check_for_recalibration():
  Si algún criterio tiene confianza baja (α+β < 10):
    No recalibrar — poco datos
  Si tiene confianza media (10-50):
    Recalibrar si el cambio propuesto es > 5%
  Si tiene confianza alta (>50):
    Recalibrar si el cambio propuesto es > 2%

generate_calibration_report():
  Para cada criterio mostrar:
  - Valor inicial vs valor actual
  - Número de observaciones
  - Confianza en el nuevo valor
  - Dirección del cambio (más estricto/más permisivo)

REGLAS DE SEGURIDAD INVARIABLES:
Nunca recalibrar fuera de [min_absoluto, max_absoluto]
Nunca recalibrar con menos de 5 observaciones
Nunca recalibrar más de 10% en una sola actualización
Registrar TODOS los cambios en el audit trail

Guardar estado en config/bayesian-criteria.json

ARGUMENTOS CLI:
--update CRITERIO OUTCOME: actualizar un criterio
--report: ver reporte de calibración
--thresholds: ver umbrales actuales
--reset CRITERIO: resetear al valor inicial

TAREA 3 - Crear scripts/self-improvement-engine.py
Script orquestador que coordina DSPy y Bayesian updating
para ejecutar el ciclo completo de autoaprendizaje.

CICLO DE AUTOAPRENDIZAJE (ejecutar semanalmente):
1. Leer resultados del audit trail de la última semana
2. Para cada decisión del pipeline con outcome conocido:
   a. Actualizar criterio bayesiano correspondiente
   b. Añadir ejemplo de entrenamiento a DSPy
3. Verificar si hay suficientes ejemplos para recompilar
4. Si sí: recompilar módulos DSPy
5. Verificar si hay criterios que necesitan recalibración
6. Generar informe de mejoras aplicadas
7. Enviar resumen via Telegram
8. Registrar ciclo en Knowledge Graph

ARGUMENTOS:
--run: ejecutar ciclo completo
--dry-run: simular sin aplicar cambios
--report: solo ver informe sin ejecutar

TAREA 4 - Crear docs/skills/skill-self-improvement.md
Documenta el sistema de autoaprendizaje:

COMPONENTES:
1. DSPy: optimiza cómo el sistema comunica y razona
2. Bayesian Updating: optimiza qué umbrales usa el sistema
3. Self-Improvement Engine: orquesta ambos semanalmente

CICLO COMPLETO:
Resultado real → Actualización bayesiana → Recompilación DSPy
→ Pipeline mejorado → Mejor resultado → ...

GARANTÍAS DE SEGURIDAD:
- Nunca cambia criterios críticos sin suficiente evidencia
- Siempre registra cada cambio en el audit trail
- Siempre puede hacer rollback al estado anterior
- Nunca relaja: PF mínimo, DD máximo, Catastrophic Veto WFO

TAREA 5 - Actualizar .gitignore y config
Añadir al .gitignore:
  config/dspy-compiled/
  config/dspy-training/
  config/bayesian-criteria.json

Crear config/bayesian-criteria.json con los valores
iniciales de todos los criterios documentados arriba.

Al terminar:
git add .
git commit -m "Autoaprendizaje: DSPy optimizer, Bayesian criteria updater, Self-improvement engine, documentación"
git push origin main
Confirma con tabla.