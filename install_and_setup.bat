@echo off
setlocal enabledelayedexpansion
title Instalador UGC Production Engine - DTC
chcp 65001 >nul

echo ========================================================
echo   INSTALADOR AUTOMATICO - UGC PRODUCTION ENGINE (AI)
echo ========================================================
echo.

:: 1. Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no se encuentra en el PATH.
    echo Por favor instala Python 3.10 o superior desde https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Verificando version de Python...
python -c "import sys; print('Python detectado:', sys.version.split()[0])"
echo.

:: 2. Actualizar pip e instalar dependencias
echo [2/4] Instalando paquetes y librerias requeridas (Whisper, FFmpeg, PyTorch, PyYAML)...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Hubo un problema al instalar los paquetes de requirements.txt.
    pause
    exit /b 1
)
echo.

:: 3. Inicializar FFmpeg estatico
echo [3/4] Inicializando y verificando binarios de FFmpeg...
python -c "import static_ffmpeg; static_ffmpeg.add_paths(); print('FFmpeg configurado correctamente')"
echo.

:: 4. Validacion del sistema
echo [4/4] Verificando estructura de plantillas y modulos...
python -c "
from pathlib import Path
t = Path('_CREATOR_TEMPLATE')
assert t.exists(), 'Plantilla _CREATOR_TEMPLATE no encontrada'
print('Estructura de plantillas verificada exitosamente.')
"
echo.

echo ========================================================
echo   ¡INSTALACION Y CONFIGURACION COMPLETADAS CON EXITO!
echo ========================================================
echo.
echo Para abrir el menu principal interactivo ejecuta: ugc_studio.bat
echo.
pause
