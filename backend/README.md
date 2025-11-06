# YOLO11 API - Backend

Sistema completo de API REST para detección de objetos con YOLO11, incluyendo entrenamiento de modelos personalizados.

## 🚀 Características

- **Inferencia en tiempo real**: Detecta objetos en imágenes usando modelos YOLO11
- **Entrenamiento personalizado**: Entrena tus propios modelos con datasets personalizados
- **Gestión de datasets**: Crea, administra y valida datasets de entrenamiento
- **Gestión de modelos**: Administra, exporta y valida modelos entrenados
- **Autenticación OAuth2**: Login con Google, GitHub y Facebook
- **Login tradicional**: Email y contraseña con JWT tokens
- **Almacenamiento en nube**: Integración con Google Drive y OneDrive
- **API RESTful completa**: Documentación interactiva con FastAPI
- **Soporte multi-GPU**: Entrenamiento optimizado con CUDA
- **Formatos de imagen**: JPG, PNG, BMP, WEBP y más

## 📋 Requisitos

- Python 3.8+
- CUDA 11.8+ (opcional, para GPU)
- 8GB RAM mínimo (16GB recomendado para entrenamiento)
- Espacio en disco: 10GB+ para modelos y datasets

## 🔧 Instalación

### 1. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
copy .env.example .env

# Editar .env con tu configuración
```

### 4. Iniciar el servidor

```bash
# Modo desarrollo
python -m app.main

# O usando uvicorn directamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: http://localhost:8000

## ⚙️ Variables de Entorno

El archivo `.env` debe contener:

```env
# Security
SECRET_KEY=tu-clave-secreta-super-segura-cambia-esto

# OAuth2 - Google
GOOGLE_CLIENT_ID=tu-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu-google-client-secret

# OAuth2 - GitHub  
GITHUB_CLIENT_ID=tu-github-client-id
GITHUB_CLIENT_SECRET=tu-github-client-secret

# OAuth2 - Facebook
FACEBOOK_CLIENT_ID=tu-facebook-app-id
FACEBOOK_CLIENT_SECRET=tu-facebook-app-secret
```

**Usuario de prueba predeterminado:**
- Email: `admin@admin.com`
- Password: `admin123`

**Nota:** Para OAuth, consulta `CONFIGURACION_OAUTH.md` en la raíz del proyecto.

## 📚 Documentación API

Una vez iniciado el servidor, accede a:

- **Swagger UI (interactiva)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🎯 Endpoints Principales

### Inferencia

```bash
# Detectar objetos en una imagen
POST /api/v1/predict
  - file: imagen (multipart/form-data)
  - model_name: nombre del modelo (opcional)
  - confidence: umbral de confianza (default: 0.25)
  - iou: umbral de IoU (default: 0.45)

# Detección por lote
POST /api/v1/predict/batch
  - files: lista de imágenes
  - model_name, confidence, iou, etc.

# Detección desde URL
POST /api/v1/predict/url
  - url: URL de la imagen
  - model_name, confidence, iou
```

### Entrenamiento

```bash
# Iniciar entrenamiento
POST /api/v1/train
  Body (JSON):
  {
    "dataset_name": "my_dataset",
    "model_size": "n",
    "epochs": 100,
    "batch_size": 16,
    "imgsz": 640
  }

# Ver estado del entrenamiento
GET /api/v1/train/{job_id}

# Listar trabajos de entrenamiento
GET /api/v1/train

# Cancelar entrenamiento
DELETE /api/v1/train/{job_id}
```

### Datasets

```bash
# Crear dataset
POST /api/v1/datasets
  Body (JSON):
  {
    "name": "my_dataset",
    "class_names": ["person", "car", "dog"]
  }

# Listar datasets
GET /api/v1/datasets

# Información de dataset
GET /api/v1/datasets/{dataset_name}

# Agregar imágenes
POST /api/v1/datasets/{dataset_name}/images
  - files: lista de imágenes
  - split: train/val/test

# Agregar imagen anotada
POST /api/v1/datasets/{dataset_name}/images/annotated
  - file: imagen
  - split: train/val/test
  - annotations: JSON con anotaciones

# Validar dataset
GET /api/v1/datasets/{dataset_name}/validate
```

### Modelos

