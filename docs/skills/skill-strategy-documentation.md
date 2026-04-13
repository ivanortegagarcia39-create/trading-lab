# Skill: Documentacion de Estrategias Generadas por SQ

## Proposito
Define como documentar la logica de cada estrategia
que SQ genera libremente. Con el Builder libre
nadie diseño la logica — SQ la encontro solo.
Necesitamos entender que hace cada estrategia
aprobada para poder diagnosticar problemas
en produccion si los hay.

---

## POR QUE DOCUMENTAR SI NO DISEÑAMOS LA LOGICA

Con el enfoque anterior el humano diseñaba la
logica y sabia exactamente que indicadores usaba.
Con el Builder libre SQ puede generar estrategias
con combinaciones de 5-6 indicadores que nadie
penso. Si el EA falla en produccion y no sabes
que logica tiene no puedes diagnosticar nada.

La documentacion NO es para juzgar la logica.
Es para poder diagnosticar problemas tecnicos.

---

## CUANDO DOCUMENTAR

Documentar la logica de una estrategia cuando
pasa el Evaluation Gate — antes del Retester.
No documentar las descartadas — son demasiadas
y no aporta valor.

Actualizar la documentacion cuando:
- El WFO cambia parametros (v1 → v2)
- Se exporta a MT5 (v2 → v3)
- Se detecta un problema en produccion

---

## COMO EXTRAER LA LOGICA DE SQ

### Paso 1: Abrir la estrategia en SQ
En el databank del Builder seleccionar la
estrategia y hacer doble clic para ver los detalles.

### Paso 2: Ir a la pestaña Codigo/Logica
SQ muestra la logica de la estrategia en
formato visual o pseudocodigo.

### Paso 3: Documentar los elementos

Extraer y documentar:

CONDICIONES DE ENTRADA LONG:
- Condicion 1: [indicador] [operador] [valor/indicador]
- Condicion 2: [indicador] [operador] [valor/indicador]
- Condicion 3: [indicador] [operador] [valor/indicador]

CONDICIONES DE ENTRADA SHORT:
- Condicion 1: [indicador] [operador] [valor/indicador]
- Condicion 2: [indicador] [operador] [valor/indicador]
- Condicion 3: [indicador] [operador] [valor/indicador]

STOP LOSS:
- Tipo: [ATR-based / fijo]
- Valor: [multiplicador ATR o pips]
- Periodo ATR: [valor]

TAKE PROFIT:
- Tipo: [ATR-based / fijo]
- Valor: [multiplicador ATR o pips]
- Periodo ATR: [valor]
- Ratio TP/SL efectivo: [valor]:1

INDICADORES USADOS:
- [indicador 1]: periodo [valor]
- [indicador 2]: periodo [valor]
- [indicador 3]: periodo [valor]

FILTROS:
- Horario: [inicio] a [fin]
- Max trades/dia: [valor]
- Direccion: [long+short / solo long / solo short]

---

## FORMATO DEL DOCUMENTO DE LOGICA

Guardar en:
results\reviewed\[ID]-logica.md

Formato:

# Logica de Estrategia — [ID]

## Identificacion
ID: [ACTIVO]-[BUILD]-[ID-SQ]
Activo: [simbolo]
Build: [numero]
Generada por: SQ Builder libre
Fecha: [fecha]

## Tipo de estrategia
Clasificacion SQ: [lo que SQ indique]
Estilo aparente: [trend-following / mean-reversion / breakout / mixto]
Complejidad: [numero de condiciones de entrada]

## Logica de entrada

### Long
Condicion 1: [descripcion exacta]
Condicion 2: [descripcion exacta]
Condicion 3: [descripcion exacta si existe]

Traduccion a lenguaje natural:
"Entra largo cuando [descripcion simple]"

### Short
Condicion 1: [descripcion exacta]
Condicion 2: [descripcion exacta]
Condicion 3: [descripcion exacta si existe]

Traduccion a lenguaje natural:
"Entra corto cuando [descripcion simple]"

### Simetria
La logica long y short son simetricas: SI/NO
Si NO → documentar la diferencia

## Gestion de salida
SL: [tipo y valor]
TP: [tipo y valor]
Ratio TP/SL: [valor]:1
Salida fin de dia: SI/NO
Salida viernes: SI/NO

## Indicadores utilizados
| Indicador | Periodo | Rol en la logica |
|-----------|---------|-----------------|
| [nombre] | [valor] | [entrada/filtro/salida] |
| [nombre] | [valor] | [entrada/filtro/salida] |
| [nombre] | [valor] | [entrada/filtro/salida] |

## Parametros principales
| Parametro | Valor v1 | Valor v2 (WFO) | Optimizable |
|-----------|----------|----------------|-------------|
| [nombre] | [valor] | [valor] | SI/NO |
| [nombre] | [valor] | [valor] | SI/NO |
| [nombre] | [valor] | [valor] | SI/NO |

## Observaciones tecnicas
- Numero total de condiciones: [N]
- Usa indicadores de tendencia: SI/NO — [cuales]
- Usa indicadores de momentum: SI/NO — [cuales]
- Usa indicadores de volatilidad: SI/NO — [cuales]
- Usa precio puro: SI/NO — [cuales]
- Logica comprensible: SI/NO
  (algunas estrategias de SQ tienen logica
  que funciona estadisticamente pero no tiene
  explicacion economica obvia — es normal)

---

## DIAGNOSTICO DE PROBLEMAS EN PRODUCCION

Cuando el performance-monitor detecta problemas
con un EA en produccion consultar este documento
para diagnosticar:

### El EA no genera trades
Verificar las condiciones de entrada.
Si usa indicador de tendencia (ADX, EMA) puede
que el mercado este en regimen opuesto.
Si usa condicion de precio (Highest/Lowest) puede
que la volatilidad sea insuficiente.

### El EA genera demasiados trades
Verificar los filtros.
Si las condiciones de entrada son poco restrictivas
el EA puede generar mas señales de las esperadas
en periodos de alta volatilidad.

### SL se activa demasiado frecuentemente
Verificar el multiplicador ATR.
Si el ATR actual es mayor que el ATR historico
del backtest el SL puede estar demasiado ajustado.

### TP nunca se alcanza
Verificar el ratio TP/SL.
Si el TP es muy ambicioso (4x ATR) en un mercado
de baja volatilidad actual puede no alcanzarse.

### Rendimiento peor que el backtest
Verificar si los indicadores usados dependen
de un regimen de mercado especifico.
Si el mercado cambio de regimen la estrategia
puede estar fuera de su contexto favorable.

---

## LO QUE ESTA DOCUMENTACION NO HACE

NO juzga si la logica tiene sentido economico.
NO recomienda cambiar la logica.
NO sugiere mejoras a la estrategia.
NO opina sobre los indicadores elegidos por SQ.

SQ encontro la logica. Los numeros la validaron.
La documentacion solo registra que hace para
poder diagnosticar problemas tecnicos.

---

## REGLA FUNDAMENTAL

Documentar no es juzgar. Documentar es registrar.
Si SQ genero una estrategia con CCI + Keltner + ROC
que pasa todos los filtros del pipeline no importa
si un humano entiende por que funciona.
Los numeros dicen que funciona. Eso es suficiente.
La documentacion existe para diagnosticar fallos
tecnicos — no para validar la logica.