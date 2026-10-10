"""
train_compare.py — Multi-Architecture Comparison Training
AgriPulse AI | Crop Health Intelligence Module

Trains ResNet18, ResNet50, DenseNet121, and EfficientNet-B0 on the same
Potato/Tomato dataset (reusing dataset.py) for a fair accuracy comparison
against the already-trained MobileNetV2 baseline.

Usage (in Colab, from /content):
    !python model/train_compare.py --data_root data/plantvillage --epochs 5

Saves:
  - model/checkpoints/<arch>_best.pt   for each architecture
  - comparison_results.json            summary of val/test accuracy per model
"""

import argparse
import json
import time
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from model.dataset import create_data_loaders

PROJECT_ROOT   = Path(__file__).parent.parent
CHECKPOINT_DIR = PROJECT_ROOT / "model" / "checkpoints"
RESULTS_FILE   = PROJECT_ROOT / "comparison_results.json"
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)


# ─── Model builders per architecture ──────────────────────────────────────────
def build_resnet(num_classes: int, depth: int = 18) -> nn.Module:
    if depth == 18:
        model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    else:
        model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)

    for param in model.parameters():
        param.requires_grad = False
    for param in model.layer4.parameters():   # unfreeze last residual block
        param.requires_grad = True

    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, 512),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.2),
        nn.Linear(512, num_classes),
    )
    return model


def build_densenet121(num_classes: int) -> nn.Module:
    model = models.densenet121(weights=models.DenseNet121_Weights.IMAGENET1K_V1)

    for param in model.parameters():
        param.requires_grad = False
    for param in model.features.denseblock4.parameters():
        param.requires_grad = True
    for param in model.features.norm5.parameters():
        param.requires_grad = True

    in_features = model.classifier.in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, 512),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.2),
        nn.Linear(512, num_classes),
    )
    return model


def build_efficientnet_b0(num_classes: int) -> nn.Module:
    model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)

    for param in model.parameters():
        param.requires_grad = False
    for block in list(model.features)[-3:]:
        for param in block.parameters():
            param.requires_grad = True

    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, 512),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.2),
        nn.Linear(512, num_classes),
    )
    return model


BUILDERS = {
    "resnet18":         lambda n: build_resnet(n, depth=18),
    "resnet50":         lambda n: build_resnet(n, depth=50),
    "densenet121":      build_densenet121,
    "efficientnet_b0":  build_efficientnet_b0,
}


# ─── Training / eval loops (same logic as train.py) ───────────────────────────
def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss, correct, total = 0.0, 0, 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * images.size(0)
        correct += (outputs.argmax(dim=1) == labels).sum().item()
        total += images.size(0)
    return total_loss / total, correct / total


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        loss = criterion(outputs, labels)
        total_loss += loss.item() * images.size(0)
        correct += (outputs.argmax(dim=1) == labels).sum().item()
        total += images.size(0)
    return total_loss / total, correct / total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_root",  type=str, default="data/plantvillage")
    parser.add_argument("--epochs",     type=int, default=5)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--lr",         type=float, default=1e-4)
    parser.add_argument("--models",     type=str, default="resnet18,resnet50,densenet121,efficientnet_b0",
                        help="Comma-separated list of models to train")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on: {device}\n")

    data_root = PROJECT_ROOT / args.data_root
    train_loader, val_loader, test_loader, class_names, class_weights = create_data_loaders(
        str(data_root), batch_size=args.batch_size
    )
    class_weights = class_weights.to(device)
    num_classes = len(class_names)

    results = {}
    archs = args.models.split(",")

    for arch in archs:
        arch = arch.strip()
        if arch not in BUILDERS:
            print(f"Skipping unknown architecture: {arch}")
            continue

        print(f"\n{'='*60}\nTraining: {arch}\n{'='*60}")
        model = BUILDERS[arch](num_classes).to(device)

        trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
        total     = sum(p.numel() for p in model.parameters())
        print(f"Trainable params: {trainable:,} / {total:,} ({100*trainable/total:.1f}%)")

        criterion = nn.CrossEntropyLoss(weight=class_weights)
        optimizer = optim.Adam(
            filter(lambda p: p.requires_grad, model.parameters()),
            lr=args.lr, weight_decay=1e-4
        )

        best_val_acc = 0.0
        best_path = CHECKPOINT_DIR / f"{arch}_best.pt"
        t_start = time.time()

        for epoch in range(1, args.epochs + 1):
            t0 = time.time()
            train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
            val_loss, val_acc = evaluate(model, val_loader, criterion, device)
            elapsed = time.time() - t0
            print(f"  Epoch {epoch}/{args.epochs} [{elapsed:.0f}s] "
                  f"Train Acc: {train_acc*100:.2f}% | Val Acc: {val_acc*100:.2f}%")

            if val_acc > best_val_acc:
                best_val_acc = val_acc
                torch.save({
                    "arch": arch,
                    "model_state": model.state_dict(),
                    "val_accuracy": val_acc,
                    "class_names": class_names,
                    "num_classes": num_classes,
                }, best_path)

        # Final test accuracy using best val checkpoint
        ckpt = torch.load(best_path, map_location=device)
        model.load_state_dict(ckpt["model_state"])
        test_loss, test_acc = evaluate(model, test_loader, criterion, device)
        total_time = time.time() - t_start

        results[arch] = {
            "val_accuracy":  round(best_val_acc, 4),
            "test_accuracy": round(test_acc, 4),
            "trainable_params": trainable,
            "total_params": total,
            "training_time_sec": round(total_time, 1),
        }
        print(f"  -> Best Val Acc: {best_val_acc*100:.2f}% | Test Acc: {test_acc*100:.2f}% "
              f"| Time: {total_time:.0f}s")

    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}\nCOMPARISON SUMMARY\n{'='*60}")
    print(f"{'Model':<18}{'Val Acc':<12}{'Test Acc':<12}{'Params':<12}{'Time (s)':<10}")
    for arch, r in results.items():
        print(f"{arch:<18}{r['val_accuracy']*100:<12.2f}{r['test_accuracy']*100:<12.2f}"
              f"{r['total_params']:<12,}{r['training_time_sec']:<10}")

    print(f"\nSaved full results -> {RESULTS_FILE}")


if __name__ == "__main__":
    main()
