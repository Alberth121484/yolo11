# -*- coding: utf-8 -*-
import os
from pathlib import Path

# Configuracion
dataset = "sopa_best_choice_codo_200_gr"
base_path = Path("backend") / "datasets" / dataset

# Crear carpetas
labels_train = base_path / "labels" / "train"
labels_val = base_path / "labels" / "val"
labels_train.mkdir(parents=True, exist_ok=True)
labels_val.mkdir(parents=True, exist_ok=True)

# Crear anotaciones para train
images_train = base_path / "images" / "train"
count = 0
for ext in ['*.jpg', '*.jpeg', '*.png']:
    for img in images_train.glob(ext):
        label_file = labels_train / f"{img.stem}.txt"
        with open(label_file, 'w') as f:
            f.write("0 0.5 0.5 0.75 0.75\n")
        count += 1
        print(f"Creado: {label_file.name}")

# Crear anotaciones para val
images_val = base_path / "images" / "val"
for ext in ['*.jpg', '*.jpeg', '*.png']:
    for img in images_val.glob(ext):
        label_file = labels_val / f"{img.stem}.txt"
        with open(label_file, 'w') as f:
            f.write("0 0.5 0.5 0.75 0.75\n")
        count += 1
        print(f"Creado: {label_file.name}")

print(f"\nTotal: {count} anotaciones creadas")
print("Ahora puedes entrenar de nuevo!")
