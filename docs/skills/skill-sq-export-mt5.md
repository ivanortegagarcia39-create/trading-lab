# Skill: Exportacion de Estrategias SQ a MT5

## Proposito
Guia para el export-specialist.
Define el proceso completo para exportar una
estrategia aprobada de StrategyQuant X a un
EA (Expert Advisor) operativo en MT5.

---

## VERIFICACION OBLIGATORIA PRE-EXPORTACION

Antes de exportar cualquier estrategia, ejecutar
los siguientes pasos en orden. Si alguno falla,
no avanzar al siguiente.

### Paso 0a — Auditoria MQL5 obligatoria

Ejecutar el auditor antes de subir el EA a MT5:
```
python scripts/mql5-auditor.py --file [ruta_al_mq5] --ollama-url http://localhost:11434
```

El auditor debe retornar APPROVE (exit code 0).
Si retorna REVIEW (exit code 1): revisar los warnings.
Si retorna REJECT (exit code 2): NO exportar — corregir o descartar.

El resultado queda registrado automaticamente en:
results/approved/[nombre-estrategia]/mql5-audit.json

### Paso 0b — Test unitario en MT5 (1 mes rapido)

Despues de compilar en MT5 y antes del forward test real,
ejecutar un backtest de verificacion de 1 mes reciente:
- Symbol: [simbolo correcto]
- Period: H1
- Model: Every tick based on real ticks
- Date: ultimos 30 dias
- Deposit: 25000

Criterio de aprobacion: el EA ejecuta al menos 1 trade.
Si no ejecuta ningun trade en 30 dias: problema de configuracion
→ revisar simbolo, temporalidad y condiciones antes de continuar.

---

## REQUISITOS PREVIOS

Antes de exportar verificar:
- Estrategia en results\approved\ con todos
  los informes completos
- MT5 instalado y conectado a cuenta demo
  de la prop firm objetivo
- SQ X version actualizada

---

## PROCESO DE EXPORTACION EN SQ

### Paso 1: Abrir la estrategia en SQ
- Abrir SQ → Builder o Retester
- Cargar la estrategia desde results\approved\
- Verificar que los parametros son los correctos:
  * Simbolo correcto
  * Temporalidad H1
  * SL y TP ATR-based
  * Riesgo 1%

### Paso 2: Exportar a MQL5
- En SQ con la estrategia abierta
- Clic en "Export" o "Exportar"
- Seleccionar formato: MQL5 (MetaTrader 5)
- Seleccionar opciones de exportacion:
  * Include money management: SI
  * Risk percent: 1.0
  * Use ATR for SL/TP: SI
  * Magic number: asignar numero unico (ej: 12345)

### Paso 3: Guardar el archivo exportado
Guardar el archivo .mq5 en:
C:\Users\ivano\trading-lab\results\approved\
[nombre-estrategia]\[nombre].mq5

---

## CONFIGURACION EN MT5

### Paso 1: Compilar el EA
- Abrir MT5 → Tools → MetaEditor (F4)
- File → Open → buscar el archivo .mq5
- Compilar con F7
- Verificar 0 errores y 0 warnings criticos

### Paso 2: Parametros del EA en MT5
Al activar el EA verificar estos parametros:

Simbolo: [correcto para la prop firm]
EURUSD en FTMO puede aparecer como:
- EURUSD (sin sufijo)
- EURUSD. (con punto)
- EURUSDm (con m)
Verificar el nombre exacto en el broker de la prop firm.

Temporalidad: H1 — CRITICO
No activar el EA en temporalidad incorrecta.

Gestion del dinero:
- Risk mode: Percent of balance
- Risk percent: 1.0
- NO usar lote fijo

Horario de trading:
- Start hour: 8
- End hour: 20
- Trade on Friday: SI con cierre antes de fin sesion
- Trade on weekends: NO

Max trades por dia: 2

### Paso 3: Verificar simbolo correcto
Cada prop firm usa nombres de simbolos diferentes.
FTMO con Eightcap: EURUSD (sin sufijo)
FTMO con Purple Trading: verificar en la plataforma
Antes de activar en cuenta real verificar en demo.

---

## BACKTEST DE VERIFICACION EN MT5

### Configuracion del Strategy Tester
- Symbol: [simbolo correcto]
- Period: H1
- Model: Every tick based on real ticks
- Date: 2021.01.01 a fecha actual
- Deposit: 25000
- Currency: USD
- Leverage: 1:100

### Criterios de aceptacion
El backtest de MT5 debe ser consistente con
el Retester de SQ:

| Metrica  | SQ Retester | MT5 Backtest | Diferencia max |
|----------|-------------|--------------|----------------|
| PF       | [valor]     | [valor]      | 10%            |
| DD max   | [valor]     | [valor]      | 15%            |
| Trades   | [valor]     | [valor]      | 20%            |

Si la diferencia supera estos limites:
→ investigar causa antes de continuar
→ posibles causas: simbolo incorrecto,
  temporalidad incorrecta, parametros distintos

---

## FORWARD TEST EN DEMO

### Duracion minima
2 semanas de operacion en cuenta demo de la
prop firm objetivo antes de activar en cuenta real.

### Que verificar
- El EA abre y cierra posiciones correctamente
- Los SL y TP se ejecutan en los niveles correctos
- El tamaño de posicion es correcto (1% del balance)
- El EA respeta el maximo de 2 trades por dia
- El EA no opera fuera del horario configurado
- El EA no opera los fines de semana

### Señales de problema en forward test
- EA no abre ninguna posicion en 2 semanas
  → verificar simbolo y temporalidad
