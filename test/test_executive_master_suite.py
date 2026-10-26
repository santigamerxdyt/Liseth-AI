"""
Comprehensive unit test suite for the Executive Master Suite:
1. Logistics & Inventory Supply Chain (EOQ, ROP, ABC Pareto)
2. Harvard Strategic Negotiation (ZOPA, BATNA, Nash Surplus)
3. DIAN Tax Compliance & Fiscal Calendar (RST vs Ordinario, UVT thresholds)
4. Balanced Scorecard & OKRs (4 Perspectives, Progress Tracking)
5. Action Dispatcher Integrations
"""
import pytest
from app.services.logistics_inventory_service import logistics_inventory_service
from app.services.negotiation_engine_service import negotiation_engine_service
from app.services.dian_tax_service import dian_tax_service
from app.services.bsc_okrs_service import bsc_okrs_service

from app.actions.logistics_inventory_action import logistics_inventory_action
from app.actions.negotiation_engine_action import negotiation_engine_action
from app.actions.dian_tax_action import dian_tax_action
from app.actions.bsc_okrs_action import bsc_okrs_action


def test_logistics_inventory_service():
    # EOQ: D=10000, S=50000, H=2500 -> Q* = sqrt(2 * 10000 * 50000 / 2500) = sqrt(400000) = 632.46
    eoq = logistics_inventory_service.calculate_eoq(
        annual_demand=10000.0,
        order_cost=50000.0,
        holding_cost=2500.0,
        unit_cost=15000.0
    )
    assert round(eoq["optimal_order_quantity_eoq"], 1) == 632.5
    assert eoq["orders_per_year"] > 0
    assert eoq["annual_ordering_cost"] > 0
    assert eoq["annual_holding_cost"] > 0

    # ROP: d=30, L=5, service_level=95%, sigma=5
    rop = logistics_inventory_service.calculate_rop(
        daily_demand=30.0,
        lead_time_days=5.0,
        service_level_pct=95.0,
        std_dev_daily_demand=5.0
    )
    assert rop["lead_time_demand"] == 150.0
    assert rop["safety_stock_units"] > 0
    assert rop["reorder_point_rop_units"] > 150.0

    # ABC Classification
    items = [
        {"code": "P1", "name": "Servidor", "demand": 10, "cost": 5000000},   # 50M
        {"code": "P2", "name": "Llavero", "demand": 1000, "cost": 10000},     # 10M
        {"code": "P3", "name": "Cable", "demand": 500, "cost": 2000}          # 1M
    ]
    abc = logistics_inventory_service.classify_abc(items)
    assert abc["total_skus"] == 3
    assert abc["total_value"] == 61000000.0
    assert abc["classified_items"][0]["zone"] == "A"


def test_negotiation_engine_service():
    # 1. Positive ZOPA
    neg_pos = negotiation_engine_service.evaluate_negotiation(
        buyer_reservation_price=60000000.0,
        seller_reservation_price=45000000.0
    )
    assert neg_pos["has_zopa"] is True
    assert neg_pos["zopa_size"] == 15000000.0
    assert neg_pos["fair_midpoint_price"] == 52500000.0
    assert neg_pos["status"] == "ZOPA_POSITIVA"

    # 2. Negative ZOPA (Impasse)
    neg_neg = negotiation_engine_service.evaluate_negotiation(
        buyer_reservation_price=40000000.0,
        seller_reservation_price=55000000.0
    )
    assert neg_neg["has_zopa"] is False
    assert neg_neg["gap"] == 15000000.0
    assert neg_neg["status"] == "ZOPA_NEGATIVA_IMPASSE"

    md = negotiation_engine_service.format_markdown_report(neg_pos)
    assert "ZOPA POSITIVA" in md
    assert "Método Harvard" in md


def test_dian_tax_service():
    # 1. Obligation check
    # Above threshold
    check_high = dian_tax_service.check_renta_obligation(
        patrimonio_bruto=250000000.0,
        ingresos_brutos=30000000.0
    )
    assert check_high["is_obligated"] is True
    assert "Patrimonio bruto" in check_high["reasons"][0]

    # Below threshold
    check_low = dian_tax_service.check_renta_obligation(
        patrimonio_bruto=50000000.0,
        ingresos_brutos=40000000.0
    )
    assert check_low["is_obligated"] is False

    # 2. RST vs Ordinario
    sim = dian_tax_service.simulate_rst_vs_ordinario(
        gross_annual_income=180000000.0,
        deductible_expenses=60000000.0,
        activity_type="servicios_profesionales"
    )
    assert sim["ordinario"]["total_liability"] > 0
    assert sim["regimen_simple"]["total_liability"] > 0
    assert "recommendation" in sim

    # 3. Calendar
    cal = dian_tax_service.get_tax_deadlines("901.234.567-8")
    assert len(cal["deadlines_2026"]) >= 3
    assert cal["last_two_digits"] == "67"


def test_bsc_okrs_service():
    dash = bsc_okrs_service.get_dashboard()
    assert dash["global_corporate_health_pct"] > 0
    assert "Financiera" in dash["perspectives"]
    assert "Clientes" in dash["perspectives"]
    assert "Procesos Internos" in dash["perspectives"]
    assert "Aprendizaje & Crecimiento" in dash["perspectives"]

    # Update KR
    updated = bsc_okrs_service.update_kr_progress("KR-01", 60000000.0)
    assert updated is True

    md = bsc_okrs_service.format_markdown_report()
    assert "BALANCED SCORECARD" in md
    assert "Perspectiva Financiera" in md


def test_action_dispatcher_handlers():
    # 1. logistics_inventory_action (eoq)
    res_eoq = logistics_inventory_action({"action": "eoq", "annual_demand": 2000, "order_cost": 20000, "holding_cost": 1000})
    assert res_eoq["status"] == "success"
    assert res_eoq["eoq"]["optimal_order_quantity_eoq"] > 0

    # 2. negotiation_engine_action
    res_neg = negotiation_engine_action({"buyer_reservation_price": 30000000.0, "seller_reservation_price": 25000000.0})
    assert res_neg["status"] == "success"
    assert res_neg["negotiation"]["has_zopa"] is True

    # 3. dian_tax_action (renta_check)
    res_tax = dian_tax_action({"action": "renta_check", "patrimonio_bruto": 300000000.0})
    assert res_tax["status"] == "success"
    assert res_tax["result"]["is_obligated"] is True

    # 4. bsc_okrs_action (dashboard)
    res_okr = bsc_okrs_action({"action": "dashboard"})
    assert res_okr["status"] == "success"
    assert res_okr["dashboard"]["global_corporate_health_pct"] > 0
