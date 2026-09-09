@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo   UGC AI PRODUCTION ENGINE -- ACTUALIZADOR DE 1 CLIC
echo ========================================================
echo.
echo [1/2] Descargando las ultimas mejoras y skills desde GitHub...
git pull origin main

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Hubo un problema al ejecutar git pull.
    echo Por favor verifica tu conexion a internet o conflictos de git.
    pause
    exit /b 1
)

echo.
echo [2/2] Verificando dependencias de Python...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    python -m pip install -q --upgrade pip
    pip install -q -r requirements.txt
) else (
    python -m pip install -q --upgrade pip
    pip install -q -r requirements.txt
)

echo.
echo ========================================================
echo   ACTUALIZACION COMPLETADA CON EXITO!
echo   - Skills actualizadas con el estandar JSON-First 1:1
echo   - Modulo AudioCadenceAnalyzer y Cover Headline integrados
echo   - Coreografia I2V y Checkpoints activados
echo ========================================================
echo.
pause
