import subprocess
import time
import glob
import sys
import importlib.util
import requests
from pathlib import Path

_tg_path = Path(__file__).parent / "telegram-notifier.py"
_spec = importlib.util.spec_from_file_location("telegram_notifier", _tg_path)
tg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tg)

# 1. Arrancar TradingLab API
proc1 = subprocess.Popen(
    ['python', 'scripts/tradinglab-api.py'],
    cwd=r'C:\Users\ivano\trading-lab'
)
time.sleep(5)
r = requests.get('http://localhost:8765/health')
print(f"API: {r.json()}")

# 2. Arrancar N8N
proc2 = subprocess.Popen(
    [r'C:\Users\ivano\AppData\Roaming\npm\n8n.cmd', 'start'],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    shell=True
)
time.sleep(20)
r2 = requests.get('http://localhost:5678')
print(f"N8N: {r2.status_code}")

# 3. Relanzar Build via sqcli
subprocess.Popen(
    [r'D:\sqcli.exe', '-project', 'action=start', 'name=Builder'],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
print("Builder lanzado via sqcli")

# 4. Verificar arranque de sqcli y Builder
time.sleep(30)

tasklist = subprocess.check_output(['tasklist'], text=True, errors='ignore')
sqcli_ok = 'sqcli.exe' in tasklist.lower()

sqx_files = glob.glob(r'D:\user\projects\Builder\Results\*.sqx')
sqx_ok = len(sqx_files) >= 1

if sqcli_ok and sqx_ok:
    tg.send_info(f"Startup OK — sqcli activo, {len(sqx_files)} .sqx en Builder/Results")
elif sqcli_ok and not sqx_ok:
    tg.send_info("Startup parcial — sqcli activo pero sin .sqx en Builder/Results aún")
else:
    tg.send_error(f"Startup FALLO — sqcli no detectado en procesos")
