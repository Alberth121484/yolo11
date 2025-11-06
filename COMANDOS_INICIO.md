# 🚀 Comandos para Iniciar Backend y Frontend

## ⚠️ IMPORTANTE: Dos Terminales Separadas

Necesitas **2 terminales abiertas** al mismo tiempo:
- Terminal 1: Backend (Python/FastAPI)
- Terminal 2: Frontend (React/Vite)

---

## 🔴 DETENER SERVICIOS ACTUALES

Si ya están corriendo, presiona en cada terminal:
```
Ctrl + C
```

---

## 🟢 TERMINAL 1: BACKEND

### Abrir Terminal PowerShell:
1. Presiona `Win + R`
2. Escribe: `powershell`
3. Enter

### Comandos:
```powershell
# Ir a la carpeta del backend
cd d:\IA\modelos\yolo12\backend

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Si da error de permisos, ejecuta PRIMERO:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Iniciar backend
python -m app.main
```

### Lo que verás (sin errores):
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Backend corriendo en:
http://localhost:8000

---

## 🟢 TERMINAL 2: FRONTEND

### Abrir OTRA Terminal PowerShell:
1. Presiona `Win + R`
2. Escribe: `powershell`
3. Enter

### Comandos:
```powershell
# Ir a la carpeta del frontend
cd d:\IA\modelos\yolo12\frontend

# Iniciar frontend (Vite)
npm run dev
```

### Lo que verás (sin errores):
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
➜  press h + enter to show help
```

### Frontend corriendo en:
http://localhost:3000

---

## 📋 VERIFICACIÓN RÁPIDA

### Backend OK:
- ✅ Dice "Uvicorn running on http://127.0.0.1:8000"
- ✅ No hay errores rojos
- ✅ Puedes abrir http://localhost:8000/docs

### Frontend OK:
- ✅ Dice "Local: http://localhost:3000/"
- ✅ No hay errores rojos
- ✅ Puedes abrir http://localhost:3000

---

## 🐛 ERRORES COMUNES Y SOLUCIONES

### Backend: "ModuleNotFoundError"
```
❌ ModuleNotFoundError: No module named 'app'
```
**Solución:**
```powershell
# Asegúrate de estar en backend/
cd d:\IA\modelos\yolo12\backend

# Y que el venv esté activado (debes ver (venv) al inicio)
.\venv\Scripts\Activate.ps1
```

### Backend: "Address already in use"
```
❌ ERROR: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)
```
**Solución:**
```powershell
# El puerto 8000 ya está en uso, matar el proceso:
Get-Process -Name python | Stop-Process -Force

# Luego reintentar
python -m app.main
```

### Frontend: "npm: command not found"
```
❌ npm : El término 'npm' no se reconoce...
```
**Solución:**
```powershell
# Instalar Node.js primero
# Descarga desde: https://nodejs.org/
# Después de instalar, cierra y abre nueva terminal
```

### Frontend: "EADDRINUSE: address already in use"
```
❌ Port 3000 is in use
```
**Solución:**
```powershell
# Matar proceso en puerto 3000:
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process -Force

# O usar otro puerto:
npm run dev -- --port 3001
```

---

## 🔄 REINICIAR SERVICIOS

### Para aplicar cambios en Backend:
```powershell
# En la terminal del backend:
Ctrl + C
python -m app.main
```

### Para aplicar cambios en Frontend:
```powershell
# En la terminal del frontend:
Ctrl + C
npm run dev
```

**Nota:** El frontend con Vite tiene hot-reload, normalmente NO necesitas reiniciar.

---

## 📊 MONITOREAR LOGS

### Backend (Terminal 1):
Verás logs en tiempo real:
```
INFO: Starting training with yolo11n.pt
INFO: Job abc123: Progress callback - Epoch 1/50
INFO: Job abc123: Epoch 1/50 - mAP: 0.1234
```

### Frontend (Terminal 2):
Verás requests y hot-reload:
```
10:30:15 AM [vite] page reload index.html
10:30:20 AM [vite] hmr update /src/pages/Training.jsx
```

### Navegador (DevTools):
```
F12 → Console
```
Verás logs del JavaScript:
```
Training page mounted
Fetching trainings...
Training list updated: 3 jobs
```

---

## 🎯 WORKFLOW RECOMENDADO

1. **Abrir 2 Terminales**
2. **Terminal 1: Iniciar Backend**
   ```
   cd d:\IA\modelos\yolo12\backend
   .\venv\Scripts\Activate.ps1
   python -m app.main
   ```
3. **Terminal 2: Iniciar Frontend**
   ```
   cd d:\IA\modelos\yolo12\frontend
   npm run dev
   ```
4. **Navegador: Abrir App**
   ```
   http://localhost:3000
   ```
5. **Ver Logs en Ambas Terminales**

---

## 💡 TIPS

- **No cierres las terminales** mientras uses la app
- **Backend:** Logs más importantes aquí (errores de Python, YOLO, etc.)
- **Frontend:** Errores de JavaScript/React aquí
- **Navegador:** F12 para ver errores del cliente
- **Hot Reload:** Frontend se actualiza solo, backend NO

---

## 🚨 SI TODO FALLA

### Reset Completo:

```powershell
# Matar todos los procesos Python
Get-Process -Name python | Stop-Process -Force

# Matar procesos Node
Get-Process -Name node | Stop-Process -Force

# Esperar 5 segundos
Start-Sleep -Seconds 5

# Iniciar de nuevo
# Terminal 1:
cd d:\IA\modelos\yolo12\backend
.\venv\Scripts\Activate.ps1
python -m app.main

# Terminal 2:
cd d:\IA\modelos\yolo12\frontend
npm run dev
```

---

## ✅ CHECKLIST DE INICIO

Antes de reportar errores, verifica:

- [ ] 2 terminales abiertas
- [ ] Backend en d:\IA\modelos\yolo12\backend
- [ ] Frontend en d:\IA\modelos\yolo12\frontend
- [ ] Venv activado en backend (ves "(venv)")
- [ ] Backend dice "Uvicorn running"
- [ ] Frontend dice "Local: http://localhost:3000"
- [ ] No hay errores rojos en ninguna terminal
- [ ] Navegador puede abrir ambas URLs

---

**¡Listo para iniciar!** 🚀
