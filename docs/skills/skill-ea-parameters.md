# Skill: Parámetros de EA para TradingLab

## Propósito
Define todos los parámetros que debe incluir cada EA exportado desde SQ
para operar correctamente en producción bajo las reglas FTMO.
Verificar que el EA exportado tenga todos los parámetros obligatorios
antes de desplegarlo en VPS.

---

## PARÁMETROS OBLIGATORIOS

Todos los EAs exportados desde SQ deben exponer estos parámetros:

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| Risk | double | 1.0 | Porcentaje de riesgo por trade sobre capital |
| MagicNumber | int | (único) | Identificador único del EA — no repetir entre EAs |
| MaxSlippagePips | int | (por activo) | Límite de slippage aceptado — ver tabla por activo |
| UseNewsFilter | bool | true | Activar filtro de noticias antes de abrir posición |
| NewsFilterMinutes | int | 15 | Ventana de protección en minutos antes/después |
| UseDynamicSpreadProtection | bool | true | No operar si spread > MaxSpreadMultiplier × spread_ref |
| MaxSpreadMultiplier | double | 3.0 | Factor máximo de spread permitido |
| CloseOnFriday | bool | true | Cerrar todas las posiciones el viernes |
| FridayCloseHour | int | 20 | Hora UTC de cierre viernes (20 UTC = 22 CEST) |
| UseHeartbeat | bool | true | Escribir archivo de heartbeat para vps-health-monitor |
| HeartbeatFile | string | (ruta VPS) | Ruta absoluta al archivo de heartbeat en el VPS |

---

## PARÁMETROS OPCIONALES

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| MaxDailyTrades | int | 2 | Máximo número de trades por día |
| TradingStartHour | int | 6 | Hora UTC de inicio de sesión de trading |
| TradingEndHour | int | 18 | Hora UTC de fin de sesión de trading |
| UseAntiSync | bool | true | Añadir delay aleatorio para evitar sincronización entre EAs |
| AntiSyncMinMs | int | 500 | Delay mínimo en milisegundos |
| AntiSyncMaxMs | int | 3500 | Delay máximo en milisegundos |

---

## VALORES POR ACTIVO

### MaxSlippagePips por activo

| Activo | MaxSlippagePips | Justificación |
|--------|----------------|---------------|
| XAUUSD | 50 | Metal volátil — slippage alto en noticias |
| EURUSD | 5 | Par líquido — slippage bajo |
| GBPUSD | 5 | Par líquido — slippage bajo |
| USDJPY | 5 | Par líquido — slippage bajo |
| USDCHF | 5 | Par líquido — slippage bajo |
| AUDUSD | 5 | Par líquido — slippage bajo |
| XAGUSD | 15 | Metal — slippage medio |
| Índices | 20 | Variable según índice |

### Risk por tamaño de portfolio

| Estrategias activas | Risk % |
|---------------------|--------|
| 1-2 | 1.0% |
| 3 | 1.0% |
| 4 | 0.9% |
| 5 | 0.8% |
| 6+ | 0.6% |
| 8 | 0.5% |

El portfolio-builder.py calcula el Risk óptimo automáticamente.
No modificar manualmente el Risk sin consultar la tabla de portfolio.

---

## MAGIC NUMBER

El MagicNumber identifica unívocamente cada EA en la cuenta.
Dos EAs con el mismo MagicNumber se interferirán mutuamente.

Convención TradingLab:

```
MagicNumber = BUILD * 10000 + ESTRATEGIA_NUM
Ejemplo: Build 11, estrategia 3 → MagicNumber = 110003
```

El export-specialist asigna el MagicNumber automáticamente.
Nunca reutilizar un MagicNumber de una estrategia descartada.

---

## NEWS FILTER

### Cómo funciona UseNewsFilter = true

1. EA llama a función `IsNewsTime()` antes de cada señal de entrada
2. Si hay noticia HIGH impact en ventana ±NewsFilterMinutes → no abrir posición
3. Si hay posición abierta cuando comienza la ventana → mantener (no cerrar)
4. Tras la ventana → reanudar operativa normal

