"""
Unit tests for system_router endpoints (/api/status, /api/config, /api/history).
"""
import pytest
from fastapi.testclient import TestClient
from app.config import settings
from app.main import app

client = TestClient(app)
client.post("/api/auth/login", json={"pin": settings.JARVIS_ACCESS_PIN})


def test_system_status_endpoint():
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert data["status"] == "online"
    assert data["system"] == "JARVIS / Liseth"
    assert "port" in data
    assert "activeModel" in data


def test_system_config_endpoint():
    res = client.get("/api/config")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert "apiKeyConfigured" in data
    assert "voiceSettings" in data


def test_chat_history_roundtrip():
    # 1. Post a new history
    test_history = [
        {"role": "user", "parts": [{"text": "Hola Liseth prueba de persistencia"}]},
        {"role": "model", "parts": [{"text": "A su orden, Señor Santiago"}]},
    ]
    post_res = client.post("/api/history", json={"history": test_history})
    assert post_res.status_code == 200
    assert post_res.json()["ok"] is True

    # 2. Get history back
    get_res = client.get("/api/history")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["ok"] is True
    assert len(data["history"]) >= 2
    assert data["history"][0]["parts"][0]["text"] == "Hola Liseth prueba de persistencia"


def test_system_dnd_endpoints():
    # 1. Get DND status
    res = client.get("/api/system/dnd")
    assert res.status_code == 200
    assert "dnd" in res.json()

    # 2. Enable DND
    post_res = client.post("/api/system/dnd", json={"enabled": True})
    assert post_res.status_code == 200
    assert post_res.json()["dnd"] is True

    # 3. Disable DND
    post_res2 = client.post("/api/system/dnd", json={"enabled": False})
    assert post_res2.status_code == 200
    assert post_res2.json()["dnd"] is False


def test_system_optimize_ram_endpoint():
    res = client.post("/api/system/optimize-ram", json={})
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert "message" in data


def test_system_calendar_endpoints():
    # 1. Add event
    post_res = client.post("/api/system/calendar", json={
        "summary": "Reunión de prueba API",
        "startTime": "2026-10-16T17:00:00",
        "meetingLink": "https://meet.google.com/test-endpoint"
    })
    assert post_res.status_code == 200
    evt = post_res.json()["event"]
    assert evt["summary"] == "Reunión de prueba API"

    # 2. Get events
    get_res = client.get("/api/system/calendar")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["ok"] is True
    assert any(e["id"] == evt["id"] for e in data["events"])


def test_system_deep_work_endpoints():
    # 1. Start session
    start_res = client.post("/api/system/deep-work", json={
        "action": "start",
        "duration": 45,
        "task": "Programación backend"
    })
    assert start_res.status_code == 200
    assert start_res.json()["ok"] is True
    assert start_res.json()["data"]["status"] == "started"
    assert start_res.json()["data"]["duration_minutes"] == 45

    # 2. Get status
    stat_res = client.get("/api/system/deep-work")
    assert stat_res.status_code == 200
    stat_data = stat_res.json()["data"]
    assert stat_data["is_active"] is True
    assert stat_data["task"] == "Programación backend"

    # 3. Stop session
    stop_res = client.post("/api/system/deep-work", json={"action": "stop"})
    assert stop_res.status_code == 200
    assert stop_res.json()["data"]["status"] == "stopped"

    # 4. Verify inactive
    stat_res2 = client.get("/api/system/deep-work")
    assert stat_res2.json()["data"]["is_active"] is False


def test_system_shutdown_endpoint(monkeypatch):
    """Verifies that the /api/system/shutdown endpoint triggers gracefully."""
    monkeypatch.setattr("app.actions.system_shutdown.shutdown_liseth", lambda delay_seconds: "Hasta luego, señor Santiago.")
    res = client.post("/api/system/shutdown", json={"delaySeconds": 0.1})
    assert res.status_code == 200
    assert res.json()["ok"] is True
    assert "Hasta luego" in res.json()["message"]

