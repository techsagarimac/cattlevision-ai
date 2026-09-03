"""CattleVision AI FastAPI application."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import alerts, analysis, analyze, animals, dashboard, health, media
from app.config import get_settings
from app.database import SessionLocal, init_db
from app.services.demo import seed_demo_data
from app.services.detector import CattleDetector
from app.utils.errors import AppError, app_error_handler, unhandled_error_handler


@asynccontextmanager
async def lifespan(application: FastAPI):
    settings = get_settings()
    init_db()
    if settings.seed_demo_data:
        db = SessionLocal()
        try:
            seed_demo_data(db)
        finally:
            db.close()
    application.state.detector = CattleDetector(settings.models_dir, settings.yolo_confidence)
    yield
    application.state.detector = None


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="CattleVision AI",
        description=(
            "AI-Based Cattle Health & Welfare Monitoring System. "
            "Educational computer-vision project — not a veterinary diagnostic system."
        ),
        version=settings.app_version,
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_exception_handler(AppError, app_error_handler)
    application.add_exception_handler(Exception, unhandled_error_handler)
    application.include_router(health.router, prefix="/api")
    application.include_router(analyze.router, prefix="/api")
    application.include_router(animals.router, prefix="/api")
    application.include_router(alerts.router, prefix="/api")
    application.include_router(dashboard.router, prefix="/api")
    application.include_router(analysis.router, prefix="/api")
    application.include_router(media.router, prefix="/api")
    return application


app = create_app()
