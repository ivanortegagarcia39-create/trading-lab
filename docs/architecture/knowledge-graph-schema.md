# Arquitectura: Knowledge Graph Schema

## Propósito

El Knowledge Graph conecta toda la memoria institucional del sistema.
No son documentos sueltos sino nodos conectados que permiten queries como:

> "¿Qué builds anteriores con XAUUSD H1 en régimen tendencia-altavol
> produjeron estrategias rentables y qué tenían en común?"

Esto es imposible con documentos en texto plano o con búsqueda semántica.
Requiere recorrer relaciones causales: Build → Strategy → GateDecision → Lesson → Criterion.

---

## Esquema visual

```
Build --[PRODUCED]--> Strategy --[VALIDATED_BY]--> GateDecision
                          |                              |
                    [TRADED_IN]                    [TRIGGERED]
                          |                              |
                    MarketRegime                      Lesson
                                                        |
                                             [CAUSED_ADJUSTMENT]
                                                        |
                    LiveOutcome --[UPDATED]-------> Criterion
                          ^
                          |
              Strategy --[HAD_OUTCOME]
```

---

## Tipos de nodos

### Build
Representa un ciclo de búsqueda en StrategyQuant.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| build_id | STRING (PK) | Ej: "B10", "B11" |
| activo | STRING | Ej: "XAUUSD" |
| timeframe | STRING | Siempre "H1" |
| fecha | STRING | Fecha de inicio del build |
| spread | DOUBLE | Spread usado en pips |
| estado | STRING | ACTIVO / COMPLETADO / FALLIDO |

### Strategy
Estrategia generada por el Builder libre.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| strategy_id | STRING (PK) | Ej: "XAUUSD_B11_S001" |
| build_id | STRING | Build que la generó |
| pf | DOUBLE | Profit Factor IS |
| dd | DOUBLE | Max Drawdown % |
| trades | INT64 | Número de trades IS |
| win_rate | DOUBLE | Win rate % |
| sharpe | DOUBLE | Sharpe ratio |
| estado | STRING | APROBADA / DESCARTADA / EN_PRODUCCION |

### MarketRegime
Régimen de mercado en el que operó la estrategia.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| nombre | STRING (PK) | Ej: "tendencia-altavol" |
| adx_min | DOUBLE | ADX mínimo del régimen |
| adx_max | DOUBLE | ADX máximo |
| atr_ratio | DOUBLE | ATR relativo al promedio |
| descripcion | STRING | Descripción textual |

### GateDecision
Decisión de una puerta del pipeline sobre una estrategia.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| decision_id | STRING (PK) | Ej: "XAUUSD_B11_S001-G1-2026-04-28" |
| strategy_id | STRING | Estrategia evaluada |
| gate_num | INT64 | 1=EvalGate, 2=Retester, 3=Paso12b, 4=WFO, 5=Portfolio |
| gate_name | STRING | Nombre legible de la puerta |
| resultado | STRING | PASA / DESCARTAR / ESPERA |
| criterio | STRING | Criterio exacto que activó la decisión |
| fecha | STRING | Fecha de la decisión |

### Lesson
Lección aprendida del sistema.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| lesson_id | STRING (PK) | Ej: "LECCION-001" |
| titulo | STRING | Título de la lección |
| estado | STRING | TENTATIVA / ESTRUCTURAL / PERMANENTE |
| ocurrencias | INT64 | Veces confirmada en contextos diferentes |
| fecha | STRING | Fecha de primera detección |

### LiveOutcome
Resultado real de una estrategia en producción.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| outcome_id | STRING (PK) | Ej: "XAUUSD_B11_S001-OUT-2026-05-15" |
| strategy_id | STRING | Estrategia evaluada |
| pf_produccion | DOUBLE | PF real en producción |
| dd_produccion | DOUBLE | DD máximo real |
| duracion_dias | INT64 | Días en producción |
| veredicto | STRING | PASS / FAIL / RETIRADA |

