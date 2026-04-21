# Skill: Seleccion y Gestion de Portfolio Automatico

## Proposito
Define como el correlation-analyst y el orchestrator
seleccionan automaticamente combinaciones de estrategias
para formar un portfolio diversificado que maximice
la probabilidad de superar challenges de prop firms.
El objetivo NO es encontrar la mejor estrategia individual
sino el mejor CONJUNTO de estrategias complementarias.

---

## POR QUE PORTFOLIO Y NO ESTRATEGIA INDIVIDUAL

Una sola estrategia con PF 1.5 y DD 5% puede tener
rachas perdedoras de 2-3 meses. En ese periodo
el challenge de la prop firm se pierde.

Un portfolio de 4 estrategias no correlacionadas
con PF promedio 1.4 y DD individual 5% tiene un
DD combinado mucho menor porque cuando una pierde
las otras compensan. La curva de equity es mas
suave y la probabilidad de superar el challenge
aumenta drasticamente.

Ejemplo numerico:
Estrategia A sola: probabilidad de pasar challenge 55%
Estrategia B sola: probabilidad de pasar challenge 50%
Portfolio A+B (correlacion 0.2): probabilidad 75%
Portfolio A+B+C+D (correlacion < 0.3): probabilidad 85%+

---

## ESTRUCTURA DEL PORTFOLIO OBJETIVO

### Portfolio minimo viable
- 3 estrategias no correlacionadas
- Al menos 2 estilos diferentes
  (trend-following + mean-reversion)
- Al menos 2 activos diferentes si hay datos
- DD combinado estimado < 10%

### Portfolio optimo
- 5 estrategias no correlacionadas
- 3 estilos diferentes
- 2-3 activos diferentes
- DD combinado estimado < 8%
- Correlacion maxima entre cualquier par: 0.4

### Portfolio maximo
- 8 estrategias activas simultaneamente
- Mas de 8 es contraproducente: el riesgo
  por estrategia individual se reduce tanto
  que el rendimiento total es insuficiente
  para superar el challenge en tiempo razonable

---

## CRITERIOS DE SELECCION AUTOMATICA

### Paso 1: Pool de candidatas aprobadas
Todas las estrategias que pasaron el WFO con
dictamen ROBUSTA o ACEPTABLE forman el pool.
El pool se mantiene actualizado automaticamente.

### Paso 2: Scoring individual
Cada candidata recibe una puntuacion automatica:

Componentes del score (total sobre 100):
- PF OOS promedio WFO: peso 25%
  Score = (PF OOS - 1.0) x 50 (max 25 puntos)
- WFE: peso 20%
  Score = WFE x 0.20 (max 20 puntos)
- DD OOS maximo: peso 20%
  Score = (10 - DD OOS%) x 2 (max 20 puntos)
- Estabilidad parametros WFO: peso 15%
  Score = (1 - desviacion%) x 15 (max 15 puntos)
- Trades por mes: peso 10%
  Score = min(trades_mes / 3, 10) (max 10 puntos)
- Ultima ventana WFO: peso 10%
  Score = (PF ultima / PF promedio) x 10 (max 10 puntos)

Score minimo para entrar en el portfolio: 55/100

### Paso 3: Matriz de correlacion
Para cada par de candidatas calcular correlacion.

Metodos de calculo (en orden de preferencia):
1. Portfolio Master de SQ — curvas de equity
2. Comparacion visual de periodos de drawdown
3. Estimacion por activo y estilo (tabla rapida)

Tabla rapida de correlacion estimada:
| Caso | Correlacion |
|------|-------------|
| Mismo activo, mismo estilo | 0.7-0.9 |
| Mismo activo, estilos opuestos | 0.1-0.3 |
| Activos correlacionados (EUR/GBP), mismo estilo | 0.5-0.7 |
| Activos no correlacionados (EUR/XAU), mismo estilo | 0.2-0.4 |
| Activos no correlacionados, estilos opuestos | -0.1-0.2 |

### Paso 4: Seleccion greedy del portfolio
Algoritmo automatico de seleccion:

1. Ordenar candidatas por score de mayor a menor
2. La primera candidata entra automaticamente
3. Para cada siguiente candidata verificar:
   a. Correlacion con CADA estrategia ya incluida < 0.5
   b. DD combinado estimado con portfolio actual < 12%
   c. No viola reglas de diversificacion (max 2 por activo,
      max 2 por estilo)
4. Si cumple todo → incluir en portfolio
5. Si no cumple → mover a cola de espera
6. Repetir hasta llenar el portfolio o agotar candidatas

