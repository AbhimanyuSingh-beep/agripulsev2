"""
main.py — AgriPulse AI FastAPI Backend
Crop Health Intelligence Module

Endpoints:
  GET  /health          — sanity check
  POST /predict         — crop disease prediction from uploaded image
  POST /remedy          — plain-language remedy via Claude API
  GET  /models          — architecture comparison from comparison_results.json
  POST /scans           — save the latest scanned photo of a disease
  GET  /scans           — list saved scan photos
  GET  /scans/{name}    — serve one saved scan photo

Run with:
  uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to sys.path so model/ is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.predict import router as predict_router
from backend.remedy  import router as remedy_router
from backend.models_info import router as models_router
from backend.scans import router as scans_router

# ─── App Setup ───────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "AgriPulse AI — Crop Health Intelligence",
    description = "Detects crop diseases from leaf photos and generates farmer-friendly remedies.",
    version     = "1.0.0",
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

# ─── CORS — allow frontend dev server ────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # CRA fallback
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ─── Routers ─────────────────────────────────────────────────────────────────
app.include_router(predict_router)
app.include_router(remedy_router)
app.include_router(models_router)
app.include_router(scans_router)


# ─── Health Check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health_check():
    """Quick liveness probe — returns OK if the server is up."""
    return {"status": "ok", "service": "AgriPulse AI Crop Health Intelligence"}


# ─── Root ─────────────────────────────────────────────────────────────────────
@app.get("/", tags=["System"])
async def root():
    return {
        "message":   "AgriPulse AI backend is running",
        "docs":      "/docs",
        "endpoints": ["/health", "/predict", "/remedy", "/models", "/scans"],
    }
