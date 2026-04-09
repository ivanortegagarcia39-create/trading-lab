# Skill: Correlacion de Portfolio

## Proposito
Guia para el correlation-analyst y el orchestrator.
Define como verificar que las estrategias aprobadas
no estan correlacionadas entre si antes de añadir
una nueva al portfolio.
Dos estrategias correlacionadas duplican el riesgo
sin diversificar el portfolio.

---

## POR QUE ES CRITICO VERIFICAR CORRELACIONES

Si tienes dos estrategias que:
- Operan el mismo activo
- En la misma direccion (ambas long o ambas short)
- Con logica similar (ambas trend following)

Cuando el mercado va en contra de ambas al mismo
tiempo el DD se duplica.
Con dos estrategias correlacionadas puedes violar
el limite de DD de la prop firm aunque cada
estrategia individualmente este dentro del limite.

Ejemplo critico:
Estrategia A: max DD 5% en backtest
Estrategia B: max DD 5% en backtest
Si estan correlacionadas al 80%:
DD combinado real puede ser hasta 9% → viola limite FTMO

---

## TIPOS DE CORRELACION

### Correlacion positiva alta (> 0.7)
Las dos estrategias ganan y pierden al mismo tiempo.
PELIGROSO — no añadir al portfolio.

### Correlacion positiva moderada (0.3 a 0.7)
Las estrategias tienen cierta dependencia.
ACEPTABLE con precaucion — reducir tamaño de posicion.

### Correlacion baja (-0.3 a 0.3)
Las estrategias son independientes.
IDEAL — maxima diversificacion del portfolio.

### Correlacion negativa (-0.7 a -0.3)
Las estrategias tienden a compensarse mutuamente.
MUY BUENO — reduce el DD del portfolio.

### Correlacion negativa alta (< -0.7)
Cuando una gana la otra pierde consistentemente.
BUENO para reducir DD pero limita el beneficio total.

---

## COMO CALCULAR CORRELACION EN SQ

### Metodo 1 — Comparar curvas de equity
1. Exportar los resultados de ambas estrategias
   del Retester (periodo OOS 2021-2026)
2. En SQ → Portfolio Master → añadir ambas
3. Ver la curva de equity combinada
4. Si la curva combinada es mas suave que cada
   una por separado → baja correlacion (bueno)
5. Si la curva combinada tiene los mismos valles
   que cada una → alta correlacion (malo)

### Metodo 2 — Analisis visual de drawdowns
Comparar los periodos de drawdown de cada estrategia:
- Si los drawdowns ocurren en los mismos meses
  → correlacion alta → NO añadir al portfolio
- Si los drawdowns ocurren en meses diferentes
  → correlacion baja → SI añadir al portfolio

### Metodo 3 — Correlacion por activo y estilo
Regla rapida para estimar correlacion sin calculos:

| Caso                              | Correlacion estimada |
|-----------------------------------|----------------------|
| Mismo activo, mismo estilo        | MUY ALTA (0.8+)      |
| Mismo activo, estilos opuestos    | BAJA (0.1-0.3)       |
| Activos correlacionados (EUR/USD  |                      |
| y GBP/USD), mismo estilo          | ALTA (0.6-0.8)       |
| Activos no correlacionados        |                      |
| (EUR/USD y XAU/USD), mismo estilo | MODERADA (0.3-0.5)   |
| Activos no correlacionados,       |                      |
| estilos opuestos                  | BAJA O NEGATIVA      |

---

## CORRELACIONES CONOCIDAS ENTRE ACTIVOS

### Alta correlacion (evitar mismo estilo)
- EUR/USD y GBP/USD: correlacion ~0.85
- EUR/USD y EUR/JPY: correlacion ~0.75
- XAU/USD y XAG/USD: correlacion ~0.80
- NQ y ES (SP500): correlacion ~0.85

### Correlacion moderada (precaucion)
- EUR/USD y USD/JPY: correlacion ~0.50 inversa
- EUR/USD y XAU/USD: correlacion ~0.40

### Baja correlacion (ideal para diversificar)
- EUR/USD y NQ: correlacion ~0.20
- XAU/USD y NQ: correlacion ~0.15
- Forex y Futuros CME en general: baja correlacion

---

## REGLAS DE CONSTRUCCION DEL PORTFOLIO

### Regla 1 — Maximo 2 estrategias por activo
No tener mas de 2 estrategias operando el mismo
activo simultaneamente.
Si hay 2 en EUR/USD → deben tener estilos opuestos
(una trend following, otra mean reversion).

### Regla 2 — Maximo 60% del riesgo en Forex
Si el portfolio tiene 5 estrategias:
- Maximo 3 en Forex (EUR/USD, GBP/USD)
- Minimo 2 en otros activos (XAU/USD, NQ, GC)

### Regla 3 — Verificar DD combinado
Antes de añadir una nueva estrategia calcular:
DD combinado estimado = DD1 + DD2 x correlacion
Si DD combinado > 7% → no añadir hasta revisar

### Regla 4 — Priorizar baja correlacion
Al elegir entre dos estrategias aprobadas
para el portfolio, elegir siempre la que tenga
menor correlacion con las estrategias existentes.

---

## CHECKLIST PRE-ADICION AL PORTFOLIO

Antes de añadir una nueva estrategia aprobada
al portfolio activo verificar:

[ ] Correlacion con estrategias existentes < 0.6
[ ] DD combinado estimado < 7%
[ ] No mas de 2 estrategias en el mismo activo
[ ] Estilos complementarios si mismo activo
[ ] Activos diversificados en el portfolio
[ ] Informe de correlation-analyst completado
[ ] Decision humana final: SI

---

## FORMATO DE INFORME DE CORRELACION

Fecha: [fecha]
Nueva estrategia: [nombre]
Generado por: correlation-analyst

PORTFOLIO ACTUAL:
| Estrategia | Activo  | Estilo          | DD max |
|------------|---------|-----------------|--------|
| [nombre1]  | EUR/USD | Trend Following | 5.2%   |
| [nombre2]  | XAU/USD | Mean Reversion  | 4.8%   |

ANALISIS DE CORRELACION:
| Par de estrategias    | Correlacion estimada | Riesgo |
|-----------------------|----------------------|--------|
| Nueva vs Estrategia1  | [valor]              | [bajo/medio/alto] |
| Nueva vs Estrategia2  | [valor]              | [bajo/medio/alto] |

DD COMBINADO ESTIMADO:
Portfolio actual max DD: [valor]
Con nueva estrategia: [valor]
Dentro del limite 7%: SI/NO

DECISION:
[ ] AÑADIR AL PORTFOLIO — correlacion aceptable
[ ] AÑADIR CON PRECAUCION — reducir tamaño posicion
[ ] NO AÑADIR — correlacion demasiado alta

Informe guardado en:
results\approved\[nombre]-correlation-report.md