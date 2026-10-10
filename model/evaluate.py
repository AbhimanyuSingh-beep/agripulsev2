"""
evaluate.py — Test Set Evaluation + Confusion Matrix
AgriPulse AI | Crop Health Intelligence Module

Usage:
    python model/evaluate.py --data_root data/plantvillage

Loads the best checkpoint, runs on the test split, and saves:
  - plots/confusion_matrix.png   (for the exhibition poster)
  - Prints final test accuracy + per-class breakdown
"""

import sys
import argparse
import json
from pathlib import Path

import torch
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from model.dataset import create_data_loaders
from model.train import build_model

PROJECT_ROOT   = Path(__file__).parent.parent
CHECKPOINT_DIR = PROJECT_ROOT / "model" / "checkpoints"
PLOTS_DIR      = PROJECT_ROOT / "plots"
LABELS_FILE    = PROJECT_ROOT / "backend" / "class_labels.json"

PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def load_model(checkpoint_path: Path, device: torch.device):
    ckpt = torch.load(checkpoint_path, map_location=device)
    num_classes  = ckpt["num_classes"]
    class_names  = ckpt["class_names"]
    model = build_model(num_classes, unfreeze_last_n=3)
    model.load_state_dict(ckpt["model_state"])
    model = model.to(device)
    model.eval()
    return model, class_names


@torch.no_grad()
def run_test_evaluation(model, test_loader, num_classes, device):
    all_preds, all_labels = [], []

    for images, labels in test_loader:
        images = images.to(device)
        outputs = model(images)
        preds   = outputs.argmax(dim=1).cpu().numpy()
        all_preds.extend(preds)
        all_labels.extend(labels.numpy())

    all_preds  = np.array(all_preds)
    all_labels = np.array(all_labels)
    accuracy   = (all_preds == all_labels).mean()
    return all_preds, all_labels, accuracy


def plot_confusion_matrix(preds, labels, class_names, plots_dir: Path):
    from sklearn.metrics import confusion_matrix, classification_report

    cm = confusion_matrix(labels, preds, labels=list(range(len(class_names))))

    # Normalize per-row (recall per class)
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
    cm_norm = np.nan_to_num(cm_norm)

    # Shorten class names for readability on the plot
    short_names = []
    for name in class_names:
        parts = name.split("___")
        crop  = parts[0].split("_")[0][:4]   # e.g. "Toma"
        if len(parts) > 1:
            disease = parts[1].replace("_", " ")
            # Shorten to first 14 chars
            disease = disease[:14]
        else:
            disease = "?"
        short_names.append(f"{crop} — {disease}")

    n = len(class_names)
    fig, ax = plt.subplots(figsize=(max(12, n * 0.7), max(10, n * 0.6)))

    im = ax.imshow(cm_norm, interpolation="nearest", cmap="YlOrRd", vmin=0, vmax=1)
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02, label="Recall")

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(short_names, rotation=45, ha="right", fontsize=7)
    ax.set_yticklabels(short_names, fontsize=7)
    ax.set_xlabel("Predicted Label", fontsize=11)
    ax.set_ylabel("True Label",      fontsize=11)
    ax.set_title("Confusion Matrix — AgriPulse AI\n(Normalized by true class)", fontsize=13)

    # Annotate cells with recall values
    thresh = cm_norm.max() / 2.0
    for i in range(n):
        for j in range(n):
            val = cm_norm[i, j]
            if val > 0.05:  # only annotate non-trivial cells
                ax.text(j, i, f"{val:.2f}",
                        ha="center", va="center", fontsize=6,
                        color="white" if val > thresh else "black")

    fig.tight_layout()
    out_path = plots_dir / "confusion_matrix.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✅ Confusion matrix saved → {out_path}")

    # Also print classification report to console
    print("\n📊 Classification Report:")
    print(classification_report(labels, preds, target_names=class_names))


def main():
    parser = argparse.ArgumentParser(description="Evaluate AgriPulse model on test set")
    parser.add_argument("--data_root",  type=str, default="data/plantvillage")
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--num_workers",type=int, default=4)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🚀 Evaluating on: {device}")

    ckpt_path = CHECKPOINT_DIR / "best_model.pt"
    if not ckpt_path.exists():
        print(f"❌ No checkpoint found at {ckpt_path}. Run train.py first.")
        sys.exit(1)

    model, class_names = load_model(ckpt_path, device)
    print(f"✅ Loaded checkpoint: {ckpt_path}")
    print(f"   Classes: {len(class_names)}")

    data_root = PROJECT_ROOT / args.data_root
    _, _, test_loader, _ = create_data_loaders(
        str(data_root), batch_size=args.batch_size, num_workers=args.num_workers
    )

    print("\n⏳ Running test set evaluation...")
    preds, labels, accuracy = run_test_evaluation(model, test_loader, len(class_names), device)

    print(f"\n🏆 Test Accuracy: {accuracy * 100:.2f}%")

    plot_confusion_matrix(preds, labels, class_names, PLOTS_DIR)

    # Update README placeholder
    summary_file = PLOTS_DIR / "accuracy_summary.txt"
    with open(summary_file, "w") as f:
        f.write(f"AgriPulse AI — Model Performance Summary\n")
        f.write(f"=========================================\n")
        f.write(f"Model:         MobileNetV2 (ImageNet pretrained, fine-tuned)\n")
        f.write(f"Dataset:       PlantVillage (Tomato, Potato, Corn, Grape)\n")
        f.write(f"Num Classes:   {len(class_names)}\n")
        f.write(f"Test Accuracy: {accuracy * 100:.2f}%\n")
    print(f"✅ Saved accuracy summary → {summary_file}")


if __name__ == "__main__":
    main()
