# Integracion Ollama — TradingLab

## Que es Ollama en el proyecto

Ollama corre modelos LLM localmente en alber.
Sin coste de API, sin limites de uso, sin enviar
datos del proyecto a servicios externos.

Permite que el pipeline tenga capacidad de analisis
de lenguaje natural en tareas repetitivas de bajo-medio
riesgo sin consumir tokens de Claude API.

---

## Modelos a instalar en alber

deepseek-r1:7b
  Uso principal: analisis de estrategias y decisiones
  Tamaño: ~4GB
  Requisito RAM: 8GB minimo

llama3.1:8b
  Uso principal: resumenes ejecutivos post-build
  Tamaño: ~4.7GB
  Requisito RAM: 8GB minimo

Instalar ambos antes de activar scripts que los usan.

---

## Division de tareas: Ollama vs Claude API

### Ollama (local, gratuito, privado)
- Analisis de codigo MQL5 (mql5-auditor.py)
- Resumenes ejecutivos post-build (build-analyzer.py)
- Analisis de lessons-learned.md para patrones
- Reflexion diaria de decisiones del sistema
- Consultas a la knowledge base (ChromaDB)
- Cualquier tarea repetitiva con contexto acotado

### Claude API (cloud, coste por token)
- Decisiones complejas del orchestrator
- Generacion de documentacion nueva
- Analisis de situaciones no previstas
- Sesiones de planning y arquitectura
- Tareas que requieren razonamiento profundo
  o contexto largo (> 4k tokens efectivos)

Criterio de asignacion: si la tarea es repetible,
tiene contexto acotado y no requiere razonamiento
de vanguardia → Ollama. Si necesita maxima capacidad
o el contexto es amplio y complejo → Claude API.

---

## Instalacion en alber

```
winget install Ollama.Ollama
ollama pull deepseek-r1:7b
ollama pull llama3.1:8b
```

Verificar que estan instalados:
```
ollama list
```

Resultado esperado:
```
NAME                 ID              SIZE   MODIFIED
deepseek-r1:7b       ...             4.7GB  ...
llama3.1:8b          ...             4.7GB  ...
```

Ollama corre como servicio en http://localhost:11434
Se inicia automaticamente al arrancar Windows.

---

## Integracion con scripts Python

Los scripts Python se conectan a Ollama via HTTP:

```python
import requests

def query_ollama(prompt: str, model: str = "deepseek-r1:7b") -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )
    return response.json()["response"]
```

Si Ollama no esta disponible → fallback a analisis
estatico sin LLM (ya implementado en mql5-auditor.py).

El fallback garantiza que el pipeline no se bloquea
si alber no tiene Ollama activo.

---

## Scripts que usan Ollama

scripts/mql5-auditor.py
  Modelo: deepseek-r1:7b
  Tarea: auditar codigo MQL5 exportado
  Fallback: reglas estaticas de auditoria

scripts/build-analyzer.py (pendiente crear)
  Modelo: llama3.1:8b
  Tarea: resumen ejecutivo de resultados post-build
  Fallback: resumen de metricas sin interpretacion

---

## Consideraciones de hardware

Ollama y SQ NO deben correr simultaneamente en alber.
SQ usa CPU al 100% durante builds — Ollama necesita
CPU y RAM para inferencia.

Protocolo:
- Durante builds SQ: Ollama en standby (no consultar)
- Fuera de builds: Ollama disponible para analisis
- Si RAM < 16GB: cerrar SQ antes de consultar Ollama

Temperatura maxima recomendada durante inferencia: 80C.

---

## Estado del proyecto

Fase actual: Capa 0
Ollama disponible: pendiente instalar en alber
Scripts con soporte Ollama: mql5-auditor.py (completo)
Integracion completa: Capa 2 del roadmap
