# Informe Semanal — 2026-W19
Generado: 2026-05-15

---

## Estado del Pipeline

| Metrica | Valor |
|---------|-------|
| Build activo | {
  "build": 12,
  "activo": "EURUSD",
  "spread_real": 0.5,
  "started": "2026-05-15T13:37:48.941859",
  "status": "running"
} |
| Estrategias en databank | 0 |
| EvalGate: pasan | 0 / 0 |
| Portfolio | 0 estrategias (N/A) |
| Ultima sesion | 2026-05-07T12:28:02 |

---

## Portfolio Activo

| Estrategia | Activo | Peso HRP |
|------------|--------|----------|
| (ninguna activa) | — | — |

---

## Estado del Sistema

OK:23 WARN:5 FAIL:0 — 2026-05-07T12:28:00

Health checks: OK:23 — WARN:5 — FAIL:0

---

## Planning Maestro

**202 / 222 tareas completadas (91.0%)**

---

## Lecciones Estructurales

- LECCION-001: M15 con comisiones reales FTMO elimina el edge
- LECCION-002: Hipotesis humana restringe el espacio de busqueda
- LECCION-005: XAUUSD H1 inviable con spread 60 pips y reglas FTMO

---

## Proximas Acciones

Comando exacto: python scripts/build-launcher.py --build 11 --activo XAUUSD --spread-real 30
### Planning Maestro
| Metrica | Valor |
|---------|-------|

## Proxima Semana

| Elemento | Detalle |
|----------|---------|
| Proximo build (Thompson) | EURUSD |
| Criterios bayesianos a revisar | sin ajustes pendientes |

**Cola de activos pendientes:**
  - Cola de Builds — 4 activos
  - ============================================================
  - ▶ 1. XAUUSD     Score:80    EN_CURSO     Build 11
  - Build 10 completado (spread 30 pips). Build 11 pendiente con spread 60 pips.
  - Notas: Spread corregido a 60 pips. Lanzar en alber.

**Shadow mode terminando esta semana:**
  - ninguna

---

## Sistema de Autoaprendizaje

| Componente | Estado | Última actualización |
|------------|--------|---------------------|
| Knowledge Graph | 0 builds, 0 estrategias | 2026-05-07 |
| Bayesian Criteria | 5 criterios | 2026-04-28 |
| DSPy Optimizer | 0 módulos compilados | — |
| Thompson Sampling | no inicializado | — |
| Concept Drift | sin datos | — |
| Champion-Challenger | sin datos | — |
| Self-improvement | Último ciclo:  |  |

---

---
*Generado por auto-reporter.py — TradingLab*
