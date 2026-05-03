"""
model-router.py — Router central de modelos LLM para TradingLab.
Decide automáticamente qué modelo usar para cada tarea según coste,
calidad y privacidad.

Uso CLI:
    python scripts/model-router.py --task build_analysis --prompt "..."
    python scripts/model-router.py --task mql5_audit --prompt "..." --dry-run
    python scripts/model-router.py --stats
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

ROOT         = Path(__file__).parent.parent
USAGE_LOG    = ROOT / "results" / "model-usage.jsonl"
API_KEYS_FILE = ROOT / "config" / "api-keys.json"

# ─── Tabla de enrutamiento ────────────────────────────────────────────────────
# Cada entrada es una lista ordenada por prioridad (más barato/privado primero)

ROUTING_TABLE: dict[str, list[str]] = {
    "mql5_audit":            ["deepseek_local", "kimi_k26"],
    "mql5_refactor_large":   ["kimi_k26"],
    "build_analysis":        ["deepseek_local", "kimi_k26"],
    "strategy_evaluation":   ["deepseek_local"],
    "lesson_synthesis":      ["deepseek_local"],
    "strategy":              ["claude_opus", "kimi_k26"],
    "causal_analysis":       ["claude_opus", "gpt_55"],
    "equity_curve_analysis": ["gpt_55"],
    "report_generation":     ["claude_sonnet", "llama_local"],
    "code_review_large":     ["claude_sonnet", "kimi_k26"],
    "hypothesis_generation": ["claude_sonnet", "deepseek_local"],
    "critical_audit":        ["claude_opus", "gpt_55"],
    "bulk_classification":   ["claude_haiku", "deepseek_local"],
}

# Coste estimado por token (USD)
MODEL_COSTS: dict[str, dict] = {
    "deepseek_local": {"input": 0.0,      "output": 0.0},
    "llama_local":    {"input": 0.0,      "output": 0.0},
    "kimi_k26":       {"input": 0.00095,  "output": 0.00466},   # por 1K tokens
    "gpt_55":         {"input": 0.005,    "output": 0.030},
    "claude_opus":    {"input": 0.015,    "output": 0.075},     # $15/1M input
    "claude_sonnet":  {"input": 0.003,    "output": 0.015},     # $3/1M input
    "claude_haiku":   {"input": 0.0008,   "output": 0.004},     # $0.80/1M input
}

ANTHROPIC_MODELS: dict[str, str] = {
    "claude_opus":   "claude-opus-4-6",
    "claude_sonnet": "claude-sonnet-4-6",
    "claude_haiku":  "claude-haiku-4-5-20251001",
}

OLLAMA_MODELS: dict[str, str] = {
    "deepseek_local": "deepseek-r1:7b",
    "llama_local":    "llama3.1:8b",
}

OLLAMA_URL   = "http://localhost:11434"
OLLAMA_TIMEOUT = 180


# ─── Excepciones ─────────────────────────────────────────────────────────────

class ModelUnavailableError(Exception):
    pass


# ─── Carga de claves API ──────────────────────────────────────────────────────

def _load_api_key(key_name: str) -> str:
    """Lee la clave API de config/api-keys.json o de variable de entorno."""
    import os
    env_map = {
        "openai_api_key":    "OPENAI_API_KEY",
        "moonshot_api_key":  "MOONSHOT_API_KEY",
        "anthropic_api_key": "ANTHROPIC_API_KEY",
        "firecrawl_api_key": "FIRECRAWL_API_KEY",
    }
    env_var = env_map.get(key_name, key_name.upper())
    env_val = os.environ.get(env_var, "")
    if env_val:
        return env_val

    if API_KEYS_FILE.exists():
        try:
            keys = json.loads(API_KEYS_FILE.read_text(encoding="utf-8"))
            return keys.get(key_name, "")
        except Exception:
            pass
    return ""


# ─── Llamadas a modelos ───────────────────────────────────────────────────────

def _call_ollama(model_key: str, prompt: str) -> str:
    """Llama a un modelo local via Ollama. Lanza ModelUnavailableError si no responde."""
    ollama_model = OLLAMA_MODELS.get(model_key, "deepseek-r1:7b")
    payload = json.dumps({
        "model":  ollama_model,
        "prompt": prompt,
        "stream": False,
    }).encode()

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
            data = json.loads(resp.read())
            return data.get("response", "").strip()
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        raise ModelUnavailableError(f"Ollama no disponible ({ollama_model}): {e}") from e


def _ollama_available(model_key: str) -> bool:
    try:
        req = urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=5)
        if req.status != 200:
            return False
        tags = json.loads(req.read())
        target = OLLAMA_MODELS.get(model_key, "")
        return any(target in m.get("name", "") for m in tags.get("models", []))
    except Exception:
        return False


def _call_kimi(prompt: str, thinking: bool = False) -> str:
    """Llama a Kimi K2.6 via API Moonshot (compatible con OpenAI SDK)."""
    api_key = _load_api_key("moonshot_api_key")
    if not api_key:
        raise ModelUnavailableError("MOONSHOT_API_KEY no configurada")

    try:
        from openai import OpenAI
    except ImportError:
        raise ModelUnavailableError("openai SDK no instalado. Ejecuta: pip install openai")

    client = OpenAI(api_key=api_key, base_url="https://api.moonshot.cn/v1")
    messages = [{"role": "user", "content": prompt}]
    kwargs: dict = {"model": "moonshot-v1-128k", "messages": messages}
    if thinking:
        kwargs["temperature"] = 1.0

    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content or ""


def _call_anthropic(model_key: str, prompt: str) -> str:
    """Llama a un modelo Claude via API Anthropic (compatible con OpenAI SDK)."""
    api_key = _load_api_key("anthropic_api_key")
    if not api_key:
        raise ModelUnavailableError("ANTHROPIC_API_KEY no configurada")

    try:
        from openai import OpenAI
    except ImportError:
        raise ModelUnavailableError("openai SDK no instalado. Ejecuta: pip install openai")

    model_id = ANTHROPIC_MODELS.get(model_key, "claude-sonnet-4-6")
    client = OpenAI(api_key=api_key, base_url="https://api.anthropic.com/v1")
    resp = client.chat.completions.create(
        model=model_id,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content or ""


def _call_gpt55(prompt: str, image_path: str | None = None,
                reasoning_effort: str = "medium") -> str:
    """Llama a GPT-5.5 via OpenAI API, con soporte multimodal opcional."""
    api_key = _load_api_key("openai_api_key")
    if not api_key:
        raise ModelUnavailableError("OPENAI_API_KEY no configurada")

    try:
        from openai import OpenAI
    except ImportError:
        raise ModelUnavailableError("openai SDK no instalado. Ejecuta: pip install openai")

    client = OpenAI(api_key=api_key)

    if image_path:
        import base64
        img_data = Path(image_path).read_bytes()
        b64 = base64.b64encode(img_data).decode()
        ext = Path(image_path).suffix.lstrip(".").lower()
        mime = f"image/{ext}" if ext in ("png", "jpg", "jpeg", "gif", "webp") else "image/png"
        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
        ]
    else:
        content = prompt

    resp = client.chat.completions.create(
        model="gpt-4.5-preview",  # actualizar cuando GPT-5.5 esté disponible
        messages=[{"role": "user", "content": content}],
    )
    return resp.choices[0].message.content or ""


# ─── Dispatcher ───────────────────────────────────────────────────────────────

def _dispatch(model_key: str, prompt: str, image_path: str | None = None) -> str:
    if model_key in ("deepseek_local", "llama_local"):
        return _call_ollama(model_key, prompt)
    elif model_key == "kimi_k26":
        return _call_kimi(prompt)
    elif model_key == "gpt_55":
        return _call_gpt55(prompt, image_path=image_path)
    elif model_key in ANTHROPIC_MODELS:
        return _call_anthropic(model_key, prompt)
    else:
        raise ModelUnavailableError(f"Modelo desconocido: {model_key}")


def _is_available(model_key: str) -> bool:
    if model_key in ("deepseek_local", "llama_local"):
        return _ollama_available(model_key)
    elif model_key == "kimi_k26":
        return bool(_load_api_key("moonshot_api_key"))
    elif model_key == "gpt_55":
        return bool(_load_api_key("openai_api_key"))
    elif model_key in ANTHROPIC_MODELS:
        return bool(_load_api_key("anthropic_api_key"))
    return False


# ─── Log de uso ───────────────────────────────────────────────────────────────

def _log_usage(task_type: str, model_used: str, prompt_tokens: int,
               output_tokens: int, elapsed_s: float) -> None:
    costs = MODEL_COSTS.get(model_used, {"input": 0.0, "output": 0.0})
    cost_usd = (prompt_tokens / 1000) * costs["input"] + (output_tokens / 1000) * costs["output"]

    entry = {
        "timestamp":     datetime.now().isoformat(timespec="seconds"),
        "task_type":     task_type,
        "model":         model_used,
        "prompt_tokens": prompt_tokens,
        "output_tokens": output_tokens,
        "cost_usd":      round(cost_usd, 6),
        "elapsed_s":     round(elapsed_s, 2),
    }
    USAGE_LOG.parent.mkdir(exist_ok=True)
    with USAGE_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ─── Función pública principal ────────────────────────────────────────────────

def route(task_type: str, prompt: str, image_path: str | None = None,
          context: dict | None = None) -> str:
    """
    Enruta la tarea al modelo correcto y devuelve la respuesta.
    Aplica fallback automático si el modelo primario no está disponible.
    Registra uso en results/model-usage.jsonl.
    """
    candidates = ROUTING_TABLE.get(task_type, ["deepseek_local"])

    full_prompt = prompt
    if context:
        ctx_str = json.dumps(context, ensure_ascii=False, indent=2)
        full_prompt = f"{prompt}\n\nContexto adicional:\n{ctx_str}"

    last_error = None
    for model_key in candidates:
        if not _is_available(model_key):
            continue
        t0 = time.time()
        try:
            response = _dispatch(model_key, full_prompt, image_path=image_path)
            elapsed = time.time() - t0
            prompt_tokens  = len(full_prompt.split())
            output_tokens  = len(response.split())
            _log_usage(task_type, model_key, prompt_tokens, output_tokens, elapsed)
            return response
        except ModelUnavailableError as e:
            last_error = e
            continue
        except Exception as e:
            last_error = e
            continue

    # Todos los candidatos fallaron — último recurso: Ollama genérico si hay alguno
    for fallback in ["deepseek_local", "llama_local", "kimi_k26"]:
        if fallback not in candidates and _is_available(fallback):
            t0 = time.time()
            try:
                response = _dispatch(fallback, full_prompt, image_path=image_path)
                elapsed = time.time() - t0
                _log_usage(task_type, f"{fallback}(fallback)", len(full_prompt.split()),
                           len(response.split()), elapsed)
                return response
            except Exception:
                pass

    raise ModelUnavailableError(
        f"Ningún modelo disponible para '{task_type}'. "
        f"Último error: {last_error}"
    )


# ─── Estadísticas de uso ──────────────────────────────────────────────────────

def get_usage_stats() -> dict:
    """Lee el log y devuelve estadísticas agregadas."""
    if not USAGE_LOG.exists():
        return {"total_calls": 0, "by_model": {}, "total_cost_usd": 0.0, "month_cost_usd": 0.0}

    by_model: dict[str, dict] = {}
    total_cost = 0.0
    month_cost = 0.0
    current_month = datetime.now().strftime("%Y-%m")

    with USAGE_LOG.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            model = entry.get("model", "unknown")
            cost  = float(entry.get("cost_usd", 0.0))
            total_cost += cost
            if entry.get("timestamp", "").startswith(current_month):
                month_cost += cost
            if model not in by_model:
                by_model[model] = {"calls": 0, "tokens_in": 0, "tokens_out": 0, "cost_usd": 0.0}
            by_model[model]["calls"]      += 1
            by_model[model]["tokens_in"]  += entry.get("prompt_tokens", 0)
            by_model[model]["tokens_out"] += entry.get("output_tokens", 0)
            by_model[model]["cost_usd"]   += cost

    total_calls = sum(v["calls"] for v in by_model.values())
    return {
        "total_calls":    total_calls,
        "by_model":       by_model,
        "total_cost_usd": round(total_cost, 4),
        "month_cost_usd": round(month_cost, 4),
    }


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Model Router — TradingLab")
    parser.add_argument("--task",    help="Tipo de tarea (ej: build_analysis, mql5_audit)")
    parser.add_argument("--prompt",  help="Prompt a enviar (o usar stdin)")
    parser.add_argument("--image",   help="Ruta a imagen para tareas multimodales")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostrar qué modelo se usaría sin llamarlo")
    parser.add_argument("--stats",   action="store_true",
                        help="Mostrar estadísticas de uso")
    parser.add_argument("--list-tasks", action="store_true",
                        help="Listar todas las tareas disponibles")
    args = parser.parse_args()

    if args.list_tasks:
        print("\nTabla de enrutamiento:")
        print(f"  {'TASK_TYPE':30s}  MODELOS (por prioridad)")
        print("  " + "-" * 60)
        for task, models in ROUTING_TABLE.items():
            print(f"  {task:30s}  {' > '.join(models)}")
        return 0

    if args.stats:
        stats = get_usage_stats()
        print("\nModel Router — Estadísticas de uso")
        print("=" * 45)
        print(f"  Total llamadas:      {stats['total_calls']}")
        print(f"  Coste total:         ${stats['total_cost_usd']:.4f}")
        print(f"  Coste mes actual:    ${stats['month_cost_usd']:.4f}")
        print()
        for model, data in stats["by_model"].items():
            print(f"  {model}:")
            print(f"    Llamadas: {data['calls']}  |  "
                  f"Tokens in: {data['tokens_in']}  out: {data['tokens_out']}  |  "
                  f"Coste: ${data['cost_usd']:.4f}")
        return 0

    if not args.task:
        parser.print_help()
        return 1

    prompt = args.prompt
    if not prompt:
        prompt = sys.stdin.read().strip()
    if not prompt:
        print("[ERROR] Se requiere --prompt o entrada por stdin.")
        return 1

    candidates = ROUTING_TABLE.get(args.task, ["deepseek_local"])

    if args.dry_run:
        print(f"\nDry-run para tarea '{args.task}':")
        for i, model in enumerate(candidates):
            avail = _is_available(model)
            status = "DISPONIBLE" if avail else "no disponible"
            selected = " ← seleccionado" if avail and i == next(
                (j for j, m in enumerate(candidates) if _is_available(m)), -1
            ) else ""
            print(f"  {i+1}. {model}: {status}{selected}")
        return 0

    try:
        response = route(args.task, prompt, image_path=args.image)
        print(response)
        return 0
    except ModelUnavailableError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
