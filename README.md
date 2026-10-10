# 🌿 AgriPulse AI — Crop Health Intelligence

> Real-time crop disease detection using PyTorch + FastAPI + React
> Built by **Abhimanyu Singh** (VIT Bhopal)

Upload a photo of a crop leaf → the AI tells you the disease and what to do about it, in plain language, read aloud.

**Supported crops:** 🍅 Tomato · 🌽 Corn
**Disease classes:** 14 (including healthy variants)

---

## ⚠️ IMPORTANT: Model Checkpoints (Download Required for Compare Mode)

Four CNN models were trained on the PlantVillage dataset (Corn + Tomato, 14 classes) and compared:

| Model | Val Acc | Test Acc | Params | In this zip? |
|-------|---------|----------|--------|--------------|
| **EfficientNet-B0** (final model) | 98.23% | **98.05%** | 4.7M | ✅ Yes |
| ResNet18 | 97.59% | 97.36% | 11.4M | ❌ Google Drive |
| ResNet50 | 97.68% | 97.14% | 24.6M | ❌ Google Drive |
| DenseNet121 | [XX.XX]% | [XX.XX]% | [XX]M | ❌ Google Drive |

**EfficientNet-B0** achieved the best accuracy with the fewest parameters, so it is the main model of the app and is **already included** at:

```
model/checkpoints/efficientnet_b0_best.pt
```

Due to the 100 MB submission size limit, the other three checkpoints are stored on Google Drive.

### 📥 Where to download

**Google Drive folder:** https://drive.google.com/drive/folders/1VOtY2uk7PRlTvFfJVky_RF4hzLckDFze?usp=sharing

Files in that folder:
- `resnet18_best.pt`
- `resnet50_best.pt`
- `densenet121_best.pt`

### 📂 Where to paste

1. Download the three `.pt` files from the link above.
2. Paste them into the project's checkpoints folder:

```
agripulse-main/
└── model/
    └── checkpoints/
        ├── efficientnet_b0_best.pt   ← already included
        ├── resnet18_best.pt          ← paste here
        ├── resnet50_best.pt          ← paste here
        └── densenet121_best.pt       ← paste here
```

3. Restart the backend. Compare mode will now use all 4 models.

> **The app works without the Drive files.** Prediction runs on EfficientNet-B0 alone; only the multi-model Compare mode needs the extra three checkpoints.

> `node_modules/`, `venv/` and `__pycache__/` were removed to reduce size. The setup steps below recreate them.

---

## 📋 Prerequisites

| Software | Why needed | Download |
|---|---|---|
| **Python 3.10+** | Runs the AI backend | https://www.python.org/downloads/ |
| **Node.js 18+** | Runs the React frontend | https://nodejs.org/en/download |

> On Windows, tick ✅ **"Add Python to PATH"** during Python installation.

Verify:
```bash
python --version
node --version
```

---

## 📁 Project Structure

```
agripulse-main/
├── backend/                 # FastAPI server
│   ├── main.py              # App entry point
│   ├── predict.py           # POST /predict
│   ├── remedy.py            # POST /remedy (Gemini AI)
│   ├── class_labels.json    # 14 Corn + Tomato class names (training order)
│   ├── requirements.txt     # Python packages
│   └── .env.example         # Copy to .env and add API key
├── frontend/                # React + Vite web app
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/      # ImageUploader, ResultCard, AudioPlayer
│   └── package.json
├── model/                   # ML code
│   ├── dataset.py           # Corn + Tomato data loading + augmentation
│   ├── train.py             # Training script
│   ├── train_compare.py     # Trains/compares the 4 models
│   ├── evaluate.py          # Accuracy + confusion matrix
│   ├── export.py            # TorchScript export
│   ├── inference.py         # Prediction logic (used by backend)
│   ├── colab_training_guide.py
│   └── checkpoints/         # Model weights (.pt)
├── demo_samples/            # Sample leaf images for testing
├── comparison_results.json  # Results of the 4-model comparison
├── AgriPulse_AI_Final_Review (PPT)
├── run_backend.ps1
└── README.md
```

---

## 🚀 Setup & Run

### Step 1 — Backend

Open a terminal inside the project folder (`agripulse-main/`):

```bash
# Create virtual environment (once)
python -m venv venv

# Activate it (every new terminal)
venv\Scripts\activate            # Windows
# source venv/bin/activate       # Mac/Linux

# Install packages (2–5 min)
pip install -r backend/requirements.txt
```

### Step 2 — API Key (Gemini)

