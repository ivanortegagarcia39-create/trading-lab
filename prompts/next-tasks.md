Lee CLAUDE.md y todos los archivos en agents/ y docs/skills/.

Continuamos desde ivano. Dos bloques en paralelo.

BLOQUE A — Automatización Selenium para SQ

TAREA A1 - Crear scripts/sq-controller.py
Script que controla StrategyQuant X desde Python usando Selenium.
Automatiza todas las acciones manuales en SQ.

INSTALACIÓN: pip install selenium webdriver-manager

SQ tiene una interfaz web accesible en localhost:
StrategyQuant X corre en http://localhost:19042
(puerto por defecto de SQ X)

FUNCIONES PRINCIPALES:

connect():
  Inicializar Selenium WebDriver (Chrome o Firefox)
  Navegar a http://localhost:19042
  Verificar que SQ está corriendo
  Si no está corriendo → raise SQNotRunningError

set_symbol(symbol_name):
  Navegar a la sección de símbolos
  Seleccionar el símbolo especificado
  Verificar que el spread es correcto

configure_builder(config: dict):
  Navegar al Builder
  Configurar todos los parámetros del dict:
    symbol, timeframe, capital, risk,
    generations, population, islands,
    max_strategies, trading_hours,
    sl_type, tp_type, atr_multiplier_sl, atr_multiplier_tp

set_data_range(is_start, is_end, oos_start, oos_end):
  Configurar fechas IS y OOS en el Builder

activate_all_blocks():
  En la pestaña de bloques/indicadores
  Activar todos los grupos disponibles
  Sin restricciones de indicadores

set_filters(min_pf, min_trades_month, max_dd):
  Configurar filtros del Builder

start_builder():
  Pulsar el botón Start del Builder
  Verificar que el Builder está corriendo
  Registrar timestamp de inicio

stop_builder():
  Pulsar el botón Stop del Builder
  Esperar confirmación de parada

get_databank_count():
  Leer el número de estrategias en el databank
  Devolver el número actual

export_databank_csv(output_folder):
  Exportar todas las estrategias del databank a CSV
  Guardar en output_folder
  Devolver lista de archivos exportados

get_builder_status():
  Leer el estado actual del Builder:
  RUNNING, STOPPED, FINISHED
  Número de estrategias generadas
  Mejor PF actual

MANEJO DE ERRORES:
Si SQ no responde → retry 3 veces con 10s de espera
Si elemento no encontrado → log detallado + raise
Todos los clicks con waits explícitos (no time.sleep fijo)

ARGUMENTOS CLI:
--connect: verificar conexión con SQ
--configure --build N --activo XAUUSD: configurar builder
--start: iniciar builder
--stop: parar builder
--status: ver estado actual
--export --output results/: exportar databank

TAREA A2 - Actualizar scripts/build-launcher.py
Lee el archivo actual. Añadir opción --auto:

Si --auto está presente:
  Usar sq-controller.py para configurar SQ automáticamente
  Llamar a sq_controller.configure_builder(config)
  Llamar a sq_controller.start_builder()
  Mostrar: "Builder iniciado automáticamente"

Si --auto NO está presente (modo actual):
  Mostrar instrucciones manuales como hasta ahora
  (mantener compatibilidad con modo manual)

TAREA A3 - Crear scripts/sq-watchdog.py
Script que vigila SQ durante un build y actúa si hay problemas.

MONITOREA CADA 15 MINUTOS:
1. SQ sigue corriendo (proceso activo)
2. Builder sigue generando (databank count aumenta)
3. No hay errores en el log de SQ
4. Uso de memoria dentro de límites (<85% RAM)

ACCIONES AUTOMÁTICAS:
Si SQ se congela (databank no crece en 30 min):
  Intentar reiniciar el Builder via sq-controller
  Si falla → alerta Telegram CRÍTICO
  
Si SQ se cierra inesperadamente:
  Alerta Telegram CRÍTICO
  Intentar relanzar SQ automáticamente
  Registrar incidente en audit trail

Si memoria > 85%:
  Alerta Telegram WARNING
  Log del estado de memoria

ARGUMENTOS:
--watch --build N: vigilar build activo
--interval: intervalo de check en minutos (default 15)

---

BLOQUE B — Mejoras del sistema v8.1

