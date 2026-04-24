---
fecha: 2026-04-22
build: 10
activo: XAUUSD
timeframe: H1
duracion_horas: En curso
estrategias_generadas: 3121+
estrategias_databank: 2
tasa_aprobacion: 0.06
pf_maximo: 1.31
pf_promedio: N/A
dd_mejor: 57.99
spread_configurado: 30
estado: EN_CURSO
---

# Build 10 — XAUUSD H1

## Resumen
- **Fecha inicio:** 2026-04-22
- **Activo:** XAUUSD
- **Spread configurado:** 30 pips

## Resultados
- Estrategias generadas: 3121+ (build en curso)
- Estrategias en databank: 2
- Tasa de aprobación: 0.06%
- PF máximo: 1.31
- PF promedio: N/A (muestra insuficiente)
- DD mejor estrategia: 57.99%

## Análisis
[Pendiente — ejecutar build-analyzer.py al completar el build]

## Observación Crítica

**PROBLEMA DETECTADO: Spread insuficiente**

El DD del 57.99% en la mejor estrategia indica que el
spread configurado es 30 pips (spread real de XAUUSD)
en lugar de 60 pips (el doble requerido por el planning
maestro — backtest sucio con spread 2x).

**Acción:** Corregir el spread a 60 pips en el próximo build.
Ver docs/skills/skill-builder-libre.md — configuración de spreads.

Este build NO produce estrategias válidas para el pipeline
si el spread 2x no estaba aplicado desde el inicio.

## Decisión del Pipeline
- [ ] EvalGate ejecutado
- [ ] Retester ejecutado
- [ ] WFO ejecutado
- [ ] Portfolio verificado

## Lecciones de este Build
- TENTATIVA: Spread 2x es obligatorio desde el inicio del build.
  Un spread incorrecto invalida todo el databank generado.
  Verificar siempre la configuración antes de lanzar el Builder.

[Ver docs/lessons-learned.md para registro formal]
