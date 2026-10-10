"""
Copies ONE real leaf photo per disease from your PlantVillage dataset into
frontend/public/diseases/ with the names the app expects.

Usage (run from the frontend folder):
    python fill_disease_photos.py "C:\\path\\to\\dataset"

The dataset folder must contain one sub-folder per class, e.g.
    Tomato___Late_blight, Corn___Common_rust, Tomato___healthy ...
"""
import re, shutil, sys
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit(__doc__)

src = Path(sys.argv[1])
out = Path("public/diseases")
out.mkdir(parents=True, exist_ok=True)

def slug(key):
    return re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")

EXT = {".jpg", ".jpeg", ".png", ".webp"}
done = 0
for folder in sorted(p for p in src.rglob("*") if p.is_dir()):
    if not re.match(r"^(Tomato|Corn)___", folder.name):
        continue
    imgs = sorted(f for f in folder.iterdir() if f.suffix.lower() in EXT)
    if not imgs:
        continue
    pick = imgs[len(imgs) // 3]          # a photo from the middle, not the first
    dest = out / f"{slug(folder.name)}.jpg"
    shutil.copy(pick, dest)
    print("OK ", folder.name, "->", dest.name)
    done += 1
print(f"\n{done} photos copied to {out}")
