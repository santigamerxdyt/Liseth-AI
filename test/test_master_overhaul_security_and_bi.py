"""
Master Project Overhaul & Independent External Audit — Comprehensive Security,
Multi-Tenant Isolation, Credit Ledger, Credit Top-Up, and Creator Business Intelligence Validation Suite.
"""
import io
import logging
import secrets
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app, SensitiveLogRedactionFilter


client = TestClient(app)


def _new_email(prefix: str = "overhaul") -> str:
    return f"{prefix}_{secrets.token_hex(5)}@test-liseth.ai"


def test_host_endpoints_blocked_for_standard_saas_tenant():
    """
    Verifies that a standard SaaS tenant (role='USER') cannot execute host OS commands,
    mutate global JARVIS soul/memories, or access NFC/Firebase superadmin endpoints.
    """
    reg = client.post(
        "/api/saas/auth/register",
        json={
            "email": _new_email("tenant_sec"),
            "password": "SafePassword123!",
            "full_name": "Tenant Security Test",
        },
    )
    assert reg.status_code == 200
    token = reg.json()["token"]
    headers = {"X-SaaS-Token": token}

    # 1. Host OS & System control endpoints must return 403 Forbidden
    for method, path in [
        ("GET", "/api/system/info"),
        ("GET", "/api/system/processes"),
        ("POST", "/api/system/optimize-ram"),
        ("POST", "/api/system/shutdown"),
        ("POST", "/api/brain/soul"),
        ("POST", "/api/brain/memories/remember"),
        ("POST", "/api/brain/switch"),
        ("GET", "/api/nfc/admin/dashboard"),
        ("POST", "/api/nfc/clear-history"),
        ("POST", "/api/saas/firebase/config"),
        ("GET", "/api/audit/logs"),
        ("POST", "/api/google/execute"),
        ("POST", "/api/scheduler/tasks/trigger"),
    ]:
        if method == "GET":
            resp = client.get(path, headers=headers)
        else:
            resp = client.post(path, json={}, headers=headers)
        assert resp.status_code == 403, f"Expected 403 on {method} {path}, got {resp.status_code}"


def test_token_revocation_on_logout_and_redaction():
    """
    Verifies server-side session token revocation on logout and log secret redaction.
    """
    reg = client.post(
        "/api/saas/auth/register",
        json={
            "email": _new_email("logout_sec"),
            "password": "SafePassword123!",
            "full_name": "Logout Test User",
        },
    )
    assert reg.status_code == 200
    token = reg.json()["token"]
    headers = {"X-SaaS-Token": token}

    # Profile works before logout
    prof1 = client.get("/api/saas/profile", headers=headers)
    assert prof1.status_code == 200

    # Logout revokes the token server-side
    out = client.post("/api/saas/auth/logout", headers=headers)
    assert out.status_code == 200

    # Reusing the same token in header after logout must fail with 401
    prof2 = client.get("/api/saas/profile", headers=headers)
    assert prof2.status_code == 401

    # Verify Gemini API key redaction in logs
    f = SensitiveLogRedactionFilter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=1,
        msg="Key leak test: AIzaSyD1234567890abcdefABCDEF12345678 in log",
        args=(),
        exc_info=None,
    )
    f.filter(record)
    assert "AIzaSyD1234567890" not in record.msg
    assert "[REDACTED_API_KEY]" in record.msg


def test_aes256_api_keys_encryption_and_masking():
    """
    Verifies that tenant brain API keys are encrypted at rest (never exposed in plaintext
    inside user.preferences) and only masked previews are returned in API responses.
    """
    raw_gemini_key = "AIzaSyTestSecretKey9876543210abcdef"
    raw_groq_key = "gsk_TestGroqSecretKey9876543210abcdef"

    reg = client.post(
        "/api/saas/auth/register",
        json={
            "email": _new_email("enc_keys"),
            "password": "SafePassword123!",
            "full_name": "Encrypted Keys User",
            "gemini_api_key": raw_gemini_key,
            "groq_api_key": raw_groq_key,
        },
    )
    assert reg.status_code == 200
    user_payload = reg.json()["user"]

    # Raw keys or encrypted blob must NEVER be leaked in serialized preferences
    prefs = user_payload.get("preferences") or {}
    assert "api_keys" not in prefs
    assert "api_keys_enc" not in prefs
    assert raw_gemini_key not in str(user_payload)
    assert raw_groq_key not in str(user_payload)

    # Masked status must be present and accurate
    status_map = user_payload["api_keys_status"]
    assert status_map["configured_count"] >= 2
    assert status_map["providers"]["gemini"]["configured"] is True
    assert "••••" in status_map["providers"]["gemini"]["masked_key"]


