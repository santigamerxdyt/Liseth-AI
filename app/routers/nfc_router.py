"""
NFC & Contactless Payment Router for JARVIS / Liseth.
Provides API endpoints for Web NFC interaction, contactless payment generation,
vCard digital business card beaming, electronic invoices, currency conversion, and proximity unlock.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.nfc_service import nfc_service
from app.services.invoice_service import invoice_service

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


class InvoiceCreateRequest(BaseModel):
    client_name: str = Field(..., description="Nombre o razón social del cliente")
    client_id: str = Field(default="222222222222", description="Documento o NIT del cliente")
    items: Optional[List[Dict[str, Any]]] = Field(default=None, description="Lista de ítems facturados")
    amount: Optional[float] = Field(default=None, description="Monto total rápido si no se detallan ítems")
    concept: Optional[str] = Field(default="Servicios Profesionales de Consultoría", description="Concepto general")
    tax_rate: float = Field(default=0.19, description="Tasa de IVA (0.19 para 19%)")
    retefuente_rate: float = Field(default=0.0, description="Tasa de Retención en la Fuente")
    currency: str = Field(default="COP", description="Moneda de facturación")
    payment_method: str = Field(default="Bre-B Contactless", description="Método de pago")
    nfc_tx_id: Optional[str] = Field(default=None, description="ID de transacción NFC vinculada")


class BadgeVerifyRequest(BaseModel):
    badge_uid: str = Field(..., description="UID del tag NFC o llave de seguridad")


class BadgeEnrollRequest(BaseModel):
    badge_uid: str = Field(..., description="UID del tag NFC")
    label: str = Field(default="Credencial de Santiago", description="Etiqueta descriptiva")
    secret: Optional[str] = Field(default=None, description="Secreto opcional")


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


# ─── ENDPOINTS: FACTURACIÓN ELECTRÓNICA & RECIBOS ───
@router.post("/invoice")
async def create_invoice(req: InvoiceCreateRequest):
    """Generates a pro-forma electronic invoice with CUFE hash."""
    items = req.items
    if not items and req.amount:
        items = [{
            "description": req.concept or "Servicios Profesionales",
            "quantity": 1,
            "unit_price": req.amount
        }]

    inv = invoice_service.generate_invoice(
        client_name=req.client_name,
        client_id=req.client_id,
        items=items,
        tax_rate=req.tax_rate,
        retefuente_rate=req.retefuente_rate,
        currency=req.currency,
        payment_method=req.payment_method,
        nfc_tx_id=req.nfc_tx_id
    )
    return {"ok": True, "invoice": inv}


@router.get("/invoices")
async def list_invoices(limit: int = Query(default=20, ge=1, le=100)):
    """Lists recent electronic pro-forma invoices."""
    items = invoice_service.get_invoices(limit=limit)
    return {"ok": True, "invoices": items, "count": len(items)}


# ─── ENDPOINTS: DIVISAS & CONVERSIÓN CRIPTO ───
@router.get("/convert")
async def convert_currency_endpoint(
    amount: float = Query(default=1.0, gt=0),
    from_curr: str = Query(default="USD"),
    to_curr: str = Query(default="COP")
):
    """Converts amounts between COP, USD, EUR, USDT, BTC, and ETH."""
    res = nfc_service.convert_currency(amount, from_curr=from_curr, to_curr=to_curr)
    return {"ok": True, "conversion": res}


# ─── ENDPOINTS: DESBLOQUEO POR PROXIMIDAD (STARK KEY) ───
@router.post("/verify-badge")
async def verify_badge_endpoint(req: BadgeVerifyRequest):
    """Verifies if an NFC tag is an authorized security key for proximity unlock."""
    res = nfc_service.verify_security_badge(req.badge_uid)
    return {"ok": True, "result": res}


@router.post("/enroll-badge")
async def enroll_badge_endpoint(req: BadgeEnrollRequest):
    """Enrolls an NFC tag as an authorized proximity key."""
    res = nfc_service.enroll_security_badge(req.badge_uid, label=req.label, secret=req.secret)
    return {"ok": True, "badge": res}
