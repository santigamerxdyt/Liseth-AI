"""
Comprehensive unit test suite for the newly added Strategic & Executive Modules:
1. Investment Project Evaluator (NPV, IRR, Payback, B/C, Scenarios)
2. Corporate Risk Matrix & 5x5 Heatmap (ISO 31000)
3. Colombia Macroeconomic Radar & Payroll Liquidation Engine
4. Pitch Deck & Presentation Generator
5. Action Dispatcher Integrations
"""
import pytest
from app.services.investment_evaluator_service import investment_evaluator_service
from app.services.risk_matrix_service import risk_matrix_service
from app.services.colombia_macro_service import colombia_macro_service
from app.services.pitch_generator_service import pitch_generator_service

from app.actions.investment_evaluator_action import investment_evaluator_action
from app.actions.risk_matrix_action import risk_matrix_action
from app.actions.colombia_macro_action import colombia_macro_action
from app.actions.pitch_generator_action import pitch_generator_action


def test_investment_evaluator_service():
    # Example: Initial Investment = 50M COP, Flows: 20M, 25M, 30M, Discount Rate: 10%
    inv = 50000000.0
    flows = [20000000.0, 25000000.0, 30000000.0]
    rate = 0.10

    res = investment_evaluator_service.evaluate_project(
        name="Proyecto Planta Valle",
        initial_investment=inv,
        cash_flows=flows,
        discount_rate=rate,
        currency="COP"
    )

    assert res["project_id"].startswith("PROJ-")
    assert res["npv"] > 0
    assert res["irr_pct"] is not None and res["irr_pct"] > 10.0
    assert res["payback_years"] is not None and res["payback_years"] < 3.0
    assert res["benefit_cost_ratio"] > 1.0
    assert "VIABLE" in res["decision"]
    assert "scenarios" in res
    assert res["scenarios"]["optimistic_plus_20"]["npv"] > res["scenarios"]["base"]["npv"]
    assert res["scenarios"]["pessimistic_minus_20"]["npv"] < res["scenarios"]["base"]["npv"]

    md = investment_evaluator_service.format_markdown_report(res)
    assert "EVALUACIÓN FINANCIERA DE PROYECTO" in md
    assert "VAN" in md
    assert "TIR" in md


def test_risk_matrix_service():
    heatmap = risk_matrix_service.get_heatmap_5x5()
    assert heatmap["total_risks"] >= 4
    assert "cells" in heatmap
    assert "inherent_counts" in heatmap

    # Add a new risk
    new_risk = risk_matrix_service.add_risk(
        title="Fluctuación de Costos de Transporte",
        category="Operacional",
        probability=4,
        impact=3,
        control="Contratos forward con transportadoras",
        residual_probability=2,
        residual_impact=2,
        owner="Santiago / COO"
    )

    assert new_risk["id"].startswith("RSK-")
    assert new_risk["inherent_risk"] == 12
    assert new_risk["inherent_level"] == "ALTO"
    assert new_risk["residual_risk"] == 4
    assert new_risk["residual_level"] == "BAJO"

    # Verify list
    risks = risk_matrix_service.list_risks()
    assert any(r["id"] == new_risk["id"] for r in risks)

    # Delete the created risk
    deleted = risk_matrix_service.delete_risk(new_risk["id"])
    assert deleted is True


def test_colombia_macro_and_payroll_service():
    indicators = colombia_macro_service.get_macro_indicators()
    assert indicators["year"] == 2026
    assert indicators["trm_cop_usd"] > 3500.0
    assert indicators["uvt_cop"] > 40000.0
    assert indicators["smlmv_cop"] > 1000000.0

    # UVT Conversion
    conv = colombia_macro_service.convert_uvt(amount=100.0, direction="uvt_to_cop")
    assert conv["cop"] == round(100.0 * indicators["uvt_cop"], 2)

    # Payroll liquidation: salary 2,000,000 COP (< 2 SMLMV -> has transport allowance)
    payroll = colombia_macro_service.liquidate_payroll(
        base_salary=2000000.0,
        risk_level=1
    )
    assert payroll["base_salary"] == 2000000.0
    assert payroll["has_transport"] is True
    assert payroll["transport_allowance"] == indicators["aux_transporte_cop"]
    assert payroll["is_exempt_art_114_1"] is True
    assert payroll["employee"]["health_deduction"] == 80000.0  # 4%
    assert payroll["employee"]["pension_deduction"] == 80000.0  # 4%
    assert payroll["total_company_cost"] > 2000000.0
    assert payroll["cost_multiplier"] > 1.35

    md = colombia_macro_service.format_markdown_report(payroll)
    assert "LIQUIDACIÓN LABORAL Y COSTO EMPRESA" in md
    assert "Factor Multiplicador Real" in md


def test_pitch_generator_service():
    deck = pitch_generator_service.generate_deck(
        business_name="BioValle Tech",
        industry="agroindustria",
        funding_ask=180000000.0,
        currency="COP",
        founder_name="Santiago Huerfano",
        city="Palmira, Colombia"
    )

    assert deck["business_name"] == "BioValle Tech"
    assert deck["total_slides"] == 10
    assert len(deck["slides"]) == 10
    assert deck["slides"][0]["title"] == "BIOVALLE TECH"
    assert "Problema" in deck["slides"][1]["title"]
    assert "Solución" in deck["slides"][2]["title"]
    assert "Magia" in deck["slides"][3]["title"]
    assert "Modelo de Negocio" in deck["slides"][4]["title"]
    assert "Mercado" in deck["slides"][5]["title"]
    assert "Go-to-Market" in deck["slides"][6]["title"]
    assert "Competitivo" in deck["slides"][7]["title"]
    assert "Equipo" in deck["slides"][8]["title"]
    assert "Financieras" in deck["slides"][9]["title"]

    md = pitch_generator_service.format_markdown(deck)
    assert "PITCH DECK EJECUTIVO" in md
    assert "Diapositiva 10" in md


def test_action_dispatcher_handlers():
    # 1. investment_evaluator_action
    inv_res = investment_evaluator_action({
        "project_name": "Iniciativa E-commerce",
        "initial_investment": 30000000.0,
        "cash_flows": [15000000.0, 18000000.0, 22000000.0],
        "discount_rate": 0.15
    })
    assert inv_res["status"] == "success"
    assert inv_res["result"]["npv"] > 0

    # 2. risk_matrix_action
    rsk_res = risk_matrix_action({"action": "summary"})
    assert rsk_res["status"] == "success"
    assert "heatmap" in rsk_res

    # 3. colombia_macro_action
    macro_res = colombia_macro_action({"action": "payroll", "base_salary": 3500000.0})
    assert macro_res["status"] == "success"
    assert "payroll" in macro_res

    # 4. pitch_generator_action
    pitch_res = pitch_generator_action({
        "business_name": "Stark Analytics UNAL",
        "industry": "consultoria",
        "funding_ask": 120000000.0
    })
    assert pitch_res["status"] == "success"
    assert len(pitch_res["deck"]["slides"]) == 10
