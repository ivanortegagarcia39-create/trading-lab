PYTHONUTF8=1 python -c "
import zipfile, shutil, io, re

cfx = r'D:\user\projects\Optimizer\project.cfx'
shutil.copy2(cfx, cfx + '.bak_build12')

with zipfile.ZipFile(cfx) as z:
    task = z.read('Optimize-Task1.xml').decode()
    config = z.read('config.xml').decode()

# Reemplazar XAUUSD por EURUSD
for old, new in [
    ('XAUUSD_M1_dukas', 'EURUSD_M1_dukas'),
    ('XAUUSD_ftmo', 'EURUSD_ftmo'),
    ('XAUUSD_dukascopy', 'EURUSD_dukascopy'),
    ('uSymbol=\"XAUUSD\"', 'uSymbol=\"EURUSD\"'),
    ('uSymbolName=\"XAUUSD\"', 'uSymbolName=\"EURUSD\"'),
    ('defaultSpread=\"60\"', 'defaultSpread=\"1.0\"'),
    ('defaultSpread=\"60.0\"', 'defaultSpread=\"1.0\"'),
    ('defaultSpread=\"0.3\"', 'defaultSpread=\"1.0\"'),
    ('defaultSlippage=\"2.0\"', 'defaultSlippage=\"0.5\"'),
    ('slippage=\"2\"', 'slippage=\"0.5\"'),
]:
    task = task.replace(old, new)

buf = io.BytesIO()
with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zout:
    zout.writestr('config.xml', config)
    zout.writestr('Optimize-Task1.xml', task)

with open(cfx, 'wb') as f:
    f.write(buf.getvalue())

with zipfile.ZipFile(cfx) as z:
    t = z.read('Optimize-Task1.xml').decode()

print(f'XAUUSD residual: {t.count(\"XAUUSD\")}')
print(f'EURUSD presente: {t.count(\"EURUSD\")}')
print(f'Spreads: {re.findall(r\"defaultSpread=.([^.]+).\", t)}')
print(f'Slippages: {re.findall(r\"defaultSlippage=.([^.]+).\", t)}')
print('OK' if t.count('XAUUSD') == 0 else 'FALLO')
"