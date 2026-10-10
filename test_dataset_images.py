"""
test_dataset_images.py — pipeline check using real PlantVillage images.

Usage (from the project root, same terminal as test_demo.py):
    python test_dataset_images.py "C:\\path\\to\\plantvillage_folder" 20

The folder must contain class subfolders like Tomato___healthy, Corn___Common_rust...
Samples N images per class (default 20), runs them through the deployed model and
prints per-class accuracy. These images may have been in the training split, so the
numbers are optimistic; this checks the pipeline (labels / preprocessing), not accuracy.
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, ".")
from model.inference import predict

root = Path(sys.argv[1])
n    = int(sys.argv[2]) if len(sys.argv) > 2 else 20
EXT  = {".jpg", ".jpeg", ".png", ".webp"}

folders = sorted(d.name for d in root.iterdir()
                 if d.is_dir() and (d.name.startswith("Corn") or d.name.startswith("Tomato")))
print(f"\n{len(folders)} classes found (training order):")
for i, f in enumerate(folders):
    print(f"  [{i:2}] {f}")
print()

random.seed(0)
total = correct = 0
for i, f in enumerate(folders):
    imgs   = [p for p in (root / f).iterdir() if p.suffix.lower() in EXT]
    sample = random.sample(imgs, min(n, len(imgs)))
    right, wrong = 0, {}
    for p in sample:
        idx = predict(p.read_bytes())["class_index"]
        if idx == i:
            right += 1
        else:
            wrong[idx] = wrong.get(idx, 0) + 1
    total += len(sample); correct += right
    extra = f"   wrong -> {wrong}" if wrong else ""
    print(f"[{i:2}] {f:48} {right:3}/{len(sample):<3}{extra}")

print(f"\nOverall: {correct}/{total} = {100 * correct / max(total, 1):.1f}%")