### Criterion
Umbral de decisión del pipeline con historial de cambios.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| criterion_id | STRING (PK) | Ej: "pf_oos_minimo" |
| nombre | STRING | Nombre legible |
| umbral_actual | DOUBLE | Valor vigente |
| umbral_inicial | DOUBLE | Valor original del sistema |
| ultima_actualizacion | STRING | Fecha del último ajuste |

---

## Tipos de aristas

| Arista | Desde | Hacia | Significado |
|--------|-------|-------|-------------|
| PRODUCED | Build | Strategy | Este build generó esta estrategia |
| VALIDATED_BY | Strategy | GateDecision | Esta estrategia fue evaluada por esta puerta |
| TRADED_IN | Strategy | MarketRegime | Esta estrategia operó en este régimen |
| TRIGGERED | GateDecision | Lesson | Esta decisión de puerta generó esta lección |
| CAUSED_ADJUSTMENT | Lesson | Criterion | Esta lección causó el ajuste de este criterio |
| HAD_OUTCOME | Strategy | LiveOutcome | Esta estrategia tuvo este resultado en producción |
| UPDATED | LiveOutcome | Criterion | Este outcome llevó a actualizar este criterio |

---

## Tipos de queries soportadas

### 1. Linaje de estrategia
¿Qué build la generó? ¿Qué gates superó? ¿En qué régimen operó? ¿Qué resultó?

```bash
python scripts/knowledge-graph.py --mode query \
    --query lineage --strategy-id XAUUSD_B11_S001
```

### 2. Similitud de builds
¿Qué builds anteriores con este activo produjeron estrategias rentables?

```bash
python scripts/knowledge-graph.py --mode query \
    --query similar_builds --activo XAUUSD
```

### 3. Lecciones por puerta
¿Qué lecciones surgieron de la puerta WFO (gate 4)?

```bash
python scripts/knowledge-graph.py --mode query \
    --query lessons_for_gate --gate 4
```

### 4. Estadísticas del grafo

```bash
python scripts/knowledge-graph.py --mode stats
```

---

## Diferencia con ChromaDB

| | Kùzu (KG) | ChromaDB |
|--|-----------|----------|
| Tipo | Grafo relacional | Vector store |
| Queries | Estructurales sobre relaciones causales | Similitud semántica de texto |
| Pregunta que responde | "¿Qué causó qué?" | "¿Qué documentos son similares a esto?" |
| Ejemplo | "¿Qué lecciones surgieron de fallos en WFO?" | "¿Qué documentos hablan de drawdown?" |
| Persistencia | `.kuzu/` (embebido) | `chroma_db/` (embebido) |

**Usar juntos:** Kùzu para "qué pasó y por qué", ChromaDB para "qué documentos son relevantes para esto".
El orchestrator consulta ambos antes de tomar decisiones.

---

## Inicialización y mantenimiento

### Primer uso
```bash
# Instalar Kùzu
pip install kuzu

# Inicializar grafo vacío
python scripts/knowledge-graph.py --mode init

# Importar historial existente
python scripts/kg-importer.py
```

### Integración automática en el pipeline
- `build-finisher.py` inserta automáticamente builds y estrategias aprobadas
- `lessons-analyzer.py` inserta automáticamente lecciones ESTRUCTURALES

### Persistencia
El grafo se persiste en `.kuzu/` en la raíz del repo.
Este directorio está en `.gitignore` — no se versiona.
Es un artefacto local, como `chroma_db/`.

---

## Referencias

- `scripts/knowledge-graph.py` — motor del KG (Kùzu)
- `scripts/kg-importer.py` — importación del historial
- `scripts/build-finisher.py` — integración automática post-build
- `scripts/lessons-analyzer.py` — integración automática de lecciones
- `docs/architecture/pipeline-diagram.md` — diagrama del pipeline completo
