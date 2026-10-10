"""
inference.py — Model Inference Function
AgriPulse AI | Crop Health Intelligence Module

This module provides the predict() function used by the FastAPI backend.
It tries to load the real trained model; falls back to mock output if not found
(so the full frontend + API pipeline works before training is complete).
"""

import io
import json
import random
from pathlib import Path
from typing import Optional

import torch
from PIL import Image
from torchvision import transforms

# ─── Paths ───────────────────────────────────────────────────────────────────
PROJECT_ROOT  = Path(__file__).parent.parent
LABELS_FILE   = PROJECT_ROOT / "backend" / "class_labels.json"
SCRIPTED_MODEL = PROJECT_ROOT / "model" / "checkpoints" / "model_scripted.pt"
CHECKPOINT     = PROJECT_ROOT / "model" / "checkpoints" / "efficientnet_b0_best.pt"

# ─── Image Preprocessing (must match training transforms exactly) ─────────────
PREPROCESS = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

# ─── Load class labels ────────────────────────────────────────────────────────
def _load_labels() -> dict:
    if LABELS_FILE.exists():
        with open(LABELS_FILE) as f:
            data = json.load(f)
        # Ensure keys are ints (JSON integers stay ints, but be explicit)
        return {int(item["index"]): item for item in data["classes"]}
    # Minimal fallback if labels file doesn't exist yet
    return {}

# ─── Load model (singleton, loaded once at startup) ───────────────────────────
_model: Optional[torch.jit.ScriptModule | torch.nn.Module] = None
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_is_mock = False

def _load_model():
    global _model, _is_mock

    if SCRIPTED_MODEL.exists():
        print(f"[OK] Loading TorchScript model: {SCRIPTED_MODEL}")
        _model = torch.jit.load(str(SCRIPTED_MODEL), map_location=_device)
        _model.eval()
        _is_mock = False

    elif CHECKPOINT.exists():
        from torchvision import models
        import torch.nn as nn
        ckpt        = torch.load(str(CHECKPOINT), map_location=_device)
        num_classes = ckpt["num_classes"]

        _model = models.efficientnet_b0(weights=None)
        for param in _model.parameters():
            param.requires_grad = False
        in_features = _model.classifier[1].in_features
        _model.classifier = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(in_features, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.2),
            nn.Linear(512, num_classes),
        )
        _model.load_state_dict(ckpt["model_state"])
        _model = _model.to(_device)
        _model.eval()
        _is_mock = False
        print(f"[OK] Loaded EfficientNet-B0 checkpoint: {CHECKPOINT}")

    else:
        print("[WARN] No trained model found. Running in MOCK mode.")
        print("       Train and export the model first for real predictions.")
        _is_mock = True


# Load at import time
_load_model()
_class_labels = _load_labels()


# ─── Public API ──────────────────────────────────────────────────────────────
def predict(image_bytes: bytes) -> dict:
    """
    Run inference on raw image bytes.

    Returns:
        {
          "crop":       str,
          "disease":    str,
          "confidence": float (0–1),
          "is_healthy": bool,
          "class_index": int,
          "mock":       bool  # True if no real model is loaded
        }
    """
    if _is_mock:
        return _mock_predict()

    # Preprocess
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = PREPROCESS(image).unsqueeze(0).to(_device)  # [1, 3, 224, 224]

    # Forward pass
    with torch.no_grad():
        logits = _model(tensor)                   # [1, num_classes]
        probs  = torch.softmax(logits, dim=1)     # [1, num_classes]
        conf, class_idx = probs.max(dim=1)

    class_idx  = int(class_idx.item())
    confidence = float(conf.item())

    # Top-3 for debugging
    top3_vals, top3_idxs = torch.topk(probs[0], k=min(3, probs.shape[1]))
    top3 = [
        {
            "index": int(idx.item()),
            "label": _class_labels.get(int(idx.item()), {}).get("folder", "?"),
            "prob":  round(float(val.item()), 4),
        }
        for idx, val in zip(top3_idxs, top3_vals)
    ]

    # Look up crop/disease from class index
    label_info = _class_labels.get(class_idx, {
        "crop":       "Unknown",
        "disease":    "Unknown",
        "is_healthy": False,
    })

    if label_info.get("crop") == "Unknown":
        print(f"[WARN] class_idx={class_idx} not found in class_labels.json "
              f"(has {len(_class_labels)} entries). "
              "Run fix_class_labels.py to regenerate class_labels.json.")

    return {
        "crop":        label_info.get("crop",       "Unknown"),
        "disease":     label_info.get("disease",    "Unknown"),
        "confidence":  round(confidence, 4),
        "is_healthy":  label_info.get("is_healthy", False),
        "class_index": class_idx,
        "top3":        top3,
        "mock":        False,
    }


def _mock_predict() -> dict:
    """
    Returns a realistic-looking random prediction for pipeline testing.
    Cycles through all 4 crops with random diseases.
    """
    mock_classes = [
        {"crop": "Tomato",  "disease": "Late Blight",         "is_healthy": False},
        {"crop": "Tomato",  "disease": "Healthy",             "is_healthy": True},
        {"crop": "Potato",  "disease": "Early Blight",        "is_healthy": False},
        {"crop": "Potato",  "disease": "Healthy",             "is_healthy": True},
        {"crop": "Corn",    "disease": "Common Rust",         "is_healthy": False},
        {"crop": "Corn",    "disease": "Healthy",             "is_healthy": True},
        {"crop": "Grape",   "disease": "Black Rot",           "is_healthy": False},
        {"crop": "Grape",   "disease": "Healthy",             "is_healthy": True},
        {"crop": "Tomato",  "disease": "Bacterial Spot",      "is_healthy": False},
        {"crop": "Grape",   "disease": "Esca (Black Measles)","is_healthy": False},
    ]
    choice     = random.choice(mock_classes)
    confidence = round(random.uniform(0.72, 0.97), 4)  # realistic high confidence

    return {
        "crop":        choice["crop"],
        "disease":     choice["disease"],
        "confidence":  confidence,
        "is_healthy":  choice["is_healthy"],
        "class_index": -1,
        "mock":        True,
    }
