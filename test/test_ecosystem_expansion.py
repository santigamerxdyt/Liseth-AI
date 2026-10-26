# -*- coding: utf-8 -*-
"""
Unit tests for the new ecosystem services:
1. Marketing & Digital Growth Engine (app/services/marketing_growth_service.py)
2. Talent Management & Organizational Climate (app/services/talent_management_service.py)
3. Forex Radar & Hedging (app/services/forex_radar_service.py)
4. Action Dispatcher Integration & Schema Verification
"""

import pytest
from app.services.marketing_growth_service import marketing_growth_service
from app.services.talent_management_service import talent_management_service
from app.services.forex_radar_service import forex_radar_service
from app.services.action_dispatcher import SYSTEM_TOOL_DECLARATIONS
from app.actions.marketing_growth_action import marketing_growth_action
from app.actions.talent_management_action import talent_management_action
from app.actions.forex_radar_action import forex_radar_action


def test_marketing_growth_unit_economics():
    res = marketing_growth_service.calculate_unit_economics(
        cac=120000.0, arpu=65000.0, churn_monthly_pct=3.0, gross_margin_pct=80.0, currency="COP"
    )
    assert res["cac"] == 120000.0
    assert res["arpu"] == 65000.0
    assert res["gross_margin_pct"] == 80.0
    assert res["churn_monthly_pct"] == 3.0
    assert res["ltv"] > 1000000.0
    assert res["ltv_cac_ratio"] > 10.0
    assert res["cac_payback_months"] < 3.0
    assert "optimal" in res["status"] or "healthy" in res["status"]


def test_marketing_growth_funnel_and_roas():
    # Funnel
    funnel = marketing_growth_service.diagnose_funnel(
        impressions=100000, clicks=2500, leads_mql=200, opportunities_sql=50, closed_won=15
    )
    assert funnel["conversion_rates"]["ctr_pct"] == 2.5
    assert funnel["conversion_rates"]["click_to_mql_pct"] == 8.0
    assert funnel["stages"]["closed_won"] == 15

    # ROAS
    roas = marketing_growth_service.calculate_roas_and_attribution([
        {"channel": "Google Search", "spend": 1000000, "revenue": 4500000, "conversions": 20},
        {"channel": "Meta Ads", "spend": 1000000, "revenue": 2000000, "conversions": 10}
    ])
    assert roas["total_spend"] == 2000000.0
    assert roas["total_revenue"] == 6500000.0
    assert roas["blended_roas"] == 3.25
    assert roas["best_channel"] == "Google Search"


def test_talent_management_9box_and_enps():
    # 9-box Star
    star = talent_management_service.evaluate_9box(
        employee_name="Santiago", performance_score=3.0, potential_score=3.0, role="CEO"
    )
    assert "Estrella" in star["quadrant"]
    assert star["performance_level"] == "Alto"
    assert star["potential_level"] == "Alto"

    # 9-box Dilemma / PIP
    inconsistent = talent_management_service.evaluate_9box(
        employee_name="Juan", performance_score=1.2, potential_score=2.0
    )
    assert "Dilema" in inconsistent["quadrant"]

    # eNPS
    enps = talent_management_service.calculate_enps(promoters=60, passives=30, detractors=10)
    assert enps["total_respondents"] == 100
    assert enps["promoters_pct"] == 60.0
    assert enps["detractors_pct"] == 10.0
    assert enps["enps_score"] == 50.0
    assert "EXCEPCIONAL" in enps["diagnostic"]


def test_talent_management_turnover_cost():
    t_cost = talent_management_service.calculate_turnover_cost(
        departures=3, avg_headcount=30, avg_salary_cop=3000000.0, period_months=12
    )
    assert t_cost["turnover_rate_pct"] == 10.0
    assert t_cost["annualized_turnover_pct"] == 10.0
    assert t_cost["cost_per_departure_cop"] == 12000000.0
    assert t_cost["total_turnover_cost_cop"] == 36000000.0


def test_forex_radar_rates_and_hedging():
    # Forex radar
    rates = forex_radar_service.get_forex_radar(base_usd_cop=4200.0)
    assert rates["trm_oficial_cop"] == 4200.0
    assert rates["dolar_tarjeta_cop"] > 4200.0
    assert rates["euro_cop"] > 4200.0
    assert "USDT" in rates["arbitrage_tip"]

    # Forward hedging
    hedge = forex_radar_service.simulate_forward_hedge(
        amount_usd=20000.0, spot_rate_cop=4200.0, days_forward=90,
        rate_cop_annual_pct=10.0, rate_usd_annual_pct=5.0
    )
    assert hedge["spot_rate_cop"] == 4200.0
    assert hedge["forward_rate_cop"] > 4200.0
    assert hedge["hedging_cost_cop"] > 0
    assert "Forward" in hedge["strategic_recommendation"]


def test_dispatcher_actions_and_schemas():
    # Direct action tests
    act_mkt = marketing_growth_action({
        "action_type": "unit_economics", "cac": 100000, "arpu": 50000, "churn_monthly_pct": 2.5
    })
    assert "UNIT ECONOMICS" in act_mkt
    assert "Ratio LTV / CAC" in act_mkt

    act_funnel = marketing_growth_action({
        "action_type": "funnel", "impressions": 50000, "clicks": 2000, "leads_mql": 150
    })
    assert "EMBUDO DE CONVERSIÓN" in act_funnel or "EMBUDO DE" in act_funnel

    act_talent = talent_management_action({
        "action_type": "9box", "employee_name": "Laura", "performance_score": 2.9, "potential_score": 2.8
    })
    assert "MATRIZ 9-BOX" in act_talent
    assert "Estrella" in act_talent

    act_enps = talent_management_action({
        "action_type": "enps", "promoters": 40, "passives": 10, "detractors": 5
    })
    assert "CLIMA ORGANIZACIONAL" in act_enps

    act_forex = forex_radar_action({
        "action_type": "radar", "base_usd_cop": 4150.0
    })
    assert "RADAR CAMBIARIO" in act_forex
    assert "TRM Oficial" in act_forex

    act_hedge = forex_radar_action({
        "action_type": "hedge", "amount_usd": 15000, "days_forward": 60
    })
    assert "COBERTURA CAMBIARIA FORWARD" in act_hedge

    # Verify tool schemas registered in SYSTEM_TOOL_DECLARATIONS
    schema_names = [t["name"] for t in SYSTEM_TOOL_DECLARATIONS]
    assert "marketing_growth" in schema_names
    assert "talent_management" in schema_names
    assert "forex_radar" in schema_names
