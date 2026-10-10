"""
models_info.py — /models Endpoint
AgriPulse AI | Crop Health Intelligence Module

GET /models
  Reads backend/comparison_results.json (written by train_compare.py in Colab)
  and returns the architecture comparison for the frontend model panel.
  Update the JSON after any retraining and the UI updates automatically.
"""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["Models"])

RESULTS_FILE = Path(__file__).parent / "comparison_results.json"

LABELS = {
    "efficientnet_b0": "EfficientNet-B0",
    "densenet121":     "DenseNet121",
    "resnet50":        "ResNet50",
    "resnet18":        "ResNet18",
}


def _params_str(n: int) -> str:
    return f"{n / 1e6:.1f}M"


@router.get("/models")
async def get_models():
    if not RESULTS_FILE.exists():
        raise HTTPException(status_code=404, detail="comparison_results.json not found in backend/.")

    with open(RESULTS_FILE, encoding="utf-8") as f:
        data = json.load(f)

    # Winner = highest test accuracy; ties broken by fewer parameters
    best_key  = max(data, key=lambda k: (data[k]["test_accuracy"], -data[k]["total_params"]))
    best      = data[best_key]
    best_name = LABELS.get(best_key, best_key)

    models = {}
    for key, m in sorted(data.items(), key=lambda kv: -kv[1]["test_accuracy"]):
        test_pct = round(m["test_accuracy"] * 100, 2)
        label    = LABELS.get(key, key)

        if key == best_key:
            why = (f"Best choice: highest test accuracy ({test_pct}%) with only "
                   f"{_params_str(m['total_params'])} parameters, so it is also light and fast to serve.")
        else:
            gap   = round((best["test_accuracy"] - m["test_accuracy"]) * 100, 2)
            ratio = m["total_params"] / best["total_params"]
            size  = (f"{ratio:.1f}x the parameters" if ratio >= 1
                     else f"{1 / ratio:.1f}x fewer parameters")
            why = f"{gap} points lower test accuracy than {best_name}, with {size}."

        models[key] = {
            "label":   label,
            "valAcc":  round(m["val_accuracy"] * 100, 2),
            "testAcc": test_pct,
            "params":  _params_str(m["total_params"]),
            "time":    f"{int(round(m['training_time_sec']))}s",
            "why":     why,
            "winner":  key == best_key,
        }

    return {"best": best_key, "models": models}
