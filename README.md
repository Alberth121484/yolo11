# 🚀 YOLO11 - Sistema Completo de Detección de Objetos con IA

Sistema profesional de detección de objetos usando YOLO11 con interfaz web de administración completa.

## 📋 Descripción

Este proyecto es un sistema completo que combina:
- **Backend FastAPI**: API REST robusta para inferencia y entrenamiento de modelos YOLO11
- **Frontend React**: Interfaz web moderna y responsive para administración
- **YOLO11**: Última versión de Ultralytics para detección de objetos en tiempo real

## ✨ Características Principales

### Backend (FastAPI)
- ✅ **Inferencia en tiempo real**: Detecta objetos en imágenes individuales o por lotes
- ✅ **Entrenamiento personalizado**: Entrena tus propios modelos con datasets personalizados
- ✅ **Gestión de datasets**: Crea, administra y valida datasets de entrenamiento
- ✅ **Gestión de modelos**: Administra, exporta y valida modelos entrenados
- ✅ **Autenticación OAuth2**: Login con Google, GitHub y Facebook
- ✅ **Login tradicional**: Email y contraseña con JWT
- ✅ **Almacenamiento en nube**: Integración con Google Drive y OneDrive
- ✅ **API RESTful completa**: Documentación interactiva con Swagger/ReDoc
- ✅ **Soporte multi-GPU**: Entrenamiento optimizado con CUDA
- ✅ **Background tasks**: Entrenamientos asíncronos sin bloquear la API

### Frontend (React + Vite)
- ✅ **Dashboard interactivo**: Vista general con estadísticas y accesos rápidos
- ✅ **Autenticación completa**: Login con OAuth o credenciales
- ✅ **Configuración de almacenamiento**: Gestiona almacenamiento local o en nube
- ✅ **Anotación de imágenes**: Herramienta integrada para etiquetar objetos
- ✅ **Drag & Drop**: Sube imágenes arrastrándolas
- ✅ **Monitoreo en tiempo real**: Visualiza el progreso de entrenamientos
- ✅ **Responsive**: Funciona en desktop, tablet y móvil
- ✅ **UI Moderna**: Diseño profesional con TailwindCSS
- ✅ **Notificaciones**: Feedback visual de todas las acciones

## 🛠️ Tecnologías

### Backend
- Python 3.8+
- FastAPI
- Ultralytics YOLO11
- PyTorch
- OpenCV
- SQLAlchemy (para futuras mejoras)

### Frontend
- React 18
- Vite
- TailwindCSS
- React Router
- Axios
- Lucide Icons

## 📦 Instalación Rápida

### Requisitos Previos
- Python 3.8+
- Node.js 16+
- CUDA 11.8+ (opcional, para GPU)
- 8GB RAM mínimo (16GB recomendado)

### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/yolo11.git
cd yolo11
```

### 2. Configurar Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate

# Activar entorno (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy .env.example .env
# Edita .env con tu configuración
```

### 3. Configurar Frontend

```bash
cd ../frontend

# Instalar dependencias
npm install
```

## 🚀 Iniciar el Sistema

### Opción 1: Manualmente

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # Windows
# o
source venv/bin/activate  # Linux/Mac

python -m app.main
# o
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Accede a:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentación API: http://localhost:8000/docs

**Credenciales de prueba:**
- Email: `admin@admin.com`
- Password: `admin123`

### Opción 2: Scripts automatizados

**Windows:**
```bash
# Iniciar todo
.\start.bat

# Solo backend
.\start-backend.bat

# Solo frontend
.\start-frontend.bat
```

**Linux/Mac:**
```bash
# Dar permisos
chmod +x start.sh start-backend.sh start-frontend.sh

# Iniciar todo
./start.sh

# Solo backend
./start-backend.sh

# Solo frontend
./start-frontend.sh
```

## 📚 Guías de Uso

### 1. Detectar Objetos en Imágenes

1. Ve a **Inferencia** en el menú
2. Arrastra una o más imágenes al área de carga
3. Ajusta los parámetros (modelo, confidence, IoU)
4. Haz clic en "Detectar Objetos"
5. Visualiza los resultados con las detecciones

### 2. Crear y Entrenar un Modelo Personalizado

#### Paso 1: Crear Dataset
1. Ve a **Datasets** > **Crear Dataset**
2. Nombre: `mi_dataset`
3. Clases: `perro, gato, pajaro` (separadas por comas)
4. Haz clic en **Crear**

#### Paso 2: Subir Imágenes
1. Selecciona tu dataset creado
2. Haz clic en "Agregar Imágenes"
3. Selecciona el split (train/val/test)
4. Sube las imágenes

