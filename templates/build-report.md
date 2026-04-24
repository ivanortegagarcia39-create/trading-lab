---
fecha: {{date:YYYY-MM-DD}}
build: 
activo: 
timeframe: H1
duracion_horas: 
estrategias_generadas: 
estrategias_databank: 
tasa_aprobacion: 
pf_maximo: 
pf_promedio: 
dd_mejor: 
spread_configurado: 
estado: EN_CURSO
---

# Build {{build}} — {{activo}}

## Resumen
- **Fecha inicio:** {{date}}
- **Activo:** {{activo}}
- **Spread configurado:** {{spread_configurado}} pips

## Resultados
- Estrategias generadas: {{estrategias_generadas}}
- Estrategias en databank: {{estrategias_databank}}
- Tasa de aprobación: {{tasa_aprobacion}}%
- PF máximo: {{pf_maximo}}
- PF promedio: {{pf_promedio}}
- DD mejor estrategia: {{dd_mejor}}%

## Análisis
[Claude Code genera este análisis con build-analyzer.py]

## Decisión del Pipeline
- [ ] EvalGate ejecutado
- [ ] Retester ejecutado
- [ ] WFO ejecutado
- [ ] Portfolio verificado

## Lecciones de este Build
[Ver docs/lessons-learned.md]
