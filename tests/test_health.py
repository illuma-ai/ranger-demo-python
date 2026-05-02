from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_extended_returns_all_fields() -> None:
    response = client.get("/health/extended")
    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert isinstance(data["status"], str)
    assert data["status"] == "ok"

    assert "uptime_seconds" in data
    assert isinstance(data["uptime_seconds"], float)
    assert data["uptime_seconds"] >= 0

    assert "version" in data
    assert isinstance(data["version"], str)
    assert data["version"] == "1.0.0"
