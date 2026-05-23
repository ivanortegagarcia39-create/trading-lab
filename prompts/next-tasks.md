$env:PYTHONUTF8=1; python -c "
from pathlib import Path
import json

ROOT = Path(r'C:\Users\ivano\trading-lab')

# Ver qué scripts de autoaprendizaje existen y si tienen datos
scripts_auto = [
    'thompson-sampling.py',
    'concept-drift-detector.py', 
    'kg-importer.py',
    'knowledge-graph.py',
    'lessons-analyzer.py',
    'bayesian-optimizer.py',
    'champion-challenger.py',
    'dspy-optimizer.py',
]

for s in scripts_auto:
    p = ROOT / 'scripts' / s
    exists = p.exists()
    print(f'  {\"OK\" if exists else \"FALTA\"} {s}')

# Ver si build-finisher.py llama a estos scripts
print()
finisher = (ROOT / 'scripts' / 'build-finisher.py').read_text(encoding='utf-8', errors='ignore')
for s in scripts_auto:
    nombre = s.replace('.py', '')
    if nombre in finisher:
        print(f'  build-finisher llama a: {s}')

# Ver si hay datos reales en los JSONs de autoaprendizaje
print()
auto_jsons = [
    'results/thompson-state.json',
    'results/drift-detection.json', 
    'results/kg-data.json',
    'results/champion-challenger.json',
]
for j in auto_jsons:
    p = ROOT / j
    if p.exists():
        size = p.stat().st_size
        print(f'  {j}: {size:,} bytes')
    else:
        print(f'  FALTA: {j}')
" 2>&1 | Out-String