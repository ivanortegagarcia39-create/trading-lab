//+------------------------------------------------------------------+
//| ConnectionMonitor.mqh                                            |
//| Libreria MQL5 reutilizable para monitoreo de conexion.           |
//|                                                                  |
//| Incluir en todos los EAs exportados desde TradingLab:            |
//|   #include "ConnectionMonitor.mqh"                               |
//|                                                                  |
//| Funciones publicas:                                              |
//|   IsConnectionHealthy()       — verifica conexion al broker      |
//|   CheckPreTradeConnection()   — verificar antes de OrderSend     |
//|   SendHeartbeat(file_path)    — escribir timestamp para monitor  |
//|   ReconnectWithBackoff(tries) — reconexion con backoff exponencial|
//+------------------------------------------------------------------+

#property strict

//+------------------------------------------------------------------+
//| Constantes de configuracion                                      |
//+------------------------------------------------------------------+

// Segundos entre escrituras de heartbeat (para no saturar I/O)
#define CM_HEARTBEAT_INTERVAL_SEC   60

// Intentos de reconexion maximos por defecto
#define CM_DEFAULT_MAX_ATTEMPTS     5

// Delay inicial de backoff en milisegundos
#define CM_BACKOFF_BASE_MS          5000


//+------------------------------------------------------------------+
//| Estado interno del monitor                                       |
//+------------------------------------------------------------------+

static datetime _cm_last_heartbeat    = 0;
static datetime _cm_disconnect_start  = 0;
static bool     _cm_was_connected     = true;


//+------------------------------------------------------------------+
//| IsConnectionHealthy                                              |
//|                                                                  |
//| Devuelve true si el terminal esta conectado al broker.           |
//| Usa TerminalInfoInteger(TERMINAL_CONNECTED) — el indicador       |
//| nativo de MT5 para el estado de la conexion.                     |
//+------------------------------------------------------------------+
bool IsConnectionHealthy()
{
    return (bool)TerminalInfoInteger(TERMINAL_CONNECTED);
}


//+------------------------------------------------------------------+
//| CheckPreTradeConnection                                          |
//|                                                                  |
//| Verificar ANTES de cada OrderSend. Si no hay conexion:           |
//|   - Registra el evento en el log del EA con timestamp.           |
//|   - Devuelve false para que el EA aborte la orden.               |
//|                                                                  |
//| Uso en el EA:                                                    |
//|   if (!CheckPreTradeConnection()) return;                        |
//|   // OrderSend(...)                                              |
//+------------------------------------------------------------------+
bool CheckPreTradeConnection()
{
    if (!IsConnectionHealthy())
    {
        PrintFormat("[CM] ABORT: Sin conexion al broker. Orden cancelada. [%s]",
                    TimeToString(TimeGMT(), TIME_DATE | TIME_SECONDS));
        return false;
    }

    // Verificar tambien que hay cotizaciones actualizadas
    datetime last_tick = (datetime)SymbolInfoInteger(Symbol(), SYMBOL_TIME);
    datetime now_gmt   = TimeGMT();

    // Si el ultimo tick tiene mas de 5 minutos → posible problema de feed
    if (now_gmt - last_tick > 300)
    {
        PrintFormat("[CM] WARN: Ultimo tick de %s hace %ds. Posible problema de feed.",
                    Symbol(), (int)(now_gmt - last_tick));
        // No abortar por esto — solo avisar. El broker puede tener momentos sin cotizacion.
    }

    return true;
}


//+------------------------------------------------------------------+
//| SendHeartbeat                                                    |
//|                                                                  |
//| Escribe el timestamp Unix actual en file_path.                   |
//| El vps-health-monitor.py lee este archivo para detectar          |
//| Ghost Freeze (EA vivo pero congelado internamente).              |
//|                                                                  |
//| Llamar en OnTick() — la funcion limita la frecuencia a           |
//| CM_HEARTBEAT_INTERVAL_SEC para no saturar el disco.              |
//|                                                                  |
//| Uso en el EA:                                                    |
//|   void OnTick() {                                                |
//|       SendHeartbeat("C:\\trading-lab\\heartbeat.txt");           |
//|       ...                                                        |
//|   }                                                              |
//+------------------------------------------------------------------+
void SendHeartbeat(string file_path)
{
    datetime now = TimeGMT();

    // Limitar la frecuencia de escritura
    if (now - _cm_last_heartbeat < CM_HEARTBEAT_INTERVAL_SEC) return;
    _cm_last_heartbeat = now;

    // Escribir el timestamp Unix como string
    int handle = FileOpen(file_path, FILE_WRITE | FILE_TXT | FILE_ANSI, '\n', CP_ACP);
    if (handle == INVALID_HANDLE)
    {
        PrintFormat("[CM] ERROR: No se pudo abrir heartbeat file: %s (error %d)",
                    file_path, GetLastError());
        return;
    }

    // Escribir como Unix timestamp (compatible con Python time.time())
    FileWriteString(handle, IntegerToString((long)now));
    FileClose(handle);
}


