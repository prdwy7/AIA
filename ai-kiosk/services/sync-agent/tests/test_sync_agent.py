"""sync-agent skeleton smoke tests."""

from fastapi.testclient import TestClient
from sync_agent.main import create_app


def test_health():
    with TestClient(create_app()) as c:
        r = c.get("/health")
        assert r.status_code == 200
        assert r.json()["service"] == "sync-agent"


def test_ready():
    with TestClient(create_app()) as c:
        r = c.get("/ready")
        assert r.status_code == 200
        assert r.json()["ready"] is True
