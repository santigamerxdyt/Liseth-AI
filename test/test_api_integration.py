"""
Integration tests for FastAPI application endpoints, auth middleware, and static serving.
"""
import pytest
from fastapi.testclient import TestClient
from app.config import settings
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["version"] == "2.0.0"


def test_serve_frontend_index_and_static():
    # Test index.html
    res_index = client.get("/")
    assert res_index.status_code == 200
    assert "text/html" in res_index.headers["content-type"]
    assert "Liseth" in res_index.text

    # Test static css
    res_css = client.get("/static/css/style.css")
    assert res_css.status_code == 200
    assert "text/css" in res_css.headers["content-type"]

    # Test static js
    res_js = client.get("/static/js/app.js")
    assert res_js.status_code == 200

    # Test manifest
    res_manifest = client.get("/static/manifest.json")
    assert res_manifest.status_code == 200


def test_auth_middleware_blocks_unauthorized_api():
    # Accessing /api/files without credentials must return 401
    res = client.get("/api/files")
    assert res.status_code == 401
    data = res.json()
    assert data["ok"] is False
    assert data["authRequired"] is True


def test_login_flow_and_authenticated_access():
    correct_pin = settings.JARVIS_ACCESS_PIN

    # 1. Failed login with wrong PIN
    res_bad = client.post("/api/auth/login", json={"pin": "wrong_pin_9999"})
    assert res_bad.status_code == 401
    assert res_bad.json()["ok"] is False

    # 2. Successful login with configured PIN
    res_login = client.post("/api/auth/login", json={"pin": correct_pin})
    assert res_login.status_code == 200
    data = res_login.json()
    assert data["ok"] is True
    assert "token" in data
    token = data["token"]

    # Cookie liseth_session should be set in response
    assert "liseth_session" in res_login.cookies

    # 3. Access protected endpoint with cookie
    res_files = client.get("/api/files", cookies={"liseth_session": token})
    assert res_files.status_code == 200
    assert "files" in res_files.json()

    # 4. Access protected endpoint with Bearer header
    res_files_header = client.get(
        "/api/files",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res_files_header.status_code == 200
    assert "files" in res_files_header.json()

    # 5. Check auth status
    res_status = client.get("/api/auth/status", cookies={"liseth_session": token})
    assert res_status.status_code == 200
    assert res_status.json()["authenticated"] is True

    # 6. Logout
    res_logout = client.post("/api/auth/logout")
    assert res_logout.status_code == 200
    assert res_logout.json()["authenticated"] is False
