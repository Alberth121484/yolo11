@echo off
echo ========================================
echo   Iniciando Backend YOLO11 API
echo ========================================
echo.

cd backend

echo Activando entorno virtual...
call venv\Scripts\activate

echo.
echo Iniciando servidor FastAPI...
echo Backend estara disponible en: http://localhost:8000
echo Documentacion: http://localhost:8000/docs
echo.

python -m app.main

pause
