# Skill: PCA para Diversificacion Real del Portfolio

## Proposito

El PCA (Analisis de Componentes Principales) identifica
los factores de riesgo subyacentes que realmente mueven
el portfolio. Dos estrategias pueden parecer descorrelacionadas
por su PF pero responder al mismo factor macro subyacente.

El problema: la correlacion de Pearson entre estrategias
mide la similitud de sus retornos historicos.
No mide si ambas estrategias colapsan ante el mismo evento.
El PCA identifica estos colapsos conjuntos antes de que ocurran.

---

## FACTORES DE RIESGO IDENTIFICADOS

### Factor Dolar (USD)

Activos afectados: EUR/USD, GBP/USD, AUD/USD, XAU/USD
Todos tienen correlacion negativa con el USD.
En eventos de fortaleza del dolar (crisis, risk-off extremo)
todos estos activos se mueven juntos en la misma direccion.

Una estrategia en EURUSD y otra en XAUUSD pueden parecer
descorrelacionadas en condiciones normales.
En un evento de dolar fuerte — se mueven juntas.

### Factor Carry Trade

Activos afectados: USD/JPY, GBP/JPY, AUD/JPY
Pares de alto diferencial de tasas de interes.
Sensibles al ciclo de risk-on / risk-off global.
En momentos de panic selling los inversores cierran
posiciones carry masivamente — todos los pares JPY se mueven.

### Factor Risk-On / Risk-Off

Activos afectados: US500, DE40, XAU/USD (efecto refugio)
En crashes de mercado (2008, COVID, SVB) estos activos
se correlacionan fuertemente aunque en direcciones opuestas
(indices bajan, oro sube pero con alta correlacion en modulo).

---

## REGLA DE DIVERSIFICACION PCA

### En Capa 3+ (con 5+ estrategias activas)

Maximo 1 estrategia por factor de riesgo principal.
Si ya hay una estrategia en EURUSD (Factor Dolar):
  la siguiente estrategia no puede ser en XAUUSD, GBP/USD
  ni AUD/USD hasta que haya estrategias en otros factores.

### En Capa 0-2 (estado actual)

Maximo 2 activos del Factor Dolar simultaneamente.
Esta regla ya esta documentada en skill-portfolio-selection.md
como regla anti-monocultivo USD.

En Capa 0-2 el portfolio tiene pocas estrategias —
el PCA completo no es aplicable con 3-5 estrategias.
Se aplica la regla simplificada del Factor Dolar.

---

## ANALISIS POR SESION

Las correlaciones no son constantes a lo largo del dia.
El mismo par de activos puede tener correlaciones muy
distintas segun la sesion de trading.

| Sesion | Caracteristica | Correlaciones |
|--------|----------------|---------------|
| Asiatica (00:00-08:00 CEST) | Tecnicamente mas puro | Mas bajas |
| Londres (08:00-17:00 CEST) | Liquidez alta, noticias EU | Moderadas |
| Overlap Londres-NY (14:00-17:00) | Maxima liquidez | Mas altas |

El PCA debe calcularse por separado para cada sesion
cuando haya suficiente historial de produccion.
Una estrategia que opera en sesion asiatica puede
coexistir con otra que opera en overlap sin conflicto PCA.

Esta granularidad requiere:
  Minimo 6 meses de produccion real por estrategia.
  Clasificacion de cada trade por sesion en el log.
  No implementar antes de Fase 8.

---

## CUANDO IMPLEMENTAR

| Capa | Regla de diversificacion |
|------|-------------------------|
| Capa 0-2 | Regla anti-monocultivo USD (max 2 activos Factor Dolar) |
| Capa 3 | PCA simplificado — 1 estrategia por factor principal |
| Capa 4+ | PCA por sesion — analisis granular con historial real |

El PCA completo requiere:
  5+ estrategias activas con 3+ meses de produccion real.
  Datos de retorno diario por estrategia (de production-logs).
  Implementacion Python: sklearn.decomposition.PCA.

Antes de Capa 3: usar la regla anti-monocultivo USD
ya documentada en skill-portfolio-selection.md.

---

## INTEGRACION CON EL PIPELINE

El correlation-analyst ejecuta el PCA mensualmente
cuando hay 5+ estrategias activas.
El resultado informa al orchestrator pero no descarta
automaticamente ninguna estrategia existente.

Si el PCA revela que 2 estrategias responden al mismo factor:
  La mas reciente (menor historial) pasa a lista de espera.
  Se busca reemplazo en activo de factor diferente.
  No se retira la estrategia existente — solo se pausa el scaling.

---

## LO QUE ESTA SKILL NUNCA HACE

NUNCA reemplaza la correlacion de Pearson — la complementa.
NUNCA descarta estrategias en Capa 0-2 por analisis PCA.
NUNCA aplica el PCA por sesion sin 6 meses de historial real.
NUNCA permite mas de 1 estrategia por factor en Capa 3+.
