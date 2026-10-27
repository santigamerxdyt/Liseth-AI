# -*- coding: utf-8 -*-
"""
Unit tests for Pricing Strategy & Price Elasticity of Demand (PED),
and Advanced Bank Credit Amortization & Debt Optimization Services.
"""

import pytest
from app.services.pricing_elasticity_service import pricing_elasticity_service
from app.services.credit_amortization_service import credit_amortization_service, LEGAL_USURY_RATE_EA_PCT
from app.actions.pricing_elasticity_action import pricing_elasticity_action
from app.actions.credit_amortization_action import credit_amortization_action
from app.services.action_dispatcher import SYSTEM_TOOL_DECLARATIONS


def test_pricing_elasticity_inelastic_demand():
    """Verify inelastic demand logic (|Ed| < 1)."""
    res = pricing_elasticity_service.evaluate_pricing_strategy(
        product_name="Insumo Agrícola Especializado",
        current_price=100000.0,
        unit_marginal_cost=40000.0,
        current_monthly_units=500.0,
        price_elasticity=-0.50,
        currency="COP"
    )

    assert "INELÁSTICA" in res["elasticity_analysis"]["classification"]
    assert res["elasticity_analysis"]["coefficient_ed"] == -0.50
    # In inelastic demand, best simulated price is higher than current price
    assert res["optimization"]["best_simulated_price"] > 100000.0
    assert res["optimization"]["potential_margin_gain"] > 0
    assert len(res["simulation_curve"]) == 8


def test_pricing_elasticity_arc_calculation():
    """Verify Arc (midpoint) elasticity calculation from test price/volume."""
    # Price rises from 50,000 to 60,000 (+20%)
    # Quantity falls from 1,000 to 750 (-25%)
    res = pricing_elasticity_service.evaluate_pricing_strategy(
        product_name="Producto Retail",
        current_price=50000.0,
        unit_marginal_cost=25000.0,
        current_monthly_units=1000.0,
        test_price=60000.0,
        test_volume=750.0
    )
    ed = res["elasticity_analysis"]["coefficient_ed"]
    assert ed < -1.0  # Elastic
    assert "ELÁSTICA" in res["elasticity_analysis"]["classification"]
    assert res["optimization"]["optimal_theoretical_price"] > 0


def test_credit_amortization_french_system():
    """Verify French system constant payment and balance reduction."""
    res = credit_amortization_service.calculate_amortization(
        loan_name="Crédito Capital de Trabajo",
        principal_amount=30000000.0,
        annual_interest_rate_ea_pct=18.0,
        term_months=36,
        amortization_system="french",
        extra_monthly_prepayment=0.0
    )

    t = res["loan_terms"]
    p = res["payment_summary"]
    assert t["contracted_term_months"] == 36
    assert t["effective_term_months"] == 36
    assert p["total_principal_paid"] == 30000000.0
    assert p["total_interest_paid"] > 0
    assert res["usury_compliance"]["is_legal"] is True
    assert len(res["schedule_preview"]) > 0


def test_credit_amortization_german_system_savings():
    """Verify German system pays less total interest than French system."""
    res_french = credit_amortization_service.calculate_amortization(
        principal_amount=40000000.0,
        annual_interest_rate_ea_pct=20.0,
        term_months=48,
        amortization_system="french"
    )
    res_german = credit_amortization_service.calculate_amortization(
        principal_amount=40000000.0,
        annual_interest_rate_ea_pct=20.0,
        term_months=48,
        amortization_system="german"
    )

    french_interest = res_french["payment_summary"]["total_interest_paid"]
    german_interest = res_german["payment_summary"]["total_interest_paid"]
    assert german_interest < french_interest


def test_credit_amortization_prepayment_relief():
    """Verify extra prepayment reduces months and saves interest."""
    res = credit_amortization_service.calculate_amortization(
        principal_amount=50000000.0,
        annual_interest_rate_ea_pct=19.5,
        term_months=60,
        amortization_system="french",
        extra_monthly_prepayment=500000.0  # 500k monthly prepayment
    )

    prep = res["prepayment_optimization"]
    assert prep["months_shortened"] > 0
    assert prep["interest_saved"] > 0
    assert prep["interest_saved_pct"] > 0
    assert res["loan_terms"]["effective_term_months"] < 60


def test_credit_amortization_usury_detection():
    """Verify detection of loan exceeding legal usury rate."""
    illegal_rate = LEGAL_USURY_RATE_EA_PCT + 5.0
    res = credit_amortization_service.calculate_amortization(
        principal_amount=10000000.0,
        annual_interest_rate_ea_pct=illegal_rate,
        term_months=12
    )

    assert res["usury_compliance"]["is_legal"] is False
    assert "SUPERA la tasa de usura legal" in res["usury_compliance"]["status_note"]


def test_pricing_elasticity_action_wrapper():
    """Verify action text generation for pricing elasticity."""
    out = pricing_elasticity_action({
        "product_name": "Software SaaS",
        "current_price": 80000.0,
        "unit_marginal_cost": 15000.0,
        "current_monthly_units": 600.0,
        "price_elasticity": -0.8
    })

    assert "ESTRATEGIA DE PRECIOS" in out
    assert "INELÁSTICA" in out
    assert "Índice de Lerner" in out


def test_credit_amortization_action_wrapper():
    """Verify action text generation for credit amortization."""
    out = credit_amortization_action({
        "principal_amount": 25000000.0,
        "annual_interest_rate_ea_pct": 19.0,
        "term_months": 24,
        "extra_monthly_prepayment": 300000.0
    })

    assert "SIMULADOR DE CRÉDITO" in out
    assert "Cuota Mensual Inicial" in out
    assert "ESTRATEGIA DE PREPAGOS" in out
    assert "COMPARATIVO DE SISTEMAS" in out


def test_system_tool_declarations_42():
    """Verify tool schemas are registered in SYSTEM_TOOL_DECLARATIONS."""
    schema_names = [t["name"] for t in SYSTEM_TOOL_DECLARATIONS]
    assert "pricing_elasticity" in schema_names
    assert "credit_amortization" in schema_names
