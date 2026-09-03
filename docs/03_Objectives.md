# Objectives

## Primary objectives

1. Design a full-stack application (FastAPI + React) for cattle monitoring from images, videos, and an optional webcam.
2. Integrate YOLO object detection to locate cattle and report confidence and bounding boxes.
3. Implement a simple tracker so video detections receive stable IDs such as Cow #01.
4. Classify basic behaviours using movement and box geometry (with architecture ready for a future ML anomaly model).
5. Compute an experimental risk score and generate inspection-oriented alerts.
6. Persist animals, observations, behaviour records, alerts, and analysis sessions in SQLite.
7. Provide a dashboard, animal detail page, alert workflow, and analysis history.
8. Document setup, limitations, and college-level methodology.

## Secondary objectives

- Seed labelled DEMO DATA for viva demonstration.
- Validate uploads (type and size) and return readable errors.
- Process video on the server so the browser remains responsive.
- Explain how a custom cattle-trained YOLO model can replace the COCO baseline.

## Non-objectives (out of scope for the MVP)

- Medical diagnosis or disease naming
- Guaranteed identity across days or cameras
- Production-grade multi-farm cloud operations
- Requirement for specialised farm hardware
