# TradingLab

Sistema 100% automatico de generacion, validacion y despliegue de portfolios de estrategias de trading algoritmico para superar cuentas de fondeo (prop firms).

Sin sesgo humano en ninguna decision del pipeline. La unica intervencion humana es el forward test en demo antes del challenge real.

---

## Filosofia — Builder Libre

Los Builds 1-8 fallaron porque el humano restringia el espacio de busqueda.
A partir del Build 9, el sistema opera con 4 principios inquebrantables:

| # | Principio |
|---|-----------|
| 1 | SQ decide la logica de entrada — paleta completa +100 indicadores, sin hipotesis humana |
| 2 | Los numeros deciden que avanza — criterios automaticos en cada puerta del pipeline |
| 3 | El portfolio se construye por correlacion — no por preferencia ni intuicion |
| 4 | La unica intervencion humana es el forward test demo — en ningun otro momento el humano decide |

**El sesgo humano fue el problema. No la herramienta. No el mercado. No la configuracion.**

---

## Arquitectura del Sistema

### Pipeline completo (8 puertas)

```
DATOS HISTORICOS (Dukascopy M1, 2003-2020)
         |
         v
+─────────────────────────────────────────────────────────────+
│  PUERTA 0 — SQ Builder libre (24-48h)  ← HUMANO LANZA/PARA  │
│  Paleta completa: 100+ indicadores                           │
│  PF min > 1.3 | Trades/mes > 6 | Monte Carlo activado        │
│  Genera: 500-1000+ candidatas en databank                    │
+─────────────────────────────────────────────────────────────+
         | ~1000 candidatas
         v
+─────────────────────────────────────────────────────────────+
│  PUERTA 1 — Evaluation Gate (AUTO)                           │
│  evaluator-assistant.py                                      │
│  PF >= 1.5 | DD <= 7% | Trades >= 120 | WR >= 38%           │
│  Tasa de aprobacion: ~15%                                    │
+─────────────────────────────────────────────────────────────+
         | ~150 pasan
         v
+─────────────────────────────────────────────────────────────+
│  PUERTA 2 — Retester OOS  ← HUMANO LANZA SQ                 │
│  SQ Retester, datos 2021-actual                              │
│  PF OOS >= 1.3 | Caida PF <= 20% | DD OOS <= 6.5%           │
│  Tasa de aprobacion: ~40%                                    │
+─────────────────────────────────────────────────────────────+
         | ~60 pasan
         v
+─────────────────────────────────────────────────────────────+
│  PUERTA 3 — SPP / Parametros                                 │
│  SQ Optimizer — variacion parametros +-10%                   │
│  Logica estable bajo variacion                               │
│  Tasa de aprobacion: ~50%                                    │
+─────────────────────────────────────────────────────────────+
         | ~30 pasan
         v
+─────────────────────────────────────────────────────────────+
│  PUERTA 4 — WFO Matrix  ← HUMANO LANZA SQ                   │
│  SQ Optimizer Walk-Forward                                   │
│  WFE >= 50% | 0 ventanas PF < 0.9 | DD OOS <= 7%            │
│  Tasa de aprobacion: ~50%                                    │
+─────────────────────────────────────────────────────────────+
         | ~15 pasan
         v
+─────────────────────────────────────────────────────────────+
│  PUERTA 5 — Stress Test                                      │
│  SQ Retester — 5 periodos criticos                           │
│  2008, 2015, 2020, 2022, 2023 | DD < 8% | PF > 1.0 en 3/5  │
│  Tasa de aprobacion: ~60%                                    │
+─────────────────────────────────────────────────────────────+
         | ~9 pasan
         v
+─────────────────────────────────────────────────────────────+
│  PUERTA 6 — Multimarket Test                                 │
│  SQ Retester — activos correlacionados                       │
│  PF > 1.0 en al menos 1 activo diferente                     │
│  Tasa de aprobacion: ~70%                                    │
+─────────────────────────────────────────────────────────────+
         | ~6 pasan
         v
+─────────────────────────────────────────────────────────────+
│  PUERTA 7 — Portfolio Selection (AUTO)                       │
│  portfolio-builder.py                                        │
│  Correlacion < 0.5 | DD combinado < 12% | HRP pesos         │
│  Objetivo: 3-5 estrategias no correlacionadas                │
+─────────────────────────────────────────────────────────────+
         | 3-5 incluidas
         v
+─────────────────────────────────────────────────────────────+
│  PUERTA 8 — Forward Test Demo  ← UNICA INTERVENCION HUMANA  │
│  MT5 demo — 2 semanas minimo                                 │
│  PF demo >= 70% PF OOS | DD demo < DD OOS max               │
+─────────────────────────────────────────────────────────────+
         | aprobadas
         v
+─────────────────────────────────────────────────────────────+
│  PRODUCCION                                                  │
│  EA compilado en MT5 | Challenge prop firm | Cuenta funded   │
│  performance-monitor.py — monitoreo continuo                 │
+─────────────────────────────────────────────────────────────+
```

