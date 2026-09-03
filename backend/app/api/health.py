from fastapi import APIRouter, Request

from app.schemas import DISCLAIMER, HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(request: Request):
    detector = request.app.state.detector
    status = detector.status()
    return HealthResponse(
        status="ok" if status["loaded"] else "degraded",
        app="CattleVision AI",
        version="1.0.0",
        model_loaded=status["loaded"],
        model_path=status["model_path"],
        model_message=status["message"],
        disclaimer=DISCLAIMER,
    )


@router.get("/model/status")
def model_status(request: Request):
    detector = request.app.state.detector
    payload = detector.status()
    payload["help"] = (
        "Place yolov8n.pt or cattle.pt in the models/ folder. "
        "Run python backend/scripts/download_model.py to download YOLOv8n."
    )
    return payload
