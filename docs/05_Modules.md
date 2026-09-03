# Modules

## Module 1 — Cattle detection

YOLO inference on images, video frames, and live frames. Outputs animal ID, box, confidence, and image coordinates. Missing weights produce HTTP 503 with setup instructions.

## Module 2 — Animal tracking

IoU + centroid matching with a disappeared-frame budget. Records approximate movement distance and time visible. Tracking is disclosed as imperfect.

## Module 3 — Behaviour analysis

Rule-based labels: Standing, Walking/moving, Resting/lying, Low activity. Still images use aspect ratio only and state that movement cannot be measured from one frame. Public YOLO pose models are human-centric; cattle posture uses box geometry instead.

## Module 4 — Abnormal activity detection

Risk score 0–100 with bands 0–30 Normal, 31–60 Monitor, 61–80 Attention Required, 81–100 High Attention. Triggers include very low movement, long inactivity, extreme box shape, optional asymmetric-step heuristic, and sudden activity drop. Alerts recommend inspection, not treatment.

## Module 5 — Health / welfare dashboard

Totals for cattle, behaviour groups, attention counts, average activity, current alerts, and four charts (activity over time, behaviour counts, risk distribution, alerts over time). Demo rows are badge-labelled.

## Supporting modules

- Image analysis page with original/processed preview and download
- Video analysis page with progress polling
- Live camera page with getUserMedia fallback message
- Animal detail page (behaviour, risk, histories, recommendation)
- Alert resolve workflow
- Analysis session history
- Demo seeder
