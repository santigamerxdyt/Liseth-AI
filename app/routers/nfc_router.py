"""
NFC CORE Router for JARVIS / Liseth.
Provides API endpoints for Web NFC, device capability detection, NDEF validation,
Smart Business Cards, dynamic links, P2P file exchange, contactless payment generation,
electronic invoices, AI triggers, merchant loyalty, and CREATOR NFC Management Center.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header, HTTPException, Query, Request, Response
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
    phone: str = Field(default="+57 312 237 6474", description="Teléfono celular")
    email: str = Field(default="santigamerxdyt@gmail.com", description="Correo electrónico")
    url: str = Field(default="https://github.com/santigamerxdyt/Liseth-AI", description="Enlace web o portafolio")
    notes: Optional[str] = Field(default="Contacto asistido por Liseth AI 2.0 / JARVIS", description="Notas adicionales")
    socials: Optional[Dict[str, str]] = Field(default=None, description="Redes sociales {linkedin, twitter, github, etc.}")
    commercial_info: Optional[Dict[str, Any]] = Field(default=None, description="Datos de negocio y facturación")


class TapRecordRequest(BaseModel):
    serial_number: Optional[str] = Field(default=None, description="Número de serie del tag NFC")
    records: Optional[List[Dict[str, Any]]] = Field(default=[], description="Lista de registros NDEF leídos")
    raw_text: Optional[str] = Field(default=None, description="Texto plano si no es NDEF complejo")
    simulated: bool = Field(default=False, description="True si es una simulación de escritorio")


class ValidateWriteRequest(BaseModel):
    records: List[Dict[str, Any]] = Field(..., description="Registros NDEF a validar")
    tag_type: str = Field(default="NTAG215", description="Tipo de etiqueta (NTAG213, NTAG215, NTAG216, MIFARE_1K)")
    is_locked: bool = Field(default=False, description="Estado de bloqueo de la etiqueta")


class DynamicLinkRequest(BaseModel):
    short_code: str = Field(..., description="Código o slug corto para la etiqueta")
    title: str = Field(..., description="Título descriptivo del enlace")
    destination_url: str = Field(..., description="URL real a la que redirige")
    destination_type: str = Field(default="url", description="Tipo de destino (url, profile, agent, checkout)")
    requires_auth: bool = Field(default=False, description="Si requiere sesión activa")


class FileTransferIntentRequest(BaseModel):
    file_name: str = Field(..., description="Nombre del archivo a compartir")
    file_url: str = Field(..., description="URL segura de descarga del archivo")
    file_size_bytes: int = Field(default=0, description="Tamaño del archivo en bytes")
    file_mime_type: str = Field(default="application/octet-stream", description="Tipo MIME")
    requires_owner_consent: bool = Field(default=True, description="Si requiere autorización previa")
    ttl_minutes: int = Field(default=15, description="Minutos de vigencia del enlace NFC")


class AITriggerRequest(BaseModel):
    agent_id: str = Field(default="jarvis_productivity", description="Identificador del agente")
    prompt_template: str = Field(default="Iniciar sesión de trabajo profundo", description="Prompt a ejecutar")
    skill_code: Optional[str] = Field(default=None, description="Skill específica")
    context_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadatos de contexto autorizados")


class ChallengeVerifyRequest(BaseModel):
    tag_id: str = Field(..., description="ID o UID del tag")
    client_response_hmac: str = Field(..., description="HMAC-SHA256 calculado por el cliente")


class MerchantCheckinRequest(BaseModel):
    store_id: str = Field(default="store_demo", description="Identificador del comercio")
    user_id: str = Field(..., description="Identificador del cliente")


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


# =============================================================================
# 1. HARDWARE & CAPABILITY DETECTION
# =============================================================================

@router.get("/status")
async def get_nfc_status():
    """Returns capabilities and status of the Liseth NFC Core Engine."""
    return nfc_service.get_status()


@router.get("/capabilities")
async def get_device_capabilities(
    request: Request,
    has_web_nfc: Optional[bool] = Query(None),
    user_agent: Optional[str] = Header(None),
):
    """Detects client device capabilities, operational limits, and fallback channels."""
    ua = user_agent or request.headers.get("user-agent", "")
    return nfc_service.detect_device_capabilities(user_agent=ua, has_web_nfc=has_web_nfc)


@router.post("/validate-write")
async def validate_tag_write_endpoint(req: ValidateWriteRequest):
    """Validates if an NDEF message fits inside the tag's physical memory capacity."""
    return nfc_service.validate_tag_write(
        records=req.records,
        tag_type=req.tag_type,
        is_locked=req.is_locked,
    )


# =============================================================================
# 2. SMART BUSINESS CARDS & VCARD
# =============================================================================

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
        notes=req.notes or "",
        socials=req.socials,
        commercial_info=req.commercial_info,
    )
    return {"ok": True, "vcard": res}


# =============================================================================
# 3. SMART LINKS & DYNAMIC REDIRECTION
# =============================================================================

@router.post("/links")
async def create_dynamic_link_endpoint(req: DynamicLinkRequest):
    """Creates or updates a dynamic NFC short link manageable from backend."""
    link = nfc_service.create_dynamic_link(
        short_code=req.short_code,
        title=req.title,
        destination_url=req.destination_url,
        destination_type=req.destination_type,
        requires_auth=req.requires_auth,
    )
    return {"ok": True, "link": link}


