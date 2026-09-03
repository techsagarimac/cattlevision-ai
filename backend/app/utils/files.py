"""Upload validation and file helpers."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import UploadFile

from app.utils.errors import InvalidFileError

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov"}
IMAGE_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "application/octet-stream"}
VIDEO_CONTENT_TYPES = {
    "video/mp4",
    "video/avi",
    "video/quicktime",
    "video/x-msvideo",
    "application/octet-stream",
}


def extension_of(filename: str) -> str:
    return Path(filename or "").suffix.lower()


def validate_image(file: UploadFile, max_bytes: int) -> None:
    if not file.filename:
        raise InvalidFileError("No image file was provided.")
    ext = extension_of(file.filename)
    if ext not in IMAGE_EXTENSIONS:
        raise InvalidFileError("Unsupported image type. Allowed: jpg, jpeg, png.")
    if file.content_type and file.content_type.lower() not in IMAGE_CONTENT_TYPES:
        raise InvalidFileError(f"Unsupported image content type: {file.content_type}")
    if file.size is not None and file.size > max_bytes:
        raise InvalidFileError(f"Image is too large. Maximum size is {max_bytes // (1024 * 1024)} MB.")


def validate_video(file: UploadFile, max_bytes: int) -> None:
    if not file.filename:
        raise InvalidFileError("No video file was provided.")
    ext = extension_of(file.filename)
    if ext not in VIDEO_EXTENSIONS:
        raise InvalidFileError("Unsupported video type. Allowed: mp4, avi, mov.")
    if file.content_type and file.content_type.lower() not in VIDEO_CONTENT_TYPES:
        raise InvalidFileError(f"Unsupported video content type: {file.content_type}")
    if file.size is not None and file.size > max_bytes:
        raise InvalidFileError(f"Video is too large. Maximum size is {max_bytes // (1024 * 1024)} MB.")


def unique_name(original: str) -> str:
    ext = extension_of(original) or ".bin"
    return f"{uuid.uuid4().hex}{ext}"


def public_media_url(kind: str, filename: str) -> str:
    return f"/api/media/{kind}/{filename}"
