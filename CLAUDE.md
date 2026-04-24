# CLAUDE.md — Constitucion del Proyecto TradingLab

## Proposito del proyecto
Sistema 100% automatico de generacion, validacion
y despliegue de portfolios de estrategias de trading
algoritmico para superar cuentas de fondeo (prop firms).
Sin sesgo humano en ninguna decision del pipeline.
Multi-activo. Multi-prop firm. Multi-estrategia.

## Filosofia del proyecto
4 principios inquebrantables:
1. SQ decide la logica de entrada — no el humano
2. Los numeros deciden que avanza — no la intuicion
3. El portfolio se construye por correlacion — no por preferencia
4. Los activos se priorizan por scoring — no por gusto

La unica intervencion humana es el forward test
en demo antes del challenge real.

## Por que esta filosofia
Builds 1-8: hipotesis humana + firma humana = 0 aprobadas
Build 9+: Builder libre + evaluacion automatica + multi-activo

El sesgo humano fue el problema. No la herramienta.
No el mercado. No la configuracion. El humano.

## Sistema de agentes (11 activos)
1. market-selector — prioriza activos por scoring numerico
2. market-analyst — configura Builder libre (NO genera hipotesis)
3. propfirm-analyst — compara prop firms automaticamente
4. funding-specialist — evalua compatibilidad FTMO
5. sq-specialist — configura SQ y genera informes tecnicos
6. evaluator-assistant — genera informes Evaluation Gate
7. correlation-analyst — gestiona portfolio automatico
8. export-specialist — exporta estrategias a MT5
9. performance-monitor — monitorea EAs en produccion
10. data-manager — gestiona datos de todos los activos
11. orchestrator — coordina y decide 100% automatico

## Universo de mercados

### Forex Majors (Dukascopy M1 desde 2003)
EUR/USD, GBP/USD, USD/JPY, USD/CHF,
AUD/USD, NZD/USD, USD/CAD

### Forex Crosses (Dukascopy M1 desde 2003)
EUR/GBP, EUR/JPY, GBP/JPY, EUR/AUD,
EUR/CHF, AUD/JPY, GBP/AUD, CAD/JPY, NZD/JPY

### Metales (Dukascopy M1 desde 2003)
XAU/USD (Oro), XAG/USD (Plata)

### Indices (Dukascopy M1 disponible)
US30 (Dow), US500 (S&P), NAS100 (Nasdaq),
DE40 (DAX), UK100 (FTSE), JP225 (Nikkei)

### Cripto (datos desde 2017-2018)
BTC/USD, ETH/USD

Total: 30+ activos disponibles.
Priorizados automaticamente por scoring numerico.
El market-selector decide el orden — no el humano.

## Temporalidad
H1 unicamente para todos los activos.

## Comisiones por activo
Cada activo tiene comisiones especificas que
deben verificarse con la prop firm objetivo
ANTES de cada build.

### Forex Majors
- Spread: 0.5-1.0 pips segun par
- Comision: 7 USD por lote
- Slippage: 0.5 pips

### Forex Crosses
- Spread: 0.8-2.0 pips segun par
- Comision: 7 USD por lote
- Slippage: 0.8 pips

### Metales
XAU/USD: Spread 30 pips + 7 USD + 2 pip slippage
XAG/USD: Spread 3 pips + 7 USD + 1 pip slippage

### Indices
- Spread y comision variable segun prop firm
- Verificar SIEMPRE antes de configurar

### Cripto
- Spread alto y variable
- Mercado 24/7 — ajustar opciones de negociacion
- Verificar SIEMPRE antes de configurar

## Enfoque de generacion
Builder libre con paleta completa de +100 indicadores.
Sin hipotesis humana. Sin restriccion de logica.
Modo continuo 24-48 horas por activo.
Configuracion en: docs\skills\skill-builder-libre.md

