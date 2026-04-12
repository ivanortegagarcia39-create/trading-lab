# Skill: Verificacion de Comisiones Multi-Activo

## Proposito
Protocolo obligatorio para verificar las comisiones
exactas de cualquier activo ANTES de lanzar el
Builder libre. Comisiones incorrectas invalidan
todos los resultados — fue el error del Build 4.
Este protocolo se ejecuta automaticamente por
el data-manager y el sq-specialist.

---

## POR QUE ES CRITICO

Build 4: 6 candidatas con PF 1.53-1.70.
Resultado real con comisiones: TODAS descartadas.
Semanas de trabajo perdidas por no verificar
comisiones antes de lanzar.

Con el Builder libre de 48 horas el coste de
un error de comisiones es aun mayor — 48 horas
de computo generando candidatas que no valen nada.

---

## CUANDO VERIFICAR COMISIONES

SIEMPRE antes de lanzar un build para:
1. Un activo que nunca se ha usado antes
2. Un activo que no se ha usado en mas de 30 dias
3. Cuando se cambia de prop firm objetivo
4. Cuando el propfirm-analyst detecta cambios
   en las condiciones de una prop firm

---

## PROCESO DE VERIFICACION

### Paso 1: Identificar la prop firm objetivo
El propfirm-analyst ya ha recomendado una prop firm
para este activo. Verificar cual es.

### Paso 2: Buscar las comisiones oficiales
Ir a la web oficial de la prop firm y buscar:

FTMO:
- Pagina de especificaciones de instrumentos
- Buscar el activo exacto (ej: EURUSD, XAUUSD)
- Anotar: spread tipico, comision por lote, swap

E8 Funding:
- Pagina de condiciones de trading
- Buscar el activo exacto
- Anotar: spread, comision, swap

TFT:
- Pagina de instrumentos
- Buscar el activo exacto
- Anotar: spread, comision, swap

Apex / MFF / TopStep:
- Solo futuros CME — margenes diferentes
- Buscar especificaciones del contrato
- Anotar: comision por contrato, tick value

### Paso 3: Calcular los 3 valores para SQ

Para cada activo necesitamos 3 valores exactos:

1. SPREAD (Desviacion en SQ)
   = spread tipico de la prop firm en pips
   NOTA: verificar que el pip size de SQ
   coincide con el de la prop firm.
   Si no coincide → ajustar el valor.

2. COMISION
   = comision por lote completo (round turn) en USD
   La mayoria de prop firms: 7 USD por lote Forex
   Algunos activos pueden ser diferentes.

3. SLIPPAGE (Deslizamiento en SQ)
   = estimacion del deslizamiento real
   Forex majors: 0.5 pips
   Forex crosses: 0.8 pips
   Metales: 1-2 pips
   Indices: 1-2 puntos
   Cripto: variable — usar 2-5 pips

### Paso 4: Verificar pip size en SQ
CRITICO para metales e indices.

Abrir SQ → Gestor de datos → seleccionar simbolo
→ verificar pip size.

Ejemplo XAU/USD:
- Spread real FTMO: ~30 USD por lote
- Si pip size en SQ = 0.01 → introducir 30 pips
- Si pip size en SQ = 0.1 → introducir 3 pips
- Si pip size en SQ = 1.0 → introducir 0.3 pips

ERROR COMUN: introducir el spread en pips sin
verificar el pip size de SQ. Un factor de 10x
de error hace que todas las estrategias sean
irreales.

### Paso 5: Documentar y confirmar

Crear archivo de verificacion:
strategyquant\databanks\comisiones-[activo]-[fecha].md

Formato:
Activo: [simbolo]
Prop firm: [nombre]
Fecha verificacion: [fecha]
Fuente: [URL de la pagina oficial]

VALORES VERIFICADOS:
- Spread real prop firm: [valor] [unidad]
- Pip size en SQ: [valor]
- Spread a introducir en SQ: [valor] pips
- Comision por lote: [valor] USD
- Slippage estimado: [valor] pips

VERIFICACION CRUZADA:
- Spread en SQ genera coste similar al real: SI/NO
- Pip size SQ coincide con prop firm: SI/NO

RESULTADO:
[ ] COMISIONES VERIFICADAS — listo para build
[ ] ERROR DETECTADO — corregir antes de lanzar

Verificado por: data-manager + sq-specialist
Intervencion humana: NO

---

## COMISIONES VERIFICADAS ACTUALMENTE

