# Skill: Custom Projects de SQ X — Pipeline Automatico

## Proposito
Configurar un Custom Project en StrategyQuant X para
ejecutar el pipeline completo de un ciclo de build sin
necesidad de pulsar botones manualmente entre fases.
Un solo Start — SQ encadena todas las tareas.

---

## QUE SON LOS CUSTOM PROJECTS

Un Custom Project es un flujo de trabajo encadenado
dentro de SQ X que ejecuta tareas en secuencia:
Builder → filtro → Retester → WFO → exportacion.

Sin Custom Project:
- El humano lanza el Builder
- El humano espera y lanza el Retester
- El humano espera y lanza el Optimizer
- El humano mueve archivos entre fases

Con Custom Project:
- El humano pulsa Start una sola vez
- SQ ejecuta todo el flujo automaticamente
- Si no hay suficientes aprobadas → SQ vuelve al Builder
- El humano recibe el resultado final

Esto elimina la unica fuente de intervencion humana
involuntaria en las fases intermedias del pipeline.

---

## FLUJO COMPLETO DEL CUSTOM PROJECT

```
[START]
    |
    v
TAREA 1: Builder Libre (24-48h continuo)
    Configuracion segun skill-builder-libre.md
    Stop condition: PF maximo sin mejora 6h
    Output: databank con candidatas PF > 1.3
    |
    v
TAREA 2: EvalGate Filter (automatico Python)
    Script: scripts/eval-gate-filter.py
    Filtros: Total Trades >= 120, Win Rate >= 38%, MaxDD <= 7%
    Output: candidatas que pasan al Retester
    |
    v
TAREA 3: Retester (batch automatico)
    Modo: All strategies in databank
    Periodo IS: 2003.05.05 a 2020.12.31
    Monte Carlo: ACTIVADO (aqui, no en el Builder)
    Output: estrategias con metricas IS robustas
    |
    v
TAREA 4: Paso 12b OOS (automatico)
    Script: scripts/paso-12b.py
    Filtros: PF OOS >= 1.2, caida PF <= 25%, DD OOS <= 7%
    Output: candidatas para WFO
    |
    v
TAREA 5: WFO Matrix (automatico)
    Tipo: Walk Forward Matrix
    Ventanas: 12 IS + 3 OOS
    Anchoring: Off (ventanas flotantes)
    Output: estrategias con WFE y metricas WFO
    |
    v
TAREA 6: Portfolio Filter (automatico Python)
    Script: scripts/portfolio-filter.py
    Filtros: WFE >= 50%, criterios skill-evaluation-auto.md
    Correlacion: correlation-analyst automatico
    Output: estrategias para el portfolio
    |
    v
DECISION: estrategias aprobadas >= 3?
    |
    SI → [END] — pipeline completado
    NO → Go To Task: TAREA 1 (nuevo ciclo Builder)
```

---

## CONFIGURACION DE CADA TAREA EN SQ X

### TAREA 1: Builder Libre

Tipo de tarea: Builder
Configuracion: segun skill-builder-libre.md completo
Condicion de parada:
  - Start again when finished: ON
  - Stop: cuando PF maximo no mejora en 6 horas
  - O cuando el humano para manualmente
Transition: automatica a TAREA 2 al parar

### TAREA 2: EvalGate Filter

Tipo de tarea: Custom Analysis
Script externo: python scripts/eval-gate-filter.py
  --input databank/
  --output results/eval-gate/
  --min-trades 120
  --min-winrate 38
  --max-dd 7
Transition: automatica a TAREA 3 si hay candidatas
Si 0 candidatas → Go To Task TAREA 1

### TAREA 3: Retester

Tipo de tarea: Retester
Mode: All strategies from previous task
Periodo: 2003.05.05 a 2020.12.31
Configuracion:
  Monte Carlo: ACTIVADO
  Mayor precision: ACTIVADO
  Delay aleatorio: 1 bar
Transition: automatica a TAREA 4

### TAREA 4: Paso 12b OOS

