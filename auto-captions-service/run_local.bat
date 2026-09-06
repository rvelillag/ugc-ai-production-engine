@echo off
title Auto-Captions Animated Service (CapCut Style)
echo ========================================================
echo   Iniciando Auto-Captions Animated Service
echo ========================================================
cd /d "%~dp0"

echo [1/3] Verificando dependencias...
pip install -r requirements.txt

echo [2/3] Iniciando servidor FastAPI en http://localhost:8000 ...
echo Documentacion interactiva disponible en: http://localhost:8000/docs
echo ========================================================

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
