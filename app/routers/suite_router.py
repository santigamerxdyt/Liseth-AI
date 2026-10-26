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
