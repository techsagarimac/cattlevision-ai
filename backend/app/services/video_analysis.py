"""Frame-by-frame video analysis with tracking, behavior, and risk scoring."""

from __future__ import annotations

import uuid
from collections import Counter
from pathlib import Path

import cv2
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.services.annotator import draw_detections
from app.services.behavior import classify_behavior
from app.services.detector import CattleDetector
from app.services import persistence
from app.services.jobs import job_store
from app.services.risk import RECOMMENDATION, score_track
from app.services.tracker import CattleTracker
from app.utils.errors import InvalidFileError
from app.utils.files import public_media_url


def start_video_job(detector: CattleDetector, video_path: Path, original_name: str) -> str:
    detector.require()
    job_id = uuid.uuid4().hex
    job_store.create(job_id)
    thread_name = f"video-job-{job_id[:8]}"
    import threading

    worker = threading.Thread(
        target=_run_job,
        args=(job_id, detector, video_path, original_name),
        name=thread_name,
        daemon=True,
    )
    worker.start()
    return job_id


def _run_job(job_id: str, detector: CattleDetector, video_path: Path, original_name: str) -> None:
    db = SessionLocal()
    try:
        result = analyze_video(db, detector, video_path, original_name, job_id)
        job_store.update(
            job_id,
            status="completed",
            progress=100.0,
            message="Video analysis complete",
            session_id=result["session_id"],
            result=result,
            error=None,
        )
    except Exception as exc:
        job_store.update(
            job_id,
            status="failed",
            message="Video analysis failed",
            error=str(exc),
        )
    finally:
        db.close()


def analyze_video(
    db: Session,
    detector: CattleDetector,
    video_path: Path,
    original_name: str,
    job_id: str | None = None,
) -> dict:
    settings = get_settings()
    detector.require()
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise InvalidFileError("The uploaded file could not be read as a video. Use mp4, avi, or mov.")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 360)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    stride = max(1, settings.video_detect_stride)

    processed_name = f"processed_{video_path.stem}.mp4"
    processed_path = settings.processed_dir / processed_name
    writer = _open_writer(processed_path, fps / stride, width, height)

    session = persistence.create_session(
        db,
        file_name=original_name,
        analysis_type="video",
        original_path=str(video_path),
        job_id=job_id,
    )
    if job_id:
        job_store.update(job_id, session_id=session.id, status="processing", message="Detecting cattle in video")

    tracker = CattleTracker()
    last_items_by_id: dict[int, dict] = {}
    frame_index = 0
    processed_count = 0
    behavior_counter: Counter[str] = Counter()

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame_index % stride != 0:
                frame_index += 1
                continue

            timestamp = frame_index / fps
            detections = detector.detect(frame)
            tracks = tracker.update(detections, frame_index, timestamp)
            items = []
            for track in tracks:
                estimate = classify_behavior(track, image_height=float(height))
                risk = score_track(track, estimate)
                item = {
                    "animal_id": track.label,
                    "track_id": track.track_id,
                    "confidence": round(track.confidence, 4),
                    "x": round(track.bbox[0], 1),
                    "y": round(track.bbox[1], 1),
                    "width": round(track.bbox[2] - track.bbox[0], 1),
                    "height": round(track.bbox[3] - track.bbox[1], 1),
                    "behavior": estimate.behavior,
                    "movement": estimate.movement_label,
                    "movement_score": estimate.movement_score,
                    "activity_score": estimate.activity_score,
                    "risk_score": risk.score,
                    "risk_band": risk.band,
                    "timestamp": round(timestamp, 2),
                    "frame_index": frame_index,
                    "notes": estimate.notes + risk.reasons,
                    "total_distance": round(track.total_distance, 1),
                    "time_visible": round(track.time_visible, 2),
                    "should_alert": risk.should_alert,
                    "alert_type": risk.alert_type,
                    "alert_message": risk.message,
                    "severity": risk.band,
                }
                items.append(item)
                last_items_by_id[track.track_id] = item
                behavior_counter[estimate.behavior] += 1

            annotated = draw_detections(
                frame,
                items,
                title=f"CattleVision AI  t={timestamp:.1f}s  cattle={len(items)}",
            )
            if writer is not None:
                writer.write(annotated)

            processed_count += 1
            if job_id and total_frames > 0:
                progress = min(99.0, (frame_index / total_frames) * 100.0)
                job_store.update(job_id, progress=round(progress, 1), message=f"Processed {processed_count} frames")
            frame_index += 1
    finally:
        cap.release()
        if writer is not None:
            writer.release()

    alerts_count = 0
    activity_values = []
    for item in last_items_by_id.values():
        animal = persistence.upsert_animal(
            db,
            item["animal_id"],
            session.id,
            item["behavior"],
            item["risk_score"],
            item["confidence"],
        )
        persistence.add_observation(
            db,
            animal,
            confidence=item["confidence"],
            behavior=item["behavior"],
            movement_score=item["movement_score"],
            risk_score=item["risk_score"],
            bbox=(item["x"], item["y"], item["width"], item["height"]),
            frame_index=item["frame_index"],
            notes="; ".join(item["notes"]),
        )
        persistence.add_behavior_record(
            db,
            animal,
            behavior=item["behavior"],
            duration_seconds=item["time_visible"],
            movement_label=item["movement"],
        )
        activity_values.append(item.get("activity_score", item["movement_score"]))
        if item.get("should_alert"):
            persistence.add_alert(
                db,
                animal,
                alert_type=item.get("alert_type") or "Possible Health Concern",
                severity=item.get("severity") or "Monitor",
                message=item.get("alert_message")
                or f"⚠ Possible abnormal activity detected for {item['animal_id']}.",
                risk_score=item["risk_score"],
            )
            alerts_count += 1

    avg_activity = sum(activity_values) / len(activity_values) if activity_values else 0.0
    persistence.finish_session(
        db,
        session,
        total_animals=len(last_items_by_id),
        total_alerts=alerts_count,
        processed_path=str(processed_path) if processed_path.exists() else None,
        average_activity=round(avg_activity, 1),
        notes="Video tracking is approximate. IDs may switch under occlusion.",
    )

    processed_url = public_media_url("processed", processed_name) if processed_path.exists() else None
    return {
        "session_id": session.id,
        "cattle_count": len(last_items_by_id),
        "average_activity": round(avg_activity, 1),
        "alerts_generated": alerts_count,
        "behavior_stats": dict(behavior_counter),
        "processed_video_url": processed_url,
        "detections": list(last_items_by_id.values()),
        "disclaimer": (
            "CattleVision AI video results are experimental visual indicators. "
            + RECOMMENDATION
        ),
    }


def _open_writer(path: Path, fps: float, width: int, height: int):
    fps = max(5.0, fps)
    for codec in ("mp4v", "avc1", "XVID"):
        fourcc = cv2.VideoWriter_fourcc(*codec)
        writer = cv2.VideoWriter(str(path), fourcc, fps, (width, height))
        if writer.isOpened():
            return writer
        writer.release()
    return None
