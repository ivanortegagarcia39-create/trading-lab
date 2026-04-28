Lee CLAUDE.md y todos los archivos en agents/ y docs/skills/.

Continuamos desde ivano. Crea los siguientes archivos.

TAREA 1 - Crear scripts/news-filter-checker.py
Script que verifica si hay noticias de alto impacto próximas
antes de abrir una operación o lanzar un build.

FUNCIONES:
- Consultar ForexFactory calendar API (si disponible)
- Si no hay API disponible: usar lista hardcodeada de horarios típicos
  de noticias de alto impacto por día de la semana
- Verificar si hay evento en los próximos 30 minutos
- Verificar si hay evento NFP o FOMC en los próximos 30 minutos
  (ventana extendida de 30 minutos en lugar de 15)
- Output: SAFE / WARNING / DANGER
  SAFE: sin noticias en próximos 30 minutos
  WARNING: noticia de impacto medio en próximos 15 minutos
  DANGER: noticia de alto impacto en próximos 30 minutos

Horarios típicos hardcodeados (UTC):
Lunes: sin noticias críticas típicas
Martes: 09:00 (datos europeos), 13:30 (datos EEUU)
Miércoles: 13:30 (datos EEUU), 18:00 (FOMC si aplica)
Jueves: 07:00 (BCE si aplica), 13:30 (NFP jueves previo)
Viernes: 13:30 (NFP primer viernes del mes)

Argumento: --check-now (verificar estado actual)
           --activo (para filtrar noticias relevantes)

TAREA 2 - Crear scripts/spread-monitor.py
Script que monitorea el spread actual de los activos
para detectar condiciones anómalas antes de operar.

FUNCIONES:
- Leer spread actual desde MT5 si está disponible
- Si MT5 no disponible: usar spread de referencia de config/build-defaults.json
- Comparar spread actual vs spread promedio del activo
- Calcular factor de spread: spread_actual / spread_promedio
- Output por activo:
  NORMAL: factor < 1.5x
  ELEVATED: factor 1.5x - 3x (operar con precaución)
  EXTREME: factor > 3x (no operar — Dynamic Spread Protection)

Argumentos: --activo, --check-interval (default 60s), --watch

TAREA 3 - Crear docs/skills/skill-ea-parameters.md
Documenta todos los parámetros que debe tener cada EA exportado
desde SQ para TradingLab:

PARÁMETROS OBLIGATORIOS:
- Risk: porcentaje de riesgo por trade (default 1.0)
- MagicNumber: identificador único del EA
- MaxSlippagePips: límite de slippage por activo
- UseNewsFilter: activar filtro de noticias (default true)
- NewsFilterMinutes: ventana de protección (default 15)
- UseDynamicSpreadProtection: activar si spread > 3x (default true)
- MaxSpreadMultiplier: factor máximo de spread permitido (default 3.0)
- CloseOnFriday: cerrar posiciones viernes 22:00 CEST (default true)
- FridayCloseHour: hora de cierre viernes en UTC (default 20)
- UseHeartbeat: activar heartbeat para vps-health-monitor (default true)
- HeartbeatFile: ruta al archivo de heartbeat

PARÁMETROS OPCIONALES:
- MaxDailyTrades: máximo trades por día (default 2)
- TradingStartHour: hora inicio sesión UTC (default 6)
- TradingEndHour: hora fin sesión UTC (default 18)
- UseAntiSync: activar delay aleatorio anti-sincronización (default true)
- AntiSyncMinMs: delay mínimo en ms (default 500)
- AntiSyncMaxMs: delay máximo en ms (default 3500)

VALORES POR ACTIVO:
XAUUSD: MaxSlippagePips=50, Risk=1.0
EURUSD: MaxSlippagePips=5, Risk=1.0
GBPUSD: MaxSlippagePips=5, Risk=1.0
USDJPY: MaxSlippagePips=5, Risk=1.0

TAREA 4 - Crear docs/skills/skill-forward-test-protocol.md
Documenta el protocolo completo del forward test en MT5 demo:

CONFIGURACIÓN INICIAL:
1. Abrir cuenta demo FTMO (válida 45 días)
2. Capital demo = capital del challenge objetivo (10k, 25k, etc.)
3. Desplegar EA en VPS con parámetros de producción
4. Configurar Risk = 1% (o ajustado por portfolio)
5. Verificar que EA abre trades correctamente en las primeras 24h

MONITOREO DIARIO:
- Verificar que el EA sigue conectado (heartbeat activo)
- Registrar balance diario en ftmo-account-tracker.py
- Si DD > 3% → alerta, revisar si es normal o señal de problema
- Si 5 días sin trades → verificar configuración del EA

CRITERIOS DE APROBACIÓN AUTOMÁTICA:
Los 3 deben cumplirse simultáneamente:
1. Mínimo 20 trades ejecutados
2. PF producción >= 70% del PF OOS del backtest
3. DD máximo <= DD OOS del backtest * 1.30

CRITERIO DE FALLA AUTOMÁTICA:
Si cualquiera falla → estrategia a cola de reemplazo
Sin segunda oportunidad en el mismo ciclo

TRAS APROBAR:
orchestrator genera notificación Telegram con todos los datos
Humano responde SI para autorizar compra del challenge
Sistema registra la autorización en audit trail

TAREA 5 - Actualizar docs/project-status.md
Fecha: 2026-04-28
Estado completo actualizado:
- Scripts Python: 41 operativos
- Planning: 163/183 tareas (89%)
- Próxima acción inmediata: ir a alber, git pull, lanzar Build 11
- Comando exacto para mañana:
  python scripts/build-launcher.py --build 11 --activo XAUUSD --spread-real 30

Al terminar:
git add .
git commit -m "Scripts: news-filter-checker, spread-monitor. Skills: ea-parameters, forward-test-protocol. Project-status actualizado 2026-04-28"
git push origin main
Confirma con tabla.