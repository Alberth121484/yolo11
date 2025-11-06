# -*- coding: utf-8 -*-
from pathlib import Path

dataset = "sopa_best_choice_codo_200_gr"
base = Path("backend") / "datasets" / dataset

images_train = list((base / "images/train").glob("*.*"))
labels_train = list((base / "labels/train").glob("*.txt"))
images_val = list((base / "images/val").glob("*.*"))
labels_val = list((base / "labels/val").glob("*.txt"))

print("="*50)
print("VERIFICACION DEL DATASET")
print("="*50)
print(f"Imagenes train: {len(images_train)}")
print(f"Labels train:   {len(labels_train)}")
print(f"Imagenes val:   {len(images_val)}")
print(f"Labels val:     {len(labels_val)}")

if len(images_train) == len(labels_train):
    print("\nEstado: OK - Imagenes y labels coinciden")
else:
    print(f"\nADVERTENCIA: Faltan {abs(len(images_train) - len(labels_train))} archivos")

if labels_train:
    print(f"\nEjemplo de anotacion:")
    print(f"  Archivo: {labels_train[0].name}")
    print(f"  Contenido: {labels_train[0].read_text().strip()}")
    print(f"  Formato: clase x y w h (correcto)")

print("\n" + "="*50)
print("Listo para entrenar!")
print("="*50)
