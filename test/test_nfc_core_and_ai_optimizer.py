"""
Comprehensive Test Suite for:
1. NFC CORE ENGINE (Hardware capabilities, NDEF R/W validation, Smart Cards, Dynamic Links,
   P2P File Exchange, AI NFC Triggers, Contactless Payments, Merchant Hub, Anti-Replay Security).
2. AI TOKEN OPTIMIZER & SMART MODEL ROUTER (Context compression, complexity routing,
   response profiles, tool pruning, tenant-isolated cache, token savings).
3. RESOURCE OPTIMIZER (RAM/CPU telemetry, garbage collection cleanup, Low-Power Mode).
4. CREATOR CONTROL CENTERS (NFC Management Center & AI Performance Center).
"""

import time
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.nfc_service import nfc_service
from app.services.token_optimizer_service import token_optimizer_service
from app.services.resource_optimizer_service import resource_optimizer_service

client = TestClient(app)


class TestNFCCoreEngine:
    def test_hardware_and_device_capabilities_detection(self):
        # 1. Android Chrome (Web NFC Native)
        cap_android = nfc_service.detect_device_capabilities(
            user_agent="Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/120.0 Mobile Safari/537.36",
            has_web_nfc=True,
        )
        assert cap_android["ok"] is True
        assert cap_android["web_nfc_supported"] is True
        assert cap_android["capabilities"]["ndef_read"] is True
        assert cap_android["capabilities"]["ndef_write"] is True
        assert cap_android["capability_score_pct"] == 100

        # 2. iOS Safari (Blocked by Apple -> Fallback Matrix)
        cap_ios = nfc_service.detect_device_capabilities(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1",
            has_web_nfc=False,
        )
        assert cap_ios["ok"] is True
        assert cap_ios["web_nfc_supported"] is False
        assert any("dynamic_qr_code" in f["channel"] for f in cap_ios["fallback_matrix"])
        assert any("universal_deep_link" in f["channel"] for f in cap_ios["fallback_matrix"])

        # 3. Desktop Browser
        cap_desktop = nfc_service.detect_device_capabilities(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            has_web_nfc=False,
        )
        assert cap_desktop["client_device"]["is_desktop"] is True
        assert cap_desktop["capabilities"]["simulated_holographic_tap"] is True

        # API endpoint check
        resp = client.get("/api/nfc/capabilities")
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

    def test_ndef_write_validation_and_capacity_limits(self):
        # Small payload fits in NTAG213 (144 bytes)
        small_records = [{"type": "text", "data": "Hola Liseth"}]
        val_small = nfc_service.validate_tag_write(small_records, tag_type="NTAG213")
        assert val_small["valid"] is True
        assert val_small["can_write"] is True

        # Oversized payload exceeds NTAG213
        oversized = [{"type": "text", "data": "A" * 300}]
        val_big = nfc_service.validate_tag_write(oversized, tag_type="NTAG213")
        assert val_big["valid"] is False
        assert "excede la capacidad" in val_big["error"]

        # Locked tag cannot be written
        val_locked = nfc_service.validate_tag_write(small_records, tag_type="NTAG215", is_locked=True)
        assert val_locked["valid"] is False
        assert "protegida contra escritura" in val_locked["error"]

    def test_smart_business_card_vcard_generation(self):
        card = nfc_service.create_vcard_payload(
            name="Santiago Huérfano López",
            role="CEO & Creador Liseth AI",
            organization="Universidad Nacional de Colombia",
            phone="+57 312 237 6474",
            email="santigamerxdyt@gmail.com",
            socials={"linkedin": "santiagohuerfano", "github": "santigamerxdyt"},
            commercial_info={"nequi": "+57 312 237 6474", "bre_b": "@NEQUISAN243100"},
        )
        assert card["type"] == "vcard"
        assert "FN:Santiago Huérfano López" in card["vcard_text"]
        assert "TEL;TYPE=CELL,VOICE:+57 312 237 6474" in card["vcard_text"]
        assert "X-SOCIALPROFILE;TYPE=LINKEDIN:santiagohuerfano" in card["vcard_text"]
        assert "@NEQUISAN243100" in card["vcard_text"]
        assert len(card["ndef_records"]) == 3

        # API endpoint test
        api_card = client.post(
            "/api/nfc/create-vcard",
            json={
                "name": "Santiago",
                "role": "CEO",
                "phone": "+57 312 237 6474",
                "socials": {"github": "santigamerxdyt"},
            },
        ).json()
        assert api_card["ok"] is True
        assert api_card["vcard"]["type"] == "vcard"

    def test_smart_dynamic_links_and_redirection(self):
        link = nfc_service.create_dynamic_link(
            short_code="test-portfolio",
            title="Mi Portafolio",
            destination_url="https://liseth.ai/portfolio/santiago",
            destination_type="profile",
        )
        assert link["short_code"] == "test-portfolio"
        assert link["clicks_count"] == 0

        # Resolve link
        resolved = nfc_service.resolve_dynamic_link("test-portfolio")
        assert resolved is not None
        assert resolved["clicks_count"] == 1
        assert resolved["destination_url"] == "https://liseth.ai/portfolio/santiago"

        # Update destination dynamically without reflashing
        updated = nfc_service.create_dynamic_link(
            short_code="test-portfolio",
            title="Mi Portafolio Actualizado",
            destination_url="https://liseth.ai/portfolio/v2",
        )
        assert updated["destination_url"] == "https://liseth.ai/portfolio/v2"

        # Test API endpoint
        res_api = client.get("/api/nfc/l/test-portfolio")
        assert res_api.status_code == 200
        assert res_api.json()["link"]["destination_url"] == "https://liseth.ai/portfolio/v2"

    def test_p2p_secure_file_exchange_with_ephemeral_token(self):
        intent = nfc_service.create_file_transfer_intent(
            sender_user_id="santiago",
            file_name="Informe_Financiero_2026.pdf",
            file_url="https://liseth.ai/secure-files/pdf-2026.pdf",
            file_size_bytes=1048576,
            file_mime_type="application/pdf",
            requires_owner_consent=True,
            ttl_minutes=15,
        )
        assert intent["status"] == "ready_to_beam"
        token = intent["access_token"]
        assert token.startswith("BEAM-")

        # Consent required first
        dl_unauthorized = nfc_service.redeem_file_transfer(token)
        assert dl_unauthorized["ok"] is False
        assert dl_unauthorized.get("requires_consent") is True

        # Grant consent and download
        intent["consent_granted"] = True
        dl_authorized = nfc_service.redeem_file_transfer(token, recipient_user_id="destinatario_1")
        assert dl_authorized["ok"] is True
        assert dl_authorized["file_name"] == "Informe_Financiero_2026.pdf"
        assert dl_authorized["file_size_bytes"] == 1048576

    def test_ai_nfc_trigger_smart_ai_tag(self):
        trigger = nfc_service.create_ai_trigger_payload(
            agent_id="executive_agent",
            prompt_template="Revisar matriz de riesgos y balance financiero",
            skill_code="business_strategy",
            context_metadata={"project_id": "proj_liseth_2026"},
        )
        assert trigger["agent_id"] == "executive_agent"
        assert trigger["payload"]["protocol"] == "LISETH_AI_NFC_TRIGGER_V1"
        assert len(trigger["ndef_records"]) == 3

        # API endpoint check
        resp = client.post(
            "/api/nfc/ai-trigger",
            json={
                "agent_id": "jarvis_productivity",
                "prompt_template": "Modo Trabajo Profundo",
            },
        ).json()
        assert resp["ok"] is True
        assert resp["ai_trigger"]["agent_id"] == "jarvis_productivity"

    def test_contactless_payments_and_tokenized_pos(self):
        pay = nfc_service.create_payment_payload(
            amount=75000.0,
            currency="COP",
            concept="Renovación Suscripción SaaS",
            recipient="Santiago",
            method="bre_b",
        )
        assert pay["status"] == "pending_tap"
        assert pay["amount"] == 75000.0
        assert "breb://pay" in pay["deep_link"]
        assert len(pay["signature"]) == 16

        # Emulate incoming contactless tap
        tap_res = nfc_service.process_incoming_tap(
            serial_number="04:B2:C3:D4:E5:F6:01",
            records=pay["ndef_records"],
            simulated=False,
        )
        assert tap_res["type"] == "payment"
        assert tap_res["extracted_data"]["payment"]["amount"] == 75000.0

        # Currency conversion check
        conv = nfc_service.convert_currency(100.0, from_curr="USD", to_curr="COP")
        assert conv["converted_amount"] == 415000.0

    def test_cryptographic_anti_replay_challenge_and_verification(self):
        badge = nfc_service.enroll_security_badge(
            badge_uid="04:SEC:TAG:99",
            label="Tag Despacho Santiago",
            secret="SUPER_SECRET_KEY_2026",
        )
        assert badge["is_active"] is True

        # Generate challenge
        chal = nfc_service.generate_tag_challenge(badge["id"])
        assert chal["ok"] is True
        nonce = chal["nonce"]

        # Client computes HMAC-SHA256(secret_hash, nonce)
        import hmac, hashlib
        correct_hmac = hmac.new(badge["secret_hash"].encode("utf-8"), nonce.encode("utf-8"), hashlib.sha256).hexdigest()

        # Valid challenge response
        ver_ok = nfc_service.verify_tag_challenge(badge["id"], correct_hmac)
        assert ver_ok["ok"] is True
        assert ver_ok["authenticated"] is True

        # Replay attack test (nonce consumed, reuse should fail)
        ver_replay = nfc_service.verify_tag_challenge(badge["id"], correct_hmac)
        assert ver_replay["ok"] is False

    def test_merchant_catalog_and_loyalty_checkin(self):
        cat = nfc_service.get_merchant_catalog("store_demo")
        assert "Liseth Tech Store" in cat["business_name"]
        assert len(cat["catalog"]) >= 2

        chk = nfc_service.record_merchant_checkin("store_demo", "user_123")
        assert chk["ok"] is True
        assert chk["points_earned"] == 10

    def test_creator_nfc_dashboard(self):
        dash = nfc_service.get_creator_dashboard()
        assert dash["ok"] is True
        assert dash["metrics"]["total_tags_registered"] >= 1
        assert len(dash["dynamic_links"]) >= 1

        api_dash = client.get("/api/nfc/admin/dashboard").json()
        assert api_dash["ok"] is True
        assert "metrics" in api_dash


