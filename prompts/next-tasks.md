import zipfile, re

with zipfile.ZipFile(r'D:\user\projects\Builder\project.cfx') as z:
    xml = z.read('Build-Task1.xml').decode()

print("=== VERIFICACION COMPLETA BUILD 11 ===")
print(f"Capital: {re.findall(r'<InitialCapital>(\d+)</InitialCapital>', xml)}")
print(f"Spread: {re.findall(r'defaultSpread=\"([^\"]+)\"', xml)[:2]}")
print(f"Slippage: {re.findall(r'slippage=\"([^\"]+)\"', xml)[:3]}")
print(f"Simbolo: {re.findall(r'symbol=\"([^\"]+)\"', xml)[:3]}")
print(f"Timeframe: {re.findall(r'timeframe=\"([^\"]+)\"', xml)[:3]}")
print(f"MM activo: {re.findall(r'<Method type=\"([^\"]+)\" use=\"true\">', xml)}")
print(f"SL min-max: {re.findall(r'SLmin|SLmax|minSL|maxSL|MinimumSL|MaximumSL', xml)[:5]}")
print(f"PT min-max: {re.findall(r'PTmin|PTmax|minPT|maxPT|MinimumPT|MaximumPT', xml)[:5]}")
print(f"Trades/mes min: {re.findall(r'AvgTradesPerMonth[^>]*>([^<]+)', xml)[:3]}")
print(f"PF minimo: {re.findall(r'ProfitFactor[^>]*>([^<]+)|Numeric-Value value=\"([\d.]+)\"[^/]*/>[^<]*</Right', xml)[:3]}")
print(f"Indicadores activos: {xml.count('use=\"true\"')} de {xml.count('<Block ')}")
print(f"Max estrategias: {re.findall(r'maxStrategies|MaxStrategies|databankSize', xml)[:3]}")
print(f"Modo continuo: {re.findall(r'restartWhenFinished|StartAgainWhenFinished|continueWhenFinished', xml)[:3]}")
print(f"IS periodo: {re.findall(r'dateFrom|dateTo', xml)[:4]}")