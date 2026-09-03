# How to run CattleVision AI

## 1. Backend

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/download_model.py   # saves models/yolov8n.pt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs: http://127.0.0.1:8000/docs  
Health: http://127.0.0.1:8000/api/health

## 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173

## 3. First image analysis

1. Confirm `/api/health` shows `model_loaded: true`.
2. Open **Image Analysis**.
3. Upload a jpg/png of cattle.
4. Click **Run detection**.
5. Download the processed image if needed.

If the model is missing, the UI shows:
`AI model not found. Please download/configure the model.`

## 4. Tests

```bash
cd backend
source .venv/bin/activate
pytest -q
```
