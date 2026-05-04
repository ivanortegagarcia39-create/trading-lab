@echo off
REM ============================================================
REM  TradingLab -- launch-build.bat
REM  Uso: launch-build.bat [BUILD] [ACTIVO] [SPREAD]
REM  Ejemplo: launch-build.bat 11 XAUUSD 30
REM ============================================================

setlocal

set BUILD=%1
set ACTIVO=%2
set SPREAD=%3

if "%BUILD%"=="" set BUILD=11
if "%ACTIVO%"=="" set ACTIVO=XAUUSD
if "%SPREAD%"=="" set SPREAD=30

set REPO=C:\Users\ivano\trading-lab
set SQ_EXE=D:\StrategyQuantX_nocheck.exe
set PYTHON=python

echo.
echo ============================================================
echo   TradingLab ^| Build %BUILD% ^| %ACTIVO% ^| Spread %SPREAD% pips
echo ============================================================
echo.

cd /d %REPO%

echo [1/6] Actualizando repositorio...
git pull origin main
if errorlevel 1 ( echo [ERROR] git pull fallo. & pause & exit /b 1 )
echo       OK

echo [2/6] Cerrando StrategyQuant si esta abierto...
tasklist /FI "IMAGENAME eq StrategyQuantX_nocheck.exe" 2>NUL | find /I "StrategyQuantX_nocheck.exe" >NUL
if not errorlevel 1 (
    taskkill /IM StrategyQuantX_nocheck.exe /F >NUL 2>&1
    timeout /t 4 /nobreak >NUL
    echo       OK -- SQ cerrado
) else ( echo       SQ no estaba abierto )

echo [3/6] Extrayendo CFX actual...
%PYTHON% -c "import zipfile,os; os.makedirs(r'D:/user/projects/Builder/extracted',exist_ok=True); zipfile.ZipFile(r'D:/user/projects/Builder/project.cfx').extractall(r'D:/user/projects/Builder/extracted'); print('OK')"
if errorlevel 1 ( echo [ERROR] No se pudo extraer CFX. & pause & exit /b 1 )
echo       OK

echo [4/6] Generando CFX para Build %BUILD% %ACTIVO% spread %SPREAD%...
%PYTHON% scripts\sq-project-generator.py --build %BUILD% --activo %ACTIVO% --spread-real %SPREAD%
if errorlevel 1 ( echo [ERROR] Fallo al generar CFX. & pause & exit /b 1 )
echo       OK

echo [5/6] Validando configuracion...
%PYTHON% scripts\sq-project-generator.py --validate --build %BUILD%

echo [6/6] Abriendo StrategyQuant...
if exist "%SQ_EXE%" ( start "" "%SQ_EXE%" & echo       OK ) else ( echo [WARN] Abre SQ manualmente )

echo.
echo ============================================================
echo   Build %BUILD% listo. Unico paso manual: Builder > START
echo ============================================================
echo.
pause
