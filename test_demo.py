"""
test_demo.py — run every image in demo_samples through the current model.
Place in the project root (the agripulse folder), then run:  python test_demo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, ".")
from model.inference import predict

for p in sorted(Path("demo_samples").rglob("*")):
    if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
        r = predict(p.read_bytes())
        top = ", ".join(f"{x['label'].split('___')[-1]} {x['prob']:.2f}" for x in r["top3"])
        print(f"{p.name:38} -> {r['crop']} {r['disease']} ({r['confidence']:.2f}) | {top}")
