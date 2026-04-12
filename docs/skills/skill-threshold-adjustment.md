# Skill: Protocolo de Ajuste de Umbrales

## Proposito
Define cuando y como ajustar los criterios numericos
de skill-evaluation-auto.md de forma automatica
sin sesgo humano. Evita dos problemas:
1. Mantener umbrales demasiado estrictos que no
   dejan pasar ninguna candidata (parálisis)
2. Relajar umbrales por frustracion emocional
   sin justificacion estadistica (sesgo)

Los ajustes de umbrales se rigen por reglas
matematicas — no por decisiones humanas.

---

## PRINCIPIO FUNDAMENTAL

Los umbrales no son sagrados pero tampoco son
negociables emocionalmente. Solo se ajustan
cuando los datos demuestran que es necesario
y siempre dentro de rangos predefinidos.

Frases que NUNCA justifican un ajuste:
- "Llevamos mucho tiempo sin resultados"
- "Esta casi pasa, le bajamos un poco"
- "Con un poco menos de exigencia tendriamos mas"
- "En otros sistemas usan umbrales mas bajos"

Frases que SI justifican un ajuste:
- "En 3 builds consecutivos 0 candidatas pasan
  el Evaluation Gate con PF > 1.5 pero hay 50+
  con PF entre 1.3 y 1.5"
- "El 95% de las candidatas se descartan en la
  misma puerta por el mismo criterio"
- "Los datos estadisticos de 3 builds muestran
  que el umbral actual es inalcanzable para
  este activo con estas comisiones"

---

## CUANDO SE ACTIVA EL PROTOCOLO DE AJUSTE

El orchestrator activa este protocolo automaticamente
cuando detecta CUALQUIERA de estas condiciones:

### Condicion 1 — Bloqueo en Evaluation Gate
3 builds consecutivos del mismo activo con:
- 0 candidatas que pasan el Evaluation Gate
- Pero mas de 30 candidatas con PF entre 1.3 y 1.4
Indica que el umbral PF >= 1.5 puede ser demasiado
estricto para ese activo con esas comisiones.

### Condicion 2 — Bloqueo en paso 12b
3 ciclos consecutivos donde:
- Mas de 10 candidatas pasan el Evaluation Gate
- Pero 0 pasan el paso 12b
- La caida de PF promedio es 22-28%
Indica que el umbral de caida 20% puede ser
demasiado estricto.

### Condicion 3 — Bloqueo en WFO
5 candidatas consecutivas con:
- Todas descartadas en WFO
- WFE promedio entre 35% y 48%
Indica que el umbral WFE 50% puede ser
demasiado estricto para ese activo.

### Condicion 4 — Exceso de descartes en una puerta
Una puerta descarta mas del 95% de las candidatas
en 3 builds consecutivos por el MISMO criterio.
Indica que ese criterio especifico puede estar
calibrado demasiado estricto.

---

## COMO SE AJUSTAN LOS UMBRALES

### Regla 1 — Solo un criterio a la vez
Nunca ajustar mas de un criterio simultaneamente.
Si se ajustan dos a la vez no se puede saber
cual tuvo el efecto.

### Regla 2 — Ajuste minimo
Cada ajuste mueve el umbral lo minimo posible.
No saltar de PF >= 1.5 a PF >= 1.2.
Mover en pasos pequeños y medir el efecto.

### Regla 3 — Limites absolutos infranqueables
Cada criterio tiene un limite absoluto que
NUNCA se puede cruzar independientemente de
los datos. Estos limites protegen contra
estrategias verdaderamente malas.

### Regla 4 — Documentar y medir
Cada ajuste se documenta con la justificacion
estadistica. Despues de 2 builds con el nuevo
umbral se mide el efecto y se decide si
mantener, ajustar mas o revertir.

---

## TABLA DE UMBRALES AJUSTABLES

### Evaluation Gate

| Criterio | Valor actual | Minimo ajuste | Limite absoluto |
|----------|-------------|---------------|-----------------|
| PF IS | >= 1.5 | >= 1.4 | >= 1.3 |
| Max DD IS | <= 6% | <= 7% | <= 8% |
| Trades totales | >= 120 | >= 100 | >= 80 |
| Trades/mes | >= 10 | >= 8 | >= 6 |
| Win Rate | >= 38% | >= 35% | >= 30% |
| Anos positivos | >= 75% | >= 70% | >= 65% |

### Paso 12b

