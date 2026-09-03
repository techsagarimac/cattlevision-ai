#!/usr/bin/env python3
"""Download YOLOv8n weights into the project's models/ folder."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODELS = ROOT / "models"
TARGET = MODELS / "yolov8n.pt"


def main() -> int:
    MODELS.mkdir(parents=True, exist_ok=True)
    if TARGET.exists():
        print(f"Model already present: {TARGET}")
        return 0
    try:
        from ultralytics import YOLO
    except ImportError:
        print("Install backend dependencies first: pip install -r backend/requirements.txt")
        return 1

    print("Downloading YOLOv8n (COCO, includes the 'cow' class)...")
    model = YOLO("yolov8n.pt")
    # Ultralytics stores the file in the current working directory or cache.
    candidates = [
        Path("yolov8n.pt"),
        Path.cwd() / "yolov8n.pt",
        Path.home() / ".cache" / "ultralytics" / "yolov8n.pt",
    ]
    src = next((p for p in candidates if p.exists()), None)
    if src is None:
        # After first YOLO() call the weight is often in CWD.
        for path in Path.cwd().glob("**/yolov8n.pt"):
            src = path
            break
    if src is None:
        print("Download finished but yolov8n.pt was not found. Copy it into models/ manually.")
        print("Expected location: models/yolov8n.pt")
        return 1
    if src.resolve() != TARGET.resolve():
        shutil.copy2(src, TARGET)
    print(f"Saved model to {TARGET}")
    print("CattleVision AI will use this file on the next backend start.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
