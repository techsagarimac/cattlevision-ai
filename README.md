# CattleVision AI

**AI-Based Cattle Health & Welfare Monitoring System**

CattleVision AI is a college major-project application that uses computer vision to detect cattle in images and videos, estimate simple behaviours, and flag **possible** abnormal activity for a human to inspect.

This is an **educational / engineering** system. It is **not** a veterinary diagnostic product. It cannot definitively diagnose disease. Alerts use wording such as “Possible Health Concern”, “Abnormal Activity Detected”, and “Veterinary Inspection Recommended”.

---

## Project objective

Help observers review cattle from uploaded images, uploaded videos, or an optional webcam, so animals that appear unusually still, recumbent, or irregular in motion can be **inspected in person**.

## Problem statement

Visual welfare checks on a farm are time-consuming and easy to miss when many animals are present. Students and small farms need a demonstrable, hardware-free tool that:

- finds cattle in a photo or video
- keeps approximate IDs during a clip
- summarises standing / walking / resting / low activity
- raises an experimental risk score when patterns look unusual

## Proposed solution

A FastAPI backend runs Ultralytics YOLO (COCO `cow` class, or a custom `cattle.pt` model). OpenCV handles media. A simple IoU tracker maintains IDs on video. Rule-based behaviour and risk modules write SQLite records. A React dashboard presents counts, charts, animal pages, and alerts. Demo data is clearly labelled **DEMO DATA**.

## Features

- Image cattle detection with bounding boxes, IDs, and confidence
- Video analysis with tracking, movement, behaviour, and alerts
- Optional live webcam (browser); clear message if the camera is missing
- Experimental risk bands: Normal / Monitor / Attention Required / High Attention
- Dashboard cards and Recharts graphs
- Animal detail, alerts (mark resolved), analysis history
- SQLite persistence via SQLAlchemy
- Demo mode for viva presentations without farm footage
- Explicit model-missing error instead of silent failure

## Technology stack

| Layer | Tools |
| --- | --- |
| Backend | Python 3.11+, FastAPI, SQLAlchemy, SQLite |
| Vision | OpenCV, Ultralytics YOLO, NumPy, Pandas |
| Frontend | React, Vite, Recharts |
| Storage | `backend/uploads`, `backend/processed`, `cattlevision.db` |

## System architecture

```
Browser (React / Vite)
        |  REST /api
FastAPI  —  YOLO detector
        —  Tracker + behaviour + risk
        —  SQLite (animals, observations, alerts, sessions)
        —  Annotated images/videos
```

## AI workflow

1. Validate and store the upload.
2. Run YOLO; keep cattle-like classes only.
3. Image: assign Cow #01… left to right; posture from box shape.
4. Video: track boxes; estimate motion and activity duration.
5. Compute an **experimental** 0–100 risk score.
6. Draw overlays; save processed media; store DB rows.
7. Frontend polls video jobs so the browser does not freeze.

The behaviour module is rule-based on purpose. `risk.py` is the slot for a future trained anomaly model.

## Database architecture

Tables: `animals`, `observations`, `behavior_records`, `alerts`, `analysis_sessions`.  
See `docs/08_Database_Design.md`.

## Installation

### Backend setup

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` if you need to change ports, file-size limits, or disable demo seeding.

### Frontend setup

```bash
cd frontend
npm install
```

### Model setup

See `models/README.md`. Short version:

```bash
cd backend
source .venv/bin/activate
python scripts/download_model.py
```

Place `yolov8n.pt` or `cattle.pt` in `models/`. If the file is missing, every detection API returns a clear 503 message.

## How to run

Terminal 1:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2:

```bash
cd frontend
npm run dev
```

Open **http://127.0.0.1:5173**. Interactive API: **http://127.0.0.1:8000/docs**.

More detail: `RUN.md`.

## How to test

```bash
cd backend
source .venv/bin/activate
pytest -q
```

Tests cover health, demo dashboard, animals, alerts, file validation, tracker IoU, and risk bands. They do **not** require a GPU. Image/video inference tests need `models/yolov8n.pt` and are run manually in the UI.

## Sample workflow

1. Start backend and frontend.
2. Open the dashboard (demo herd of 12 animals).
3. Toggle **Show demo data** off to hide sample rows.
4. Go to **Image Analysis**, upload a cow photo, inspect boxes and confidences.
5. Go to **Video Analysis**, upload a short mp4, wait for the progress bar, review alerts.
6. Open an animal (for example demo **Cow #04**) and read the recommendation.
7. On **Alerts**, mark an item resolved.

## API summary

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | App + model status |
| GET | `/api/model/status` | Model path / missing-model help |
| POST | `/api/analyze/image` | Cattle detection on an image |
| POST | `/api/analyze/video` | Start backend video job |
| GET | `/api/analyze/video/{job_id}` | Poll job progress |
| POST | `/api/analyze/frame` | Live webcam frame |
| GET | `/api/animals` | List animals |
| GET | `/api/animals/{id}` | Animal detail |
| GET | `/api/alerts` | List alerts |
| POST | `/api/alerts/{id}/resolve` | Mark resolved |
| GET | `/api/dashboard` | Cards + chart series |
| GET | `/api/analysis` | Session history |
| GET | `/api/analysis/{id}` | One session |
| GET | `/api/media/{uploads\|processed}/{file}` | Saved media |

Query flag `include_demo=true|false` filters demo records on dashboard, animals, and alerts.

## Limitations

- COCO `cow` is not a custom dairy/beef dataset.
- Track IDs can jump when animals overlap or the camera moves.
- “Limping” is a coarse motion heuristic, not gait analysis.
- One photo cannot measure duration of inactivity.
- Risk scores are **experimental computer-vision indicators**, not medical findings.
- Large videos are slow on CPU; analysis uses a frame stride.

## Future improvements

- Train YOLO on a labelled farm cattle dataset
- Replace rules with a supervised behaviour / anomaly model
- Multi-camera farm layout and edge devices
- RFID or ear-tag ID fusion
- Temperature / humidity IoT context
- Mobile app for field workers

## How this project can be expanded into a real farm system

- **Multiple cameras** covering sheds, walkways, and water points, with a camera registry in the database.
- **Edge AI** (Jetson / Coral / farm PC) so video is not streamed unprocessed to a laptop.
- **IoT sensors** for waterer visits, barn temperature, humidity, and ammonia as context next to vision scores.
- **RFID identification** so Cow #04 in vision is joined to a lifetime animal record.
- **Cloud monitoring** for multi-site dashboards, user roles, and audit logs.
- **Mobile application** for alerts and “inspect this pen” tasks.
- **Custom cattle behaviour dataset** with standing, lying, lame gait, and rumination labels collected under farm lighting.

A production farm system would also need privacy policy, on-animal welfare SOPs, and a veterinarian in the validation loop. This repository stops at a demonstrable MVP.

## Project structure

```
cattlevision-ai/
├── backend/          FastAPI app, SQLite, uploads, tests
├── frontend/         React + Vite UI
├── models/           YOLO weights (not committed) + README
├── sample_data/      Demo descriptions
├── docs/             College project write-ups
├── README.md
└── RUN.md
```

## Disclaimer

CattleVision AI does not replace a qualified veterinarian. Use it only as a visual screening aid for education and engineering demonstration.
