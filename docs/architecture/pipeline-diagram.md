# Diagrama del Pipeline — TradingLab

Flujo completo desde el build hasta la produccion.
Actualizado: 2026-04-28

---

```
╔══════════════════════════════════════════════════════════════════════╗
║                    PIPELINE TRADINGLAB — CAPA 0                     ║
╚══════════════════════════════════════════════════════════════════════╝

  PREPARACION (automatica)
  ─────────────────────────
  data-manager.md         market-selector.md        market-analyst.md
  Verificar datos M1  →   Scoring numerico       →   Configurar Builder
  Dukascopy 2003+         (30+ activos)              sin hipotesis humana
                          El activo con mayor
                          score gana el ciclo
                          ↓
  ┌────────────────────────────────────────────────────────────────┐
  │  build-launcher.py — checklist interactivo antes de lanzar    │
  │  python scripts/build-launcher.py --build N --activo XAUUSD   │
  └────────────────────────────────────────────────────────────────┘
                          ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  PUERTA 0 — SQ Builder libre (24-48h)  ← HUMANO LANZA Y PARA   │
  │  Paleta completa: 100+ indicadores                              │
  │  PF mín > 1.3 | Trades/mes > 6 | MC activado                   │
  │  Genera: 500-1000+ candidatas en databank                       │
  └─────────────────────────────────────────────────────────────────┘
                          ↓
              ┌───────────────────────┐
              │  Exportar CSVs de SQ  │  ← HUMANO EXPORTA
              │  SQ → Databank → CSV  │
              └───────────────────────┘
                          ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  PUERTA 1 — Evaluation Gate (AUTO)                              │
  │  evaluator-assistant.py                                         │
  │  PF ≥ 1.5 | DD ≤ 7% | Trades ≥ 120 | WR ≥ 38%                 │
  │  Tasa de aprobacion: ~10-20%                                    │
  └─────────────────────────────────────────────────────────────────┘
                    ↓              ↓
               PASA (~30)    DESCARTAR → results/rejected/
                    ↓              + criterio documentado
  ┌─────────────────────────────────────────────────────────────────┐
  │  PUERTA 2 — Retester OOS / Paso 12b  ← HUMANO LANZA SQ         │
  │  SQ Retester                                                    │
  │  PF OOS ≥ 1.3 | Caida PF ≤ 20% | DD OOS ≤ 6.5%                │
  │  Tasa de aprobacion: ~40%                                       │
  └─────────────────────────────────────────────────────────────────┘
                    ↓              ↓
               PASA (~12)    DESCARTAR
                    ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  PUERTA 3 — SPP                                                 │
  │  SQ Optimizer — parametros ±10%                                 │
  │  Logica estable con variacion de parametros                     │
  │  Tasa de aprobacion: ~50%                                       │
  └─────────────────────────────────────────────────────────────────┘
                    ↓              ↓
               PASA (~6)     DESCARTAR
                    ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  PUERTA 4 — WFO Matrix  ← HUMANO LANZA SQ                      │
  │  SQ Optimizer — Walk Forward                                    │
  │  WFE ≥ 50% | 0 ventanas PF < 0.9 | DD OOS ≤ 7%                 │
  │  Tasa de aprobacion: ~50%                                       │
  └─────────────────────────────────────────────────────────────────┘
                    ↓              ↓
               PASA (~3)     DESCARTAR
                    ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  PUERTA 5 — Stress Test                                         │
  │  SQ Retester — 5 periodos criticos                              │
  │  DD < 8% en cada periodo | PF > 1.0 en 3/5 periodos            │
  │  Tasa de aprobacion: ~60%                                       │
  └─────────────────────────────────────────────────────────────────┘
                    ↓              ↓
               PASA (~2)     DESCARTAR
                    ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  PUERTA 6 — Multimarket Test                                    │
  │  SQ Retester — activos correlacionados                          │
  │  PF > 1.0 en al menos 1 activo diferente al IS                  │
  │  Tasa de aprobacion: ~70%                                       │
  └─────────────────────────────────────────────────────────────────┘
                    ↓              ↓
               PASA (~1-2)   DESCARTAR
                    ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  PUERTA 7 — Portfolio Selection (AUTO)                          │
  │  portfolio-builder.py                                           │
  │  Correlacion < 0.5 | DD combinado < 12%                         │
  │  Objetivo: 3-5 estrategias no correlacionadas                   │
  └─────────────────────────────────────────────────────────────────┘
                    ↓              ↓
           INCLUIDO (~3-5)   ESPERA (cola)
                    ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  PUERTA 8 — Forward Test Demo  ← UNICA INTERVENCION HUMANA     │
  │  MT5 demo — 2 semanas                                           │
  │  PF demo ≥ 70% PF OOS | DD demo < DD OOS max                   │
  │  Tasa de aprobacion: ~70%                                       │
  └─────────────────────────────────────────────────────────────────┘
                    ↓              ↓
               PASA          FALLA → volver a Puerta 1
                    ↓
  ┌─────────────────────────────────────────────────────────────────┐
  │  PRODUCCION                                                     │
  │  export-specialist.md → EA compilado en MT5                     │
  │  performance-monitor.md → monitoreo continuo                    │
  │  propfirm: Challenge → Cuenta Funded                            │
  └─────────────────────────────────────────────────────────────────┘

  ═══════════════════════════════════════════════════════
  RESUMEN DE RATIOS ESTIMADOS (por cada 1000 candidatas)
  ═══════════════════════════════════════════════════════

  Puerta 0 (Builder)    : 1000 candidatas generadas
  Puerta 1 (EvalGate)   :  100-200 pasan  (~15%)
  Puerta 2 (Retester)   :   40-80 pasan   (~40%)
  Puerta 3 (SPP)        :   20-40 pasan   (~50%)
  Puerta 4 (WFO)        :   10-20 pasan   (~50%)
  Puerta 5 (Stress)     :    6-12 pasan   (~60%)
  Puerta 6 (Multimarket):    4-8 pasan    (~70%)
  Puerta 7 (Portfolio)  :    3-5 incluidas
  Puerta 8 (FT Demo)    :    2-4 pasan    (~70%)
  PRODUCCION            :    2-4 EAs activos

  ═══════════════════════════════════════════════════════
  HERRAMIENTAS POR ETAPA
  ═══════════════════════════════════════════════════════

  Preparacion    build-launcher.py, pre-build-checklist.py, sqx-build-config.py
  EvalGate       evaluator-assistant.py, pipeline-runner.py
  Finalizacion   build-finisher.py, build-analyzer.py, build-queue-manager.py
  Portfolio      portfolio-builder.py, hrp-portfolio.py, correlation-analyst.md
  Monitoreo      portfolio-monitor.py, performance-monitor.md, telegram-notifier.py
  Informes       auto-reporter.py, session-starter.py, system-health-check.py
  Auditoria      hash-logger.py, strategy-versioning.py, knowledge-base.py
```

---

## Puntos de intervencion humana

| Punto | Accion humana | Herramienta automatica |
|-------|--------------|----------------------|
| Pre-build | Ejecutar build-launcher.py y confirmar | pre-build-checklist.py |
| Build | Pulsar Start en SQ Builder | — |
| Exportar CSVs | SQ → Databank → Export CSV | — |
| Retester | Pulsar Start en SQ Retester | build-finisher.py (post) |
| WFO | Pulsar Start en SQ Optimizer | — |
| Forward Test | Cargar EA en MT5 demo, esperar 2 semanas | — |
| Challenge | Comprar challenge en prop firm | — |

En ningun otro momento el humano interviene en las decisiones del pipeline.

---

## Referencias

- Pipeline completo: `docs/skills/skill-pipeline-flow.md`
- Checklist de puertas: `docs/skills/skill-pipeline-gates-checklist.md`
- Criterios automaticos: `docs/skills/skill-evaluation-auto.md`
- Umbrales numericos: `config/pipeline-config.json`
