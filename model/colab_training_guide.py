# AgriPulse AI — Google Colab Training Notebook
# This file shows what the Colab notebook contains.
# Open it at: https://colab.research.google.com
# Runtime → Change runtime type → T4 GPU → Save
#
# ════════════════════════════════════════════════════════════════
# STEP 1: Mount Google Drive (to save model)
# ════════════════════════════════════════════════════════════════
#
# from google.colab import drive
# drive.mount('/content/drive')
#
# ════════════════════════════════════════════════════════════════
# STEP 2: Download PlantVillage from Kaggle
# ════════════════════════════════════════════════════════════════
#
# Upload your kaggle.json (from https://kaggle.com/account → API)
# from google.colab import files
# files.upload()  # upload kaggle.json
#
# !mkdir -p ~/.kaggle && cp kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json
# !kaggle datasets download -d emmarex/plantdisease --unzip -p /content/plantvillage
#
# ════════════════════════════════════════════════════════════════
# STEP 3: Install dependencies
# ════════════════════════════════════════════════════════════════
#
# !pip install torch torchvision matplotlib scikit-learn --quiet
#
# ════════════════════════════════════════════════════════════════
# STEP 4: Filter dataset (keep only 4 crops)
# ════════════════════════════════════════════════════════════════
#
# import os, shutil
# from pathlib import Path
#
# src = Path('/content/plantvillage/PlantVillage')
# dst = Path('/content/plantvillage_filtered')
# KEEP = ['Corn', 'Grape', 'Potato', 'Tomato']
#
# for folder in src.iterdir():
#     crop = folder.name.split('_')[0].split('(')[0].strip()
#     if any(k.lower() in crop.lower() for k in KEEP):
#         shutil.copytree(folder, dst / folder.name, dirs_exist_ok=True)
#         print(f'  ✓ {folder.name}')
#
# print(f'\nTotal classes: {len(list(dst.iterdir()))}')
#
# ════════════════════════════════════════════════════════════════
# STEP 5: Upload model/ folder scripts (or paste inline)
# ════════════════════════════════════════════════════════════════
# Upload dataset.py and train.py from this project, then:
#
# !python train.py --data_root /content/plantvillage_filtered --epochs 15
#
# ════════════════════════════════════════════════════════════════
# STEP 6: Export model
# ════════════════════════════════════════════════════════════════
#
# !python export.py
#
# ════════════════════════════════════════════════════════════════
# STEP 7: Download model files
# ════════════════════════════════════════════════════════════════
#
# from google.colab import files
# files.download('model/checkpoints/model_scripted.pt')
# files.download('model/checkpoints/best_model.pt')
# files.download('backend/class_labels.json')
# files.download('plots/accuracy_curve.png')
# files.download('plots/loss_curve.png')
#
# ════════════════════════════════════════════════════════════════
# After downloading:
# Place model_scripted.pt in: model/checkpoints/
# Place class_labels.json in: backend/
# Place plots/*.png in: plots/
# ════════════════════════════════════════════════════════════════

print("See comments above for the full Colab workflow.")
print("This file is a guide — open Colab and follow each STEP.")
