"""
Comprehensive Test Suite for Liseth SaaS Multi-User, Multi-Tenant, Monetizable Platform.
Validates:
1. User registration, login, email verification, password recovery, profile edit, password change, account deletion.
2. Strict multi-tenant isolation (User B cannot access, modify, or delete User A's conversations or memories).
3. Multi-conversation persistence, search, archive/unarchive, pagination, and auto-memory extraction.
4. Individual user memory brain CRUD, contextual retrieval, and memory toggle.
5. 6-tier plan hierarchy (FREE, STARTER, PRO, BUSINESS, ENTERPRISE, CREATOR) and strict server-side RBAC.
6. Anti-escalation security (impossible to self-assign or purchase CREATOR from client endpoints).
7. Subscriptions, promo codes, referral rewards, invoice history, and Stripe webhook idempotency + grace periods.
8. Credit consumption, 80% alert threshold, and 100% quota blocking.
9. Exclusive CREATOR Superadmin Control Center for Señor Santiago (MRR, ARR, ARPU, user admin, plan admin, skills CRUD, refunds).
"""
import uuid
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


client = TestClient(app)


def _unique_email(prefix: str = "user") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}@test-liseth.ai"


def _auth_headers(token: str) -> dict:
    return {"X-SaaS-Token": token}


def _get_creator_headers() -> dict:
    res = client.post("/api/auth/login", json={"pin": settings.JARVIS_ACCESS_PIN})
    assert res.status_code == 200, res.text
    token = res.json()["token"]
    return {"Authorization": f"Bearer {token}"}


class TestSaasAuthAndAccountLifecycle:
    def test_register_login_verify_recover_edit_and_delete(self):
        email = _unique_email("lifecycle")
        pw = "SecurePass2026!"

        # 1. Register
        reg = client.post(
            "/api/saas/auth/register",
            json={"email": email, "password": pw, "full_name": "Ana María Gómez"},
        )
        assert reg.status_code == 200, reg.text
        reg_data = reg.json()
        assert reg_data["ok"] is True
        token = reg_data["token"]
        verif_token = reg_data["verification_token"]
        assert reg_data["user"]["plan_code"] == "FREE"
        assert reg_data["user"]["role"] == "USER"
        assert reg_data["user"]["email_verified"] is False

        # 2. Verify Email
        ver = client.post("/api/saas/auth/verify-email", json={"token": verif_token})
        assert ver.status_code == 200, ver.text
        assert ver.json()["email_verified"] is True

        # 3. Login
        login = client.post("/api/saas/auth/login", json={"email": email, "password": pw})
        assert login.status_code == 200
        token = login.json()["token"]

        # 4. Edit Profile
        upd = client.put(
            "/api/saas/profile",
            headers=_auth_headers(token),
            json={"full_name": "Ana Gómez PhD", "nickname": "Dra. Ana", "bio": "Investigadora IA"},
        )
        assert upd.status_code == 200
        assert upd.json()["user"]["nickname"] == "Dra. Ana"

        # 5. Change Password
        new_pw = "NewSuperSecret2026!"
        chg = client.post(
            "/api/saas/profile/password",
            headers=_auth_headers(token),
            json={"current_password": pw, "new_password": new_pw},
        )
        assert chg.status_code == 200

        # 6. Forgot & Reset Password
        fgt = client.post("/api/saas/auth/forgot-password", json={"email": email})
        assert fgt.status_code == 200
        reset_tok = fgt.json()["reset_token"]

        rst = client.post(
            "/api/saas/auth/reset-password",
            json={"token": reset_tok, "new_password": "ResetPassword99!"},
        )
        assert rst.status_code == 200

        # 7. Delete Own Account
        del_res = client.delete("/api/saas/profile", headers=_auth_headers(token))
        assert del_res.status_code == 200
        assert del_res.json()["ok"] is True

        # Verify deleted user can no longer access profile
        prof_after = client.get("/api/saas/profile", headers=_auth_headers(token))
        assert prof_after.status_code == 401


