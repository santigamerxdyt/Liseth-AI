# -*- coding: utf-8 -*-
"""
Unit tests for ESG Governance and Corporate Treasury / Working Capital Services.
"""

import pytest
from app.services.esg_governance_service import esg_governance_service
from app.services.treasury_working_capital_service import treasury_working_capital_service
from app.services.action_dispatcher import SYSTEM_TOOL_DECLARATIONS
from app.actions.esg_governance_action import esg_governance_action
from app.actions.treasury_working_capital_action import treasury_working_capital_action


def test_esg_governance_evaluation():
    # 1. High ESG Rating
    res = esg_governance_service.evaluate_esg(
        company_name="Stark Corp Palmira",
        environmental_score=85.0,
        social_score=88.0,
        governance_score=90.0,
        sector="Agrotech & Logística",
        headcount=120
    )
    assert res["composite_esg_score"] >= 85.0
    assert "AAA" in res["esg_rating"]
    assert res["status"] == "optimal"

    # 2. Critical ESG Rating
    critical = esg_governance_service.evaluate_esg(
        company_name="Empresa Rezago",
        environmental_score=20.0,
        social_score=30.0,
        governance_score=35.0
    )
    assert critical["composite_esg_score"] < 35.0
    assert "CCC" in critical["esg_rating"]
    assert critical["status"] == "critical"
    assert len(critical["strategic_recommendations"]) >= 3


def test_treasury_cash_conversion_cycle():
    res = treasury_working_capital_service.calculate_cash_conversion_cycle(
        dso_receivables_days=40.0,
        dio_inventory_days=30.0,
        dpo_payables_days=50.0,
        annual_revenue_cop=1200000000.0,
        annual_cogs_cop=800000000.0
    )
    # CCC = 40 + 30 - 50 = 20 days
    assert res["ccc_days"] == 20.0
    assert res["cuentas_por_cobrar_cop"] > 0
    assert res["inventarios_cop"] > 0
    assert res["cuentas_por_pagar_cop"] > 0
    assert res["ktno_cop"] > 0
    assert "ALTA EFICIENCIA" in res["efficiency_diagnosis"]


def test_treasury_factoring_simulation():
    res = treasury_working_capital_service.simulate_factoring_discount(
        invoice_face_value_cop=50000000.0,
        days_to_maturity=60,
        monthly_discount_rate_pct=1.40,
        platform_fee_pct=0.30
    )
    assert res["invoice_face_value_cop"] == 50000000.0
    assert res["discount_cost_cop"] > 0
    assert res["platform_fee_cop"] > 0
    assert res["net_cash_received_cop"] < 50000000.0
    assert res["effective_annual_rate_ea_pct"] > 0
    assert "Anticipar esta factura" in res["recommendation"]


def test_actions_and_dispatcher_schemas():
    # Direct action test: ESG
    act_esg = esg_governance_action({
        "company_name": "Agrovalle",
        "environmental_score": 80.0,
        "social_score": 85.0,
        "governance_score": 90.0
    })
    assert "GOBIERNO CORPORATIVO & SOSTENIBILIDAD ESG" in act_esg
    assert "Agrovalle" in act_esg

    # Direct action test: Treasury CCC
    act_ccc = treasury_working_capital_action({
        "action_type": "ccc",
        "dso_receivables_days": 45,
        "dio_inventory_days": 35,
        "dpo_payables_days": 40
    })
    assert "CICLO DE CONVERSIÓN DE EFECTIVO" in act_ccc
    assert "40.0 días" in act_ccc

    # Direct action test: Treasury Factoring
    act_fac = treasury_working_capital_action({
        "action_type": "factoring",
        "invoice_face_value_cop": 20000000.0,
        "days_to_maturity": 45
    })
    assert "FACTORING ELECTRÓNICO" in act_fac
    assert "$20,000,000.00 COP" in act_fac

    # Verify tool schemas registered in SYSTEM_TOOL_DECLARATIONS
    schema_names = [t["name"] for t in SYSTEM_TOOL_DECLARATIONS]
    assert "esg_governance" in schema_names
    assert "treasury_working_capital" in schema_names