### EUR/USD — FTMO (VERIFICADO)
- Spread: 0.5 pips
- Comision: 7 USD por lote
- Slippage: 0.5 pips
- Pip size SQ: 0.0001
- Estado: ACTIVO — listo para build

### XAU/USD — FTMO (VERIFICADO)
- Spread: 30 pips
- Comision: 7 USD por lote
- Slippage: 2 pips
- Pip size SQ: verificar antes de cada build
- Estado: ACTIVO — verificar pip size

### Resto de activos — PENDIENTE DE VERIFICACION
Los siguientes activos requieren verificacion
completa antes del primer build:

Forex Majors:
- GBP/USD: spread estimado ~0.8 pips — VERIFICAR
- USD/JPY: spread estimado ~0.5 pips — VERIFICAR
- USD/CHF: spread estimado ~0.8 pips — VERIFICAR
- AUD/USD: spread estimado ~0.6 pips — VERIFICAR
- NZD/USD: spread estimado ~1.0 pips — VERIFICAR
- USD/CAD: spread estimado ~0.8 pips — VERIFICAR

Forex Crosses:
- EUR/GBP: spread estimado ~0.8 pips — VERIFICAR
- EUR/JPY: spread estimado ~1.0 pips — VERIFICAR
- GBP/JPY: spread estimado ~1.5 pips — VERIFICAR
- EUR/AUD: spread estimado ~1.5 pips — VERIFICAR
- Resto: VERIFICAR antes de usar

Metales:
- XAG/USD: spread estimado ~3 pips — VERIFICAR
  CRITICO: verificar pip size en SQ

Indices:
- US30: spread estimado ~2.0 pts — VERIFICAR
  CRITICO: verificar pip size y tick value en SQ
- US500: spread estimado ~0.5 pts — VERIFICAR
- NAS100: spread estimado ~1.5 pts — VERIFICAR
- DE40: spread estimado ~1.5 pts — VERIFICAR
- UK100: spread estimado ~1.5 pts — VERIFICAR
- JP225: spread estimado ~10 pts — VERIFICAR

Cripto:
- BTC/USD: spread estimado ~20 USD — VERIFICAR
  CRITICO: spread muy alto y variable
- ETH/USD: spread estimado ~2 USD — VERIFICAR

NOTA: Todos los valores "estimados" son aproximados
y DEBEN verificarse en la web oficial de la prop firm
antes de lanzar cualquier build.

---

## ERRORES COMUNES DE COMISIONES

### Error 1: Pip size incorrecto
El error mas peligroso. Un factor de 10x en el
spread hace que SQ genere estrategias que ganan
en backtest pero pierden en real.
Solucion: SIEMPRE verificar pip size en SQ
antes de introducir el spread.

### Error 2: Comisiones diferentes Builder vs Retester
Si el Builder usa spread 0.5 y el Retester usa
spread 0.8 los resultados no son comparables.
Solucion: copiar EXACTAMENTE las comisiones
del Builder al Retester.

### Error 3: No incluir slippage
Muchos ignoran el slippage pero en operativa real
existe. No incluirlo hace los resultados optimistas.
Solucion: SIEMPRE incluir slippage estimado.

### Error 4: Usar spreads de cuenta demo
Los spreads de la cuenta demo pueden ser diferentes
a los de la cuenta del challenge.
Solucion: usar spreads de las especificaciones
oficiales de la prop firm, no de la demo.

### Error 5: No actualizar comisiones
Las prop firms cambian spreads y comisiones.
Verificar cada 30 dias minimo.
Solucion: el propfirm-analyst monitorea cambios.

---

## INTEGRACION CON EL PIPELINE

El data-manager y el sq-specialist verifican
comisiones automaticamente como parte del
checklist pre-build (skill-precbuild-checklist.md).

Si las comisiones no estan verificadas para
el activo seleccionado → NO lanzar el build.

Flujo:
1. market-selector elige activo por scoring
2. data-manager verifica datos disponibles
3. sq-specialist verifica comisiones con esta skill
4. Si comisiones verificadas → configurar Builder
5. Si comisiones NO verificadas → verificar primero
6. Solo lanzar con comisiones CONFIRMADAS

---

## REGLA FUNDAMENTAL

48 horas de build con comisiones incorrectas
= 48 horas perdidas completamente.
Verificar comisiones tarda 15 minutos.
No hay excusa para no hacerlo.
Los numeros del backtest solo valen si las
comisiones son reales.