class TestAITokenOptimizerAndSmartRouter:
    def test_conversation_history_compression(self):
        # 10 conversational turns with greetings and redundant messages
        history = [
            {"role": "system", "content": "Instrucción central inmutable: Eres Liseth AI."},
            {"role": "user", "content": "Hola buenos días, ¿cómo estás hoy?"},
            {"role": "assistant", "content": "Hola Santiago, estoy excelente y lista para ayudarte."},
            {"role": "user", "content": "Quiero que el presupuesto del proyecto X sea exactamente $50,000 USD."},
            {"role": "assistant", "content": "Entendido, he registrado el presupuesto del proyecto X en $50,000 USD."},
            {"role": "user", "content": "Ok muchas gracias por favor recuérdalo siempre."},
            {"role": "assistant", "content": "Con gusto, guardado en memoria."},
            {"role": "user", "content": "Ahora calcula el margen de utilidad si los costos son $30,000 USD."},
            {"role": "assistant", "content": "El margen de utilidad es $20,000 USD (40%)."},
            {"role": "user", "content": "¿Cuál es la rentabilidad sobre costo?"},
        ]

        compressed, stats = token_optimizer_service.compress_conversation_history(
            history,
            max_tokens_budget=80,
            keep_last_turns=3,
        )
        assert stats["compressed"] is True
        assert stats["tokens_saved"] > 0
        # System instruction must be preserved!
        assert any(m["role"] == "system" and "Instrucción central inmutable" in m["content"] for m in compressed)
        # Summarized context was injected
        assert any("Contexto histórico resumido" in m["content"] for m in compressed)
        # Recent active turns preserved
        assert compressed[-1]["content"] == "¿Cuál es la rentabilidad sobre costo?"

    def test_dynamic_response_profile_detection(self):
        # Brief
        assert token_optimizer_service.detect_response_profile("Hola qué tal") == "brief"
        assert token_optimizer_service.detect_response_profile("ok listo gracias") == "brief"

        # Technical
        assert token_optimizer_service.detect_response_profile("Escribe una funcion def calcular_wacc() en Python") == "technical"
        assert token_optimizer_service.detect_response_profile("Corrige este error de fastapi y sql") == "technical"

        # Structured
        assert token_optimizer_service.detect_response_profile("Genera una tabla comparativa en formato json") == "structured"

        # Explanatory
        assert token_optimizer_service.detect_response_profile("Explica cómo funciona la tasa interna de retorno") == "explanatory"

    def test_smart_model_router_complexity_and_plan_routing(self):
        # Simple query on FREE plan -> fast lite model
        r_simple_free = token_optimizer_service.route_model("Hola, buenos días", user_plan="FREE")
        assert r_simple_free["selected_model"] == "gemini-3.1-flash-lite"
        assert r_simple_free["complexity"] == "simple"

        # Complex technical query on BUSINESS plan -> high reasoning model
        r_complex_biz = token_optimizer_service.route_model(
            "Diseña la arquitectura microservicios con class DockerOrchestrator y auditoria de seguridad WACC",
            user_plan="BUSINESS",
        )
        assert r_complex_biz["complexity"] == "complex"
        assert r_complex_biz["selected_model"] in ("gemini-2.5-pro", "claude-3-5-sonnet")

    def test_tool_and_skill_pruning(self):
        available_skills = [
            "nfc_contactless_tool",
            "business_finance_wacc",
            "academic_research_openalex",
            "data_ml_pandas",
            "security_audit_cve",
            "code_helper_refactor",
            "voice_engine_tts",
        ]

        # Financial prompt should prune non-financial tools
        pruned_fin = token_optimizer_service.prune_skills_for_prompt(
            prompt="Calcula el flujo de caja y la tabla de amortización del préstamo",
            available_skill_codes=available_skills,
            max_tools=2,
        )
        assert "business_finance_wacc" in pruned_fin
        assert len(pruned_fin) <= 2

    def test_tenant_isolated_response_cache(self):
        user_a = "user_santiago"
        user_b = "user_otro"
        prompt = "¿Cuál es el NIT oficial de la empresa?"

        # Set cache for User A
        token_optimizer_service.set_cached_response(
            user_id=user_a,
            prompt=prompt,
            model_id="gemini-3.1-flash-lite",
            profile="brief",
            response_data={"text": "El NIT de Santiago es 1000000000-1"},
            ttl_seconds=300,
        )

        # User A gets cache hit
        hit_a = token_optimizer_service.get_cached_response(
            user_id=user_a,
            prompt=prompt,
            model_id="gemini-3.1-flash-lite",
            profile="brief",
        )
        assert hit_a is not None
        assert "1000000000-1" in hit_a["text"]

        # User B CANNOT see User A's cached response (Strict Multi-Tenant Isolation)
        hit_b = token_optimizer_service.get_cached_response(
            user_id=user_b,
            prompt=prompt,
            model_id="gemini-3.1-flash-lite",
            profile="brief",
        )
        assert hit_b is None

    def test_quality_evaluation_harness(self):
        eval_good = token_optimizer_service.evaluate_quality(
            user_prompt="Escribe una función en Python",
            response_text="```python\ndef saludar():\n    return 'Hola'\n```",
            profile="technical",
        )
        assert eval_good["score"] >= 0.9
        assert eval_good["status"] == "excellent"

        eval_bad = token_optimizer_service.evaluate_quality(
            user_prompt="Escribe código",
            response_text="No sé",
            profile="technical",
        )
        assert eval_bad["score"] < 0.5


