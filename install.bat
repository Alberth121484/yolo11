@echo off
echo ========================================
echo   Instalacion Completa - YOLO11 System
echo ========================================
echo.

echo [1/4] Verificando Python...
python --version
if errorlevel 1 (
    echo ERROR: Python no esta instalado
    echo Por favor instala Python 3.8+ desde python.org
    pause
    exit /b 1
)

echo.
echo [2/4] Verificando Node.js...
node --version
if errorlevel 1 (
    echo ERROR: Node.js no esta instalado
    echo Por favor instala Node.js desde nodejs.org
    pause
    exit /b 1
)

echo.
echo [3/4] Instalando Backend...
cd backend

echo Creando entorno virtual...
python -m venv venv

echo Activando entorno virtual...
call venv\Scripts\activate

echo Instalando dependencias de Python...
pip install --upgrade pip
pip install -r requirements.txt

echo Copiando archivo de configuracion...
if not exist .env (
    copy .env.example .env
    echo IMPORTANTE: Edita backend\.env con tu configuracion
)

cd ..

echo.
echo [4/4] Instalando Frontend...
cd frontend

echo Instalando dependencias de Node.js...
call npm install

cd ..

echo.
echo ========================================
echo   Instalacion Completada!
echo ========================================
echo.
echo Proximos pasos:
echo 1. Edita backend\.env con tu configuracion
echo 2. Ejecuta start-backend.bat en una terminal
echo 3. Ejecuta start-frontend.bat en otra terminal
echo 4. Abre http://localhost:3000 en tu navegador
echo.
echo Documentacion completa: README.md
echo.

pause