The remedy feature uses Google Gemini. Get a **free** key at https://aistudio.google.com/app/apikey, then:

```bash
copy backend\.env.example backend\.env        # Windows
# cp backend/.env.example backend/.env        # Mac/Linux
```

Open `backend/.env` and fill in:

```
GEMINI_API_KEY_1=paste_your_key_here
GEMINI_API_KEY_2=paste_your_key_here
GEMINI_API_KEY_3=paste_your_key_here
```

(The same key can be used for all three.)

### Step 3 — Start the backend

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Step 4 — Start the frontend

Open a **new terminal**:

```bash
cd frontend
npm install        # once
npm run dev
```

Frontend: http://localhost:5173

### Step 5 — Use the app

1. Open **Chrome or Edge** → http://localhost:5173
2. Upload a leaf photo (or use one from `demo_samples/`)
3. Click **Analyze Leaf**
4. See the disease, confidence and remedy. Use **Play Aloud** to hear it.

---

## 🌿 Disease Classes (14)

| Crop | Classes |
|------|---------|
| Tomato (10) | Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Spider Mites, Target Spot, Yellow Leaf Curl Virus, Mosaic Virus, Healthy |
| Corn (4) | Cercospora / Gray Leaf Spot, Common Rust, Northern Leaf Blight, Healthy |

---

## 🧠 Model Training

Dataset: PlantVillage — https://www.kaggle.com/datasets/emmarex/plantdisease (Corn and Tomato classes only)

All 4 models were trained in Google Colab (T4 GPU) for 20 epochs with transfer learning (ImageNet pretrained) and class weighting to handle class imbalance. Input size 224×224, Adam optimizer, CrossEntropy loss.

### Option A — Google Colab (free GPU)
Follow `model/colab_training_guide.py`, then place the downloaded `.pt` file in `model/checkpoints/` and `class_labels.json` in `backend/`.

### Option B — Local (CUDA GPU)
```bash
# Place the dataset at data/plantvillage/ (one subfolder per class)
python model/train.py --data_root data/plantvillage --epochs 20
python model/train_compare.py --data_root data/plantvillage
python model/evaluate.py --data_root data/plantvillage
python model/export.py
```

Full comparison numbers are saved in `comparison_results.json`.

---

## 🔌 API Reference

### POST `/predict`
```
Body: multipart/form-data  { file: <image> }
Returns: {
  "crop": "Tomato",
  "disease": "Late Blight",
  "confidence": 0.94,
  "is_healthy": false,
  "confidence_percent": "94.0%",
  "low_confidence_warning": null
}
```

### POST `/remedy`
```
Body: { "crop": "Tomato", "disease": "Late Blight" }
Returns: {
  "explanation": "Late Blight is a fungal disease caused by...",
  "remedy": "1. Remove infected leaves...\n2. Apply copper fungicide..."
}
```

---

## ⚠️ Known Limitations

- The model is trained on **PlantVillage** (lab-style photos of a single leaf on a plain background). It works best on similar images.
- Field photos with complex backgrounds, and crops outside **Corn and Tomato**, can give confident but wrong answers. The 60% confidence warning cannot catch every such case.
- For the most reliable results, use the images in `demo_samples/`.

---

## ❓ Troubleshooting

| Problem | Fix |
|---|---|
| `python is not recognized` | Reinstall Python and tick "Add to PATH" |
| `ModuleNotFoundError: No module named 'fastapi'` | Activate the venv: `venv\Scripts\activate` |
| `No trained model found / MOCK mode` | `efficientnet_b0_best.pt` is missing from `model/checkpoints/`, or its name doesn't match `model/inference.py` |
| Compare mode shows fewer than 4 models | Download the other 3 `.pt` files from the Google Drive link above and paste them into `model/checkpoints/` |
| Frontend shows "Cannot connect to backend" | Make sure the backend is running on port 8000 (check `/health`) |
| No remedy text | Add your Gemini key in `backend/.env` |
| "Play Aloud" not working | Use Chrome or Edge (Web Speech API) |
| Wrong disease labels | `class_labels.json` must match the class order used in training (14 Corn + Tomato classes) |

**Notes**
- **Mock mode:** with no trained model, the backend returns simulated predictions so the UI can still be tested.
- **Confidence threshold:** predictions below 60% show a "try a clearer photo" warning.

---

## 🎪 Demo Quick Start

```bash
# Terminal 1 — Backend
venv\Scripts\activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Open Chrome → http://localhost:5173 and use images from `demo_samples/`.

---

*AgriPulse AI · Crop Health Intelligence · Made by Abhimanyu Singh*
