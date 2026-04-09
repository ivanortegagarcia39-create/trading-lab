# Skill: Ejecucion del Challenge en Prop Firm

## Proposito
Guia para el propfirm-analyst y el export-specialist.
Define el proceso exacto para ejecutar un challenge
en una prop firm desde la compra hasta el primer
dia de operativa real.
Evita errores criticos en el momento mas importante.

---

## ANTES DE COMPRAR EL CHALLENGE

### Verificaciones obligatorias
Antes de gastar dinero en un challenge verificar:

[ ] La estrategia tiene informe de aprobacion completo
[ ] EA exportado y compilado en MT5 sin errores
[ ] Backtest MT5 consistente con SQ (diferencia < 10%)
[ ] Forward test en demo completado (minimo 2 semanas)
[ ] propfirm-analyst ha recomendado esta prop firm
[ ] El DD simulado < 70% del limite de la prop firm
[ ] Trades por mes >= 20 (alcanzable el objetivo)
[ ] Decision humana final: SI

### Seleccion del tamaño de cuenta
Para el primer challenge:
- Empezar con la cuenta mas pequeña disponible
- FTMO: cuenta de 10.000$ para el primer intento
- Si pasa → escalar a 25.000$ en Verification
- Si falla → analizar causa y repetir con 10.000$

Razon: minimizar el coste de aprendizaje.
Un challenge de 10.000$ en FTMO cuesta ~155 EUR.
Un challenge de 25.000$ cuesta ~250 EUR.

---

## PROCESO DE COMPRA DEL CHALLENGE

### FTMO 2-Step
1. Ir a ftmo.com
2. Seleccionar FTMO Challenge
3. Seleccionar 2-Step (NO el 1-Step)
4. Seleccionar tamaño: 10.000$ para empezar
5. Seleccionar divisa de la cuenta: USD
6. Completar el pago
7. Recibireis email con credenciales MT5

### Verificar el email de bienvenida
El email de FTMO incluye:
- Servidor MT5 de conexion
- Login de la cuenta
- Password
- Nombre del simbolo EUR/USD en ese broker
  (puede ser EURUSD, EURUSDm, EURUSD. etc)

---

## CONFIGURACION DEL MT5 PARA EL CHALLENGE

### Paso 1: Conectar MT5 al servidor de FTMO
1. Abrir MT5
2. File → Open an Account
3. Buscar el broker de FTMO (Eightcap o similar)
4. Introducir las credenciales del email
5. Verificar que la cuenta aparece conectada

### Paso 2: Verificar el simbolo correcto
CRITICO: el nombre del simbolo puede ser diferente
al que usamos en SQ.

En MT5 verificar exactamente como aparece EUR/USD:
- Ver en Market Watch el nombre exacto
- Puede ser: EURUSD, EURUSDm, EURUSD.
- Anotar el nombre exacto

### Paso 3: Ajustar el EA al simbolo correcto
Si el simbolo en MT5 es diferente al del backtest:
1. Abrir MetaEditor (F4 en MT5)
2. Abrir el archivo .mq5 del EA
3. Buscar el parametro de simbolo
4. Cambiar al nombre exacto del broker
5. Recompilar con F7
6. Verificar 0 errores

### Paso 4: Activar el EA en MT5
1. Abrir el grafico de EUR/USD H1
2. Verificar que la temporalidad es H1
3. Arrastrar el EA desde el Navigator al grafico
4. En la ventana de parametros verificar:
   - Risk percent: 1.0
   - Max trades per day: 2
   - Start hour: 8
   - End hour: 20
   - Magic number: [el asignado en la exportacion]
5. Activar el boton de AutoTrading (verde)
6. Verificar que el EA muestra cara sonriente
   en la esquina superior derecha del grafico

---

## PRIMER DIA DE OPERATIVA

### Verificaciones del primer dia
Al inicio del primer dia de trading:

[ ] MT5 conectado al servidor correctamente
[ ] EA activo con cara sonriente en el grafico
[ ] AutoTrading activado (boton verde arriba)
[ ] Balance correcto segun el tamaño del challenge
[ ] No hay posiciones abiertas de dias anteriores

### Que esperar el primer dia
- El EA puede no abrir ninguna posicion el primer dia
  si las condiciones de mercado no se cumplen
- Esto es NORMAL — no tocar nada
- El EA opera solo cuando se cumplen las condiciones
- No forzar trades manualmente

