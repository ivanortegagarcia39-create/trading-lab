Lee CLAUDE.md y todos los archivos en agents/.

Dos tareas en paralelo:

TAREA 1 - Añadir personalidad a los 5 agentes principales
Para cada uno de estos agentes, añadir al inicio del archivo
una sección ## Personalidad con tono, estilo y ejemplo real:

agents/orchestrator.md:
  Tono: Ejecutivo. Directo. Sin rodeos.
  Estilo: "Pipeline iniciado. Build 11, XAUUSD H1. ETA 48h."
  Evitar: explicaciones innecesarias, preguntas al humano

agents/evaluator-assistant.md:
  Tono: Quirúrgico. Numérico. Sin ambigüedad.
  Estilo: "PF 1.31. DD 57.99%. No pasa. Criterio: DD > 7%."
  Evitar: suavizar rechazos, dar segundas oportunidades

agents/performance-monitor.md:
  Tono: Vigilante. Alerta temprana. Proactivo.
  Estilo: "DD 3.2% detectado. Tendencia: +0.4%/día. Atención."
  Evitar: alarmar sin datos, ignorar señales débiles

agents/knowledge-synthesizer.md:
  Tono: Científico. Escéptico. Exige evidencia.
  Estilo: "3 ocurrencias confirmadas en 2 regímenes. ESTRUCTURAL."
  Evitar: elevar lecciones sin evidencia suficiente

agents/market-regime-detector.md:
  Tono: Sensor. Objetivo. Sin interpretación subjetiva.
  Estilo: "ADX 27.3. ATR 1.8x media. Régimen: tendencia-altavol."
  Evitar: especular sobre duración del régimen

TAREA 2 - Ampliar scripts/model-router.py con modelos Anthropic
Lee el archivo actual. Añadir estos modelos a la tabla:

"claude_opus": modelo claude-opus-4-6, coste $15/1M input,
  latencia alta, calidad máxima
  Usar para: strategy (máxima calidad), causal_analysis, critical_audit

"claude_sonnet": modelo claude-sonnet-4-6, coste $3/1M input,
  latencia media, calidad alta
  Usar para: report_generation, code_review_large, hypothesis_generation

"claude_haiku": modelo claude-haiku-4-5-20251001, coste $0.80/1M input,
  latencia baja, calidad buena
  Usar para: bulk_classification, quick tasks

Actualizar la tabla de enrutamiento:
  "strategy": claude_opus (si disponible) o kimi_k26
  "causal_analysis": claude_opus o gpt_55
  "critical_audit": claude_opus o gpt_55
  "report_generation": claude_sonnet o llama_local
  "bulk_classification": claude_haiku o deepseek_local

Los modelos Anthropic usan la misma API key de OpenAI-compatible
pero con base_url https://api.anthropic.com/v1
Leer ANTHROPIC_API_KEY de config/api-keys.json

TAREA 3 - Crear docs/claude-project-setup.md
Documenta cómo configurar el Claude Project de TradingLab:

Qué es un Claude Project y por qué elimina la fricción
Qué archivos cargar: CLAUDE.md, lessons-learned, propfirm-rules, project-status
Las instrucciones exactas a pegar en el Project
Cómo mantener los archivos actualizados (sincronizar tras cada sesión importante)
Qué NO cargar: archivos con credenciales, .chromadb, .kuzu

Al terminar:
git add .
git commit -m "v8.1: personalidad agentes, model-router Anthropic, claude-project-setup"
git push origin main
Confirma con tabla.