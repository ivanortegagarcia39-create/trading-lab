Añade estos comandos a scripts/telegram-listener.py:

/METRICS — responde con métricas del build activo:
  - Lee pipeline.lock → build, activo, tiempo corriendo
  - Cuenta .sqx en Builder/Results
  - Formatea y envía mensaje Telegram

/STRATEGIES — lista las estrategias aprobadas:
  - Lee evaluation-gate-results.json si existe
  - Muestra nombre, PF, DD, trades de cada aprobada
  - Si no hay ninguna → "Sin estrategias aprobadas aún"

/PORTFOLIO — estado del portfolio:
  - Lee strategies-registry.json si existe
  - Muestra estrategias activas, DD combinado
  - Si vacío → "Portfolio vacío — objetivo 3 estrategias"

/BUILD — info del build activo:
  - Lee pipeline.lock
  - Muestra build, activo, spread, SL/PT, IS period, timestamp inicio

Cada comando debe:
- Enviar la respuesta directamente al chat de Telegram via bot
- Funcionar en modo --check igual que los comandos existentes
- Si falla → responder "Error al obtener datos" sin abortar

git add -A && git commit -m "feat: telegram-listener añade comandos METRICS STRATEGIES PORTFOLIO BUILD" && git push origin main