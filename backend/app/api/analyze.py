from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.schemas import FrameAnalysisResponse, ImageAnalysisResponse, VideoJobStartResponse, VideoJobStatusResponse
from app.services.image_analysis import analyze_image
from app.services.jobs import job_store
from app.services.live import analyze_frame, reset_session
from app.services.video_analysis import start_video_job
from app.utils.errors import AppError, InvalidFileError
from app.utils.files import unique_name, validate_image, validate_video

router = APIRouter(prefix="/analyze", tags=["analyze"])
settings = get_settings()


@router.post("/image", response_model=ImageAnalysisResponse)
async def analyze_image_endpoint(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    validate_image(file, settings.max_image_mb * 1024 * 1024)
    contents = await file.read()
    if len(contents) > settings.max_image_mb * 1024 * 1024:
        raise InvalidFileError(f"Image is too large. Maximum size is {settings.max_image_mb} MB.")
    detector = request.app.state.detector
    result = analyze_image(
        db,
        detector,
        contents,
        file.filename or "upload.jpg",
        settings.processed_dir,
        settings.upload_dir,
    )
    return result


@router.post("/video", response_model=VideoJobStartResponse)
async def analyze_video_endpoint(
    request: Request,
    file: UploadFile = File(...),
):
    validate_video(file, settings.max_video_mb * 1024 * 1024)
    detector = request.app.state.detector
    detector.require()
    contents = await file.read()
    if len(contents) > settings.max_video_mb * 1024 * 1024:
        raise InvalidFileError(f"Video is too large. Maximum size is {settings.max_video_mb} MB.")
    saved = settings.upload_dir / unique_name(file.filename or "upload.mp4")
    saved.write_bytes(contents)
    job_id = start_video_job(detector, saved, file.filename or saved.name)
    return VideoJobStartResponse(
        job_id=job_id,
        status="queued",
        message="Video accepted. Processing on the server so the browser stays responsive.",
    )


@router.get("/video/{job_id}", response_model=VideoJobStatusResponse)
def video_job_status(job_id: str):
    job = job_store.get(job_id)
    if job is None:
        raise AppError("Analysis job not found.", status_code=404, code="job_not_found")
    result = job.result or {}
    return VideoJobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        message=job.message,
        session_id=job.session_id,
        cattle_count=result.get("cattle_count"),
        average_activity=result.get("average_activity"),
        alerts_generated=result.get("alerts_generated"),
        behavior_stats=result.get("behavior_stats"),
        processed_video_url=result.get("processed_video_url"),
        error=job.error,
        disclaimer=result.get("disclaimer"),
    )


@router.post("/frame", response_model=FrameAnalysisResponse)
async def analyze_live_frame(
    request: Request,
    file: UploadFile = File(...),
    session_token: str = Form("live-default"),
):
    validate_image(file, settings.max_image_mb * 1024 * 1024)
    contents = await file.read()
    detector = request.app.state.detector
    return analyze_frame(detector, contents, session_token)


@router.post("/frame/reset")
def reset_live_session(session_token: str = "live-default"):
    reset_session(session_token)
    return {"ok": True, "session_token": session_token}


@router.get("/webcam/backend")
def backend_webcam_probe():
    """Optional: report whether OpenCV can open camera index 0 on the server."""
    import cv2

    try:
        cap = cv2.VideoCapture(0)
        available = bool(cap.isOpened())
        cap.release()
    except Exception as exc:
        return {
            "available": False,
            "message": f"Backend webcam is unavailable: {exc}. Use the browser Live Camera page instead.",
        }
    if not available:
        return {
            "available": False,
            "message": "No webcam was detected on the server. Use uploaded images/videos or the browser camera page.",
        }
    return {
        "available": True,
        "message": "A webcam is visible to OpenCV on this machine. The web app still uses the browser camera for safety.",
    }
