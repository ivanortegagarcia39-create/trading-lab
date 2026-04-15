# Skill: Priorizacion de Computo y Builds

## Proposito
Define como priorizar que activos se procesan
primero y cuantos ciclos dedicar a cada uno.
Con 30+ activos y builds de 24-48h por activo,
un ciclo completo sin priorizacion tardaria meses.
La priorizacion es numerica y automatica.
No se elige un activo porque "parece prometedor".

---

## Sistema de scoring de prioridad

Cada activo recibe un score de prioridad (0-100)
calculado antes de cada ciclo de builds.
El activo con mayor score se procesa primero.

### Componentes del score

#### Factor 1 — Historial de aprobacion (0-40 pts)
Basado en ciclos anteriores del mismo activo.

Sin historial previo: 20 pts (neutro)
Tasa de aprobacion IS->Portfolio > 10%: 40 pts
Tasa de aprobacion IS->Portfolio 5-10%: 30 pts
Tasa de aprobacion IS->Portfolio 1-5%: 15 pts
Tasa de aprobacion IS->Portfolio 0%
  con 2+ ciclos: 5 pts
Activo pausado por 2 challenges fallidos: 0 pts

#### Factor 2 — Necesidad del portfolio (0-30 pts)
Basado en gaps del portfolio actual.

Portfolio vacio (0 estrategias): 30 pts
Activo no representado en portfolio: 25 pts
Activo con 1 estrategia en portfolio: 10 pts
Activo con 2 estrategias en portfolio: 0 pts
  (maximo 2 por activo segun regla de portfolio)

#### Factor 3 — Calidad de datos historicos (0-20 pts)
Basado en disponibilidad y calidad de datos H1.

10+ años de datos limpios verificados: 20 pts
7-10 años de datos: 15 pts
5-7 años de datos: 10 pts
3-5 años de datos: 5 pts
Menos de 3 años: 0 pts (no usar)

#### Factor 4 — Diversificacion de estilo (0-10 pts)
Basado en estilos ya presentes en el portfolio.

El activo tiene perfil de volatilidad distinto
a todos los activos ya en portfolio: 10 pts
Perfil similar a 1 activo en portfolio: 5 pts
Perfil similar a 2+ activos en portfolio: 0 pts

---

## Calculo del score — ejemplo

Activo: EURUSD
Factor 1: tasa aprobacion 8% en ciclo anterior = 30 pts
Factor 2: ya tiene 1 estrategia en portfolio = 10 pts
Factor 3: 12 años de datos limpios = 20 pts
Factor 4: perfil similar a GBPUSD en portfolio = 5 pts
Score total: 65/100

Activo: XAUUSD
Factor 1: sin historial previo = 20 pts
Factor 2: no representado en portfolio = 25 pts
Factor 3: 8 años de datos = 15 pts
Factor 4: perfil distinto a todos = 10 pts
Score total: 70/100

Decision automatica: XAUUSD se procesa primero.

---

## Reglas de ciclos por activo

### Ciclos maximos consecutivos por activo
Un mismo activo no puede recibir mas de
2 ciclos de build consecutivos sin rotar
a otro activo.
Razon: evitar sobre-representacion y
detectar activos improductivos antes.

### Rotacion obligatoria
Despues de 2 ciclos consecutivos en un activo:
rotar al siguiente por score aunque el activo
anterior tenga score mas alto.
El activo anterior puede volver despues de
que otros 2 activos hayan tenido su ciclo.

### Activos en pausa
Activos pausados por 2 challenges fallidos
consecutivos: excluir del scoring durante
4 ciclos completos.
Despues de 4 ciclos: reincorporar con
Factor 1 = 5 pts hasta nuevo historial.

---

## Lista de activos disponibles por categoria

### Forex Majors (prioridad base alta)
EURUSD, GBPUSD, USDJPY, USDCHF,
AUDUSD, USDCAD, NZDUSD

### Forex Crosses (prioridad base media)
EURGBP, EURJPY, GBPJPY, AUDJPY,
EURCHF, GBPCHF, CADJPY

### Metales (prioridad base alta — diversificacion)
XAUUSD, XAGUSD

### Indices US (prioridad base media)
US30, US500, US100

### Indices EU/JP (prioridad base baja — datos limitados)
GER40, UK100, JPN225

### Crypto (prioridad base baja — volatilidad extrema)
BTCUSD, ETHUSD

---

## Planificacion de ciclos

Antes de cada nuevo ciclo el orchestrator:

Paso 1 — Recalcular scores de todos los activos
Usar formula de 4 factores con datos actualizados.

Paso 2 — Aplicar reglas de rotacion
Excluir activos en pausa.
Verificar limite de 2 ciclos consecutivos.

Paso 3 — Generar cola de prioridad
Ordenar activos por score descendente.
Documentar en: results\build-queue.md

Paso 4 — Estimar tiempo total
Numero de activos en cola x duracion media de build.
Si el tiempo estimado supera 2 semanas:
limitar la cola a los 5 activos de mayor score.

Formato de build-queue.md:
========================================
COLA DE BUILDS — [fecha]
========================================
Posicion | Activo | Score | Razon principal
1        | [sim]  | [N]   | [factor dominante]
2        | [sim]  | [N]   | [factor dominante]
...
Activos en pausa: [lista]
Ciclos consecutivos actuales: [activo] x[N]
Tiempo estimado cola completa: [dias]
========================================

---

## Lo que esta skill NUNCA hace

NUNCA elige un activo porque "el mercado
esta interesante ahora mismo".
NUNCA salta la cola de prioridad por
intuicion o noticias del mercado.
NUNCA dedica ciclos ilimitados al mismo activo.
NUNCA ignora un activo con score alto
por preferencia personal.

El score decide el orden. Sin excepciones.