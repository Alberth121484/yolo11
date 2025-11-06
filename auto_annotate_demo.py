"""
Script de Auto-Anotación para DEMO/TESTING

⚠️ ADVERTENCIA: Este script crea anotaciones GENÉRICAS solo para probar que el sistema funciona.
Para un modelo REAL, debes anotar manualmente con LabelImg o Roboflow.

Este script anota el centro de cada imagen como si fuera el objeto.
Es útil para verificar que todo funciona, pero NO para producción.
"""
import os
from pathlib import Path

def auto_annotate_for_demo(dataset_name="sopa_best_choice_codo_200_gr"):
    """
    Crea anotaciones genéricas para todas las imágenes del dataset
    
    Cada anotación coloca un cuadro en el centro de la imagen
    cubriendo aproximadamente el 80% del área.
    """
    
    base_path = Path("backend") / "datasets" / dataset_name
    
    # Rutas
    images_train = base_path / "images" / "train"
    labels_train = base_path / "labels" / "train"
    
    images_val = base_path / "images" / "val"
    labels_val = base_path / "labels" / "val"
    
    # Crear directorios de labels
    labels_train.mkdir(parents=True, exist_ok=True)
    labels_val.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("AUTO-ANOTADOR PARA DEMO/TESTING")
    print("="*60)
    print("\n⚠️  ADVERTENCIA:")
    print("   Esto crea anotaciones genéricas SOLO para testing.")
    print("   Para un modelo real, anota manualmente con LabelImg.\n")
    
    total_created = 0
    
    # Procesar imágenes de entrenamiento
    print("📁 Procesando imágenes de entrenamiento...")
    for img_ext in ['*.jpg', '*.jpeg', '*.png']:
        for img_file in images_train.glob(img_ext):
            label_file = labels_train / f"{img_file.stem}.txt"
            
            # Formato YOLO: clase x_center y_center width height (normalizados 0-1)
            # clase=0 (primera y única clase)
            # x,y = 0.5 (centro)
            # w,h = 0.75 (75% del tamaño de la imagen)
            with open(label_file, 'w') as f:
                f.write("0 0.5 0.5 0.75 0.75\n")
            
            print(f"  ✓ {img_file.name} → {label_file.name}")
            total_created += 1
    
    # Procesar imágenes de validación
    print("\n📁 Procesando imágenes de validación...")
    for img_ext in ['*.jpg', '*.jpeg', '*.png']:
        for img_file in images_val.glob(img_ext):
            label_file = labels_val / f"{img_file.stem}.txt"
            
            with open(label_file, 'w') as f:
                f.write("0 0.5 0.5 0.75 0.75\n")
            
            print(f"  ✓ {img_file.name} → {label_file.name}")
            total_created += 1
    
    print("\n" + "="*60)
    print(f"✅ {total_created} anotaciones creadas exitosamente")
    print("="*60)
    
    # Verificar
    train_labels = list(labels_train.glob("*.txt"))
    val_labels = list(labels_val.glob("*.txt"))
    
    print(f"\n📊 Resumen:")
    print(f"   Anotaciones train: {len(train_labels)}")
    print(f"   Anotaciones val:   {len(val_labels)}")
    print(f"   Total:             {len(train_labels) + len(val_labels)}")
    
    # Mostrar ejemplo
    if train_labels:
        print(f"\n📄 Ejemplo de anotación creada:")
        with open(train_labels[0], 'r') as f:
            print(f"   Archivo: {train_labels[0].name}")
            print(f"   Contenido: {f.read().strip()}")
            print(f"   Formato: clase x_center y_center width height")
    
    print("\n🎯 Siguiente Paso:")
    print("   1. Ve a 'Entrenamiento' en la web")
    print("   2. Inicia nuevo entrenamiento con este dataset")
    print("   3. Espera a que complete (5-10 minutos)")
    print("   4. Prueba en 'Inferencia'")
    print("   5. ¡Debería detectar algo ahora!")
    
    print("\n⚠️  RECUERDA:")
    print("   Para un modelo REAL, debes anotar manualmente:")
    print("   - Instala: pip install labelImg")
    print("   - Ejecuta: labelImg")
    print("   - Anota cada imagen correctamente")
    print("   - Lee: COMO_ANOTAR.md para instrucciones completas")
    
    return total_created


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        dataset = sys.argv[1]
    else:
        dataset = "sopa_best_choice_codo_200_gr"
    
    try:
        total = auto_annotate_for_demo(dataset)
        
        if total > 0:
            print("\n✅ ¡Listo! Ahora puedes entrenar de nuevo.")
        else:
            print("\n❌ No se crearon anotaciones. Verifica que existan imágenes.")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("   Asegúrate de ejecutar desde la carpeta raíz del proyecto")