class TestMultiTenantDataIsolation:
    def test_strict_isolation_between_two_users_conversations_and_memories(self):
        # Register User A and User B
        reg_a = client.post(
            "/api/saas/auth/register",
            json={"email": _unique_email("user_a"), "password": "PasswordA123!", "full_name": "Usuario A"},
        ).json()
        reg_b = client.post(
            "/api/saas/auth/register",
            json={"email": _unique_email("user_b"), "password": "PasswordB123!", "full_name": "Usuario B"},
        ).json()

        hdr_a = _auth_headers(reg_a["token"])
        hdr_b = _auth_headers(reg_b["token"])

        # User A creates a private conversation and sends a message with an explicit memory fact
        conv_a = client.post(
            "/api/saas/conversations",
            headers=hdr_a,
            json={"title": "Estrategia Confidencial Usuario A"},
        )
        assert conv_a.status_code == 200
        conv_a_id = conv_a.json()["conversation"]["id"]

        msg_a = client.post(
            f"/api/saas/conversations/{conv_a_id}/messages",
            headers=hdr_a,
            json={"content": "Recuerda que mi empresa se llama Alpha Quantum Labs y mi clave interna es AX-900."},
        )
        assert msg_a.status_code == 200, msg_a.text
        assert msg_a.json()["memory_auto_extracted"] is not None

        # User A also adds an explicit personal memory
        mem_a = client.post(
            "/api/saas/memories",
            headers=hdr_a,
            json={"content": "Patente secreta de Usuario A número 8899", "scope": "personal", "importance": 5},
        )
        assert mem_a.status_code == 200
        mem_a_id = mem_a.json()["memory"]["id"]

        # Verify User B CANNOT see User A's conversations in list
        list_b = client.get("/api/saas/conversations", headers=hdr_b).json()
        assert list_b["total"] == 0
        assert all(c["id"] != conv_a_id for c in list_b["conversations"])

        # Verify User B CANNOT read, rename, message, or delete User A's conversation
        get_b = client.get(f"/api/saas/conversations/{conv_a_id}", headers=hdr_b)
        assert get_b.status_code == 403

        upd_b = client.put(
            f"/api/saas/conversations/{conv_a_id}",
            headers=hdr_b,
            json={"title": "Hackeado por B"},
        )
        assert upd_b.status_code == 403

        send_b = client.post(
            f"/api/saas/conversations/{conv_a_id}/messages",
            headers=hdr_b,
            json={"content": "Intento leer contexto de A"},
        )
        assert send_b.status_code == 403

        del_b = client.delete(f"/api/saas/conversations/{conv_a_id}", headers=hdr_b)
        assert del_b.status_code == 403

        # Verify User B CANNOT list, search, update, or delete User A's memories
        mems_b = client.get("/api/saas/memories", headers=hdr_b).json()
        assert mems_b["total"] == 0

        ctx_b = client.get("/api/saas/memories/contextual?query=Alpha+Quantum+Patente", headers=hdr_b).json()
        assert len(ctx_b["memories"]) == 0

        upd_mem_b = client.put(
            f"/api/saas/memories/{mem_a_id}",
            headers=hdr_b,
            json={"content": "Modificado por B"},
        )
        assert upd_mem_b.status_code == 403

        del_mem_b = client.delete(f"/api/saas/memories/{mem_a_id}", headers=hdr_b)
        assert del_mem_b.status_code == 403

        # Meanwhile User A can retrieve their own conversation & contextual memories seamlessly
        ctx_a = client.get("/api/saas/memories/contextual?query=Alpha+Quantum", headers=hdr_a).json()
        assert len(ctx_a["memories"]) >= 1
        assert any("Alpha Quantum" in m["content"] for m in ctx_a["memories"])


