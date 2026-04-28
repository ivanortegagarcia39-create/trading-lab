Lee CLAUDE.md y todos los archivos en agents/ y docs/skills/.

Continuamos desde ivano. Vamos a implementar las últimas
mejoras que podemos hacer sin hardware.

TAREA 1 - Crear scripts/regime-strategy-matcher.py
Script que conecta el régimen de mercado actual con
las estrategias más adecuadas para ese régimen.

PROPÓSITO:
No todas las estrategias funcionan igual en todos los regímenes.
Una estrategia generada en tendencia-altavol puede fallar
en rango-bajovol. Este script aprende qué estrategias
funcionan mejor en cada régimen.

FUNCIONES:
record_regime_performance(strategy_id, regime, week_pf):
  Registra el PF de una estrategia en un régimen específico
  Guarda en results/regime-performance.json

get_best_strategies_for_regime(regime):
  Devuelve las estrategias ordenadas por PF medio
  en el régimen especificado
  Útil para decidir qué estrategia priorizar cuando
  el régimen cambia

get_regime_compatibility(strategy_id):
  Para una estrategia, muestra su PF medio en cada régimen
  Identifica en qué régimen funciona mejor y peor

recommend_for_current_regime():
  Detecta el régimen actual (via market-regime-snapshot)
  Recomienda las estrategias más adecuadas para ese régimen
  Si no hay suficientes datos → "Sin datos suficientes"

ARGUMENTOS:
--record STRATEGY_ID REGIME WEEK_PF
--best-for REGIME
--compatibility STRATEGY_ID
--recommend

TAREA 2 - Crear scripts/pipeline-health-monitor.py
Monitor de salud del pipeline completo.
Detecta si el pipeline está funcionando correctamente
o si hay señales de degradación.

MÉTRICAS QUE MONITOREA:
1. Tasa de aprobación por puerta (últimas 4 semanas)
   Si tasa < 50% de la tasa histórica → WARNING
2. Tiempo medio de build (últimas 3 builds)
   Si aumenta > 20% → posible problema de hardware
3. Número de builds sin resultados consecutivos
   Si > 2 builds consecutivos sin pasar EvalGate → ALERTA
4. Deriva de criterios bayesianos
   Si algún criterio cambió > 15% → revisar
5. Salud del Knowledge Graph
   Si no hay actualizaciones en > 7 días → WARNING

DASHBOARD EN TEXTO:
Genera un dashboard ASCII con semáforo por cada métrica
VERDE: funcionando normal
AMARILLO: revisar pronto
ROJO: acción inmediata requerida

ARGUMENTOS:
--report: generar reporte completo
--watch: modo continuo (actualiza cada hora)
--fix: intentar autocorrecciones menores

TAREA 3 - Crear scripts/strategy-retirement-manager.py
Gestiona el ciclo de vida completo de las estrategias
desde su creación hasta su retiro del portfolio.

ESTADOS DE UNA ESTRATEGIA:
standby → en espera de ser evaluada
candidate → pasó EvalGate, en proceso de validación
shadow → challenger en paper trading
active → en producción con capital real
decaying → señales de deterioro detectadas
retired → retirada del portfolio
failed_challenge → falló el challenge demo

TRANSICIONES AUTOMÁTICAS:
standby → candidate: cuando pasa EvalGate
candidate → shadow: cuando pasa WFO y Forward Test
shadow → active: cuando es promovida por champion-challenger
active → decaying: cuando ADDM detecta drift confirmado
decaying → retired: si no mejora en 4 semanas
decaying → active: si se recupera (ADDM normal 4 semanas)

FUNCIONES:
transition_state(strategy_id, new_state, reason):
  Cambia el estado de una estrategia
  Registra en KG y audit trail
  Notifica via Telegram si es un estado importante

get_lifecycle_report():
  Resumen de todas las estrategias por estado
  Tiempo medio en cada estado
  Estrategias que necesitan atención

check_for_transitions():
  Verifica si alguna estrategia debe transicionar de estado
  Basado en métricas actuales y criterios bayesianos
  Ejecutar diariamente

ARGUMENTOS:
--report: ver ciclo de vida de todas las estrategias
--check: verificar transiciones pendientes
--transition STRATEGY_ID NEW_STATE REASON: transición manual

TAREA 4 - Actualizar scripts/self-improvement-engine.py
Lee el archivo actual. Añadir dos pasos más al ciclo:

Después del paso [2f]:
  [2g] Ejecutar pipeline-health-monitor --report
       Si hay métricas en ROJO → incluir en informe urgente
  [2h] Ejecutar strategy-retirement-manager --check
       Si hay estrategias que deben transicionar → ejecutar
       y registrar en el informe del ciclo

TAREA 5 - Crear docs/skills/skill-strategy-lifecycle.md
Documenta el ciclo de vida completo de una estrategia
desde que SQ la genera hasta que se retira:

ESTADOS: standby → candidate → shadow → active →
         decaying → retired / failed_challenge

TIEMPO TÍPICO EN CADA ESTADO:
standby: 0-2 días (evaluación automática)
candidate: 1-3 días (Retester + WFO + Stress Test)
shadow: 4 semanas (Champion-Challenger)
active: meses o años (en producción)
decaying: máximo 4 semanas antes de decisión final
retired: permanente (registro histórico)

MÉTRICAS DE CALIDAD DEL CICLO:
Tasa de conversión standby → active (objetivo: > 5%)
Duración media en producción antes de decay
Causa más frecuente de retiro

Al terminar:
git add .
git commit -m "Scripts: regime-strategy-matcher, pipeline-health-monitor, strategy-retirement-manager. Skills: strategy-lifecycle"
git push origin main
Confirma con tabla.