| Criterio | Valor actual | Minimo ajuste | Limite absoluto |
|----------|-------------|---------------|-----------------|
| PF OOS | >= 1.3 | >= 1.2 | >= 1.1 |
| Caida PF | <= 20% | <= 25% | <= 30% |
| DD OOS | <= 6.5% | <= 7% | <= 8% |
| Trades/mes OOS | >= 6 | >= 5 | >= 4 |

### WFO

| Criterio | Valor actual | Minimo ajuste | Limite absoluto |
|----------|-------------|---------------|-----------------|
| WFE | >= 50% | >= 45% | >= 40% |
| PF OOS promedio | >= 1.25 | >= 1.15 | >= 1.05 |
| PF OOS ultima | >= 1.1 | >= 1.0 | >= 0.9 |
| Desv parametros | < 25% | < 30% | < 35% |

### Portfolio

| Criterio | Valor actual | Minimo ajuste | Limite absoluto |
|----------|-------------|---------------|-----------------|
| Score minimo | >= 55 | >= 50 | >= 45 |
| Correlacion max | < 0.5 | < 0.55 | < 0.6 |
| DD combinado | < 12% | < 13% | < 15% |

---

## PROCESO DE AJUSTE AUTOMATICO

### Paso 1: Deteccion
El orchestrator detecta una de las 4 condiciones
de activacion durante la revision post-build.

### Paso 2: Identificacion
Identificar el criterio exacto que causa el bloqueo.
Verificar que es el MISMO criterio en los 3 builds.

### Paso 3: Verificacion de limite
Consultar la tabla — el criterio actual esta
por encima del limite absoluto?
Si esta en el limite absoluto → NO ajustar.
El problema no es el umbral — es el activo
o las comisiones. Probar otro activo.

### Paso 4: Calcular nuevo umbral
Mover al valor de "minimo ajuste" de la tabla.
Si ya esta en el minimo ajuste → mover al
limite absoluto.
Si ya esta en el limite absoluto → NO ajustar mas.

### Paso 5: Documentar
Crear archivo en docs\ con el ajuste:

AJUSTE DE UMBRAL — [fecha]
Criterio: [nombre]
Valor anterior: [valor]
Nuevo valor: [valor]
Condicion de activacion: [cual de las 4]
Datos estadisticos:
- Build [N]: [dato]
- Build [N+1]: [dato]
- Build [N+2]: [dato]
Justificacion: [estadistica, no emocional]
Limite absoluto: [valor] — NO se puede cruzar
Revision: despues de 2 builds con nuevo umbral
Decidido por: orchestrator-auto
Intervencion humana: NO

### Paso 6: Actualizar skill-evaluation-auto.md
Cambiar el valor del criterio en la skill.
Hacer commit con mensaje descriptivo.

### Paso 7: Medir efecto
Despues de 2 builds con el nuevo umbral:
- Mas candidatas pasan? Cuantas?
- Las que pasan son de calidad aceptable?
- El paso siguiente descarta demasiadas?

Si el ajuste no mejora los resultados → revertir.
Si mejora → mantener el nuevo umbral.

---

## CUANDO NO AJUSTAR UMBRALES

### El activo no tiene edge
Si despues de 3 builds con todos los umbrales
en el limite absoluto sigue sin haber candidatas
el problema NO es el umbral — es el activo.
Accion: el market-selector prioriza otro activo.
No seguir bajando umbrales.

### Las comisiones son demasiado altas
Si el activo tiene spreads altos (cripto, exoticos)
las comisiones pueden eliminar cualquier edge.
Accion: verificar comisiones con propfirm-analyst.
Considerar otra prop firm con mejores condiciones.

### Pocos datos historicos
Si el activo tiene datos desde 2017 (cripto)
en vez de 2003 hay menos muestra estadistica.
Accion: aceptar que los umbrales son correctos
pero la muestra es insuficiente. No ajustar.

### Frustración del equipo
Si el unico argumento es "llevamos mucho sin
resultados" → NO ajustar. Eso es sesgo emocional.
Los datos estadisticos deciden, no la frustracion.

---

## HISTORIAL DE AJUSTES

Mantener un registro en docs\ de todos los
ajustes realizados para poder analizar tendencias:

docs\threshold-history.md

Formato:
| Fecha | Criterio | Anterior | Nuevo | Razon | Efecto |
|-------|----------|----------|-------|-------|--------|
| [fecha] | [criterio] | [valor] | [valor] | [dato] | [resultado tras 2 builds] |

---

## REGLA FUNDAMENTAL

Los umbrales se ajustan por matematica.
No por emocion. No por prisa. No por frustracion.
Si los datos de 3 builds muestran que un umbral
es inalcanzable → se ajusta al minimo necesario.
Si no hay datos → no se toca.
El limite absoluto NUNCA se cruza.