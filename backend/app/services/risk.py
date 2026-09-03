"""Experimental visual risk scoring. Not a medical diagnosis."""

from __future__ import annotations

from dataclasses import dataclass

from app.services.behavior import BehaviorEstimate
from app.services.tracker import Track


RISK_BANDS = (
    (30, "Normal"),
    (60, "Monitor"),
    (80, "Attention Required"),
    (100, "High Attention"),
)

RECOMMENDATION = (
    "Inspect the animal and consult a qualified veterinarian if concerns persist. "
    "This score is an experimental computer-vision indicator, not a diagnosis."
)


def risk_band(score: float) -> str:
    if score <= 30:
        return "Normal"
    if score <= 60:
        return "Monitor"
    if score <= 80:
        return "Attention Required"
    return "High Attention"


@dataclass
class RiskResult:
    score: float
    band: str
    reasons: list[str]
    should_alert: bool
    alert_type: str | None
    message: str | None


def score_track(track: Track, estimate: BehaviorEstimate) -> RiskResult:
    score = 8.0
    reasons: list[str] = []

    if estimate.behavior == "Low activity":
        score += 28
        reasons.append("Very low movement")
    if estimate.behavior == "Resting/lying" and track.time_visible > 45:
        score += 12
        reasons.append("Extended recumbent posture in the observed clip")
    if track.time_visible > 25 and estimate.movement_score < 8:
        score += 22
        reasons.append("Long inactivity")
    if estimate.possible_limp:
        score += 18
        reasons.append("Possible limping / asymmetric movement")
    if estimate.sudden_change:
        score += 20
        reasons.append("Sudden major change in activity")

    x1, y1, x2, y2 = track.bbox
    aspect = (x2 - x1) / max(1.0, y2 - y1)
    if aspect > 2.2:
        score += 10
        reasons.append("Unusual posture (extreme bounding-box shape)")

    score = max(0.0, min(100.0, score))
    band = risk_band(score)
    should_alert = score >= 31
    alert_type = None
    message = None
    if should_alert:
        alert_type = reasons[0] if reasons else "Possible Health Concern"
        message = f"Possible abnormal activity detected for {track.label}."
    return RiskResult(
        score=round(score, 1),
        band=band,
        reasons=reasons,
        should_alert=should_alert,
        alert_type=alert_type,
        message=message,
    )


def score_still_image(estimate: BehaviorEstimate, confidence: float) -> RiskResult:
    score = 10.0
    reasons: list[str] = ["Single-frame analysis has limited temporal evidence."]
    if estimate.behavior == "Resting/lying":
        score += 18
        reasons.append("Possible recumbent posture in the image")
    if confidence < 0.45:
        score += 8
        reasons.append("Lower detection confidence")
    score = max(0.0, min(100.0, score))
    band = risk_band(score)
    return RiskResult(
        score=round(score, 1),
        band=band,
        reasons=reasons,
        should_alert=score >= 31,
        alert_type="Possible Health Concern" if score >= 31 else None,
        message="Possible Health Concern — posture or confidence warrants a visual check."
        if score >= 31
        else None,
    )
