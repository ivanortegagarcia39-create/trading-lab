@echo off
echo Creando tareas de inicio automatico...

schtasks /create /tn "TradingLab-N8N" ^
  /tr "\"C:\Users\ivano\AppData\Roaming\npm\n8n.cmd\" start" ^
  /sc onlogon /ru ivano /f
if %errorlevel%==0 (echo [OK] TradingLab-N8N creada) else (echo [ERROR] TradingLab-N8N)

schtasks /create /tn "TradingLab-API" ^
  /tr "python \"C:\Users\ivano\trading-lab\scripts\tradinglab-api.py\"" ^
  /sc onlogon /ru ivano /f
if %errorlevel%==0 (echo [OK] TradingLab-API creada) else (echo [ERROR] TradingLab-API)

echo.
echo Verificando:
schtasks /query /tn "TradingLab-N8N" /fo list 2>nul | findstr "Nombre\|Estado"
schtasks /query /tn "TradingLab-API" /fo list 2>nul | findstr "Nombre\|Estado"
pause
