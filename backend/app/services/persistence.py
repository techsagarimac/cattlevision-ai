"""Persist analysis results into SQLite."""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import Alert, AnalysisSession, Animal, BehaviorRecord, Observation
from app.services.risk import RECOMMENDATION


def create_session(
    db: Session,
    *,
    file_name: str,
    analysis_type: str,
    original_path: str | None = None,
    job_id: str | None = None,
    is_demo: bool = False,
) -> AnalysisSession:
    session = AnalysisSession(
        file_name=file_name,
        analysis_type=analysis_type,
        original_path=original_path,
        status="processing",
        job_id=job_id,
        is_demo=is_demo,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def upsert_animal(
    db: Session,
    identifier: str,
    session_id: int,
    behavior: str,
    risk_score: float,
    confidence: float,
    is_demo: bool = False,
) -> Animal:
    animal = (
        db.query(Animal)
        .filter(Animal.animal_identifier == identifier, Animal.source_session_id == session_id)
        .first()
    )
    if animal is None:
        animal = Animal(
            animal_identifier=identifier,
            source_session_id=session_id,
            is_demo=is_demo,
        )
        db.add(animal)
        db.flush()
    animal.last_behavior = behavior
    animal.last_risk_score = risk_score
    animal.last_confidence = confidence
    animal.last_seen_at = datetime.utcnow()
    return animal


def add_observation(
    db: Session,
    animal: Animal,
    *,
    confidence: float,
    behavior: str,
    movement_score: float,
    risk_score: float,
    bbox: tuple[float, float, float, float],
    frame_index: int = 0,
    notes: str | None = None,
    is_demo: bool = False,
    timestamp: datetime | None = None,
) -> Observation:
    x, y, w, h = bbox
    obs = Observation(
        animal_id=animal.id,
        timestamp=timestamp or datetime.utcnow(),
        confidence=confidence,
        behavior=behavior,
        movement_score=movement_score,
        risk_score=risk_score,
        bbox_x=x,
        bbox_y=y,
        bbox_w=w,
        bbox_h=h,
        frame_index=frame_index,
        notes=notes,
        is_demo=is_demo,
    )
    db.add(obs)
    return obs


def add_behavior_record(
    db: Session,
    animal: Animal,
    *,
    behavior: str,
    duration_seconds: float,
    movement_label: str,
    is_demo: bool = False,
    started_at: datetime | None = None,
) -> BehaviorRecord:
    started = started_at or datetime.utcnow()
    record = BehaviorRecord(
        animal_id=animal.id,
        behavior=behavior,
        started_at=started,
        ended_at=started + timedelta(seconds=duration_seconds),
        duration_seconds=duration_seconds,
        movement_label=movement_label,
        is_demo=is_demo,
    )
    db.add(record)
    return record


def add_alert(
    db: Session,
    animal: Animal | None,
    *,
    alert_type: str,
    severity: str,
    message: str,
    risk_score: float,
    recommendation: str = RECOMMENDATION,
    is_demo: bool = False,
    timestamp: datetime | None = None,
) -> Alert:
    alert = Alert(
        animal_id=animal.id if animal else None,
        alert_type=alert_type,
        severity=severity,
        message=message,
        recommendation=recommendation,
        risk_score=risk_score,
        timestamp=timestamp or datetime.utcnow(),
        is_demo=is_demo,
    )
    db.add(alert)
    return alert


def finish_session(
    db: Session,
    session: AnalysisSession,
    *,
    total_animals: int,
    total_alerts: int,
    processed_path: str | None,
    average_activity: float,
    notes: str | None = None,
    status: str = "completed",
    error_message: str | None = None,
) -> AnalysisSession:
    session.end_time = datetime.utcnow()
    session.total_animals = total_animals
    session.total_alerts = total_alerts
    session.processed_path = processed_path
    session.average_activity = average_activity
    session.notes = notes
    session.status = status
    session.error_message = error_message
    db.commit()
    db.refresh(session)
    return session
