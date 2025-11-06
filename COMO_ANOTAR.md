# 📝 Cómo Anotar Imágenes para YOLO

## ❌ Problema: Sin Anotaciones

Tu dataset tiene:
- ✅ 20 imágenes
- ❌ 0 anotaciones

**El modelo NO puede aprender sin anotaciones.**

---

## 🎯 ¿Qué son las Anotaciones?

Son archivos `.txt` que le dicen al modelo DÓNDE está el objeto en cada imagen.

```
Estructura:
📁 datasets/sopa_best_choice_codo_200_gr/
├─ 📁 images/train/
│  ├─ imagen1.jpg ✓
│  ├─ imagen2.jpg ✓
│  └─ imagen3.jpg ✓
└─ 📁 labels/train/
   ├─ imagen1.txt ✗ (FALTA)
   ├─ imagen2.txt ✗ (FALTA)
   └─ imagen3.txt ✗ (FALTA)
```

---

## 🛠️ SOLUCIÓN 1: LabelImg (Rápido y Local)

### 📥 Instalar LabelImg

```bash
pip install labelImg
```

### 🚀 Usar LabelImg

1. **Abrir LabelImg:**
```bash
labelImg
```

2. **Configurar:**
   - Clic en **"Open Dir"** → Selecciona: `backend/datasets/sopa_best_choice_codo_200_gr/images/train`
   - Clic en **"Change Save Dir"** → Selecciona: `backend/datasets/sopa_best_choice_codo_200_gr/labels/train`
   - **IMPORTANTE:** Clic en **"YOLO"** (esquina inferior izquierda) para cambiar el formato

3. **Anotar Cada Imagen:**
   - Presiona **"W"** para crear un cuadro
   - Arrastra el cuadro alrededor del producto (la sopa)
   - Escribe el nombre de la clase: **"SOPA BEST CHOICE CODO 200 GR"**
   - Presiona **"D"** para pasar a la siguiente imagen
   - Repite para las 20 imágenes

4. **Verificar:**
   - Cada imagen debe tener su archivo `.txt` correspondiente
   - Ejemplo: `imagen1.jpg` → `imagen1.txt`

### 🎥 Tutorial Visual

