# Skill: Versionado de Estrategias

## Proposito
Define como rastrear cada version de una estrategia
a lo largo del pipeline — desde que SQ la genera
hasta que opera en produccion.
Sin versionado claro es imposible saber que version
esta en cada fase, que parametros tiene y que
cambios se hicieron en el WFO o la exportacion.

---

## POR QUE ES CRITICO

Una estrategia pasa por 6 transformaciones:

1. SQ la genera en el Builder (version original)
2. Pasa el Evaluation Gate (misma version)
3. Se retestea con datos OOS (misma version)
4. Se optimiza en el WFO (parametros cambian)
5. Se exporta a MT5 (formato cambia)
6. Opera en produccion (posibles ajustes de riesgo)

Si no hay versionado claro:
- No sabes que parametros tiene el EA en produccion
- No puedes comparar el backtest con la operacion real
- Si algo falla no sabes que version revisar
- Si quieres reemplazar no sabes que version era

---

## SISTEMA DE IDENTIFICACION

### ID unico de estrategia
Cada estrategia generada por SQ tiene un ID
interno en el databank. Usar ese ID como base.

Formato del ID del proyecto:
[ACTIVO]-[BUILD]-[ID-SQ]-[VERSION]

Ejemplo:
EURUSD-B9-0847-v1

Donde:
- EURUSD: activo
- B9: Build numero 9
- 0847: ID interno de SQ en el databank
- v1: version 1 (original del Builder)

### Versiones

v1 — Version original del Builder
La estrategia tal como SQ la genero.
Parametros originales sin modificar.
Archivo: results\raw\build-results\[ID]-v1.sqx

v2 — Version post-WFO
Parametros optimizados por Walk-Forward.
Los parametros que cambiaron se documentan.
Archivo: results\approved\[ID]-v2.sqx

v3 — Version exportada a MT5
Codigo MQL5 compilado con parametros finales.
Puede tener ajustes de riesgo por portfolio.
Archivo: results\approved\[ID]-v3.mq5

v4 — Version en produccion
EA activo en cuenta de prop firm.
Riesgo ajustado segun tamaño del portfolio.
Magic number asignado.
No hay archivo — es el v3 con config especifica.

---

## DOCUMENTO DE TRAZABILIDAD

Cada estrategia que pasa el Evaluation Gate
recibe un documento de trazabilidad que se
actualiza en cada fase del pipeline.

Guardar en:
results\reviewed\[ID]-trazabilidad.md

Formato:

# Trazabilidad — [ID]

## Datos generales
ID: [ACTIVO]-[BUILD]-[ID-SQ]
Activo: [simbolo]
Build: [numero]
Ticket: [TICKET-ID]
Fecha generacion: [fecha]
Prop firm objetivo: [nombre]

## Version 1 — Builder original
Fecha: [fecha]
Archivo: results\raw\build-results\[ID]-v1.sqx
Logica: [descripcion generada por SQ]
Indicadores usados: [lista]
Condiciones de entrada: [lista]
SL: [valor ATR]
TP: [valor ATR]
Parametros principales:
  - [param 1]: [valor]
  - [param 2]: [valor]
  - [param 3]: [valor]

Metricas IS:
  - PF: [valor]
  - DD: [valor]%
  - Trades: [numero]
  - Trades/mes: [numero]
  - Win Rate: [valor]%
  - Ratio TP/SL: [valor]:1

Estado: EVALUATION GATE [PASA/DESCARTAR]

## Version 1 — Retester OOS
Fecha: [fecha]
Periodo OOS: 2021.01.01 a [fecha]

Metricas OOS:
  - PF OOS: [valor]
  - DD OOS: [valor]%
  - Caida PF: [valor]%
  - Trades OOS: [numero]

Estado paso 12b: [CONTINUAR/DESCARTAR]

## Version 2 — Post-WFO
Fecha: [fecha]
Archivo: results\approved\[ID]-v2.sqx

Parametros ANTES del WFO (v1):
  - [param 1]: [valor original]
  - [param 2]: [valor original]
  - [param 3]: [valor original]

Parametros DESPUES del WFO (v2):
  - [param 1]: [valor optimizado]
  - [param 2]: [valor optimizado]
  - [param 3]: [valor optimizado]

