"""Image analysis pipeline: detect cattle, annotate, persist results."""

from __future__ import annotations

from pathlib import Path

import cv2
from sqlalchemy.orm import Session

from app.services.annotator import draw_detections
from app.services.behavior import classify_still_image
from app.services.detector import CattleDetector
from app.services import persistence
from app.services.risk import RECOMMENDATION, score_still_image
from app.utils.errors import InvalidFileError
from app.utils.files import public_media_url, unique_name


def analyze_image(
    db: Session,
    detector: CattleDetector,
    image_bytes: bytes,
    original_name: str,
    processed_dir: Path,
    upload_dir: Path,
) -> dict:
    detector.require()
    array = _decode_image(image_bytes)
    saved_original = upload_dir / unique_name(original_name)
    saved_original.write_bytes(image_bytes)

    detections = detector.detect(array)
    items = []
    session = persistence.create_session(
        db,
        file_name=original_name,
        analysis_type="image",
        original_path=str(saved_original),
    )

    observations: list[str] = []
    alerts_count = 0
    for idx, det in enumerate(detections):
        label = f"Cow #{idx + 1:02d}"
        estimate = classify_still_image(det.aspect_ratio, det.confidence)
        risk = score_still_image(estimate, det.confidence)
        animal = persistence.upsert_animal(
            db,
            label,
            session.id,
            estimate.behavior,
            risk.score,
            det.confidence,
        )
        persistence.add_observation(
            db,
            animal,
            confidence=det.confidence,
            behavior=estimate.behavior,
            movement_score=estimate.movement_score,
            risk_score=risk.score,
            bbox=(det.x, det.y, det.width, det.height),
            notes="; ".join(estimate.notes),
        )
        persistence.add_behavior_record(
            db,
            animal,
            behavior=estimate.behavior,
            duration_seconds=0,
            movement_label=estimate.movement_label,
        )
        if risk.should_alert:
            persistence.add_alert(
                db,
                animal,
                alert_type=risk.alert_type or "Possible Health Concern",
                severity=risk.band.lower(),
                message=f"⚠ Possible abnormal activity detected for {label}.",
                risk_score=risk.score,
            )
            alerts_count += 1
        items.append(
            {
                "animal_id": label,
                "confidence": round(det.confidence, 4),
                "x": round(det.x, 1),
                "y": round(det.y, 1),
                "width": round(det.width, 1),
                "height": round(det.height, 1),
                "behavior": estimate.behavior,
                "movement": estimate.movement_label,
                "movement_score": estimate.movement_score,
                "risk_score": risk.score,
                "risk_band": risk.band,
                "timestamp": None,
                "frame_index": 0,
                "notes": estimate.notes + risk.reasons,
            }
        )
        observations.append(
            f"{label} — Confidence {det.confidence:.0%}, possible behavior: {estimate.behavior}, "
            f"experimental risk {risk.score:.0f}/100 ({risk.band})."
        )

    if not detections:
        observations.append("No cattle were detected in this image. Try a clearer, closer photo of cows.")

    annotated = draw_detections(array, items, title="CattleVision AI — Image Analysis")
    processed_name = f"processed_{saved_original.stem}.jpg"
    processed_path = processed_dir / processed_name
    cv2.imwrite(str(processed_path), annotated)

    avg_conf = sum(d.confidence for d in detections) / len(detections) if detections else 0.0
    avg_activity = (
        sum(item["movement_score"] if item["movement_score"] else item.get("risk_score", 0) for item in items) / len(items)
        if items
        else 0.0
    )
    # Activity for still images uses the heuristic activity score stored as complement of risk.
    still_activity = 0.0
    if items:
        still_activity = sum(max(0.0, 100.0 - i["risk_score"] * 0.4) for i in items) / len(items)

    persistence.finish_session(
        db,
        session,
        total_animals=len(detections),
        total_alerts=alerts_count,
        processed_path=str(processed_path),
        average_activity=round(still_activity, 1),
        notes="Single-image cattle detection. Movement cannot be measured from one frame.",
    )

    return {
        "session_id": session.id,
        "file_name": original_name,
        "cattle_count": len(detections),
        "average_confidence": round(avg_conf, 4),
        "detections": items,
        "observations": observations,
        "processed_image_url": public_media_url("processed", processed_name),
        "original_image_url": public_media_url("uploads", saved_original.name),
        "model_name": detector.model_name or "unknown",
        "disclaimer": (
            "This is an educational computer-vision result, not a veterinary diagnosis. "
            + RECOMMENDATION
        ),
        "is_demo": False,
        "average_activity": avg_activity,
    }


def _decode_image(image_bytes: bytes):
    import numpy as np

    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise InvalidFileError("The uploaded file could not be read as an image. Use jpg, jpeg, or png.")
    return image
