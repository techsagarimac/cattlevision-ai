"""Pydantic API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    model_loaded: bool
    model_path: str | None = None
    model_message: str | None = None
    disclaimer: str


class DetectionBox(BaseModel):
    animal_id: str
    confidence: float
    x: float
    y: float
    width: float
    height: float
    behavior: str = "Unknown"
    movement: str = "Unknown"
    movement_score: float = 0.0
    risk_score: float = 0.0
    risk_band: str = "Normal"
    timestamp: float | None = None
    frame_index: int = 0
    notes: list[str] = Field(default_factory=list)


class ImageAnalysisResponse(BaseModel):
    session_id: int
    file_name: str
    cattle_count: int
    average_confidence: float
    detections: list[DetectionBox]
    observations: list[str]
    processed_image_url: str
    original_image_url: str
    model_name: str
    disclaimer: str
    is_demo: bool = False


class VideoJobStartResponse(BaseModel):
    job_id: str
    status: str
    message: str


class VideoJobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    message: str
    session_id: int | None = None
    cattle_count: int | None = None
    average_activity: float | None = None
    alerts_generated: int | None = None
    behavior_stats: dict[str, int] | None = None
    processed_video_url: str | None = None
    error: str | None = None
    disclaimer: str | None = None


class FrameAnalysisResponse(BaseModel):
    session_token: str
    cattle_count: int
    detections: list[DetectionBox]
    alerts: list[str]
    model_loaded: bool
    disclaimer: str


class AnimalSummary(BaseModel):
    id: int
    animal_identifier: str
    last_behavior: str | None
    last_risk_score: float
    last_confidence: float
    last_seen_at: datetime | None
    is_demo: bool
    open_alerts: int = 0


class ObservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    confidence: float
    behavior: str
    movement_score: float
    risk_score: float


class BehaviorRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    behavior: str
    started_at: datetime
    ended_at: datetime | None
    duration_seconds: float
    movement_label: str


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    animal_id: int | None
    animal_identifier: str | None = None
    alert_type: str
    severity: str
    message: str
    recommendation: str
    risk_score: float
    timestamp: datetime
    resolved: bool
    is_demo: bool


class AnimalDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    animal_identifier: str
    current_behavior: str | None
    activity_score: float
    risk_score: float
    detection_confidence: float
    time_monitored_seconds: float
    last_seen_at: datetime | None
    is_demo: bool
    observations: list[ObservationOut]
    behavior_history: list[BehaviorRecordOut]
    alerts: list[AlertOut]
    recommendation: str
    disclaimer: str


class DashboardResponse(BaseModel):
    total_animals: int
    active_animals: int
    resting_animals: int
    animals_requiring_attention: int
    normal: int
    monitor: int
    attention_required: int
    high_attention: int
    average_activity: float
    current_alerts: list[AlertOut]
    activity_over_time: list[dict]
    behavior_counts: dict[str, int]
    risk_distribution: dict[str, int]
    alerts_over_time: list[dict]
    includes_demo_data: bool
    disclaimer: str


class AnalysisSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_name: str
    analysis_type: str
    start_time: datetime
    end_time: datetime | None
    total_animals: int
    total_alerts: int
    status: str
    processed_path: str | None
    processed_url: str | None = None
    notes: str | None
    error_message: str | None
    is_demo: bool
    average_activity: float


DISCLAIMER = (
    "CattleVision AI is an educational computer-vision monitoring tool. "
    "It does not diagnose disease. Scores and alerts are experimental visual "
    "indicators that recommend human/veterinary inspection when concerns persist."
)
