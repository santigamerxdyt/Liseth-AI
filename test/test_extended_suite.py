"""
Unit tests for Liseth Extended Executive Suite:
- Personal Finance & Smart Budgeting
- Stark Vault Cryptographic Generator & Shannon Entropy
- Colombian Commercial Contracts & Legal Minutas (Services, NDA, Pagaré)
- Stark Mission Control (Deep Focus & Memory Compaction)
"""

import pytest
from app.services.personal_finance_service import personal_finance_service
from app.services.stark_vault_service import stark_vault_service
from app.services.legal_contracts_service import legal_contracts_service
from app.services.focus_engine_service import focus_engine_service
from app.actions.personal_finance_action import personal_finance_action
from app.actions.stark_vault_action import stark_vault_action
from app.actions.legal_contracts_action import legal_contracts_action


def test_personal_finance_operations():
    # Test adding expense
    e = personal_finance_service.add_entry(
        amount=35000.0,
        category="Alimentacion",
        entry_type="expense",
        description="Cena de trabajo"
    )
    assert e["amount"] == 35000.0
    assert e["category"] == "Alimentacion"

    # Test adding income
    inc = personal_finance_service.add_entry(
        amount=500000.0,
        category="Consultoria & Negocios",
        entry_type="income",
        description="Anticipo asesoría"
    )
    assert inc["type"] == "income"
    assert inc["amount"] == 500000.0

    # Test summary and savings calculation
    sm = personal_finance_service.get_summary()
    assert sm["total_income"] >= 500000.0
    assert sm["total_expense"] >= 35000.0
    assert "Alimentacion" in sm["category_expenses"]

    # Test Markdown formatting
    md = personal_finance_service.format_summary_markdown(sm)
    assert "Balance Financiero" in md
    assert "Ingresos Totales" in md


def test_stark_vault_passwords_and_entropy():
    # Test complex password
    res_complex = stark_vault_service.generate_password(length=20, mode="complex")
    assert len(res_complex["password"]) == 20
    assert res_complex["entropy_bits"] > 80.0
    assert res_complex["score"] >= 80

    # Test Diceware passphrase
    res_pass = stark_vault_service.generate_password(length=16, mode="passphrase")
    assert "-" in res_pass["password"]
    assert res_pass["mode"] == "passphrase"

    # Test PIN
    res_pin = stark_vault_service.generate_password(length=6, mode="pin")
    assert len(res_pin["password"]) == 6
    assert res_pin["password"].isdigit()

    # Test entropy evaluation of a weak password
    weak_audit = stark_vault_service.evaluate_password_strength("123456")
    assert weak_audit["score"] < 40

    # Test entropy of strong password
    strong_audit = stark_vault_service.evaluate_password_strength("K9#mQ$8xL!2vR@7pZ")
    assert strong_audit["score"] > 80
    assert "siglos" in strong_audit["crack_time"] or "años" in strong_audit["crack_time"]


def test_legal_contracts_generation():
    # Test Colombian Professional Services Contract
    cto = legal_contracts_service.generate_contract(
        template_type="servicios_profesionales",
        party_b_name="Distribuidora del Pacífico S.A.",
        party_b_id="900.555.444-3",
        amount=3800000.0,
        scope="Diagnóstico Financiero y Modelo de Costos ABC",
        duration_days=45,
        city="Palmira"
    )
    assert cto["id"].startswith("CTO-")
    assert "CONTRATO DE PRESTACIÓN DE SERVICIOS" in cto["title"]
    assert "Distribuidora del Pacífico S.A." in cto["content_markdown"]
    assert "$3,800,000.00 COP" in cto["content_markdown"]
    assert "Bre-B" in cto["content_markdown"]
    assert "Cámara de Comercio" in cto["content_markdown"]

    # Test NDA
    nda = legal_contracts_service.generate_contract(
        template_type="nda",
        party_b_name="Inversiones Valle Verde",
        scope="Prototipo de Inteligencia Artificial Liseth"
    )
    assert "ACUERDO DE CONFIDENCIALIDAD" in nda["title"]
    assert "Inversiones Valle Verde" in nda["content_markdown"]

    # Test Pagaré
    pagare = legal_contracts_service.generate_contract(
        template_type="pagare",
        party_b_name="Comercializadora Andina",
        amount=1200000.0
    )
    assert "PAGARÉ A LA ORDEN" in pagare["title"]
    assert "$1,200,000.00 COP" in pagare["content_markdown"]


def test_focus_engine_and_memory_purge():
    # Test focus session start & stop
    sess = focus_engine_service.start_focus_session(duration_minutes=30, objective="Estudio de Finanzas")
    assert sess["duration_minutes"] == 30
    assert sess["status"] == "in_progress"

    status = focus_engine_service.get_focus_status()
    assert status["active"] is True
    assert status["remaining_seconds"] > 0

    stop_res = focus_engine_service.stop_focus_session()
    assert stop_res["status"] == "completed"

    # Test memory purge
    purge = focus_engine_service.purge_system_memory()
    assert purge["status"] == "optimized"


def test_action_dispatcher_integration():
    # Finance action
    res_f = personal_finance_action({"action": "summary"})
    assert "Balance Financiero" in res_f

    # Vault action
    res_v = stark_vault_action({"action": "generate", "length": 16})
    assert "Credencial Criptográfica Stark Generada" in res_v

    # Contracts action
    res_c = legal_contracts_action({"action": "draft", "template": "nda", "client": "TechCorp Cali"})
    assert "ACUERDO DE CONFIDENCIALIDAD" in res_c