### Verificaciones durante el dia
Cada 2-3 horas verificar:
- MT5 sigue conectado al servidor
- EA sigue activo (cara sonriente)
- No hay errores en el journal de MT5
- Balance y equity dentro de los limites

---

## MONITOREO DIARIO DEL CHALLENGE

### Al final de cada dia de trading
1. Anotar en Obsidian → 06_Decisions:
   - Fecha
   - Trades ejecutados
   - Resultado del dia (+/- %)
   - DD acumulado
   - Distancia al daily loss limit
   - Distancia al max DD limit

2. Calcular distancia a limites:
   FTMO cuenta 10.000$:
   - Daily Loss Limit: 500$ (5%)
   - Max DD Limit: 1.000$ (10%)
   - Margen operativo daily: 300$ (3%)
   - Margen operativo max DD: 700$ (7%)

3. Activar alerta si:
   - DD diario > 300$ → ALERTA AMARILLA
   - DD diario > 400$ → ALERTA NARANJA
   - DD diario > 450$ → ALERTA ROJA — considerar
     cerrar posiciones manualmente

### Señales de problema durante el challenge
- EA no opera en 5 dias consecutivos
  → verificar conexion y parametros
- EA opera fuera del horario configurado
  → revisar parametros de sesion
- Tamaño de posicion incorrecto
  → revisar money management
- DD acumulado > 7%
  → activar protocolo de alerta del
  performance-monitor

---

## ERRORES CRITICOS A EVITAR

### Error 1: Operar manualmente durante el challenge
NUNCA abrir o cerrar posiciones manualmente
mientras el EA esta activo.
Puede crear confusion entre trades del EA
y trades manuales.
FTMO puede detectarlo como cambio de estrategia.

### Error 2: Cambiar parametros del EA durante el challenge
NUNCA cambiar los parametros del EA una vez
el challenge ha empezado.
Si hay un problema → pausar el EA y analizar
antes de cualquier cambio.

### Error 3: Ignorar las alertas de DD
Si el DD se acerca al limite → actuar inmediatamente.
No esperar a que se viole el limite.
Mejor pausar el EA y perder el challenge que
violar el limite y perder el deposito.

### Error 4: No verificar la conexion MT5 diariamente
Si MT5 se desconecta del servidor durante horas
el EA no opera y puede perder oportunidades.
Verificar conexion al inicio de cada sesion.

### Error 5: Usar el mismo magic number en dos cuentas
Cada cuenta debe tener un magic number unico.
Si dos EAs tienen el mismo magic number en la
misma plataforma MT5 pueden interferir entre si.

---

## PROCESO DE PASO AL VERIFICATION (Fase 2)

Cuando se alcanza el objetivo del Challenge (+10%):

1. FTMO notificara por email
2. NO cerrar el EA — dejar que cierre
   todas las posiciones abiertas
3. Verificar que todas las posiciones estan cerradas
4. Esperar la activacion de la cuenta Verification
5. Conectar con las mismas credenciales o nuevas
   segun indique FTMO
6. Activar el EA con los mismos parametros
7. Objetivo Verification: +5%

---

## PROCESO SI FALLA EL CHALLENGE

Si se viola algun limite y el challenge falla:

1. Documentar en Obsidian que salio mal
2. Analizar el trade o periodo que causo el fallo
3. Determinar si fue:
   - Error del EA: revisar y corregir
   - Condicion de mercado extrema: aceptable
   - Error de configuracion: corregir antes de repetir
4. Decidir si repetir el mismo challenge o
   volver al pipeline para mejorar la estrategia
5. Si fue error del EA → corregir antes de repetir
6. Si fue condicion extrema → puede repetir
   con el mismo EA

---

## CHECKLIST COMPLETO PRE-CHALLENGE

[ ] Estrategia aprobada con todos los informes
[ ] EA exportado y compilado sin errores
[ ] Backtest MT5 consistente con SQ
[ ] Forward test en demo completado
[ ] Challenge comprado y credenciales recibidas
[ ] MT5 conectado al servidor de la prop firm
[ ] Simbolo correcto verificado en MT5
[ ] EA configurado con parametros correctos
[ ] AutoTrading activado
[ ] performance-monitor activado
[ ] Obsidian preparado para registro diario
[ ] Decision humana final: SI — empezar challenge