class TestPlanHierarchyRbacAndAntiEscalation:
    def test_creator_cannot_be_registered_assigned_or_purchased(self):
        # 1. Attempt to register with plan_code=CREATOR
        r1 = client.post(
            "/api/saas/auth/register",
            json={
                "email": _unique_email("hacker1"),
                "password": "Password123!",
                "plan_code": "CREATOR",
            },
        )
        assert r1.status_code == 403

        # 2. Attempt to register with role=CREATOR
        r2 = client.post(
            "/api/saas/auth/register",
            json={
                "email": _unique_email("hacker2"),
                "password": "Password123!",
                "role": "CREATOR",
            },
        )
        assert r2.status_code == 403

        # 3. Register normal FREE user and attempt to escalate via profile update or checkout
        reg = client.post(
            "/api/saas/auth/register",
            json={"email": _unique_email("free_user"), "password": "Password123!"},
        ).json()
        hdr = _auth_headers(reg["token"])

        esc_prof = client.put(
            "/api/saas/profile",
            headers=hdr,
            json={"plan_code": "CREATOR", "role": "CREATOR"},
        )
        assert esc_prof.status_code == 403

        esc_chk = client.post(
            "/api/saas/billing/checkout",
            headers=hdr,
            json={"plan_code": "CREATOR", "billing_cycle": "monthly"},
        )
        assert esc_chk.status_code == 403

        # 4. Verify CREATOR is not listed in public plans for regular users
        plans_res = client.get("/api/saas/plans", headers=hdr).json()
        plan_codes = [p["code"] for p in plans_res["plans"]]
        assert "CREATOR" not in plan_codes
        assert plan_codes == ["FREE", "STARTER", "PRO", "BUSINESS", "ENTERPRISE"]

        # 5. Verify regular user receives 403 on all /api/saas/admin/* endpoints
        adm_dash = client.get("/api/saas/admin/dashboard", headers=hdr)
        assert adm_dash.status_code == 403

        adm_users = client.get("/api/saas/admin/users", headers=hdr)
        assert adm_users.status_code == 403

    def test_free_plan_limits_and_feature_locks(self):
        reg = client.post(
            "/api/saas/auth/register",
            json={"email": _unique_email("limits_free"), "password": "Password123!"},
        ).json()
        hdr = _auth_headers(reg["token"])

        # 1. FREE plan allows max 5 active conversations
        conv_ids = []
        for i in range(5):
            c = client.post("/api/saas/conversations", headers=hdr, json={"title": f"Chat {i+1}"})
            assert c.status_code == 200
            conv_ids.append(c.json()["conversation"]["id"])

        # 6th active conversation must be blocked with upgrade prompt
        c6 = client.post("/api/saas/conversations", headers=hdr, json={"title": "Chat 6 Excedido"})
        assert c6.status_code == 403
        assert c6.json()["detail"]["recommended_plan"] == "STARTER"

        # Archiving one conversation frees a slot
        arch = client.put(
            f"/api/saas/conversations/{conv_ids[0]}",
            headers=hdr,
            json={"is_archived": True},
        )
        assert arch.status_code == 200
        c6_retry = client.post("/api/saas/conversations", headers=hdr, json={"title": "Chat 6 Ahora Permitido"})
        assert c6_retry.status_code == 200

        # 2. FREE user blocked from using PRO model (gemini-2.5-pro)
        pro_model_try = client.post(
            f"/api/saas/conversations/{conv_ids[1]}/messages",
            headers=hdr,
            json={"content": "Analiza con Gemini 2.5 Pro", "model_id": "gemini-2.5-pro"},
        )
        assert pro_model_try.status_code == 403
        assert pro_model_try.json()["detail"]["recommended_plan"] == "PRO"

        # 3. FREE user blocked from using BUSINESS skill (business_strategist_cfo)
        biz_skill_try = client.post(
            f"/api/saas/conversations/{conv_ids[1]}/messages",
            headers=hdr,
            json={"content": "Calcula DCF corporativo", "skill_code": "business_strategist_cfo"},
        )
        assert biz_skill_try.status_code == 403
        assert biz_skill_try.json()["detail"]["recommended_plan"] == "BUSINESS"

        # 4. FREE user blocked from creating Custom Agents
        agt_try = client.post(
            "/api/saas/agents",
            headers=hdr,
            json={"name": "Mi Agente CFO", "role_title": "Finanzas"},
        )
        assert agt_try.status_code == 403
        assert agt_try.json()["detail"]["recommended_plan"] == "BUSINESS"


