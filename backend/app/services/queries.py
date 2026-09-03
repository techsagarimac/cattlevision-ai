"""Query helpers for dashboard, animals, and alerts."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import Alert, AnalysisSession, Animal, Observation
from app.schemas import DISCLAIMER
from app.services.risk import RECOMMENDATION, risk_band


def list_animals(db: Session, include_demo: bool = True) -> list[dict]:
    query = db.query(Animal)
    if not include_demo:
        query = query.filter(Animal.is_demo.is_(False))
    animals = query.order_by(Animal.animal_identifier.asc()).all()
    results = []
    for animal in animals:
        open_alerts = db.query(Alert).filter(Alert.animal_id == animal.id, Alert.resolved.is_(False)).count()
        results.append(
            {
                "id": animal.id,
                "animal_identifier": animal.animal_identifier,
                "last_behavior": animal.last_behavior,
                "last_risk_score": animal.last_risk_score,
                "last_confidence": animal.last_confidence,
                "last_seen_at": animal.last_seen_at,
                "is_demo": animal.is_demo,
                "open_alerts": open_alerts,
            }
        )
    return results


def animal_detail(db: Session, animal_id: int) -> dict | None:
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        return None
    observations = (
        db.query(Observation).filter(Observation.animal_id == animal.id).order_by(Observation.timestamp.desc()).limit(40).all()
    )
    alerts = db.query(Alert).filter(Alert.animal_id == animal.id).order_by(Alert.timestamp.desc()).all()
    first_obs = (
        db.query(Observation).filter(Observation.animal_id == animal.id).order_by(Observation.timestamp.asc()).first()
    )
    last_obs = observations[0] if observations else None
    duration = 0.0
    if first_obs and last_obs:
        duration = max(0.0, (last_obs.timestamp - first_obs.timestamp).total_seconds())
    activity_score = 0.0
    if observations:
        activity_score = sum(o.movement_score for o in observations) / len(observations)
    recommendation = (
        "No unusual visual pattern is currently flagged. Continue routine observation."
        if animal.last_risk_score <= 30
        else "Inspect the animal for possible causes of reduced or unusual activity. "
        + RECOMMENDATION
    )
    return {
        "id": animal.id,
        "animal_identifier": animal.animal_identifier,
        "current_behavior": animal.last_behavior,
        "activity_score": round(activity_score, 1),
        "risk_score": animal.last_risk_score,
        "detection_confidence": animal.last_confidence,
        "time_monitored_seconds": duration,
        "last_seen_at": animal.last_seen_at,
        "is_demo": animal.is_demo,
        "observations": observations,
        "behavior_history": animal.behavior_records,
        "alerts": [
            {
                "id": a.id,
                "animal_id": a.animal_id,
                "animal_identifier": animal.animal_identifier,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "message": a.message,
                "recommendation": a.recommendation,
                "risk_score": a.risk_score,
                "timestamp": a.timestamp,
                "resolved": a.resolved,
                "is_demo": a.is_demo,
            }
            for a in alerts
        ],
        "recommendation": recommendation,
        "disclaimer": DISCLAIMER,
    }


def list_alerts(db: Session, include_demo: bool = True, resolved: bool | None = None) -> list[dict]:
    query = db.query(Alert)
    if not include_demo:
        query = query.filter(Alert.is_demo.is_(False))
    if resolved is not None:
        query = query.filter(Alert.resolved.is_(resolved))
    alerts = query.order_by(Alert.timestamp.desc()).all()
    output = []
    for alert in alerts:
        identifier = None
        if alert.animal_id:
            animal = db.query(Animal).filter(Animal.id == alert.animal_id).first()
            identifier = animal.animal_identifier if animal else None
        output.append(
            {
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
        )
    return output


def dashboard(db: Session, include_demo: bool = True) -> dict:
    query = db.query(Animal)
    if not include_demo:
        query = query.filter(Animal.is_demo.is_(False))
    animals = query.all()
    behavior_counts: Counter[str] = Counter()
    risk_distribution = {"Normal": 0, "Monitor": 0, "Attention Required": 0, "High Attention": 0}
    active = 0
    resting = 0
    activity_values = []
    for animal in animals:
        behavior = animal.last_behavior or "Unknown"
        behavior_counts[behavior] += 1
        band = risk_band(animal.last_risk_score)
        risk_distribution[band] = risk_distribution.get(band, 0) + 1
        if behavior in {"Walking/moving", "Standing"}:
            active += 1
        if behavior in {"Resting/lying", "Low activity"}:
            resting += 1
        activity_values.append(max(0.0, 100.0 - animal.last_risk_score * 0.35) if animal.last_risk_score else 70.0)

    attention = risk_distribution["Attention Required"] + risk_distribution["High Attention"]
    avg_activity = sum(activity_values) / len(activity_values) if activity_values else 0.0

    alerts = list_alerts(db, include_demo=include_demo, resolved=False)

    since = datetime.utcnow() - timedelta(hours=6)
    obs_query = db.query(Observation)
    if not include_demo:
        obs_query = obs_query.filter(Observation.is_demo.is_(False))
    observations = obs_query.filter(Observation.timestamp >= since).order_by(Observation.timestamp.asc()).all()
    activity_over_time: list[dict] = []
    if observations:
        import pandas as pd

        frame = pd.DataFrame(
            {
                "timestamp": [obs.timestamp for obs in observations],
                "activity": [obs.movement_score for obs in observations],
            }
        )
        frame["time"] = pd.to_datetime(frame["timestamp"]).dt.floor("15min")
        grouped = frame.groupby("time", as_index=False)["activity"].mean()
        activity_over_time = [
            {"time": row.time.isoformat(), "activity": round(float(row.activity), 1)}
            for row in grouped.itertuples()
        ]

    alert_query = db.query(Alert)
    if not include_demo:
        alert_query = alert_query.filter(Alert.is_demo.is_(False))
    recent_alerts = alert_query.filter(Alert.timestamp >= since).all()
    alert_buckets: Counter[str] = Counter()
    for alert in recent_alerts:
        key = alert.timestamp.replace(minute=0, second=0, microsecond=0).isoformat()
        alert_buckets[key] += 1
    alerts_over_time = [{"time": key, "count": count} for key, count in sorted(alert_buckets.items())]

    return {
        "total_animals": len(animals),
        "active_animals": active,
        "resting_animals": resting,
        "animals_requiring_attention": attention,
        "normal": risk_distribution["Normal"],
        "monitor": risk_distribution["Monitor"],
        "attention_required": risk_distribution["Attention Required"],
        "high_attention": risk_distribution["High Attention"],
        "average_activity": round(avg_activity, 1),
        "current_alerts": alerts[:8],
        "activity_over_time": activity_over_time,
        "behavior_counts": dict(behavior_counts),
        "risk_distribution": risk_distribution,
        "alerts_over_time": alerts_over_time,
        "includes_demo_data": include_demo and any(a.is_demo for a in animals),
        "disclaimer": DISCLAIMER,
    }


def list_sessions(db: Session) -> list[AnalysisSession]:
    return db.query(AnalysisSession).order_by(AnalysisSession.start_time.desc()).all()


def get_session(db: Session, analysis_id: int) -> AnalysisSession | None:
    return db.query(AnalysisSession).filter(AnalysisSession.id == analysis_id).first()
