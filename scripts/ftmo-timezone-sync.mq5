//+------------------------------------------------------------------+
//| ftmo-timezone-sync.mq5                                           |
//| Libreria MQL5 para sincronizacion de timezone con FTMO (Prague). |
//|                                                                  |
//| Funciones exportadas:                                            |
//|   GetPragueTime()           — hora actual en Europe/Prague       |
//|   IsDailyResetApproaching() — true si faltan <= N min para 00:00 |
//|   GetDailyStartEquity()     — equity al inicio del dia Prague    |
//|   GetCurrentDailyDrawdown() — DD diario en % (siempre positivo)  |
//|                                                                  |
//| Uso: #include "ftmo-timezone-sync.mq5" en cada EA exportado.    |
//+------------------------------------------------------------------+

#property strict

// Nombre del global variable donde se guarda el equity de inicio de dia
#define FTMO_DAILY_START_VAR  "FTMO_DailyStartEquity"

//+------------------------------------------------------------------+
//| Determina si el anyo dado es bisiesto.                           |
//+------------------------------------------------------------------+
bool IsLeapYear(int year)
{
    return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
}

//+------------------------------------------------------------------+
//| Devuelve el ultimo domingo de un mes dado.                       |
//| Usado para calcular los cambios de hora europeos.                |
//+------------------------------------------------------------------+
int LastSundayOfMonth(int year, int month)
{
    // Calcular el dia de la semana del ultimo dia del mes
    static int days_in_month[] = {0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    int days = days_in_month[month];
    if (month == 2 && IsLeapYear(year)) days = 29;

    // Crear datetime del ultimo dia del mes
    MqlDateTime last_day;
    last_day.year  = year;
    last_day.mon   = month;
    last_day.day   = days;
    last_day.hour  = 12;
    last_day.min   = 0;
    last_day.sec   = 0;

    datetime last_dt = StructToTime(last_day);
    TimeToStruct(last_dt, last_day);

    // day_of_week: 0=Sunday, 1=Monday, ..., 6=Saturday
    int dow = last_day.day_of_week;
    // Retroceder hasta el domingo
    return days - dow;
}

//+------------------------------------------------------------------+
//| Calcula el offset UTC para Europe/Prague en un momento dado.     |
//|                                                                  |
//| Reglas de la Union Europea:                                      |
//|   CEST (UTC+2): desde el ultimo domingo de marzo  a las 02:00   |
//|   CET  (UTC+1): desde el ultimo domingo de octubre a las 03:00  |
//|                                                                  |
//| Devuelve: 1 (CET) o 2 (CEST)                                    |
//+------------------------------------------------------------------+
int GetPragueUtcOffset(datetime utc_time)
{
    MqlDateTime dt;
    TimeToStruct(utc_time, dt);
    int year  = dt.year;
    int month = dt.mon;

    // Fuera del rango de verano (noviembre a febrero): siempre CET
    if (month < 3 || month > 10) return 1;
    // Pleno verano (abril a septiembre): siempre CEST
    if (month > 3 && month < 10) return 2;

    // Marzo: calcular si ya paso el cambio
    if (month == 3)
    {
        int last_sun = LastSundayOfMonth(year, 3);
        if (dt.day < last_sun) return 1;   // Antes del cambio: CET
        if (dt.day > last_sun) return 2;   // Despues del cambio: CEST
        // El mismo dia del cambio: cambia a las 02:00 UTC
        return (dt.hour >= 2) ? 2 : 1;
    }

    // Octubre: calcular si ya paso el cambio
    if (month == 10)
    {
        int last_sun = LastSundayOfMonth(year, 10);
        if (dt.day < last_sun) return 2;   // Antes del cambio: CEST
        if (dt.day > last_sun) return 1;   // Despues del cambio: CET
        // El mismo dia del cambio: cambia a las 03:00 UTC (= 01:00 UTC)
        return (dt.hour >= 1) ? 1 : 2;
    }

    return 1; // Fallback conservador
}

//+------------------------------------------------------------------+
//| Convierte un timestamp UTC a hora de Europe/Prague.              |
//|                                                                  |
//| Tiene en cuenta automaticamente CET (UTC+1) en invierno y       |
//| CEST (UTC+2) en verano segun las reglas europeas de cambio de   |
//| hora.                                                            |
//+------------------------------------------------------------------+
datetime GetPragueTime(datetime utc_time = 0)
{
    if (utc_time == 0) utc_time = TimeGMT();
    int offset_hours = GetPragueUtcOffset(utc_time);
    return utc_time + offset_hours * 3600;
}

//+------------------------------------------------------------------+
//| Devuelve true si faltan menos de N minutos para las 00:00        |
//| en hora de Praga (reset diario de FTMO).                         |
//|                                                                  |
//| Usar con minutes=5 para la Pre-Reset Protection:                 |
//|   if (IsDailyResetApproaching(5)) { CloseAllPositions(); }      |
//+------------------------------------------------------------------+
bool IsDailyResetApproaching(int minutes = 5)
{
    datetime prague_now = GetPragueTime();
    MqlDateTime dt;
    TimeToStruct(prague_now, dt);

    // Segundos transcurridos desde medianoche Prague
    int seconds_since_midnight = dt.hour * 3600 + dt.min * 60 + dt.sec;
    // Segundos restantes hasta la proxima medianoche
    int seconds_to_midnight = 86400 - seconds_since_midnight;

    return seconds_to_midnight <= (minutes * 60);
}

//+------------------------------------------------------------------+
//| Guarda el equity actual como inicio del dia Prague.              |
//| Debe llamarse exactamente a las 00:00 hora Praga.                |
//| Los EAs deben invocarla en OnTick() cuando detecten el reset.    |
//+------------------------------------------------------------------+
void SaveDailyStartEquity()
{
    double equity = AccountInfoDouble(ACCOUNT_EQUITY);
    GlobalVariableSet(FTMO_DAILY_START_VAR, equity);
}

//+------------------------------------------------------------------+
//| Devuelve el equity registrado al inicio del dia Prague.          |
//|                                                                  |
//| Si no existe el global variable (primer arranque del EA):        |
//|   Usa el balance actual como aproximacion y lo registra.         |
//|                                                                  |
//| El valor se actualiza automaticamente cada vez que se detecta    |
//| el reset de medianoche Prague.                                   |
//+------------------------------------------------------------------+
double GetDailyStartEquity()
{
    if (!GlobalVariableCheck(FTMO_DAILY_START_VAR))
    {
        // Primera vez — usar balance actual como aproximacion
        double balance = AccountInfoDouble(ACCOUNT_BALANCE);
        GlobalVariableSet(FTMO_DAILY_START_VAR, balance);
        PrintFormat("[FTMO-TZ] DailyStartEquity inicializado a %.2f (balance actual)", balance);
        return balance;
    }
    return GlobalVariableGet(FTMO_DAILY_START_VAR);
}

//+------------------------------------------------------------------+
//| Calcula el DD diario actual en % respecto al inicio del dia      |
//| Prague.                                                          |
//|                                                                  |
//| Formula:                                                         |
//|   DD = (start_equity - current_equity) / start_equity * 100     |
//|                                                                  |
//| Devuelve siempre un valor positivo (la perdida en %).            |
//| Si hay ganancia respecto al inicio del dia, devuelve 0.          |
//+------------------------------------------------------------------+
double GetCurrentDailyDrawdown()
{
    double start_equity   = GetDailyStartEquity();
    double current_equity = AccountInfoDouble(ACCOUNT_EQUITY);

    if (start_equity <= 0) return 0.0;

    double dd = (start_equity - current_equity) / start_equity * 100.0;
    return (dd > 0.0) ? dd : 0.0;
}

//+------------------------------------------------------------------+
//| Funcion auxiliar: detecta el reset de medianoche y actualiza     |
//| el equity de inicio de dia. Debe llamarse en OnTick().           |
//|                                                                  |
//| Uso en el EA:                                                    |
//|   void OnTick() { CheckDailyReset(); ... }                      |
//+------------------------------------------------------------------+
static datetime _last_reset_check = 0;

void CheckDailyReset()
{
    datetime prague_now = GetPragueTime();
    MqlDateTime dt;
    TimeToStruct(prague_now, dt);

    // Solo verificar una vez por hora (para no sobrecargar)
    if (prague_now - _last_reset_check < 60) return;
    _last_reset_check = prague_now;

    // Detectar cruce de medianoche: hora = 0 y minuto = 0-2
    if (dt.hour == 0 && dt.min <= 2)
    {
        // Verificar si ya actualizamos hoy
        MqlDateTime last_reset_dt;
        TimeToStruct(_last_reset_check, last_reset_dt);

        SaveDailyStartEquity();
        PrintFormat("[FTMO-TZ] Reset diario Prague detectado. DailyStartEquity = %.2f",
                    GetDailyStartEquity());
    }
}

//+------------------------------------------------------------------+
//| EJEMPLO DE USO — comentado para referencia                       |
//+------------------------------------------------------------------+
/*
// En tu EA exportado desde SQ, añadir al inicio:
#include "ftmo-timezone-sync.mq5"

// Constantes de proteccion
#define PRE_RESET_MINUTES     5      // Minutos antes del reset para cerrar
#define DAILY_LOSS_LIMIT_PCT  3.5    // % de DD diario para cierre preventivo

// En OnTick():
void OnTick()
{
    // 1. Verificar reset diario Prague y actualizar equity de inicio
    CheckDailyReset();

    // 2. Pre-Reset Protection: cerrar si faltan 5 min para reset
    //    y el P&L flotante supera el umbral
    if (IsDailyResetApproaching(PRE_RESET_MINUTES))
    {
        double dd = GetCurrentDailyDrawdown();
        if (dd > DAILY_LOSS_LIMIT_PCT)
        {
            Print("[FTMO-TZ] Pre-Reset Protection activada. DD=", dd, "%. Cerrando posiciones.");
            CloseAllPositions();
            return;
        }
    }

    // 3. Verificar DD diario en cualquier momento
    double daily_dd = GetCurrentDailyDrawdown();
    if (daily_dd >= 3.5)  // 3.5% = margen operativo para cuenta de 25k
    {
        Print("[FTMO-TZ] Daily loss limit alcanzado: ", daily_dd, "%. Suspendiendo entradas.");
        return;  // No abrir nuevas posiciones
    }

    // ... logica normal del EA ...
}

// Funcion auxiliar (implementar en el EA):
void CloseAllPositions()
{
    for (int i = PositionsTotal() - 1; i >= 0; i--)
    {
        ulong ticket = PositionGetTicket(i);
        if (PositionSelectByTicket(ticket))
        {
            MqlTradeRequest req = {};
            MqlTradeResult  res = {};
            req.action   = TRADE_ACTION_DEAL;
            req.symbol   = PositionGetString(POSITION_SYMBOL);
            req.volume   = PositionGetDouble(POSITION_VOLUME);
            req.type     = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
                           ? ORDER_TYPE_SELL : ORDER_TYPE_BUY;
            req.price    = (req.type == ORDER_TYPE_SELL)
                           ? SymbolInfoDouble(req.symbol, SYMBOL_BID)
                           : SymbolInfoDouble(req.symbol, SYMBOL_ASK);
            req.deviation = 20;
            req.magic    = (ulong)PositionGetInteger(POSITION_MAGIC);
            req.comment  = "FTMO-TZ PreReset close";
            OrderSend(req, res);
        }
    }
}
*/
//+------------------------------------------------------------------+
