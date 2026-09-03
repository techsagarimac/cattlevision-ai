from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alert
from app.schemas import AlertOut
from app.services import queries
from app.utils.errors import AppError

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
def get_alerts(
    include_demo: bool = Query(True),
    resolved: bool | None = Query(None),
    db: Session = Depends(get_db),
):
    return queries.list_alerts(db, include_demo=include_demo, resolved=resolved)


@router.post("/{alert_id}/resolve", response_model=AlertOut)
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert is None:
        raise AppError("Alert not found.", status_code=404, code="not_found")
    alert.resolved = True
    db.commit()
    db.refresh(alert)
    identifier = None
    if alert.animal_id:
        from app.models import Animal

        animal = db.query(Animal).filter(Animal.id == alert.animal_id).first()
        identifier = animal.animal_identifier if animal else None
    return {
        "id": alert.id,
        "animal_id": alert.animal_id,
        "animal_identifier": identifier,
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "message": alert.message,
        "recommendation": alert.recommendation,
        "risk_score": alert.risk_score,
        "timestamp": alert.timestamp,
        "resolved": alert.resolved,
        "is_demo": alert.is_demo,
    }
