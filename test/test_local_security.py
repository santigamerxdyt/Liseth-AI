"""
Unit tests for Local-Only isolation, remote IP firewall blocking (403),
and strict owner authentication locking (401).
"""
import pytest
from fastapi.testclient import TestClient
from app.config import settings
from app.main import app

client = TestClient(app)


def test_remote_ip_blocked_by_local_only_guard():
    """
    Simulates a request originating from an external network / LAN IP (e.g. 192.168.1.55).
    Must be blocked immediately with 403 Forbidden.
    """
    remote_client = TestClient(app, client=("192.168.1.55", 54321))
    res = remote_client.get("/api/status")
    assert res.status_code == 403
    data = res.json()
    assert data["ok"] is False
    assert "Acceso restringido" in data["error"]
    assert "modo local privado" in data["error"]


def test_local_ip_allowed_by_guard():
    """
    Requests from 127.0.0.1 must be accepted.
    """
    local_client = TestClient(app, client=("127.0.0.1", 54321))
    res = local_client.get("/api/status")
    assert res.status_code == 200
    assert res.json()["ok"] is True


def test_unauthenticated_api_access_blocked_401():
    """
    Endpoints that execute actions or read data must return 401 when no auth is present.
    """
    unauth_client = TestClient(app)

    protected_endpoints = [
        ("GET", "/api/system/info"),
        ("GET", "/api/system/processes"),
        ("POST", "/api/system/execute"),
        ("GET", "/api/system/search?q=test"),
        ("GET", "/api/system/read?path=test"),
        ("GET", "/api/files/catalog"),
        ("GET", "/api/scheduler/tasks"),
        ("POST", "/api/scheduler/tasks/trigger"),
        ("GET", "/api/google/status"),
        ("POST", "/api/google/execute"),
        ("GET", "/api/brain/stats"),
        ("POST", "/api/brain/chat"),
        ("GET", "/api/tts?text=test"),
    ]

    for method, path in protected_endpoints:
        if method == "GET":
            res = unauth_client.get(path)
        else:
            res = unauth_client.post(path, json={})
        assert res.status_code == 401, f"Expected 401 for {path}, got {res.status_code}"
        assert res.json()["authRequired"] is True


def test_authenticated_owner_can_access():
    """
    When authenticating with the configured personal PIN, access is granted.
    """
    auth_client = TestClient(app)
    login_res = auth_client.post("/api/auth/login", json={"pin": settings.JARVIS_ACCESS_PIN})
    assert login_res.status_code == 200
    assert login_res.json()["ok"] is True

    # Now protected endpoints succeed
    res = auth_client.get("/api/system/info")
    assert res.status_code == 200
    assert res.json()["ok"] is True
