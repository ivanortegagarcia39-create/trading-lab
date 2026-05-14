import subprocess
import time
import requests

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