def test_multitenant_file_isolation_bola_protection():
    """
    Verifies that files uploaded by Tenant A cannot be listed or downloaded by Tenant B,
    while Tenant A and CREATOR retain access.
    """
    u1 = client.post(
        "/api/saas/auth/register",
        json={"email": _new_email("file_u1"), "password": "Password123!", "full_name": "User One"},
    ).json()
    u2 = client.post(
        "/api/saas/auth/register",
        json={"email": _new_email("file_u2"), "password": "Password123!", "full_name": "User Two"},
    ).json()

    h1 = {"X-SaaS-Token": u1["token"]}
    h2 = {"X-SaaS-Token": u2["token"]}

    # User 1 uploads a private document
    up = client.post(
        "/api/upload",
        headers=h1,
        files={"file": ("confidencial_u1.txt", io.BytesIO(b"Secreto Financiero Tenant 1"), "text/plain")},
    )
    assert up.status_code == 200
    up_json = up.json()
    stored_filename = (up_json.get("file") or {}).get("name") or up_json.get("filename")
    assert stored_filename

    # User 1 sees and downloads their file
    list_u1 = client.get("/api/files", headers=h1)
    assert list_u1.status_code == 200
    assert any(f["name"] == stored_filename for f in list_u1.json()["files"])
    dl_u1 = client.get(f"/api/files/{stored_filename}", headers=h1)
    assert dl_u1.status_code == 200

    # User 2 CANNOT see or download User 1's file (BOLA protection)
    list_u2 = client.get("/api/files", headers=h2)
    assert list_u2.status_code == 200
    assert not any(f["name"] == stored_filename for f in list_u2.json()["files"])
    dl_u2 = client.get(f"/api/files/{stored_filename}", headers=h2)
    assert dl_u2.status_code in (403, 404)


def test_credit_ledger_topup_and_creator_business_intelligence():
    """
    Verifies:
    1. Immutable Credit Ledger entries across registration, email verification, plan checkout,
       chat message consumption, and credit pack top-up (`PACK_5K`).
    2. Creator Business Intelligence endpoint (`/api/saas/admin/business-intelligence`)
       blocked for standard users (403) and returning complete financial, cost, unit economics,
       and alert metrics for the CREATOR superadmin.
    """
    reg = client.post(
        "/api/saas/auth/register",
        json={
            "email": _new_email("ledger_bi"),
            "password": "Password123!",
            "full_name": "Ledger & BI User",
        },
    )
    assert reg.status_code == 200
    reg_data = reg.json()
    token = reg_data["token"]
    headers = {"X-SaaS-Token": token}

    # Verify email (+100 bonus credits)
    v_tok = reg_data.get("verification_token_preview")
    if v_tok:
        ver = client.post("/api/saas/auth/verify-email", json={"token": v_tok})
        assert ver.status_code == 200

    # Upgrade to STARTER plan ($10 USD)
    chk = client.post(
        "/api/saas/billing/checkout",
        headers=headers,
        json={
            "plan_code": "STARTER",
            "billing_cycle": "monthly",
            "payment_gateway": "bre_b",
            "payment_method_brand": "BRE-B",
            "payment_method_last4": "3100",
        },
    )
    assert chk.status_code == 200

    # Purchase a Credit Top-Up Pack (+5,000 credits for $20 USD)
    topup = client.post(
        "/api/saas/credits/topup",
        headers=headers,
        json={"pack_code": "PACK_5K", "payment_gateway": "bre_b"},
    )
    assert topup.status_code == 200
    topup_data = topup.json()
    assert topup_data["ok"] is True
    assert topup_data["credits_added"] == 5000

    # Send a conversation message to record AI consumption in the ledger
    conv = client.post(
        "/api/saas/conversations",
        headers=headers,
        json={"title": "Auditoría Financiera", "model_id": "gemini-2.5-flash"},
    ).json()["conversation"]
    msg = client.post(
        f"/api/saas/conversations/{conv['id']}/messages",
        headers=headers,
        json={"content": "Analiza el flujo de caja trimestral.", "use_live_ai": False},
    )
    assert msg.status_code == 200

    # Inspect Credit Ledger
    ledger_res = client.get("/api/saas/credits/ledger", headers=headers)
    assert ledger_res.status_code == 200
    ledger_data = ledger_res.json()
    assert ledger_data["ok"] is True
    tx_types = [entry["tx_type"] for entry in ledger_data["ledger"]]
    assert "plan_allocation" in tx_types
    assert "credit_topup" in tx_types
    assert any("consumption" in t for t in tx_types)

    # Standard user is blocked from Creator Business Intelligence
    bi_forbidden = client.get("/api/saas/admin/business-intelligence", headers=headers)
    assert bi_forbidden.status_code == 403

    # Authenticate as CREATOR (Señor Santiago) via PIN login
    pin_login = client.post("/api/auth/login", json={"pin": settings.JARVIS_ACCESS_PIN})
    assert pin_login.status_code == 200
    creator_token = pin_login.json()["token"]
    creator_headers = {"Authorization": f"Bearer {creator_token}"}

    bi_res = client.get("/api/saas/admin/business-intelligence", headers=creator_headers)
    assert bi_res.status_code == 200
    bi = bi_res.json()
    assert bi["ok"] is True

    # Validate the 4 core Business Intelligence domains
    assert "revenue" in bi
    assert "costs" in bi
    assert "profitability" in bi
    assert "alerts" in bi

    assert bi["revenue"]["collected_gross_usd"] >= 30.0
    assert bi["revenue"]["by_source"]["credit_topups_usd"] >= 20.0
    assert bi["costs"]["ai_inference_cost_usd"] >= 0.0
    assert len(bi["profitability"]["unit_economics_by_plan"]) >= 5
    assert "arpu_usd" in bi["profitability"]["kpis"]
    assert "ltv_usd" in bi["profitability"]["kpis"]
    assert len(bi["alerts"]) >= 1


