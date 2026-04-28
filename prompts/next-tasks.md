Lee CLAUDE.md y todos los archivos en agents/ y docs/skills/.

Vamos a implementar P2.3 BOCPD+ADDM y P2.4 Champion-Challenger.

TAREA 1 - Crear scripts/concept-drift-detector.py
Sistema de detección de cambios de régimen y drift del mercado.
Implementa BOCPD (Bayesian Online Change-Point Detection)
y ADDM (Autoregressive Drift Detection Method).

BOCPD:
Detecta cuándo el mercado cambia de régimen de forma abrupta.
Útil para: detectar cuándo las estrategias actuales pueden
dejar de funcionar porque el mercado cambió.

Implementación simplificada (sin librerías externas):
- Mantener una ventana deslizante de los últimos 50 retornos
- Calcular la probabilidad de cambio de punto usando
  distribución Normal conjugada
- Si la probabilidad posterior de cambio > 0.7 → CHANGE_POINT
- Si > 0.5 → WARNING

ADDM:
Detecta drift gradual en los errores del sistema.
El "error" se define como: PF_esperado - PF_real
Si este error aumenta consistentemente → el sistema
está derivando de sus predicciones.

Implementación:
- Mantener historial de (PF_esperado, PF_real) por estrategia
- Calcular residual = PF_esperado - PF_real
- Si la media móvil del residual supera 2 desviaciones estándar
  durante 3 periodos consecutivos → DRIFT_DETECTED

FUNCIONES PRINCIPALES:

update_bocpd(returns_series, timestamp):
  Actualiza el modelo BOCPD con nuevos retornos
  Devuelve: probabilidad de cambio de punto actual
  Si > 0.7: registrar CHANGE_POINT en KG

update_addm(expected_pf, actual_pf, strategy_id, timestamp):
  Actualiza el modelo ADDM con nueva observación
  Devuelve: nivel de drift (NONE/WARNING/CRITICAL)
  Si CRITICAL: activar alerta en Telegram

get_drift_report():
  Estado actual de todos los detectores
  Cambios de punto detectados en los últimos 30 días
  Estrategias con drift detectado

check_regime_stability():
  Compara régimen actual con régimen de los últimos 30 días
  Si hubo cambio de punto reciente → recomendar re-validación
  de estrategias activas

Guardar estado en results/drift-detection.json

ARGUMENTOS CLI:
--update-bocpd: actualizar con nuevos datos
--update-addm: actualizar con nuevo par esperado/real
--report: ver reporte de drift
--check: verificar estabilidad actual

TAREA 2 - Crear scripts/champion-challenger.py
Sistema Champion-Challenger con Shadow Mode.
Permite probar nuevas estrategias en paralelo con las activas
sin arriesgar capital real.

CONCEPTO:
Champion: estrategia activa con capital real en producción
Challenger: estrategia nueva corriendo en paper trading
  en paralelo para comparar métricas

FLUJO:
1. Cuando una nueva estrategia pasa el WFO:
   Si no hay champion → se convierte en champion directo
   Si ya hay champion → se convierte en challenger (shadow)
2. El challenger corre en paper trading durante 4 semanas
3. Al final de las 4 semanas comparar métricas:
   PF challenger vs PF champion
   DD challenger vs DD champion
   Sharpe challenger vs Sharpe champion
4. Si challenger supera al champion en 2 de 3 métricas
   con significancia estadística → PROMOTION
   Champion se retira → Challenger se convierte en champion
5. Si challenger no supera → REJECTED
   Se documenta por qué y se añade al KG

FUNCIONES PRINCIPALES:

register_champion(strategy_id, metrics):
  Registra una estrategia como champion activo
  Guarda en results/champion-challenger.json

register_challenger(strategy_id, metrics):
  Registra una estrategia como challenger
  Estado inicial: SHADOW (paper trading)

update_challenger_metrics(strategy_id, new_metrics):
  Actualiza métricas del challenger con datos recientes

evaluate_challenger(strategy_id):
  Compara challenger vs champion actual
  Test estadístico simple: t-test sobre retornos
  Veredicto: PROMOTE / REJECT / CONTINUE (más datos)

promote_challenger(strategy_id):
  El challenger se convierte en champion
  El champion anterior pasa a RETIRED
  Registrar en KG y audit trail
  Notificar via Telegram

get_status():
  Estado actual de todos los champions y challengers
  Por activo: quien es el champion, cuántos challengers

Guardar estado en results/champion-challenger.json

ARGUMENTOS CLI:
--register-champion: registrar champion
--register-challenger: registrar challenger
--evaluate: evaluar un challenger
--status: ver estado actual
--promote: promover manualmente un challenger

TAREA 3 - Crear scripts/internal-critic.py
El Crítico Interno automático (P2.5).
Revisa las decisiones del pipeline retrospectivamente
y propone mejoras concretas.

EJECUCIÓN: semanal automática via self-improvement-engine

PROCESO:
1. Leer últimas 20 decisiones del audit trail
2. Para cada decisión con outcome conocido:
   ¿El pipeline acertó o falló?
   ¿Qué criterio tomó la decisión correcta/incorrecta?
3. Identificar los 3 errores más costosos del período
4. Para cada error generar hipótesis de causa:
   Si modelos disponibles: usar model-router (deepseek local)
   Si no: análisis estadístico básico
5. Proponer ajuste concreto al criterio responsable
6. Verificar si el ajuste habría funcionado en datos históricos
7. Si pasa la verificación: enviar propuesta al bayesian-updater
8. Registrar todo en KG y lessons-learned.md

MÉTRICAS QUE REVISA:
- Tasa de falsos positivos por puerta del pipeline
- Tasa de falsos negativos por puerta del pipeline
- Correlación entre criterios y outcomes reales
- Drift de criterios vs resultados (ADDM)

ARGUMENTOS:
--run: ejecutar revisión completa
--dry-run: simular sin aplicar cambios
--report: ver último informe del crítico

TAREA 4 - Actualizar scripts/self-improvement-engine.py
Lee el archivo actual. Añadir al ciclo de autoaprendizaje:

Después del paso [2/7]:
  [2b] Ejecutar concept-drift-detector --check
       Si hay drift → añadir alerta al informe
  [2c] Ejecutar champion-challenger --evaluate para cada challenger
       Si alguno listo para promoción → incluir en informe
  [2d] Ejecutar internal-critic --dry-run
       Incluir propuestas del crítico en el informe final

TAREA 5 - Crear docs/skills/skill-concept-drift.md
Documenta el sistema de detección de drift:

BOCPD: para cambios abruptos de régimen de mercado
ADDM: para degradación gradual de las estrategias
Cuándo actuar vs cuándo ignorar señales de drift
Integración con el ciclo de autoaprendizaje semanal

Al terminar:
git add .
git commit -m "P2.3+P2.4+P2.5: concept-drift-detector, champion-challenger, internal-critic, self-improvement actualizado"
git push origin main
Confirma con tabla.