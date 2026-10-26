"""
Comprehensive unit test suite for the Advanced Multi-Domain Executive Suite:
1. DIAN Tax Payment & Formulario 490 Settlement (PSE, Usury Interest, Extemporaneity)
2. Business Valuation (DCF Gordon-Shapiro, Multiples, Venture Capital Method)
3. Fleet Routes & Colombian Freight Logistics
4. Biocognitive Telemetry & Executive Habits
5. Action Dispatcher Integrations
"""
import pytest
from app.services.tax_payment_service import tax_payment_service
from app.services.business_valuation_service import business_valuation_service
from app.services.fleet_routes_service import fleet_routes_service
from app.services.biocognitive_habits_service import biocognitive_habits_service

from app.actions.tax_payment_action import tax_payment_action
from app.actions.business_valuation_action import business_valuation_action
from app.actions.fleet_routes_action import fleet_routes_action
from app.actions.biocognitive_habits_action import biocognitive_habits_action


def test_tax_payment_service():
    # 1. On-time payment (no penalties, no interest)
    ontime = tax_payment_service.settle_form_490(
        concept_key="retefuente",
        tax_year=2026,
        period="01",
        nit="901.884.221-3",
        base_tax_amount=2000000.0,
        due_date_str="2026-02-15T00:00:00Z",
        payment_date_str="2026-02-14T00:00:00Z"
    )
    assert ontime["base_tax_amount"] == 2000000.0
    assert ontime["extemporaneity_penalty"] == 0.0
    assert ontime["moratory_interest"] == 0.0
    assert ontime["total_payable"] == 2000000.0

    # 2. Late payment (45 days late -> 2 months -> penalty >= minimum 10 UVT, interest > 0)
    late = tax_payment_service.settle_form_490(
        concept_key="iva",
        tax_year=2026,
        period="01",
        nit="901.884.221-3",
        base_tax_amount=5000000.0,
        due_date_str="2026-03-15T00:00:00Z",
        payment_date_str="2026-04-30T00:00:00Z"
    )
    assert late["days_late"] > 40
    assert late["extemporaneity_penalty"] >= 497990.0  # Min 10 UVT
    assert late["moratory_interest"] > 0
    assert late["total_payable"] > 5000000.0

    # 3. PSE Gateway Intent & Confirmation
    intent = tax_payment_service.generate_pse_intent(ontime, bank_name="Bancolombia")
    assert "muisca.dian.gov.co" in intent["payment_url"]
    assert intent["cus_code"].startswith("CUS-DIAN-")

    payment = tax_payment_service.confirm_payment(ontime, "Bancolombia", intent["cus_code"])
    assert payment["status"] == "PAGADO_PAZ_Y_SALVO"

    hist = tax_payment_service.get_payment_history()
    assert any(p["receipt_id"] == ontime["receipt_id"] for p in hist)


def test_business_valuation_service():
    # 1. DCF Valuation
    flows = [50000000.0, 70000000.0, 95000000.0, 120000000.0]
    dcf = business_valuation_service.valuation_dcf(
        projected_flows=flows,
        wacc_discount_rate=0.12,
        terminal_growth_g=0.03,
        cash_balance=25000000.0,
        total_debt=10000000.0
    )
    assert dcf["enterprise_value_ev"] > 0
    assert dcf["equity_value"] == round(dcf["enterprise_value_ev"] + 25000000.0 - 10000000.0, 2)
    assert len(dcf["annual_table"]) == 4

    # 2. Multiples
    mult = business_valuation_service.valuation_multiples(
        ebitda=100000000.0,
        annual_revenue=500000000.0,
        industry_key="tech_saas"
    )
    assert mult["valuation_by_ebitda"]["base"] == 1200000000.0  # 12x
    assert mult["valuation_by_revenue"] == 2000000000.0         # 4x

    # 3. Venture Capital
    vc = business_valuation_service.valuation_venture_capital(
        target_exit_value=10000000000.0,
        years_to_exit=5,
        required_roi_multiple=5.0,
        investment_amount=500000000.0
    )
    assert vc["post_money_valuation"] == 2000000000.0
    assert vc["pre_money_valuation"] == 1500000000.0
    assert vc["investor_equity_share_pct"] == 25.0


def test_fleet_routes_service():
    freight = fleet_routes_service.calculate_freight(
        route_key="palmira_cali",
        vehicle_key="turbo_4_ton"
    )
    assert freight["origin"] == "Palmira"
    assert freight["destination"] == "Cali"
    assert freight["distance_km"] == 28.0
    assert freight["total_freight_cost_cop"] > 0
    assert freight["co2_emissions_kg"] > 0

    md = fleet_routes_service.format_markdown_report(freight)
    assert "FLETE LOGÍSTICO" in md
    assert "Combustible" in md


def test_biocognitive_habits_service():
    habits = biocognitive_habits_service.evaluate_habits(
        sleep_hours=8.0,
        water_glasses=8,
        deep_work_hours=4.0,
        energy_rating=9,
        chronotype="matutino_alondra"
    )
    assert habits["biocognitive_index_pct"] >= 80.0
    assert habits["status"] == "OPTIMO"
    assert "08:30" in habits["peak_window"]

    md = biocognitive_habits_service.format_markdown_report(habits)
    assert "TELEMETRÍA BIOCOGNITIVA" in md
    assert "Índice Biocognitivo" in md


def test_action_dispatcher_handlers():
    # 1. Tax payment settle
    res_tax = tax_payment_action({
        "action": "settle",
        "concept": "retefuente",
        "amount": 2500000.0
    })
    assert res_tax["status"] == "success"
    assert res_tax["settlement"]["total_payable"] >= 2500000.0

    # 2. Tax payment PSE
    res_pse = tax_payment_action({
        "action": "pse_link",
        "concept": "retefuente",
        "amount": 1000000.0,
        "bank": "Bancolombia"
    })
    assert res_pse["status"] == "success"
    assert "intent" in res_pse

    # 3. Business Valuation DCF
    res_val = business_valuation_action({
        "method": "dcf",
        "cash_flows": [40000000.0, 50000000.0, 60000000.0]
    })
    assert res_val["status"] == "success"
    assert res_val["valuation"]["enterprise_value_ev"] > 0

    # 4. Fleet Routes
    res_fleet = fleet_routes_action({
        "route": "palmira_yumbo",
        "vehicle": "van_urbana"
    })
    assert res_fleet["status"] == "success"
    assert res_fleet["freight"]["total_freight_cost_cop"] > 0

    # 5. Biocognitive habits
    res_bio = biocognitive_habits_action({
        "action": "log",
        "sleep_hours": 7.5,
        "energy_rating": 8
    })
    assert res_bio["status"] == "success"
    assert res_bio["biocognitive"]["biocognitive_index_pct"] > 70.0