**Ratio global estimado:** ~0.5% de candidatas iniciales llegan a produccion.

### Dispositivos

| Dispositivo | Rol |
|-------------|-----|
| **ivano** (PC principal) | Claude Code, Git, Python, documentacion |
| **alber** (PC dedicado) | StrategyQuant X — Builder, Retester, WFO |
| **VPS MT5** (pendiente) | MetaTrader 5 — EAs en produccion |

### Agentes activos (11)

| Agente | Funcion |
|--------|---------|
| `market-selector` | Prioriza activos por scoring numerico (30+ activos) |
| `market-analyst` | Configura Builder libre — sin hipotesis humana |
| `propfirm-analyst` | Compara prop firms por activo y estrategia |
| `funding-specialist` | Evalua compatibilidad con reglas FTMO/E8/TFT |
| `sq-specialist` | Configura Builder, Retester y Optimizer en SQ |
| `evaluator-assistant` | Genera informes del Evaluation Gate |
| `correlation-analyst` | Construye y gestiona el portfolio automaticamente |
| `export-specialist` | Exporta estrategias aprobadas a MQL5/MT5 |
| `performance-monitor` | Monitorea EAs en produccion y alerta sobre riesgo |
| `data-manager` | Verifica y gestiona datos historicos en SQ |
| `orchestrator` | Coordina el pipeline — aplica criterios numericos |

---

## Requisitos

### Software

| Componente | Version | Uso |
|------------|---------|-----|
| Python | 3.11+ | Scripts del pipeline |
| StrategyQuant X | Build 143+ | Builder, Retester, Optimizer, WFO |
| MetaTrader 5 | Cualquiera | Forward test demo y produccion |
| Git | Cualquiera | Control de versiones |

### Dependencias Python

```bash
pip install pandas numpy scipy chromadb requests python-telegram-bot
```

### Variables de entorno

```bash
TELEGRAM_BOT_TOKEN=<token del bot @tradinglab_monitor_bot>
TELEGRAM_CHAT_ID=<chat ID>
ANTHROPIC_API_KEY=<clave API Claude>   # Capa 2+
```

---

## Instalacion

```bash
git clone https://github.com/ivanortegagarcia39-create/trading-lab.git
cd trading-lab
pip install -r requirements.txt
```

---

## Como lanzar un build

### 1. Pre-build checklist

```bash
python scripts/build-launcher.py --build 11 --activo XAUUSD --spread-real 60
```

Verifica comisiones, datos disponibles, configuracion del Builder y genera el checklist interactivo.

### 2. Lanzar Builder en SQ (en alber)

- Abrir StrategyQuant X → proyecto Builder
- Verificar: paleta completa activada, Monte Carlo ON, `Start again when finished` ON
- Pulsar Start — dejar correr 24-48 horas
- Parar cuando el PF maximo no suba en 6+ horas consecutivas

### 3. Exportar resultados y ejecutar Evaluation Gate

```bash
# Tras exportar CSVs desde SQ Databank:
python scripts/build-finisher.py --build 11 --activo XAUUSD --results-folder results/
```

### 4. Health check del sistema

```bash
python scripts/system-health-check.py
```

### 5. Informe semanal

```bash
python scripts/auto-reporter.py --no-ollama
```

### 6. Estado de la cola de builds

```bash
python scripts/build-queue-manager.py list
```

---

## Estructura de carpetas

```
trading-lab/
├── CLAUDE.md                          ← constitucion del proyecto
├── dashboard.md                       ← panel de estado Obsidian
├── agents/                            ← definicion de los 11 agentes
├── config/
│   ├── build-defaults.json            ← spreads y comisiones por defecto
│   └── pipeline-config.json           ← umbrales numericos del pipeline
├── docs/
│   ├── architecture/                  ← diagramas y vision general
│   ├── roadmap/                       ← planning maestro (222 tareas)
│   ├── skills/                        ← 70+ skills del pipeline
│   ├── project-status.md              ← estado del proyecto
│   └── lessons-learned.md             ← aprendizajes acumulados
├── include/
│   └── ConnectionMonitor.mqh          ← libreria MQL5 para VPS
├── results/                           ← outputs del pipeline por build
├── scripts/                           ← 70+ scripts Python
│   ├── build-launcher.py              ← lanzar build con checklist
│   ├── build-finisher.py              ← cerrar build y procesar resultados
│   ├── evaluator-assistant.py         ← Evaluation Gate automatico
│   ├── portfolio-builder.py           ← seleccion automatica del portfolio
│   ├── system-health-check.py         ← verificacion del sistema
│   ├── auto-reporter.py               ← informe semanal automatico
│   ├── telegram-notifier.py           ← alertas via Telegram
│   ├── knowledge-base.py              ← ChromaDB — 909+ chunks indexados
│   └── ...                            ← 60+ scripts adicionales
├── templates/                         ← plantillas Obsidian
└── .github/workflows/
    ├── validate-skills.yml            ← verifica formato de docs en cada push
    └── pipeline-check.yml             ← alerta si criterios numericos se relajan
```

