Necesito que parchees el Build-Task1.xml dentro del CFX 
D:/user/projects/Builder/project.cfx para corregir 3 nodos 
que apuntan a EURUSD cuando deberían apuntar a XAUUSD.

Los cambios exactos son:
1. <Chart symbol="EURUSD_M1_dukas" → <Chart symbol="XAUUSD_M1_dukas"
2. <Symbol name="EURUSD_M1_dukas" ... uSymbol="EURUSD" broker="3"> 
   → name="XAUUSD_M1_dukas" ... uSymbol="XAUUSD" broker="8">
   Y dentro: <InstrumentInfo instrument="EURUSD_dukascopy" 
   → instrument="XAUUSD_ftmo" con los parámetros correctos de XAUUSD
3. En <Instruments>: eliminar el nodo EURUSD_dukascopy residual

Hazlo con Python leyendo el CFX como ZIP, modificando el XML 
en memoria, y reempaquetando. Haz backup del CFX original antes.

Luego verifica con:
import zipfile, re
t = zipfile.ZipFile(r'D:/user/projects/Builder/project.cfx').read('Build-Task1.xml').decode()
print(re.findall(r'EURUSD', t)[:5])
print(re.findall(r'XAUUSD', t)[:5])
El resultado debe tener 0 ocurrencias de EURUSD y varias de XAUUSD.

También actualiza scripts/sq-project-generator.py para que 
aplique estos patches automáticamente en futuros builds.

Cuando termines: git add -A && git commit -m "fix: patch CFX EURUSD->XAUUSD datos backtest + fix sq-project-generator" && git push origin main