# Skill: Timeframe Selector — Priorizacion de Temporalidades

## Proposito
Definir que temporalidades son viables para cada categoria
de uso (produccion, I+D, experimentacion) y como asignar
recursos de CPU al Builder segun la prioridad del timeframe.
Este selector elimina la subjetividad del humano en la
eleccion de temporalidades.

---

## LAS 3 CATEGORIAS DE TEMPORALIDAD

### Categoria 1: Produccion Core
Temporalidades: H1, H4
Funcion: portfolio principal de produccion
Caracteristicas:
  - Bajo mantenimiento — menos operaciones, menos supervision
  - Compatibles con reglas de prop firms (no se activan
    detecciones anti-scalping, cumplen minimum holding time)
  - Datos historicos M1 suficientes para reconstruir velas H1/H4
    con precision desde 2003 (Dukascopy)
  - Ratio señal/ruido alto — menos trades, mas calidad

Criterios minimos de aprobacion por TF:
  H1: Total Trades >= 120 en periodo IS (2003-2020)
      Trades/mes >= 8 en IS
  H4: Total Trades >= 50 en periodo IS
      Trades/mes >= 3 en IS
  Razon: H4 genera menos trades por definicion —
  umbral proporcional a la temporalidad

### Categoria 2: Incubadora Tactica
Temporalidades: M30, M15
Funcion: I+D rapida, deteccion de cambios de regimen,
  candidatas para portfolio cuando H1/H4 no generan suficientes
Caracteristicas:
  - Requieren criterios MAS estrictos que H1 para compensar
    el mayor ruido inherente a temporalidades cortas
  - Requieren Test de Estres de Velocidad antes de pasar al portfolio
  - Pueden llegar a produccion si pasan todos los filtros adicionales

Criterios minimos de aprobacion por TF:
  M30: Total Trades >= 180 en periodo IS
       Trades/mes >= 12
  M15: Total Trades >= 300 en periodo IS
       Trades/mes >= 20
  Razon: temporalidades cortas deben compensar con mayor
  numero de trades para tener significancia estadistica

Test de Estres de Velocidad (obligatorio para M30 y M15):
  Validar la estrategia en minimo 2 años completos
  aunque el build usara una ventana de solo 6 meses.
  Objetivo: verificar que el edge no es especifico de
  un regimen de 6 meses sino que persiste en el tiempo.
  Criterio: PF > 1.2 en cada uno de los 2 años de test.

### Categoria 3: I+D Pura
Temporalidades: M5, M1
Funcion: experimentacion, investigacion de mercados
  intradiarios, deteccion de micro-patrones
Restriccion: NUNCA van a produccion directa
Razon:
  - Incompatibles con reglas de prop firms:
    * Deteccion automatica de scalping (trades < 2 min)
    * Minimum holding time (FTMO requiere >= 2 minutos)
    * HFT detection en algunas prop firms
  - Coste de transaccion en M5/M1 consume el edge
    a comisiones FTMO reales de 7 USD/lote + spread
  - Requieren datos de tick de alta calidad que
    Dukascopy no garantiza en todos los activos

Uso legitimo de M5/M1:
  - Analisis de patrones intradiarios para informar
    la logica de indicadores en H1
  - Investigacion de comportamiento de spreads
  - Test de ideas antes de subirlas a H1

---

## SCORING DE PRIORIZACION DE CPU

El market-selector asigna recursos de CPU del Builder
segun la prioridad de la temporalidad y el estado del portfolio.

| Prioridad | TF | Condicion de activacion | CPU asignada |
|-----------|-----|------------------------|-------------|
| 1 | H1, H4 | Siempre — son el portfolio principal | Preferente |
| 2 | M30, M15 | Cuando H1/H4 tienen build activo en produccion | Secundaria |
| 3 | M5, M1 | Solo si hay recursos ociosos y no hay build H1/H4 pendiente | Minima |

Regla de asignacion:
  Si hay un build H1 en curso → toda la CPU disponible a H1
  Si H1 esta en retester/wfo → se puede lanzar M30 con 50% CPU
  Si H1/H4 tienen portfolio completo (3+ aprobadas) → M15 con 30% CPU
  M5/M1 nunca compiten con builds de produccion

---

## RESTRICCIONES OPERACIONALES POR TF

### H1 (produccion)
- Sesion: 08:00 a 20:00 CEST
- Max trades/dia: 2
- No operar viernes despues de las 17:00
- Salida fin de dia: ACTIVADO

### H4 (produccion)
- Sesion: sin restriccion horaria (velas de 4 horas)
- Max trades/dia: 1 (una vela H4 puede cubrir varios H1)
- No abrir posicion en la ultima barra antes del fin de semana

### M30, M15 (incubadora)
- Sesion: 09:00 a 17:00 (sesion europea activa)
- Max trades/dia: 4
- Test de Estres de Velocidad: OBLIGATORIO antes de produccion
- Slippage: +0.5 pips adicionales en comisiones respecto a H1
  para compensar ejecucion menos favorable en TF cortos

### M5, M1 (I+D)
- Sin restricciones en I+D — cualquier sesion para experimentos
- PROHIBIDO en builds de produccion
- PROHIBIDO en challenges reales

---

## DECISION DEL TIMEFRAME

El timeframe NO lo elige el humano.
El market-selector evalua los 5 criterios de scoring
de activo incluyendo el TF optimo para ese activo.

La logica de seleccion automatica:
1. El activo con mayor score recibe build H1 siempre
2. Si el activo tiene alta volatilidad intradiaria → valorar H4
3. Si el portfolio H1 ya tiene 5+ estrategias → valorar M30
4. M15 y M5/M1 solo si hay justificacion numerica

---

## LO QUE ESTE SELECTOR NUNCA HACE

NUNCA elige una temporalidad por preferencia o intuicion
NUNCA mezcla temporalidades dentro de la misma estrategia
NUNCA baja un TF a M5/M1 para aumentar el numero de trades
  si la estrategia no genera suficientes en H1
  (pocos trades en H1 significa estrategia de baja frecuencia,
  no un error que se corrige cambiando el TF)
NUNCA sube un TF a H4 para "suavizar" los resultados
  de una estrategia que falla en H1
NUNCA aprueba M5/M1 para produccion bajo ninguna circunstancia