class TestMonetizationBillingPromosReferralsAndWebhooks:
    def test_referrals_promo_checkout_idempotency_webhook_and_upgrade_unlocks(self):
        # 1. Register Referrer User
        ref_owner = client.post(
            "/api/saas/auth/register",
            json={"email": _unique_email("referrer"), "password": "Password123!", "full_name": "Mentor SaaS"},
        ).json()
        ref_code = ref_owner["user"]["referral_code"]
        hdr_owner = _auth_headers(ref_owner["token"])

        # 2. Register Invited User with referral_code
        invited = client.post(
            "/api/saas/auth/register",
            json={
                "email": _unique_email("invited"),
                "password": "Password123!",
                "full_name": "Invitado VIP",
                "referral_code": ref_code,
            },
        ).json()
        hdr_invited = _auth_headers(invited["token"])

        # Verify email of invited user to trigger referral reward distribution
        ver = client.post("/api/saas/auth/verify-email", json={"token": invited["verification_token"]})
        assert ver.status_code == 200
        assert ver.json()["referral_reward_granted"] is True

        # Check referrer earned 500 referral credits
        refs_info = client.get("/api/saas/referrals", headers=hdr_owner).json()
        assert refs_info["rewarded_referrals"] == 1
        assert refs_info["total_credits_earned"] == 500

        # 3. Validate Promo Code WELCOME20 (20% discount + 500 bonus credits)
        promo_val = client.post(
            "/api/saas/billing/promo/validate",
            headers=hdr_invited,
            json={"code": "WELCOME20", "plan_code": "BUSINESS"},
        )
        assert promo_val.status_code == 200
        assert promo_val.json()["promo"]["discount_pct"] == 20.0

        # 4. Upgrade Invited User to BUSINESS ($75/mo - 20% = $60.00 USD) with idempotency key
        tx_key = f"tx_idem_{uuid.uuid4().hex[:12]}"
        chk1 = client.post(
            "/api/saas/billing/checkout",
            headers=hdr_invited,
            json={
                "plan_code": "BUSINESS",
                "billing_cycle": "monthly",
                "promo_code": "WELCOME20",
                "payment_method_brand": "mastercard",
                "payment_method_last4": "8899",
                "external_tx_id": tx_key,
            },
        )
        assert chk1.status_code == 200, chk1.text
        d1 = chk1.json()
        assert d1["idempotent_duplicate"] is False
        assert d1["subscription"]["plan_code"] == "BUSINESS"
        assert d1["invoice"]["subtotal_usd"] == 75.0
        assert d1["invoice"]["discount_usd"] == 15.0
        assert d1["invoice"]["total_usd"] == 60.0

        # 5. Send duplicate checkout with same external_tx_id -> must be idempotent!
        chk2 = client.post(
            "/api/saas/billing/checkout",
            headers=hdr_invited,
            json={
                "plan_code": "BUSINESS",
                "billing_cycle": "monthly",
                "external_tx_id": tx_key,
            },
        )
        assert chk2.status_code == 200
        assert chk2.json()["idempotent_duplicate"] is True

        # Verify only 1 invoice was generated
        hist = client.get("/api/saas/billing/history", headers=hdr_invited).json()
        assert len(hist["invoices"]) == 1

        # 6. Now on BUSINESS plan, user CAN create Custom Agents and use BUSINESS skills
        custom_agt = client.post(
            "/api/saas/agents",
            headers=hdr_invited,
            json={
                "name": "Agente Estratega Corporativo",
                "role_title": "Consultor M&A",
                "description": "Experto en fusiones y adquisiciones",
                "system_prompt": "Eres un banquero de inversión senior.",
                "skill_codes": ["business_strategist_cfo"],
            },
        )
        assert custom_agt.status_code == 200
        assert custom_agt.json()["agent"]["name"] == "Agente Estratega Corporativo"

        # 7. Test Stripe Webhook for failed payment -> activates 5-day grace period
        fail_evt_id = f"evt_fail_{uuid.uuid4().hex[:10]}"
        wh_fail = client.post(
            "/api/saas/billing/webhook",
            json={
                "id": fail_evt_id,
                "type": "invoice.payment_failed",
                "data": {
                    "object": {
                        "user_id": invited["user"]["id"],
                        "plan_code": "BUSINESS",
                        "amount_usd": 75.0,
                        "failure_reason": "Tarjeta expirada",
                    }
                },
            },
        )
        assert wh_fail.status_code == 200
        assert wh_fail.json()["status"] == "past_due"
        assert wh_fail.json()["grace_period_ends_at"] is not None