Tipo de tarea: Custom Analysis
Script externo: python scripts/paso-12b.py
  --retester-output results/retester/
  --output results/paso12b/
  --oos-start 2021-01-01
  --min-pf-oos 1.2
  --max-caida-pf 25
  --max-dd-oos 7
Transition: automatica a TAREA 5 si hay candidatas
Si 0 candidatas → Go To Task TAREA 1

### TAREA 5: WFO Matrix

Tipo de tarea: Optimizer
Tipo de optimizacion: Walk Forward Matrix
Configuracion IS: 12 periodos
Configuracion OOS: 3 periodos
Anchoring: OFF
Transition: automatica a TAREA 6

### TAREA 6: Portfolio Filter

Tipo de tarea: Custom Analysis
Script externo: python scripts/portfolio-filter.py
  --wfo-output results/wfo/
  --output results/approved/
  --min-wfe 50
  --correlation-max 0.5
  --max-dd-portfolio 12
Transition:
  Si aprobadas >= 3 → END (pipeline completado)
  Si aprobadas < 3 → Go To Task TAREA 1

---

## LOOP AUTOMATICO

La condicion de retorno al Builder es critica:

```
Si estrategias_aprobadas_acumuladas < 3:
    Go To Task: TAREA 1
    Razon: el portfolio minimo requiere 3 estrategias
           no correlacionadas aprobadas por WFO
```

El contador de aprobadas es acumulativo entre ciclos.
Si el ciclo anterior aprobo 2 y este aprueba 1 → total 3 → END.
Si el ciclo anterior aprobo 0 y este aprueba 0 → ciclo 3 → etc.

Limite de ciclos para evitar bucle infinito: 5 ciclos maximo.
Si tras 5 ciclos hay < 3 aprobadas → ALERTA al humano:
"5 ciclos completados sin portfolio minimo.
 Posible problema con los datos o los umbrales.
 Revision manual requerida."

---

## CUSTOM ANALYSIS PYTHON — INTEGRACION

SQ X permite ejecutar scripts externos en puntos del flujo.
Los scripts del proyecto siguen esta convencion:

Inputs del script:
- Carpeta con CSVs exportados por SQ (separador ;)
- Parametros de umbral via argumentos CLI

Outputs del script:
- Lista de IDs de estrategias que pasan (una por linea)
- Codigo de salida: 0 = hay candidatas, 1 = ninguna paso
- Log en results/logs/[fecha]-[tarea].log

SQ lee el codigo de salida para decidir la transicion.
El script NO modifica los archivos de SQ directamente.

Scripts existentes en el proyecto:
- scripts/validate-sqx-build.py — validacion de reproducibilidad
- scripts/validate-sqx-folder.py — validacion de carpetas
- scripts/verify-symbol-specs.py — verificacion de specs

Scripts pendientes (Fase 1):
- scripts/eval-gate-filter.py
- scripts/paso-12b.py
- scripts/portfolio-filter.py

---

## PARAMETROS TECNICOS DE TRANSICION

| De tarea | A tarea | Condicion | Accion si falla |
|----------|---------|-----------|-----------------|
| Builder | EvalGate | databank > 0 estrategias | Error critico |
| EvalGate | Retester | candidatas > 0 | Go To Builder |
| Retester | Paso 12b | completado sin error | continuar siempre |
| Paso 12b | WFO | candidatas > 0 | Go To Builder |
| WFO | Portfolio | completado sin error | continuar siempre |
| Portfolio | END | aprobadas >= 3 | Go To Builder |

---

## LO QUE EL CUSTOM PROJECT NUNCA HACE

NUNCA modifica los criterios numericos automaticamente
NUNCA aprueba estrategias que no cumplan los umbrales
NUNCA consulta al humano entre tareas (excepto alerta ciclos)
NUNCA ejecuta mas de 5 ciclos sin notificar
NUNCA decide el activo ni los parametros del Builder
  (esos vienen de market-selector y market-analyst)
NUNCA reemplaza la verificacion de lock file del orchestrator

---

## REGLA FUNDAMENTAL

Un solo Start — SQ hace todo.
El humano no toca nada entre el Builder y los resultados finales.
Si el humano interviene en medio del flujo rompe la trazabilidad.
