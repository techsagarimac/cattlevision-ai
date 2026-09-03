"""Live-camera frame analysis with per-session tracking."""

from __future__ import annotations

import time
from collections import defaultdict

import cv2
import numpy as np

from app.services.behavior import classify_behavior
from app.services.detector import CattleDetector
from app.services.risk import RECOMMENDATION, score_track
from app.services.tracker import CattleTracker
from app.utils.errors import InvalidFileError

_sessions: dict[str, CattleTracker] = {}
_session_started: dict[str, float] = defaultdict(time.time)


def analyze_frame(detector: CattleDetector, image_bytes: bytes, session_token: str) -> dict:
    detector.require()
    image = _decode(image_bytes)
    tracker = _sessions.setdefault(session_token, CattleTracker(max_disappeared=12))
    if session_token not in _session_started:
        _session_started[session_token] = time.time()

    detections = detector.detect(image)
    elapsed = time.time() - _session_started[session_token]
    tracks = tracker.update(detections, frame_index=int(elapsed * 10), timestamp=elapsed)
    items = []
    alerts = []
    h = image.shape[0]
    for track in tracks:
        estimate = classify_behavior(track, image_height=float(h))
        risk = score_track(track, estimate)
        items.append(
            {
                "animal_id": track.label,
                "confidence": round(track.confidence, 4),
                "x": round(track.bbox[0], 1),
                "y": round(track.bbox[1], 1),
                "width": round(track.bbox[2] - track.bbox[0], 1),
                "height": round(track.bbox[3] - track.bbox[1], 1),
                "behavior": estimate.behavior,
                "movement": estimate.movement_label,
                "movement_score": estimate.movement_score,
                "risk_score": risk.score,
                "risk_band": risk.band,
                "timestamp": round(elapsed, 2),
                "frame_index": 0,
                "notes": estimate.notes,
            }
        )
        if risk.should_alert and risk.message:
            alerts.append(risk.message)

    return {
        "session_token": session_token,
        "cattle_count": len(items),
        "detections": items,
        "alerts": alerts,
        "model_loaded": detector.loaded,
        "disclaimer": "Live camera analysis is experimental and not a veterinary diagnosis. " + RECOMMENDATION,
    }


def reset_session(session_token: str) -> None:
    _sessions.pop(session_token, None)
    _session_started.pop(session_token, None)


def _decode(image_bytes: bytes):
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise InvalidFileError("Live frame could not be decoded as an image.")
    return image