```bash
# Listar modelos
GET /api/v1/models

# Información del modelo
GET /api/v1/models/{model_name}

# Descargar modelo
GET /api/v1/models/{model_name}/download

# Subir modelo personalizado
POST /api/v1/models/upload
  - file: archivo .pt

# Exportar modelo
POST /api/v1/models/{model_name}/export
  - format: onnx/torchscript/coreml

# Validar modelo
POST /api/v1/models/{model_name}/validate
  - dataset_name: nombre del dataset
```

### Autenticación

```bash
# Login con credenciales
POST /api/v1/auth/login/credentials
  Body (JSON):
  {
    "email": "admin@admin.com",
    "password": "admin123"
  }

# Login con OAuth (Google/GitHub/Facebook)
GET /api/v1/auth/login/{provider}

# Callback de OAuth
GET /api/v1/auth/callback/{provider}

# Obtener usuario actual
GET /api/v1/auth/me
  Headers: Authorization: Bearer {token}

# Cerrar sesión
POST /api/v1/auth/logout
  Headers: Authorization: Bearer {token}
```

### Configuración

```bash
# Obtener configuración de almacenamiento
GET /api/v1/config/storage
  Headers: Authorization: Bearer {token}

# Guardar configuración de almacenamiento
POST /api/v1/config/storage
  Headers: Authorization: Bearer {token}
  Body (JSON):
  {
    "type": "local|google_drive|onedrive",
    "credentials": {}
  }

# Probar conexión de almacenamiento
POST /api/v1/config/storage/test
  Headers: Authorization: Bearer {token}

# Resetear a almacenamiento local
DELETE /api/v1/config/storage
  Headers: Authorization: Bearer {token}
```

## 💡 Ejemplos de Uso

### Ejemplo 1: Detección de objetos con Python

```python
import requests

# Subir imagen para detección
url = "http://localhost:8000/api/v1/predict"
files = {"file": open("imagen.jpg", "rb")}
data = {
    "model_name": "yolo11n.pt",
    "confidence": 0.25
}

response = requests.post(url, files=files, data=data)
result = response.json()

print(f"Detectados {len(result['detections'])} objetos")
for detection in result["detections"]:
    print(f"- {detection['class_name']}: {detection['confidence']:.2f}")
```

### Ejemplo 2: Crear y entrenar modelo personalizado

```python
import requests

# 1. Crear dataset
url = "http://localhost:8000/api/v1/datasets"
data = {
    "name": "productos",
    "class_names": ["manzana", "naranja", "platano"]
}
response = requests.post(url, json=data)
print(response.json())

# 2. Subir imágenes al dataset
url = "http://localhost:8000/api/v1/datasets/productos/images"
files = [
    ("files", open("img1.jpg", "rb")),
    ("files", open("img2.jpg", "rb")),
]
data = {"split": "train"}
response = requests.post(url, files=files, data=data)

# 3. Iniciar entrenamiento
url = "http://localhost:8000/api/v1/train"
data = {
    "dataset_name": "productos",
    "model_size": "n",
    "epochs": 50,
    "batch_size": 16
}
response = requests.post(url, json=data)
job = response.json()
print(f"Job ID: {job['job_id']}")

# 4. Monitorear progreso
import time
url = f"http://localhost:8000/api/v1/train/{job['job_id']}"
while True:
    response = requests.get(url)
    status = response.json()
    print(f"Estado: {status['status']}, Epoch: {status['current_epoch']}/{status['epochs']}")
    if status["status"] in ["completed", "failed"]:
        break
    time.sleep(10)
```

### Ejemplo 3: Usando cURL

```bash
# Detección simple
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@imagen.jpg" \
  -F "confidence=0.3"

# Crear dataset
curl -X POST "http://localhost:8000/api/v1/datasets" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "mi_dataset",
    "class_names": ["gato", "perro"]
  }'

# Iniciar entrenamiento
curl -X POST "http://localhost:8000/api/v1/train" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_name": "mi_dataset",
    "model_size": "n",
    "epochs": 100,
    "batch_size": 16
  }'
```

