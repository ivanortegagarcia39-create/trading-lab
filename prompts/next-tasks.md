Lee CLAUDE.md y todos los archivos en agents/ y docs/skills/.

Vamos a implementar P3.3 Firecrawl y P3.5 Thompson Sampling.
LangGraph y AutoGen los dejamos para Capa 2 cuando haya
estrategias en producción. Qdrant lo dejamos para cuando
haya >1M vectores.

TAREA 1 - Crear scripts/propfirm-monitor.py
Sistema de monitoreo de cambios en T&C de prop firms.
Alternativa a Firecrawl usando requests + BeautifulSoup
que no requiere API externa.

PROPÓSITO:
Detectar automáticamente cuando una prop firm cambia
sus reglas antes de que afecte a estrategias en producción.

FUNCIONES PRINCIPALES:

check_propfirm_changes():
  Para cada prop firm en config/propfirm-rules.json:
  1. Descargar la página de T&C usando requests
  2. Calcular SHA-256 del contenido relevante
  3. Comparar con el hash guardado anteriormente
  4. Si cambió → clasificar como CRÍTICO/IMPORTANTE/INFORMATIVO
  5. Guardar nuevo hash en results/propfirm-hashes.json

URLs a monitorear:
  ftmo: https://ftmo.com/en/trading-rules/
  e8_funding: https://e8funding.com/rules/
  brightfunded: https://brightfunded.com/trading-rules/

CLASIFICACIÓN DE CAMBIOS:
Leer el diff del contenido y buscar keywords:
  CRÍTICO: "prohibited", "banned", "EA", "automated",
           "drawdown", "daily loss"
  IMPORTANTE: "minimum", "trading days", "profit split"
  INFORMATIVO: cualquier otro cambio

ACCIONES POR NIVEL:
CRÍTICO → Telegram CRITICAL + pausar deploys automáticamente
IMPORTANTE → Telegram WARNING + revisar en próxima sesión
INFORMATIVO → log sin alerta

Guardar historial en results/propfirm-changes-log.json

ARGUMENTOS:
--check: verificar cambios ahora
--history: ver historial de cambios
--force: forzar actualización de hashes aunque no haya cambios
--dry-run: simular sin guardar

TAREA 2 - Crear scripts/thompson-sampling.py
Sistema Thompson Sampling para selección óptima
de activos y estrategias basado en resultados históricos.

PROPÓSITO:
En lugar de seleccionar activos y estrategias de forma
estática, el sistema aprende qué combinaciones funcionan
mejor y las prioriza automáticamente.

MODELO:
Para cada par (activo, timeframe):
  Beta(α, β) donde:
  α = número de builds exitosos (PF > 1.5 en WFO)
  β = número de builds fallidos

Para cada estrategia en el portfolio:
  Beta(α, β) donde:
  α = semanas con PF >= PF_OOS_backtest
  β = semanas con PF < PF_OOS_backtest

FUNCIONES PRINCIPALES:

sample_next_asset():
  Para cada par (activo, timeframe) disponible:
    Muestrear de Beta(α+1, β+1) — priors no informativos
  Devolver el par con mayor muestra
  Este es el próximo activo a buildear

update_asset_outcome(activo, timeframe, success):
  success=True: build produjo >= 1 estrategia con PF > 1.5
  success=False: build no produjo estrategias válidas
  Actualizar α o β del par correspondiente

sample_strategy_allocation(portfolio_strategies):
  Para cada estrategia activa:
    Muestrear de su Beta(α, β)
  Devolver pesos proporcionales a las muestras
  Esto determina el peso relativo de cada estrategia

update_strategy_outcome(strategy_id, success):
  success=True: semana con PF >= PF_OOS
  success=False: semana con PF < PF_OOS

get_asset_rankings():
  Listar activos ordenados por media posterior Beta
  Incluir: α, β, media, confianza (α+β)

Guardar estado en results/thompson-state.json

ARGUMENTOS:
--next-asset: sugerir próximo activo a buildear
--rankings: ver rankings de activos
--update-asset ACTIVO TIMEFRAME SUCCESS: actualizar asset
--update-strategy STRATEGY_ID SUCCESS: actualizar estrategia
--allocations: ver allocations sugeridas del portfolio

TAREA 3 - Actualizar scripts/build-queue-manager.py
Lee el archivo actual. Integrar Thompson Sampling:

Cuando se llama a "next":
  Si hay datos de Thompson Sampling disponibles:
    Usar thompson-sampling.py --next-asset para sugerir
    el próximo activo en lugar del orden fijo de la cola
  Si no hay datos suficientes (< 3 builds por activo):
    Mantener el orden actual de la cola

TAREA 4 - Actualizar scripts/self-improvement-engine.py
Lee el archivo actual. Añadir al ciclo:

Después del paso [2d]:
  [2e] Ejecutar propfirm-monitor --check --dry-run
       Si hay cambios críticos → incluir en informe urgente
  [2f] Actualizar Thompson Sampling con resultados recientes
       thompson-sampling.py --update-asset con builds de la semana

TAREA 5 - Crear docs/skills/skill-thompson-sampling.md
Documenta el sistema Thompson Sampling:

PROPÓSITO:
En lugar de elegir el próximo activo manualmente o por
un scoring fijo, el sistema aprende qué activos y timeframes
producen las mejores estrategias y los prioriza.

CÓMO FUNCIONA:
Cada activo tiene una distribución Beta que representa
nuestra "creencia" sobre su calidad como fuente de estrategias.
Con cada build: si sale bien → más probable que sea bueno
                si sale mal → menos probable

Al principio (sin datos): todos los activos son igualmente
probables → exploración amplia.
Con datos: los activos con track record mejor tienen más
probabilidad → explotación de lo que funciona.

BALANCE EXPLORACIÓN/EXPLOTACIÓN:
Thompson Sampling balancea esto automáticamente.
No hace falta decidir manualmente cuándo explorar nuevos
activos vs explotar los que ya funcionan.

Al terminar:
git add .
git commit -m "P3.3+P3.5: propfirm-monitor, thompson-sampling, integración build-queue y self-improvement"
git push origin main
Confirma con tabla.