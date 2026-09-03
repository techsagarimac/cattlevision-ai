from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.schemas import AnalysisSessionOut
from app.services import queries
from app.utils.errors import AppError
from app.utils.files import public_media_url

router = APIRouter(prefix="/analysis", tags=["analysis"])
settings = get_settings()


def _to_out(session) -> dict:
    processed_url = None
    if session.processed_path:
        name = Path(session.processed_path).name
        processed_url = public_media_url("processed", name)
    return {
        "id": session.id,
        "file_name": session.file_name,
        "analysis_type": session.analysis_type,
        "start_time": session.start_time,
        "end_time": session.end_time,
        "total_animals": session.total_animals,
        "total_alerts": session.total_alerts,
        "status": session.status,
        "processed_path": session.processed_path,
        "processed_url": processed_url,
        "notes": session.notes,
        "error_message": session.error_message,
        "is_demo": session.is_demo,
        "average_activity": session.average_activity,
    }


@router.get("", response_model=list[AnalysisSessionOut])
def list_analysis(db: Session = Depends(get_db)):
    return [_to_out(s) for s in queries.list_sessions(db)]


@router.get("/{analysis_id}", response_model=AnalysisSessionOut)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    session = queries.get_session(db, analysis_id)
    if session is None:
        raise AppError("Analysis session not found.", status_code=404, code="not_found")
    return _to_out(session)
