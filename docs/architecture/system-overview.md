# TradingLab — Arquitectura General del Sistema

Ultima actualizacion: 2026-04-26

---

## Vision General

Sistema 100% automatico de generacion, validacion y despliegue
de portfolios de estrategias de trading algoritmico para
superar cuentas de fondeo (prop firms).

Sin sesgo humano en ninguna decision del pipeline.
La unica intervencion humana: forward test tecnico en demo
y la compra del challenge con autorizacion explicita.

---

## Flujo Completo del Pipeline

```
DATOS HISTORICOS (Dukascopy M1, 2003-2020)
         |
         v
+-------------------+
|  BUILDER LIBRE    |  24-48h en SQ, paleta completa +100 indicadores
|  (SQ en alber)   |  Sin hipotesis humana — SQ decide la logica
+-------------------+
         | ~1000 candidatas generadas
         v
+-------------------+
|   EVAL GATE       |  evaluator-assistant.py (automatico)
|   (Python)        |  Trades>=120, WR>=38%, DD<=7%, Sharpe>=0.5
+-------------------+
         | ~200 pasan (tasa esperada: 5-15%)
         v
+-------------------+
|   RETESTER OOS    |  SQ Retester, datos 2021-actual
|   (SQ manual)    |  Comisiones identicas al Builder
+-------------------+
         | todas retestadas en lote
         v
+-------------------+
|   PASO 12b AUTO   |  orchestrator (automatico)
|   (Python)        |  PF_OOS>=1.3, caida<=20%, DD_OOS<=6.5%
+-------------------+
         | ~40 pasan
         v
+-------------------+
|   SPP VALIDATION  |  SQ Optimizer — permutacion de parametros
|   (SQ manual)    |  Descarte si PF cae >30% en alguna permutacion
+-------------------+
         | ~20 pasan
         v
+-------------------+
|   STRESS TEST     |  SQ Retester con 5 periodos criticos
|   (SQ manual)    |  2008, 2015, 2020, 2022, 2023 — DD<8% en cada uno
+-------------------+
         | ~15 pasan
         v
+-------------------+
|   WFO             |  SQ Walk-Forward, ventanas deslizantes
|   (SQ manual)    |  WFE>=50% aprobacion, <40% descarte
+-------------------+
         | ~10 pasan
         v
+-------------------+
|   INFLATION DIAG  |  inflation-diagnostic.py (automatico)
|   + GT-SCORE      |  Sobreajuste IS/OOS, score 0-100
+-------------------+
         | ~7 pasan
         v
+-------------------+
|   PORTFOLIO AUTO  |  portfolio-builder.py (automatico)
|   (Python)        |  Correlacion<0.5, DD_combinado<12%, HRP pesos
+-------------------+
         | 3-5 estrategias seleccionadas
         v
+-------------------+
|   EXPORT MT5      |  export-specialist
|   (manual)        |  mql5-auditor.py + Market Impact Sim + deploy demo
+-------------------+
         v
+-------------------+
|   FORWARD TEST    |  20 trades minimo en demo
|   (humano tecnico)| PF_demo>=70% PF_OOS, DD_demo<=DD_OOS+30%
+-------------------+
         v
+-------------------+
| CHALLENGE COMPRA  |  UNICA decision humana economica
|   (humano SI/NO)  |  Notificacion Telegram → humano autoriza
+-------------------+
         v
+-------------------+
|   CHALLENGE EA    |  EA en VPS, Fase 1 (+10%) → Fase 2 (+5%)
|   (automatico)    |  performance-monitor + risk manager adaptativo
+-------------------+
         v
+-------------------+
|   FUNDED ACCOUNT  |  Scaling cada 4 meses (+25%)
|   (automatico)    |  scaling-manager + account-recovery-manager
+-------------------+
```

**Ratio global:** ~0.5% de candidatas iniciales llegan a produccion.

---

## Dispositivos del Sistema

| Dispositivo | Rol | Estado |
|-------------|-----|--------|
| **ivano** (PC principal) | Claude Code, Git, Python, documentacion | Activo |
| **alber** (PC dedicado) | StrategyQuant X — Builder y Retester | Activo (builds en curso) |
| **VPS MT5** (pendiente) | MetaTrader 5 — EAs en produccion | Pendiente contratacion |

### ivano
- Claude Code para documentacion, scripts Python y coordinacion
- Git push al repositorio central
- Ejecucion de scripts de analisis (evaluator-assistant, portfolio-builder, etc.)
- Obsidian vault sobre el mismo repo

### alber
- StrategyQuant X Build 143 corriendo 24/7
- Builder libre en modo continuo
- Retester y WFO en lote
- Sin internet durante builds (solo datos locales)
- Repositorio local sincronizado manualmente con ivano

### VPS MT5 (futuro — Fase 5)
- MetaTrader 5 con EAs compilados
- vps-health-monitor.py + ConnectionMonitor.mqh activos
- ftmo-timezone-sync.mq5 para calculo correcto del DD FTMO
- Sin intervencion humana continua

---

## Repositorio

GitHub: `ivanortegagarcia39-create/trading-lab`
Rama principal: `main`
CI/CD: GitHub Actions (validate-skills.yml, pipeline-check.yml)

Estructura de carpetas:
```
trading-lab/
├── CLAUDE.md                  ← constitucion del proyecto
├── dashboard.md               ← panel de estado Obsidian
├── agents/                    ← definicion de los 11 agentes
├── config/
│   └── build-defaults.json    ← configuracion base de builds
├── docs/
│   ├── architecture/          ← este archivo
│   ├── roadmap/               ← planning maestro
│   ├── skills/                ← skills del pipeline
│   ├── project-status.md
│   └── lessons-learned.md
├── include/
│   └── ConnectionMonitor.mqh  ← libreria MQL5
├── results/                   ← outputs del pipeline
├── scripts/                   ← scripts Python y MQL5
├── templates/                 ← plantillas Obsidian
└── .github/workflows/         ← CI/CD
```

---

## Archivos Clave

| Archivo | Proposito |
|---------|-----------|
| `CLAUDE.md` | Constitucion — reglas inquebrantables del proyecto |
| `agents/orchestrator.md` | Agente coordinador — coordina el pipeline completo |
| `docs/skills/skill-evaluation-auto.md` | Criterios numericos exactos de cada puerta |
| `docs/skills/skill-builder-libre.md` | Configuracion del Builder sin hipotesis humana |
| `docs/roadmap/planning-maestro-status.md` | Estado de las 186 tareas del planning |
| `config/build-defaults.json` | Spreads, comisiones y parametros por defecto |
| `scripts/evaluator-assistant.py` | EvalGate automatico post-build |
| `scripts/portfolio-builder.py` | Seleccion automatica del portfolio |
| `scripts/pre-build-checklist.py` | Verificacion antes de lanzar cada build |
| `scripts/build-analyzer.py` | Analisis ejecutivo con Ollama post-build |
| `dashboard.md` | Panel visual del proyecto en Obsidian |

---

## Capas del Roadmap

| Capa | Descripcion | Estado |
|------|-------------|--------|
| Capa 0 | Pipeline automatico multi-activo | ACTIVO |
| Capa 1 | Expansion completa de mercados | Pendiente |
| Capa 2 | N8N + Claude API — ciclos autonomos | Pendiente |
| Capa 3 | MT5 operando solo multi-prop firm | Pendiente |
| Capa 4 | Escalado y rebalanceo automatico | Pendiente |
