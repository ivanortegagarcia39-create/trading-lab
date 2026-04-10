# CLAUDE.md — Constitucion del Proyecto TradingLab

## Proposito del proyecto
Desarrollar un sistema 100% automatico de generacion,
validacion y despliegue de estrategias de trading
algoritmico para superar cuentas de fondeo (prop firms).
Sin sesgo humano en la seleccion de estrategias.
Sin intervencion humana en las decisiones del pipeline.

## Filosofia del proyecto
El mercado no sabe lo que el humano piensa que
deberia funcionar. Los Builds 1-8 fallaron porque
un humano decidia que indicadores usar y SQ solo
podia buscar dentro de ese espacio limitado.

Principios fundamentales:
1. SQ decide la logica de entrada — no el humano
2. Los numeros deciden que avanza — no la intuicion
3. El portfolio se construye por correlacion — no por preferencia
4. La unica intervencion humana es el forward test en demo

## Definicion de robustez
Una estrategia es robusta si cumple TODOS estos
criterios numericos sin excepcion:
- PF IS >= 1.5
- PF OOS >= 1.3
- Caida PF IS→OOS <= 20%
- Max DD <= 6.5% en IS y OOS
- WFE >= 50%
- Trades >= 120 en IS
- Años positivos >= 75%
- Monte Carlo sin degradacion significativa
- Correlacion < 0.5 con cada estrategia del portfolio

Si falla UN solo criterio → se descarta automaticamente.

## Rol de Claude en este proyecto
Claude actua como orquestador automatico.
Claude aplica criterios numericos sin subjetividad.
Claude coordina agentes en el orden correcto.
Claude NO toma decisiones basadas en intuicion.
Claude NO da segunda oportunidad a estrategias descartadas.
Claude NO genera hipotesis de logica de entrada.

## Sistema de agentes (11 activos)

### Agentes operativos
1. market-selector — selecciona activo optimo
2. market-analyst — configura parametros de busqueda
   (NO genera hipotesis — rol rediseñado)
3. propfirm-analyst — analiza y compara prop firms
4. funding-specialist — evalua compatibilidad FTMO
5. sq-specialist — configura SQ y genera informes
6. evaluator-assistant — genera informes Evaluation Gate
7. correlation-analyst — gestiona portfolio automatico
8. export-specialist — exporta estrategias a MT5
9. performance-monitor — monitorea EAs en produccion
10. data-manager — gestiona datos historicos en SQ
11. orchestrator — coordina y decide automaticamente

### Agentes planificados
- risk-manager — gestion de riesgo avanzada
- news-researcher — contexto macro

## Enfoque de generacion de estrategias
Builder libre de SQ con paleta completa de
+100 indicadores. Sin hipotesis humana.
Sin restriccion de logica de entrada.

Lo que el humano define: restricciones de riesgo
Lo que SQ define: logica de entrada
Lo que el pipeline filtra: sobreajuste

Configuracion completa en:
docs\skills\skill-builder-libre.md

## Pipeline 100% automatico

Fase 1 — Preparacion:
data-manager → market-selector → market-analyst
(configurar Builder libre)

Fase 2 — Build:
SQ Builder libre corriendo 24-48h en modo continuo
1000+ candidatas en databank

Fase 3 — Evaluacion automatica:
evaluator-assistant → orchestrator aplica
criterios de skill-evaluation-auto.md
~200-300 pasan al Retester

Fase 4 — Validacion automatica:
Retester → paso 12b → WFO
Criterios automaticos en cada puerta
~5-15 estrategias aprobadas

Fase 5 — Portfolio automatico:
correlation-analyst selecciona combinaciones
~3-10 incluidas en portfolio

Fase 6 — Produccion:
export-specialist → forward test demo
(UNICA intervencion humana)
→ challenge → performance-monitor

Criterios numericos completos en:
docs\skills\skill-evaluation-auto.md

## Universo de mercados
Mercados activos:
- EUR/USD (Forex spot — datos en SQ)
- XAU/USD (Oro spot — datos en SQ)

Mercados pendientes:
- GBP/USD, USD/JPY — Capa 1
- GC, NQ (futuros CME) — Capa 2

Temporalidad: H1 unicamente

## Prop firm principal
FTMO Challenge 2-Step — cuenta 25.000 USD
Reglas completas en: docs\funding-rules.md

Puntos criticos:
- Daily Loss 5% DINAMICO
- Max DD 10% DINAMICO solo sube
- Min 4 dias con posiciones INICIADAS
- Sin Regla del Mejor Dia en 2-Step
- Margenes operativos: 3% daily, 7% max DD

## Objetivo de portfolio
Portfolio minimo: 3 estrategias no correlacionadas
Portfolio optimo: 5 estrategias no correlacionadas
Correlacion maxima entre cualquier par: 0.5
DD combinado maximo: 12%

Criterios en: docs\skills\skill-portfolio-selection.md

## Configuracion estandar FTMO
Obligatoria en TODOS los builds y retests:

EUR/USD:
- Spread: 0.5 pips
- Comision: 7 USD por lote
- Slippage: 0.5 pips

XAU/USD:
- Spread: 30 pips
- Comision: 7 USD por lote
- Slippage: 2 pips

Periodo IS: 2003.05.05 a 2020.12.31
Periodo OOS: 2021.01.01 a fecha actual

## Reglas inquebrantables
1. SQ decide la logica — nunca el humano
2. Los numeros deciden — nunca la intuicion
3. Sin segunda oportunidad para estrategias descartadas
4. Comisiones reales FTMO en todos los builds
5. H1 como temporalidad principal
6. Ratio TP/SL minimo 2:1
7. Riesgo 1% por trade (ajustable por portfolio)
8. Max 2 trades por dia
9. Datos OOS nunca en el Builder
10. Mismas comisiones en Builder y Retester
11. Forward test demo obligatorio antes de challenge
12. Portfolio por correlacion no por preferencia
13. CLAUDE.md no se modifica sin consenso

## Intervencion humana permitida
SOLO en estos momentos:
- Lanzar y parar el Builder en SQ
- Lanzar Retester y Optimizer en SQ
- Forward test en demo (2 semanas)
- Comprar challenge en prop firm
- Revision semanal del estado del sistema
- Ajustar umbrales del sistema si es necesario

En NINGUN otro momento el humano decide nada.

## Historial de builds
Builds 1-8: enfoque con hipotesis humana — TODOS FALLIDOS
Build 9+: enfoque Builder libre sin sesgo humano

## Roadmap
Capa 0: pipeline automatico manual (estado actual)
Capa 1: expansion mercados tras 3 estrategias
Capa 2: N8N + Claude API — ciclos continuos
Capa 3: automatizacion total con MT5
Capa 4: escalado multi-prop firm

Detalle en: docs\roadmap-v2.md