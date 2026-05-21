# Lessons Learned — TradingLab

## Proposito del documento
Registro permanente de aprendizajes reales derivados de
decisiones concretas del pipeline. Solo se documentan
hechos observados — no hipotesis ni teorias.
Este documento es consultado por el orchestrator al
inicio de cada nuevo ciclo para no repetir errores.

---

## FORMATO OBLIGATORIO DE CADA ENTRADA

Cada leccion sigue exactamente este formato:

```
### LECCION-[NNN]: [titulo corto]

Fecha: YYYY-MM-DD
Build(s): [numero(s) de build]
Decision: PASA / DESCARTAR / ALERTA / CONFIGURACION
Criterio que activo la decision: [criterio exacto]
Resultado observado: [que paso concretamente]
Leccion aplicable: [que debe cambiar o mantenerse en ciclos futuros]
Ocurrencias confirmadas: [N] / minimo 3 para leccion estructural
Estado: TENTATIVA / ESTRUCTURAL / OBSOLETA

CONTEXTO:
  Regimen de mercado: [tendencia-altavol / tendencia-bajovol /
    rango-altavol / rango-bajovol / N/A]
  Epoca del año: [Q1 / Q2 / Q3 / Q4] [año]
  Volumen relativo: [alto / normal / bajo / N/A]
  Prop firm activa: [FTMO / BrightFunded / E8 / ninguna]
  Activo principal: [XAUUSD / EURUSD / etc / N/A]
  Fase del proyecto: [Capa 0 / 1 / 2 / 3 / 4]
```

---

## CAMPO CONTEXTO — OBLIGATORIO EN CADA ENTRADA

Sin contexto una leccion puede ser ruido estadistico.
El contexto permite distinguir lecciones estructurales
(validas siempre) de lecciones situacionales
(validas solo en ese regimen o epoca).

Campos obligatorios del CONTEXTO:
  Regimen de mercado: tendencia-altavol /
    tendencia-bajovol / rango-altavol / rango-bajovol
  Epoca del año: Q1 / Q2 / Q3 / Q4 [año]
  Volumen relativo: alto / normal / bajo
  Prop firm activa: FTMO / BrightFunded / E8 / ninguna
  Activo principal: XAUUSD / EURUSD / etc
  Fase del proyecto: Capa 0 / 1 / 2 / 3 / 4

Si algun campo es N/A (configuracion de herramientas,
pre-build) documentarlo explicitamente como N/A
con una razon breve.

---

## REGLA ANTI-FALSA-LECCION

Una leccion es ESTRUCTURAL si tiene >= 3 ocurrencias confirmadas
en contextos diferentes.
Una leccion con 1-2 ocurrencias es TENTATIVA — se documenta
pero NO modifica los umbrales del sistema.

Razon: el mercado tiene suficiente ruido para que un patron
aparezca 2 veces por azar. Solo con 3+ confirmaciones
en contextos independientes se puede hablar de un patron real.

El orchestrator NO puede elevar una leccion TENTATIVA
a ESTRUCTURAL sin las 3 ocurrencias.
El humano tampoco puede hacerlo por intuicion.
El knowledge-synthesizer valida automaticamente si se cumplen
los requisitos de contextos independientes antes de elevar
el estado de cualquier leccion.

Estado de cada leccion:
  TENTATIVA: 1-2 ocurrencias
  ESTRUCTURAL: 3+ ocurrencias en al menos 2 regimenes de mercado
    distintos y en al menos 2 epocas del año distintas
  OBSOLETA: condiciones del mercado cambiaron — ya no aplica

---

## INSTRUCCION PARA EL ORCHESTRATOR

Cada decision importante del pipeline genera entrada automatica:

- Cada DESCARTAR en Evaluation Gate → registrar criterio y metricas
- Cada PASA al WFO → registrar metricas IS y context del regimen
- Cada DESCARTAR en WFO → registrar WFE y ventanas fallidas
- Cada ALERTA de Market Health Score < 50 → registrar contexto

Al inicio de cada ciclo nuevo el orchestrator lee este documento
y verifica:
  1. Las lecciones ESTRUCTURALES — para no repetir configuraciones
     que ya se sabe que fallan
  2. Las lecciones TENTATIVAS con 2 ocurrencias — para estar
     atento a una posible tercera confirmacion

---

## HISTORIAL DE LECCIONES

---

### LECCION-001: M15 con comisiones reales FTMO elimina el edge

Fecha: 2026-03-15 (estimado — dispositivo anterior)
Build(s): 3, 4, 5, 6
Decision: DESCARTAR (4 builds consecutivos)
Criterio que activo la decision: PF maximo < 1.3 con comisiones reales
Resultado observado: Builds 3-6 en M15 con comisiones FTMO reales
  (7 USD/lote + spread 0.5-1.0 pip) nunca superaron PF 1.27.
  Sin comisiones el PF llegaba a 1.53-1.70 (Build 4) —
  las comisiones eliminaban completamente el edge de M15.