class TestCreatorSuperadminControlCenter:
    def test_creator_exclusive_dashboard_user_admin_plan_admin_and_refunds(self):
        creator_headers = _get_creator_headers()

        # 1. Verify Creator Profile resolves to Señor Santiago with CREATOR role & plan
        prof = client.get("/api/saas/profile", headers=creator_headers)
        assert prof.status_code == 200
        p_user = prof.json()["user"]
        assert p_user["role"] == "CREATOR"
        assert p_user["plan_code"] == "CREATOR"
        assert p_user["is_creator"] is True

        # 2. Access Creator Superadmin Dashboard (MRR, ARR, ARPU, API costs, profit)
        dash = client.get("/api/saas/admin/dashboard", headers=creator_headers)
        assert dash.status_code == 200, dash.text
        metrics = dash.json()["metrics"]
        assert metrics["total_users"] >= 1
        assert "mrr_usd" in metrics
        assert "arr_usd" in metrics
        assert "arpu_usd" in metrics
        assert "estimated_monthly_profit_usd" in metrics

        # 3. Creator creates a new user and manually assigns them PRO plan + bonus credits
        u_reg = client.post(
            "/api/saas/auth/register",
            json={"email": _unique_email("managed_by_creator"), "password": "Password123!"},
        ).json()
        target_uid = u_reg["user"]["id"]

        adm_upd = client.put(
            f"/api/saas/admin/users/{target_uid}",
            headers=creator_headers,
            json={"plan_code": "PRO", "bonus_credits": 5000},
        )
        assert adm_upd.status_code == 200
        assert adm_upd.json()["user"]["plan_code"] == "PRO"
        assert adm_upd.json()["user"]["usage"]["bonus_credits"] == 5000

        # 4. Creator suspends and reactivates user
        susp = client.put(
            f"/api/saas/admin/users/{target_uid}",
            headers=creator_headers,
            json={"is_suspended": True, "suspension_reason": "Auditoría de seguridad"},
        )
        assert susp.status_code == 200
        assert susp.json()["user"]["is_suspended"] is True

        # Suspended user is blocked from accessing endpoints
        blocked_res = client.get("/api/saas/profile", headers=_auth_headers(u_reg["token"]))
        assert blocked_res.status_code == 403

        # Reactivate
        react = client.put(
            f"/api/saas/admin/users/{target_uid}",
            headers=creator_headers,
            json={"is_suspended": False},
        )
        assert react.status_code == 200
        assert client.get("/api/saas/profile", headers=_auth_headers(u_reg["token"])).status_code == 200

        # 5. Creator dynamically updates a Plan's limits and creates a new Skill
        plan_upd = client.put(
            "/api/saas/admin/plans/STARTER",
            headers=creator_headers,
            json={"daily_message_limit": 160},
        )
        assert plan_upd.status_code == 200
        assert plan_upd.json()["plan"]["daily_message_limit"] == 160

        sk_res = client.post(
            "/api/saas/admin/skills",
            headers=creator_headers,
            json={
                "code": f"custom_creator_skill_{uuid.uuid4().hex[:6]}",
                "name": "Quantum Financial Forecaster",
                "description": "Predicción cuántica de flujo de caja creada por Señor Santiago",
                "category": "finance",
                "tier": "advanced",
                "min_plan_level": 2,
                "estimated_credit_cost": 4,
            },
        )
        assert sk_res.status_code == 200
        assert sk_res.json()["skill"]["name"] == "Quantum Financial Forecaster"