### Paso 5: Calculo de DD combinado
Formula simplificada:
DD_combinado = sqrt(sum(DD_i^2) + 2 x sum(corr_ij x DD_i x DD_j))

Donde:
- DD_i = drawdown maximo de la estrategia i
- corr_ij = correlacion entre estrategias i y j

Si el DD combinado supera el 12% no añadir mas
estrategias aunque haya candidatas disponibles.

---

## REGLAS DE DIVERSIFICACION

### Por activo
- Maximo 2 estrategias por activo
- Si hay 2 en EUR/USD deben tener estilos opuestos
- Priorizar diversificacion entre activos

### Por estilo
- Maximo 3 estrategias trend-following
- Maximo 3 estrategias mean-reversion
- Minimo 1 de cada estilo en el portfolio

### Por temporalidad
- Todas en H1 actualmente
- Cuando se expanda a otras temporalidades
  priorizar diversificacion temporal

### Por prop firm
- Cada estrategia puede asignarse a una prop firm
  diferente para maximizar diversificacion
- EUR/USD → FTMO o E8
- XAU/USD → FTMO
- Futuros (futuro) → Apex o MFF

---

## GESTION DINAMICA DEL PORTFOLIO

### Cuando reemplazar una estrategia
El performance-monitor detecta deterioro y el
correlation-analyst decide el reemplazo.

Criterios de reemplazo automatico:
- PF real de los ultimos 3 meses < 0.9
- DD real supera el 150% del DD del backtest
- Win rate real < 70% del win rate del backtest
- 3 meses consecutivos con PF < 1.0

Proceso de reemplazo:
1. Performance-monitor detecta deterioro
2. Orchestrator retira la estrategia de produccion
3. Correlation-analyst busca en el pool de espera
   la mejor candidata compatible con el portfolio
4. Si hay candidata → reemplazar automaticamente
5. Si no hay candidata → lanzar nuevo ciclo de Builder

### Cuando ampliar el portfolio
Si el portfolio tiene menos de 3 estrategias activas
el orchestrator lanza un nuevo ciclo de Builder
automaticamente para generar mas candidatas.

### Rebalanceo mensual
Cada primer lunes de mes el correlation-analyst
recalcula la correlacion real del portfolio
con datos de operacion real y verifica que
las correlaciones no han cambiado significativamente.

Si alguna correlacion real supera 0.6 →
reconsiderar la combinacion.

---

## ASIGNACION DE RIESGO POR ESTRATEGIA

### Portfolio de 3 estrategias
Riesgo por estrategia: 1% por trade (sin cambio)
Riesgo total maximo del portfolio: 3% por dia
(si las 3 operan simultaneamente con 1 trade cada una)

### Portfolio de 5 estrategias
Riesgo por estrategia: 0.8% por trade
Riesgo total maximo: 4% por dia
Ajustar en las propiedades del EA antes de produccion

### Portfolio de 8 estrategias
Riesgo por estrategia: 0.5% por trade
Riesgo total maximo: 4% por dia

REGLA: El riesgo total del portfolio por dia
nunca debe superar el 4% para mantener margen
con el Daily Loss Limit de FTMO (5% dinamico).

---

## FORMATO DE INFORME DE PORTFOLIO

Fecha: [fecha]
Generado por: correlation-analyst

PORTFOLIO ACTUAL:
| # | Estrategia | Activo | Estilo | Score | DD max | Estado |
|---|------------|--------|--------|-------|--------|--------|
| 1 | [nombre]   | EUR/USD | TF    | 72    | 4.8%   | Activa |
| 2 | [nombre]   | XAU/USD | MR    | 68    | 5.1%   | Activa |
| 3 | [nombre]   | EUR/USD | MR    | 65    | 4.5%   | Activa |

MATRIZ DE CORRELACION:
|   | E1  | E2   | E3  |
|---|-----|------|-----|
| E1| 1.0 | 0.22 | 0.18|
| E2| 0.22| 1.0  | 0.31|
| E3| 0.18| 0.31 | 1.0 |

DD COMBINADO ESTIMADO: [valor]%
RIESGO POR ESTRATEGIA: [valor]% por trade
RIESGO TOTAL MAXIMO DIA: [valor]%

COLA DE ESPERA:
| Estrategia | Score | Razon espera |
|------------|-------|--------------|
| [nombre]   | 61    | Corr > 0.5 con E1 |

SIGUIENTE ACCION:
[ ] Portfolio completo — monitoreo continuo
[ ] Portfolio incompleto — lanzar nuevo ciclo Builder
[ ] Reemplazo necesario — candidata [nombre] disponible

---

## MARKOWITZ vs HRP — CUANDO USAR CADA UNO

