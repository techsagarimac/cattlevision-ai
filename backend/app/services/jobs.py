"""In-memory video analysis job store."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any


@dataclass
class VideoJob:
    job_id: str
    status: str = "queued"
    progress: float = 0.0
    message: str = "Waiting to start"
    session_id: int | None = None
    result: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, VideoJob] = {}
        self._lock = threading.Lock()

    def create(self, job_id: str) -> VideoJob:
        job = VideoJob(job_id=job_id)
        with self._lock:
            self._jobs[job_id] = job
        return job

    def get(self, job_id: str) -> VideoJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def update(self, job_id: str, **kwargs) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            for key, value in kwargs.items():
                setattr(job, key, value)


job_store = JobStore()
