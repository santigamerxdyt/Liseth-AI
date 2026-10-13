"""
Unit tests for system_router endpoints (/api/status, /api/config, /api/history).
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


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
