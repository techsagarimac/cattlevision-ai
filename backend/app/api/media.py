from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.config import get_settings
from app.utils.errors import AppError, InvalidFileError

router = APIRouter(prefix="/media", tags=["media"])
settings = get_settings()

ALLOWED_KINDS = {
    "uploads": settings.upload_dir,
    "processed": settings.processed_dir,
}


@router.get("/{kind}/{filename}")
def get_media(kind: str, filename: str):
    if kind not in ALLOWED_KINDS:
        raise AppError("Unknown media type.", status_code=404, code="not_found")
    if "/" in filename or "\\" in filename or filename.startswith("."):
        raise InvalidFileError("Invalid file name.")
    path = ALLOWED_KINDS[kind] / filename
    resolved = path.resolve()
    root = ALLOWED_KINDS[kind].resolve()
    if root not in resolved.parents and resolved != root:
        raise InvalidFileError("Invalid file path.")
    if not resolved.exists() or not resolved.is_file():
        raise AppError("File not found.", status_code=404, code="not_found")
    return FileResponse(resolved)
