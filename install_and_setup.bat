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

echo [1/5] Verificando version de Python...
python -c "import sys; print('Python detectado:', sys.version.split()[0])"
echo.

:: 2. Actualizar pip e instalar dependencias
echo [2/5] Instalando paquetes y librerias requeridas (Whisper, FFmpeg, PyTorch, PyYAML)...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Hubo un problema al instalar los paquetes de requirements.txt.
    pause
    exit /b 1
)
echo.

:: 3. Inicializar FFmpeg estatico
echo [3/5] Inicializando y verificando binarios de FFmpeg...
python -c "import static_ffmpeg; static_ffmpeg.add_paths(); print('FFmpeg configurado correctamente')"
echo.

:: 4. Validacion del sistema
echo [4/5] Verificando estructura de plantillas y modulos...
python -c "
from pathlib import Path
t = Path('_CREATOR_TEMPLATE')
assert t.exists(), 'Plantilla _CREATOR_TEMPLATE no encontrada'
print('Estructura de plantillas verificada exitosamente.')
"
echo.

:: 5. Registrar marca de instalacion completa
echo [5/6] Registrando marca de instalacion completa...
python -c "
import hashlib
from pathlib import Path
from datetime import date
req_hash = hashlib.sha256(Path('requirements.txt').read_bytes()).hexdigest()
Path('.setup_complete').write_text(f'{date.today().isoformat()} {req_hash}\n', encoding='utf-8')
print('Marca de instalacion creada: .setup_complete')
"
echo.

:: 6. Registrar comando global 'ugc' en el PATH de Windows
echo [6/6] Configurando comando global 'ugc' en el sistema...
python ugc.py setup-path
echo.

echo ========================================================
echo   ¡INSTALACION Y CONFIGURACION COMPLETADAS CON EXITO!
echo ========================================================
echo.
echo Ahora puedes ejecutar 'ugc' desde cualquier carpeta o terminal.
echo Para abrir el menu interactivo tradicional ejecuta: ugc_studio.bat
echo.
pause
