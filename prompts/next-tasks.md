PYTHONUTF8=1 python -c "
import json
from datetime import datetime

ranking = {
    'fecha': datetime.now().isoformat(),
    'capital': 25000,
    'riesgo_pct': 1,
    'sl_referencia': 50,
    'ranking': [
        {'activo': 'EURUSD', 'coste_trade': 14.50, 'pct_riesgo': 5.8, 'estado': 'ACTIVO - Build 12'},
        {'activo': 'USDJPY', 'coste_trade': 15.00, 'pct_riesgo': 6.0, 'estado': 'Build 13'},
        {'activo': 'AUDUSD', 'coste_trade': 16.00, 'pct_riesgo': 6.5, 'estado': 'Build 14'},
        {'activo': 'GBPUSD', 'coste_trade': 18.00, 'pct_riesgo': 7.2, 'estado': 'Build 15'},
        {'activo': 'USDCHF', 'coste_trade': 19.00, 'pct_riesgo': 7.6, 'estado': 'Pendiente'},
        {'activo': 'NZDUSD', 'coste_trade': 22.00, 'pct_riesgo': 8.8, 'estado': 'Pendiente'},
        {'activo': 'USDCAD', 'coste_trade': 23.00, 'pct_riesgo': 9.2, 'estado': 'Pendiente'},
        {'activo': 'XAUUSD', 'coste_trade': 317.00, 'pct_riesgo': 126.8, 'estado': 'DESCARTADO'},
    ]
}

with open('results/asset-viability-ranking.json', 'w') as f:
    json.dump(ranking, f, indent=2)
print('Ranking guardado')
"

git add -A && git commit -m "feat: asset viability ranking - XAUUSD descartado, EURUSD primero" && git push origin main