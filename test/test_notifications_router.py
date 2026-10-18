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


def test_telegram_status_endpoint():
    res = client.get("/api/notifications/telegram/status")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert "hasToken" in data
    assert "isPolling" in data


def test_telegram_webhook_commands():
    # 1. /start command
    res_start = client.post("/api/notifications/telegram/webhook", json={
        "message": {"chat": {"id": 123456}, "text": "/start"}
    })
    assert res_start.status_code == 200
    assert "Liseth" in res_start.json()["reply"]
    assert "/estado" in res_start.json()["reply"]

    # 2. /estado command
    res_stat = client.post("/api/notifications/telegram/webhook", json={
        "message": {"chat": {"id": 123456}, "text": "/estado"}
    })
    assert res_stat.status_code == 200
    assert "Telemetría" in res_stat.json()["reply"]

    # 3. /dnd command
    res_dnd = client.post("/api/notifications/telegram/webhook", json={
        "message": {"chat": {"id": 123456}, "text": "/dnd"}
    })
    assert res_dnd.status_code == 200
    assert "Modo No Molestar" in res_dnd.json()["reply"]

