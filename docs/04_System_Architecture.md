# System Architecture

## Logical view

```
┌─────────────────────────────────────────────┐
│  React UI (Vite)                            │
│  Dashboard, Image, Video, Live, Animals,    │
│  Alerts, History, About                     │
└──────────────────┬──────────────────────────┘
                   │ HTTP JSON / multipart
┌──────────────────▼──────────────────────────┐
│  FastAPI                                    │
│  /api/health  /api/analyze/*  /api/animals  │
│  /api/alerts  /api/dashboard  /api/analysis │
└──┬──────────┬──────────┬────────────────────┘
   │          │          │
   ▼          ▼          ▼
 YOLO     OpenCV      SQLite
 detect   decode,     SQLAlchemy
          annotate,   models
          write mp4
```

## Process view (image)

Upload → validate → save original → YOLO → filter cattle → posture heuristic → optional alert → draw boxes → save processed JPEG → store session.

## Process view (video)

Upload → 202-style job id → background thread reads frames (stride) → detect → track → behaviour/risk → annotate writer → persist last state of each track → client polls progress.

## Deployment view (student lab)

Two local processes: `uvicorn` on port 8000 and Vite on port 5173 with a proxy for `/api`. No Docker is required. Weights live in `models/` at the repository root.

## Future architecture hook

`CattleDetector`, `CattleTracker`, `classify_behavior`, and `score_track` are separate modules. A trained classifier can replace the last two without changing REST payloads.
