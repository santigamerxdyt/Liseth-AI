# -*- coding: utf-8 -*-
"""
Unit tests for Bank Reconciliation, GMF (4x1000) Tax Audit,
and Stochastic Monte Carlo Simulation & Capital Stress Testing Services.
"""

import pytest
from app.services.bank_reconciliation_service import bank_reconciliation_service, EXEMPTION_350_UVT_COP
from app.services.monte_carlo_service import monte_carlo_service
from app.actions.bank_reconciliation_action import bank_reconciliation_action
from app.actions.monte_carlo_action import monte_carlo_action
from app.services.action_dispatcher import SYSTEM_TOOL_DECLARATIONS


def test_bank_reconciliation_exact_balance():
    """Verify that matching balances result in a zero-difference reconciliation."""
    # Stmt = 50,000,000 + dep_transit (5,000,000) - out_checks (3,000,000) = 52,000,000
    # Books = 51,500,000 + unrec_credits (800,000) - fees (300,000) = 52,000,000
    res = bank_reconciliation_service.reconcile_statement(
        bank_statement_balance=50000000.0,
        general_ledger_balance=51500000.0,
        deposits_in_transit=5000000.0,
        outstanding_checks=3000000.0,
        bank_charges_and_fees=300000.0,
        unrecorded_bank_credits=800000.0,
        unrecorded_bank_debits=0.0,
        total_monthly_debits_cop=10000000.0,
        is_account_gmf_exempt=False,
        bank_name="Bancolombia"
    )

    assert res["is_reconciled"] is True
    assert res["summary"]["adjusted_bank_balance"] == 52000000.0
    assert res["summary"]["adjusted_book_balance"] == 52000000.0
    assert res["summary"]["difference"] == 0.0
    assert "CONCILIACIÓN PERFECTA" in res["status_label"]
    assert len(res["suggested_journal_entries"]) > 0


def test_bank_reconciliation_discrepancy():
    """Verify detection of accounting discrepancy."""
    res = bank_reconciliation_service.reconcile_statement(
        bank_statement_balance=40000000.0,
        general_ledger_balance=35000000.0,
        deposits_in_transit=0.0,
        outstanding_checks=0.0
    )
    assert res["is_reconciled"] is False
    assert res["summary"]["difference"] == 5000000.0
    assert "DESCUADRE DETECTADO" in res["status_label"]


def test_bank_reconciliation_gmf_non_exempt():
    """Verify 4x1000 calculation and 50% income tax deductibility on non-exempt accounts."""
    debits = 20000000.0  # 20M COP
    res = bank_reconciliation_service.reconcile_statement(
        bank_statement_balance=1000000.0,
        general_ledger_balance=1000000.0,
        total_monthly_debits_cop=debits,
        is_account_gmf_exempt=False
    )
    g = res["gmf_4x1000_audit"]
    # 20,000,000 * 0.004 = 80,000 COP
    assert g["total_gmf_generated_cop"] == 80000.0
    # 50% deductible in renta: 40,000 COP
    assert g["gmf_50pct_tax_deductible_cop"] == 40000.0
    assert g["gmf_non_deductible_cop"] == 40000.0


def test_bank_reconciliation_gmf_exempt_350_uvt():
    """Verify 350 UVT exemption logic for exempt accounts."""
    # Under 350 UVT -> 0 GMF
    under_uvt = EXEMPTION_350_UVT_COP - 1000000.0
    res1 = bank_reconciliation_service.reconcile_statement(
        bank_statement_balance=1000000.0,
        general_ledger_balance=1000000.0,
        total_monthly_debits_cop=under_uvt,
        is_account_gmf_exempt=True
    )
    assert res1["gmf_4x1000_audit"]["total_gmf_generated_cop"] == 0.0

    # Over 350 UVT -> GMF only on excess
    over_uvt = EXEMPTION_350_UVT_COP + 10000000.0
    res2 = bank_reconciliation_service.reconcile_statement(
        bank_statement_balance=1000000.0,
        general_ledger_balance=1000000.0,
        total_monthly_debits_cop=over_uvt,
        is_account_gmf_exempt=True
    )
    # Excess: 10,000,000 * 0.004 = 40,000 COP
    assert res2["gmf_4x1000_audit"]["total_gmf_generated_cop"] == 40000.0
    assert res2["gmf_4x1000_audit"]["gmf_50pct_tax_deductible_cop"] == 20000.0


def test_monte_carlo_resilient_project():
    """Verify stochastic Monte Carlo simulation on a strong project."""
    res = monte_carlo_service.simulate_project_capital(
        project_name="Planta Solar Valle",
        initial_investment=50000000.0,
        mean_annual_revenue=45000000.0,
        std_annual_revenue=4000000.0,
        fixed_operating_costs=8000000.0,
        variable_costs_ratio=0.20,
        discount_rate_wacc=0.10,
        project_years=5,
        simulations_count=2000
    )

    m = res["metrics"]
    assert res["project_name"] == "Planta Solar Valle"
    assert res["simulations_count"] == 2000
    assert m["prob_positive_npv_pct"] >= 95.0
    assert m["expected_npv_mean"] > 0
    assert len(res["histogram_distribution"]) == 8
    assert res["risk_assessment"]["risk_tier"] == "Bajo Riesgo Estocástico"


def test_monte_carlo_fragile_project():
    """Verify Monte Carlo detection of fragile project with high ruin probability."""
    res = monte_carlo_service.simulate_project_capital(
        project_name="Expansión Riesgosa",
        initial_investment=100000000.0,
        mean_annual_revenue=20000000.0,  # Low revenues
        std_annual_revenue=10000000.0,
        fixed_operating_costs=15000000.0,
        variable_costs_ratio=0.30,
        discount_rate_wacc=0.15,
        project_years=3,
        simulations_count=1000
    )

    m = res["metrics"]
    assert m["prob_positive_npv_pct"] < 50.0
    assert "FRAGILIDAD FINANCIERA" in res["risk_assessment"]["resilience_status"]
    assert m["var_95_cop"] > 0


def test_bank_reconciliation_action():
    """Verify action text generation for bank reconciliation."""
    out = bank_reconciliation_action({
        "bank_statement_balance": 50000000.0,
        "general_ledger_balance": 50000000.0,
        "total_monthly_debits_cop": 15000000.0
    })
    assert "AUDITORÍA DE CONCILIACIÓN BANCARIA" in out
    assert "GMF (4x1000)" in out
    assert "50% Deducible en Renta" in out


def test_monte_carlo_action():
    """Verify action text generation for Monte Carlo simulation."""
    out = monte_carlo_action({
        "project_name": "Hub Logístico",
        "initial_investment": 40000000.0,
        "mean_annual_revenue": 30000000.0,
        "simulations_count": 1000
    })
    assert "SIMULACIÓN ESTOCÁSTICA MONTE CARLO" in out
    assert "Probabilidad de VAN Positivo" in out
    assert "Value at Risk" in out


def test_system_tool_declarations_40():
    """Verify tool schemas are registered in SYSTEM_TOOL_DECLARATIONS."""
    schema_names = [t["name"] for t in SYSTEM_TOOL_DECLARATIONS]
    assert "bank_reconciliation" in schema_names
    assert "monte_carlo_simulation" in schema_names
