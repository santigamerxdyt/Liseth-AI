"""Free access and reversible account/payment shutdown."""
import asyncio

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.requests import Request

from app.config import settings
from app.core.auth import is_authenticated, is_owner_or_creator_authenticated, require_auth
from app.main import app


def request_for(host="127.0.0.1"):
    return Request({"type": "http", "headers": [], "query_string": b"", "client": (host, 1234)})


def test_free_access_without_account(monkeypatch):
    monkeypatch.setattr(settings, "FREE_ACCESS", True)
    request = request_for()
    assert is_authenticated(request)
    assert asyncio.run(require_auth(request)) == {"type": "free_access"}
    assert is_owner_or_creator_authenticated(request)
    assert not is_owner_or_creator_authenticated(request_for("203.0.113.9"))
    client = TestClient(app)
    assert client.get("/api/auth/status").json()["authenticated"] is True
    assert client.get("/api/does-not-exist").status_code == 404  # Passes auth middleware.


@pytest.mark.parametrize("path", [
    "auth/register", "auth/firebase", "auth/login", "billing/checkout",
    "billing/webhook", "billing/topup", "referrals", "admin/plans/PRO",
])
def test_commercial_endpoints_are_disabled(monkeypatch, path):
    monkeypatch.setattr(settings, "FREE_ACCESS", True)
    response = TestClient(app).post("/api/saas/" + path, json={})
    assert response.status_code == 403
    assert response.json()["freeAccess"] is True


def test_reactivation_restores_authentication(monkeypatch):
    monkeypatch.setattr(settings, "FREE_ACCESS", False)
    request = request_for()
    assert not is_authenticated(request)
    assert not is_owner_or_creator_authenticated(request)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(require_auth(request))
    assert exc.value.status_code == 401
    client = TestClient(app)
    assert client.get("/api/does-not-exist").status_code == 401
    # Public registration is restored, but invalid input cannot create an account.
    assert client.post("/api/saas/auth/register", json={}).status_code == 422


def test_shared_browser_configuration():
    response = TestClient(app).get("/access-mode.js")
    assert response.status_code == 200
    assert '"freeAccess": true' in response.text
    assert response.headers["cache-control"] == "no-store"