El correlation-analyst elige el metodo de optimizacion
segun el estado del portfolio. El humano no elige el metodo.

### HRP (Hierarchical Risk Parity) — DEFAULT

Usar HRP cuando:
- Hay < 5 estrategias en el portfolio
- Las correlaciones son inestables (diferencia > 15%
  entre los dos semestres del historico — ver hrp-portfolio.py)
- El historial en produccion real es < 12 meses
- Acaba de añadirse una estrategia nueva al portfolio

Razon: HRP no requiere estimacion de retornos esperados
(que es inestable con pocas estrategias) y es mas robusto
cuando las correlaciones cambian. No sufre del problema
de "error amplification" de Markowitz con matrices de
covarianza mal condicionadas.

### MVO Markowitz (Maximo Sharpe) — PARA PORTFOLIO MADURO

Usar MVO cuando:
- Hay >= 5 estrategias en el portfolio
- Todas tienen al menos 12 meses de historia en produccion real
- Las correlaciones han sido estables los ultimos 6 meses

Razon: con 5+ estrategias y historia suficiente la
estimacion de la matriz de covarianza es fiable y
Markowitz puede encontrar la frontera eficiente real.

### Implementacion
script: scripts/hrp-portfolio.py
  Seleccion automatica del metodo segun los criterios
  Restriccion: ninguna estrategia > 40% del portfolio
  Output: results/portfolio-weights.json

**DEFAULT ACTUAL: HRP**
El portfolio sigue en fase inicial. HRP es el metodo
hasta que se cumplan las condiciones de MVO.

---

## RESTRICCION ANTI-MONOCULTIVO USD

### Definicion del Factor Dolar
Los siguientes activos comparten el Factor Dolar como
fuente de riesgo principal:
  EURUSD, GBPUSD, AUDUSD, NZDUSD, USDCAD (inverso),
  USDJPY (inverso), USDCHF (inverso), XAUUSD

Cuando el USD se fortalece, todos estos activos se mueven
en la misma direccion. Estrategias sobre activos diferentes
pero correlacionados con el USD tienen drawdowns simultaneos.

### Regla de bloqueo automatico
Maximo 2 estrategias simultáneas cuyo activo pertenezca
al Factor Dolar.

Si se intenta añadir una tercera estrategia USD-correlacionada:
  → correlation-analyst bloquea la inclusion automaticamente
  → Decision: ESPERA hasta que una de las 2 activas se retire
  → Mensaje: "Restriccion Anti-Monocultivo USD.
    Ya hay 2 estrategias en el Factor Dolar.
    [lista de las 2 activas].
    Esta estrategia pasa a cola de espera."

### Excepcion de estilos opuestos
Si las 2 estrategias USD-correlacionadas ya activas tienen
estilos completamente opuestos (una trend-following, una mean-reversion)
Y su correlacion real medida es < 0.3:
  → Permitir la tercera con penalizacion de -5 pts en el score
  → Registrar la excepcion en el informe de portfolio
  → Aumentar frecuencia de calculo de correlacion a semanal

---

## PROCESO DE SELECCION AUTOMATICO COMPLETO

Flujo completo que ejecuta el correlation-analyst:

```
Pool de candidatas WFO aprobadas
        ↓
Paso 1: Scoring individual (formula existente)
  Descartar si score < 55/100
        ↓
Paso 2: Ordenar por score descendente
        ↓
Paso 3: Para cada candidata (greedy):
  a. Verificar correlacion < 0.5 con CADA activa
  b. Verificar DD combinado < 12% si se incluye
  c. Verificar max 2 por activo
  d. Verificar max 3 por estilo (TF/MR)
  e. VERIFICAR ANTI-MONOCULTIVO USD (max 2 Factor Dolar)
        ↓
Paso 4: Si cumple TODOS → INCLUIR
        Si falla correlacion 0.5-0.7 → ESPERA
        Si falla correlacion > 0.7 con 2+ → DESCARTAR
        Si falla anti-monocultivo → ESPERA
        ↓
Paso 5: Recalcular pesos con HRP (o MVO si aplica)
        via scripts/hrp-portfolio.py
        ↓
Paso 6: Verificar que ningun activo supera 40% del peso
        ↓
Output: portfolio actualizado en results/portfolio-weights.json
```

El humano no interviene en ningun paso.
Todo es automatico y determinista segun los criterios.

---

## REGLA FUNDAMENTAL

El portfolio se construye automaticamente
basandose en numeros y correlaciones.
No se incluye una estrategia porque "parece buena".
No se excluye una estrategia por intuicion.
El score, la correlacion, y los pesos HRP deciden.