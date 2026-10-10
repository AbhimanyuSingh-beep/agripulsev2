"""
fix_class_labels.py — Regenerate class_labels.json from the saved checkpoint.

The model's output index MUST match the class_labels.json index.
This script reads the class_names directly from best_model.pt (the exact
order used during training) and overwrites class_labels.json to match.

Run from agripulse/ directory:
    python fix_class_labels.py
"""
import json
import sys
import torch
from pathlib import Path

PROJECT_ROOT  = Path(__file__).parent
CHECKPOINT    = PROJECT_ROOT / "model" / "checkpoints" / "best_model.pt"
LABELS_FILE   = PROJECT_ROOT / "backend" / "class_labels.json"

print("=" * 60)
print("AgriPulse — Fixing class_labels.json from checkpoint")
print("=" * 60)

if not CHECKPOINT.exists():
    print(f"❌ Checkpoint not found: {CHECKPOINT}")
    sys.exit(1)

# Load checkpoint (CPU-safe)
ckpt = torch.load(str(CHECKPOINT), map_location="cpu")
class_names = ckpt["class_names"]
num_classes = ckpt["num_classes"]
val_acc     = ckpt.get("val_accuracy", 0.0)

print(f"\n✅ Loaded checkpoint:")
print(f"   num_classes  : {num_classes}")
print(f"   val_accuracy : {val_acc * 100:.2f}%")
print(f"\n📋 Class order from checkpoint (this is what the model outputs):\n")

mapping = []
for idx, folder in enumerate(class_names):
    parts   = folder.split("___")
    crop    = parts[0].replace("_(maize)", "").replace("_", " ").strip()
    disease = parts[1].replace("_", " ").strip() if len(parts) > 1 else "Unknown"
    is_healthy = "healthy" in disease.lower()

    print(f"  [{idx:2d}] {folder}")
    print(f"        crop={crop!r}  disease={disease!r}  is_healthy={is_healthy}")

    mapping.append({
        "index":      idx,
        "folder":     folder,
        "crop":       crop,
        "disease":    disease,
        "is_healthy": is_healthy,
    })

# Backup the old file
if LABELS_FILE.exists():
    backup = LABELS_FILE.with_suffix(".json.bak")
    backup.write_bytes(LABELS_FILE.read_bytes())
    print(f"\n💾 Backed up old class_labels.json → {backup.name}")

# Write the corrected file
data = {
    "classes":              mapping,
    "num_classes":          num_classes,
    "confidence_threshold": 0.60,
    "input_size":           224,
    "imagenet_mean":        [0.485, 0.456, 0.406],
    "imagenet_std":         [0.229, 0.224, 0.225],
}
with open(LABELS_FILE, "w") as f:
    json.dump(data, f, indent=2)

print(f"\n✅ Saved corrected class_labels.json → {LABELS_FILE}")
print("\n🔁 Restart the FastAPI backend for changes to take effect.")
print("=" * 60)
