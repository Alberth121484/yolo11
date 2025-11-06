# 🚀 Guía Rápida - Sistema YOLO11

## ✅ Mejoras Implementadas

### 1. **Progreso en Tiempo Real** 
✨ **Ahora verás el progreso del entrenamiento en vivo!**

- 📊 Barra de progreso visual con porcentaje
- 🔄 Badge animado "Entrenando..."
- 📈 Métricas actualizadas (mAP, Precision, Recall)
- ⏱️ Actualización cada 2 segundos
- ✓ Indicador de epoch completado

### 2. **Modelo Entrenado Disponible Automáticamente**
🎯 **Tu modelo se guarda y lista para usar!**

El modelo entrenado:
- ✅ Se guarda automáticamente con nombre legible
- ✅ Aparece en el selector de inferencia
- ✅ Se muestra en la tabla de entrenamientos
- ✅ Notificación cuando termina el entrenamiento

---

## 🎓 Cómo Usar el Sistema

### Paso 1: Entrenar tu Modelo

1. **Ve a "Entrenamiento"**
2. **Clic en "Nuevo Entrenamiento"**
3. **Selecciona tu dataset** (ej: "sopas")
4. **Configura:**
   - Tamaño: Nano (para empezar)
   - Epochs: 20-50 (para pruebas rápidas)
   - Batch: 16 (o menos si tienes poco RAM)
5. **Clic en "Iniciar"**

**¡Ahora verás el progreso en tiempo real!** 🎉

```
┌─────────────────────────────────────────┐
│ 🔄 Entrenando...                        │
│ 📊 Epoch 5/20                          │
│ mAP: 0.742 • Precision: 0.856          │
│ ████████░░░░░░░░ 25.0%                 │
│ ⏱️ Actualizando... ✓ Epoch 5 completado│
└─────────────────────────────────────────┘
```

### Paso 2: Usar tu Modelo Entrenado

**Cuando el entrenamiento termine:**

1. **Verás una notificación:**
   ```
   🎉 ✅ Entrenamiento completado!
   Modelo: sopas_yolo11n_20251105_1044.pt
   mAP: 0.892
   ```

2. **El modelo aparece en la tabla:**
   ```
   📦 sopas_yolo11n_20251105_1044.pt
   ```

3. **Ve a "Inferencia"**

4. **En el selector de modelos verás:**
   ```
   🏋️ Modelos Pre-entrenados
   ├─ YOLO11n (nano)
   ├─ YOLO11s (small)
   └─ ...
   
   🎯 Modelos Entrenados (tus modelos)
   └─ sopas_yolo11n_20251105_1044.pt (3 clases) ✓
   ```

5. **Selecciona tu modelo entrenado**

6. **Sube una imagen de sopas**

7. **¡Detecta tus clases personalizadas!** 🎯

---

## 📝 Nombres de Archivos

### Modelo Entrenado
Formato: `{dataset}\_yolo11{tamaño}\_{fecha}\_{hora}.pt`

Ejemplos:
- `sopas_yolo11n_20251105_1044.pt`
- `productos_yolo11s_20251105_1530.pt`
- `defectos_yolo11m_20251105_2210.pt`

### Ubicación
```
backend/models/
├── yolo11n.pt              (pre-entrenado)
├── yolo11s.pt              (pre-entrenado)
└── sopas_yolo11n_*.pt      (tu modelo) ✓
```

---

## 🔧 Solución de Problemas

### ❌ "Error 500 al usar modelo entrenado"

**SOLUCIÓN:** Reinicia el backend

```bash
# Presiona Ctrl+C en la terminal del backend
cd d:\IA\modelos\yolo12\backend
venv\Scripts\python.exe -m app.main
```

El frontend se actualiza automáticamente.

### ❌ "Barra no se llena / muestra 0%"

**CAUSA:** El backend no está actualizado con los cambios

**SOLUCIÓN:** 
1. Cancela el entrenamiento actual
2. Reinicia el backend (ver arriba)
3. Inicia un nuevo entrenamiento
4. ¡Ahora verás el progreso! 🚀

### ❌ "No veo mi modelo en inferencia"

**VERIFICAR:**
1. ¿El entrenamiento dice "completed"? ✅
2. ¿Ves el nombre del modelo en la tabla? 📦
3. Recarga la página de inferencia (F5)
4. Revisa la consola del backend

### ❌ "El modelo no detecta nada"

**POSIBLES CAUSAS:**
- Confidence muy alto → Bájalo a 0.15
- Modelo no entrenado suficiente → Más epochs
- Imágenes muy diferentes al entrenamiento
- Dataset con pocas imágenes → Añade más datos

---

## 💡 Tips para Mejor Detección

### Durante el Entrenamiento:
- ✅ Usa al menos 100 imágenes por clase
- ✅ Balancea las clases (misma cantidad)
- ✅ Varía ángulos, iluminación, fondos
- ✅ Anota con precisión

### Durante la Inferencia:
- ✅ Usa el modelo que entrenaste (no pre-entrenado)
- ✅ Baja confidence si no detecta (0.15)
- ✅ Usa imágenes similares al entrenamiento
- ✅ Revisa que las clases coincidan

---

## 📊 Métricas Importantes

### mAP (mean Average Precision)
- 0.5-0.6 = Aceptable ⚠️
- 0.7-0.8 = Bueno ✅
- 0.85+ = Excelente 🌟

### Precision
- Qué tan precisas son las detecciones
- Alto = Pocas falsas detecciones

### Recall
- Qué tan bien encuentra todos los objetos
- Alto = No se pierde objetos

---

## 🎯 Flujo Completo de Trabajo

```mermaid
1. Crear Dataset → 2. Subir Imágenes → 3. Anotar
                           ↓
4. Entrenar (ver progreso) → 5. Esperar (2-30 min)
                           ↓
6. Recibir notificación ✅ → 7. Ver modelo en tabla 📦
                           ↓
8. Ir a Inferencia → 9. Seleccionar modelo → 10. ¡Detectar! 🎉
```

---

## 🚀 Comandos Útiles

### Reiniciar Backend
```bash
cd d:\IA\modelos\yolo12\backend
venv\Scripts\python.exe -m app.main
```

### Reiniciar Frontend
```bash
cd d:\IA\modelos\yolo12\frontend
npm run dev
```

### Ver Logs del Backend
Mira la terminal donde corre el backend:
- Info de entrenamiento
- Progreso de epochs
- Errores si hay

### Limpiar Modelos Viejos
```bash
cd d:\IA\modelos\yolo12\backend\models
# Elimina manualmente los .pt que no necesites
```

---

## ✨ Características Nuevas

### 1. Progreso Visual
- Barra animada con gradiente
- Porcentaje exacto
- Mini barras en tabla

### 2. Notificaciones
- Toast cuando completa
- Nombre del modelo
- mAP final

### 3. Selector Inteligente
- Separa modelos pre-entrenados
- Muestra tus modelos con ícono 🎯
- Indica número de clases

### 4. Tabla Mejorada
- Columna para nombre del modelo
- Badge destacado con 📦
- mAP en color verde
- Mini barra de progreso

---

## 📞 ¿Necesitas Ayuda?

1. **Revisa los logs** del backend
2. **Verifica** que el modelo existe en `backend/models/`
3. **Reinicia** backend y frontend
4. **Prueba** con confidence más bajo
5. **Revisa** que el dataset tenga suficientes imágenes

---

**¡Listo para detectar objetos con IA! 🚀🎯**
