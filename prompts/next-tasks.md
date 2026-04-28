Lee CLAUDE.md, docs/roadmap/planning-maestro-status.md
y scripts/knowledge-graph.py.

Vamos a cerrar los gaps que podemos hacer ahora mismo.

TAREA 1 - Arreglar lecciones en el Knowledge Graph
El kg-importer.py importó las lecciones con estado TENTATIVA
pero LECCION-001 tiene 4 ocurrencias y LECCION-002 tiene 8.
Según las reglas del proyecto ambas deben ser ESTRUCTURAL.

En scripts/kg-importer.py, en la función que importa lecciones
desde lessons-learned.md, corregir el parser para que:
1. Lea el campo "Ocurrencias confirmadas: N"
2. Si N >= 3 → estado = "ESTRUCTURAL"
3. Si N < 3 → estado = "TENTATIVA"

También añadir los nodos Criterion al KG durante el init:
Los 5 criterios de config/bayesian-criteria.json deben
crear nodos Criterion en el grafo con su valor actual.

TAREA 2 - Actualizar docs/roadmap/planning-maestro-status.md
Añadir todas las tareas nuevas completadas hoy como [x]:

NUEVAS TAREAS COMPLETADAS (v8.0):
- scripts/knowledge-graph.py — KG Kùzu con 7 nodos y 7 aristas
- scripts/kg-importer.py — importador del historial al KG
- scripts/model-router.py — router de modelos DeepSeek/Kimi/GPT-5.5
- config/api-keys.json.template — template claves API
- scripts/dspy-optimizer.py — auto-optimización de prompts DSPy
- scripts/bayesian-criteria-updater.py — actualización bayesiana de umbrales
- scripts/self-improvement-engine.py — ciclo semanal de autoaprendizaje
- scripts/concept-drift-detector.py — BOCPD + ADDM detección de drift
- scripts/champion-challenger.py — Shadow Mode champion vs challenger
- scripts/internal-critic.py — crítico interno automático
- scripts/thompson-sampling.py — selección óptima de activos
- scripts/propfirm-monitor.py — monitoreo T&C prop firms
- config/propfirm-rules.json — reglas FTMO/E8/BrightFunded
- scripts/challenge-demo-simulator.py — AutoDemoPipeline v3.0
- agents/challenge-verdict-generator.md — veredicto PASS/FAIL/REVIEW
- agents/demo-account-factory.md — gestión cuentas demo
- docs/skills/skill-self-improvement.md — autoaprendizaje documentado
- docs/skills/skill-concept-drift.md — drift detection documentado
- docs/skills/skill-thompson-sampling.md — Thompson Sampling documentado
- docs/skills/skill-model-router.md — router modelos documentado
- docs/skills/skill-challenge-simulation.md — simulación challenge documentado
- docs/architecture/knowledge-graph-schema.md — esquema KG documentado

Actualizar el total: debería ser ~185/205 o similar.
Actualizar el porcentaje.

TAREA 3 - Crear scripts/quarterly-reoptimizer.py
Protocolo de reoptimización trimestral de estrategias.

PROPÓSITO:
Cada 3 meses verificar si las estrategias activas siguen
siendo rentables. Si una estrategia muestra decay confirmado,
lanzar el Improver de SQ para reoptimizar solo parámetros
(no la lógica de entrada — eso violaría Builder libre).

PROCESO TRIMESTRAL:
1. Leer portfolio activo desde results/portfolio-selected.json
2. Para cada estrategia activa:
   a. Calcular PF de los últimos 3 meses en producción
   b. Comparar con PF OOS del backtest original
   c. Si PF_real < 85% de PF_OOS durante 4+ semanas → DECAY
3. Para estrategias en DECAY:
   a. Generar alerta Telegram: "Decay confirmado: [ID]"
   b. Marcar para reoptimización en strategy-versioning
   c. Registrar en KG con causa documentada
4. Generar informe trimestral en results/quarterly-report-[fecha].md

CRITERIO IMPORTANTE:
La reoptimización SQ solo puede tocar parámetros numéricos
(multiplicadores ATR, períodos de indicadores).
NUNCA cambiar la lógica de entrada — eso es trabajo del Builder.
Si los parámetros optimizados no mejoran → retirar estrategia
y lanzar nuevo ciclo de Builder para ese activo.

ARGUMENTOS:
--run: ejecutar revisión trimestral
--dry-run: simular sin aplicar cambios
--report: ver último informe trimestral

TAREA 4 - Actualizar CLAUDE.md
Lee el archivo actual. Actualiza la sección de estado:

## Estado Actual (2026-04-29)
- Fase: Capa 0 activa — Sistema v8.0 completo
- Build activo: Build 11 PENDIENTE en alber (spread 60 pips)
- Planning maestro: ~185/205 tareas completadas
- Scripts Python operativos: 55 (todos probados)
- Autoaprendizaje: Knowledge Graph + DSPy + Bayesian + Drift + Champion-Challenger
- Telegram bot: @tradinglab_monitor_bot activo
- ChromaDB: 909 chunks indexados
- Próximo hito: Primera estrategia aprobada por WFO (Build 11)

TAREA 5 - Ejecutar re-index completo del KG y ChromaDB
Después de los cambios anteriores:
1. Borrar .kuzu/ y reiniciar el KG
2. Ejecutar kg-importer.py para reimportar con correcciones
3. Ejecutar knowledge-base.py re-index para actualizar ChromaDB

Comandos a ejecutar:
rmdir /s /q .kuzu
python scripts/knowledge-graph.py --mode init
python scripts/kg-importer.py
python scripts/knowledge-base.py re-index

Al terminar:
git add .
git commit -m "Revisión completa v8.0: KG corregido, planning actualizado 185+, quarterly-reoptimizer, CLAUDE.md v8.0"
git push origin main
Confirma con tabla.