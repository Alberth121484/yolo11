# YOLO11 Frontend - Interfaz de Administración

Interfaz web moderna para gestionar el sistema YOLO11 de detección de objetos.

## 🎨 Características

- **Autenticación**: Login con email/password y OAuth (Google, GitHub, Facebook)
- **Dashboard**: Vista general del sistema y estadísticas
- **Inferencia**: Interfaz drag & drop para detectar objetos en imágenes
- **Entrenamiento**: Gestión visual de entrenamientos de modelos
- **Datasets**: Administración de datasets con soporte para múltiples clases
- **Anotación**: Herramienta integrada para etiquetar imágenes
- **Modelos**: Gestión de modelos entrenados
- **Configuración**: Gestión de almacenamiento (local, Google Drive, OneDrive)
- **Diseño Responsive**: Funciona en desktop, tablet y móvil
- **Rutas protegidas**: Autenticación requerida para acceso

## 🚀 Tecnologías

- **React 18** - Framework UI
- **Vite** - Build tool ultrarrápido
- **TailwindCSS** - Styling moderno
- **React Router** - Navegación
- **Axios** - HTTP client
- **React Dropzone** - Upload de archivos
- **Lucide React** - Iconos
- **React Hot Toast** - Notificaciones

## 📦 Instalación

```bash
# Instalar dependencias
npm install

# Modo desarrollo
npm run dev

# Build para producción
npm run build

# Preview de producción
npm run preview
```

## 🔧 Configuración

La aplicación se conecta al backend en `http://localhost:8000` por defecto.

Para cambiar la URL del API, edita `src/lib/api.js`:

```javascript
const API_BASE_URL = 'http://tu-servidor:8000/api/v1'
```

O usa variable de entorno:

```bash
# .env.local
VITE_API_URL=http://tu-servidor:8000/api/v1
```

## 📱 Páginas

### Login
- Login con email y contraseña
- Login con Google OAuth
- Login con GitHub OAuth
- Login con Facebook OAuth
- Redirección automática si ya está autenticado

**Credenciales de prueba:**
- Email: `admin@admin.com`
- Password: `admin123`

### Dashboard
- Estadísticas del sistema
- Entrenamientos recientes
- Accesos rápidos

### Inferencia
- Upload de imágenes (drag & drop)
- Configuración de parámetros
- Visualización de resultados
- Detección batch

### Entrenamiento
- Crear nuevos entrenamientos
- Monitorear progreso en tiempo real
- Historial de entrenamientos
- Cancelar/reanudar entrenamientos

### Datasets
- Crear datasets
- Subir imágenes
- Anotar imágenes
- Validar datasets

### Anotación
- Canvas interactivo para dibujar bounding boxes
- Selección de clase para cada anotación
- Guardado automático en train/val/test
- Navegación entre imágenes

### Modelos
- Listar modelos disponibles
- Descargar modelos
- Eliminar modelos
- Ver información de modelos

### Configuración
- **General**: Configuración de la aplicación
- **Almacenamiento**: Selección de almacenamiento (Local/Google Drive/OneDrive)
- **Cuenta**: Información del usuario y logout

## 🎨 Personalización

### Colores
Edita `tailwind.config.js` para cambiar el esquema de colores:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        // Tu paleta personalizada
      },
    },
  },
}
```

### Layout
El layout está en `src/components/Layout.jsx` y es completamente personalizable.

## 🔐 Autenticación

### Flujo de Login

1. Usuario accede a `/login`
2. Elige entre:
   - **Email/Password**: Ingresa credenciales y obtiene JWT token
   - **OAuth**: Redirige a proveedor (Google/GitHub/Facebook)
3. Token JWT se guarda en `localStorage`
4. Usuario es redirigido al dashboard
5. Todas las rutas están protegidas con `ProtectedRoute`

### AuthContext

El `AuthContext` maneja:
- Estado del usuario actual
- Función de logout
- Verificación de autenticación
- Carga inicial del usuario

```javascript
// Usar en componentes
import { useAuth } from '@/context/AuthContext'

function MyComponent() {
  const { user, logout, isAuthenticated, loading } = useAuth()
  
  if (loading) return <div>Cargando...</div>
  if (!isAuthenticated) return <Navigate to="/login" />
  
  return <div>Hola, {user.name}!</div>
}
```

### Rutas Protegidas

Todas las rutas principales requieren autenticación:

```javascript
<Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
  <Route index element={<Dashboard />} />
  <Route path="inference" element={<Inference />} />
  // ... más rutas
</Route>
```

## 📝 Estructura

```
frontend/
├── public/                # Assets estáticos
├── src/
│   ├── components/        # Componentes reutilizables
│   │   └── Layout.jsx
│   ├── context/           # React Context
│   │   └── AuthContext.jsx
│   ├── lib/               # Utilidades
│   │   ├── api.js        # Cliente API
│   │   └── utils.js      # Funciones helper
│   ├── pages/             # Páginas principales
│   │   ├── Login.jsx      # Página de login
│   │   ├── AuthCallback.jsx # Callback OAuth
│   │   ├── Dashboard.jsx
│   │   ├── Inference.jsx
│   │   ├── Training.jsx
│   │   ├── Datasets.jsx
│   │   ├── Annotate.jsx   # Anotación de imágenes
│   │   ├── Models.jsx
│   │   └── SettingsNew.jsx # Configuración completa
│   ├── App.jsx            # App principal con rutas protegidas
│   ├── main.jsx           # Entry point
│   └── index.css          # Estilos globales
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── .gitignore
└── README.md
```

## 🔒 Producción

Para producción:

1. Build la aplicación:
```bash
npm run build
```

2. Los archivos estarán en `dist/`

3. Sirve con cualquier servidor HTTP:
```bash
# Nginx, Apache, etc.
```

4. Configura CORS en el backend

## 🐛 Troubleshooting

### Proxy Error
Si ves errores de proxy, verifica que el backend esté corriendo en `http://localhost:8000`

### Build Errors
```bash
# Limpia node_modules
rm -rf node_modules package-lock.json
npm install
```

### CSS no carga
Verifica que TailwindCSS esté configurado correctamente en `postcss.config.js`

## 📄 Licencia

MIT