## 🏗️ Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                # Aplicación FastAPI principal
│   ├── config.py              # Configuración
│   ├── schemas.py             # Modelos Pydantic
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── health.py      # Endpoints de salud
│   │       ├── inference.py   # Endpoints de inferencia
│   │       ├── training.py    # Endpoints de entrenamiento
│   │       ├── datasets.py    # Endpoints de datasets
│   │       ├── models.py      # Endpoints de modelos
│   │       ├── auth.py        # Endpoints de autenticación
│   │       └── config.py      # Endpoints de configuración
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── oauth.py           # Configuración OAuth2
│   │   └── jwt.py             # Gestión de tokens JWT
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py            # Modelos de usuario
│   └── services/
│       ├── yolo_service.py    # Servicio YOLO
│       ├── dataset_service.py # Servicio de datasets
│       └── storage/           # Adaptadores de almacenamiento
│           ├── __init__.py
│           ├── base.py        # Interfaz base
│           ├── local.py       # Almacenamiento local
│           ├── google_drive.py # Adaptador Google Drive
│           ├── onedrive.py    # Adaptador OneDrive
│           └── factory.py     # Factory de almacenamiento
├── datasets/                  # Datasets de entrenamiento
│   └── .gitkeep
├── models/                    # Modelos .pt
│   └── .gitkeep
├── uploads/                   # Imágenes subidas
│   └── .gitkeep
├── results/                   # Resultados de inferencia
│   └── .gitkeep
├── requirements.txt           # Dependencias Python
├── .env.example               # Plantilla de variables de entorno
├── .gitignore
└── README.md
```

## 🔒 Seguridad

Para producción:

1. **Cambiar SECRET_KEY**: Genera una clave segura en `.env`
2. **CORS**: Configura orígenes permitidos en `main.py`
3. **Rate limiting**: Implementa limitación de requests
4. **Autenticación**: Agrega JWT o OAuth2
5. **HTTPS**: Usa certificado SSL/TLS
6. **Validación**: Valida todos los inputs de usuarios

## 🐛 Solución de Problemas

### Error: CUDA out of memory

```bash
# Reduce el batch size en entrenamiento
{
  "batch_size": 8  # En lugar de 16
}
```

### Error: Model not found

```bash
# El modelo se descargará automáticamente la primera vez
# Asegúrate de tener conexión a internet
```

### Error: Dataset validation failed

```bash
# Verifica la estructura del dataset
GET /api/v1/datasets/{dataset_name}/validate
```

### Puerto 8000 ocupado

```bash
# Cambia el puerto en .env
PORT=8080

# O al iniciar
uvicorn app.main:app --port 8080
```

## 📊 Modelos YOLO11 Disponibles

| Modelo | Tamaño | Parámetros | mAP | Velocidad |
|--------|--------|------------|-----|-----------|
| YOLOv11n | 6 MB | 2.6M | 39.5 | 1.5ms |
| YOLOv11s | 19 MB | 9.4M | 47.0 | 2.5ms |
| YOLOv11m | 40 MB | 20.1M | 51.5 | 4.7ms |
| YOLOv11l | 53 MB | 25.3M | 53.4 | 6.2ms |
| YOLOv11x | 110 MB | 56.9M | 54.7 | 11.3ms |

## 📈 Mejores Prácticas

### Preparación de Datos

1. **Calidad de imágenes**: Usa imágenes claras y bien iluminadas
2. **Variedad**: Incluye diferentes ángulos, iluminaciones y contextos
3. **Balance de clases**: Mantén un balance entre clases
4. **Anotaciones precisas**: Verifica que las anotaciones sean correctas
5. **Split adecuado**: 70% train, 20% val, 10% test

### Entrenamiento

1. **Transfer learning**: Usa modelos pre-entrenados
2. **Data augmentation**: YOLO11 lo hace automáticamente
3. **Early stopping**: Configura patience adecuado
4. **Validación constante**: Monitorea métricas de validación
5. **Checkpoints**: Guarda modelos periódicamente

### Inferencia

1. **Batch processing**: Procesa múltiples imágenes a la vez
2. **Ajusta thresholds**: confidence e IOU según tu caso
3. **Tamaño de imagen**: Usa imgsz consistente con entrenamiento
4. **Caché de modelos**: Los modelos se cachean automáticamente
5. **Monitoreo**: Revisa tiempos de inferencia

## 🤝 Contribución

Para contribuir:

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -am 'Agrega nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crea un Pull Request

## 📝 Licencia

Este proyecto usa Ultralytics YOLO11, que está bajo licencia AGPL-3.0.

## 🔗 Enlaces Útiles

- [Documentación YOLO11](https://docs.ultralytics.com/es/models/yolo11/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Ultralytics](https://ultralytics.com/)

## 📧 Soporte

Para preguntas o problemas:
- Revisa la documentación
- Busca en issues existentes
- Crea un nuevo issue con detalles

---

**Desarrollado con ❤️ usando YOLO11 y FastAPI**