Leccion aplicable: H1 como temporalidad minima para todos
  los activos con comisiones FTMO reales. M15 descartado
  formalmente del pipeline de produccion.
  Ver skill-timeframe-selector.md para la clasificacion completa.
Ocurrencias confirmadas: 4 — ESTRUCTURAL

CONTEXTO:
  Regimen de mercado: mixto (builds en periodos diferentes)
  Epoca del año: Q1 2026
  Volumen relativo: normal
  Prop firm activa: FTMO (objetivo)
  Activo principal: EURUSD (builds 3-6)
  Fase del proyecto: Capa 0

---

### LECCION-002: Hipotesis humana restringe el espacio de busqueda

Fecha: 2026-04-11 (formalizacion del aprendizaje)
Build(s): 1, 2, 3, 4, 5, 6, 7, 8
Decision: CONFIGURACION — cambio de enfoque completo
Criterio que activo la decision: 8 builds consecutivos sin
  producir una sola estrategia aprobada en el Evaluation Gate
Resultado observado: Builds 1-8 restringian el Builder a
  2-3 indicadores elegidos por el humano (EMA+ADX, NBAR+RSI,
  TrendFollowing EMA50). SQ solo exploraba combinaciones
  dentro del espacio limitado por la hipotesis humana.
  Ningun build produjo candidatas con PF >= 1.4 en Retester.
Leccion aplicable: eliminar toda hipotesis humana de la
  configuracion del Builder. Paleta completa de 100+
  indicadores sin restriccion. SQ decide la logica.
  Ver CLAUDE.md y skill-builder-libre.md.
Ocurrencias confirmadas: 8 — ESTRUCTURAL

CONTEXTO:
  Regimen de mercado: mixto (8 builds en varios meses)
  Epoca del año: Q4 2025 a Q1 2026
  Volumen relativo: normal
  Prop firm activa: FTMO (objetivo)
  Activo principal: EURUSD (builds 1-8)
  Fase del proyecto: Capa 0

---

### LECCION-003: PowerShell corrompe CSVs con separador ; de SQ

Fecha: 2026-04-20
Build(s): Fase 0 (pre-build)
Decision: CONFIGURACION — estandar de terminal del proyecto
Criterio que activo la decision: script de validacion fallaba
  al ejecutarse desde PowerShell debido a que Import-Csv
  asume coma como separador por defecto en entorno Windows
Resultado observado: al intentar procesar CSVs exportados
  por SQ con separador ; desde PowerShell, los datos se
  parseaban incorrectamente — todas las columnas quedaban
  en una sola o los numeros europeos (coma decimal) se
  corrompian. El script funcionaba correctamente con
  Python directo usando csv.DictReader(delimiter=";").
Leccion aplicable: usar Python directamente para toda
  manipulacion de CSVs de SQ. Nunca PowerShell para datos.
  Ver seccion "Estandar de terminal" en skill-builder-libre.md.
Ocurrencias confirmadas: 1 — TENTATIVA (pendiente confirmacion)

CONTEXTO:
  Regimen de mercado: N/A (configuracion de herramientas)
  Epoca del año: Q2 2026
  Volumen relativo: N/A
  Prop firm activa: ninguna
  Activo principal: N/A
  Fase del proyecto: Capa 0

---

### LECCION-004: Gaps M1 XAUUSD Dukascopy son estructurales, no un error

Fecha: 2026-04-20
Build(s): Build 10 (verificacion pre-build)
Decision: ALERTA → ACEPTADO con documentacion
Criterio que activo la decision: gaps del 2.615% en datos
  M1 XAUUSD Dukascopy detectados por data-manager
Resultado observado: los datos M1 del Oro en Dukascopy
  tienen gaps estructurales del 2-3% en cualquier descarga.
  No es un error de la descarga ni del proyecto.
  Causa probable: Dukascopy no tiene liquidez continua
  en XAU/USD los fines de semana y algunas sesiones asiaticas.
  Los gaps M1 tienen impacto minimo en velas H1 porque
  60 barras M1 construyen una vela H1 y los gaps aislados
  no distorsionan la vela H1 resultante.
Leccion aplicable: aceptar hasta 3% de gaps en datos M1
  para activos metalicos (XAU, XAG). Para forex majors
  el umbral de aceptacion es 0.5%.
  Ver docs/Fase-0-verificacion.md.
Ocurrencias confirmadas: 1 — TENTATIVA

CONTEXTO:
  Regimen de mercado: N/A (verificacion de datos)
  Epoca del año: Q2 2026
  Volumen relativo: N/A
  Prop firm activa: ninguna
  Activo principal: XAUUSD
  Fase del proyecto: Capa 0

---

### LECCION-005: CFX residual apunta a activo incorrecto

