# Advanced Features v3 — Roadmap Fichas Capa 2 y Capa 3

Status: FICHAS DEFINIDAS — implementacion pendiente segun hitos
Ultima actualizacion: 2026-04-21

---

## CUANDO IMPLEMENTAR CADA FICHA

| Ficha | Capa | Hito de activacion |
|-------|------|--------------------|
| GT-Score | 3 | 3+ estrategias en produccion durante 3+ meses |
| Market Impact Simulator | 2 | Antes del primer challenge real |
| MQL5 Auditor Avanzado | 2 | Capa 2 activa (N8N + Claude API) |
| Audit Trail externo | 3 | Primera cuenta fondeada activa |

---

## FICHA 1 — GT-Score (Capa 3)

### Objetivo
Metrica unica que reemplaza al Profit Factor como criterio
principal de evaluacion en Capa 3. El PF tiene limitaciones
conocidas: es sensible a pocos trades con PnL extremo y no
captura la estabilidad temporal ni la robustez real.
El GT-Score agrega las 4 dimensiones de calidad que importan.

### Arquitectura de la metrica

GT-Score = suma ponderada de 4 componentes (total: 100 puntos)

| Componente | Peso | Como se calcula |
|------------|------|-----------------|
| Consistencia temporal | 25% | PF estable por años en IS: desviacion estandar del PF anual / PF medio. Score = 25 * (1 - min(std_pf/mean_pf, 1)) |
| Robustez parametrica | 25% | SPP ±10% sin caida > 20%: % de permutaciones que no caen > 20%. Score = 25 * pct_pass |
| Robustez multiactivo | 25% | PF > 1.0 en activos correlacionados. Score = 25 si PF > 1.0 en 2/2 correlados, 12 si 1/2, 0 si 0/2 |
| Calidad de ejecucion | 25% | Ratio slippage real vs backtest en forward test. Score = 25 * min(slippage_backtest/slippage_real, 1) |

### Umbral de aprobacion
GT-Score >= 65/100

### Comparativa con criterios actuales (Capa 1)
En Capa 3 el GT-Score NO reemplaza los criterios existentes — los COMPLEMENTA.
Una estrategia debe pasar el WFO Y tener GT-Score >= 65.
Si GT-Score < 65 pero WFO aprueba → zona de revision manual.

### Archivo a crear cuando se implemente
docs/skills/skill-gt-score-calc.md
Contenido: formulas exactas, ejemplos de calculo, criterios edge case

### Dependencias tecnicas
- Datos de slippage real del forward test (performance-monitor.md)
- Resultados SPP del pipeline (skill-spp-validation.md)
- Resultados multimarket (skill-multimarket-validation.md)
- Al menos 6 meses de datos de produccion real

---

## FICHA 2 — Market Impact Simulator (Capa 2)

### Objetivo
Validar que la estrategia es escalable al tamaño de lotes
real de una cuenta fondeada. Una estrategia que funciona
con 0.01 lotes puede degradarse con 1.0 lote si mueve
el mercado o si el broker no puede ejecutar al precio.

### Metodo de simulacion
Para cada trade del backtest, calcular el impacto de mercado
estimado segun el tamaño del lote:

```
slippage_adicional = lote_real * factor_impacto_por_activo
precio_entrada_real = precio_backtest + slippage_adicional * direccion
```

Factores de impacto estimados por activo:
| Activo | Factor (pips/lote) |
|--------|-------------------|
| XAUUSD | 0.5 pips/lote |
| EURUSD | 0.2 pips/lote |
| GBPUSD | 0.3 pips/lote |
| Indices | 1.0 pts/lote |

### Criterio
Si el PF recalculado con el impacto de mercado simulado
cae mas del 15% respecto al PF original → DESCARTAR.

PF_impacto_simulado / PF_backtest >= 0.85

### Cuando se ejecuta
Despues del forward test, antes de la autorizacion del challenge.
Usa el tamaño de cuenta real del challenge (25k, 50k, 100k)
para calcular los lotes reales que operara el EA.

### Archivo a crear cuando se implemente
docs/skills/skill-reactive-sim.md
Contenido: calculos de impacto por activo, calibracion del factor,
relacion con el slippage observado en forward test

---

## FICHA 3 — MQL5 Auditor Avanzado con QuantCode-Bench (Capa 2)

### Objetivo
Extension del scripts/mql5-auditor.py de la Fase 1.
Añadir benchmarks de calidad de codigo de trading
para comparar el EA exportado contra mejores practicas
de la industria.

### Auditorias adicionales en Capa 2
- Benchmark de latencia de ejecucion: medir tiempo entre
  señal de entrada y OrderSend en el backtest
- Deteccion de look-ahead bias en indicadores custom
  (si los hay — los exportados por SQ no deberian tenerlo)
- Verificacion de manejo de errores TRADE_RETCODE_*
- Verificacion de cierre correcto de posiciones
  al final de la sesion de trading
- Test de idempotencia: si el EA recibe la misma señal
  dos veces en la misma barra, ¿abre una o dos posiciones?

### Integracion con Ollama en Capa 2
En Capa 2 se tiene acceso a modelos mas grandes via Ollama.
Usar: deepseek-coder-33b o equivalente disponible en 2026
El mql5-auditor.py actual soporta cualquier modelo Ollama
via el parametro --ollama-url.

### Archivo base ya implementado
scripts/mql5-auditor.py — Fase 1
Extender en Capa 2 sin romper la interfaz actual.

---

## FICHA 4 — Audit Trail con Hash Blockchain + Verificacion Externa

### Estado actual (Fase 1)
scripts/hash-logger.py implementa un blockchain simple
con SHA-256 encadenado en results/audit-trail.log.
La cadena es verificable localmente con `verify_chain()`.

### Objetivo en Capa 3
Exportar el audit trail en formato compatible con
verificacion externa — para demostrar a prop firms
o inversores que todas las decisiones del pipeline
fueron automaticas y no manipuladas.

### Formato objetivo (Capa 3)
Cada bloque del audit trail exportable a:
- JSON-LD con schema.org/AuditEvent
- CSV con firma digital incluida
- API publica de solo-lectura (webhook opcional)

### Dependencias
- Primer challenge real aprobado (prueba de concepto)
- Decisión sobre nivel de transparencia publica
- scripts/hash-logger.py estable durante 3+ meses

### Archivo a crear cuando se implemente
docs/architecture/audit-trail-public.md

---

## SIGUIENTE FICHA A IMPLEMENTAR

Segun el estado actual del proyecto (Fase 1, Build 10 en curso):
La proxima ficha a implementar es la FICHA 2 (Market Impact Simulator)
porque es necesaria antes del primer challenge real.

Criterio de activacion: cuando el orchestrator genere la primera
notificacion de autorizacion de challenge (CASO 1).
Implementar la Ficha 2 en ese momento — no antes.

Razon: implementar herramientas antes de necesitarlas
es inversion especulativa. Implementar cuando el hito
de activacion se alcanza es la filosofia del proyecto.
