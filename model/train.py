"""
train.py — MobileNetV2 Transfer Learning Training Script
AgriPulse AI | Crop Health Intelligence Module

Usage:
    python model/train.py --data_root data/plantvillage --epochs 15

Trains MobileNetV2 (pretrained ImageNet) on the 4-crop PlantVillage subset.
Saves:
  - model/checkpoints/best_model.pt  (best val accuracy)
  - plots/accuracy_curve.png
  - plots/loss_curve.png
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from model.dataset import create_data_loaders

# ─── Paths ───────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
CHECKPOINT_DIR = PROJECT_ROOT / "model" / "checkpoints"
PLOTS_DIR      = PROJECT_ROOT / "plots"
LABELS_FILE    = PROJECT_ROOT / "backend" / "class_labels.json"

CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


# ─── Model Builder ───────────────────────────────────────────────────────────
def build_model(num_classes: int, unfreeze_last_n: int = 3) -> nn.Module:
    """
    Loads pretrained MobileNetV2, freezes base layers, replaces classifier.

    Strategy:
      - Freeze ALL layers first
      - Unfreeze the last N feature blocks (default: last 3 inverted residual blocks)
      - Replace the final classifier Linear layer with num_classes outputs

    This gives fast training while adapting the top layers to our domain.
    """
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)

    # Step 1: Freeze all parameters
    for param in model.parameters():
        param.requires_grad = False

    # Step 2: Unfreeze the last N feature blocks (fine-tuning)
    features = list(model.features)
    for block in features[-unfreeze_last_n:]:
        for param in block.parameters():
            param.requires_grad = True

    # Step 3: Replace the classifier head
    # MobileNetV2 classifier: [Dropout(0.2), Linear(1280, 1000)]
    in_features = model.classifier[1].in_features  # 1280
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, 512),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.2),
        nn.Linear(512, num_classes),
    )

    return model


# ─── Training Loop ───────────────────────────────────────────────────────────
def train_one_epoch(model, loader, criterion, optimizer, device, epoch):
    model.train()
    total_loss, correct, total = 0.0, 0, 0

    for batch_idx, (images, labels) in enumerate(loader):
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss    = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * images.size(0)
        preds      = outputs.argmax(dim=1)
        correct    += (preds == labels).sum().item()
        total      += images.size(0)

        if (batch_idx + 1) % 20 == 0:
            print(f"  Epoch {epoch} [{batch_idx+1}/{len(loader)}] "
                  f"Loss: {loss.item():.4f}")

    avg_loss = total_loss / total
    accuracy = correct / total
    return avg_loss, accuracy


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss, correct, total = 0.0, 0, 0

    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        loss    = criterion(outputs, labels)

        total_loss += loss.item() * images.size(0)
        preds      = outputs.argmax(dim=1)
        correct    += (preds == labels).sum().item()
        total      += images.size(0)

    return total_loss / total, correct / total


# ─── Save class mapping ───────────────────────────────────────────────────────
def save_class_mapping(class_names: list, labels_file: Path):
    """
    Writes/updates class_labels.json with the actual folder → index mapping
    discovered during training (so inference uses the exact same ordering).
    """
    mapping = []
    for idx, folder in enumerate(class_names):
        parts   = folder.split("___")
        crop    = parts[0].replace("_(maize)", "").replace("_", " ").strip()
        disease = parts[1].replace("_", " ").strip() if len(parts) > 1 else "Unknown"
        mapping.append({
            "index":      idx,
            "folder":     folder,
            "crop":       crop,
            "disease":    disease,
            "is_healthy": "healthy" in disease.lower(),
        })

    data = {
        "classes":            mapping,
        "num_classes":        len(mapping),
        "confidence_threshold": 0.60,
        "input_size":         224,
        "imagenet_mean":      [0.485, 0.456, 0.406],
        "imagenet_std":       [0.229, 0.224, 0.225],
    }
    with open(labels_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved class mapping → {labels_file}")


# ─── Plot Training Curves ─────────────────────────────────────────────────────
def save_training_plots(history: dict, plots_dir: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    epochs = range(1, len(history["train_loss"]) + 1)

    # Loss curve
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(epochs, history["train_loss"], "b-o", label="Train Loss", linewidth=2)
    ax.plot(epochs, history["val_loss"],   "r-o", label="Val Loss",   linewidth=2)
    ax.set_xlabel("Epoch", fontsize=12)
    ax.set_ylabel("Cross-Entropy Loss", fontsize=12)
    ax.set_title("Training & Validation Loss — AgriPulse AI", fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(plots_dir / "loss_curve.png", dpi=150)
    plt.close(fig)

    # Accuracy curve
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(epochs, [a * 100 for a in history["train_acc"]], "b-o",
            label="Train Accuracy", linewidth=2)
    ax.plot(epochs, [a * 100 for a in history["val_acc"]],   "r-o",
            label="Val Accuracy",   linewidth=2)
    ax.set_xlabel("Epoch", fontsize=12)
    ax.set_ylabel("Accuracy (%)", fontsize=12)
    ax.set_title("Training & Validation Accuracy — AgriPulse AI", fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 100)
    fig.tight_layout()
    fig.savefig(plots_dir / "accuracy_curve.png", dpi=150)
    plt.close(fig)

    print(f"✅ Saved training curves → {plots_dir}")


# ─── Main ────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Train MobileNetV2 on PlantVillage")
    parser.add_argument("--data_root",    type=str, default="data/plantvillage",
                        help="Path to organized PlantVillage dataset")
    parser.add_argument("--epochs",       type=int, default=15)
    parser.add_argument("--batch_size",   type=int, default=32)
    parser.add_argument("--lr",           type=float, default=1e-4)
    parser.add_argument("--num_workers",  type=int, default=4)
    parser.add_argument("--unfreeze_last",type=int, default=3,
                        help="Unfreeze last N MobileNetV2 feature blocks")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🚀 Training on: {device}")
    if device.type == "cpu":
        print("⚠️  No GPU detected. Training will be slow (~1–2 hours). "
              "Consider using the Google Colab notebook instead.")

    # Data
    data_root = PROJECT_ROOT / args.data_root
    train_loader, val_loader, _, class_names, class_weights = create_data_loaders(
        str(data_root), batch_size=args.batch_size, num_workers=args.num_workers
    )
    class_weights = class_weights.to(device)

    num_classes = len(class_names)
    print(f"\n📋 Number of classes: {num_classes}")

    # Save mapping so inference.py uses the same order
    save_class_mapping(class_names, LABELS_FILE)

    # Model
    model = build_model(num_classes, unfreeze_last_n=args.unfreeze_last)
    model = model.to(device)

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total     = sum(p.numel() for p in model.parameters())
    print(f"🔧 Trainable params: {trainable:,} / {total:,} ({100*trainable/total:.1f}%)\n")

    # Optimizer + Loss
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=args.lr, weight_decay=1e-4
    )
    # Reduce LR by 0.5 if val_loss doesn't improve for 3 epochs
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=3
    )

    # Training
    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}
    best_val_acc  = 0.0
    best_ckpt     = CHECKPOINT_DIR / "best_model.pt"

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, device, epoch
        )
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)
        scheduler.step(val_loss)

        elapsed = time.time() - t0
        print(f"\n📈 Epoch {epoch:02d}/{args.epochs} [{elapsed:.0f}s] | "
              f"Train Loss: {train_loss:.4f}, Acc: {train_acc*100:.2f}% | "
              f"Val Loss: {val_loss:.4f}, Acc: {val_acc*100:.2f}%")

        history["train_loss"].append(train_loss)
        history["train_acc"].append(train_acc)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)

        # Save best checkpoint
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({
                "epoch":        epoch,
                "model_state":  model.state_dict(),
                "val_accuracy": val_acc,
                "class_names":  class_names,
                "num_classes":  num_classes,
            }, best_ckpt)
            print(f"   💾 New best! Saved checkpoint (val_acc={val_acc*100:.2f}%)")

    print(f"\n🏆 Training complete! Best validation accuracy: {best_val_acc*100:.2f}%")
    print(f"   Checkpoint saved → {best_ckpt}")

    save_training_plots(history, PLOTS_DIR)


if __name__ == "__main__":
    main()
