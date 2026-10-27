"""
Extended Executive Suite Router for JARVIS / Liseth.
Provides API endpoints for Personal Wealth Management, Stark Vault Password Engine,
Legal Contract Generation, and Deep Work Focus / Memory Purge.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.personal_finance_service import personal_finance_service
from app.services.stark_vault_service import stark_vault_service
from app.services.legal_contracts_service import legal_contracts_service
from app.services.focus_engine_service import focus_engine_service
from app.services.investment_evaluator_service import investment_evaluator_service
from app.services.risk_matrix_service import risk_matrix_service
from app.services.colombia_macro_service import colombia_macro_service
from app.services.pitch_generator_service import pitch_generator_service
from app.services.logistics_inventory_service import logistics_inventory_service
from app.services.negotiation_engine_service import negotiation_engine_service
from app.services.dian_tax_service import dian_tax_service
from app.services.bsc_okrs_service import bsc_okrs_service
from app.services.tax_payment_service import tax_payment_service
from app.services.business_valuation_service import business_valuation_service
from app.services.fleet_routes_service import fleet_routes_service
from app.services.biocognitive_habits_service import biocognitive_habits_service
from app.services.stock_trading_service import stock_trading_service
from app.services.dividend_screener_service import dividend_screener_service
from app.services.bank_reconciliation_service import bank_reconciliation_service
from app.services.monte_carlo_service import monte_carlo_service
from app.services.pricing_elasticity_service import pricing_elasticity_service
from app.services.credit_amortization_service import credit_amortization_service
from app.services.business_canvas_ansoff_service import business_canvas_ansoff_service
from app.services.sagrilaft_compliance_service import sagrilaft_compliance_service
from app.services.predictive_intelligence_service import predictive_intelligence_service




router = APIRouter(prefix="/api/suite", tags=["suite"])


class FinanceEntryRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Monto en COP")
    category: str = Field(default="Alimentacion", description="Categoría")
    entry_type: str = Field(default="expense", description="expense o income")
    description: str = Field(default="Gasto general", description="Descripción")
    payment_method: str = Field(default="Contactless / Efectivo", description="Método")


class BudgetCapRequest(BaseModel):
    category: str = Field(..., description="Categoría")
    monthly_limit: float = Field(..., gt=0, description="Tope mensual")


class PasswordGenRequest(BaseModel):
    length: int = Field(default=18, ge=6, le=64, description="Longitud")
    mode: str = Field(default="complex", description="complex, passphrase, pin")


class ContractGenRequest(BaseModel):
    template: str = Field(default="servicios_profesionales", description="servicios_profesionales, nda, pagare, acta_entrega")
    client_name: str = Field(..., description="Nombre del cliente o contraparte")
    client_id: str = Field(default="900.000.000-1", description="NIT o cédula")
    amount: float = Field(default=2500000.0, description="Monto")
    scope: str = Field(default="Asesoría en Administración y Consultoría", description="Objeto")
    city: str = Field(default="Palmira, Valle del Cauca", description="Ciudad")


class FocusSessionRequest(BaseModel):
    duration_minutes: int = Field(default=25, ge=5, le=120)
    objective: str = Field(default="Trabajo Profundo & Estudio")


# ─── FINANZAS PERSONALES ───
@router.get("/finances/summary")
async def get_finance_summary(month: Optional[str] = None):
    return personal_finance_service.get_summary(month=month)


@router.post("/finances/add")
async def add_finance_entry(req: FinanceEntryRequest):
    res = personal_finance_service.add_entry(
        amount=req.amount,
        category=req.category,
        entry_type=req.entry_type,
        description=req.description,
        payment_method=req.payment_method
    )
    return {"ok": True, "entry": res}


@router.post("/finances/budget")
async def set_category_budget(req: BudgetCapRequest):
    res = personal_finance_service.set_budget_cap(req.category, req.monthly_limit)
    return {"ok": True, "budget": res}


# ─── BÓVEDA STARK ───
@router.post("/vault/generate")
async def generate_password_endpoint(req: PasswordGenRequest):
    res = stark_vault_service.generate_password(length=req.length, mode=req.mode)
    return {"ok": True, "result": res}


@router.get("/vault/audit")
async def audit_password_endpoint(password: str = Query(...)):
    res = stark_vault_service.evaluate_password_strength(password)
    return {"ok": True, "audit": res}


# ─── CONTRATOS Y MINUTAS ───
@router.post("/contracts/generate")
async def generate_contract_endpoint(req: ContractGenRequest):
    res = legal_contracts_service.generate_contract(
        template_type=req.template,
        party_b_name=req.client_name,
        party_b_id=req.client_id,
        amount=req.amount,
        scope=req.scope,
        city=req.city
    )
    return {"ok": True, "contract": res}


# ─── MODO FOCO Y MISION CONTROL ───
@router.post("/focus/start")
async def start_focus_endpoint(req: FocusSessionRequest):
    res = focus_engine_service.start_focus_session(duration_minutes=req.duration_minutes, objective=req.objective)
    return {"ok": True, "session": res}


@router.post("/focus/stop")
async def stop_focus_endpoint():
    res = focus_engine_service.stop_focus_session()
    return {"ok": True, "session": res}


@router.get("/focus/status")
async def get_focus_status_endpoint():
    return focus_engine_service.get_focus_status()


@router.post("/focus/purge-memory")
async def purge_memory_endpoint():
    res = focus_engine_service.purge_system_memory()
    return {"ok": True, "result": res}


# ─── EVALUACIÓN DE PROYECTOS DE INVERSIÓN (VAN, TIR, PAYBACK) ───
class InvestmentEvalRequest(BaseModel):
    name: str = Field(default="Iniciativa Estratégica", description="Nombre del proyecto")
    initial_investment: float = Field(..., gt=0, description="Inversión inicial")
    cash_flows: List[float] = Field(..., description="Flujos proyectados anuales")
    discount_rate: float = Field(default=0.12, ge=0.0, le=1.0, description="Tasa de descuento")
    currency: str = Field(default="COP", description="Moneda")


@router.post("/projects/eval")
async def evaluate_project_endpoint(req: InvestmentEvalRequest):
    res = investment_evaluator_service.evaluate_project(
        name=req.name,
        initial_investment=req.initial_investment,
        cash_flows=req.cash_flows,
        discount_rate=req.discount_rate,
        currency=req.currency
    )
    return {"ok": True, "evaluation": res}


# ─── MATRIZ DE RIESGOS CORPORATIVOS & MAPA DE CALOR 5x5 ───
class RiskAddRequest(BaseModel):
    title: str = Field(..., description="Título del evento de riesgo")
    category: str = Field(default="Estrategico", description="Categoría")
    probability: int = Field(default=3, ge=1, le=5)
    impact: int = Field(default=3, ge=1, le=5)
    control: str = Field(default="Protocolo de mitigación preventiva")
    residual_probability: int = Field(default=2, ge=1, le=5)
    residual_impact: int = Field(default=2, ge=1, le=5)
    owner: str = Field(default="Santiago / CEO")


@router.get("/risks/heatmap")
async def get_risk_heatmap_endpoint():
    return risk_matrix_service.get_heatmap_5x5()


@router.post("/risks/add")
async def add_risk_endpoint(req: RiskAddRequest):
    res = risk_matrix_service.add_risk(
        title=req.title,
        category=req.category,
        probability=req.probability,
        impact=req.impact,
        control=req.control,
        residual_probability=req.residual_probability,
        residual_impact=req.residual_impact,
        owner=req.owner
    )
    return {"ok": True, "risk": res}


@router.delete("/risks/{risk_id}")
async def delete_risk_endpoint(risk_id: str):
    ok = risk_matrix_service.delete_risk(risk_id)
    return {"ok": ok, "risk_id": risk_id}


# ─── RADAR MACROECONÓMICO & LIQUIDADOR LABORAL COLOMBIA ───
class PayrollCalcRequest(BaseModel):
    base_salary: float = Field(..., gt=0, description="Salario base en COP")
    risk_level: int = Field(default=1, ge=1, le=5, description="Nivel ARL (1 a 5)")
    include_transport: Optional[bool] = Field(default=None, description="Inclusión de auxilio de transporte")
    apply_exemption_114_1: Optional[bool] = Field(default=None, description="Exoneración Art. 114-1 E.T.")


@router.get("/macro/indicators")
async def get_macro_indicators_endpoint():
    return colombia_macro_service.get_macro_indicators()


@router.post("/macro/payroll")
async def calculate_payroll_endpoint(req: PayrollCalcRequest):
    res = colombia_macro_service.liquidate_payroll(
        base_salary=req.base_salary,
        risk_level=req.risk_level,
        include_transport=req.include_transport,
        apply_exemption_114_1=req.apply_exemption_114_1
    )
    return {"ok": True, "payroll": res}


# ─── GENERADOR DE PITCH DECKS DE INVERSIÓN ───
class PitchDeckRequest(BaseModel):
    business_name: str = Field(..., description="Nombre del negocio o proyecto")
    industry: str = Field(default="tech_saas", description="tech_saas, consultoria, agroindustria, ecommerce")
    problem: Optional[str] = Field(default=None, description="Problema central")
    solution: Optional[str] = Field(default=None, description="Solución propuesta")
    funding_ask: float = Field(default=250000000.0, gt=0, description="Capital solicitado")
    currency: str = Field(default="COP", description="Moneda")
    founder: str = Field(default="Santiago Huerfano Lopez", description="Fundador")
    city: str = Field(default="Palmira / Cali, Colombia", description="Ciudad")


@router.post("/pitch/generate")
async def generate_pitch_deck_endpoint(req: PitchDeckRequest):
    res = pitch_generator_service.generate_deck(
        business_name=req.business_name,
        industry=req.industry,
        problem_statement=req.problem,
        solution_value=req.solution,
        funding_ask=req.funding_ask,
        currency=req.currency,
        founder_name=req.founder,
        city=req.city
    )
    return {"ok": True, "deck": res}


# ─── GESTIÓN DE CADENA DE SUMINISTRO & INVENTARIOS (EOQ & ROP) ───
class EoqRequest(BaseModel):
    annual_demand: float = Field(..., gt=0)
    order_cost: float = Field(..., gt=0)
    holding_cost: float = Field(..., gt=0)
    unit_cost: float = Field(default=0.0, ge=0.0)


class RopRequest(BaseModel):
    daily_demand: float = Field(..., gt=0)
    lead_time_days: float = Field(..., gt=0)
    service_level_pct: float = Field(default=95.0, ge=50.0, le=99.9)
    std_dev_daily_demand: float = Field(default=0.0, ge=0.0)


class AbcClassificationRequest(BaseModel):
    items: List[Dict[str, Any]] = Field(default_factory=list)


@router.post("/logistics/eoq")
async def calculate_eoq_endpoint(req: EoqRequest):
    res = logistics_inventory_service.calculate_eoq(
        annual_demand=req.annual_demand,
        order_cost=req.order_cost,
        holding_cost=req.holding_cost,
        unit_cost=req.unit_cost
    )
    return {"ok": True, "eoq": res}


@router.post("/logistics/rop")
async def calculate_rop_endpoint(req: RopRequest):
    res = logistics_inventory_service.calculate_rop(
        daily_demand=req.daily_demand,
        lead_time_days=req.lead_time_days,
        service_level_pct=req.service_level_pct,
        std_dev_daily_demand=req.std_dev_daily_demand
    )
    return {"ok": True, "rop": res}


@router.post("/logistics/abc")
async def calculate_abc_endpoint(req: AbcClassificationRequest):
    res = logistics_inventory_service.classify_abc(items=req.items)
    return {"ok": True, "abc": res}


# ─── NEGOCIACIÓN ESTRATÉGICA (MODELO HARVARD: ZOPA & BATNA) ───
class NegotiationRequest(BaseModel):
    buyer_reservation_price: float = Field(..., gt=0)
    seller_reservation_price: float = Field(..., gt=0)
    buyer_target_price: Optional[float] = None
    seller_target_price: Optional[float] = None
    buyer_batna: Optional[str] = None
    seller_batna: Optional[str] = None
    currency: str = Field(default="COP")


@router.post("/negotiation/eval")
async def evaluate_negotiation_endpoint(req: NegotiationRequest):
    res = negotiation_engine_service.evaluate_negotiation(
        buyer_reservation_price=req.buyer_reservation_price,
        seller_reservation_price=req.seller_reservation_price,
        buyer_target_price=req.buyer_target_price,
        seller_target_price=req.seller_target_price,
        buyer_batna=req.buyer_batna,
        seller_batna=req.seller_batna,
        currency=req.currency
    )
    return {"ok": True, "negotiation": res}


# ─── AUDITORÍA TRIBUTARIA DIAN & RÉGIMEN SIMPLE ───
class RstCompareRequest(BaseModel):
    gross_annual_income: float = Field(..., gt=0)
    deductible_expenses: float = Field(..., ge=0)
    activity_type: str = Field(default="servicios_profesionales")


class RentaCheckRequest(BaseModel):
    patrimonio_bruto: float = Field(default=0.0)
    ingresos_brutos: float = Field(default=0.0)
    consumos_tarjeta: float = Field(default=0.0)
    compras_totales: float = Field(default=0.0)
    consignaciones_bancarias: float = Field(default=0.0)


@router.post("/tax/rst-compare")
async def compare_rst_endpoint(req: RstCompareRequest):
    res = dian_tax_service.simulate_rst_vs_ordinario(
        gross_annual_income=req.gross_annual_income,
        deductible_expenses=req.deductible_expenses,
        activity_type=req.activity_type
    )
    return {"ok": True, "simulation": res}


@router.post("/tax/renta-check")
async def check_renta_endpoint(req: RentaCheckRequest):
    res = dian_tax_service.check_renta_obligation(
        patrimonio_bruto=req.patrimonio_bruto,
        ingresos_brutos=req.ingresos_brutos,
        consumos_tarjeta=req.consumos_tarjeta,
        compras_totales=req.compras_totales,
        consignaciones_bancarias=req.consignaciones_bancarias
    )
    return {"ok": True, "audit": res}


@router.get("/tax/calendar")
async def get_tax_calendar_endpoint(nit: str = Query(default="12345678")):
    return dian_tax_service.get_tax_deadlines(nit_or_cedula=nit)


# ─── BALANCED SCORECARD & OKRS CORPORATIVOS ───
class OkrUpdateRequest(BaseModel):
    kr_id: str = Field(...)
    value: float = Field(...)


@router.get("/okrs/dashboard")
async def get_okrs_dashboard_endpoint():
    return bsc_okrs_service.get_dashboard()


@router.post("/okrs/update")
async def update_okr_progress_endpoint(req: OkrUpdateRequest):
    ok = bsc_okrs_service.update_kr_progress(req.kr_id, req.value)
    return {"ok": ok, "kr_id": req.kr_id, "new_value": req.value}


# ─── LIQUIDACIÓN Y PAGO DE IMPUESTOS DIAN (FORMULARIO 490 & PSE) ───
class TaxSettleRequest(BaseModel):
    concept: str = Field(default="retefuente")
    year: int = Field(default=2026)
    period: str = Field(default="01")
    nit: str = Field(default="901.884.221-3")
    amount: float = Field(..., gt=0)
    due_date: Optional[str] = None
    payment_date: Optional[str] = None


class PsePaymentRequest(BaseModel):
    receipt_id: str = Field(...)
    bank_name: str = Field(default="Bancolombia")


@router.post("/tax-payment/settle")
async def settle_tax_endpoint(req: TaxSettleRequest):
    res = tax_payment_service.settle_form_490(
        concept_key=req.concept,
        tax_year=req.year,
        period=req.period,
        nit=req.nit,
        base_tax_amount=req.amount,
        due_date_str=req.due_date,
        payment_date_str=req.payment_date
    )
    return {"ok": True, "settlement": res}


@router.post("/tax-payment/pse")
async def create_pse_payment_endpoint(req: PsePaymentRequest):
    # Retrieve or build intent
    settlement = tax_payment_service.settle_form_490(
        concept_key="retefuente",
        tax_year=2026,
        period="01",
        nit="901.884.221-3",
        base_tax_amount=1500000.0
    )
    settlement["receipt_id"] = req.receipt_id
    intent = tax_payment_service.generate_pse_intent(settlement, bank_name=req.bank_name)
    tax_payment_service.confirm_payment(settlement, req.bank_name, intent["cus_code"])
    return {"ok": True, "intent": intent}


@router.get("/tax-payment/history")
async def get_tax_history_endpoint():
    return tax_payment_service.get_payment_history()


# ─── VALUACIÓN FINANCIERA DE EMPRESAS (DCF & MÚLTIPLOS) ───
class DcfValuationRequest(BaseModel):
    cash_flows: List[float] = Field(...)
    wacc: float = Field(default=0.12, ge=0.01, le=1.0)
    terminal_growth_g: float = Field(default=0.03, ge=0.0, le=0.15)
    cash: float = Field(default=0.0, ge=0.0)
    debt: float = Field(default=0.0, ge=0.0)
    currency: str = Field(default="COP")


class MultiplesValuationRequest(BaseModel):
    ebitda: float = Field(..., ge=0)
    annual_revenue: float = Field(..., ge=0)
    industry: str = Field(default="tech_saas")
    currency: str = Field(default="COP")


@router.post("/valuation/dcf")
async def valuation_dcf_endpoint(req: DcfValuationRequest):
    res = business_valuation_service.valuation_dcf(
        projected_flows=req.cash_flows,
        wacc_discount_rate=req.wacc,
        terminal_growth_g=req.terminal_growth_g,
        cash_balance=req.cash,
        total_debt=req.debt,
        currency=req.currency
    )
    return {"ok": True, "valuation": res}


@router.post("/valuation/multiples")
async def valuation_multiples_endpoint(req: MultiplesValuationRequest):
    res = business_valuation_service.valuation_multiples(
        ebitda=req.ebitda,
        annual_revenue=req.annual_revenue,
        industry_key=req.industry,
        currency=req.currency
    )
    return {"ok": True, "valuation": res}


# ─── OPTIMIZACIÓN DE RUTAS & FLETES COLOMBIA ───
class FreightRouteRequest(BaseModel):
    route: str = Field(default="palmira_cali")
    vehicle: str = Field(default="turbo_4_ton")
    distance_km: Optional[float] = None
    fuel_price: float = Field(default=16500.0)
    cargo_weight: Optional[float] = None


@router.post("/fleet/freight")
async def calculate_freight_endpoint(req: FreightRouteRequest):
    res = fleet_routes_service.calculate_freight(
        route_key=req.route,
        vehicle_key=req.vehicle,
        custom_distance_km=req.distance_km,
        fuel_price_gallon=req.fuel_price,
        cargo_weight_tons=req.cargo_weight
    )
    return {"ok": True, "freight": res}


# ─── TELEMETRÍA BIOCOGNITIVA & HÁBITOS CEO ───
class BiohabitsLogRequest(BaseModel):
    sleep_hours: float = Field(default=7.5, ge=0.0, le=24.0)
    water_glasses: int = Field(default=8, ge=0, le=30)
    deep_work_hours: float = Field(default=4.0, ge=0.0, le=24.0)
    energy_rating: int = Field(default=8, ge=1, le=10)
    chronotype: str = Field(default="matutino_alondra")


@router.post("/biohabits/eval")
async def evaluate_biohabits_endpoint(req: BiohabitsLogRequest):
    res = biocognitive_habits_service.evaluate_habits(
        sleep_hours=req.sleep_hours,
        water_glasses=req.water_glasses,
        deep_work_hours=req.deep_work_hours,
        energy_rating=req.energy_rating,
        chronotype=req.chronotype
    )
    return {"ok": True, "biocognitive": res}


@router.get("/biohabits/status")
async def get_biohabits_status_endpoint():
    return biocognitive_habits_service.get_latest_status()


# ─── TERMINAL BURSÁTIL & TRADING CUANTITATIVO ───
class StockTradingRequest(BaseModel):
    ticker: str = Field(default="ECOPETROL")
    current_price: float = Field(..., gt=0)
    rsi: float = Field(default=48.0, ge=0.0, le=100.0)
    macd_signal: str = Field(default="bullish_cross")
    ema_50: float = Field(default=0.0)
    ema_200: float = Field(default=0.0)
    atr: float = Field(default=0.0)
    total_trading_capital: float = Field(default=10000000.0, gt=0)
    currency: str = Field(default="COP")


@router.post("/stock-trading/analyze")
async def analyze_stock_trading_endpoint(req: StockTradingRequest):
    res = stock_trading_service.analyze_trading_signal(
        ticker=req.ticker,
        current_price=req.current_price,
        rsi=req.rsi,
        macd_signal=req.macd_signal,
        ema_50=req.ema_50,
        ema_200=req.ema_200,
        atr=req.atr,
        total_trading_capital=req.total_trading_capital,
        currency=req.currency
    )
    return {"ok": True, "analysis": res}


# ─── RADAR DE ACCIONES CON DIVIDENDOS & PRESUPUESTO AJUSTADO ───
class DividendScreenRequest(BaseModel):
    budget: float = Field(..., gt=0)
    market: str = Field(default="BVC")
    min_yield_pct: float = Field(default=5.0)
    reinvest_dividends: bool = Field(default=True)
    projection_years: int = Field(default=5, ge=1, le=10)


@router.post("/dividends/screen")
async def screen_dividends_endpoint(req: DividendScreenRequest):
    res = dividend_screener_service.screen_dividend_stocks(
        budget=req.budget,
        market=req.market,
        min_yield_pct=req.min_yield_pct,
        reinvest_dividends=req.reinvest_dividends,
        projection_years=req.projection_years
    )
    return {"ok": True, "screening": res}


@router.get("/dividends/catalog")
async def get_dividends_catalog_endpoint(market: Optional[str] = Query(None)):
    return {"ok": True, "catalog": dividend_screener_service.list_available_stocks(market=market)}


# ─── CONCILIACIÓN BANCARIA & AUDITORÍA GMF (4x1000) ───
class BankReconciliationRequest(BaseModel):
    bank_statement_balance: float = Field(...)
    general_ledger_balance: float = Field(...)
    deposits_in_transit: float = Field(default=0.0, ge=0.0)
    outstanding_checks: float = Field(default=0.0, ge=0.0)
    bank_charges_and_fees: float = Field(default=0.0, ge=0.0)
    unrecorded_bank_credits: float = Field(default=0.0, ge=0.0)
    unrecorded_bank_debits: float = Field(default=0.0, ge=0.0)
    total_monthly_debits_cop: float = Field(default=0.0, ge=0.0)
    is_account_gmf_exempt: bool = Field(default=False)
    bank_name: str = Field(default="Bancolombia")
    currency: str = Field(default="COP")


@router.post("/reconciliation/audit")
async def audit_reconciliation_endpoint(req: BankReconciliationRequest):
    res = bank_reconciliation_service.reconcile_statement(
        bank_statement_balance=req.bank_statement_balance,
        general_ledger_balance=req.general_ledger_balance,
        deposits_in_transit=req.deposits_in_transit,
        outstanding_checks=req.outstanding_checks,
        bank_charges_and_fees=req.bank_charges_and_fees,
        unrecorded_bank_credits=req.unrecorded_bank_credits,
        unrecorded_bank_debits=req.unrecorded_bank_debits,
        total_monthly_debits_cop=req.total_monthly_debits_cop,
        is_account_gmf_exempt=req.is_account_gmf_exempt,
        bank_name=req.bank_name,
        currency=req.currency
    )
    return {"ok": True, "reconciliation": res}


# ─── SIMULACIÓN ESTOCÁSTICA MONTE CARLO & STRESS TESTING ───
class MonteCarloRequest(BaseModel):
    project_name: str = Field(default="Proyecto Estratégico")
    initial_investment: float = Field(..., gt=0)
    mean_annual_revenue: float = Field(..., gt=0)
    std_annual_revenue: float = Field(default=5000000.0, ge=0)
    fixed_operating_costs: float = Field(default=10000000.0, ge=0)
    variable_costs_ratio: float = Field(default=0.25, ge=0.0, le=0.95)
    discount_rate_wacc: float = Field(default=0.12, ge=0.001, le=1.0)
    project_years: int = Field(default=5, ge=1, le=20)
    simulations_count: int = Field(default=5000, ge=500, le=20000)
    currency: str = Field(default="COP")


@router.post("/monte-carlo/simulate")
async def simulate_monte_carlo_endpoint(req: MonteCarloRequest):
    res = monte_carlo_service.simulate_project_capital(
        project_name=req.project_name,
        initial_investment=req.initial_investment,
        mean_annual_revenue=req.mean_annual_revenue,
        std_annual_revenue=req.std_annual_revenue,
        fixed_operating_costs=req.fixed_operating_costs,
        variable_costs_ratio=req.variable_costs_ratio,
        discount_rate_wacc=req.discount_rate_wacc,
        project_years=req.project_years,
        simulations_count=req.simulations_count,
        currency=req.currency
    )
    return {"ok": True, "simulation": res}


# ─── ESTRATEGIA DE PRECIOS & ELASTICIDAD DE DEMANDA ───
class PricingElasticityRequest(BaseModel):
    product_name: str = Field(default="Producto / Servicio")
    current_price: float = Field(..., gt=0)
    unit_marginal_cost: float = Field(..., ge=0)
    current_monthly_units: float = Field(default=1000.0, gt=0)
    price_elasticity: Optional[float] = None
    test_price: Optional[float] = None
    test_volume: Optional[float] = None
    currency: str = Field(default="COP")


@router.post("/pricing/elasticity")
async def evaluate_pricing_endpoint(req: PricingElasticityRequest):
    res = pricing_elasticity_service.evaluate_pricing_strategy(
        product_name=req.product_name,
        current_price=req.current_price,
        unit_marginal_cost=req.unit_marginal_cost,
        current_monthly_units=req.current_monthly_units,
        price_elasticity=req.price_elasticity,
        test_price=req.test_price,
        test_volume=req.test_volume,
        currency=req.currency
    )
    return {"ok": True, "pricing": res}


# ─── SIMULADOR DE CRÉDITOS & OPTIMIZACIÓN DE DEUDA ───
class CreditAmortizationRequest(BaseModel):
    loan_name: str = Field(default="Crédito Comercial / Libre Inversión")
    principal_amount: float = Field(..., gt=0)
    annual_interest_rate_ea_pct: float = Field(..., gt=0)
    term_months: int = Field(default=36, ge=1, le=360)
    amortization_system: str = Field(default="french")
    extra_monthly_prepayment: float = Field(default=0.0, ge=0)
    prepayment_strategy: str = Field(default="reduce_term")
    currency: str = Field(default="COP")


@router.post("/credit/amortization")
async def calculate_credit_endpoint(req: CreditAmortizationRequest):
    res = credit_amortization_service.calculate_amortization(
        loan_name=req.loan_name,
        principal_amount=req.principal_amount,
        annual_interest_rate_ea_pct=req.annual_interest_rate_ea_pct,
        term_months=req.term_months,
        amortization_system=req.amortization_system,
        extra_monthly_prepayment=req.extra_monthly_prepayment,
        prepayment_strategy=req.prepayment_strategy,
        currency=req.currency
    )
    return {"ok": True, "amortization": res}

# ─── MODELO DE NEGOCIO CANVAS & MATRIZ ANSOFF ───
class BusinessCanvasAnsoffRequest(BaseModel):
    project_name: str = Field(..., description="Nombre del proyecto o empresa")
    industry: str = Field(default="Servicios / Tecnología / Comercio")
    value_proposition: str = Field(default="")
    customer_segments: str = Field(default="")
    channels: str = Field(default="")
    customer_relationships: str = Field(default="")
    revenue_streams: str = Field(default="")
    key_resources: str = Field(default="")
    key_activities: str = Field(default="")
    key_partners: str = Field(default="")
    cost_structure: str = Field(default="")
    ansoff_quadrant: str = Field(default="market_penetration")
    investment_budget: float = Field(default=30000000.0, ge=0)
    currency: str = Field(default="COP")


@router.post("/business/canvas-ansoff")
async def evaluate_canvas_endpoint(req: BusinessCanvasAnsoffRequest):
    res = business_canvas_ansoff_service.evaluate_canvas_and_ansoff(
        project_name=req.project_name,
        industry=req.industry,
        value_proposition=req.value_proposition,
        customer_segments=req.customer_segments,
        channels=req.channels,
        customer_relationships=req.customer_relationships,
        revenue_streams=req.revenue_streams,
        key_resources=req.key_resources,
        key_activities=req.key_activities,
        key_partners=req.key_partners,
        cost_structure=req.cost_structure,
        ansoff_quadrant=req.ansoff_quadrant,
        investment_budget=req.investment_budget,
        currency=req.currency
    )
    return {"ok": True, "canvas_ansoff": res}


# ─── AUDITORÍA DE CUMPLIMIENTO SAGRILAFT & PTEE ───
class SagrilaftComplianceRequest(BaseModel):
    company_name: str = Field(..., description="Razón social de la compañía")
    annual_revenue_smmlv: float = Field(..., ge=0)
    total_assets_smmlv: float = Field(..., ge=0)
    sector: str = Field(default="servicios")
    has_compliance_officer: bool = Field(default=True)
    due_diligence_level: str = Field(default="ordinaria")
    pep_involvement: bool = Field(default=False)
    cash_intensive_pct: float = Field(default=5.0, ge=0, le=100)
    has_whistleblower_channel: bool = Field(default=True)
    international_operations: bool = Field(default=False)


@router.post("/compliance/sagrilaft")
async def audit_sagrilaft_endpoint(req: SagrilaftComplianceRequest):
    res = sagrilaft_compliance_service.audit_compliance(
        company_name=req.company_name,
        annual_revenue_smmlv=req.annual_revenue_smmlv,
        total_assets_smmlv=req.total_assets_smmlv,
        sector=req.sector,
        has_compliance_officer=req.has_compliance_officer,
        due_diligence_level=req.due_diligence_level,
        pep_involvement=req.pep_involvement,
        cash_intensive_pct=req.cash_intensive_pct,
        has_whistleblower_channel=req.has_whistleblower_channel,
        international_operations=req.international_operations
    )
    return {"ok": True, "sagrilaft": res}

# ─── INTELIGENCIA PREDICTIVA & ANTICIPACIÓN 3 PASOS ADELANTE ───
class PredictiveAnticipateRequest(BaseModel):
    context: Optional[str] = None


@router.get("/predictive/anticipate")
async def get_predictive_plan_endpoint(context: Optional[str] = Query(None)):
    res = predictive_intelligence_service.get_anticipatory_plan(context=context)
    return {"ok": True, "anticipation": res}


@router.post("/predictive/anticipate")
async def post_predictive_plan_endpoint(req: PredictiveAnticipateRequest):
    res = predictive_intelligence_service.get_anticipatory_plan(context=req.context)
    return {"ok": True, "anticipation": res}