#### Paso 3: Anotar Imágenes
Puedes anotar manualmente o usar herramientas como:
- [LabelImg](https://github.com/heartexlabs/labelImg)
- [CVAT](https://www.cvat.ai/)
- [Roboflow](https://roboflow.com/)

Exporta en formato YOLO y coloca las anotaciones en la carpeta labels correspondiente.

#### Paso 4: Entrenar Modelo
1. Ve a **Entrenamiento** > **Nuevo Entrenamiento**
2. Selecciona tu dataset
3. Elige el tamaño del modelo (nano recomendado para empezar)
4. Configura epochs (100 para empezar)
5. Haz clic en **Iniciar Entrenamiento**
6. Monitorea el progreso en tiempo real

### 3. Usar tu Modelo Entrenado

1. Una vez completado el entrenamiento, el modelo estará disponible en **Modelos**
2. Ve a **Inferencia**
3. Selecciona tu modelo personalizado
4. Sube imágenes y detecta objetos

### 4. Configurar Autenticación OAuth (Opcional)

Si deseas usar login con Google, GitHub o Facebook:

1. Lee la guía completa en `CONFIGURACION_OAUTH.md`
2. Crea aplicaciones OAuth en cada plataforma
3. Configura las credenciales en `backend/.env`
4. Los usuarios podrán iniciar sesión con redes sociales

### 5. Configurar Almacenamiento en Nube (Opcional)

Para sincronizar datasets con Google Drive o OneDrive:

1. Inicia sesión en la aplicación
2. Ve a **Configuración** > **Almacenamiento**
3. Selecciona el proveedor (Google Drive / OneDrive)
4. Conecta tu cuenta
5. Guarda la configuración

Tus datasets se sincronizarán automáticamente con la nube.

## 📖 Documentación Completa

### API Endpoints

#### Inferencia
```bash
POST /api/v1/predict
POST /api/v1/predict/batch
POST /api/v1/predict/url
GET  /api/v1/result/{filename}
```

#### Entrenamiento
```bash
POST   /api/v1/train
GET    /api/v1/train
GET    /api/v1/train/{job_id}
DELETE /api/v1/train/{job_id}
GET    /api/v1/train/{job_id}/metrics
POST   /api/v1/train/{job_id}/resume
```

#### Datasets
```bash
POST   /api/v1/datasets
GET    /api/v1/datasets
GET    /api/v1/datasets/{name}
DELETE /api/v1/datasets/{name}
POST   /api/v1/datasets/{name}/images
POST   /api/v1/datasets/{name}/images/annotated
POST   /api/v1/datasets/{name}/split
GET    /api/v1/datasets/{name}/validate
```

#### Modelos
```bash
GET    /api/v1/models
GET    /api/v1/models/{name}
GET    /api/v1/models/{name}/download
POST   /api/v1/models/upload
DELETE /api/v1/models/{name}
POST   /api/v1/models/{name}/export
POST   /api/v1/models/{name}/validate
```

#### Autenticación
```bash
POST   /api/v1/auth/login/credentials     # Login con email/password
GET    /api/v1/auth/login/{provider}      # Login OAuth (google/github/facebook)
GET    /api/v1/auth/callback/{provider}   # Callback OAuth
GET    /api/v1/auth/me                    # Obtener usuario actual
POST   /api/v1/auth/logout                # Cerrar sesión
```

#### Configuración
```bash
GET    /api/v1/config/storage             # Obtener config de almacenamiento
POST   /api/v1/config/storage             # Guardar config de almacenamiento
POST   /api/v1/config/storage/test        # Probar conexión
DELETE /api/v1/config/storage             # Resetear a local
GET    /api/v1/config/training-defaults   # Configuración de entrenamiento
POST   /api/v1/config/training-defaults   # Guardar defaults
```

### Ejemplos con Python

```python
import requests

# Detectar objetos
url = "http://localhost:8000/api/v1/predict"
files = {"file": open("imagen.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())

# Crear dataset
url = "http://localhost:8000/api/v1/datasets"
data = {
    "name": "productos",
    "class_names": ["manzana", "naranja", "platano"]
}
response = requests.post(url, json=data)

# Iniciar entrenamiento
url = "http://localhost:8000/api/v1/train"
data = {
    "dataset_name": "productos",
    "model_size": "n",
    "epochs": 50
}
response = requests.post(url, json=data)
```

## 🏗️ Estructura del Proyecto

```
yolo11/
├── backend/                    # Backend FastAPI
│   ├── app/
│   │   ├── api/v1/            # Endpoints de la API
│   │   │   ├── auth.py        # Autenticación
│   │   │   ├── config.py      # Configuración
│   │   │   ├── datasets.py    # Datasets
│   │   │   ├── inference.py   # Inferencia
│   │   │   ├── training.py    # Entrenamiento
│   │   │   └── models.py      # Modelos
│   │   ├── auth/              # Módulo de autenticación
│   │   │   ├── oauth.py       # OAuth2
│   │   │   └── jwt.py         # JWT tokens
│   │   ├── models/            # Modelos de datos
│   │   │   └── user.py        # Usuario y sesión
│   │   ├── services/          # Lógica de negocio
│   │   │   ├── storage/       # Adaptadores de almacenamiento
│   │   │   │   ├── base.py
│   │   │   │   ├── local.py
│   │   │   │   ├── google_drive.py
│   │   │   │   ├── onedrive.py
│   │   │   │   └── factory.py
│   │   │   ├── training.py
│   │   │   └── inference.py
│   │   ├── config.py          # Configuración
│   │   ├── schemas.py         # Modelos Pydantic
│   │   └── main.py            # Aplicación principal
│   ├── datasets/              # Datasets de entrenamiento
│   ├── models/                # Modelos .pt
│   ├── uploads/               # Imágenes subidas
│   ├── results/               # Resultados de inferencia
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── frontend/                  # Frontend React
│   ├── src/
│   │   ├── components/       # Componentes reutilizables
│   │   ├── context/          # React Context
│   │   │   └── AuthContext.jsx
│   │   ├── pages/            # Páginas principales
│   │   │   ├── Login.jsx
│   │   │   ├── AuthCallback.jsx
│   │   │   ├── SettingsNew.jsx
│   │   │   ├── Annotate.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Inference.jsx
│   │   │   ├── Training.jsx
│   │   │   ├── Datasets.jsx
│   │   │   └── Models.jsx
│   │   ├── lib/              # Utilidades y API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── README.md
│
├── CONFIGURACION_OAUTH.md     # Guía de configuración OAuth
├── IMPLEMENTACION_COMPLETA.md # Documentación técnica
├── .gitignore
└── README.md                  # Este archivo
```

## 🔒 Seguridad

Para producción:

1. **Cambiar SECRET_KEY** en `.env`
2. **Configurar CORS** en `backend/app/main.py`
3. **Agregar autenticación** (JWT, OAuth2)
4. **Usar HTTPS**
5. **Rate limiting** para endpoints
6. **Validar todos los inputs**
7. **Limitar tamaño de archivos**

## 🐛 Solución de Problemas

### Backend no inicia
```bash
# Verificar instalación de dependencias
pip install -r requirements.txt

# Verificar puerto disponible
netstat -ano | findstr :8000
```

### Frontend no conecta al backend
```bash
# Verificar CORS en backend
# Verificar URL en frontend/src/lib/api.js
# Verificar que backend esté corriendo
```

### Error CUDA out of memory
```bash
# Reducir batch size en entrenamiento
# Usar modelo más pequeño (nano o small)
# Cerrar otras aplicaciones que usen GPU
```

### Modelo no descarga
```bash
# Verificar conexión a internet
# Modelos se descargan automáticamente la primera vez
# Espera unos minutos en la primera ejecución
```

## 📊 Modelos YOLO11

| Modelo | Tamaño | Parámetros | mAP50-95 | Velocidad | Uso Recomendado |
|--------|--------|------------|----------|-----------|-----------------|
| YOLOv11n | 6 MB | 2.6M | 39.5% | 1.5ms | Dispositivos edge, tiempo real |
| YOLOv11s | 19 MB | 9.4M | 47.0% | 2.5ms | Balance velocidad/precisión |
| YOLOv11m | 40 MB | 20.1M | 51.5% | 4.7ms | Aplicaciones generales |
| YOLOv11l | 53 MB | 25.3M | 53.4% | 6.2ms | Alta precisión |
| YOLOv11x | 110 MB | 56.9M | 54.7% | 11.3ms | Máxima precisión |

## 💡 Mejores Prácticas

### Preparación de Datos
- Mínimo 100 imágenes por clase (300+ recomendado)
- Balance entre clases
- Variedad de ángulos, iluminación y contextos
- Anotaciones precisas y consistentes
- Split: 70% train, 20% val, 10% test

### Entrenamiento
- Empezar con modelo pre-entrenado (pretrained=true)
- Comenzar con pocos epochs (50-100) y aumentar según necesidad
- Usar early stopping (patience=50)
- Monitorear métricas de validación
- Guardar checkpoints regularmente

### Inferencia
- Ajustar confidence según tu caso de uso
- Usar batch processing para múltiples imágenes
- Cachear modelos en memoria
- Usar el modelo más pequeño que cumpla tus requisitos

## 🤝 Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto usa Ultralytics YOLO11, licenciado bajo AGPL-3.0.

## 🙏 Créditos

- [Ultralytics YOLO11](https://docs.ultralytics.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [TailwindCSS](https://tailwindcss.com/)

## 📧 Soporte

Para preguntas o problemas:
- 📖 Revisa la documentación completa
- 🐛 Reporta bugs en Issues
- 💬 Discusiones en Discussions

---

**¡Construido con ❤️ usando YOLO11, FastAPI y React!**

🌟 Si te gusta este proyecto, dale una estrella en GitHub
