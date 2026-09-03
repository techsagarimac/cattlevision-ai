"""Seed clearly labelled DEMO DATA so the dashboard can be demonstrated without a farm."""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import Alert, AnalysisSession, Animal, BehaviorRecord, Observation
from app.services.risk import RECOMMENDATION

DEMO_NOTE = "DEMO DATA — sample records for demonstration, not real AI detections."


def demo_already_seeded(db: Session) -> bool:
    return db.query(Animal).filter(Animal.is_demo.is_(True)).first() is not None


def seed_demo_data(db: Session) -> None:
    if demo_already_seeded(db):
        return

    now = datetime.utcnow()
    session = AnalysisSession(
        file_name="demo_herd_overview",
        analysis_type="demo",
        start_time=now - timedelta(hours=6),
        end_time=now,
        total_animals=12,
        total_alerts=3,
        status="completed",
        notes=DEMO_NOTE,
        is_demo=True,
        average_activity=72.0,
    )
    db.add(session)
    db.flush()

    herd = [
        ("Cow #01", "Walking/moving", 12.0, 0.94, "Normal"),
        ("Cow #02", "Standing", 18.0, 0.91, "Normal"),
        ("Cow #03", "Walking/moving", 15.0, 0.88, "Normal"),
        ("Cow #04", "Low activity", 64.0, 0.90, "Monitor"),
        ("Cow #05", "Resting/lying", 22.0, 0.86, "Normal"),
        ("Cow #06", "Standing", 20.0, 0.92, "Normal"),
        ("Cow #07", "Low activity", 72.0, 0.89, "Attention Required"),
        ("Cow #08", "Walking/moving", 10.0, 0.95, "Normal"),
        ("Cow #09", "Standing", 16.0, 0.87, "Normal"),
        ("Cow #10", "Resting/lying", 28.0, 0.84, "Normal"),
        ("Cow #11", "Walking/moving", 14.0, 0.93, "Normal"),
        ("Cow #12", "Standing", 48.0, 0.81, "Monitor"),
    ]

    behavior_timeline = {
        "Cow #04": [
            ("Walking/moving", 0, 15),
            ("Standing", 15, 25),
            ("Low activity", 25, 35),
            ("Low activity", 35, 38),
        ],
        "Cow #07": [
            ("Standing", 0, 20),
            ("Low activity", 20, 50),
        ],
    }

    for identifier, behavior, risk, confidence, _band in herd:
        animal = Animal(
            animal_identifier=identifier,
            created_at=now - timedelta(hours=6),
            is_demo=True,
            last_behavior=behavior,
            last_risk_score=risk,
            last_confidence=confidence,
            last_seen_at=now - timedelta(minutes=8),
            source_session_id=session.id,
            notes=DEMO_NOTE,
        )
        db.add(animal)
        db.flush()

        for minutes_ago in (90, 75, 60, 45, 30, 15, 5):
            ts = now - timedelta(minutes=minutes_ago)
            movement = 70.0 if behavior == "Walking/moving" else 35.0 if behavior == "Standing" else 12.0
            if identifier in ("Cow #04", "Cow #07") and minutes_ago <= 35:
                sample_behavior = "Low activity"
                sample_risk = risk
                movement = 8.0
            else:
                sample_behavior = behavior
                sample_risk = max(8.0, risk - 10)
            db.add(
                Observation(
                    animal_id=animal.id,
                    timestamp=ts,
                    confidence=confidence,
                    behavior=sample_behavior,
                    movement_score=movement,
                    risk_score=sample_risk,
                    is_demo=True,
                    notes=DEMO_NOTE,
                )
            )

        timeline = behavior_timeline.get(identifier)
        if timeline:
            for label, start_min, end_min in timeline:
                started = now - timedelta(minutes=(38 - start_min) if identifier == "Cow #04" else (50 - start_min))
                duration = (end_min - start_min) * 60
                db.add(
                    BehaviorRecord(
                        animal_id=animal.id,
                        behavior=label,
                        started_at=started,
                        ended_at=started + timedelta(seconds=duration),
                        duration_seconds=duration,
                        movement_label="Low" if "Low" in label or "Resting" in label else "Normal",
                        is_demo=True,
                    )
                )
        else:
            db.add(
                BehaviorRecord(
                    animal_id=animal.id,
                    behavior=behavior,
                    started_at=now - timedelta(minutes=40),
                    ended_at=now - timedelta(minutes=5),
                    duration_seconds=35 * 60,
                    movement_label="Normal" if risk < 31 else "Low",
                    is_demo=True,
                )
            )

    db.flush()
    cow04 = db.query(Animal).filter(Animal.animal_identifier == "Cow #04", Animal.is_demo.is_(True)).one()
    cow07 = db.query(Animal).filter(Animal.animal_identifier == "Cow #07", Animal.is_demo.is_(True)).one()
    cow12 = db.query(Animal).filter(Animal.animal_identifier == "Cow #12", Animal.is_demo.is_(True)).one()

    alerts = [
        (
            cow04,
            "Low activity",
            "Monitor",
            "⚠ Possible abnormal activity detected for Cow #04.",
            64.0,
            now - timedelta(minutes=12),
        ),
        (
            cow07,
            "Unusually low activity",
            "Attention Required",
            "⚠ Possible abnormal activity detected for Cow #07.",
            72.0,
            now - timedelta(minutes=20),
        ),
        (
            cow12,
            "Activity change",
            "Monitor",
            "⚠ Possible Health Concern for Cow #12 — activity dropped compared with earlier observations.",
            48.0,
            now - timedelta(hours=2),
        ),
    ]
    for animal, alert_type, severity, message, risk, ts in alerts:
        db.add(
            Alert(
                animal_id=animal.id,
                alert_type=alert_type,
                severity=severity,
                message=message,
                recommendation=RECOMMENDATION,
                risk_score=risk,
                timestamp=ts,
                resolved=False,
                is_demo=True,
            )
        )

    db.commit()
