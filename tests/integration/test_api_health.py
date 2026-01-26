"""Integration test: API health endpoint."""

from fastapi.testclient import TestClient

from thermal_commons_mvp.api.main import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "COOL" in data.get("service", "")
