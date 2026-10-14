"""
Tests for Google Workspace API router endpoints.
"""
from fastapi.testclient import TestClient
from app.config import settings
from app.main import app

client = TestClient(app)
client.post("/api/auth/login", json={"pin": settings.JARVIS_ACCESS_PIN})


def test_google_status_endpoint():
    res = client.get("/api/google/status")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert "connected" in data
    assert "hasCredentials" in data


def test_google_auth_url_endpoint():
    res = client.get("/api/google/auth-url")
    # Returns 200 with URL or 400 if credentials not configured in environment
    assert res.status_code in [200, 400]
    if res.status_code == 200:
        assert "authUrl" in res.json()
        assert "accounts.google.com" in res.json()["authUrl"]


def test_google_execute_sensitive_action_requires_confirmation():
    # Sending email must require confirmation
    res = client.post(
        "/api/google/execute",
        json={
            "action": "google_send_email",
            "params": {
                "to": "test@example.com",
                "subject": "Test",
                "body": "Hola",
            },
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert data["requiresConfirmation"] is True
    assert "confirmation" in data
