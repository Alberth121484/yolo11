"""
Script para verificar que tu dataset está correctamente estructurado
"""
import os
from pathlib import Path

def verificar_dataset(dataset_name):
    base_path = Path(f"backend/datasets/{dataset_name}")
    
    print(f"\n{'='*60}")
    print(f"VERIFICANDO DATASET: {dataset_name}")
    print(f"{'='*60}\n")
    
    # Verificar estructura
    carpetas_requeridas = [
        "images/train", "images/val", "images/test",
        "labels/train", "labels/val", "labels/test"
    ]
    
    print("📁 Estructura de carpetas:")
    for carpeta in carpetas_requeridas:
        path = base_path / carpeta
        existe = "✅" if path.exists() else "❌"
        print(f"  {existe} {carpeta}")
    
    print("\n📊 Conteo de archivos:")
    
    for split in ["train", "val", "test"]:
        img_path = base_path / "images" / split
        lbl_path = base_path / "labels" / split
        
        if img_path.exists() and lbl_path.exists():
            imagenes = list(img_path.glob("*.jpg")) + list(img_path.glob("*.png"))
            labels = list(lbl_path.glob("*.txt"))
            
            print(f"\n  {split.upper()}:")
            print(f"    Imágenes: {len(imagenes)}")
            print(f"    Labels:   {len(labels)}")
            
            if len(imagenes) != len(labels):
                print(f"    ⚠️  ADVERTENCIA: Número de imágenes y labels no coincide")
            else:
                print(f"    ✅ Imágenes y labels coinciden")
            
            # Verificar que cada imagen tenga su label
            faltantes = []
            for img in imagenes[:5]:  # Verificar primeras 5
                label_name = img.stem + ".txt"
                label_path = lbl_path / label_name
                if not label_path.exists():
                    faltantes.append(img.name)
            
            if faltantes:
                print(f"    ⚠️  Faltan labels para: {', '.join(faltantes)}")
    
    # Verificar data.yaml
    yaml_path = base_path / "data.yaml"
    if yaml_path.exists():
        print(f"\n✅ data.yaml existe")
        with open(yaml_path, 'r', encoding='utf-8') as f:
            print("\n📄 Contenido de data.yaml:")
            print("  " + "\n  ".join(f.read().split("\n")))
    else:
        print(f"\n❌ data.yaml NO existe")
    
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    # Cambia 'sopas' por el nombre de tu dataset
    verificar_dataset("sopas")
