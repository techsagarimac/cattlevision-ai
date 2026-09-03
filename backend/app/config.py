"""Application configuration."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "CattleVision AI"
    app_version: str = "1.0.0"
    database_url: str = "sqlite:///./cattlevision.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    max_image_mb: int = 10
    max_video_mb: int = 80
    yolo_confidence: float = 0.35
    seed_demo_data: bool = True
    video_detect_stride: int = 3
    live_max_disappeared: int = 20

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def models_dir(self) -> Path:
        return PROJECT_ROOT / "models"

    @property
    def upload_dir(self) -> Path:
        return BACKEND_DIR / "uploads"

    @property
    def processed_dir(self) -> Path:
        return BACKEND_DIR / "processed"

    @property
    def sample_data_dir(self) -> Path:
        return PROJECT_ROOT / "sample_data"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.processed_dir.mkdir(parents=True, exist_ok=True)
    settings.models_dir.mkdir(parents=True, exist_ok=True)
    return settings
