# Skill: Evaluation Gate Automatico — Sin Intervencion Humana

## Proposito
Define los criterios numericos exactos que el
orchestrator y el evaluator-assistant aplican
de forma 100% automatica para aprobar o descartar
estrategias en cada puerta del pipeline.
Ninguna decision subjetiva. Solo numeros.

---

## FILOSOFIA DE LA EVALUACION AUTOMATICA

El sesgo humano en la seleccion de estrategias
fue la causa principal de los 8 builds fallidos.
Frases como "esta parece prometedora" o "le damos
otra oportunidad" no existen en este sistema.

Una estrategia cumple los numeros o no los cumple.
No hay zona gris salvo casos estadisticamente
excepcionales que representan menos del 5%
de las candidatas.

---

## FASE 1 — FILTRO DEL BUILDER (automatico en SQ)

Estas estrategias nunca llegan al Evaluation Gate
porque SQ las descarta internamente:

- PF < 1.3 → no entra en el databank
- Trades/mes < 6 → no entra en el databank
- Ratio Ret/DD < 0.8 → no entra en el databank

Solo las estrategias que superan estos filtros
aparecen en el databank para ser evaluadas.

---

## FASE 2 — EVALUATION GATE (automatico por orchestrator)

### Criterios de DESCARTE AUTOMATICO
Si cumple CUALQUIERA de estos → DESCARTAR
sin consultar al humano:

- PF in-sample < 1.4
- Max DD in-sample > 7%
- Trades totales < 80
- Trades por mes < 8
- Win Rate < 30%
- Ratio TP/SL efectivo < 1.8:1
- Años con PF < 1.0 superan el 35% del total
- Mas del 45% del beneficio en un solo mes
- DD maximo ocurre en los ultimos 3 meses del IS
- Max racha perdedora > 8 trades consecutivos

### Criterios de APROBACION AUTOMATICA para Retester
Si cumple TODOS estos → PASA al Retester
sin consultar al humano:

- PF in-sample >= 1.5
- Max DD in-sample <= 6%
- Trades totales >= 120
- Trades por mes >= 10
- Win Rate >= 38%
- Ratio TP/SL efectivo >= 2:1
- Años con PF >= 1.0 superan el 75% del total
- Ningun mes con mas del 40% del beneficio total
- DD maximo NO en los ultimos 3 meses del IS
- Max racha perdedora <= 6 trades consecutivos
- Monte Carlo: sin degradacion significativa

### Zona de revision automatica
Si no cae en descarte ni en aprobacion el
orchestrator clasifica como REVISION PENDIENTE.

Criterios de revision automatica:
- PF entre 1.4 y 1.5 → revisar si trades > 150
  Si trades > 150 → PASA (mayor muestra compensa)
  Si trades <= 150 → DESCARTAR
- DD entre 6% y 7% → revisar si PF > 1.6
  Si PF > 1.6 → PASA (alto PF compensa DD marginal)
  Si PF <= 1.6 → DESCARTAR
- Años negativos entre 25% y 35% → revisar si
  los años negativos coinciden con crisis conocidas
  (2008, 2015, 2020) → PASA
  Si no coinciden con crisis → DESCARTAR

CRITICO: Estas reglas de revision tambien son
automaticas. El orchestrator las aplica sin
consultar al humano. No hay zona gris real.

---

## FASE 3 — ANALISIS OOS PASO 12b (automatico)

### Criterios de DESCARTE AUTOMATICO
Si cumple CUALQUIERA → DESCARTAR sin consultar:

- PF OOS < 1.2
- Caida de PF (IS → OOS) > 25%
- DD OOS > 7%
- Trades/mes OOS < 5
- Frecuencia OOS cae mas del 50% respecto al IS

### Criterios de APROBACION para WFO
Si cumple TODOS → PASA al WFO sin consultar:

- PF OOS >= 1.3
- Caida de PF <= 20%
- DD OOS <= 6.5%
- Trades/mes OOS >= 6
- Frecuencia OOS no cae mas del 40% respecto al IS

### Revision automatica paso 12b
- PF OOS entre 1.2 y 1.3 → DESCARTAR
  (no llegara al umbral necesario en WFO)
- Caida PF entre 20% y 25% → DESCARTAR
  (sobreajuste probable)
- DD OOS entre 6.5% y 7% → DESCARTAR
  (margen insuficiente para FTMO)

En el paso 12b NO hay zona gris.
O pasa o se descarta. El WFO es demasiado
costoso en tiempo para lanzarlo con dudas.

---

## FASE 4 — DICTAMEN WFO (automatico)

