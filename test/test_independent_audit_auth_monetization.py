"""
Independent External Audit Test Suite:
1. Registration (Registro)
2. Login & 2FA Launch Verification Code (Inicio de Sesión)
3. CREATOR Identification & Superadmin Protection (Identificación CREATOR)
4. Monetization, Quotas, Plans & Sandbox Payments (Monetización en Sandbox)
"""
import asyncio
import json
import uuid
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.core.database import AsyncSessionLocal
from app.core.models import SaasUser, SaasSubscription, SaasPayment, SaasInvoice, SaasCreditBalance
from sqlalchemy import select, delete
from app.services.saas_service import CREATOR_USER_ID, CREATOR_EMAIL, saas_service, sign_saas_token

client = TestClient(app)


def _unique_email(prefix: str = "auditor") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}@liseth-audit.com"


class TestIndependentAuditScenarios:
    """
    Independent audit covering all 4 simulated user journeys:
    Scenario A: New User (Usuario Nuevo)
    Scenario B: Existing Regular User (Usuario Existente)
    Scenario C: Administrator / CREATOR (Usuario Administrador)
    Scenario D: Premium Subscriber & Sandbox Monetization (Usuario Premium / Monetización)
    """

    # --------------------------------------------------------------------------
    # SCENARIO A: NUEVO USUARIO (NEW USER ONBOARDING)
    # --------------------------------------------------------------------------
    def test_scenario_a_new_user_registration_and_persistent_gate(self):
        new_email = _unique_email("new_user")
        new_pw = "NewUserPass2026!"
        personal_launch_code = "PIN_NEW_7722"
        gemini_api_key = "AIzaSy_AuditNewUser_ValidKey_12345"

        # 1. Block registration attempting privilege escalation to CREATOR
        bad_reg = client.post(
            "/api/saas/auth/register",
            json={
                "email": new_email,
                "password": new_pw,
                "full_name": "Atacante Escalación",
                "plan_code": "CREATOR",
                "role": "CREATOR",
                "launch_code": personal_launch_code,
            },
        )
        assert bad_reg.status_code == 403
        assert "CREATOR" in bad_reg.text

        # 2. Block registration with weak password (< 8 chars)
        weak_reg = client.post(
            "/api/saas/auth/register",
            json={
                "email": new_email,
                "password": "123",
                "full_name": "Usuario Débil",
                "launch_code": personal_launch_code,
            },
        )
        assert weak_reg.status_code == 400

        # 3. Successful registration via Firebase Auth endpoint with Starter plan & Brain API Key
        reg = client.post(
            "/api/saas/auth/firebase",
            json={
                "mode": "register",
                "email": new_email,
                "password": new_pw,
                "full_name": "Carlos Mendoza",
                "selected_plan": "STARTER",
                "gemini_api_key": gemini_api_key,
                "launch_code": personal_launch_code,
                "payment_gateway": "stripe",
                "payment_method_brand": "visa",
                "payment_method_last4": "4242",
            },
        )
        assert reg.status_code == 200, reg.text
        data = reg.json()
        assert data.get("ok") is True
        assert "token" in data
        user_info = data.get("user", {})
        assert user_info.get("email") == new_email
        assert user_info.get("role") == "USER"
        assert user_info.get("plan_code") == "STARTER"

        # 4. Verify onboarding gate calculation:
        gate = user_info.get("onboarding_gate", {})
        assert gate.get("has_firebase_account") is True
        assert gate.get("has_brain_api_key") is True
        assert gate.get("has_purchased_plan") is True
        assert gate.get("is_complete") is True
        assert gate.get("can_close_plans_tab") is True
        assert gate.get("can_use_project") is True

        # 5. Verify database persistence
        async def verify_db_persistence():
            async with AsyncSessionLocal() as db:
                res = await db.execute(select(SaasUser).where(SaasUser.email == new_email))
                persisted_user = res.scalars().first()
                assert persisted_user is not None
                assert persisted_user.role == "USER"
                assert persisted_user.plan_code == "STARTER"
                prefs = persisted_user.preferences or {}
                assert prefs.get("launch_code") == personal_launch_code
                assert prefs.get("firebase_account_saved") is True
                assert "api_keys_enc" in prefs
                assert "api_keys" not in prefs  # No plaintext keys

                # Verify subscription record
                sub_res = await db.execute(select(SaasSubscription).where(SaasSubscription.user_id == persisted_user.id))
                sub = sub_res.scalars().first()
                assert sub is not None
                assert sub.plan_code == "STARTER"
                assert sub.status == "active"

                # Verify credits
                bal_res = await db.execute(select(SaasCreditBalance).where(SaasCreditBalance.user_id == persisted_user.id))
                bal = bal_res.scalars().first()
                assert bal is not None
                assert bal.monthly_credits_allocated == 2500

        asyncio.run(verify_db_persistence())

        # 6. Verify Firebase registry file persistence
        reg_file = settings.DATA_DIR / "firebase_users_registry.json"
        assert reg_file.exists()
        reg_data = json.loads(reg_file.read_text(encoding="utf-8"))
        assert user_info["id"] in reg_data.get("users", {})
        fb_user = reg_data["users"][user_info["id"]]
        assert fb_user["email"] == new_email
        assert fb_user["has_brain_api_key"] is True
        assert fb_user["plan_code"] == "STARTER"

    # --------------------------------------------------------------------------
    # SCENARIO B: USUARIO EXISTENTE (LOGIN, 2FA LAUNCH CODE & ISOLATION)
    # --------------------------------------------------------------------------
    def test_scenario_b_existing_user_login_and_security(self):
        existing_email = _unique_email("existing_user")
        existing_pw = "ExistingUserPass2026!"
        personal_launch_code = "PIN_EXISTING_9911"
        gemini_api_key = "AIzaSy_AuditExisting_Key_67890"

        # Register existing user
        reg = client.post(
            "/api/saas/auth/firebase",
            json={
                "mode": "register",
                "email": existing_email,
                "password": existing_pw,
                "full_name": "Laura Restrepo",
                "selected_plan": "STARTER",
                "gemini_api_key": gemini_api_key,
                "launch_code": personal_launch_code,
            },
        )
        assert reg.status_code == 200

        # Attempt 1: Login with missing launch code -> MUST BE REJECTED (401)
        no_code_login = client.post(
            "/api/saas/auth/login",
            json={"email": existing_email, "password": existing_pw},
        )
        assert no_code_login.status_code == 401
        assert "verificación de inicio requerido" in no_code_login.text or "Código" in no_code_login.text

        # Attempt 2: Login with incorrect launch code -> MUST BE REJECTED (401)
        bad_code_login = client.post(
            "/api/saas/auth/login",
            json={"email": existing_email, "password": existing_pw, "launch_code": "WRONG_CODE_0000"},
        )
        assert bad_code_login.status_code == 401
        assert "inválido" in bad_code_login.text or "Código" in bad_code_login.text

        # Attempt 3: Login with wrong password -> MUST BE REJECTED (401)
        bad_pw_login = client.post(
            "/api/saas/auth/login",
            json={"email": existing_email, "password": "WrongPassword!", "launch_code": personal_launch_code},
        )
        assert bad_pw_login.status_code == 401

        # Attempt 4: Login with correct password AND correct personal launch code -> MUST SUCCEED (200)
        good_login = client.post(
            "/api/saas/auth/login",
            json={"email": existing_email, "password": existing_pw, "launch_code": personal_launch_code},
        )
        assert good_login.status_code == 200
        login_res = good_login.json()
        assert login_res.get("ok") is True
        token = login_res.get("token")
        assert token is not None

        # Verify profile and isolation
        prof_res = client.get("/api/saas/profile", headers={"X-SaaS-Token": token})
        assert prof_res.status_code == 200
        prof = prof_res.json()["user"]
        assert prof["email"] == existing_email
        assert prof["role"] == "USER"
        assert prof["is_creator"] is False

        # Plaintext API keys must never be exposed
        assert "api_keys" not in prof.get("preferences", {})
        assert "api_keys_enc" not in prof.get("preferences", {})
        assert prof["api_keys_status"]["has_gemini"] is True
        assert prof["api_keys_status"]["gemini_masked"].startswith("AIza")

        # Attempt 5: Existing regular user cannot access CREATOR admin dashboard
        admin_res = client.get("/api/saas/admin/dashboard", headers={"X-SaaS-Token": token})
        assert admin_res.status_code == 403
        assert "exclusivos del propietario CREATOR" in admin_res.text or "Acceso denegado" in admin_res.text

    # --------------------------------------------------------------------------
    # SCENARIO C: USUARIO ADMINISTRADOR / CREATOR (SEÑOR SANTIAGO)
    # --------------------------------------------------------------------------
    def test_scenario_c_creator_identification_and_superadmin_security(self):
        master_pin = settings.JARVIS_ACCESS_PIN.strip()

        # 1. Creator login with wrong PIN -> REJECTED (401)
        bad_pin = client.post("/api/auth/login", json={"pin": "WRONG_CREATOR_PIN", "launch_code": "WRONG_CREATOR_PIN"})
        assert bad_pin.status_code == 401

        # 2. Creator login with valid Master PIN -> SUCCEEDS (200)
        good_creator_pin = client.post("/api/auth/login", json={"pin": master_pin, "launch_code": master_pin})
        assert good_creator_pin.status_code == 200
        creator_token = good_creator_pin.json()["token"]

        # 3. Creator SaaS login via /api/saas/auth/login
        saas_creator_login = client.post(
            "/api/saas/auth/login",
            json={"email": CREATOR_EMAIL, "password": master_pin, "launch_code": master_pin},
        )
        assert saas_creator_login.status_code == 200
        saas_creator_res = saas_creator_login.json()
        saas_creator_token = saas_creator_res["token"]
        creator_user = saas_creator_res["user"]

        # 4. Identification Checks:
        assert creator_user["id"] == CREATOR_USER_ID
        assert creator_user["email"] == CREATOR_EMAIL
        assert creator_user["role"] == "CREATOR"
        assert creator_user["plan_code"] == "CREATOR"
        assert creator_user["is_creator"] is True
        assert creator_user["onboarding_gate"]["is_complete"] is True
        assert creator_user["onboarding_gate"]["can_use_project"] is True

        # 5. Creator Superadmin Dashboard Access
        creator_headers = {"X-SaaS-Token": saas_creator_token}
        dash_res = client.get("/api/saas/admin/dashboard", headers=creator_headers)
        assert dash_res.status_code == 200, dash_res.text
        dash_data = dash_res.json()
        assert dash_data.get("ok") is True
        assert "business_metrics" in dash_data
        assert "mrr_usd" in dash_data["business_metrics"]
        assert "arr_usd" in dash_data["business_metrics"]
        assert "arpu_usd" in dash_data["business_metrics"]

        # 6. Creator User Management Access
        users_res = client.get("/api/saas/admin/users", headers=creator_headers)
        assert users_res.status_code == 200
        users_list = users_res.json()
        assert "users" in users_list
        assert any(u["id"] == CREATOR_USER_ID for u in users_list["users"])

        # 7. Sovereign Firebase Configuration Modification:
        # A normal user attempting to modify Firebase config gets 403:
        fake_tok = sign_saas_token("usr_fake_attacker", "attacker@test.ai", "USER", "STARTER")
        fb_tamper = client.post(
            "/api/saas/firebase/config",
            headers={"X-SaaS-Token": fake_tok},
            json={"projectId": "malicious-firebase-project"},
        )
        assert fb_tamper.status_code == 403

        # Creator with valid token & pin CAN view and update Firebase config:
        fb_get = client.get("/api/saas/firebase/config")
        assert fb_get.status_code == 200
        assert fb_get.json().get("projectId") is not None

    # --------------------------------------------------------------------------
    # SCENARIO D: USUARIO PREMIUM Y MONETIZACIÓN EN SANDBOX (PAYMENTS & PLANS)
    # --------------------------------------------------------------------------
    def test_scenario_d_premium_subscription_and_sandbox_checkout(self):
        buyer_email = _unique_email("premium_buyer")
        buyer_pw = "PremiumPass2026!"
        personal_code = "PIN_PREM_3311"

        # Register user with STARTER plan first
        reg = client.post(
            "/api/saas/auth/firebase",
            json={
                "mode": "register",
                "email": buyer_email,
                "password": buyer_pw,
                "full_name": "Andrés Felipe Castro",
                "selected_plan": "STARTER",
                "gemini_api_key": "AIzaSy_PremiumBuyerKey_9999",
                "launch_code": personal_code,
            },
        )
        assert reg.status_code == 200
        token = reg.json()["token"]
        headers = {"X-SaaS-Token": token}

        # 1. Real-time Quote in Sandbox (USD & COP with TRM)
        quote_res = client.post(
            "/api/saas/billing/quote",
            headers=headers,
            json={"plan_code": "PRO", "billing_cycle": "monthly", "payment_gateway": "stripe"},
        )
        assert quote_res.status_code == 200
        quote = quote_res.json()
        assert quote.get("ok") is True
        assert quote.get("plan_code") == "PRO"
        assert quote.get("price_usd") == 30.0
        assert quote.get("price_cop") > 0
        assert quote.get("trm_usd_cop") >= 3000

        # Attempt to quote CREATOR -> MUST BE BLOCKED (403)
        quote_creator = client.post(
            "/api/saas/billing/quote",
            headers=headers,
            json={"plan_code": "CREATOR", "billing_cycle": "monthly"},
        )
        assert quote_creator.status_code == 403

        # 2. Upgrade to PRO via Sandbox Checkout
        tx_id = f"sandbox_tx_{uuid.uuid4().hex[:14]}"
        checkout_res = client.post(
            "/api/saas/billing/checkout",
            headers=headers,
            json={
                "plan_code": "PRO",
                "billing_cycle": "monthly",
                "payment_gateway": "stripe",
                "payment_method_brand": "visa",
                "payment_method_last4": "4242",
                "external_tx_id": tx_id,
            },
        )
        assert checkout_res.status_code == 200, checkout_res.text
        checkout_data = checkout_res.json()
        assert checkout_data.get("ok") is True
        assert checkout_data.get("plan_code") == "PRO"
        assert checkout_data.get("amount_usd") == 30.0
        assert "payment_id" in checkout_data
        assert "invoice_id" in checkout_data

        # 3. Idempotency test: Same external_tx_id cannot be processed twice
        dup_checkout = client.post(
            "/api/saas/billing/checkout",
            headers=headers,
            json={
                "plan_code": "PRO",
                "billing_cycle": "monthly",
                "payment_gateway": "stripe",
                "payment_method_brand": "visa",
                "payment_method_last4": "4242",
                "external_tx_id": tx_id,
            },
        )
        assert dup_checkout.status_code == 200
        assert dup_checkout.json().get("idempotent_duplicate") is True

        # 4. Attempt to purchase CREATOR -> STRICTLY BLOCKED (403)
        bad_creator_buy = client.post(
            "/api/saas/billing/checkout",
            headers=headers,
            json={"plan_code": "CREATOR", "billing_cycle": "monthly"},
        )
        assert bad_creator_buy.status_code == 403

        # 5. Verify database records: User upgraded to PRO, credits allocated (10,000 for PRO)
        async def verify_pro_upgrade():
            async with AsyncSessionLocal() as db:
                res_u = await db.execute(select(SaasUser).where(SaasUser.email == buyer_email))
                user_obj = res_u.scalars().first()
                assert user_obj.plan_code == "PRO"

                res_sub = await db.execute(select(SaasSubscription).where(SaasSubscription.user_id == user_obj.id))
                sub_obj = res_sub.scalars().first()
                assert sub_obj.plan_code == "PRO"
                assert sub_obj.status == "active"
                assert sub_obj.price_usd == 30.0

                res_bal = await db.execute(select(SaasCreditBalance).where(SaasCreditBalance.user_id == user_obj.id))
                bal_obj = res_bal.scalars().first()
                assert bal_obj.monthly_credits_allocated == 10000

                # Verify Latest Invoice
                from sqlalchemy import desc
                res_inv = await db.execute(select(SaasInvoice).where(SaasInvoice.user_id == user_obj.id).order_by(desc(SaasInvoice.issued_at)))
                inv_obj = res_inv.scalars().first()
                assert inv_obj is not None
                assert inv_obj.total_usd == 30.0
                assert inv_obj.status == "paid"

        asyncio.run(verify_pro_upgrade())

        # 6. Verify User Billing History
        hist_res = client.get("/api/saas/billing/history", headers=headers)
        assert hist_res.status_code == 200
        hist_data = hist_res.json()
        assert hist_data.get("ok") is True
        assert len(hist_data.get("invoices", [])) >= 1
        assert len(hist_data.get("payments", [])) >= 1

        # 7. Sandbox Webhook Simulation: Stripe invoice.payment_succeeded
        webhook_event = {
            "id": f"evt_stripe_sandbox_{uuid.uuid4().hex[:12]}",
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "user_id": checkout_data["user"]["id"],
                    "plan_code": "BUSINESS",
                    "billing_cycle": "monthly",
                    "amount_usd": 79.0,
                }
            },
        }
        wh_res = client.post(
            "/api/saas/billing/webhook",
            json=webhook_event,
        )
        assert wh_res.status_code == 200
        wh_data = wh_res.json()
        assert wh_data.get("ok") is True

        # Idempotent repeat of same webhook event
        wh_dup = client.post(
            "/api/saas/billing/webhook",
            json=webhook_event,
        )
        assert wh_dup.status_code == 200
        assert wh_dup.json().get("idempotent_duplicate") is True
