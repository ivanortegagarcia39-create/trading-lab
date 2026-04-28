Lee CLAUDE.md y todos los archivos en agents/ y docs/skills/.

Continuamos desde ivano. Crea los siguientes archivos.

TAREA 1 - Crear scripts/retester-helper.py
Script que ayuda a gestionar el proceso del Retester en SQ
después de que el EvalGate aprueba estrategias.

FLUJO:
1. Lee results/evaluation-gate-results.json
2. Muestra la lista de estrategias que pasan el EvalGate
3. Para cada estrategia muestra instrucciones exactas para el Retester en SQ:
   - Nombre exacto del archivo .sqx
   - Configuración del Retester recomendada
   - Fechas IS y OOS a usar
   - Si debe ejecutar Monte Carlo: Sí (200 simulaciones, 95% confianza)
4. Después del Retester muestra criterios del Paso 12b para verificar
5. Genera checklist de resultados que el usuario debe rellenar manualmente
6. Guarda checklist en results/retester-checklist-[fecha].md

ARGUMENTOS: --eval-results (default: results/evaluation-gate-results.json)

TAREA 2 - Crear scripts/wfo-helper.py  
Script que ayuda a gestionar el proceso WFO después del Retester.

FLUJO:
1. Lee results/retester-checklist-[fecha].md más reciente
2. Muestra estrategias que pasan el Paso 12b
3. Para cada estrategia muestra instrucciones exactas para el WFO en SQ:
   - Configuración WFO recomendada: IS 70%, OOS 30%, 5 ventanas
   - Activar WF Matrix: Sí
   - Catastrophic Veto: activado
4. Después del WFO muestra criterios de aprobación:
   - WFE >= 50%
   - >= 3/5 configuraciones pasadas
   - Catastrophic Veto: ninguna ventana PF < 0.8
5. Genera checklist WFO en results/wfo-checklist-[fecha].md

TAREA 3 - Crear scripts/stress-tester.py
Script que guía el stress test histórico de las 5 épocas críticas.

FLUJO:
1. Lee results/wfo-checklist más reciente
2. Muestra estrategias que pasan el WFO
3. Para cada estrategia y cada época crítica muestra:
   - Nombre del período: Crisis 2008, Flash CHF 2015, COVID 2020, Inflación 2022, SVB 2023
   - Fechas exactas a configurar en el Retester de SQ
   - Criterio: DD < 8% en cada período
4. Genera tabla de resultados a rellenar manualmente
5. Guarda en results/stress-test-results-[fecha].md
6. Calcula score final por estrategia (cuántos períodos pasa)

TAREA 4 - Crear docs/skills/skill-pipeline-execution-guide.md
Guía práctica de ejecución del pipeline completo.
Esta es la guía que se usa durante una sesión real de trabajo.

ESTRUCTURA:
1. Antes de empezar (comandos de inicio de sesión)
2. Fase Builder (build-launcher.py + SQ manual)
3. Fase EvalGate (build-finisher.py automático)
4. Fase Retester (retester-helper.py + SQ manual)
5. Fase WFO (wfo-helper.py + SQ manual)
6. Fase Stress Test (stress-tester.py + SQ manual)
7. Fase Portfolio (portfolio-builder.py automático)
8. Fase Forward Test (MT5 demo automático)
9. Autorización del Challenge (Telegram → SI humano)
10. Comandos de fin de sesión

Para cada fase: comando exacto + qué hace el humano + qué hace el sistema.

TAREA 5 - Actualizar docs/roadmap/planning-maestro-status.md
Añadir como completadas las últimas tareas:
- scripts/build-launcher.py
- scripts/build-finisher.py
- scripts/build-queue-manager.py
- scripts/retester-helper.py
- scripts/wfo-helper.py
- scripts/stress-tester.py
- docs/skills/skill-pipeline-gates-checklist.md
- docs/skills/skill-pipeline-execution-guide.md
- docs/architecture/pipeline-diagram.md
- ChromaDB re-indexado con 909 chunks

Actualizar total: debería llegar a ~158/172 o más.

Al terminar:
git add .
git commit -m "Scripts: retester-helper, wfo-helper, stress-tester. Skills: pipeline-execution-guide. Planning actualizado ~158/172"
git push origin main
Confirma con tabla.