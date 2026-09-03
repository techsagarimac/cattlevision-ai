# Technology Stack

## Backend

- Python 3.11+
- FastAPI and Uvicorn
- SQLAlchemy 2.x with SQLite
- OpenCV (headless) for decode/encode
- Ultralytics YOLO
- NumPy and Pandas (numerical summaries / future tabular export)
- Pydantic Settings for configuration
- Pytest and HTTPX TestClient

## Frontend

- React 18
- Vite
- JavaScript (JSX)
- React Router
- Recharts
- Custom CSS (agriculture / AI visual language: forest green, cream, wheat)

## AI

- Default: YOLOv8n COCO weights (`cow` class)
- Optional: user-supplied `cattle.pt`
- Rule-based behaviour and risk (no disease classifier)

## Data

- SQLite file `backend/cattlevision.db`
- Uploaded originals in `backend/uploads/`
- Annotated outputs in `backend/processed/`

## Why this stack

The stack matches common university syllabi (Python + REST + React), runs on a laptop, and keeps the vision pipeline visible for viva questions. FastAPI’s OpenAPI page documents endpoints without extra tooling.