WFE: [valor]%
Dictamen WFO: [APROBADA/DESCARTAR]

## Version 3 — Exportacion MT5
Fecha: [fecha]
Archivo: results\approved\[ID]-v3.mq5
Compilacion: sin errores SI/NO
Backtest MT5 PF: [valor]
Backtest SQ PF: [valor]
Diferencia: [valor]%
Simbolo MT5: [nombre exacto en broker]
Magic number: [numero]

## Version 4 — Produccion
Fecha inicio: [fecha]
Prop firm: [nombre]
Cuenta: [tamaño]
Riesgo por trade: [valor]% (ajustado por portfolio)
Forward test demo: [fechas]
Forward test resultado: CORRECTO / PROBLEMA
Estado: ACTIVO / PAUSADO / RETIRADO

## Historial de cambios
| Fecha | Version | Cambio | Razon |
|-------|---------|--------|-------|
| [fecha] | v1 | Generada por Builder libre | Build [N] |
| [fecha] | v1 | Aprobada Evaluation Gate | Criterios auto |
| [fecha] | v1 | Aprobada paso 12b | PF OOS [valor] |
| [fecha] | v2 | Parametros optimizados WFO | WFE [valor]% |
| [fecha] | v2 | Aprobada dictamen WFO | ROBUSTA |
| [fecha] | v2 | Incluida en portfolio | Score [valor] corr [valor] |
| [fecha] | v3 | Exportada a MT5 | Compilacion OK |
| [fecha] | v4 | Activada en produccion | Forward test OK |

---

## REGLAS DE VERSIONADO

### Regla 1 — Nunca modificar versiones anteriores
v1 se conserva siempre intacta. Si el WFO cambia
parametros se crea v2. Nunca sobreescribir v1.

### Regla 2 — Documentar cada cambio de parametro
Si un parametro cambia entre versiones documentar:
- Que parametro cambio
- Valor anterior
- Valor nuevo
- Razon del cambio (WFO, ajuste portfolio, etc)

### Regla 3 — Un solo archivo por version
v1 = un archivo .sqx
v2 = un archivo .sqx
v3 = un archivo .mq5
No tener multiples archivos de la misma version.

### Regla 4 — Trazabilidad completa antes de produccion
Antes de activar un EA en produccion el documento
de trazabilidad debe tener TODAS las secciones
completadas hasta Version 3. Sin excepciones.

### Regla 5 — ID inmutable
Una vez asignado el ID no cambia aunque la
estrategia pase por WFO o exportacion.
EURUSD-B9-0847 es siempre esa estrategia.
Las versiones v1/v2/v3/v4 indican la fase.

---

## ESTRUCTURA DE ARCHIVOS POR ESTRATEGIA

Cuando una estrategia avanza en el pipeline
sus archivos se organizan asi:

results\raw\build-results\EURUSD-B9-0847-v1.sqx
results\reviewed\EURUSD-B9-0847-trazabilidad.md
results\reviewed\EURUSD-B9-0847-funding-eval.md
results\reviewed\EURUSD-B9-0847-propfirm-eval.md
results\approved\EURUSD-B9-0847-v2.sqx
results\approved\EURUSD-B9-0847-v3.mq5
results\approved\EURUSD-B9-0847-export-report.md
results\approved\EURUSD-B9-0847-prechallenge-checklist.md

Si se descarta en cualquier fase:
results\rejected\EURUSD-B9-0847-v1.sqx
results\rejected\EURUSD-B9-0847-descarte.md

---

## INTEGRACION CON EL PIPELINE

El sq-specialist crea el documento de trazabilidad
cuando una estrategia pasa el Evaluation Gate.
Lo actualiza en cada fase posterior.

El export-specialist completa las secciones
de Version 3 durante la exportacion.

El performance-monitor actualiza la seccion
de Version 4 cuando el EA entra en produccion.

El correlation-analyst referencia el ID unico
en todos los informes de portfolio.

---

## REGLA FUNDAMENTAL

Cada estrategia tiene un ID unico inmutable
y un documento de trazabilidad completo.
Si no sabes que version esta en produccion
no deberias tener un EA operando.
La trazabilidad no es opcional — es obligatoria
antes de activar cualquier EA.