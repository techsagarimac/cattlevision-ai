"""Cattle detection using Ultralytics YOLO.

Default model: YOLOv8n trained on COCO. The COCO class list includes `cow`,
which is used as a practical cattle detector for this educational MVP.

Custom cattle weights can be placed at models/cattle.pt and will be preferred.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from app.utils.errors import InferenceError, ModelNotFoundError

CATTLE_CLASS_NAMES = {"cow", "cattle", "ox", "bull", "heifer", "calf"}
MODEL_CANDIDATES = ("cattle.pt", "yolov8n.pt", "yolo11n.pt", "yolov8s.pt")


@dataclass
class Detection:
    class_name: str
    confidence: float
    x: float
    y: float
    width: float
    height: float
    centroid: tuple[float, float] = field(init=False)

    def __post_init__(self) -> None:
        self.centroid = (self.x + self.width / 2.0, self.y + self.height / 2.0)

    @property
    def xyxy(self) -> tuple[float, float, float, float]:
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    @property
    def aspect_ratio(self) -> float:
        if self.height <= 1:
            return 1.0
        return self.width / self.height


class CattleDetector:
    def __init__(self, models_dir: Path, confidence: float = 0.35):
        self.models_dir = Path(models_dir)
        self.confidence = confidence
        self.model = None
        self.model_path: Path | None = None
        self.model_name: str | None = None
        self.error: str | None = None
        self._load()

    def _load(self) -> None:
        found = None
        for name in MODEL_CANDIDATES:
            candidate = self.models_dir / name
            if candidate.exists():
                found = candidate
                break

        if found is None:
            self.error = (
                "AI model not found. Please download/configure the model. "
                "Place yolov8n.pt or a custom cattle.pt file in the models/ folder. "
                "Run: python backend/scripts/download_model.py"
            )
            return

        try:
            from ultralytics import YOLO

            self.model = YOLO(str(found))
            self.model_path = found
            self.model_name = found.name
            self.error = None
        except Exception as exc:  # pragma: no cover - depends on local torch
            self.model = None
            self.error = f"Failed to load AI model at {found}: {exc}"

    @property
    def loaded(self) -> bool:
        return self.model is not None

    def require(self) -> None:
        if not self.loaded:
            raise ModelNotFoundError(self.error)

    def detect(self, image_bgr: np.ndarray) -> list[Detection]:
        self.require()
        try:
            results = self.model.predict(
                source=image_bgr,
                conf=self.confidence,
                verbose=False,
            )
        except Exception as exc:
            raise InferenceError(f"AI inference failed: {exc}") from exc

        detections: list[Detection] = []
        if not results:
            return detections

        result = results[0]
        names = result.names or {}
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            return detections

        for box in boxes:
            cls_id = int(box.cls[0].item()) if box.cls is not None else -1
            class_name = str(names.get(cls_id, "")).lower()
            if class_name not in CATTLE_CLASS_NAMES:
                continue
            conf = float(box.conf[0].item()) if box.conf is not None else 0.0
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]
            detections.append(
                Detection(
                    class_name=class_name,
                    confidence=conf,
                    x=x1,
                    y=y1,
                    width=max(1.0, x2 - x1),
                    height=max(1.0, y2 - y1),
                )
            )

        detections.sort(key=lambda d: d.x)
        return detections

    def status(self) -> dict:
        return {
            "loaded": self.loaded,
            "model_path": str(self.model_path) if self.model_path else None,
            "model_name": self.model_name,
            "message": None if self.loaded else self.error,
        }
