"""
Automated Verification Suite for:
1. Always require identity verification code ("Código de Verificación de Inicio")
2. Always require login on application and web startup
3. Mobile device responsiveness, viewport, touch targets, and audio safeguards
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.core.database import AsyncSessionLocal
from sqlalchemy import select
from app.core.models import SaasUser
import asyncio

client = TestClient(app)


def test_verify_launch_code_endpoint():
    # 1. Rejects invalid launch code
    bad_resp = client.post("/api/auth/verify-launch-code", json={"code": "wrong_code_999"})
    assert bad_resp.status_code == 401
    assert bad_resp.json().get("ok") is False

    # 2. Accepts valid master launch code
    correct_pin = settings.JARVIS_ACCESS_PIN.strip()
    good_resp = client.post("/api/auth/verify-launch-code", json={"code": correct_pin})
    assert good_resp.status_code == 200
    assert good_resp.json().get("ok") is True
    assert good_resp.json().get("valid") is True


def test_creator_login_with_launch_code():
    correct_pin = settings.JARVIS_ACCESS_PIN.strip()
    resp = client.post(
        "/api/auth/login",
        json={"pin": correct_pin, "launch_code": correct_pin}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("ok") is True
    assert data.get("authenticated") is True
    assert "token" in data


def test_saas_user_registration_and_login_with_launch_code():
    test_email = "launchuser@lisethguard.com"
    test_pw = "LaunchSecure123!"
    personal_code = "SECRET_PIN_8899"

    # 1. Clean up old user if present
    async def cleanup():
        async with AsyncSessionLocal() as db:
            existing = await db.execute(select(SaasUser).where(SaasUser.email == test_email))
            u_old = existing.scalars().first()
            if u_old:
                await db.delete(u_old)
                await db.commit()

    asyncio.run(cleanup())

    # 2. Register user with personal launch code and brain key
    reg_resp = client.post(
        "/api/saas/auth/firebase",
        json={
            "mode": "register",
            "email": test_email,
            "password": test_pw,
            "full_name": "Usuario Verificado",
            "selected_plan": "STARTER",
            "gemini_api_key": "AIzaSyTestKeyForLaunchVerification",
            "launch_code": personal_code,
        },
    )
    assert reg_resp.status_code == 200, reg_resp.text
    data = reg_resp.json()
    assert data.get("ok") is True

    # 3. Attempt login with INCORRECT launch code -> MUST BE REJECTED (401)
    bad_login = client.post(
        "/api/saas/auth/firebase",
        json={
            "mode": "login",
            "email": test_email,
            "password": test_pw,
            "launch_code": "WRONG_ATTACKER_CODE",
        },
    )
    assert bad_login.status_code == 401
    assert "verificación de inicio inválido" in bad_login.text or "Código" in bad_login.text

    # 4. Attempt login with CORRECT personal launch code -> MUST SUCCEED (200)
    good_login = client.post(
        "/api/saas/auth/firebase",
        json={
            "mode": "login",
            "email": test_email,
            "password": test_pw,
            "launch_code": personal_code,
        },
    )
    assert good_login.status_code == 200
    login_data = good_login.json()
    assert login_data.get("ok") is True
    assert "token" in login_data

    # 5. Direct login endpoint (/api/saas/auth/login) also validates launch_code
    bad_direct = client.post(
        "/api/saas/auth/login",
        json={
            "email": test_email,
            "password": test_pw,
            "launch_code": "BAD_PIN_0000",
        },
    )
    assert bad_direct.status_code == 401

    good_direct = client.post(
        "/api/saas/auth/login",
        json={
            "email": test_email,
            "password": test_pw,
            "launch_code": personal_code,
        },
    )
    assert good_direct.status_code == 200


def test_html_mobile_safeguards_and_auth_gate_fields():
    for fpath in ["index.html", "app/static/index.html", "jarvis.html"]:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        # Viewport has interactive-widget and mobile capabilities
        assert "interactive-widget=resizes-content" in content
        assert "mobile-web-app-capable" in content

        # Auth modal has dedicated launch code inputs
        assert 'id="gate-login-launch-code"' in content
        assert 'id="gate-reg-launch-code"' in content

        # Check that checkAuthSession does NOT auto-bypass modal on start
        assert "showAuthModal()" in content
        assert "sessionStorage.removeItem(\"liseth_active_session_authenticated\")" in content

        # Mobile CSS safeguards
        assert "@media (max-width: 768px)" in content
        assert "gate-main-grid" in content
        assert "unlockMobileAudioOnTouch" in content