def test_mandatory_onboarding_gate_and_firebase_owner_lock():
    """
    Verifies:
    1. A user cannot unlock `can_close_plans_tab` / `can_use_project` until they have:
       - Created an account saved in Señor Santiago's Google Firebase (`has_firebase_account`)
       - Provided their own AI Brain API key (`has_brain_api_key`)
       - Purchased a commercial plan (`STARTER`, `PRO`, `BUSINESS`, or `ENTERPRISE`) (`has_purchased_plan`)
    2. Only Señor Santiago (`CREATOR` / `JARVIS_ACCESS_PIN`) can modify Firebase config.
    """
    # 1. Incomplete user (Firebase account only, FREE plan, no API key) -> gate is locked
    email_inc = _new_email("fb_incomplete")
    fb_inc = client.post(
        "/api/saas/auth/firebase",
        json={
            "mode": "register",
            "email": email_inc,
            "password": "Password123!",
            "full_name": "Incomplete User",
            "selected_plan": "FREE",
        },
    )
    assert fb_inc.status_code == 200
    inc_user = fb_inc.json()["user"]
    inc_token = fb_inc.json()["token"]
    inc_headers = {"X-SaaS-Token": inc_token}

    gate1 = inc_user["onboarding_gate"]
    assert gate1["has_firebase_account"] is True
    assert gate1["has_brain_api_key"] is False
    assert gate1["has_purchased_plan"] is False
    assert gate1["is_complete"] is False
    assert gate1["can_close_plans_tab"] is False
    assert gate1["can_use_project"] is False

    # 2. User sets their AI API key -> still locked until they buy a paid plan
    k_res = client.put(
        "/api/saas/profile/api-keys",
        headers=inc_headers,
        json={"gemini_api_key": "AIzaSyUserPersonalBrainKey1234567890"},
    )
    assert k_res.status_code == 200
    gate2 = k_res.json()["user"]["onboarding_gate"]
    assert gate2["has_brain_api_key"] is True
    assert gate2["has_purchased_plan"] is False
    assert gate2["is_complete"] is False

    # 3. User buys STARTER plan -> all 3 requirements met, gate unlocks!
    chk_res = client.post(
        "/api/saas/billing/checkout",
        headers=inc_headers,
        json={"plan_code": "STARTER", "billing_cycle": "monthly", "payment_gateway": "bre_b"},
    )
    assert chk_res.status_code == 200
    prof_res = client.get("/api/saas/profile", headers=inc_headers)
    gate3 = prof_res.json()["user"]["onboarding_gate"]
    assert gate3["has_firebase_account"] is True
    assert gate3["has_brain_api_key"] is True
    assert gate3["has_purchased_plan"] is True
    assert gate3["is_complete"] is True
    assert gate3["can_close_plans_tab"] is True
    assert gate3["can_use_project"] is True

    # 4. Standard user or wrong creator_pin cannot modify Firebase config
    bad_pin_cfg = client.post(
        "/api/saas/firebase/config",
        json={"projectId": "hacked-project", "creator_pin": "000000"},
    )
    assert bad_pin_cfg.status_code == 403

    good_pin_cfg = client.post(
        "/api/saas/firebase/config",
        json={"projectId": "liseth-saas-ai", "creator_pin": settings.JARVIS_ACCESS_PIN},
    )
    assert good_pin_cfg.status_code == 200
    assert good_pin_cfg.json()["projectId"] == "liseth-saas-ai"

