"""
Tests for Notifications API router endpoints.
"""
from fastapi.testclient import TestClient
from app.config import settings
from app.main import app

client = TestClient(app)
client.post("/api/auth/login", json={"pin": settings.JARVIS_ACCESS_PIN})


def test_notifications_test_endpoint():
    res = client.post("/api/notifications/test", json={"message": "Prueba de alerta", "channel": "all"})
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert data["success"] is True
    assert "Prueba de alerta" in data["content"]