Fecha: 2026-05-04
Build(s): 11 (detectado pre-launch)
Decision: ALERTA -> CORREGIDO
Criterio: nodos EURUSD_dukascopy residuales en CFX de XAUUSD
Resultado observado: CFX tenía instrument=XAUUSD_ftmo correcto
  pero Chart symbol=EURUSD_M1_dukas incorrecto. SQ habría
  backtestado lógica XAUUSD con datos EURUSD.
Leccion aplicable: verificar TODOS los nodos del CFX antes
  de lanzar, no solo spread e instrumento FTMO.
  verify_cfx() obligatorio en sq-project-generator.py.
Ocurrencias confirmadas: 1 — TENTATIVA

CONTEXTO:
  Regimen de mercado: N/A
  Epoca del año: Q2 2026
  Volumen relativo: N/A
  Prop firm activa: ninguna
  Activo principal: XAUUSD
  Fase del proyecto: Capa 0

---

## LECCIONES PENDIENTES DE CONFIRMACION

Las siguientes situaciones han ocurrido una vez y estan
bajo observacion. Si se confirman 2 veces mas pasan a
ESTRUCTURAL y pueden modificar umbrales del sistema.

- Leccion-003: PowerShell corrompe CSVs (1 ocurrencia)
- Leccion-004: Gaps M1 XAU estructurales (1 ocurrencia)
- Leccion-005: CFX residual activo incorrecto (1 ocurrencia)

---

## ACTUALIZACION DEL DOCUMENTO

Este documento se actualiza:
- Automaticamente: cada vez que el orchestrator registra
  una decision que activa una leccion existente
- Manualmente por el humano: revision semanal del estado

El orchestrator añade entradas al historial pero NO puede:
- Elevar lecciones de TENTATIVA a ESTRUCTURAL sin las 3 ocurrencias
- Marcar lecciones como OBSOLETAS sin consenso humano
- Modificar los criterios del Evaluation Gate basandose
  en lecciones TENTATIVAS

---

### LECCION-005: XAUUSD H1 inviable con spread 60 pips y reglas FTMO

Fecha: 2026-05-15
Build(s): 9, 10, 11
Decision: DESCARTAR activo permanentemente
Criterio que activo la decision: Coste por trade supera el riesgo permitido
Resultado observado: Con spread 60 pips (30 real x2), SL 50 pips y capital
  25000 USD al 1% de riesgo, el coste por trade es 317 USD vs riesgo de 250 USD.
  El coste supera el riesgo en un 26.8%. Con ratio 2:1 el ratio efectivo real
  es 1.6:1, por debajo del minimo del sistema. 3 builds consecutivos con 0
  estrategias en Results confirman la inviabilidad.
Leccion aplicable: XAUUSD descartado permanentemente con las reglas actuales.
  Activos viables: EURUSD (5.8%), USDJPY (6%), AUDUSD (6.5%), GBPUSD (7.2%).
  Ver results/asset-viability-ranking.json para ranking completo.
Ocurrencias confirmadas: 3 — ESTRUCTURAL
Estado: ESTRUCTURAL

CONTEXTO:
  Regimen de mercado: mixto (3 builds en periodos diferentes)
  Epoca del año: Q1-Q2 2026
  Volumen relativo: normal
  Prop firm activa: FTMO (objetivo)
  Activo principal: XAUUSD
  Fase del proyecto: Capa 0

---

### LECCION-006: IS period < 100% genera muestra insuficiente en Retester

Fecha: 2026-05-21
Build(s): 12 (confirmado en builds anteriores)
Decision: DESCARTAR build completo
Criterio que activo la decision: Todas las estrategias con 5-23 trades en IS —
  por debajo del minimo de 80 trades requerido por el Evaluation Gate
Resultado observado: Build 12 configurado con IS period al 76%. El Builder
  divide el IS internamente cuando el periodo no es 100%, generando estrategias
  optimizadas sobre un subperiodo reducido. Resultado: 5-23 trades por
  estrategia en el periodo de evaluacion. El Retester descarto el build
  completo por muestra estadisticamente insuficiente. Ninguna estrategia
  supero los 80 trades minimos.
Leccion aplicable: IS period siempre al 100% en el Builder sin excepcion.
  Con IS parcial SQ sobreajusta a un subperiodo minimo y las estrategias
  no tienen muestra suficiente para validacion estadistica.
  Verificar IS period = 100% en checklist pre-build obligatorio.
Ocurrencias confirmadas: 2+ — ESTRUCTURAL (build 12 + builds anteriores)
Estado: ESTRUCTURAL

CONTEXTO:
  Regimen de mercado: N/A (error de configuracion del Builder)
  Epoca del año: Q2 2026
  Volumen relativo: N/A
  Prop firm activa: FTMO (objetivo)
  Activo principal: EURUSD
  Fase del proyecto: Capa 0