- SL o TP no se ejecutan correctamente
  → revisar parametros de exportacion
- Tamaño de posicion incorrecto
  → revisar configuracion de money management
- EA opera fuera de horario
  → revisar configuracion de sesion

---

## CHECKLIST COMPLETO PRE-CHALLENGE

[ ] Estrategia en results\approved\ completa
[ ] Archivo .mq5 compilado sin errores en MT5
[ ] Backtest MT5 consistente con SQ (diferencia < 10%)
[ ] Forward test en demo completado (2 semanas)
[ ] Simbolo correcto para la prop firm elegida
[ ] Temporalidad H1 configurada
[ ] Riesgo 1% configurado correctamente
[ ] Max 2 trades por dia configurado
[ ] Horario 08:00-20:00 configurado
[ ] No opera fines de semana confirmado
[ ] Magic number unico asignado
[ ] performance-monitor preparado para activar
[ ] Decision humana final: SI

---

## PARAMETRO MAXSLIPPAGE — OBLIGATORIO EN CADA EA

Cada EA exportado debe tener configurado el parametro
MaxSlippagePips antes de activarse en produccion.
Este parametro rechaza ordenes si el slippage real
supera el umbral — proteccion critica para momentos
de baja liquidez o noticias economicas.

### Valores por activo

| Activo | MaxSlippagePips | Razon |
|--------|----------------|-------|
| XAUUSD | 50 pips | Spread alto y variable en Oro |
| EURUSD | 5 pips | Spread bajo y estable en majors |
| GBPUSD | 5 pips | Major — volatilidad moderada |
| USDJPY | 5 pips | Major — volatilidad moderada |
| AUDUSD | 5 pips | Major |
| NZDUSD | 8 pips | Menos liquido que otros majors |
| USDCAD | 8 pips | Sensible a datos petroleo |
| USDCHF | 8 pips | Historico de gaps por SNB |
| XAGUSD | 30 pips | Spread muy alto en Plata |
| Indices | 20 pips | Spread variable por sesion |
| Cripto | 100 pips | Spread muy variable |

Para activos no listados: usar 10 pips como valor conservador.

### Como configurar en SQ antes de exportar

SQ → Tab Opciones → MaxSlippage
Introducir el valor en pips segun la tabla.

Si SQ no tiene este parametro visible en la version actual:
→ anyadirlo manualmente en el archivo .mq5 exportado
→ declarar como input al inicio del archivo:
  input int MaxSlippagePips = [valor]; // Slippage maximo en pips

El export-specialist verifica que el parametro existe
y tiene el valor correcto antes de entregar el EA al
orchestrator para el forward test.

---

## PROTOCOLO DE FAILOVER VPS

El VPS donde corre MT5 es la infraestructura critica.
Un fallo del VPS puede resultar en posiciones abiertas
sin gestion activa — riesgo de violacion de limites FTMO.

### Configuracion MT5 para auto-recuperacion

En MT5 → Herramientas → Opciones → Expert Advisors:
[ ] Allow automated trading — ACTIVADO
[ ] Allow DLL imports — segun necesidad del EA
[ ] Disable when account is changed — DESACTIVADO
    (permite reconexion automatica)

### Protocolo de recuperacion automatica

Al reiniciarse MT5 tras un fallo de VPS:
1. MT5 se conecta automaticamente al broker
2. Los EAs se recargan con sus parametros guardados
3. El EA lee las posiciones abiertas existentes
   (OrderSelect por MagicNumber) y retoma el control
4. El performance-monitor detecta la reconexion
   y verifica que el EA esta activo dentro de los 5 minutos

### Alerta por inactividad del VPS

Si el performance-monitor no recibe datos del EA durante 10 minutos:
→ Registrar evento: "VPS-INACTIVO" en hash-logger
→ Notificar CASO 2 (alerta critica al humano):
  "ALERTA: VPS sin datos por 10 minutos.
   Posible fallo del VPS o desconexion de MT5.
   Cuenta: [prop firm] [numero]
   Posiciones abiertas al ultimo reporte: [numero]
   Accion requerida: verificar VPS y estado del EA."
→ El humano debe verificar manualmente el VPS

Umbral de 10 minutos: da tiempo suficiente para reconexiones
normales del broker sin generar falsos positivos, pero
es lo suficientemente corto para actuar antes de que
una posicion abierta viole el daily loss limit.

### Latencia recomendada

Latencia maxima aceptable entre VPS y broker: 5ms.
El broker de FTMO (Eightcap) tiene servidores en:
- Equinix LD4 (Londres) — recomendado para cuentas FTMO EU
- Equinix NY4 (Nueva York) — para cuentas FTMO US
Elegir VPS en el mismo datacenter que el servidor del broker.

---

## PROBLEMAS COMUNES Y SOLUCIONES

### EA no compila
Causa: version de SQ incompatible con MT5
Solucion: actualizar SQ o MT5 a ultima version

### Resultados muy diferentes entre SQ y MT5
Causa 1: simbolo incorrecto en MT5
Causa 2: temporalidad incorrecta
Causa 3: modelo de backtest diferente
Solucion: verificar cada parametro uno por uno

### EA no opera en forward test
Causa 1: simbolo no disponible en el broker
Causa 2: EA no activado correctamente (boton verde)
Causa 3: horario de trading muy restrictivo
Solucion: verificar simbolo y configuracion

### Tamaño de posicion incorrecto
Causa: money management configurado como lote fijo
Solucion: cambiar a riesgo porcentual en parametros