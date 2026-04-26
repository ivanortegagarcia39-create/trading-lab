# Skill: Deployment de EAs en MetaTrader 5

## Proposito

Define el proceso completo de deployment de estrategias
aprobadas en MetaTrader 5 — desde la verificacion previa
hasta el monitoreo en produccion.
El deployment es la ultima frontera antes del capital real.
Un error aqui puede destruir un challenge en minutos.

---

## PRE-DEPLOYMENT CHECKLIST (obligatorio)

Antes de desplegar cualquier EA — en demo o funded.
El export-specialist verifica cada item. Sin excepciones.

### Verificacion de codigo

- [ ] mql5-auditor.py → resultado APPROVE
  Si resultado es REJECT → no continuar hasta corregir.
  Ver scripts/mql5-auditor.py para criterios exactos.

- [ ] Unit test en MT5 Strategy Tester (1 mes de datos)
  Verificar que: abre trades, cierra por SL/TP, sin errores en Journal.
  El test debe mostrar al menos 1 ciclo completo (entrada + salida).

### Verificacion de parametros del EA

- [ ] MagicNumber: unico para esta estrategia en todas las cuentas
  Consultar coordination-detector.py para verificar que no hay colision.
  Un MagicNumber duplicado puede mezclar posiciones de dos EAs.

- [ ] Risk: configurado como porcentaje (no lotes fijos)
  Valor default: 1% (ajustar segun portfolio — ver skill-capital-management.md)

- [ ] MaxSlippagePips: configurado segun el activo
  | Activo | MaxSlippagePips |
  |--------|-----------------|
  | XAUUSD | 50 |
  | EURUSD | 5 |
  | GBPUSD | 5 |
  | Indices | 10 |

- [ ] Simbolo del broker verificado contra el simbolo del backtest
  El nombre exacto puede diferir (ej: XAUUSD vs XAUUSDm).
  Un simbolo incorrecto → el EA no abre posiciones.

### Verificacion de librerias

- [ ] ConnectionMonitor.mqh incluido y activo
  Heartbeat habilitado: SendHeartbeat() en OnTick().
  Pre-trade check: CheckPreTradeConnection() antes de cada orden.

- [ ] ftmo-timezone-sync.mq5 activo
  GetCurrentDailyDrawdown() usando timezone Prague.
  CheckDailyReset() llamado en cada tick.
  Sin esto el DD diario se puede calcular mal y violar la regla FTMO.

---

## DEPLOYMENT EN DEMO (FORWARD TEST)

Requisito previo: pre-deployment checklist completo.

### Pasos

```
1. Compilar .ex5 desde .mq5 en MetaEditor
   Si hay errores de compilacion → corregir antes de continuar.

2. Copiar .ex5 al VPS (o cuenta demo en MT5 local)
   Ruta: MetaTrader5/MQL5/Experts/TradingLab/[nombre-ea].ex5

3. Abrir MT5 y conectar al broker demo de la prop firm
   FTMO: crear cuenta demo gratuita en ftmo.com
   Usar el servidor demo de la MISMA prop firm del challenge.

4. Abrir grafico del activo en H1
   Verificar que el simbolo existe en Market Watch.

5. Arrastrar el EA al grafico
   Configurar parametros:
     MagicNumber: [valor unico]
     Risk: [1% o ajustado]
     MaxSlippagePips: [segun activo]
   Activar AutoTrading (boton verde arriba).
   Verificar cara sonriente en esquina superior derecha del grafico.

6. Verificar heartbeat en logs
   results/production-logs/ debe recibir archivo de heartbeat.
   Si no hay heartbeat en 5 min → revisar configuracion.

7. Actualizar strategies-registry.json:
   estado: "demo"
   fecha_deploy_demo: [ISO-8601]
   cuenta_demo: [ID de cuenta]
```

### Checklist diario durante el forward test

Ver skill-forward-test-protocol.md para el checklist completo.
Minimo: verificar EA activo (cara sonriente) + sin errores en Journal.

---

## DEPLOYMENT EN FUNDED (POST-CHALLENGE)

