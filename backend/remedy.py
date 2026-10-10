"""
remedy.py — /remedy Endpoint
AgriPulse AI | Crop Health Intelligence Module

POST /remedy
  Body: { "crop": str, "disease": str }
  Returns: { "explanation": str, "remedy": str }

Strategy:
  1. Check in-memory + disk cache first (instant response)
  2. Try Gemini API if a valid key (AIza...) is configured
  3. Fall back to the built-in disease knowledge base (always works, no key needed)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel

load_dotenv()  # Load keys from backend/.env

router = APIRouter(tags=["Remedy"])

# ─── Built-in Disease Knowledge Base ─────────────────────────────────────────
# Covers every disease in class_labels.json. Always available, no API needed.
_KNOWLEDGE_BASE: dict[str, dict] = {
    # ── Potato ────────────────────────────────────────────────────────────────
    "potato|early blight": {
        "explanation": (
            "Early blight is a fungal disease caused by Alternaria solani. "
            "It creates dark brown spots with yellow rings on older leaves, "
            "especially in warm, humid weather."
        ),
        "remedy": (
            "1. Remove and destroy infected leaves immediately — do not compost them.\n"
            "2. Spray the plant with a copper-based fungicide or mancozeb every 7–10 days.\n"
            "3. Water the plants at the base in the morning so leaves dry quickly.\n"
            "4. Avoid overcrowding plants — good airflow prevents fungal spread.\n"
            "5. After harvest, clear all plant debris from the field."
        ),
    },
    "potato|late blight": {
        "explanation": (
            "Late blight is a dangerous disease caused by Phytophthora infestans. "
            "It causes dark, water-soaked lesions on leaves and tubers and spreads "
            "very fast in cool, wet conditions."
        ),
        "remedy": (
            "1. Remove and burn all infected plant parts immediately — do not leave them in the field.\n"
            "2. Spray with a systemic fungicide (metalaxyl + mancozeb) every 5–7 days.\n"
            "3. Avoid overhead watering — wet leaves spread the disease fast.\n"
            "4. Hill up soil around plants to protect tubers from infection.\n"
            "5. Harvest tubers early if the disease is spreading quickly."
        ),
    },
    "potato|healthy": {
        "explanation": "Your potato plant looks healthy! The leaves are green and show no signs of disease.",
        "remedy": (
            "1. Keep watering regularly at the base of the plant, not on leaves.\n"
            "2. Check leaves every few days for early signs of spots or discolouration.\n"
            "3. Apply balanced fertilizer (NPK) once a month during growing season.\n"
            "4. Control weeds around plants to reduce pest and disease risk."
        ),
    },
    # ── Tomato ────────────────────────────────────────────────────────────────
    "tomato|bacterial spot": {
        "explanation": (
            "Bacterial spot is caused by Xanthomonas bacteria. "
            "It creates small, dark, water-soaked spots on leaves and fruit, "
            "spreading quickly through rain splash and infected tools."
        ),
        "remedy": (
            "1. Remove all visibly infected leaves and put them in a sealed bag — do not compost.\n"
            "2. Spray with copper-based bactericide (copper hydroxide) every 7 days.\n"
            "3. Avoid working with plants when they are wet to prevent spreading bacteria.\n"
            "4. Disinfect your tools with diluted bleach (1:9 ratio) between plants.\n"
            "5. Rotate crops — do not grow tomatoes in the same spot next season."
        ),
    },
    "tomato|early blight": {
        "explanation": (
            "Early blight is caused by the fungus Alternaria solani. "
            "It starts as brown spots with yellow halos on lower leaves "
            "and works upward, weakening the plant over time."
        ),
        "remedy": (
            "1. Prune and remove lower infected leaves as soon as you see spots.\n"
            "2. Apply mancozeb or chlorothalonil fungicide spray every 7–10 days.\n"
            "3. Add mulch around the base to prevent soil from splashing onto leaves.\n"
            "4. Water in the morning at the base only, never overhead.\n"
            "5. Feed the plant with potassium-rich fertilizer to boost immunity."
        ),
    },
    "tomato|late blight": {
        "explanation": (
            "Late blight is caused by Phytophthora infestans and is one of the most "
            "destructive tomato diseases. It forms large, dark, oily-looking patches "
            "on leaves and fruit very quickly in cool, wet weather."
        ),
        "remedy": (
            "1. Act immediately — remove and destroy all infected plant material by burning.\n"
            "2. Apply a systemic fungicide (metalaxyl or cymoxanil) right away.\n"
            "3. Avoid watering from above — use drip irrigation if possible.\n"
            "4. Space plants well apart so air can circulate between them.\n"
            "5. If more than 30% of the plant is infected, remove the entire plant to save neighbors."
        ),
    },
    "tomato|leaf mold": {
        "explanation": (
            "Leaf mold is caused by the fungus Passalora fulva. "
            "It appears as pale green or yellow patches on the upper leaf surface "
            "with an olive-green mold on the underside, thriving in high humidity."
        ),
        "remedy": (
            "1. Improve ventilation — open greenhouse vents or space plants further apart.\n"
            "2. Remove and destroy severely infected leaves immediately.\n"
            "3. Spray with chlorothalonil or copper fungicide every 7 days.\n"
            "4. Reduce humidity by watering in the morning only at the base.\n"
            "5. Avoid splashing water on leaves — wet conditions allow the fungus to spread."
        ),
    },
    "tomato|septoria leaf spot": {
        "explanation": (
            "Septoria leaf spot is a fungal disease showing as small, circular spots "
            "with dark borders and light grey centres on lower leaves first. "
            "It spreads upward in wet weather and can defoliate the whole plant."
        ),
        "remedy": (
            "1. Remove infected leaves from the bottom of the plant first.\n"
            "2. Apply mancozeb or copper-based fungicide every 7–10 days.\n"
            "3. Avoid wetting the foliage when watering.\n"
            "4. Mulch around the base to prevent soil splash.\n"
            "5. Clean up all plant debris at the end of the season."
        ),
    },
    "tomato|spider mites two spotted spider mite": {
        "explanation": (
            "Two-spotted spider mites are tiny pests (almost invisible) that suck sap "
            "from leaves, causing yellow speckles and fine webbing. "
            "They thrive in hot, dry weather and multiply very fast."
        ),
        "remedy": (
            "1. Spray plants with a strong jet of water to knock mites off leaves.\n"
            "2. Apply neem oil spray (5 ml per litre of water) every 5 days.\n"
            "3. Use miticide (abamectin or bifenazate) if infestation is severe.\n"
            "4. Increase humidity around plants — mites dislike moisture.\n"
            "5. Remove heavily infested leaves and dispose in a sealed bag."
        ),
    },
    "tomato|target spot": {
        "explanation": (
            "Target spot is caused by the fungus Corynespora cassiicola. "
            "It creates circular lesions with distinct rings (like a target) "
            "on leaves, stems, and fruit, spreading in warm, humid weather."
        ),
        "remedy": (
            "1. Remove and destroy infected plant parts.\n"
            "2. Spray with chlorothalonil or azoxystrobin fungicide every 7 days.\n"
            "3. Avoid planting tomatoes in the same area for at least 2 years.\n"
            "4. Maintain good airflow by pruning overcrowded branches.\n"
            "5. Water at the base only to keep leaves dry."
        ),
    },
    "tomato|tomato yellowleaf  curl virus": {
        "explanation": (
            "Tomato Yellow Leaf Curl Virus (TYLCV) is spread by whiteflies. "
            "Infected plants show upward curling of leaves, yellowing, and stunted growth. "
            "There is no cure — prevention through whitefly control is essential."
        ),
        "remedy": (
            "1. Remove and destroy infected plants immediately to stop the virus spreading.\n"
            "2. Control whiteflies with yellow sticky traps placed near plants.\n"
            "3. Spray insecticide (imidacloprid or thiamethoxam) to kill whiteflies.\n"
            "4. Use reflective silver mulch to repel whiteflies from the field.\n"
            "5. Next season, plant virus-resistant tomato varieties."
        ),
    },
    "tomato|tomato mosaic virus": {
        "explanation": (
            "Tomato Mosaic Virus causes mottled light and dark green patterns on leaves, "
            "distorted growth, and reduced fruit quality. "
            "It spreads through infected hands, tools, and seeds."
        ),
        "remedy": (
            "1. Remove and destroy infected plants — there is no chemical cure.\n"
            "2. Wash hands with soap before and after handling plants.\n"
            "3. Disinfect all tools with 10% bleach solution between uses.\n"
            "4. Control aphids and other sap-sucking insects that can spread the virus.\n"
            "5. Use certified virus-free seeds in the next planting season."
        ),
    },
    "tomato|healthy": {
        "explanation": "Your tomato plant looks healthy! No signs of disease are visible on the leaf.",
        "remedy": (
            "1. Water regularly at the base in the morning — avoid wetting leaves.\n"
            "2. Check weekly for early signs of spots, yellowing, or pests.\n"
            "3. Apply balanced NPK fertilizer once a month.\n"
            "4. Prune suckers to improve airflow and reduce disease risk."
        ),
    },
}

# Normalize a key for lookup (lowercase, strip extra spaces)
def _kb_key(crop: str, disease: str) -> str:
    return f"{crop.strip().lower()}|{disease.strip().lower()}"


def _lookup_knowledge_base(crop: str, disease: str) -> Optional[dict]:
    """
    Try exact match, then fuzzy prefix match.
    Returns {"explanation": ..., "remedy": ...} or None.
    """
    key = _kb_key(crop, disease)
    if key in _KNOWLEDGE_BASE:
        return _KNOWLEDGE_BASE[key]

    # Fuzzy: try if any KB key starts with our disease token
    disease_lower = disease.strip().lower()
    crop_lower    = crop.strip().lower()
    for kb_key, val in _KNOWLEDGE_BASE.items():
        kb_crop, kb_disease = kb_key.split("|", 1)
        if kb_crop == crop_lower and (
            kb_disease.startswith(disease_lower[:8]) or
            disease_lower.startswith(kb_disease[:8])
        ):
            return val

    return None


# ─── Persistent disk cache ────────────────────────────────────────────────────
_CACHE_FILE = Path(__file__).parent / "remedy_cache.json"


def _load_cache() -> dict:
    if _CACHE_FILE.exists():
        try:
            with open(_CACHE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_cache(cache: dict) -> None:
    try:
        with open(_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


_remedy_cache: dict[str, dict] = _load_cache()


# ─── Pydantic models ──────────────────────────────────────────────────────────
class RemedyRequest(BaseModel):
    crop:    str
    disease: str


class RemedyResponse(BaseModel):
    explanation: str
    remedy:      str
    cached:      bool = False
    source:      str  = "knowledge_base"   # "gemini" | "knowledge_base" | "cache"


# ─── Gemini helper (optional — only used when a real AIza key is present) ─────
def _has_valid_gemini_key() -> bool:
    """Real Gemini API keys start with 'AIza'. AQ.* tokens are NOT API keys."""
    for var in ("GEMINI_API_KEY_1", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3", "GEMINI_API_KEY"):
        k = os.getenv(var, "").strip()
        if k.startswith("AIza"):
            return True
    return False


def _try_gemini(crop: str, disease: str) -> Optional[tuple[str, str]]:
    """
    Attempt to call Gemini. Returns (explanation, remedy) or None if unavailable.
    Only called when _has_valid_gemini_key() is True.
    """
    try:
        import google.generativeai as genai

        keys = []
        for var in ("GEMINI_API_KEY_1", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3", "GEMINI_API_KEY"):
            k = os.getenv(var, "").strip()
            if k.startswith("AIza") and k not in keys:
                keys.append(k)

        if disease.lower() == "healthy":
            prompt = (
                f"The {crop} leaf appears HEALTHY. "
                "Write 1 sentence saying it looks healthy. Then give 2 short tips to keep it that way. "
                "Plain text only. No markdown."
            )
        else:
            prompt = (
                f"You are an agricultural advisor for a small farmer in India.\n"
                f"Crop: {crop}\nDisease: {disease}\n\n"
                "Respond in EXACTLY this format (plain text, no markdown):\n\n"
                "EXPLANATION: [1-2 sentences about what this disease is and what causes it]\n\n"
                "REMEDY:\n1. [step one]\n2. [step two]\n3. [step three]\n4. [step four]\n\n"
                "Under 150 words total."
            )

        for key in keys:
            try:
                genai.configure(api_key=key)
                model    = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=600,
                        temperature=0.4,
                    ),
                )
                raw = response.text.strip()
                explanation, remedy = _parse_response(raw, crop, disease)
                if explanation:
                    return explanation, remedy
            except Exception as e:
                print(f"[Gemini key failed] {e}")
                continue

    except ImportError:
        pass

    return None


# ─── Response parser ──────────────────────────────────────────────────────────
def _parse_response(text: str, crop: str, disease: str) -> tuple[str, str]:
    clean = text.replace("**", "").replace("__", "")
    upper = clean.upper()

    remedy_pos = upper.find("REMEDY:")
    expl_pos   = upper.find("EXPLANATION:")

    if expl_pos != -1 and remedy_pos != -1:
        explanation = clean[expl_pos + len("EXPLANATION:") : remedy_pos].strip()
        remedy      = clean[remedy_pos + len("REMEDY:"):].strip()
    elif expl_pos != -1:
        explanation = clean[expl_pos + len("EXPLANATION:"):].strip()
        remedy      = ""
    elif remedy_pos != -1:
        explanation = ""
        remedy      = clean[remedy_pos + len("REMEDY:"):].strip()
    else:
        explanation = clean.strip()
        remedy      = ""

    # Strip any leaked prefixes
    for prefix in ("EXPLANATION:", "REMEDY:"):
        if explanation.upper().startswith(prefix):
            explanation = explanation[len(prefix):].strip()
        if remedy.upper().startswith(prefix):
            remedy = remedy[len(prefix):].strip()

    return explanation.strip(), remedy.strip()


# ─── Main endpoint ────────────────────────────────────────────────────────────
@router.post("/remedy", response_model=RemedyResponse)
async def get_remedy(req: RemedyRequest):
    """
    Returns farmer-friendly diagnosis + remedy.

    Priority:
    1. Memory/disk cache  — instant
    2. Gemini AI (if a real AIza key is configured)  — rich, personalised
    3. Built-in knowledge base  — always works, no key needed
    """
    cache_key = f"{req.crop.strip().lower()}|{req.disease.strip().lower()}"

    # ── 1. Cache hit ──────────────────────────────────────────────────────────
    if cache_key in _remedy_cache:
        entry = _remedy_cache[cache_key]
        # Only use cache if remedy field is non-empty and not a leaked prefix
        if entry.get("remedy") and not entry["remedy"].upper().startswith("EXPLANATION:"):
            return RemedyResponse(
                explanation = entry["explanation"],
                remedy      = entry["remedy"],
                cached      = True,
                source      = entry.get("source", "cache"),
            )
        # Stale/corrupt cache entry — remove and regenerate
        del _remedy_cache[cache_key]

    # ── 2. Try Gemini (only if real API key present) ──────────────────────────
    source = "knowledge_base"
    explanation = ""
    remedy      = ""

    if _has_valid_gemini_key():
        result = _try_gemini(req.crop, req.disease)
        if result:
            explanation, remedy = result
            source = "gemini"

    # ── 3. Fall back to built-in knowledge base ───────────────────────────────
    if not explanation:
        kb = _lookup_knowledge_base(req.crop, req.disease)
        if kb:
            explanation = kb["explanation"]
            remedy      = kb["remedy"]
            source      = "knowledge_base"
        else:
            # Generic fallback for unknown combinations
            if req.disease.lower() == "healthy":
                explanation = f"Your {req.crop} plant looks healthy! Keep up the good care."
                remedy      = (
                    "1. Water regularly at the base — avoid wetting leaves.\n"
                    "2. Check weekly for early signs of disease or pests.\n"
                    "3. Apply balanced fertilizer once a month."
                )
            else:
                explanation = (
                    f"Your {req.crop} plant shows signs of {req.disease}. "
                    "This is a fungal or bacterial condition that needs prompt attention."
                )
                remedy = (
                    "1. Remove and destroy all visibly infected leaves.\n"
                    "2. Spray with a broad-spectrum fungicide or copper-based bactericide.\n"
                    "3. Avoid watering from above — water at the base only.\n"
                    "4. Ensure good airflow around the plant by removing crowded growth."
                )

    # ── 4. Cache the result ───────────────────────────────────────────────────
    _remedy_cache[cache_key] = {
        "explanation": explanation,
        "remedy":      remedy,
        "source":      source,
        "cached_at":   datetime.now().isoformat(),
    }
    _save_cache(_remedy_cache)

    return RemedyResponse(
        explanation = explanation,
        remedy      = remedy,
        cached      = False,
        source      = source,
    )


# ─── Cache management endpoints ──────────────────────────────────────────────
@router.get("/remedy/cache", tags=["Remedy"])
async def get_cache_status():
    return {
        "total_cached": len(_remedy_cache),
        "cache_file":   str(_CACHE_FILE),
        "entries": [
            {
                "crop":      k.split("|")[0].title(),
                "disease":   k.split("|")[1].title(),
                "source":    v.get("source", "unknown"),
                "cached_at": v.get("cached_at", "unknown"),
            }
            for k, v in _remedy_cache.items()
        ],
    }


@router.delete("/remedy/cache", tags=["Remedy"])
async def clear_cache():
    """Clears both in-memory and on-disk remedy cache."""
    _remedy_cache.clear()
    if _CACHE_FILE.exists():
        _CACHE_FILE.unlink()
    return {"message": "Cache cleared successfully."}