## Pipeline 100% automatico
Preparacion → Builder libre 24-48h →
Evaluation Gate AUTO → Retester → Paso 12b AUTO →
WFO → Dictamen AUTO → Portfolio AUTO →
Export → Demo (unico humano) → Challenge → Monitor

Criterios numericos en: docs\skills\skill-evaluation-auto.md

## Objetivo de portfolio
- Minimo: 3 estrategias no correlacionadas
- Optimo: 5 estrategias en activos diferentes
- Maximo: 8 estrategias activas
- Correlacion maxima entre par: 0.5
- DD combinado maximo: 12%
- Diversificacion por activo, estilo y grupo

Criterios en: docs\skills\skill-portfolio-selection.md

## Prop firms objetivo
- FTMO 2-Step: Forex + Metales + Indices
- E8 Funding: Forex + Metales
- TFT: Forex + Metales + Indices
- Apex: Futuros CME (cuando haya datos)
- MFF: Futuros CME (cuando haya datos)

El propfirm-analyst decide automaticamente
que prop firm es optima para cada estrategia
y activo. Sin preferencia humana.

## Reglas inquebrantables
1. SQ decide la logica — nunca el humano
2. Los numeros deciden — nunca la intuicion
3. Los activos se priorizan por score — no por gusto
4. Sin segunda oportunidad para descartadas
5. Comisiones reales verificadas antes de cada build
6. H1 como temporalidad para todos los activos
7. Ratio TP/SL minimo 2:1
8. Riesgo ajustable por tamaño de portfolio
9. Max 2 trades por dia por estrategia
10. Datos OOS nunca en el Builder
11. Forward test demo obligatorio antes de challenge
12. Portfolio por correlacion y diversificacion
13. CLAUDE.md no se modifica sin consenso

## Intervencion humana permitida
SOLO en estos momentos:
- Pulsar Inicio/Parar en SQ
- Lanzar Retester y Optimizer en SQ
- Forward test en demo (2 semanas)
- Comprar challenge en prop firm
- Revision semanal del estado
- Ajustar umbrales del sistema si necesario

En NINGUN otro momento el humano decide nada.

## Historial
Builds 1-8: enfoque hipotesis humana — TODOS FALLIDOS
Build 9+: enfoque Builder libre multi-activo sin sesgo

## Roadmap
Capa 0: pipeline automatico multi-activo (actual)
Capa 1: expansion completa de mercados
Capa 2: N8N + Claude API — ciclos autonomos
Capa 3: MT5 operando solo multi-prop firm
Capa 4: escalado y rebalanceo automatico

---

## REGLAS DE COMPORTAMIENTO — CLAUDE CODE

Estas reglas complementan la constitucion del proyecto.
Se aplican en todas las sesiones de trabajo.

### 1. Pensar antes de actuar
Antes de crear o modificar cualquier archivo, verificar:
- ¿Ya existe este archivo en el repo?
- ¿Ya existe esta funcionalidad en otro script?
- ¿Es esta la solucion mas simple posible?
Si la respuesta a las dos primeras es si → no duplicar.

### 2. Simplicidad primero
La solucion mas corta que funcione es la correcta.
Un script de 50 lineas es mejor que uno de 500.
Sin abstracciones prematuras.
Sin "por si acaso" — solo lo que se pide.

### 3. Cambios quirurgicos
Solo modificar el archivo indicado en la tarea.
No "aprovechar para mejorar" otros archivos.
No refactorizar lo que no esta roto.
Si hay que tocar un archivo no indicado → preguntar primero.

### 4. Ejecucion orientada al objetivo
Cada tarea tiene un criterio de exito claro.
Terminar cuando ese criterio se cumple.
Sin explicaciones innecesarias una vez completado.
Sin sugerir tareas adicionales no solicitadas.

### 5. Regla especifica de TradingLab
El planning maestro de 186 tareas define el trabajo.
No proponer tareas fuera del planning sin consultarlo.
No modificar criterios numericos del pipeline sin instruccion explicita.
Los criterios son los numeros — no la intuicion.