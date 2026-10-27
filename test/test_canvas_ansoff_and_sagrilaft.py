"""
Unit tests for Module 43 (Business Model Canvas & Ansoff Growth Strategy)
and Module 44 (SAGRILAFT & PTEE Corporate Compliance Audit).
"""

from typing import Any, Dict
import pytest

from app.services.business_canvas_ansoff_service import business_canvas_ansoff_service
from app.services.sagrilaft_compliance_service import sagrilaft_compliance_service
from app.actions.business_canvas_ansoff_action import business_canvas_ansoff_action
from app.actions.sagrilaft_compliance_action import sagrilaft_compliance_action
from app.services.action_dispatcher import SYSTEM_TOOL_DECLARATIONS


def test_canvas_ansoff_market_penetration():
    res = business_canvas_ansoff_service.evaluate_canvas_and_ansoff(
        project_name="Plataforma SaaS B2B",
        industry="Tecnología Cloud",
        value_proposition="Reducción del 40% en costos de nómina y automatización contable.",
        customer_segments="Pymes y empresas medianas en Colombia con más de 20 empleados.",
        channels="Venta consultiva directa y referidos B2B.",
        customer_relationships="Soporte VIP y Customer Success dedicado.",
        revenue_streams="Suscripción mensual recurrente y onboarding inicial.",
        key_resources="Equipo de ingenieros y base de datos distribuida.",
        key_activities="Desarrollo de software y atención al cliente.",
        key_partners="AWS Cloud y pasarelas de pago bancarias.",
        cost_structure="Servidores en la nube, nómina de desarrollo y marketing digital.",
        ansoff_quadrant="market_penetration",
        investment_budget=40000000.0,
        currency="COP"
    )

    assert res["project_name"] == "Plataforma SaaS B2B"
    assert res["coherence_score"] >= 80.0
    assert "value_proposition" in res["canvas_blocks"]
    assert res["ansoff_strategy"]["quadrant_key"] == "market_penetration"
    assert res["ansoff_strategy"]["expected_roi_pct"] == 22.5
    assert res["financials"]["investment_budget"] == 40000000.0
    assert res["financials"]["net_profit_expansion"] == 40000000.0 * 0.225
    assert len(res["roadmap"]) == 4


def test_canvas_ansoff_diversification_high_risk():
    res = business_canvas_ansoff_service.evaluate_canvas_and_ansoff(
        project_name="Spin-off AgroTech",
        industry="Agroindustria & Drones",
        ansoff_quadrant="diversification",
        investment_budget=100000000.0,
        currency="COP"
    )

    assert res["ansoff_strategy"]["quadrant_key"] == "diversification"
    assert "Alto" in res["ansoff_strategy"]["risk_level"]
    assert res["ansoff_strategy"]["expected_roi_pct"] == 45.0
    assert res["ansoff_strategy"]["payback_months"] == 24
    assert res["financials"]["net_profit_expansion"] == 45000000.0


def test_sagrilaft_compliance_large_company_obligated():
    res = sagrilaft_compliance_service.audit_compliance(
        company_name="Corporación Financiera Andina S.A.S.",
        annual_revenue_smmlv=45000.0,
        total_assets_smmlv=50000.0,
        sector="factoring",
        has_compliance_officer=True,
        due_diligence_level="intensificada",
        pep_involvement=False,
        cash_intensive_pct=3.0,
        has_whistleblower_channel=True,
        international_operations=True
    )

    assert res["company_name"] == "Corporación Financiera Andina S.A.S."
    assert res["regulatory_status"]["is_sagrilaft_obligated"] is True
    assert res["regulatory_status"]["is_ptee_obligated"] is True
    assert res["risk_assessment"]["semaphore"] == "VERDE"
    assert res["risk_assessment"]["maturity_score"] >= 75.0
    assert res["risk_assessment"]["residual_risk_score"] < res["risk_assessment"]["inherent_risk_score"]


