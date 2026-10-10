"""
predict.py — /predict Endpoint
AgriPulse AI | Crop Health Intelligence Module

POST /predict
  Body: multipart/form-data with field "file" (image)
  Returns: { crop, disease, confidence, is_healthy, low_confidence_warning? }
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from model.inference import predict

router = APIRouter(tags=["Prediction"])

CONFIDENCE_THRESHOLD = 0.60  # Below this → show warning to user


class PredictionResponse(BaseModel):
    crop:                    str
    disease:                 str
    confidence:              float
    is_healthy:              bool
    confidence_percent:      str
    low_confidence_warning:  Optional[str] = None
    mock:                    bool = False


@router.post("/predict", response_model=PredictionResponse)
async def predict_disease(file: UploadFile = File(...)):
    """
    Accepts a leaf image (JPEG/PNG/WebP) and returns:
    - The detected crop type
    - The disease label (or "Healthy")
    - Confidence score (0–1)
    - A warning if confidence is below 60%

    Supports: image/jpeg, image/png, image/webp
    """
    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
    content_type  = file.content_type or ""
    if not any(t in content_type for t in ["jpeg", "png", "webp", "jpg"]):
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: '{content_type}'. Upload a JPEG, PNG, or WebP image."
        )

    # Read image bytes
    image_bytes = await file.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    # Run inference
    try:
        result = predict(image_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Model inference failed: {str(e)}"
        )

    # Build response
    confidence       = result["confidence"]
    confidence_pct   = f"{confidence * 100:.1f}%"
    low_conf_warning = None

    if confidence < CONFIDENCE_THRESHOLD:
        low_conf_warning = (
            f"Confidence is only {confidence_pct}. "
            "The model is not sure about this diagnosis. "
            "Please try a clearer, well-lit photo of the affected leaf against a plain background."
        )

    return PredictionResponse(
        crop                   = result["crop"],
        disease                = result["disease"],
        confidence             = confidence,
        is_healthy             = result["is_healthy"],
        confidence_percent     = confidence_pct,
        low_confidence_warning = low_conf_warning,
        mock                   = result.get("mock", False),
    )
