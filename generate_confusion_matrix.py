import torch
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
from torchvision import models, transforms
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────
CHECKPOINT = Path("model/checkpoints/efficientnet_b0_best.pt")
DATA_ROOT  = Path("data/plantvillage")  # your local data folder
DEVICE     = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ─── Load checkpoint ──────────────────────────────────────────────
ckpt        = torch.load(str(CHECKPOINT), map_location=DEVICE)
class_names = ckpt["class_names"]
num_classes = len(class_names)
print(f"Classes: {num_classes}")
print(f"Device: {DEVICE}")

# ─── Build model ──────────────────────────────────────────────────
model = models.efficientnet_b0(weights=None)
in_features = model.classifier[1].in_features
model.classifier = nn.Sequential(
    nn.Dropout(p=0.3),
    nn.Linear(in_features, 512),
    nn.ReLU(inplace=True),
    nn.Dropout(p=0.2),
    nn.Linear(512, num_classes),
)
model.load_state_dict(ckpt["model_state"])
model = model.to(DEVICE)
model.eval()

# ─── Load data ────────────────────────────────────────────────────
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],
                         [0.229,0.224,0.225]),
])

dataset = ImageFolder(str(DATA_ROOT), transform=transform)
loader  = DataLoader(dataset, batch_size=32, shuffle=False, num_workers=0)

# ─── Get predictions ──────────────────────────────────────────────
all_preds  = []
all_labels = []
with torch.no_grad():
    for i, (images, labels) in enumerate(loader):
        images = images.to(DEVICE)
        outputs = model(images)
        preds   = outputs.argmax(dim=1)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.numpy())
        print(f"Batch {i+1}/{len(loader)}", end="\r")

print(f"\nTotal samples: {len(all_preds)}")

# ─── Short class names for display ────────────────────────────────
short_names = [
    c.replace("Corn___","C:").replace("Tomato___","T:")
     .replace("_"," ")[:20]
    for c in class_names
]

# ─── Confusion Matrix ─────────────────────────────────────────────
cm = confusion_matrix(all_labels, all_preds)
cm_pct = cm.astype(float) / cm.sum(axis=1, keepdims=True) * 100

plt.figure(figsize=(14, 12))
sns.heatmap(
    cm_pct,
    annot=True, fmt=".1f",
    xticklabels=short_names,
    yticklabels=short_names,
    cmap="Greens",
    linewidths=0.5,
    linecolor="gray",
    cbar_kws={"label": "% of actual class"}
)
plt.title("AgriPulse AI — EfficientNet-B0 Confusion Matrix\n(Tomato + Corn, 14 classes)", 
          fontsize=14, fontweight="bold", pad=20)
plt.xlabel("Predicted Label", fontsize=11)
plt.ylabel("Actual Label", fontsize=11)
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.yticks(rotation=0, fontsize=8)
plt.tight_layout()
plt.savefig("confusion_matrix.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved: confusion_matrix.png")

# ─── Per class report ─────────────────────────────────────────────
print("\n" + classification_report(all_labels, all_preds, target_names=short_names))