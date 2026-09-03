from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.services.behavior import classify_still_image
from app.services.detector import Detection
from app.services.risk import risk_band, score_still_image
from app.services.tracker import CattleTracker, iou


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["app"] == "CattleVision AI"
    assert "disclaimer" in body
    assert body["status"] in {"ok", "degraded"}


def test_dashboard_demo_data(client):
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    body = response.json()
    assert body["includes_demo_data"] is True
    assert body["total_animals"] >= 12
    assert "DEMO" in body["disclaimer"] or "educational" in body["disclaimer"].lower() or "not a veterinary" in body["disclaimer"].lower()


def test_animals_and_detail(client):
    listing = client.get("/api/animals")
    assert listing.status_code == 200
    animals = listing.json()
    assert len(animals) >= 12
    cow = next(a for a in animals if a["animal_identifier"] == "Cow #04")
    assert cow["is_demo"] is True
    detail = client.get(f"/api/animals/{cow['id']}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["animal_identifier"] == "Cow #04"
    assert body["is_demo"] is True
    assert len(body["observations"]) > 0


def test_alerts_resolve(client):
    response = client.get("/api/alerts")
    assert response.status_code == 200
    alerts = response.json()
    assert len(alerts) >= 1
    target = next((item for item in alerts if not item["resolved"]), alerts[0])
    resolved = client.post(f"/api/alerts/{target['id']}/resolve")
    assert resolved.status_code == 200
    assert resolved.json()["resolved"] is True


def test_invalid_image_rejected(client):
    response = client.post(
        "/api/analyze/image",
        files={"file": ("notes.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 400
    assert response.json()["error"] is True


def test_missing_analysis(client):
    response = client.get("/api/analysis/999999")
    assert response.status_code == 404


def test_iou_and_tracker():
    assert iou((0, 0, 10, 10), (0, 0, 10, 10)) == 1.0
    assert iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0
    tracker = CattleTracker()
    d1 = Detection("cow", 0.9, 10, 10, 40, 40)
    tracks = tracker.update([d1], 0, 0.0)
    assert tracks[0].label == "Cow #01"
    d2 = Detection("cow", 0.91, 12, 11, 40, 40)
    tracks = tracker.update([d2], 1, 0.1)
    assert tracks[0].label == "Cow #01"
    assert tracks[0].hits >= 2


def test_still_image_behavior_and_risk():
    lying = classify_still_image(1.8, 0.9)
    standing = classify_still_image(0.8, 0.9)
    assert lying.behavior == "Resting/lying"
    assert standing.behavior == "Standing"
    risk = score_still_image(lying, 0.9)
    assert 0 <= risk.score <= 100
    assert risk_band(12) == "Normal"
    assert risk_band(50) == "Monitor"
    assert risk_band(70) == "Attention Required"
    assert risk_band(90) == "High Attention"


def test_model_status(client):
    response = client.get("/api/model/status")
    assert response.status_code == 200
    body = response.json()
    assert "loaded" in body
    assert "help" in body


def test_sample_image_detection(client):
    root = Path(__file__).resolve().parents[2]
    model = root / "models" / "yolov8n.pt"
    sample = root / "sample_data" / "sample_cattle.jpg"
    if not model.exists() or not sample.exists():
        pytest.skip("YOLO model or sample image is not available")
    health = client.get("/api/health").json()
    if not health.get("model_loaded"):
        pytest.skip("AI model is not loaded")
    with sample.open("rb") as handle:
        response = client.post(
            "/api/analyze/image",
            files={"file": ("sample_cattle.jpg", handle, "image/jpeg")},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["cattle_count"] >= 1
    assert body["detections"][0]["animal_id"].startswith("Cow #")
    assert "not a veterinary diagnosis" in body["disclaimer"].lower() or "educational" in body["disclaimer"].lower()
