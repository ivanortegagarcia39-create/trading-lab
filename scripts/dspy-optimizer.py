#!/usr/bin/env python3
"""
dspy-optimizer.py — Auto-optimización de prompts con DSPy.

Los prompts se compilan automáticamente a partir de ejemplos reales
del pipeline en lugar de ser escritos a mano.

Uso:
    python scripts/dspy-optimizer.py --list
    python scripts/dspy-optimizer.py --stats
    python scripts/dspy-optimizer.py --compile StrategyEvaluator
    python scripts/dspy-optimizer.py --add-example StrategyEvaluator input.json output.json 0.9
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT            = Path(__file__).parent.parent
COMPILED_DIR    = ROOT / "config" / "dspy-compiled"
TRAINING_DIR    = ROOT / "config" / "dspy-training"

try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False

try:
    from model_router import get_lm_for_dspy  # type: ignore
    ROUTER_AVAILABLE = True
except ImportError:
    ROUTER_AVAILABLE = False


# ─── Módulos DSPy ─────────────────────────────────────────────────────────────

MODULES = {
    "StrategyEvaluator": {
        "description": "Evalúa métricas de estrategia y emite veredicto PASA/DESCARTAR",
        "input_fields": ["pf", "dd", "trades", "win_rate", "sharpe", "regime"],
        "output_fields": ["verdict", "justification"],
        "signature": "strategy_metrics -> evaluation_verdict",
    },
    "LessonSynthesizer": {
        "description": "Sintetiza lecciones estructurales a partir de fallos de builds",
        "input_fields": ["failures_context"],
        "output_fields": ["lesson", "recommendation"],
        "signature": "build_failures -> structural_lesson",
    },
    "BuildAnalyzer": {
        "description": "Analiza estadísticas de un build y genera informe ejecutivo",
        "input_fields": ["build_stats"],
        "output_fields": ["analysis", "next_steps"],
        "signature": "build_stats -> analysis_report",
    },
}

BASE_PROMPTS = {
    "StrategyEvaluator": (
        "Eres un evaluador automático de estrategias de trading. "
        "Dado PF={pf}, DD={dd}%, trades={trades}, win_rate={win_rate}%, "
        "sharpe={sharpe}, regime={regime}: emite PASA o DESCARTAR con justificación breve."
    ),
    "LessonSynthesizer": (
        "Eres un sintetizador de lecciones del pipeline. "
        "Dado el contexto de fallos: {failures_context}. "
        "Extrae una lección estructural (no coyuntural) y una recomendación concreta."
    ),
    "BuildAnalyzer": (
        "Eres el analista de builds de TradingLab. "
        "Estadísticas del build: {build_stats}. "
        "Redacta un análisis ejecutivo y lista los próximos pasos prioritarios."
    ),
}


# ─── DSPy Signatures ──────────────────────────────────────────────────────────

def _build_dspy_modules():
    if not DSPY_AVAILABLE:
        return {}

    class StrategyEvaluator(dspy.Signature):
        """Evalúa métricas de estrategia y emite veredicto PASA/DESCARTAR."""
        pf         = dspy.InputField(desc="Profit Factor")
        dd         = dspy.InputField(desc="Max Drawdown %")
        trades     = dspy.InputField(desc="Número de trades")
        win_rate   = dspy.InputField(desc="Win rate %")
        sharpe     = dspy.InputField(desc="Sharpe ratio")
        regime     = dspy.InputField(desc="Régimen de mercado")
        verdict    = dspy.OutputField(desc="PASA o DESCARTAR")
        justification = dspy.OutputField(desc="Justificación breve")

    class LessonSynthesizer(dspy.Signature):
        """Sintetiza lecciones estructurales a partir de fallos de builds."""
        failures_context = dspy.InputField(desc="Contexto de fallos con detalles")
        lesson           = dspy.OutputField(desc="Lección estructural")
        recommendation   = dspy.OutputField(desc="Recomendación concreta")

    class BuildAnalyzer(dspy.Signature):
        """Analiza estadísticas de un build y genera informe ejecutivo."""
        build_stats = dspy.InputField(desc="Estadísticas del build en JSON")
        analysis    = dspy.OutputField(desc="Análisis ejecutivo")
        next_steps  = dspy.OutputField(desc="Próximos pasos prioritarios")

    return {
        "StrategyEvaluator": dspy.ChainOfThought(StrategyEvaluator),
        "LessonSynthesizer": dspy.ChainOfThought(LessonSynthesizer),
        "BuildAnalyzer":     dspy.ChainOfThought(BuildAnalyzer),
    }


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _training_path(module_name: str) -> Path:
    TRAINING_DIR.mkdir(parents=True, exist_ok=True)
    return TRAINING_DIR / f"{module_name}.jsonl"


def _compiled_path(module_name: str) -> Path:
    COMPILED_DIR.mkdir(parents=True, exist_ok=True)
    return COMPILED_DIR / f"{module_name}.json"


def _load_training_examples(module_name: str) -> list:
    path = _training_path(module_name)
    if not path.exists():
        return []
    examples = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))
    return examples


# ─── Funciones principales ────────────────────────────────────────────────────

def add_training_example(module_name: str, input_data: dict, output_data: dict, score: float):
    """Añade un ejemplo al dataset de entrenamiento del módulo."""
    if module_name not in MODULES:
        print(f"ERROR: módulo '{module_name}' no existe. Disponibles: {list(MODULES)}")
        sys.exit(1)
    if not 0.0 <= score <= 1.0:
        print("ERROR: score debe estar entre 0.0 y 1.0")
        sys.exit(1)

    record = {
        "module":    module_name,
        "input":     input_data,
        "output":    output_data,
        "score":     score,
        "timestamp": datetime.now().isoformat(),
    }
    with open(_training_path(module_name), "a") as f:
        f.write(json.dumps(record) + "\n")

    count = len(_load_training_examples(module_name))
    print(f"Ejemplo añadido a {module_name}. Total: {count} (mínimo para compilar: 10)")


def compile_module(module_name: str):
    """Compila el módulo DSPy con los ejemplos de entrenamiento."""
    if module_name not in MODULES:
        print(f"ERROR: módulo '{module_name}' no existe.")
        sys.exit(1)

    examples = _load_training_examples(module_name)
    if len(examples) < 10:
        print(f"Insuficientes ejemplos: {len(examples)}/10. Acumula más antes de compilar.")
        sys.exit(1)

    if not DSPY_AVAILABLE:
        # Modo fallback: guardar resumen estadístico sin DSPy real
        good = [e for e in examples if e["score"] >= 0.7]
        compiled = {
            "module":          module_name,
            "compiled_at":     datetime.now().isoformat(),
            "examples_used":   len(examples),
            "high_quality":    len(good),
            "dspy_available":  False,
            "note": "Compilado en modo fallback (dspy-ai no instalado). Instala con: pip install dspy-ai",
            "best_examples":   good[:3],
        }
        with open(_compiled_path(module_name), "w") as f:
            json.dump(compiled, f, indent=2)
        print(f"[FALLBACK] {module_name} compilado con {len(examples)} ejemplos → {_compiled_path(module_name)}")
        return

    # Compilación real con DSPy
    modules = _build_dspy_modules()
    module  = modules[module_name]

    trainset = [
        dspy.Example(**e["input"], **e["output"]).with_inputs(*MODULES[module_name]["input_fields"])
        for e in examples
        if e["score"] >= 0.5
    ]

    metric = lambda example, pred, trace=None: (
        1.0 if getattr(pred, "verdict", "") in ["PASA", "DESCARTAR"] else 0.0
        if module_name == "StrategyEvaluator"
        else 1.0 if getattr(pred, "lesson", "") else 0.0
    )

    optimizer = dspy.BootstrapFewShot(metric=metric, max_bootstrapped_demos=4)
    compiled_module = optimizer.compile(module, trainset=trainset)

    compiled_module.save(str(_compiled_path(module_name)))
    print(f"{module_name} compilado con {len(trainset)} ejemplos → {_compiled_path(module_name)}")


def load_compiled_module(module_name: str) -> dict | None:
    """Carga el módulo compilado si existe, o None para usar el prompt base."""
    path = _compiled_path(module_name)
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def get_training_stats() -> dict:
    """Devuelve estadísticas de entrenamiento de todos los módulos."""
    stats = {}
    for module_name in MODULES:
        examples  = _load_training_examples(module_name)
        compiled  = _compiled_path(module_name)
        high_q    = [e for e in examples if e["score"] >= 0.7]
        last_comp = None
        if compiled.exists():
            data = json.loads(compiled.read_text())
            last_comp = data.get("compiled_at")

        stats[module_name] = {
            "total_examples":   len(examples),
            "high_quality":     len(high_q),
            "ready_to_compile": len(examples) >= 10,
            "compiled":         compiled.exists(),
            "last_compiled":    last_comp,
        }
    return stats


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="DSPy Optimizer — TradingLab")
    parser.add_argument("--compile",     metavar="MODULE", help="Compilar módulo DSPy")
    parser.add_argument("--stats",       action="store_true", help="Ver estado de entrenamiento")
    parser.add_argument("--list",        action="store_true", help="Listar módulos disponibles")
    parser.add_argument("--add-example", nargs=4,
                        metavar=("MODULE", "INPUT_JSON", "OUTPUT_JSON", "SCORE"),
                        help="Añadir ejemplo de entrenamiento")
    args = parser.parse_args()

    if args.list:
        print("\nMódulos DSPy disponibles:")
        print("-" * 50)
        for name, meta in MODULES.items():
            compiled = _compiled_path(name).exists()
            n_ex     = len(_load_training_examples(name))
            status   = "COMPILADO" if compiled else f"{n_ex}/10 ejemplos"
            print(f"  {name:<25} [{status}]")
            print(f"    {meta['description']}")
        print(f"\nDSPy disponible: {'SÍ' if DSPY_AVAILABLE else 'NO (pip install dspy-ai)'}")

    elif args.stats:
        stats = get_training_stats()
        print("\nEstado de entrenamiento DSPy:")
        print("-" * 60)
        for mod, s in stats.items():
            ready = "LISTO" if s["ready_to_compile"] else f"{s['total_examples']}/10"
            comp  = f"✓ {s['last_compiled'][:10]}" if s["compiled"] else "—"
            print(f"  {mod:<25} ejemplos={s['total_examples']:>3}  "
                  f"HQ={s['high_quality']:>3}  compilar={ready}  último={comp}")

    elif args.compile:
        compile_module(args.compile)

    elif args.add_example:
        module_name, input_json, output_json, score_str = args.add_example
        try:
            input_data  = json.loads(input_json)
            output_data = json.loads(output_json)
            score       = float(score_str)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"ERROR parseando argumentos: {e}")
            sys.exit(1)
        add_training_example(module_name, input_data, output_data, score)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