def test_sagrilaft_compliance_pep_red_flag():
    res = sagrilaft_compliance_service.audit_compliance(
        company_name="Constructora del Valle S.A.",
        annual_revenue_smmlv=35000.0,
        total_assets_smmlv=38000.0,
        sector="construccion",
        has_compliance_officer=False,
        due_diligence_level="ordinaria",
        pep_involvement=True,
        cash_intensive_pct=25.0,
        has_whistleblower_channel=False,
        international_operations=False
    )

    assert res["regulatory_status"]["is_sagrilaft_obligated"] is True
    assert res["risk_assessment"]["semaphore"] in ("AMARILLO", "ROJO")
    assert len(res["red_flags"]) >= 3
    assert any("PEP" in flag for flag in res["red_flags"])
    assert any("efectivo" in flag for flag in res["red_flags"])
    assert any("Oficial de Cumplimiento" in flag for flag in res["red_flags"])


def test_sagrilaft_compliance_exempt_small_company():
    res = sagrilaft_compliance_service.audit_compliance(
        company_name="Boutique Creativa S.A.S.",
        annual_revenue_smmlv=1500.0,
        total_assets_smmlv=800.0,
        sector="diseno_grafico",
        has_compliance_officer=False,
        due_diligence_level="simplificada",
        pep_involvement=False,
        cash_intensive_pct=2.0,
        has_whistleblower_channel=False,
        international_operations=False
    )

    assert res["regulatory_status"]["is_sagrilaft_obligated"] is False
    assert res["regulatory_status"]["is_ptee_obligated"] is False
    assert any("Bajo el umbral" in r for r in res["regulatory_status"]["reasons"])


def test_business_canvas_ansoff_action_wrapper():
    output = business_canvas_ansoff_action({
        "project_name": "Consultoría FinTech",
        "industry": "Finanzas",
        "value_proposition": "Optimización fiscal y financiera automatizada.",
        "customer_segments": "Directores financieros y CEOs.",
        "ansoff_quadrant": "product_development",
        "investment_budget": 50000000.0
    })

    assert "MODELO DE NEGOCIO CANVAS & MATRIZ ANSOFF" in output
    assert "Consultoría FinTech" in output or "CONSULTORÍA FINTECH" in output
    assert "LOS 9 BLOQUES DEL BUSINESS MODEL CANVAS" in output
    assert "ESTRATEGIA DE CRECIMIENTO ANSOFF" in output
    assert "Desarrollo de Nuevos Productos" in output


def test_sagrilaft_compliance_action_wrapper():
    output = sagrilaft_compliance_action({
        "company_name": "Inversiones del Cauca S.A.S.",
        "annual_revenue_smmlv": 32000.0,
        "total_assets_smmlv": 35000.0,
        "sector": "inmobiliario",
        "has_compliance_officer": True,
        "due_diligence_level": "intensificada",
        "pep_involvement": False,
        "cash_intensive_pct": 4.0,
        "has_whistleblower_channel": True
    })

    assert "AUDITORÍA DE CUMPLIMIENTO SAGRILAFT & PTEE" in output
    assert "INVERSIONES DEL CAUCA S.A.S." in output
    assert "SUPERSOCIEDADES COLOMBIA" in output
    assert "MATRIZ DE RIESGO Y SCORE DE MADUREZ" in output
    assert "PLAN DE ACCIÓN DE CUMPLIMIENTO INMEDIATO" in output


def test_system_tool_declarations_44():
    tool_names = [t["name"] for t in SYSTEM_TOOL_DECLARATIONS]
    assert "business_canvas_ansoff" in tool_names
    assert "sagrilaft_compliance" in tool_names
    assert "pricing_elasticity" in tool_names
    assert "credit_amortization" in tool_names
    assert "predictive_intelligence" in tool_names
    assert len(SYSTEM_TOOL_DECLARATIONS) >= 71