//+------------------------------------------------------------------+
//| ReconnectWithBackoff                                             |
//|                                                                  |
//| Intenta reconectar al broker con backoff exponencial.            |
//| Delays: 5s, 10s, 20s, 40s, 80s... hasta max_attempts intentos.  |
//|                                                                  |
//| Devuelve true si la reconexion fue exitosa.                      |
//|                                                                  |
//| Uso en el EA (en OnDisconnect o cuando IsConnectionHealthy       |
//| devuelve false):                                                 |
//|   if (!IsConnectionHealthy()) {                                  |
//|       bool ok = ReconnectWithBackoff(5);                         |
//|       if (!ok) { Print("[EA] Reconexion fallida."); return; }    |
//|   }                                                              |
//+------------------------------------------------------------------+
bool ReconnectWithBackoff(int max_attempts = CM_DEFAULT_MAX_ATTEMPTS)
{
    int delay_ms = CM_BACKOFF_BASE_MS;

    for (int attempt = 1; attempt <= max_attempts; attempt++)
    {
        PrintFormat("[CM] Intento de reconexion %d/%d (delay anterior: %dms)...",
                    attempt, max_attempts, delay_ms);

        // Esperar antes de intentar (excepto en el primer intento)
        if (attempt > 1)
        {
            Sleep(delay_ms);
            delay_ms = delay_ms * 2;  // Backoff exponencial
        }

        // Verificar si la conexion se restablecion
        if (IsConnectionHealthy())
        {
            PrintFormat("[CM] Reconexion exitosa en intento %d.", attempt);
            _cm_disconnect_start = 0;
            _cm_was_connected = true;
            return true;
        }

        PrintFormat("[CM] Intento %d fallido. Siguiente en %dms.", attempt, delay_ms);
    }

    PrintFormat("[CM] Reconexion fallida tras %d intentos. Accion manual requerida.", max_attempts);
    return false;
}


//+------------------------------------------------------------------+
//| MonitorConnectionState                                           |
//|                                                                  |
//| Funcion auxiliar para llamar en OnTick() junto con SendHeartbeat.|
//| Detecta cambios de estado de conexion y los registra en el log.  |
//|                                                                  |
//| Uso en el EA:                                                    |
//|   void OnTick() {                                                |
//|       SendHeartbeat("C:\\trading-lab\\heartbeat.txt");           |
//|       MonitorConnectionState();                                  |
//|       if (!CheckPreTradeConnection()) return;                    |
//|       // logica del EA                                           |
//|   }                                                              |
//+------------------------------------------------------------------+
void MonitorConnectionState()
{
    bool connected = IsConnectionHealthy();

    if (!connected && _cm_was_connected)
    {
        // Acaba de perder la conexion
        _cm_disconnect_start = TimeGMT();
        _cm_was_connected = false;
        PrintFormat("[CM] Conexion perdida a las %s (UTC)",
                    TimeToString(_cm_disconnect_start, TIME_DATE | TIME_SECONDS));
    }
    else if (connected && !_cm_was_connected)
    {
        // Conexion restaurada
        int downtime = (int)(TimeGMT() - _cm_disconnect_start);
        PrintFormat("[CM] Conexion restaurada. Tiempo sin conexion: %ds", downtime);
        _cm_disconnect_start = 0;
        _cm_was_connected = true;
    }
    else if (!connected && !_cm_was_connected)
    {
        // Sigue sin conexion — loguear cada 60 segundos
        int downtime = (int)(TimeGMT() - _cm_disconnect_start);
        if (downtime % 60 == 0)
        {
            PrintFormat("[CM] Sin conexion desde hace %ds", downtime);
        }
    }
}


//+------------------------------------------------------------------+
//| EJEMPLO DE INTEGRACION COMPLETA EN UN EA EXPORTADO              |
//+------------------------------------------------------------------+
/*

// Al inicio del archivo .mq5 exportado:
#include "ftmo-timezone-sync.mq5"
#include "ConnectionMonitor.mqh"

// Parametros de configuracion
input string HeartbeatFile   = "C:\\trading-lab\\heartbeat.txt";
input double DailyLossLimit  = 3.5;    // % DD diario para cerrar todo
input int    PreResetMinutes = 5;      // Minutos antes del reset Prague

// En OnTick():
void OnTick()
{
    // 1. Heartbeat + estado de conexion
    SendHeartbeat(HeartbeatFile);
    MonitorConnectionState();

    // 2. Verificacion pre-trade de conexion
    if (!CheckPreTradeConnection()) return;

    // 3. Reset diario Prague
    CheckDailyReset();

    // 4. Pre-Reset Protection
    if (IsDailyResetApproaching(PreResetMinutes))
    {
        double dd = GetCurrentDailyDrawdown();
        if (dd > DailyLossLimit)
        {
            Print("[EA] Pre-Reset Protection. DD=", dd, "%. Cerrando posiciones.");
            CloseAllPositions();
            return;
        }
    }

    // 5. Daily loss limit
    if (GetCurrentDailyDrawdown() >= DailyLossLimit)
    {
        Print("[EA] Daily loss limit alcanzado. Suspendiendo entradas.");
        return;
    }

    // 6. Logica normal del EA exportado desde SQ
    // ... (generada por SQ, no modificar)
}

*/
//+------------------------------------------------------------------+