@router.get("/l/{short_code}")
async def resolve_dynamic_link_endpoint(short_code: str):
    """Resolves dynamic link destination and increments tap counters."""
    link = nfc_service.resolve_dynamic_link(short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Enlace dinámico NFC no encontrado o inactivo.")
    return {"ok": True, "link": link}


# =============================================================================
# 4. P2P SECURE FILE EXCHANGE
# =============================================================================

@router.post("/files/intent")
async def create_file_transfer_intent_endpoint(req: FileTransferIntentRequest):
    """Prepares an NFC-initiated file exchange with a 15-minute expiring token."""
    res = nfc_service.create_file_transfer_intent(
        sender_user_id="santiago",
        file_name=req.file_name,
        file_url=req.file_url,
        file_size_bytes=req.file_size_bytes,
        file_mime_type=req.file_mime_type,
        requires_owner_consent=req.requires_owner_consent,
        ttl_minutes=req.ttl_minutes,
    )
    return {"ok": True, "file_transfer": res}


@router.get("/files/download/{token}")
async def redeem_file_transfer_endpoint(token: str):
    """Validates NFC token and returns file download URL."""
    res = nfc_service.redeem_file_transfer(token)
    if not res.get("ok"):
        raise HTTPException(status_code=400, detail=res.get("error", "Error en transferencia."))
    return res


# =============================================================================
# 5. AI NFC TRIGGER & SMART AI TAGS
# =============================================================================

@router.post("/ai-trigger")
async def create_ai_trigger_endpoint(req: AITriggerRequest):
    """Generates an NDEF payload to launch an AI agent or prompt on tap."""
    trigger = nfc_service.create_ai_trigger_payload(
        agent_id=req.agent_id,
        prompt_template=req.prompt_template,
        skill_code=req.skill_code,
        context_metadata=req.context_metadata,
    )
    return {"ok": True, "ai_trigger": trigger}


# =============================================================================
# 6. PAYMENTS & CONTACTLESS POS
# =============================================================================

@router.post("/create-payment")
async def create_payment_payload(req: PaymentCreateRequest):
    """Generates an NDEF-ready contactless payment token."""
    res = nfc_service.create_payment_payload(
        amount=req.amount,
        currency=req.currency,
        concept=req.concept,
        recipient=req.recipient,
        method=req.method,
        reference=req.reference,
    )
    return {"ok": True, "transaction": res}


@router.post("/record-tap")
async def record_nfc_tap(req: TapRecordRequest):
    """Registers an incoming NFC tag read event (physical or simulated)."""
    res = nfc_service.process_incoming_tap(
        serial_number=req.serial_number,
        records=req.records,
        raw_text=req.raw_text,
        simulated=req.simulated,
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


# =============================================================================
# 7. MERCHANT & COMMERCE NFC
# =============================================================================

@router.get("/merchant/catalog")
async def get_merchant_catalog_endpoint(store_id: str = Query("store_demo")):
    """Returns products, spec sheets, and promotions for store NFC tags."""
    return {"ok": True, "store": nfc_service.get_merchant_catalog(store_id)}


@router.post("/merchant/checkin")
async def merchant_checkin_endpoint(req: MerchantCheckinRequest):
    """Voluntary loyalty check-in via NFC tap."""
    return nfc_service.record_merchant_checkin(req.store_id, req.user_id)


# =============================================================================
# 8. SECURITY KEYS, PROXIMITY UNLOCK & CHALLENGE
# =============================================================================

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


@router.post("/security/challenge")
async def generate_tag_challenge_endpoint(payload: Dict[str, str]):
    """Generates an anti-replay challenge nonce for cryptographic verification."""
    tag_id = payload.get("tag_id") or payload.get("uid") or ""
    res = nfc_service.generate_tag_challenge(tag_id)
    if not res.get("ok"):
        raise HTTPException(status_code=404, detail=res.get("error", "Tag no encontrado."))
    return res


@router.post("/security/verify")
async def verify_tag_challenge_endpoint(req: ChallengeVerifyRequest):
    """Verifies the tag's HMAC response against the challenge nonce."""
    res = nfc_service.verify_tag_challenge(req.tag_id, req.client_response_hmac)
    if not res.get("ok"):
        raise HTTPException(status_code=401, detail=res.get("error", "Autenticación fallida."))
    return res


# =============================================================================
# 9. FACTURACIÓN ELECTRÓNICA & DIVISAS
# =============================================================================

@router.post("/invoice")
async def create_invoice(req: InvoiceCreateRequest):
    """Generates a pro-forma electronic invoice with CUFE hash."""
    items = req.items
    if not items and req.amount:
        items = [{
            "description": req.concept or "Servicios Profesionales",
            "quantity": 1,
            "unit_price": req.amount,
        }]

    inv = invoice_service.generate_invoice(
        client_name=req.client_name,
        client_id=req.client_id,
        items=items,
        tax_rate=req.tax_rate,
        retefuente_rate=req.retefuente_rate,
        currency=req.currency,
        payment_method=req.payment_method,
        nfc_tx_id=req.nfc_tx_id,
    )
    return {"ok": True, "invoice": inv}


@router.get("/invoices")
async def list_invoices(limit: int = Query(default=20, ge=1, le=100)):
    """Lists recent electronic pro-forma invoices."""
    items = invoice_service.get_invoices(limit=limit)
    return {"ok": True, "invoices": items, "count": len(items)}


@router.get("/convert")
async def convert_currency_endpoint(
    amount: float = Query(default=1.0, gt=0),
    from_curr: str = Query(default="USD"),
    to_curr: str = Query(default="COP"),
):
    """Converts amounts between COP, USD, EUR, USDT, BTC, and ETH."""
    res = nfc_service.convert_currency(amount, from_curr=from_curr, to_curr=to_curr)
    return {"ok": True, "conversion": res}


# =============================================================================
# 10. CREATOR NFC MANAGEMENT CENTER
# =============================================================================

@router.get("/admin/dashboard")
async def creator_nfc_dashboard_endpoint():
    """Returns telemetry and registered tag records for the CREATOR NFC Management Center."""
    return nfc_service.get_creator_dashboard()