### Eventos que bloquean entradas (XAUUSD)

| Evento | Ventana | Impacto |
|--------|---------|---------|
| NFP (primer viernes del mes) | ±60 min | Muy alto |
| FOMC Statement | ±60 min | Muy alto |
| CPI USA | ±30 min | Alto |
| PPI USA | ±30 min | Alto |
| Retail Sales USA | ±30 min | Alto |
| GDP USA | ±30 min | Alto |
| BCE Decision tipos | ±30 min | Alto |

El script news-filter-checker.py verifica el estado antes de operar manualmente.

---

## DYNAMIC SPREAD PROTECTION (DSP)

### Cómo funciona UseDynamicSpreadProtection = true

1. EA obtiene spread actual del símbolo en MT5
2. Calcula factor = spread_actual / spread_referencia
3. Si factor >= MaxSpreadMultiplier (3.0) → no abrir posición
4. Log interno: "DSP activo — spread {X}x del normal"

### Spread de referencia por activo

| Activo | Spread referencia | DSP activado si spread > |
|--------|------------------|--------------------------|
| XAUUSD | 30 pips | 90 pips |
| EURUSD | 0.5 pips | 1.5 pips |
| GBPUSD | 0.8 pips | 2.4 pips |
| USDJPY | 0.5 pips | 1.5 pips |

El script spread-monitor.py verifica el estado actual del spread.

---

## HEARTBEAT

### Cómo funciona UseHeartbeat = true

El EA escribe un timestamp en HeartbeatFile cada X minutos.
El vps-health-monitor.py verifica que el archivo se actualice.
Si el archivo no se actualiza en >15 minutos → alerta CRITICAL en Telegram.

```
HeartbeatFile = C:\TradingLab\heartbeat\EA_XAUUSD_B11.txt
Contenido: 2026-04-28 14:32:00
```

Verificación manual:
```powershell
Get-Content C:\TradingLab\heartbeat\EA_XAUUSD_B11.txt
```

---

## ANTISYNC

### Por qué usar UseAntiSync = true

Si múltiples EAs del portfolio reciben la misma señal simultáneamente,
el broker puede detectarlo como operativa coordinada.
El delay aleatorio (500ms-3500ms) evita que las órdenes lleguen juntas.

Esto no afecta el rendimiento del EA en backtesting pero sí en producción.
En backtesting no tiene efecto (el parámetro se ignora en modo histórico).

---

## CIERRE EN VIERNES

### Por qué CloseOnFriday = true

FTMO cobra triple swap el miércoles por el fin de semana.
Las posiciones abiertas el viernes hasta el lunes incurren en:
- Riesgo de gap de apertura del lunes
- Swap adicional del fin de semana

FridayCloseHour = 20 UTC → cierre a las 22:00 CEST.
El mercado XAUUSD cierra a las 21:00 UTC → cierre antes del fin de mercado.

---

## VERIFICACIÓN PRE-DEPLOY

Antes de desplegar el EA en VPS, verificar con mql5-auditor.py:

```bash
python scripts/mql5-auditor.py --file EAs/XAUUSD_B11_S001.ex5
```

El auditor verifica:
- Que todos los parámetros obligatorios están presentes
- Que MagicNumber es único en el registro
- Que los valores por defecto coinciden con la tabla por activo
- Que el código no tiene hardcoded el símbolo

---

## Referencias

- `scripts/news-filter-checker.py` — verificar noticias antes de operar
- `scripts/spread-monitor.py` — verificar spread actual
- `scripts/mql5-auditor.py` — auditar código MQL5
- `scripts/vps-health-monitor.py` — monitorear heartbeat en producción
- `docs/skills/skill-forward-test-protocol.md` — protocolo de forward test
- `docs/skills/skill-mt5-deployment.md` — despliegue en VPS
- `config/build-defaults.json` — spreads de referencia por activo
