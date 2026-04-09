# Roadmap V2 — Expansion del Sistema TradingLab

## Estado actual
- Pipeline operativo con EUR/USD y XAU/USD H1
- 4 agentes base funcionando
- 10 skills especializadas
- Objetivo inmediato: 3 estrategias aprobadas

---

## CAPA 1 — Cuando tengamos 3 estrategias aprobadas

### Nuevos agentes a añadir

#### Agente: technical-analyst
Especialista en analisis tecnico puro.
- Patrones de velas y formaciones chartistas
- Soportes y resistencias clave
- Zonas de valor y confluencias
- Complementa al market-analyst en la fase de hipotesis
- Archivo: agents\technical-analyst.md

#### Agente: correlation-analyst
Especialista en correlaciones entre activos.
- Detecta cuando dos activos se mueven juntos o invertidos
- Evita abrir estrategias correlacionadas en el portfolio
- Fundamental antes de aprobar una segunda estrategia
- Archivo: agents\correlation-analyst.md

#### Agente: risk-manager
Especialista en gestion de riesgo de portfolio.
- Calcula la exposicion total del portfolio
- Verifica que la combinacion de estrategias no supera
  los limites de drawdown de FTMO en conjunto
- Interviene antes de cada aprobacion final
- Archivo: agents\risk-manager.md

#### Agente: news-researcher
Especialista en noticias y fundamentales.
- Investiga el contexto macro antes de un build
- Identifica periodos historicos anomalos en los datos
- Genera un informe de contexto para cada hipotesis
- Archivo: agents\news-researcher.md

### Expansion de universo (Capa 1)
Primer paso: añadir mas pares Forex
- GBP/USD
- USD/JPY
Razon: misma logica que EUR/USD, datos disponibles
en Dukascopy, compatible con FTMO sin cambios.

---

## CAPA 2 — Orquestador autonomo

### Objetivo
El orquestador deja de ser reactivo y pasa a ser
proactivo — decide y ejecuta por su cuenta.

### Como funciona
Cuando se le da una tarea de alto nivel:
"Genera una hipotesis para GBP/USD y llevala
hasta el Evaluation Gate"

El orquestador:
1. Invoca market-analyst para la hipotesis
2. Invoca technical-analyst para validarla
3. Invoca funding-specialist para verificar FTMO
4. Invoca sq-specialist para la config del Builder
5. Documenta todo automaticamente
6. Espera decision humana en Evaluation Gate

### Protocolo de invocacion
INVOCAR: [nombre-agente]
TAREA: [descripcion concreta]
CONTEXTO: [archivos relevantes]
OUTPUT ESPERADO: [donde guardar el resultado]
DECISION HUMANA REQUERIDA: [SI/NO]

### Tecnologia elegida
N8N como plataforma de automatizacion.
- Instalacion local en Windows
- Interfaz visual para workflows
- Conexion nativa con Telegram y Discord
- Conexion con API REST de StrategyQuant X
- Requiere API Key de Anthropic (no plan Pro)

---

## CAPA 3 — Expansion de mercados

### Indices (DAX, SP500)
- Requiere datos de futuros (DE40, US500)
- Verificar compatibilidad con FTMO para indices
- Temporalidades: H1 (misma que Forex)

### Criptomonedas
- Mercado 24/7 — ajustes en opciones de negociacion
- FTMO permite Bitcoin y Ethereum
- Volatilidad mayor — ajustar position sizing
- Requiere revision completa de funding-rules.md

### Orden de implementacion
1. Forex adicional (GBP/USD, USD/JPY)
2. Indices (DAX, SP500)
3. Cripto (BTC, ETH)

---

## CAPA 4 — Skills adicionales planificadas

### Skills pendientes de implementar
- skill-parallel-hypotheses.md
- skill-sq-export-mt5.md
- skill-ftmo-scaling.md
- skill-pipeline-errors.md
- skill-portfolio-correlation.md

Estas skills se implementan cuando se llegue
a la Capa 1 — no antes.

---

## Orden de implementacion global

AHORA:
→ Primer build H1 con comisiones reales
→ Evaluation Gate
→ Retester 2021-2026
→ Conseguir primera estrategia aprobada
→ Repetir hasta tener 3 aprobadas

CAPA 1 (tras 3 estrategias aprobadas):
→ Crear 4 agentes nuevos
→ Ampliar universo a GBP/USD y USD/JPY
→ Implementar skills pendientes

CAPA 2 (tras 5+ estrategias aprobadas):
→ Orquestador autonomo con N8N
→ Primeros tests de automatizacion

CAPA 3 (tras sistema estable):
→ Expansion a indices
→ Evaluacion de cripto

---

## Regla fundamental que no cambia
Nunca expandir antes de tener el proceso anterior estable.
Complejidad antes de proceso = caos garantizado.