Requisito previo: challenge pasado (Fase 1 + Fase 2) + notificacion FTMO.

### Diferencias respecto al demo

El EA es identico — mismo codigo, mismos parametros basicos.
Solo cambian:

1. Cuenta: de demo a cuenta funded
   Abrir nueva conexion MT5 con credenciales de la cuenta funded.

2. Risk Manager con DD diario FTMO:
   Daily Loss Limit FTMO: 5% = 500 USD (cuenta 10k)
   Margen operativo: 4.8% = 480 USD (buffer 20 USD)
   Configurar en EA: MaxDailyLoss = 480 (en USD absolutos o % segun EA)

3. Confirmacion timezone sync:
   GetPragueOffset() devuelve offset correcto para la fecha actual.
   Verificar con una llamada de prueba antes del primer trade.

4. Notificacion de inicio en Telegram:
   "EA DESPLEGADO EN FUNDED
    Cuenta: [ID] — Firma: FTMO
    Activo: [ACTIVO] | TF: H1
    Risk: [X]% | MagicNumber: [N]
    DD diario max: 4.8% = [N] USD
    DD total max: 9.5% = [N] USD"

5. Actualizar strategies-registry.json:
   estado: "funded"
   fecha_deploy_funded: [ISO-8601]
   cuenta_funded: [ID]

6. Iniciar periodo de observacion de 4 semanas
   scaling-manager inicia el conteo del periodo de 4 meses.
   No escalar hasta completar las 4 semanas.

---

## PARAMETROS CRITICOS POR ACTIVO

| Activo | MaxSlippagePips | Spread tipico | Comision |
|--------|-----------------|---------------|----------|
| XAUUSD | 50 | 30 pips | 7 USD/lote |
| EURUSD | 5 | 0.5 pips | 7 USD/lote |
| GBPUSD | 5 | 0.8 pips | 7 USD/lote |
| USDJPY | 5 | 0.5 pips | 7 USD/lote |
| US30 | 10 | 5 ptos | variable |
| NAS100 | 10 | 5 ptos | variable |

El MaxSlippagePips no es el spread — es el slippage adicional
que el EA acepta antes de rechazar la ejecucion de una orden.
Un valor demasiado bajo puede causar que el EA no abra trades.
Un valor demasiado alto puede causar ejecuciones a precios malos.

---

## FAILOVER EN VPS

### Si MT5 se cae o pierde conexion

El ConnectionMonitor.mqh detecta la caida automaticamente.
ReconnectWithBackoff() intenta reconectar (5s → 10s → 20s → 40s → 80s).
Si no reconecta en 5 intentos → log de error.
vps-health-monitor.py detecta el fallo de heartbeat y alerta.

### Si hay posiciones abiertas durante la caida

Al reconectar, MT5 verifica las posiciones abiertas automaticamente.
El EA las gestiona normalmente (SL/TP siguen activos en el servidor).
No hay perdida de posiciones por desconexion momentanea.

### Si la caida dura > 10 minutos

vps-health-monitor.py envia alerta Telegram CRITICA:
"MT5 SIN HEARTBEAT > 10 MIN
 Cuenta: [ID] — Activo: [ACTIVO]
 Ultima senal: [timestamp]
 Posiciones abiertas: verificar en MT5 web"

El humano interviene para verificar el estado del VPS.

### Force restart

Si MT5 esta congelado (proceso existe pero sin actividad):
vps-health-monitor.py ejecuta force_restart_mt5() (Windows):
  taskkill /F /IM terminal64.exe
  Relaunch tras 30 segundos.
Disponible solo en VPS Windows.

---

## LO QUE ESTA SKILL NUNCA HACE

NUNCA despliega en funded sin haber pasado el forward test demo.
NUNCA usa lotes fijos — siempre porcentaje del balance.
NUNCA omite la verificacion del MagicNumber unico.
NUNCA despliega sin ConnectionMonitor.mqh activo.
NUNCA despliega sin ftmo-timezone-sync.mq5 activo.
NUNCA escala antes de las 4 semanas de observacion en funded.
NUNCA ignora errores en el Journal de MT5 durante el unit test.