class TestResourceOptimizerAndTelemetry:
    def test_system_ram_and_cpu_metrics(self):
        metrics = resource_optimizer_service.get_system_metrics()
        assert "timestamp" in metrics
        assert "uptime_seconds" in metrics
        assert "python_gc_counts" in metrics
        assert metrics.get("process_rss_mb", 0) > 0

    def test_garbage_collection_cleanup(self):
        cleanup = resource_optimizer_service.trigger_memory_cleanup(force=True)
        assert cleanup["ok"] is True
        assert cleanup["cleaned"] is True

    def test_low_power_mode_toggle_and_payload_optimization(self):
        client_id = "test_device_low_ram"

        # Enable low power
        res_on = resource_optimizer_service.register_client_low_power_mode(client_id, True)
        assert res_on["low_power_mode"] is True
        assert resource_optimizer_service.is_client_low_power(client_id) is True

        # Test payload stripping
        heavy_payload = {
            "status": "success",
            "result": 42,
            "full_trace": "lots of debug data...",
            "unpruned_context": "giant raw token dump...",
        }
        optimized = resource_optimizer_service.optimize_payload(heavy_payload, low_power=True)
        assert "result" in optimized
        assert "full_trace" not in optimized
        assert "unpruned_context" not in optimized

        # Disable low power
        res_off = resource_optimizer_service.register_client_low_power_mode(client_id, False)
        assert res_off["low_power_mode"] is False
        assert resource_optimizer_service.is_client_low_power(client_id) is False

    def test_creator_admin_performance_endpoints(self):
        from test.test_saas_platform import _get_creator_headers

        creator_hdr = _get_creator_headers()

        # AI Performance Center endpoint
        ai_perf = client.get("/api/saas/admin/ai-performance", headers=creator_hdr)
        assert ai_perf.status_code == 200
        data = ai_perf.json()
        assert data["ok"] is True
        assert "tokens_saved_total" in data
        assert "cache_hit_ratio_pct" in data

        # Resource Metrics endpoint
        res_met = client.get("/api/saas/admin/resource-metrics?force_gc=true", headers=creator_hdr)
        assert res_met.status_code == 200
        mdata = res_met.json()
        assert mdata["ok"] is True
        assert "metrics" in mdata
