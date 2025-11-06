# 📤 Guía para Subir el Proyecto a GitHub

Esta guía te ayudará a subir el proyecto **yolo11** a GitHub paso a paso.

## 📋 Requisitos Previos

1. **Tener Git instalado**
   ```powershell
   git --version
   ```
   Si no lo tienes, descárgalo de: https://git-scm.com/

2. **Tener una cuenta de GitHub**
   - Si no tienes una, créala en: https://github.com/signup

3. **Configurar Git** (solo la primera vez)
   ```powershell
   git config --global user.name "Tu Nombre"
   git config --global user.email "tu@email.com"
   ```

## 🚀 Pasos para Subir el Proyecto

### 1. Crear Repositorio en GitHub

1. Ve a https://github.com/new
2. **Repository name**: `yolo11`
3. **Description** (opcional): "Sistema completo de detección de objetos con YOLO11, FastAPI y React"
4. **Visibilidad**: 
   - ✅ **Public** (si quieres que sea visible para todos)
   - ⬜ **Private** (si quieres que solo tú lo veas)
5. ⚠️ **NO marques** ninguna opción de "Initialize this repository with..."
6. Click en **Create repository**

### 2. Preparar el Repositorio Local

Abre PowerShell en la carpeta del proyecto:

```powershell
cd d:\IA\modelos\yolo12
```

### 3. Inicializar Git

```powershell
# Inicializar repositorio Git
git init

# Agregar todos los archivos (respetando .gitignore)
git add .

# Ver qué archivos se agregaron
git status

# Crear el primer commit
git commit -m "Initial commit: Sistema YOLO11 con autenticación y almacenamiento en nube"
```

### 4. Conectar con GitHub

Reemplaza `TU_USUARIO` con tu nombre de usuario de GitHub:

```powershell
# Renombrar rama principal a 'main'
git branch -M main

# Conectar con tu repositorio de GitHub
git remote add origin https://github.com/TU_USUARIO/yolo11.git

# Verificar que se agregó correctamente
git remote -v
```

### 5. Subir el Código

```powershell
# Subir todo a GitHub
git push -u origin main
```

**Nota:** Te pedirá autenticación. Usa un **Personal Access Token** (no tu contraseña).

#### Crear Personal Access Token

1. Ve a: https://github.com/settings/tokens
2. Click en **Generate new token** > **Generate new token (classic)**
3. **Note**: "YOLO11 Project"
4. **Expiration**: 90 days (o lo que prefieras)
5. **Scopes**: Marca ✅ **repo** (completo)
6. Click **Generate token**
7. **⚠️ COPIA EL TOKEN** (no lo verás de nuevo)
8. Úsalo como contraseña cuando Git te lo pida

### 6. Verificar

Ve a: `https://github.com/TU_USUARIO/yolo11`

¡Tu proyecto ya está en GitHub! 🎉

## 📝 Archivos que NO se Suben (Protegidos por .gitignore)

✅ **Se ignoran automáticamente:**
- `node_modules/` (dependencias de Node)
- `venv/` o `env/` (entorno virtual Python)
- `.env` (variables de entorno secretas)
- `*.pt` (modelos entrenados pesados)
- `datasets/*/` (tus datasets personales)
- `results/*/` (resultados de entrenamientos)
- `uploads/*/` (imágenes subidas)
- `__pycache__/` (archivos temporales de Python)

## 🔄 Actualizar el Repositorio (Futuras Modificaciones)

Cada vez que hagas cambios:

```powershell
# Ver archivos modificados
git status

# Agregar cambios
git add .

# Hacer commit con mensaje descriptivo
git commit -m "Descripción de los cambios"

# Subir a GitHub
git push
```

## 🌿 Trabajar con Ramas (Opcional)

Para trabajar en nuevas características sin afectar `main`:

```powershell
# Crear nueva rama
git checkout -b feature/nueva-funcionalidad

# Hacer cambios y commits
git add .
git commit -m "Nueva funcionalidad"

# Subir rama a GitHub
git push -u origin feature/nueva-funcionalidad

# Volver a main
git checkout main

# Fusionar cambios
git merge feature/nueva-funcionalidad
```

## ⚠️ Importante - Seguridad

### ¿Qué hacer si subiste accidentalmente .env?

Si subiste tu archivo `.env` con credenciales:

1. **Elimínalo del historial**:
   ```powershell
   git rm --cached backend/.env
   git commit -m "Remove .env file"
   git push
   ```

2. **Regenera TODAS las credenciales:**
   - Cambia `SECRET_KEY`
   - Regenera Client Secrets de OAuth
   - Revoca tokens de acceso

3. **Verifica que .gitignore incluya .env**

### Mejores Prácticas

✅ **SÍ subir:**
- Código fuente
- `requirements.txt` y `package.json`
- `.env.example` (plantilla sin valores reales)
- Documentación (README, guías)
- Configuración de proyecto

❌ **NO subir:**
- Credenciales (`.env`)
- Modelos entrenados grandes (`.pt`)
- Datasets personales
- node_modules/
- venv/

## 📊 Configurar GitHub Pages (Opcional)

Si quieres publicar el frontend:

1. En GitHub, ve a **Settings** > **Pages**
2. **Source**: Deploy from a branch
3. **Branch**: `main` > `/frontend/dist`
4. Click **Save**

Necesitarás build el frontend:
```powershell
cd frontend
npm run build
```

## 🔧 Configurar Secrets de GitHub

Para CI/CD o GitHub Actions:

1. Ve a tu repo > **Settings** > **Secrets and variables** > **Actions**
2. Click **New repository secret**
3. Agrega:
   - `SECRET_KEY`
   - `GOOGLE_CLIENT_SECRET`
   - `GITHUB_CLIENT_SECRET`
   - etc.

## 📚 Recursos Adicionales

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Docs](https://docs.github.com/)
- [Pro Git Book (Español)](https://git-scm.com/book/es/v2)

## 🆘 Troubleshooting

### Error: "remote origin already exists"
```powershell
git remote remove origin
git remote add origin https://github.com/TU_USUARIO/yolo11.git
```

### Error: "failed to push some refs"
```powershell
# Primero descarga los cambios
git pull origin main --allow-unrelated-histories
# Luego sube
git push -u origin main
```

### Error: "large files"
GitHub no acepta archivos > 100MB. Si tienes modelos grandes:

```powershell
# Instalar Git LFS
git lfs install

# Trackear archivos grandes
git lfs track "*.pt"
git add .gitattributes
git commit -m "Add Git LFS for model files"
```

### Resetear todo (último recurso)
```powershell
# ⚠️ ESTO BORRA TODO EL HISTORIAL
rm -rf .git
git init
git add .
git commit -m "Fresh start"
git remote add origin https://github.com/TU_USUARIO/yolo11.git
git push -u origin main --force
```

---

## ✅ Checklist Final

Antes de hacer public tu repo, verifica:

- [ ] `.env` NO está en el repositorio
- [ ] `.gitignore` está configurado correctamente
- [ ] README.md está actualizado
- [ ] Credenciales de demo (admin@admin.com) están documentadas
- [ ] Instrucciones de instalación son claras
- [ ] No hay información sensible en el código
- [ ] El proyecto funciona después de clonar

---

**¡Tu proyecto ya está listo para compartirse en GitHub!** 🎉

Si quieres que otros contribuyan, considera agregar:
- `CONTRIBUTING.md` - Guía para contribuidores
- `LICENSE` - Licencia del proyecto
- GitHub Issues templates
- GitHub Actions para CI/CD
