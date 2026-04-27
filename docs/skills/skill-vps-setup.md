# skill-vps-setup.md — Configuración VPS para TradingLab

## Propósito
Guía para provisionar y configurar el VPS que ejecuta MT5 + EAs en producción.

---

## Requisitos mínimos

| Parámetro | Valor |
|-----------|-------|
| Ubicación | Equinix LD4 — Londres |
| Latencia objetivo | < 5 ms al bróker |
| OS | Windows Server 2019/2022 |
| RAM | 4 GB mínimo (8 GB recomendado) |
| Almacenamiento | 60 GB SSD |
| Coste mensual | $12–20/mes |

---

## Proveedores recomendados

### FXVPS
- Latencia: 1–3 ms a brokers LD4
- Precio: ~$20/mes (plan básico Windows)
- URL de referencia: fxvps.com
- Datacenter: Equinix LD4

### ForexVPS
- Latencia: 2–5 ms
- Precio: ~$15/mes
- Datacenter: LD4 / NY4 según plan

**Criterio de selección:** menor latencia al bróker objetivo, no menor precio.

---

## Instalación de MT5

### 1. Descarga e instalación
```
1. Descargar MetaTrader5Setup.exe desde el bróker objetivo
2. Instalar en C:\Program Files\MetaTrader 5\
3. Iniciar sesión con cuenta de la prop firm
4. Verificar conexión al servidor del bróker
```

### 2. Copiar EAs exportados desde SQ
```
Ruta destino:
C:\Users\<usuario>\AppData\Roaming\MetaQuotes\Terminal\
  <ID_TERMINAL>\MQL5\Experts\TradingLab\

Archivos a copiar:
  *.ex5    — EA compilado (generado por SQ export)
  *.set    — parámetros de configuración
```

### 3. Adjuntar EA al gráfico
```
1. Abrir gráfico del activo en H1
2. Arrastrar el .ex5 desde el Navigator al gráfico
3. Cargar el .set correspondiente
4. Verificar que "Algo trading" esté habilitado (botón verde)
5. Confirmar log sin errores en la pestaña Experts
```

---

## Auto-restart con tarea programada Windows

### Crear tarea en Task Scheduler
```
1. Abrir Task Scheduler → "Create Basic Task"
2. Nombre: MT5_AutoRestart
3. Trigger: "When the computer starts" + "Daily at 00:05"
4. Action: Start a program
   Programa: "C:\Program Files\MetaTrader 5\terminal64.exe"
   Argumentos: /portable
5. Conditions: desmarcar "Start only if on AC power"
6. Settings: marcar "Run task as soon as possible after missed start"
```

### Script de watchdog (opcional)
El script `scripts/vps-health-monitor.py` comprueba que MT5 está en ejecución
y lo reinicia si no responde. Ver sección siguiente.

---

## Configurar vps-health-monitor.py como servicio

### Instalar dependencia
```bash
pip install psutil requests
```

### Crear servicio con NSSM
```
1. Descargar nssm.exe (Non-Sucking Service Manager)
2. Ejecutar: nssm install VPSHealthMonitor
3. Path:        C:\Python311\python.exe
   Startup dir: C:\TradingLab\scripts\
   Arguments:   vps-health-monitor.py
4. En pestaña "Log on": cuenta de administrador local
5. nssm start VPSHealthMonitor
```

### Verificar estado
```powershell
nssm status VPSHealthMonitor
# Expected: SERVICE_RUNNING
```

### Comprobaciones del monitor
- MT5 process activo (`terminal64.exe`)
- EAs sin errores críticos en logs
- Ping al bróker < umbral configurado
- Alerta Telegram si alguna condición falla

---

## Checklist post-instalación

- [ ] MT5 conectado y mostrando precios en tiempo real
- [ ] EA adjunto al gráfico correcto con símbolo y H1
- [ ] Log Experts sin errores de inicialización
- [ ] Tarea programada de auto-restart creada
- [ ] vps-health-monitor.py corriendo como servicio
- [ ] Primera alerta INFO de Telegram recibida
- [ ] Latencia al bróker verificada (< 5 ms)
