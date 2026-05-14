$env:PYTHONUTF8=1; python -c "
import zipfile, re
from datetime import datetime, timezone

with zipfile.ZipFile(r'D:/user/projects/Builder/project.cfx') as z:
    xml = z.read('Build-Task1.xml').decode()

print('=== VERIFICACION BUILD 12 EURUSD ===')
print(f'Simbolo: {re.findall(chr(34)+r\"symbol=\"+chr(34)+r\"([^\"]+)\"', xml)[:3]}')
print(f'Spread: {re.findall(r\"defaultSpread=\"+chr(34)+r\"([^\"]+)\"+chr(34), xml)[:3]}')
print(f'Capital: {re.findall(r\"<InitialCapital>(\d+)</InitialCapital>\", xml)}')
print(f'MM activo: {re.findall(r\"<Method type=\"+chr(34)+r\"([^\"]+)\"+chr(34)+r\" use=\"+chr(34)+r\"true\"+chr(34)+r\">\", xml)}')
print(f'XAUUSD residual: {xml.count(chr(88)+chr(65)+chr(85)+chr(85)+chr(83)+chr(68))}')
print(f'EURUSD presente: {xml.count(\"EURUSD\")}')
dates = re.findall(r'dateTo=\"(\d+)\"', xml)
for d in dates[:3]:
    if int(d) > 0:
        print(f'dateTo: {datetime.fromtimestamp(int(d)/1000, tz=timezone.utc).strftime(\"%Y-%m-%d\")}')
"