"""Rule-based behavior analysis from bounding-box motion and shape.

Pose estimation for cattle is not used by default because public YOLO pose
models are trained on humans. Posture is approximated from box aspect ratio
and vertical position. This is an experimental visual heuristic.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.services.tracker import Track, centroid_distance


@dataclass
class BehaviorEstimate:
    behavior: str
    movement_label: str
    movement_score: float
    activity_score: float
    posture_note: str
    possible_limp: bool
    sudden_change: bool
    notes: list[str]


def _recent_speed(track: Track, window: int = 8) -> float:
    history = track.history[-window:]
    if len(history) < 2:
        return 0.0
    total = 0.0
    time_span = max(1e-6, history[-1]["t"] - history[0]["t"])
    for prev, curr in zip(history, history[1:]):
        total += centroid_distance(prev["centroid"], curr["centroid"])
    # Normalize by box size so distant/small animals are comparable.
    x1, y1, x2, y2 = track.bbox
    diag = max(1.0, ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
    return (total / time_span) / diag


def _aspect(track: Track) -> float:
    x1, y1, x2, y2 = track.bbox
    h = max(1.0, y2 - y1)
    return (x2 - x1) / h


def _vertical_center(track: Track) -> float:
    _x1, y1, _x2, y2 = track.bbox
    return (y1 + y2) / 2.0


def _asymmetric_motion(track: Track) -> bool:
    """Very rough limp heuristic: irregular step-to-step displacement."""
    history = track.history[-12:]
    if len(history) < 8:
        return False
    steps = [
        centroid_distance(a["centroid"], b["centroid"])
        for a, b in zip(history, history[1:])
    ]
    mean = sum(steps) / len(steps)
    if mean < 1.5:
        return False
    variance = sum((s - mean) ** 2 for s in steps) / len(steps)
    cv = (variance ** 0.5) / mean
    return cv > 0.85 and mean > 2.0


def _activity_drop(track: Track) -> bool:
    if len(track.history) < 16:
        return False
    older = track.history[-16:-8]
    newer = track.history[-8:]
    old_speed = 0.0
    new_speed = 0.0
    for a, b in zip(older, older[1:]):
        old_speed += centroid_distance(a["centroid"], b["centroid"])
    for a, b in zip(newer, newer[1:]):
        new_speed += centroid_distance(a["centroid"], b["centroid"])
    return old_speed > 25 and new_speed < old_speed * 0.25


def classify_behavior(track: Track, image_height: float = 720.0) -> BehaviorEstimate:
    speed = _recent_speed(track)
    aspect = _aspect(track)
    notes: list[str] = []
    possible_limp = _asymmetric_motion(track)
    sudden_change = _activity_drop(track)

    lying_like = aspect >= 1.55
    if lying_like:
        behavior = "Resting/lying"
        movement_label = "Low"
        posture_note = "Wide bounding box suggests a lying or recumbent posture."
    elif speed < 0.015:
        if track.time_visible > 20 and speed < 0.008:
            behavior = "Low activity"
            movement_label = "Very low"
            posture_note = "Little bounding-box movement over the observed interval."
        else:
            behavior = "Standing"
            movement_label = "Low"
            posture_note = "Upright box shape with limited displacement."
    elif speed < 0.055:
        behavior = "Standing"
        movement_label = "Normal"
        posture_note = "Small position changes consistent with standing/shifting."
    else:
        behavior = "Walking/moving"
        movement_label = "Active"
        posture_note = "Repeated centroid movement consistent with locomotion."

    movement_score = min(100.0, speed * 1400.0)
    activity_score = movement_score
    if lying_like:
        activity_score = min(activity_score, 22.0)

    if possible_limp:
        notes.append("Possible asymmetric movement pattern (experimental).")
    if sudden_change:
        notes.append("Sudden major change in activity.")
    notes.append(posture_note)

    # Unused but documents that vertical position can refine lying vs standing.
    _ = _vertical_center(track) / max(1.0, image_height)

    return BehaviorEstimate(
        behavior=behavior,
        movement_label=movement_label,
        movement_score=round(movement_score, 2),
        activity_score=round(activity_score, 2),
        posture_note=posture_note,
        possible_limp=possible_limp,
        sudden_change=sudden_change,
        notes=notes,
    )


def classify_still_image(aspect_ratio: float, confidence: float) -> BehaviorEstimate:
    notes = ["Single-image analysis cannot measure movement over time."]
    if aspect_ratio >= 1.55:
        behavior = "Resting/lying"
        movement_label = "Unknown"
        posture_note = "Box shape is consistent with a lying posture."
        activity = 18.0
    else:
        behavior = "Standing"
        movement_label = "Unknown"
        posture_note = "Box shape is consistent with an upright/standing posture."
        activity = 55.0
    notes.append(posture_note)
    if confidence < 0.5:
        notes.append("Detection confidence is moderate; visual inspection is recommended.")
    return BehaviorEstimate(
        behavior=behavior,
        movement_label=movement_label,
        movement_score=0.0,
        activity_score=activity,
        posture_note=posture_note,
        possible_limp=False,
        sudden_change=False,
        notes=notes,
    )
