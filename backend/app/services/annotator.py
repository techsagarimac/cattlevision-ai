"""Draw detection overlays for images and video frames."""

from __future__ import annotations

import cv2
import numpy as np

from app.services.detector import Detection

BAND_COLORS = {
    "Normal": (64, 140, 90),
    "Monitor": (36, 140, 220),
    "Attention Required": (40, 90, 220),
    "High Attention": (40, 40, 200),
}


def _label_color(band: str) -> tuple[int, int, int]:
    return BAND_COLORS.get(band, (64, 140, 90))


def draw_detections(
    image_bgr: np.ndarray,
    items: list[dict],
    title: str | None = None,
) -> np.ndarray:
    canvas = image_bgr.copy()
    for item in items:
        x, y, w, h = int(item["x"]), int(item["y"]), int(item["width"]), int(item["height"])
        band = item.get("risk_band", "Normal")
        color = _label_color(band)
        cv2.rectangle(canvas, (x, y), (x + w, y + h), color, 2)
        label = item.get("animal_id", "Cow")
        conf = item.get("confidence", 0)
        behavior = item.get("behavior", "")
        caption = f"{label}  {conf:.0%}"
        if behavior:
            caption += f" | {behavior}"
        _put_label(canvas, caption, x, max(0, y - 8), color)
    if title:
        _put_label(canvas, title, 12, 28, (30, 30, 30), fill=(245, 245, 245))
    return canvas


def detections_to_items(detections: list[Detection], labels: list[str] | None = None) -> list[dict]:
    items = []
    for idx, det in enumerate(detections):
        label = labels[idx] if labels else f"Cow #{idx + 1:02d}"
        items.append(
            {
                "animal_id": label,
                "confidence": det.confidence,
                "x": det.x,
                "y": det.y,
                "width": det.width,
                "height": det.height,
                "risk_band": "Normal",
                "behavior": "",
            }
        )
    return items


def _put_label(
    image: np.ndarray,
    text: str,
    x: int,
    y: int,
    color: tuple[int, int, int],
    fill: tuple[int, int, int] | None = None,
) -> None:
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.55
    thickness = 1
    (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
    pad = 4
    y1 = max(0, y - th - pad)
    fill_color = fill or color
    cv2.rectangle(image, (x, y1), (x + tw + pad * 2, y + pad), fill_color, -1)
    cv2.putText(image, text, (x + pad, y), font, scale, (255, 255, 255), thickness, cv2.LINE_AA)
