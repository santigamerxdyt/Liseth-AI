import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import AsyncSessionLocal
from sqlalchemy import select
from app.core.models import SaasUser
import asyncio


client = TestClient(app)


def test_user_registration_with_custom_brain_api_keys():
    test_email = "brainuser@teststark.com"
    test_pw = "BrainPass123!"
    gemini_test_key = "AIzaSyTestUserKey1234567890"
    groq_test_key = "gsk_testGroqUserKey1234567890"

    # 1. Clean up old user if present
    async def cleanup():
        async with AsyncSessionLocal() as db:
            existing = await db.execute(select(SaasUser).where(SaasUser.email == test_email))
            u_old = existing.scalars().first()
            if u_old:
                await db.delete(u_old)
                await db.commit()

    asyncio.run(cleanup())

    # 2. Register with brain API keys
    reg_resp = client.post(
        "/api/saas/auth/firebase",
        json={
            "mode": "register",
            "email": test_email,
            "password": test_pw,
            "full_name": "Ingeniero Stark",
            "gemini_api_key": gemini_test_key,
            "groq_api_key": groq_test_key,
        },
    )
    assert reg_resp.status_code == 200, reg_resp.text
    data = reg_resp.json()
    assert data.get("ok") is True
    token = data.get("token")
    assert token is not None

    # Check serialized user api_keys_status
    user_info = data.get("user", {})
    assert "api_keys_status" in user_info
    assert user_info["api_keys_status"]["has_gemini"] is True
    assert user_info["api_keys_status"]["has_groq"] is True
    assert "AIza" in user_info["api_keys_status"]["gemini_masked"]

    # 3. Verify keys stored in database preferences
    async def verify_db_keys():
        async with AsyncSessionLocal() as db:
            res = await db.execute(select(SaasUser).where(SaasUser.email == test_email))
            u = res.scalars().first()
            assert u is not None
            prefs = u.preferences or {}
            assert "api_keys" in prefs
            assert prefs["api_keys"].get("gemini_api_key") == gemini_test_key
            assert prefs["api_keys"].get("groq_api_key") == groq_test_key

    asyncio.run(verify_db_keys())

    # 4. GET /api/saas/profile/api-keys
    headers = {"X-SaaS-Token": token}
    get_keys_resp = client.get("/api/saas/profile/api-keys", headers=headers)
    assert get_keys_resp.status_code == 200
    keys_data = get_keys_resp.json().get("api_keys", {})
    assert keys_data["has_gemini"] is True
    assert keys_data["has_groq"] is True
    assert "••••" in keys_data["gemini_api_key"]

    # 5. Update keys via PUT /api/saas/profile/api-keys
    new_openai_key = "sk-proj-testOpenAI9876543210"
    put_keys_resp = client.put(
        "/api/saas/profile/api-keys",
        headers=headers,
        json={
            "openai_api_key": new_openai_key,
        },
    )
    assert put_keys_resp.status_code == 200
    upd_data = put_keys_resp.json()
    assert upd_data.get("ok") is True
    assert upd_data["api_keys"]["has_openai"] is True
    assert upd_data["api_keys"]["has_gemini"] is True  # preserved

    # 6. Verify database has updated keys
    async def verify_updated_db():
        async with AsyncSessionLocal() as db:
            res = await db.execute(select(SaasUser).where(SaasUser.email == test_email))
            u = res.scalars().first()
            prefs = u.preferences or {}
            assert prefs["api_keys"].get("openai_api_key") == new_openai_key
            assert prefs["api_keys"].get("gemini_api_key") == gemini_test_key

    asyncio.run(verify_updated_db())