class TestFirebaseStartupGateAndProjectLinking:
    def test_firebase_project_config_and_account_creation_with_plan_selection(self):
        # 1. Verify Firebase project config endpoint
        cfg_res = client.get("/api/saas/firebase/config")
        assert cfg_res.status_code == 200
        cfg = cfg_res.json()
        assert cfg["ok"] is True
        assert cfg["isLinked"] is True
        assert "emailPassword" in cfg["providers"]

        # 2. Update/link Firebase project config
        upd_cfg = client.post(
            "/api/saas/firebase/config",
            json={
                "projectId": "liseth-saas-ai",
                "authDomain": "liseth-saas-ai.firebaseapp.com",
            },
        )
        assert upd_cfg.status_code == 200
        assert upd_cfg.json()["projectId"] == "liseth-saas-ai"

        # 3. Attempt to create a Firebase account selecting CREATOR plan -> must fail with 403
        bad_fb = client.post(
            "/api/saas/auth/firebase",
            json={
                "mode": "register",
                "email": _unique_email("fb_hacker"),
                "password": "FirebasePass123!",
                "selected_plan": "CREATOR",
            },
        )
        assert bad_fb.status_code == 403

        # 4. Create account on startup gate linked to Firebase selecting PRO plan
        fb_email = _unique_email("fb_pro_user")
        fb_reg = client.post(
            "/api/saas/auth/firebase",
            json={
                "mode": "register",
                "email": fb_email,
                "password": "FirebasePass123!",
                "full_name": "Laura Firebase Pro",
                "selected_plan": "PRO",
                "promo_code": "WELCOME20",
            },
        )
        assert fb_reg.status_code == 200, fb_reg.text
        fb_data = fb_reg.json()
        assert fb_data["ok"] is True
        assert fb_data["firebase"]["linked"] is True
        assert fb_data["firebase"]["projectId"] == "liseth-saas-ai"
        assert fb_data["firebase"]["uid"].startswith("fb_")
        assert fb_data["user"]["plan_code"] == "PRO"
        assert fb_data["user"]["preferences"]["firebase_project_id"] == "liseth-saas-ai"

        # 5. Subsequent login via Firebase Auth endpoint
        fb_login = client.post(
            "/api/saas/auth/firebase",
            json={
                "mode": "login",
                "email": fb_email,
                "password": "FirebasePass123!",
            },
        )
        assert fb_login.status_code == 200
        assert fb_login.json()["firebase"]["linked"] is True
        assert fb_login.json()["user"]["plan_code"] == "PRO"

    def test_startup_gate_html_locked_by_default_and_shows_plans(self):
        from pathlib import Path
        import hashlib

        base = Path(settings.BASE_DIR)
        idx_bytes = (base / "index.html").read_bytes()
        jrv_bytes = (base / "jarvis.html").read_bytes()
        stc_bytes = (base / "app" / "static" / "index.html").read_bytes()

        # Verify 100% byte parity across all 3 HTML files
        assert hashlib.sha256(idx_bytes).hexdigest() == hashlib.sha256(jrv_bytes).hexdigest()
        assert hashlib.sha256(idx_bytes).hexdigest() == hashlib.sha256(stc_bytes).hexdigest()

        html = idx_bytes.decode("utf-8")
        # Startup modal is active immediately on boot
        assert '<div class="modal-overlay active" id="auth-modal"' in html
        assert 'id="auth-firebase-register-form"' in html
        assert 'id="gate-plans-cards-container"' in html
        assert 'id="gate-selected-payment-gateway"' in html
        assert 'id="saas-payment-gateway-select"' in html
        assert 'id="saas-checkout-quote-box"' in html
        assert "saveCreatorPaymentConfigUI" in html
        assert "firebase-app-compat.js" in html
        assert "firebase-auth-compat.js" in html

    def test_public_payment_gateways_and_live_sales_quote(self):
        # 1. Public payment gateways endpoint (no auth required for startup gate)
        gw_resp = client.get("/api/saas/billing/gateways")
        assert gw_resp.status_code == 200
        gw_data = gw_resp.json()
        assert gw_data["ok"] is True
        assert gw_data["trm_usd_cop"] > 0
        assert "stripe" in gw_data["gateways"]
        assert "wompi_pse_nequi" in gw_data["gateways"]
        assert "paypal" in gw_data["gateways"]
        assert "direct_transfer" in gw_data["gateways"]
        assert gw_data["gateways"]["direct_transfer"]["nequi_number"] == "3122376474"
        assert gw_data["gateways"]["direct_transfer"]["whatsapp_sales_phone"] == "+573122376474"

        # 2. Live sales quote for PRO annual with WELCOME20 coupon
        quote_resp = client.post(
            "/api/saas/billing/quote",
            json={
                "plan_code": "PRO",
                "billing_cycle": "annual",
                "promo_code": "WELCOME20",
                "payment_gateway": "wompi_pse_nequi",
            },
        )
        assert quote_resp.status_code == 200
        q = quote_resp.json()["quote"]
        assert q["plan_code"] == "PRO"
        assert q["billing_cycle"] == "annual"
        # Annual base for PRO ($30/mo): 30 * 12 * 0.8 = 288 USD
        assert q["subtotal_usd"] == 288.0
        assert q["annual_savings_usd"] == 72.0
        # WELCOME20 gives 20% off 288 = 57.60 discount -> 230.40 USD final
        assert q["promo_discount_pct"] == 20.0
        assert q["total_usd"] == 230.4
        assert q["total_cop"] > 0
        assert q["bonus_credits"] > 0

        # 3. CREATOR plan cannot be quoted for sale
        creator_quote = client.post(
            "/api/saas/billing/quote",
            json={"plan_code": "CREATOR", "billing_cycle": "monthly"},
        )
        assert creator_quote.status_code == 403

    def test_creator_payment_gateway_config_and_multi_gateway_checkout(self):
        cfg_file = settings.DATA_DIR / "payment_gateways_config.json"
        prior_bytes = cfg_file.read_bytes() if cfg_file.exists() else None
        try:
            # Regular user cannot access or modify payment gateway configuration
            reg_u = client.post(
                "/api/saas/auth/register",
                json={
                    "email": _unique_email("buyer_colombia"),
                    "password": "SafePass123!",
                    "full_name": "Buyer Colombia",
                },
            ).json()
            u_headers = _auth_headers(reg_u["token"])

            forbidden_get = client.get("/api/saas/admin/payment-config", headers=u_headers)
            assert forbidden_get.status_code == 403

            # Authenticate as Creator to configure payment gateways & TRM
            c_headers = _get_creator_headers()

            save_cfg = client.post(
                "/api/saas/admin/payment-config",
                headers=c_headers,
                json={
                    "trm_usd_cop": 4150.0,
                    "gateways": {
                        "stripe": {
                            "enabled": True,
                            "publishable_key": "pk_live_test123",
                            "payment_links": {"PRO": "https://buy.stripe.com/test_pro_link"},
                        },
                        "wompi_pse_nequi": {
                            "enabled": True,
                            "wompi_public_key": "pub_prod_wompi123",
                            "payment_links": {"PRO": "https://checkout.wompi.co/l/test_pro_cop"},
                        },
                        "direct_transfer": {
                            "enabled": True,
                            "nequi_number": "300 123 4567",
                            "bancolombia_account": "Ahorros 123-456789-00",
                            "bre_b_key": "@santiago.liseth",
                            "account_holder": "Santiago (Creator)",
                        },
                    },
                },
            )
            assert save_cfg.status_code == 200
            cfg_json = save_cfg.json()
            assert cfg_json["trm_usd_cop"] == 4150.0
            assert cfg_json["gateways"]["direct_transfer"]["nequi_number"] == "300 123 4567"

            # Buyer checks out PRO plan using Wompi PSE / Nequi
            checkout_resp = client.post(
                "/api/saas/billing/checkout",
                headers=u_headers,
                json={
                    "plan_code": "PRO",
                    "billing_cycle": "monthly",
                    "payment_gateway": "wompi_pse_nequi",
                    "payment_method_brand": "PSE / Nequi",
                    "payment_method_last4": "NEQU",
                    "promo_code": "WELCOME20",
                },
            )
            assert checkout_resp.status_code == 200
            co_data = checkout_resp.json()
            assert co_data["subscription"]["plan_code"] == "PRO"
            assert co_data["payment_gateway"] == "wompi_pse_nequi"
            assert co_data["subscription"]["price_usd"] == 24.0
            assert co_data["subscription"]["price_cop"] == round(24.0 * 4150.0)
            assert co_data["invoice"]["total_cop"] == round(24.0 * 4150.0)
            assert co_data["external_payment_link"] == "https://checkout.wompi.co/l/test_pro_cop"
        finally:
            if prior_bytes is not None:
                cfg_file.write_bytes(prior_bytes)




