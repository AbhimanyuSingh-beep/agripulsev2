"""Quick debug script — run from agripulse/ directory"""
import sys, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("STEP 1: Checking file existence")
scripted  = Path("model/checkpoints/model_scripted.pt")
best      = Path("model/checkpoints/best_model.pt")
labels    = Path("backend/class_labels.json")

print(f"  model_scripted.pt : {'EXISTS ' + str(scripted.stat().st_size//1024) + ' KB' if scripted.exists() else 'MISSING ❌'}")
print(f"  best_model.pt     : {'EXISTS ' + str(best.stat().st_size//1024) + ' KB' if best.exists() else 'MISSING ❌'}")
print(f"  class_labels.json : {'EXISTS' if labels.exists() else 'MISSING ❌'}")

print("\nSTEP 2: Reading class_labels.json")
with open(labels) as f:
    data = json.load(f)
print(f"  num_classes: {data['num_classes']}")
for c in data["classes"]:
    print(f"    [{c['index']}] {c['crop']} — {c['disease']} (healthy={c['is_healthy']})")

print("\nSTEP 3: Loading model")
from model.inference import _is_mock, _class_labels, predict
print(f"  Mock mode : {_is_mock}")
print(f"  Labels loaded: {len(_class_labels)} classes")

print("\nSTEP 4: Running test prediction on dummy image")
from PIL import Image
import io
# Create a simple green test image
img = Image.new("RGB", (224, 224), color=(34, 139, 34))
buf = io.BytesIO()
img.save(buf, format="JPEG")
result = predict(buf.getvalue())
print(f"  Result: {result}")
print("="*60)
