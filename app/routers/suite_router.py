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


