"""
scans.py — saves the latest scanned photo of each disease on this computer.

Photos are stored as normal files in  backend/saved_scans/<crop>___<disease>.jpg
A new scan of the same disease overwrites the old file, so the library card
always shows the latest scan. Files stay until you delete them.

It is already included in backend/main.py:

    from backend.scans import router as scans_router
    app.include_router(scans_router)
"""
import re
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

router = APIRouter()

SCANS_DIR = Path(__file__).parent / "saved_scans"
SCANS_DIR.mkdir(exist_ok=True)

MAX_BYTES = 3 * 1024 * 1024  # thumbnails are ~40 KB; this is just a safety limit


def norm_key(crop: str, disease: str) -> str:
    """Same rule as the frontend: lowercase, anything not a-z/0-9 becomes '_'."""
    raw = f"{crop}___healthy" if disease == "Healthy" else f"{crop}___{disease}"
    return re.sub(r"[^a-z0-9]+", "_", raw.lower()).strip("_")


@router.post("/scans")
async def save_scan(
    crop: str = Form(...),
    disease: str = Form(...),
    file: UploadFile = File(...),
):
    data = await file.read()
    if not data or len(data) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="Invalid image size")
    key = norm_key(crop, disease)
    (SCANS_DIR / f"{key}.jpg").write_bytes(data)
    return {"key": key}


@router.get("/scans")
def list_scans():
    """{key: last-modified time} — the frontend uses it to refresh changed photos."""
    return {p.stem: int(p.stat().st_mtime) for p in SCANS_DIR.glob("*.jpg")}


@router.get("/scans/{name}")
def get_scan(name: str):
    key = name[:-4] if name.endswith(".jpg") else name
    if not re.fullmatch(r"[a-z0-9_]+", key):
        raise HTTPException(status_code=404)
    path = SCANS_DIR / f"{key}.jpg"
    if not path.exists():
        raise HTTPException(status_code=404)
    return FileResponse(path, media_type="image/jpeg", headers={"Cache-Control": "no-cache"})
