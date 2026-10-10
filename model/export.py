"""
export.py — Export Trained Model to TorchScript
AgriPulse AI | Crop Health Intelligence Module

Usage:
    python model/export.py

Converts best_model.pt checkpoint to TorchScript for fast, dependency-light
inference in the FastAPI backend.

Output: model/checkpoints/model_scripted.pt
"""

import sys
import torch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from model.train import build_model

PROJECT_ROOT   = Path(__file__).parent.parent
CHECKPOINT_DIR = PROJECT_ROOT / "model" / "checkpoints"


def export_torchscript():
    ckpt_path    = CHECKPOINT_DIR / "best_model.pt"
    export_path  = CHECKPOINT_DIR / "model_scripted.pt"

    if not ckpt_path.exists():
        print(f"❌ Checkpoint not found: {ckpt_path}")
        print("   Run train.py first to generate a trained model.")
        return

    print(f"📦 Loading checkpoint: {ckpt_path}")
    ckpt = torch.load(ckpt_path, map_location="cpu")
    num_classes = ckpt["num_classes"]
    class_names = ckpt["class_names"]
    val_acc     = ckpt.get("val_accuracy", 0.0)

    # Rebuild model and load weights
    model = build_model(num_classes, unfreeze_last_n=3)
    model.load_state_dict(ckpt["model_state"])
    model.eval()

    # Trace with a dummy input (1 × 3 × 224 × 224)
    dummy_input = torch.zeros(1, 3, 224, 224)
    with torch.no_grad():
        scripted_model = torch.jit.trace(model, dummy_input)

    # Save
    scripted_model.save(str(export_path))
    print(f"✅ TorchScript model exported → {export_path}")
    print(f"   Classes:       {num_classes}")
    print(f"   Val Accuracy:  {val_acc * 100:.2f}%")
    print(f"   Class names:   {class_names[:5]} ... ({len(class_names)} total)")


if __name__ == "__main__":
    export_torchscript()