---

## Workflows N8N (Capa 2 — pendiente)

N8N esta planificado para Capa 2, cuando el sistema tenga 5+ estrategias aprobadas.
Automatizara ciclos completos sin intervencion humana:

| Workflow | Funcion |
|----------|---------|
| `market-cycle` | Detecta necesidad de nuevas estrategias → lanza Builder via SQ Remote Control |
| `eval-gate` | Llama a Claude API → orchestrator tras cada build |
| `portfolio-rebalance` | Rebalanceo mensual automatico con correlation-analyst |
| `challenge-monitor` | Monitorea P&L en tiempo real — alerta si se acerca DD limit |
| `weekly-report` | Genera y envia informe semanal via Telegram |

Tecnologia: N8N + Claude API + SQ Remote Control API + Telegram

---

## Prop firms objetivo

| Prop Firm | Tipo | Activos | Daily Loss | Max DD | Estado |
|-----------|------|---------|-----------|--------|--------|
| **FTMO 2-Step** | Evaluacion | Forex + Metales + Indices | 5% dinamico | 10% dinamico | **PRINCIPAL** |
| E8 Funding | Evaluacion | Forex + Metales | 5% estatico | 8% estatico | Alternativa |
| TFT | Evaluacion | Forex + Metales + Indices | 4% | 6% dinamico | Alternativa |
| Apex Trader | Futuros CME | Futuros | Variable | Variable | Pendiente datos |
| MFF | Futuros CME | Futuros | Variable | Variable | Pendiente datos |

El `propfirm-analyst` decide automaticamente que prop firm es optima para cada estrategia. Sin preferencia humana.

### FTMO — Reglas criticas

- **Daily Loss:** 5% dinamico — recalcula a medianoche hora Praga
- **Max DD:** 10% dinamico — solo sube, nunca baja
- **Objetivo:** Fase 1 +10% → Fase 2 +5% → Cuenta funded
- **Margen operativo:** daily loss real 3% | max DD real 7% (cuenta 25.000 USD)

---

## Universo de mercados (30+ activos)

Priorizados automaticamente por scoring numerico. El `market-selector` decide el orden — no el humano.

| Grupo | Activos | Datos desde |
|-------|---------|-------------|
| Forex Majors | EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, NZD/USD, USD/CAD | 2003 |
| Forex Crosses | EUR/GBP, EUR/JPY, GBP/JPY, EUR/AUD, EUR/CHF, AUD/JPY, GBP/AUD, CAD/JPY, NZD/JPY | 2003 |
| Metales | XAU/USD, XAG/USD | 2003 |
| Indices | US30, US500, NAS100, DE40, UK100, JP225 | Variable |
| Cripto | BTC/USD, ETH/USD | 2017 |

Temporalidad unica: **H1** — M15 descartado formalmente (comisiones reales FTMO eliminan el edge).

---

## Estado actual

- **Fase:** Capa 0 activa — sistema v8.1 completo
- **Build activo:** Build 11 PENDIENTE en alber (XAUUSD H1, spread 60 pips)
- **Planning maestro:** ~202/222 tareas completadas
- **Scripts Python operativos:** 70+
- **ChromaDB:** 909 chunks indexados
- **Telegram:** @tradinglab_monitor_bot activo
- **Portfolio actual:** 0 estrategias — objetivo minimo 3

---

## Documentacion

| Archivo | Contenido |
|---------|-----------|
| `CLAUDE.md` | Constitucion del proyecto — reglas inquebrantables |
| `docs/architecture/system-overview.md` | Vision general y dispositivos |
| `docs/architecture/pipeline-diagram.md` | Diagrama completo del pipeline |
| `docs/skills/skill-builder-libre.md` | Configuracion del Builder sin hipotesis |
| `docs/skills/skill-evaluation-auto.md` | Criterios numericos exactos de cada puerta |
| `docs/skills/skill-portfolio-selection.md` | Seleccion automatica del portfolio |
| `docs/roadmap/planning-maestro-status.md` | Estado de las 222 tareas |
| `docs/project-status.md` | Estado detallado del proyecto |
| `docs/lessons-learned.md` | Aprendizajes de los 11 builds |