![LabelImg](https://user-images.githubusercontent.com/26833433/201511720-ecdb036f-a3f0-4e75-968e-8e5dc1e75e5d.png)

**Atajos de teclado:**
- `W` = Crear cuadro
- `D` = Siguiente imagen
- `A` = Imagen anterior
- `Ctrl+S` = Guardar

---

## 🛠️ SOLUCIÓN 2: Roboflow (En la Nube)

### 📝 Pasos:

1. **Ir a:** https://roboflow.com
2. **Crear cuenta gratis**
3. **Nuevo proyecto:**
   - Tipo: Object Detection
   - Nombre: sopas_best_choice

4. **Subir imágenes:**
   - Arrastra las 20 imágenes
   - Sube todo el batch

5. **Anotar:**
   - Clic en cada imagen
   - Dibujar cuadros alrededor de las sopas
   - Etiqueta: "SOPA BEST CHOICE CODO 200 GR"

6. **Exportar:**
   - Formato: **YOLO v5 PyTorch**
   - Descargar ZIP
   - Copiar archivos a tu dataset

---

## 🛠️ SOLUCIÓN 3: Script Auto-Anotador (Para Testing)

Si solo quieres probar que el sistema funciona, puedes usar este script de auto-anotación (solo para testing, NO para producción):

```python
# auto_annotate.py
import os
from pathlib import Path

dataset = "sopa_best_choice_codo_200_gr"
images_dir = Path(f"backend/datasets/{dataset}/images/train")
labels_dir = Path(f"backend/datasets/{dataset}/labels/train")

# Crear carpeta de labels si no existe
labels_dir.mkdir(parents=True, exist_ok=True)

# Para cada imagen, crear anotación de ejemplo (objeto completo)
for img_file in images_dir.glob("*.jpg"):
    label_file = labels_dir / f"{img_file.stem}.txt"
    
    # Formato YOLO: clase x_center y_center width height (normalizados 0-1)
    # Esto anota el centro de la imagen completa
    with open(label_file, 'w') as f:
        f.write("0 0.5 0.5 0.8 0.8\n")  # Objeto en el centro, 80% del tamaño
    
    print(f"✓ Creado: {label_file.name}")

print(f"\n✅ {len(list(labels_dir.glob('*.txt')))} anotaciones creadas")
```

**⚠️ ADVERTENCIA:** Esto solo crea anotaciones genéricas para testing. Para un modelo real, debes anotar manualmente.

---

## ✅ Verificar que las Anotaciones están Correctas

### Script de Verificación:

```python
# verificar_anotaciones.py
from pathlib import Path

dataset = "sopa_best_choice_codo_200_gr"
images = list(Path(f"backend/datasets/{dataset}/images/train").glob("*.jpg"))
labels = list(Path(f"backend/datasets/{dataset}/labels/train").glob("*.txt"))

print(f"📊 Verificación del Dataset:")
print(f"  Imágenes: {len(images)}")
print(f"  Labels:   {len(labels)}")

if len(images) == len(labels):
    print("  ✅ Número correcto de anotaciones")
else:
    print(f"  ❌ Faltan {len(images) - len(labels)} anotaciones")

# Verificar contenido
if labels:
    with open(labels[0], 'r') as f:
        content = f.read()
        print(f"\n📄 Ejemplo de anotación:")
        print(f"  {content}")
        
        parts = content.strip().split()
        if len(parts) == 5:
            print("  ✅ Formato correcto (clase x y w h)")
        else:
            print("  ❌ Formato incorrecto")
```

---

## 📋 Checklist Final

Antes de entrenar de nuevo, verifica:

- [ ] Cada imagen tiene su archivo `.txt` correspondiente
- [ ] Los archivos `.txt` están en `labels/train/`
- [ ] Los archivos `.txt` tienen el formato correcto: `0 x y w h`
- [ ] Las coordenadas están normalizadas (entre 0 y 1)
- [ ] El nombre de los archivos coincide (sin extensión)
  - ✅ `imagen1.jpg` → `imagen1.txt`
  - ❌ `imagen1.jpg` → `imagen2.txt`

---

## 🎯 Después de Anotar

1. **Entrenar de nuevo:**
   ```
   - Ve a "Entrenamiento"
   - Nuevo Entrenamiento
   - Dataset: sopa_best_choice_codo_200_gr
   - Epochs: 50
   - Iniciar
   ```

2. **Esperar a que complete**

3. **Probar en Inferencia:**
   - Usa el nuevo modelo
   - Confidence: 0.15
   - ¡Ahora SÍ detectará!

---

## 💡 Tips para Buenas Anotaciones

1. **Precisión:**
   - El cuadro debe cubrir TODO el objeto
   - No dejar espacios en los bordes
   - No incluir objetos extra

2. **Consistencia:**
   - Usa el mismo criterio para todas las imágenes
   - Misma etiqueta para el mismo objeto

3. **Calidad:**
   - Revisa cada anotación antes de guardar
   - Si la imagen está borrosa, mejor no usarla

4. **Cantidad:**
   - Mínimo: 100 imágenes por clase
   - Recomendado: 200-500 imágenes
   - Más imágenes = mejor modelo

---

## 🚀 Siguiente Paso

**Anota tus 20 imágenes ahora usando LabelImg:**

```bash
# 1. Instalar
pip install labelImg

# 2. Abrir
labelImg

# 3. Anotar cada imagen (5-10 minutos total)

# 4. Verificar que se crearon los .txt

# 5. Entrenar de nuevo

# 6. ¡Disfrutar de un modelo que SÍ detecta!
```

---

**¿Necesitas ayuda con la anotación? ¡Pregunta!**
