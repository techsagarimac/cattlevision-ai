"""SQLAlchemy database models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Animal(Base):
    __tablename__ = "animals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    animal_identifier: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    last_behavior: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    last_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    source_session_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("analysis_sessions.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    observations: Mapped[list["Observation"]] = relationship(back_populates="animal", cascade="all, delete-orphan")
    behavior_records: Mapped[list["BehaviorRecord"]] = relationship(back_populates="animal", cascade="all, delete-orphan")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="animal", cascade="all, delete-orphan")


class Observation(Base):
    __tablename__ = "observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    animal_id: Mapped[int] = mapped_column(Integer, ForeignKey("animals.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    behavior: Mapped[str] = mapped_column(String(64), default="Unknown")
    movement_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    bbox_x: Mapped[float] = mapped_column(Float, default=0.0)
    bbox_y: Mapped[float] = mapped_column(Float, default=0.0)
    bbox_w: Mapped[float] = mapped_column(Float, default=0.0)
    bbox_h: Mapped[float] = mapped_column(Float, default=0.0)
    frame_index: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)

    animal: Mapped["Animal"] = relationship(back_populates="observations")


class BehaviorRecord(Base):
    __tablename__ = "behavior_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    animal_id: Mapped[int] = mapped_column(Integer, ForeignKey("animals.id"), index=True)
    behavior: Mapped[str] = mapped_column(String(64))
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    movement_label: Mapped[str] = mapped_column(String(32), default="Unknown")
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)

    animal: Mapped["Animal"] = relationship(back_populates="behavior_records")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    animal_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("animals.id"), nullable=True, index=True)
    alert_type: Mapped[str] = mapped_column(String(64))
    severity: Mapped[str] = mapped_column(String(32), default="monitor")
    message: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str] = mapped_column(Text)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)

    animal: Mapped["Animal"] = relationship(back_populates="alerts")


class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    file_name: Mapped[str] = mapped_column(String(255))
    analysis_type: Mapped[str] = mapped_column(String(32))  # image | video | live | demo
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    total_animals: Mapped[int] = mapped_column(Integer, default=0)
    total_alerts: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="completed")
    original_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    processed_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    average_activity: Mapped[float] = mapped_column(Float, default=0.0)
    job_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
