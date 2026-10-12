"""advisory-service skeleton smoke tests."""

from advisory_service.main import create_app
from fastapi.testclient import TestClient


def test_health():
    with TestClient(create_app()) as c:
        r = c.get("/health")
        assert r.status_code == 200
        assert r.json()["service"] == "advisory-service"


def test_ready():
    with TestClient(create_app()) as c:
        r = c.get("/ready")
        assert r.status_code == 200
        assert r.json()["ready"] is True
