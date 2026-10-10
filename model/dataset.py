"""
dataset.py — Data Loading & Preprocessing
AgriPulse AI | Crop Health Intelligence Module

Updated for Corn + Tomato dataset (pivoted from Potato+Tomato after unsatisfactory results).
Folder structure (flat — no crop subfolders):
  data/plantvillage_balanced/
    Potato___Early_blight/
    Potato___Late_blight/
    Potato___healthy/
    Tomato___Bacterial_spot/
    Tomato___Early_blight/
    ... etc
"""

import os
from pathlib import Path
from typing import Tuple

import torch
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms

# ─── Constants ────────────────────────────────────────────────────────────────
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]
IMAGE_SIZE    = 224

VALID_CROPS = {"Corn", "Tomato"}

# ─── Transforms ───────────────────────────────────────────────────────────────
TRAIN_TRANSFORMS = transforms.Compose([
    transforms.Resize((IMAGE_SIZE + 32, IMAGE_SIZE + 32)),
    transforms.RandomCrop(IMAGE_SIZE),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.3),
    transforms.RandomRotation(degrees=30),
    transforms.ColorJitter(brightness=0.3, contrast=0.3,
                           saturation=0.2, hue=0.1),
    transforms.RandomGrayscale(p=0.05),
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])

VAL_TRANSFORMS = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])


# ─── Label helpers ────────────────────────────────────────────────────────────
def parse_folder_name(folder: str) -> dict:
    """
    Parse flat folder names like 'Potato___Early_blight' or 'Tomato___healthy'
    into structured label info.
    """
    parts = folder.split("___")
    if len(parts) != 2:
        return None

    crop, disease_raw = parts
    if crop not in VALID_CROPS:
        return None

    disease = disease_raw.replace("_", " ").strip()
    is_healthy = disease.lower() == "healthy"

    return {
        "folder":     folder,
        "crop":       crop,
        "disease":    "Healthy" if is_healthy else disease,
        "is_healthy": is_healthy,
    }


def filter_dataset(data_root: str) -> list:
    """
    Return only Corn and Tomato folders from the flat directory.
    """
    valid_folders = []
    for folder in sorted(os.listdir(data_root)):
        full_path = os.path.join(data_root, folder)
        if not os.path.isdir(full_path):
            continue
        info = parse_folder_name(folder)
        if info is not None:
            valid_folders.append(folder)
    return valid_folders


# ─── Custom ImageFolder that filters to Potato/Tomato only ───────────────────
class CornTomatoDataset(datasets.ImageFolder):
    def __init__(self, root, transform=None):
        # Filter classes before calling super().__init__
        super().__init__(root, transform=transform)

        # Keep only Corn and Tomato classes
        valid_classes = [
            c for c in self.classes
            if c.startswith("Corn") or c.startswith("Tomato")
        ]
        valid_class_to_idx = {c: i for i, c in enumerate(sorted(valid_classes))}

        # Remap samples
        self.classes = sorted(valid_classes)
        self.class_to_idx = valid_class_to_idx
        self.samples = [
            (path, valid_class_to_idx[self.classes[old_idx]])
            for path, old_idx in self.samples
            if self.classes[old_idx] in valid_class_to_idx
        ]
        self.targets = [s[1] for s in self.samples]

        print(f"  Found {len(self.classes)} classes: {self.classes}")
        print(f"  Total images: {len(self.samples)}")


# ─── Class weight computation (counters Corn/Tomato imbalance) ───────────────
def compute_class_weights(dataset, indices: list) -> torch.Tensor:
    """
    Computes inverse-frequency class weights from the TRAINING split only.

    Rarer classes (e.g. Corn, ~17.5% of this dataset) get a higher weight,
    so the loss function penalizes mistakes on them more heavily — directly
    countering the model's tendency to default to the majority class (Tomato).

    Weights are normalized so their average is 1.0, keeping overall loss
    magnitude stable and comparable across runs.
    """
    num_classes = len(dataset.classes)
    counts = torch.zeros(num_classes)

    for idx in indices:
        _, label = dataset.samples[idx]
        counts[label] += 1

    counts = torch.clamp(counts, min=1)  # avoid divide-by-zero
    total = counts.sum()
    weights = total / (num_classes * counts)

    print("\n⚖️  Class weights (imbalance correction):")
    for i, cls in enumerate(dataset.classes):
        print(f"   {cls:<50} count={int(counts[i]):>5}  weight={weights[i]:.3f}")

    return weights


# ─── Main function ────────────────────────────────────────────────────────────
def create_data_loaders(
    data_root: str,
    batch_size: int = 32,
    val_split: float = 0.1,
    test_split: float = 0.1,
    num_workers: int = 2,
) -> Tuple[DataLoader, DataLoader, DataLoader, list, torch.Tensor]:
    """
    Creates train/val/test DataLoaders from the Corn+Tomato flat dataset.

    Returns:
        train_loader, val_loader, test_loader, class_names, class_weights
    """
    print(f"\nLoading dataset from: {data_root}")

    # Load full dataset with train transforms first (we'll override for val/test)
    full_dataset = CornTomatoDataset(data_root, transform=TRAIN_TRANSFORMS)
    class_names  = full_dataset.classes
    total        = len(full_dataset)

    # Compute split sizes
    test_size  = int(total * test_split)
    val_size   = int(total * val_split)
    train_size = total - val_size - test_size

    # Split
    train_ds, val_ds, test_ds = random_split(
        full_dataset,
        [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(42),
    )

    # Override transforms for val and test (no augmentation)
    val_ds.dataset  = CornTomatoDataset(data_root, transform=VAL_TRANSFORMS)
    test_ds.dataset = CornTomatoDataset(data_root, transform=VAL_TRANSFORMS)

    print(f"  Split → Train: {train_size} | Val: {val_size} | Test: {test_size}")

    # Compute weights from the TRAINING split's actual class distribution
    class_weights = compute_class_weights(full_dataset, train_ds.indices)

    train_loader = DataLoader(
        train_ds, batch_size=batch_size,
        shuffle=True, num_workers=num_workers, pin_memory=True
    )
    val_loader = DataLoader(
        val_ds, batch_size=batch_size,
        shuffle=False, num_workers=num_workers, pin_memory=True
    )
    test_loader = DataLoader(
        test_ds, batch_size=batch_size,
        shuffle=False, num_workers=num_workers, pin_memory=True
    )

    return train_loader, val_loader, test_loader, class_names, class_weights


# ─── Quick test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else "data/plantvillage"
    train_loader, val_loader, test_loader, classes, weights = create_data_loaders(root)
    print(f"\nClasses ({len(classes)}):")
    for i, c in enumerate(classes):
        print(f"  [{i}] {c}")
    images, labels = next(iter(train_loader))
    print(f"\nBatch shape: {images.shape}")
    print(f"Label range: {labels.min().item()} – {labels.max().item()}")
