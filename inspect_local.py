"""
inspect_local.py — local-only checks, no dataset or Colab needed.
Put in the project root (agripulse-main\agripulse-main) and run:  python inspect_local.py
"""
import json
from pathlib import Path

import torch
from PIL import Image

ROOT = Path(__file__).parent

# ── 1. What is stored inside the checkpoint? ──────────────────────────────────
print("=" * 70)
print("1. CHECKPOINT CONTENTS")
print("=" * 70)
ck = torch.load(ROOT / "model" / "checkpoints" / "efficientnet_b0_best.pt",
                map_location="cpu", weights_only=False)
for k, v in ck.items():
    if k == "model_state":
        print(f"  {k}: state_dict with {len(v)} tensors")
    else:
        s = str(v)
        print(f"  {k}: {s if len(s) < 600 else s[:600] + ' ...'}")

# Compare any stored class list with class_labels.json
labels = json.load(open(ROOT / "backend" / "class_labels.json"))["classes"]
print(f"\n  class_labels.json has {len(labels)} entries; checkpoint num_classes = {ck.get('num_classes')}")
for key in ("class_names", "classes", "idx_to_class", "class_to_idx"):
    if key in ck:
        print(f"\n  Checkpoint stores '{key}'. Compare with class_labels.json:")
        stored = ck[key]
        if isinstance(stored, dict):
            stored = [n for n, _ in sorted(stored.items(), key=lambda kv: kv[1])] \
                     if key == "class_to_idx" else [stored[i] for i in sorted(stored)]
        for i, name in enumerate(stored):
            mine = labels[i]["folder"] if i < len(labels) else "(missing)"
            flag = "" if name.split("___")[-1].replace("_", " ").lower() == \
                         mine.split("___")[-1].replace("_", " ").lower() else "   <-- MISMATCH"
            print(f"    [{i:2}] checkpoint: {name:45} labels file: {mine}{flag}")

# ── 2. Are the demo images PlantVillage-style or real-world photos? ───────────
print("\n" + "=" * 70)
print("2. DEMO IMAGE SIZES  (PlantVillage images are 256 x 256)")
print("=" * 70)
for p in sorted((ROOT / "demo_samples").rglob("*")):
    if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
        with Image.open(p) as im:
            print(f"  {p.name:38} {im.width:5} x {im.height:<5}  {p.stat().st_size / 1024:7.0f} KB")
