"""
NFC & Contactless Payment Router for JARVIS / Liseth.
Provides API endpoints for Web NFC interaction, contactless payment generation,
vCard digital business card beaming, and transaction ledger inspection.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.nfc_service import nfc_service

router = APIRouter(prefix="/api/nfc", tags=["nfc"])


class PaymentCreateRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Monto a cobrar")
    currency: str = Field(default="COP", description="Moneda (COP, USD, EUR)")
    concept: str = Field(default="Cobro por contacto", description="Concepto o descripción")
    recipient: str = Field(default="Santiago", description="Destinatario del pago")
    method: str = Field(default="bre_b", description="Método: bre_b, nequi, daviplata, card, crypto")
    reference: Optional[str] = Field(default=None, description="Referencia única opcional")


class VCardCreateRequest(BaseModel):
    name: str = Field(default="Santiago", description="Nombre completo")
    role: str = Field(default="Administrador de Empresas / CEO", description="Cargo o título")
    organization: str = Field(default="Universidad Nacional de Colombia - Sede Palmira", description="Empresa u organización")
    phone: str = Field(default="+57 300 000 0000", description="Teléfono celular")
    email: str = Field(default="santiago@unal.edu.co", description="Correo electrónico")
    url: str = Field(default="https://github.com/santigamerxdyt/Liseth-AI", description="Enlace web o portafolio")
    notes: Optional[str] = Field(default="Contacto asistido por Liseth AI 2.0", description="Notas adicionales")


class TapRecordRequest(BaseModel):
    serial_number: Optional[str] = Field(default=None, description="Número de serie del tag NFC")
    records: Optional[List[Dict[str, Any]]] = Field(default=[], description="Lista de registros NDEF leídos")
    raw_text: Optional[str] = Field(default=None, description="Texto plano si no es NDEF complejo")
    simulated: bool = Field(default=False, description="True si es una simulación de escritorio")


@router.get("/status")
async def get_nfc_status():
    """Returns capabilities and status of the Liseth NFC engine."""
    return nfc_service.get_status()


@router.post("/create-payment")
async def create_payment_payload(req: PaymentCreateRequest):
    """Generates an NDEF-ready contactless payment token."""
    res = nfc_service.create_payment_payload(
        amount=req.amount,
        currency=req.currency,
        concept=req.concept,
        recipient=req.recipient,
        method=req.method,
        reference=req.reference
    )
    return {"ok": True, "transaction": res}


@router.post("/create-vcard")
async def create_vcard_payload(req: VCardCreateRequest):
    """Generates an NDEF-ready vCard 3.0 payload for contact beaming."""
    res = nfc_service.create_vcard_payload(
        name=req.name,
        role=req.role,
        organization=req.organization,
        phone=req.phone,
        email=req.email,
        url=req.url,
        notes=req.notes or ""
    )
    return {"ok": True, "vcard": res}


@router.post("/record-tap")
async def record_nfc_tap(req: TapRecordRequest):
    """Registers an incoming NFC tag read event (physical or simulated)."""
    res = nfc_service.process_incoming_tap(
        serial_number=req.serial_number,
        records=req.records,
        raw_text=req.raw_text,
        simulated=req.simulated
    )
    return {"ok": True, "tap_result": res}


@router.get("/history")
async def get_nfc_history(limit: int = Query(default=20, ge=1, le=100)):
    """Returns the most recent contactless transactions."""
    items = nfc_service.get_ledger(limit=limit)
    return {"ok": True, "transactions": items, "count": len(items)}


@router.post("/clear-history")
async def clear_nfc_history():
    """Resets the NFC transaction ledger."""
    res = nfc_service.clear_ledger()
    return res
