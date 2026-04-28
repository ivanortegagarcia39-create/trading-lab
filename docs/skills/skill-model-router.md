# Skill: Router de Modelos LLM

## Propósito

Usar el modelo correcto para cada tarea evita gastar $30/1M tokens de GPT-5.5
en tareas que DeepSeek R1 local puede hacer gratis.
El router decide automáticamente — sin intervención humana.

---

## Principio de Coste Mínimo

Siempre usar el modelo más barato que sea suficiente para la tarea.

```
Local gratuito > Kimi K2.6 ($0.95/1M) > GPT-5.5 ($5/1M)
```

Solo escalar a modelos más caros cuando:
- La tarea requiere razonamiento muy profundo (causal_analysis, critical_audit)
- La tarea es multimodal (imágenes de curvas de equity)
- El contexto supera 128K tokens
- El modelo local no está disponible

---

## Modelos disponibles

| ID | Modelo | Coste input | Coste output | Privacidad |
|----|--------|-------------|--------------|------------|
| `deepseek_local` | DeepSeek R1 7B (Ollama) | ~$0 | ~$0 | Total |
| `llama_local` | Llama 3.1 8B (Ollama) | ~$0 | ~$0 | Total |
| `kimi_k26` | Kimi K2.6 (Moonshot API) | $0.95/1M | $4.66/1M | Externa |
| `gpt_55` | GPT-5.5 (OpenAI API) | $5/1M | $30/1M | Externa |

---

## Tabla de enrutamiento

| Tarea | Modelo primario | Fallback |
|-------|----------------|----------|
| `mql5_audit` | deepseek_local | kimi_k26 |
| `mql5_refactor_large` | kimi_k26 | — |
| `build_analysis` | deepseek_local | kimi_k26 |
| `strategy_evaluation` | deepseek_local | — |
| `lesson_synthesis` | deepseek_local | — |
| `causal_analysis` | gpt_55 | — |
| `equity_curve_analysis` | gpt_55 | — |
| `report_generation` | llama_local | deepseek_local |
| `code_review_large` | kimi_k26 | — |
| `hypothesis_generation` | deepseek_local | — |
| `critical_audit` | gpt_55 | — |
| `bulk_classification` | kimi_k26 | — |

---

## Privacidad — Regla inquebrantable

Datos que NUNCA salen a APIs externas (Kimi, GPT-5.5):
- Credenciales de cuentas
- IDs de cuentas de prop firms
- Trades reales con balances
- Información personal o financiera

Datos que SÍ pueden enviarse a APIs externas:
- Código MQL5 (sin credenciales hardcodeadas)
- Métricas estadísticas de estrategias (PF, DD, trades)
- Logs de análisis anonimizados
- Textos de análisis y reportes

El router aplica esta regla automáticamente: tareas con datos sensibles
siempre van a `deepseek_local` o `llama_local`, nunca a APIs externas.

---

## Caché de APIs

### Kimi K2.6 (Moonshot)
- Caché automático en prompts repetidos
- Descuento hasta 75% en cached input tokens
- Maximizar: reutilizar el mismo prompt base entre llamadas similares

### GPT-5.5 (OpenAI)
- Prompt caching disponible con 90% de descuento en cached input
- Usar el mismo system prompt en todas las llamadas del mismo tipo de tarea

El model-router envía el mismo prompt base por tipo de tarea para aprovechar el caché.

---

## Uso desde otros scripts

```python
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "model_router", Path(__file__).parent / "model-router.py"
)
router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(router)

# Llamada simple
response = router.route("build_analysis", prompt)

# Con contexto adicional
response = router.route("build_analysis", prompt, context=build_stats)

# Con imagen (multimodal)
response = router.route("equity_curve_analysis", prompt, image_path="chart.png")
```

---

## Uso CLI

```bash
# Ver tabla de enrutamiento
python scripts/model-router.py --list-tasks

# Dry-run: ver qué modelo se usaría
python scripts/model-router.py --task build_analysis --prompt "..." --dry-run

# Ejecutar
python scripts/model-router.py --task mql5_audit --prompt "$(cat ea.mq5)"

# Estadísticas de uso y costes
python scripts/model-router.py --stats
```

---

## Log de uso

Cada llamada se registra en `results/model-usage.jsonl`:
```json
{"timestamp": "2026-04-28T10:15:00", "task_type": "build_analysis",
 "model": "deepseek_local", "prompt_tokens": 250, "output_tokens": 180,
 "cost_usd": 0.0, "elapsed_s": 4.2}
```

Usar `--stats` para ver el resumen agregado de costes.

---

## Configuración de claves API

Copiar `config/api-keys.json.template` a `config/api-keys.json`
y rellenar con las claves reales. El archivo `.json` está en `.gitignore`.

```bash
cp config/api-keys.json.template config/api-keys.json
# Editar config/api-keys.json con las claves reales
```

Alternativamente, usar variables de entorno:
```bash
export OPENAI_API_KEY="sk-..."
export MOONSHOT_API_KEY="sk-..."
```

---

## Referencias

- `scripts/model-router.py` — implementación del router
- `config/api-keys.json.template` — template de claves API
- `results/model-usage.jsonl` — log de uso y costes
- `scripts/build-analyzer.py` — usa `route("build_analysis", ...)`
- `scripts/mql5-auditor.py` — usa `route("mql5_audit", ...)`