TAREA B1 - Crear scripts/multi-asset-scheduler.py
Script que gestiona builds en múltiples activos de forma
secuencial y automática.

PROPÓSITO:
Cuando un build termina en XAUUSD, el sistema decide
automáticamente qué activo buildear después usando
Thompson Sampling y los datos disponibles.

FUNCIONES:
get_next_build_candidate():
  Consultar thompson-sampling.py --next-asset
  Verificar que hay datos M1 disponibles para ese activo
  Verificar que el activo no ha sido buildeado recientemente
  Devolver: activo, timeframe, spread_real, razón

schedule_next_build():
  Llamar a get_next_build_candidate()
  Preparar la configuración del próximo build
  Actualizar build-queue-manager con el nuevo plan
  Notificar via Telegram: "Próximo build: [ACTIVO]"

run_continuous_scheduler():
  Bucle infinito:
    Esperar a que termine el build actual
    Ejecutar build-finisher para el build terminado
    Ejecutar schedule_next_build()
    Lanzar el próximo build automáticamente
    Esperar 48h o hasta que termine

ARGUMENTOS:
--next: mostrar próximo activo sugerido
--schedule: programar próximo build
--run: ejecutar scheduler continuo

TAREA B2 - Crear scripts/performance-dashboard.py
Dashboard completo del sistema en tiempo real.
Versión mejorada del portfolio-monitor-dashboard.py.

MUESTRA EN PANTALLA (actualizable con --watch):

═══════════════════════════════════════════════
  TRADINGLAB — Dashboard v8.1 — [fecha/hora]
═══════════════════════════════════════════════

PIPELINE:
  Build activo: [nombre o "ninguno"]
  Cola: [próximos activos]
  Último build: [fecha, activo, resultado]

PORTFOLIO:
  Estrategias activas: X
  DD combinado: X%
  PF medio: X
  Semáforo: 🟢/🟡/🔴

AUTOAPRENDIZAJE:
  KG: X builds, X estrategias
  Bayesian: último ajuste [fecha]
  Drift: [estado]
  Champion-Challenger: X champions, X challengers
  Último ciclo self-improvement: [fecha]

SISTEMA:
  Scripts: X operativos
  ChromaDB: X chunks
  Telegram: activo/inactivo
  SQ: corriendo/parado

ALERTAS ACTIVAS:
  [lista de alertas o "Sin alertas"]

═══════════════════════════════════════════════

ARGUMENTOS: --watch, --interval (default 60s), --compact

TAREA B3 - Crear scripts/lessons-auto-updater.py
Script que actualiza automáticamente lessons-learned.md
cuando el sistema detecta nuevas lecciones.

PROCESO:
1. Leer todas las lecciones del KG
2. Comparar con las lecciones en lessons-learned.md
3. Si hay lecciones nuevas en el KG que no están en el MD:
   Añadir la lección al MD con el formato correcto
4. Si hay lecciones TENTATIVA con 3+ ocurrencias:
   Elevar automáticamente a ESTRUCTURAL en el MD y el KG
5. Registrar cambios en audit trail

ARGUMENTOS:
--check: verificar si hay lecciones nuevas
--update: aplicar actualizaciones
--dry-run: mostrar cambios sin aplicar

TAREA B4 - Actualizar scripts/auto-reporter.py
Lee el archivo actual. Añadir al informe semanal:

Nueva sección "Próxima semana":
  Próximo build sugerido por Thompson Sampling
  Activos pendientes en la cola
  Criterios bayesianos que podrían ajustarse
  Estrategias en shadow mode que terminan pronto

TAREA B5 - Actualizar docs/roadmap/planning-maestro-status.md
Añadir las nuevas tareas como completadas:
- scripts/sq-controller.py — control automático de SQ via Selenium
- scripts/sq-watchdog.py — vigilancia de builds activos
- scripts/multi-asset-scheduler.py — scheduler multi-activo
- scripts/performance-dashboard.py — dashboard completo v8.1
- scripts/lessons-auto-updater.py — actualización automática lecciones
- build-launcher.py actualizado con --auto mode
- auto-reporter.py actualizado con sección "próxima semana"

Actualizar total a ~202/222 o similar.

Al terminar:
git add .
git commit -m "v8.1: Selenium SQ controller, sq-watchdog, multi-asset-scheduler, performance-dashboard, lessons-auto-updater"
git push origin main
Confirma con tabla.