### Criterios de DESCARTE AUTOMATICO
Si cumple CUALQUIERA → DESCARTAR sin consultar:

- WFE < 40%
- 2 o mas ventanas OOS con PF < 1.0
- 2 ventanas OOS negativas consecutivas
- DD OOS > 7.5% en cualquier ventana
- PF OOS < 1.0 en la ultima ventana
- Parametros optimos con desviacion > 35%
  entre ventanas

### Criterios de APROBACION AUTOMATICA FINAL
Si cumple TODOS → ESTRATEGIA APROBADA
sin consultar al humano:

- WFE >= 50%
- 0 ventanas OOS con PF < 0.9
- Maximo 1 ventana OOS con PF entre 0.9 y 1.0
  y debe ser aislada (no consecutiva)
- DD OOS <= 7% en todas las ventanas
- PF OOS ultima ventana >= 1.1
- Parametros optimos con desviacion < 25%
- PF OOS promedio >= 1.25

### Revision automatica WFO
- WFE entre 40% y 50% → DESCARTAR
  (robustez insuficiente para produccion)
- 1 ventana negativa aislada con WFE > 50%
  → PASA si PF OOS promedio >= 1.3
  → DESCARTAR si PF OOS promedio < 1.3

---

## FASE 5 — VALIDACION DE PORTFOLIO (automatico)

Despues de la aprobacion WFO el correlation-analyst
aplica estos criterios automaticamente:

### Criterios de INCLUSION en portfolio
Si cumple TODOS → se incluye automaticamente:

- Correlacion con cada estrategia activa < 0.5
- DD combinado estimado con portfolio < 12%
- No mas de 2 estrategias del mismo estilo
  (trend-following o mean-reversion) activas
- No mas de 2 estrategias en el mismo activo

### Criterios de ESPERA
Si no cumple inclusion pero la estrategia es valida:

- Correlacion > 0.5 con alguna activa → ESPERA
  Queda en cola hasta que la activa se retire
- DD combinado > 12% → ESPERA
  Queda en cola hasta que el DD del portfolio baje

### Criterios de DESCARTE de portfolio
- Correlacion > 0.7 con 2 o mas activas → DESCARTAR
  Demasiado redundante para el portfolio

---

## FASE 6 — FORWARD TEST EN DEMO (unica intervencion humana)

Esta es la UNICA fase donde el humano interviene.

Duracion: minimo 2 semanas en cuenta demo
de la prop firm objetivo.

El humano verifica:
- El EA abre y cierra posiciones correctamente
- Los SL y TP se ejecutan en los niveles correctos
- El tamaño de posicion es correcto (1% del balance)
- El EA respeta el maximo de 2 trades por dia
- El EA no opera fuera del horario configurado
- El EA no opera los fines de semana

Decision humana:
[ ] EA funciona correctamente → LANZAR CHALLENGE
[ ] EA tiene problemas → REVISAR exportacion

Esta es la unica decision humana en todo el pipeline.

---

## RESUMEN DE TASAS DE DESCARTE ESPERADAS

Con el Builder libre generando 1000+ candidatas:

Builder → Evaluation Gate: ~60-70% descartadas
Evaluation Gate → Retester: ~20-30% pasan
Retester → paso 12b: ~40-50% descartadas
Paso 12b → WFO: ~50-60% pasan
WFO → Aprobacion: ~30-40% pasan
Portfolio → Inclusion: ~60-80% incluidas

Resultado esperado de 1000 candidatas:
~5-15 estrategias aprobadas por el WFO
~3-10 incluidas en el portfolio

Esto es NORMAL. Un ratio del 1% de candidatas
que llegan a produccion es estandar en la industria.

---

## FLUJO COMPLETO SIN INTERVENCION HUMANA

SQ Builder libre corriendo 24-48h
        ↓
1000+ candidatas en databank
        ↓
Evaluation Gate automatico (orchestrator)
~200-300 pasan
        ↓
Retester automatico (sq-specialist)
        ↓
Paso 12b automatico (orchestrator)
~100-150 pasan
        ↓
WFO automatico (sq-specialist)
        ↓
Dictamen WFO automatico (orchestrator)
~5-15 aprobadas
        ↓
Portfolio automatico (correlation-analyst)
~3-10 incluidas
        ↓
Export a MT5 (export-specialist)
        ↓
Forward test en demo (UNICA intervencion humana)
        ↓
Challenge en prop firm
        ↓
Performance monitor automatico

---

## REGLA FUNDAMENTAL

Los numeros deciden. No las personas.
Si cumple los umbrales → avanza.
Si no cumple → se descarta.
Sin excepciones. Sin segunda oportunidad.
Sin "parece prometedora".