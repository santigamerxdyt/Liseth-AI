"""
Tests for BrainRouter API endpoints (/api/brain/chat, /api/brain/stats, /api/brain/force).
"""
from unittest.mock import AsyncMock
import pytest
from fastapi.testclient import TestClient
from app.config import settings
from app.main import app
from app.services.brain_router import brain_router

client = TestClient(app)
client.post("/api/auth/login", json={"pin": settings.JARVIS_ACCESS_PIN})


def test_brain_chat_endpoint_gemini_success():
    # Mock brain_router generate_response
    brain_router.generate_response = AsyncMock(return_value={
        "text": "Hola Santiago, ¿en qué puedo ayudarte hoy?",
        "brain": "gemini",
        "failover": False,
        "usage": {"input": 12, "output": 24},
        "model": "gemini-2.0-flash",
    })

    res = client.post(
        "/api/brain/chat",
        json={
            "contents": [{"role": "user", "parts": [{"text": "Hola"}]}],
            "systemInstruction": "Eres Liseth.",
        }
    )

    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert "Hola Santiago" in data["text"]
    assert data["brainUsed"] == "gemini"


def test_brain_stats_endpoint():
    res = client.get("/api/brain/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert "activeBrain" in data
    assert "stats" in data


def test_brain_force_toggle():
    res = client.post("/api/brain/force", json={"brain": "claude"})
    assert res.status_code == 200
    assert res.json()["forcedBrain"] == "claude"

    # Reset
    res_reset = client.post("/api/brain/force", json={"brain": None})
    assert res_reset.status_code == 200
    assert res_reset.json()["forcedBrain"] is None
