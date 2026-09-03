# YOLO model setup for CattleVision AI

This project uses **Ultralytics YOLO** for cattle detection.

## Which model is used?

Default MVP model:

- File: `yolov8n.pt`
- Family: YOLOv8 nano (lightweight, suitable for a college laptop)
- Training data: COCO
- Cattle class: COCO class name `cow`

The detector **only keeps detections whose class name is one of**:
`cow`, `cattle`, `ox`, `bull`, `heifer`, `calf`.

This is good enough for a demonstration. It is **not** a farm-grade cattle model.

## Where to place the file

Put the weight file here (this folder):

```
cattlevision-ai/models/yolov8n.pt
```

Optional custom model (preferred if present):

```
cattlevision-ai/models/cattle.pt
```

Load order:

1. `models/cattle.pt`
2. `models/yolov8n.pt`
3. `models/yolo11n.pt`
4. `models/yolov8s.pt`

If none of these files exist, the API returns:

**AI model not found. Please download/configure the model.**

The app does not hide this error and does not silently skip detection.

## How to download

From the project root, with the backend virtual environment activated:

```bash
cd backend
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python scripts/download_model.py
```

The script uses Ultralytics to fetch `yolov8n.pt` and copies it into `models/`.

Manual option:

1. Install backend requirements.
2. Run Python: `from ultralytics import YOLO; YOLO('yolov8n.pt')`
3. Copy the downloaded `yolov8n.pt` into `models/`.

Official Ultralytics assets are also documented at: https://docs.ultralytics.com

## How inference works

1. The image/frame is decoded with OpenCV (`BGR`).
2. `YOLO.predict()` runs at confidence `YOLO_CONFIDENCE` (default 0.35).
3. Non-cattle classes are discarded.
4. Remaining boxes are sorted left-to-right.
5. For images, IDs are `Cow #01`, `Cow #02`, …
6. For video/live, a simple IoU + centroid tracker keeps IDs as stable as it can.

## How to replace this with a custom cattle model later

1. Train YOLO on a labelled cattle dataset (roboflow / custom farm photos).
2. Export `best.pt`.
3. Copy it to `models/cattle.pt`.
4. Restart the backend.

If your custom classes use names other than `cow` / `cattle`, add those names in
`backend/app/services/detector.py` (`CATTLE_CLASS_NAMES`).

A later trained **anomaly-detection model** can replace the rule-based risk
module in `backend/app/services/risk.py` without changing the API shape.

## Hardware

No special camera or GPU is required. CPU inference with YOLOv8n is acceptable
for the MVP. A GPU will make video analysis faster but is optional.
