Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Iniciando Auto-Captions Animated Service (CapCut Style)" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

Set-Location $PSScriptRoot

Write-Host "`n[1/2] Verificando dependencias..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "`n[2/2] Iniciando servidor en http://localhost:8000 ..." -ForegroundColor Yellow
Write-Host "Swagger UI: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "========================================================`n" -ForegroundColor Green

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
