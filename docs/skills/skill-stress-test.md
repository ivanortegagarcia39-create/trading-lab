# Skill: Stress Test Historico

## Proposito

Verificar que la estrategia sobrevive los peores momentos
del mercado de los ultimos 20 anos. Una estrategia que
sobrevive estos 5 periodos tiene robustez de nivel institucional.

El WFO valida la robustez temporal en condiciones normales.
El stress test valida la supervivencia en condiciones extremas.
Son complementarios — no se sustituyen entre si.

---

## LOS 5 PERIODOS CRITICOS

### Periodo 1 — Crisis financiera global 2008
Fechas: 2008-09-01 a 2008-10-31
Caracteristicas: volatilidad extrema, iliquidez repentina,
  correlaciones que convergen a 1 entre todos los activos.
  Lehman Brothers (15 sep 2008) fue el evento detonante.
DD esperado en estrategias normales: 20-40%.
Activos mas afectados: todos los Forex majors, indices.
XAU/USD: inicialmente bajo con el mercado, luego se recupero.

### Periodo 2 — Flash crash CHF 2015
Fechas: 2015-01-13 a 2015-02-28
Caracteristicas: el SNB elimino el peg EUR/CHF el 15 enero 2015.
  EUR/CHF cayo 2.000 pips en minutos. Muchos brokers quebraron.
Activos afectados principalmente: EUR/CHF, GBP/CHF, USD/CHF.
Para XAUUSD y Forex majors no-CHF: impacto moderado.
Usar este periodo para verificar resistencia a flash crashes.

### Periodo 3 — COVID crash 2020
Fechas: 2020-02-15 a 2020-04-15
Caracteristicas: crash rapido en todos los activos de riesgo,
  luego recuperacion igualmente rapida.
  XAU/USD bajo inicialmente con el mercado (necesidad de liquidez),
  luego subio fuertemente como refugio.
Indices: -35% en 5 semanas, luego recuperacion en V.
Este periodo es el mas reciente y el mas relevante para
estrategias con datos desde 2020.

### Periodo 4 — Inflacion y subida de tipos 2022
Fechas: 2022-01-01 a 2022-06-30
Caracteristicas: tendencia bajista sostenida en indices
  y Forex (USD se fortalecion fuertemente).
  No fue un crash puntual — fue deterioro gradual de 6 meses.
XAU/USD: volatil pero sin crash extremo.
EUR/USD: tendencia bajista sostenida de 1.15 a 0.96.
Este periodo es el mas relevante para estrategias de tendencia.

### Periodo 5 — Crisis bancaria SVB 2023
Fechas: 2023-03-01 a 2023-03-31
Caracteristicas: colapso de Silicon Valley Bank (10 mar 2023),
  contagio a Credit Suisse, Signature Bank.
  Duracion corta pero intensa — volatilidad extrema en 2 semanas.
XAU/USD subio fuertemente (refugio).
USD/JPY bajo por fly-to-safety.
USD/CHF bajo (CHF como refugio alternativo).

---

## CRITERIO DE APROBACION

DD < 8% en cada periodo individual.

Si cualquier periodo supera 8% de DD:
  → DESCARTE AUTOMATICO del stress test.
  → La estrategia no avanza al portfolio.
  → Razon: si no sobrevivio el pasado no sobrevivira
    el futuro cuando ocurra un evento similar.

El 8% es mas estricto que el 10% del limite FTMO.
El margen de 2% cubre el slippage adicional en eventos extremos
donde la ejecucion real es peor que el backtest.

---

## COMO EJECUTAR EN SQ

Para cada uno de los 5 periodos:

```
1. Abrir SQ con la estrategia aprobada en WFO
2. Ir a Retester (no al Builder)
3. Cambiar fecha IS a: [fecha_inicio_periodo] a [fecha_fin_periodo]
4. Ejecutar Retester con los mismos parametros del EA
5. Registrar el DD maximo del periodo
6. Repetir para los 5 periodos
```

Documentar en el informe de exportacion:

| Periodo | Fechas | DD maximo | Estado |
|---------|--------|-----------|--------|
| Crisis 2008 | 2008-09-01 / 2008-10-31 | [X]% | PASA/FALLA |
| CHF 2015 | 2015-01-13 / 2015-02-28 | [X]% | PASA/FALLA |
| COVID 2020 | 2020-02-15 / 2020-04-15 | [X]% | PASA/FALLA |
| Inflacion 2022 | 2022-01-01 / 2022-06-30 | [X]% | PASA/FALLA |
| SVB 2023 | 2023-03-01 / 2023-03-31 | [X]% | PASA/FALLA |

Si todos los periodos muestran DD < 8%: STRESS TEST APROBADO.

---

## INTEGRACION EN EL PIPELINE

El stress test se ejecuta despues del WFO y antes del portfolio.
Es un filtro adicional — no reemplaza al WFO.

```
Builder libre → EvalGate → Retester → WFO → STRESS TEST → Portfolio → Export
```

El export-specialist verifica que el informe de exportacion
incluye la tabla de stress test con los 5 periodos.
Sin la tabla → el EA no esta listo para challenge.

Si la estrategia no tiene datos suficientes para algun periodo:
  Ejemplo: estrategia desarrollada con datos desde 2010
  no tiene datos para la Crisis 2008.
  En ese caso: marcar ese periodo como N/A y documentar.
  El criterio se aplica solo a los periodos con datos disponibles.

---

## RELACION CON EL GT-SCORE

El stress test no forma parte directa del calculo del GT-Score.
Es un filtro binario: APROBADO o DESCARTADO.
Una estrategia puede tener GT-Score = 80 y fallar el stress test.
En ese caso: DESCARTE. El GT-Score no compensa el fallo del stress.

---

## LO QUE ESTA SKILL NUNCA HACE

NUNCA acepta un DD > 8% en ningun periodo critico.
NUNCA omite el stress test antes del challenge real.
NUNCA reemplaza el WFO con el stress test — son complementarios.
NUNCA usa el GT-Score para compensar un fallo del stress test.
NUNCA marca N/A un periodo si hay datos disponibles.
