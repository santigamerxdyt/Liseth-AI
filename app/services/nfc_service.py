"""
NFC CORE ENGINE & Contactless Ecosystem Service for Liseth AI / JARVIS.
Centralizes universal NFC capabilities, hardware & platform capability detection,
NDEF read/write/validation, Smart Business Cards, dynamic links, P2P file exchange,
contactless payments, commercial merchant tags, cryptographic challenge security,
and AI NFC triggers with scoped contextual memory.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import secrets
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("jarvis.nfc_core_engine")


class NFCCoreEngine:
    """
    NFC CORE ENGINE: Centralized Near Field Communication & Contactless Engine.
    Provides hardware detection, NDEF parsing/generation, dynamic link redirection,
    AI triggers, secure file transfer handshakes, and tokenized payments.
    """

    SUPPORTED_PROTOCOLS = [
        "NFC Forum Type 2/4/5",
        "NFC Forum Type 2 (NTAG213 / NTAG215 / NTAG216)",
        "NFC Forum Type 4 (MIFARE DESFire / ISO 14443-A/B)",
        "NFC Forum Type 5 (ICODE / ISO 15693)",
        "MIFARE Classic 1K / 4K",
        "NDEF (NFC Data Exchange Format)",
        "W3C Web NFC API (NDEFReader / NDEFWriter)",
        "EMV Contactless Tokenization (ISO/IEC 7816)",
    ]

    RATES_TO_COP = {
        "COP": 1.0,
        "USD": 4150.0,
        "EUR": 4520.0,
        "USDT": 4155.0,
        "BTC": 278000000.0,
        "ETH": 10800000.0,
    }

    TAG_CAPACITIES = {
        "NTAG213": 144,
        "NTAG215": 504,
        "NTAG216": 888,
        "MIFARE_1K": 752,
        "DESFIRE_EV2": 4096,
        "DEFAULT": 504,
    }

    def __init__(self):
        self._memory_ledger: List[Dict[str, Any]] = []
        self._registered_tags: Dict[str, Dict[str, Any]] = {
            "ntag_stark_01": {
                "id": "ntag_stark_01",
                "uid": "04:STARK:KEY:01",
                "name": "Llave Maestra Stark (Santiago)",
                "category": "security_key",
                "action_type": "workspace_unlock",
                "action_payload": {"permissions": ["unlock_liseth", "sign_payment", "elevate_admin"]},
                "status": "active",
                "tag_type": "NFC Forum Type 4 (DESFire)",
                "memory_capacity_bytes": 4096,
                "is_locked": True,
                "secret_hash": hashlib.sha256(b"04:STARK:KEY:01:STARK_MASTER_2026").hexdigest(),
                "tap_count": 0,
                "last_tapped_at": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        }
        self._dynamic_links: Dict[str, Dict[str, Any]] = {
            "santiago-card": {
                "id": "nlnk_card_01",
                "short_code": "santiago-card",
                "title": "Tarjeta Profesional Santiago Huérfano López",
                "destination_url": "https://liseth.ai/profile/santiago",
                "destination_type": "profile",
                "clicks_count": 0,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            "checkout-starter": {
                "id": "nlnk_chk_01",
                "short_code": "checkout-starter",
                "title": "Checkout Plan Starter Liseth AI",
                "destination_url": "https://liseth.ai/checkout?plan=STARTER",
                "destination_type": "checkout",
                "clicks_count": 0,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        }
        self._file_transfers: Dict[str, Dict[str, Any]] = {}
        self._merchant_catalogs: Dict[str, Dict[str, Any]] = {
            "store_demo": {
                "business_name": "Liseth Tech Store & AI Lab",
                "category": "tecnologia",
                "catalog": [
                    {"id": "prod_1", "name": "Tarjeta NFC Inteligente Liseth (Física)", "price_cop": 45000, "in_stock": True},
                    {"id": "prod_2", "name": "Llavero NFC de Acceso Criptográfico", "price_cop": 35000, "in_stock": True},
                    {"id": "prod_3", "name": "Suscripción Nivel 1 Starter (Anual)", "price_cop": 399000, "in_stock": True},
                ],
                "loyalty_program": {"points_per_1k_cop": 1, "reward_threshold": 100},
                "coupons": [{"code": "NFCTAP10", "discount_pct": 10.0}],
            }
        }
        self._audit_logs: List[Dict[str, Any]] = []

    # =========================================================================
    # 1. HARDWARE & DEVICE CAPABILITY DETECTION
    # =========================================================================

    def detect_device_capabilities(
        self,
        user_agent: str = "",
        client_platform: str = "",
        has_web_nfc: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Analyzes hardware, OS, and browser capabilities to determine available NFC operations,
        limitations, and fallback channels (QR, Universal Links, HTTPS, Bluetooth).
        """
        ua = (user_agent or "").lower()
        plat = (client_platform or "").lower()

        is_android = "android" in ua or "android" in plat
        is_ios = any(i in ua for i in ["iphone", "ipad", "ipod"]) or "ios" in plat
        is_desktop = not is_android and not is_ios
        is_chrome_or_edge = any(b in ua for b in ["chrome", "crios", "edg", "edge"])

        # Determine Web NFC support (available natively in Chrome for Android 89+)
        web_nfc_available = bool(has_web_nfc) if has_web_nfc is not None else (is_android and is_chrome_or_edge)

        # Operational Matrix
        can_read_ndef = web_nfc_available or is_android
        can_write_ndef = web_nfc_available
        can_tap_to_pay_browser = True  # via payment deep links or W3C Payment Request
        can_emv_pos_tap = False  # requires certified PCI MPoC terminal or native SDK
        can_holographic_sim = True  # available on desktop/iOS as fallback

        # Platform limitations & fallback recommendations
        fallbacks: List[Dict[str, str]] = []
        limitations: List[str] = []

        if is_ios:
            limitations.append(
                "iOS Safari bloquea la API Web NFC (W3C NDEFReader). Requiere app nativa con CoreNFC o lectura nativa de iOS en segundo plano."
            )
            fallbacks.append({
                "channel": "dynamic_qr_code",
                "title": "Código QR Holográfico Dinámico",
                "description": "Permite escanear con la cámara de iOS para acceder al mismo enlace o vCard sin restricciones.",
            })
            fallbacks.append({
                "channel": "universal_deep_link",
                "title": "Enlace Universal HTTPS",
                "description": "Apertura directa mediante Universal Links de Apple.",
            })
        elif is_desktop:
            limitations.append(
                "Navegadores de escritorio no tienen antena NFC integrada de forma predeterminada."
            )
            fallbacks.append({
                "channel": "simulated_tap",
                "title": "Simulador Holográfico NFC",
                "description": "Emula el contacto y lectura de tags para pruebas y desarrollo de software.",
            })
            fallbacks.append({
                "channel": "external_reader_pc_sc",
                "title": "Lector USB/Bluetooth ACR122U",
                "description": "Integración compatible con lectores de tarjetas PC/SC de escritorio.",
            })
            fallbacks.append({
                "channel": "dynamic_qr_code",
                "title": "Código QR de Transferencia",
                "description": "Transmisión visual de datos hacia teléfonos móviles.",
            })
        else:
            fallbacks.append({
                "channel": "dynamic_qr_code",
                "title": "Código QR de Respaldo",
                "description": "Alternativa inmediata si el hardware NFC del usuario está desactivado.",
            })

        capability_score = 100 if web_nfc_available else (75 if is_ios else 80)

        return {
            "ok": True,
            "engine": "NFC CORE ENGINE v2.0 (Liseth AI)",
            "client_device": {
                "is_android": is_android,
                "is_ios": is_ios,
                "is_desktop": is_desktop,
                "platform": "Android" if is_android else ("iOS" if is_ios else "Desktop/PWA"),
            },
            "web_nfc_supported": web_nfc_available,
            "capabilities": {
                "ndef_read": can_read_ndef,
                "ndef_write": can_write_ndef,
                "ndef_lock": web_nfc_available,
                "smart_business_cards": True,
                "dynamic_links": True,
                "file_exchange_handshake": True,
                "contactless_checkout_links": can_tap_to_pay_browser,
                "terminal_pos_hooks": True,
                "simulated_holographic_tap": can_holographic_sim,
            },
            "supported_tag_types": self.SUPPORTED_PROTOCOLS,
            "capability_score_pct": capability_score,
            "limitations": limitations,
            "fallback_matrix": fallbacks,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # =========================================================================
    # 2. NDEF ENCODING, DECODING & VALIDATION
    # =========================================================================

    def validate_tag_write(
        self,
        records: List[Dict[str, Any]],
        tag_type: str = "NTAG215",
        is_locked: bool = False,
    ) -> Dict[str, Any]:
        """
        Validates payload size against tag memory capacity and verifies write lock permissions.
        """
        if is_locked:
            return {
                "valid": False,
                "error": "La etiqueta NFC está protegida contra escritura (Read-Only / Locked).",
                "can_write": False,
            }

        capacity = self.TAG_CAPACITIES.get(tag_type.upper(), self.TAG_CAPACITIES["DEFAULT"])
        # Estimate NDEF payload size in bytes
        raw_str = json.dumps(records, ensure_ascii=False)
        estimated_bytes = len(raw_str.encode("utf-8"))

        if estimated_bytes > capacity:
            return {
                "valid": False,
                "error": f"El tamaño del mensaje ({estimated_bytes} bytes) excede la capacidad de la etiqueta {tag_type} ({capacity} bytes).",
                "estimated_bytes": estimated_bytes,
                "capacity_bytes": capacity,
                "can_write": False,
            }

        return {
            "valid": True,
            "can_write": True,
            "estimated_bytes": estimated_bytes,
            "capacity_bytes": capacity,
            "remaining_bytes": capacity - estimated_bytes,
            "tag_type": tag_type,
        }

    def build_ndef_message(
        self,
        records_spec: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Constructs standardized W3C NDEFRecord structures.
        Supports: 'text', 'url', 'mime', 'smart_poster'.
        """
        ndef_records = []
        for spec in records_spec:
            rtype = spec.get("type", "text").lower()
            data = spec.get("data", "")

            if rtype == "text":
                ndef_records.append({
                    "recordType": "text",
                    "data": str(data),
                    "lang": spec.get("lang", "es"),
                })
            elif rtype in ("url", "uri"):
                ndef_records.append({
                    "recordType": "url",
                    "data": str(data),
                })
            elif rtype == "mime":
                ndef_records.append({
                    "recordType": "mime",
                    "mediaType": spec.get("mediaType", "application/json"),
                    "data": json.dumps(data) if isinstance(data, (dict, list)) else str(data),
                })
            elif rtype == "smart_poster":
                ndef_records.append({
                    "recordType": "smart_poster",
                    "title": spec.get("title", ""),
                    "url": spec.get("url", ""),
                    "action": spec.get("action", "open"),
                })

        return ndef_records

    # =========================================================================
    # 3. SMART BUSINESS CARDS (vCard 3.0/4.0 & Dynamic Public Profiles)
    # =========================================================================

    def create_vcard_payload(
        self,
        name: str = "Santiago",
        role: str = "Administrador de Empresas / CEO",
        organization: str = "Universidad Nacional de Colombia - Sede Palmira",
        phone: str = "+57 312 237 6474",
        email: str = "santigamerxdyt@gmail.com",
        url: str = "https://github.com/santigamerxdyt/Liseth-AI",
        notes: str = "Contacto asistido por Liseth AI 2.0 / JARVIS",
        socials: Optional[Dict[str, str]] = None,
        commercial_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Creates an enterprise-grade digital business card (vCard 3.0) with configurable fields.
        """
        socials = socials or {}
        social_lines = ""
        for net, handle in socials.items():
            social_lines += f"X-SOCIALPROFILE;TYPE={net.upper()}:{handle}\r\n"

        comm_note = ""
        if commercial_info:
            c_desc = commercial_info.get("company_description", "")
            c_nequi = commercial_info.get("nequi", "+57 312 237 6474")
            c_breb = commercial_info.get("bre_b", "@NEQUISAN243100")
            comm_note = f" Pagos: Nequi {c_nequi} / Bre-B {c_breb}. {c_desc}"

        full_note = (notes + comm_note).strip()

        vcard_text = (
            "BEGIN:VCARD\r\n"
            "VERSION:3.0\r\n"
            f"FN:{name}\r\n"
            f"N:{name};;;;\r\n"
            f"TITLE:{role}\r\n"
            f"ORG:{organization}\r\n"
            f"TEL;TYPE=CELL,VOICE:{phone}\r\n"
            f"EMAIL;TYPE=INTERNET,PREF:{email}\r\n"
            f"URL:{url}\r\n"
            f"{social_lines}"
            f"NOTE:{full_note}\r\n"
            "END:VCARD\r\n"
        )

        ndef_records = [
            {"recordType": "mime", "mediaType": "text/vcard", "data": vcard_text},
            {"recordType": "url", "data": url},
            {"recordType": "text", "data": f"{name} — {role} ({organization})"},
        ]

        tx_id = f"VCARD-{uuid.uuid4().hex[:6].upper()}"
        entry = {
            "id": tx_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "type": "vcard",
            "direction": "outgoing",
            "concept": f"Tarjeta Digital de {name}",
            "recipient": "Contacto Externo",
            "sender": name,
            "status": "ready_to_beam",
            "vcard_text": vcard_text,
            "ndef_records": ndef_records,
            "socials": socials,
            "commercial_info": commercial_info or {},
        }
        self._record_in_memory(entry)
        return entry

    # =========================================================================
    # 4. SMART LINKS (Dynamic Redirects Managed from Backend)
    # =========================================================================

    def create_dynamic_link(
        self,
        short_code: str,
        title: str,
        destination_url: str,
        destination_type: str = "url",
        tag_id: Optional[str] = None,
        owner_user_id: Optional[str] = None,
        requires_auth: bool = False,
    ) -> Dict[str, Any]:
        """
        Creates or updates a dynamic link associated with NFC tags.
        Can be updated at any time without having to reflash physical hardware!
        """
        clean_code = short_code.strip().lower()
        link_id = f"nlnk_{uuid.uuid4().hex[:10]}"

        link_entry = {
            "id": link_id,
            "short_code": clean_code,
            "tag_id": tag_id,
            "owner_user_id": owner_user_id,
            "title": title,
            "destination_url": destination_url,
            "destination_type": destination_type,
            "requires_auth": requires_auth,
            "clicks_count": 0,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._dynamic_links[clean_code] = link_entry
        return link_entry

    def resolve_dynamic_link(self, short_code: str) -> Optional[Dict[str, Any]]:
        """Resolves dynamic short link and increments click counter."""
        clean_code = short_code.strip().lower()
        link = self._dynamic_links.get(clean_code)
        if not link or not link.get("is_active"):
            return None
        link["clicks_count"] += 1
        link["updated_at"] = datetime.now(timezone.utc).isoformat()
        return link

    # =========================================================================
    # 5. P2P SECURE FILE EXCHANGE (NFC Discovery Handshake + HTTPS Transport)
    # =========================================================================

    def create_file_transfer_intent(
        self,
        sender_user_id: str,
        file_name: str,
        file_url: str,
        file_size_bytes: int = 0,
        file_mime_type: str = "application/octet-stream",
        requires_owner_consent: bool = True,
        ttl_minutes: int = 15,
    ) -> Dict[str, Any]:
        """
        Prepares a safe file exchange handshake:
        NFC beams an ephemeral token with 15-minute TTL; the actual payload
        is downloaded over secure HTTPS, never overloading NFC bandwidth.
        """
        transfer_id = f"nftrans_{uuid.uuid4().hex[:12]}"
        access_token = f"BEAM-{secrets.token_urlsafe(24)}"
        now_dt = datetime.now(timezone.utc)
        expires_at = datetime.fromtimestamp(now_dt.timestamp() + (ttl_minutes * 60), timezone.utc)

        entry = {
            "id": transfer_id,
            "sender_user_id": sender_user_id,
            "file_name": file_name,
            "file_url": file_url,
            "file_size_bytes": file_size_bytes,
            "file_mime_type": file_mime_type,
            "access_token": access_token,
            "requires_owner_consent": requires_owner_consent,
            "consent_granted": not requires_owner_consent,
            "status": "ready_to_beam",
            "expires_at": expires_at.isoformat(),
            "created_at": now_dt.isoformat(),
            "ndef_records": [
                {
                    "recordType": "mime",
                    "mediaType": "application/vnd.liseth.file_exchange+json",
                    "data": json.dumps({
                        "protocol": "LISETH_BEAM_FILE_V1",
                        "transfer_id": transfer_id,
                        "file_name": file_name,
                        "file_size": file_size_bytes,
                        "mime": file_mime_type,
                        "token": access_token,
                        "expires_at": expires_at.isoformat(),
                    }),
                },
                {
                    "recordType": "url",
                    "data": f"https://liseth.ai/nfc/files/download/{access_token}",
                },
            ],
        }
        self._file_transfers[access_token] = entry
        return entry

    def redeem_file_transfer(
        self,
        access_token: str,
        recipient_user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Validates file token, checks consent and expiration, and delivers download link."""
        entry = self._file_transfers.get(access_token)
        if not entry:
            return {"ok": False, "error": "Token de transferencia no encontrado o inválido."}

        # Check expiration
        exp_dt = datetime.fromisoformat(entry["expires_at"])
        if datetime.now(timezone.utc) > exp_dt:
            entry["status"] = "expired"
            return {"ok": False, "error": "El enlace de transferencia NFC ha expirado."}

        if entry.get("requires_owner_consent") and not entry.get("consent_granted"):
            return {
                "ok": False,
                "requires_consent": True,
                "message": "Se requiere confirmación explícita del propietario del archivo antes de transferirlo.",
            }

        entry["status"] = "downloaded"
        return {
            "ok": True,
            "file_name": entry["file_name"],
            "file_url": entry["file_url"],
            "file_size_bytes": entry["file_size_bytes"],
            "mime_type": entry["file_mime_type"],
            "sender_user_id": entry["sender_user_id"],
            "recipient_user_id": recipient_user_id,
        }

    # =========================================================================
    # 6. AI NFC TRIGGER & SMART AI TAGS
    # =========================================================================

    def create_ai_trigger_payload(
        self,
        agent_id: str = "jarvis_productivity",
        prompt_template: str = "Iniciar sesión de trabajo profundo",
        skill_code: Optional[str] = None,
        context_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Creates an NDEF payload that triggers a specific AI Agent or workflow on tap.
        """
        tx_id = f"AITAG-{uuid.uuid4().hex[:8].upper()}"
        payload = {
            "protocol": "LISETH_AI_NFC_TRIGGER_V1",
            "trigger_id": tx_id,
            "agent_id": agent_id,
            "prompt": prompt_template,
            "skill_code": skill_code,
            "context": context_metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        ndef_records = [
            {
                "recordType": "mime",
                "mediaType": "application/vnd.liseth.ai_trigger+json",
                "data": json.dumps(payload, ensure_ascii=False),
            },
            {
                "recordType": "url",
                "data": f"https://liseth.ai/ai/trigger?id={tx_id}&agent={agent_id}",
            },
            {
                "recordType": "text",
                "data": f"Asistente IA Liseth: {prompt_template} (Agente: {agent_id})",
            },
        ]

        return {
            "id": tx_id,
            "agent_id": agent_id,
            "prompt": prompt_template,
            "skill_code": skill_code,
            "payload": payload,
            "ndef_records": ndef_records,
            "status": "ready_to_beam",
        }

    # =========================================================================
    # 7. CONTACTLESS PAYMENTS & COMMERCE INFRASTRUCTURE
    # =========================================================================

    def convert_currency(self, amount: float, from_curr: str = "COP", to_curr: str = "USD") -> Dict[str, Any]:
        """Converts between COP, USD, EUR, USDT, BTC, and ETH."""
        f = from_curr.upper().strip()
        t = to_curr.upper().strip()
        f_rate = self.RATES_TO_COP.get(f, 1.0)
        t_rate = self.RATES_TO_COP.get(t, 1.0)

        amount_cop = amount * f_rate
        converted = amount_cop / t_rate

        return {
            "amount": amount,
            "from_currency": f,
            "to_currency": t,
            "converted_amount": round(converted, 8 if t in ("BTC", "ETH") else 2),
            "exchange_rate": round(f_rate / t_rate, 6),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def create_payment_payload(
        self,
        amount: float,
        currency: str = "COP",
        concept: str = "Pago de servicios",
        recipient: str = "Santiago",
        method: str = "bre_b",
        reference: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates a tokenized, verifiable contactless payment payload formatted for NDEF transmission.
        Strictly tokenized; never processes raw PAN or CVV card credentials.
        """
        tx_id = f"TX-NFC-{uuid.uuid4().hex[:8].upper()}"
        timestamp_iso = datetime.now(timezone.utc).isoformat()
        ref = reference or f"REF-{int(time.time())}"
        curr = currency.upper().strip()
        meth = method.lower().strip()

        sig_data = f"{tx_id}:{amount}:{curr}:{recipient}:{ref}"
        signature = hashlib.sha256(sig_data.encode("utf-8")).hexdigest()[:16]

        payment_data = {
            "protocol": "LISETH_NFC_PAY_V1",
            "tx_id": tx_id,
            "timestamp": timestamp_iso,
            "amount": float(amount),
            "currency": curr,
            "concept": concept,
            "recipient": recipient,
            "method": meth,
            "reference": ref,
            "signature": signature,
        }

        if meth in ("nequi", "nequi_pay"):
            deep_link = f"https://recarga.nequi.com.co/billetera?monto={int(amount)}&ref={ref}"
        elif meth in ("daviplata", "daviplata_pay"):
            deep_link = f"daviplata://pago?valor={int(amount)}&destino={recipient}&ref={ref}"
        elif meth in ("bre_b", "breb", "interoperable"):
            deep_link = f"breb://pay?m={int(amount)}&c={curr}&to={recipient}&ref={ref}&sig={signature}"
        elif meth in ("crypto", "usdt", "btc"):
            deep_link = f"ethereum:0x71C.../transfer?address={recipient}&uint256={amount}"
        else:
            deep_link = f"lisethpay://tx/{tx_id}?amount={amount}&currency={curr}&ref={ref}"

        ndef_records = [
            {
                "recordType": "mime",
                "mediaType": "application/vnd.liseth.payment+json",
                "data": json.dumps(payment_data, ensure_ascii=False),
            },
            {
                "recordType": "url",
                "data": deep_link,
            },
            {
                "recordType": "text",
                "data": f"Cobro Contactless Liseth: {curr} {amount:,.2f} - {concept} (Ref: {ref})",
            },
        ]

        tx_entry = {
            "id": tx_id,
            "created_at": timestamp_iso,
            "type": "payment",
            "direction": "outgoing",
            "amount": amount,
            "currency": curr,
            "recipient": recipient,
            "sender": "Santiago",
            "concept": concept,
            "method": meth,
            "status": "pending_tap",
            "payload": payment_data,
            "ndef_records": ndef_records,
            "deep_link": deep_link,
            "signature": signature,
        }
        self._record_in_memory(tx_entry)
        return tx_entry

    def get_merchant_catalog(self, store_id: str = "store_demo") -> Dict[str, Any]:
        """Returns commercial catalog, promotions, and loyalty info for a store."""
        return self._merchant_catalogs.get(store_id, self._merchant_catalogs["store_demo"])

    def record_merchant_checkin(self, store_id: str, user_id: str) -> Dict[str, Any]:
        """Voluntary loyalty visit check-in via NFC tap."""
        now_iso = datetime.now(timezone.utc).isoformat()
        return {
            "ok": True,
            "store_id": store_id,
            "user_id": user_id,
            "points_earned": 10,
            "message": "¡Visita voluntaria registrada! Has sumado 10 puntos de fidelización.",
            "timestamp": now_iso,
        }

    # =========================================================================
    # 8. SECURITY KEYS, HARDWARE CHALLENGE & TAG LIFECYCLE
    # =========================================================================

    def enroll_security_badge(
        self,
        badge_uid: str,
        label: str = "Credencial de Santiago",
        secret: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Enrolls an NFC tag UID as an authorized hardware key for proximity unlock."""
        uid_clean = badge_uid.upper().strip()
        secret_clean = secret or f"STARK-SEC-{uuid.uuid4().hex[:12]}"
        shash = hashlib.sha256(f"{uid_clean}:{secret_clean}".encode("utf-8")).hexdigest()

        badge_entry = {
            "id": uid_clean,
            "uid": uid_clean,
            "label": label,
            "name": label,
            "category": "security_key",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "secret_hash": shash,
            "is_active": True,
            "permissions": ["unlock_liseth", "sign_payment", "elevate_admin"],
        }
        self._registered_tags[uid_clean] = badge_entry
        return badge_entry

    def verify_security_badge(self, badge_uid: str) -> Dict[str, Any]:
        """Verifies if an NFC tag UID is an enrolled security key."""
        uid_clean = badge_uid.upper().strip()
        for t in self._registered_tags.values():
            if t.get("uid") == uid_clean and t.get("status") == "active":
                return {
                    "authorized": True,
                    "badge": t,
                    "message": f"Acceso concedido para {t.get('name', 'Santiago')}.",
                }
        return {
            "authorized": False,
            "message": f"Tag NFC {badge_uid} no está enrolado como llave de seguridad activa.",
        }

    def generate_tag_challenge(self, tag_id: str) -> Dict[str, Any]:
        """Generates an anti-replay cryptographic challenge nonce for sensitive tag operations."""
        tag = self._registered_tags.get(tag_id)
        if not tag:
            # Fallback by UID
            tag = next((t for t in self._registered_tags.values() if t.get("uid") == tag_id), None)
        if not tag:
            return {"ok": False, "error": "Tag no encontrado."}

        nonce = secrets.token_hex(16)
        tag["last_challenge"] = nonce
        return {
            "ok": True,
            "tag_id": tag["id"],
            "uid": tag["uid"],
            "nonce": nonce,
            "expires_in_seconds": 60,
        }

    def verify_tag_challenge(self, tag_id: str, client_response_hmac: str) -> Dict[str, Any]:
        """Validates that tag or device possesses the cryptographic secret using HMAC-SHA256."""
        tag = self._registered_tags.get(tag_id)
        if not tag:
            tag = next((t for t in self._registered_tags.values() if t.get("uid") == tag_id), None)
        if not tag:
            return {"ok": False, "error": "Tag no encontrado."}

        nonce = tag.get("last_challenge")
        if not nonce:
            return {"ok": False, "error": "No hay desafío activo para este tag."}

        secret = tag.get("secret_hash") or "DEFAULT_STARK_SECRET"
        expected = hmac.new(secret.encode("utf-8"), nonce.encode("utf-8"), hashlib.sha256).hexdigest()

        if hmac.compare_digest(expected, client_response_hmac):
            tag["last_challenge"] = None  # Consume challenge to prevent replay
            tag["tap_count"] = tag.get("tap_count", 0) + 1
            tag["last_tapped_at"] = datetime.now(timezone.utc).isoformat()
            return {"ok": True, "authenticated": True, "message": "Verificación criptográfica exitosa."}

        return {"ok": False, "authenticated": False, "error": "Firma criptográfica inválida (Posible clonación de tag)."}

    # =========================================================================
    # 9. INCOMING TAP PROCESSING & LEDGER
    # =========================================================================

    def process_incoming_tap(
        self,
        serial_number: Optional[str] = None,
        records: Optional[List[Dict[str, Any]]] = None,
        raw_text: Optional[str] = None,
        simulated: bool = False,
    ) -> Dict[str, Any]:
        """Processes an incoming physical or simulated NFC tap."""
        tx_id = f"TAP-{uuid.uuid4().hex[:8].upper()}"
        timestamp_iso = datetime.now(timezone.utc).isoformat()
        records = records or []

        parsed_type = "unknown"
        extracted_data: Dict[str, Any] = {}
        summary = "Etiqueta NFC leída correctamente."

        for rec in records:
            rtype = rec.get("recordType", "")
            data = rec.get("data", "")
            media_type = rec.get("mediaType", "")

            if media_type == "application/vnd.liseth.payment+json" or (isinstance(data, str) and "LISETH_NFC_PAY" in data):
                parsed_type = "payment"
                try:
                    pjson = json.loads(data) if isinstance(data, str) else data
                    extracted_data["payment"] = pjson
                    summary = f"Pago Contactless recibido: {pjson.get('currency', 'COP')} {pjson.get('amount', 0):,} ({pjson.get('concept', 'Sin concepto')})"
                except Exception:
                    pass

            elif media_type == "text/vcard" or (isinstance(data, str) and "BEGIN:VCARD" in data):
                parsed_type = "vcard"
                extracted_data["vcard"] = data
                summary = "Tarjeta de presentación digital (vCard) recibida."

            elif media_type == "application/vnd.liseth.ai_trigger+json":
                parsed_type = "ai_trigger"
                try:
                    pjson = json.loads(data) if isinstance(data, str) else data
                    extracted_data["ai_trigger"] = pjson
                    summary = f"Disparador IA detectado: Agente '{pjson.get('agent_id')}' con prompt '{pjson.get('prompt')}'"
                except Exception:
                    pass

            elif rtype == "url":
                if parsed_type == "unknown":
                    parsed_type = "url"
                extracted_data["url"] = data
                summary = f"Enlace dinámico recibido por NFC: {data}"

            elif rtype == "text":
                if parsed_type == "unknown":
                    parsed_type = "text"
                extracted_data["text"] = data
                summary = f"Texto recibido por NFC: {data[:60]}..."

        if raw_text and not extracted_data:
            parsed_type = "text"
            extracted_data["text"] = raw_text
            summary = f"Lectura NFC directa: {raw_text[:60]}"

        entry = {
            "id": tx_id,
            "created_at": timestamp_iso,
            "serial_number": serial_number or "NFC-TAG-SIMULATED",
            "type": parsed_type,
            "direction": "incoming",
            "status": "completed" if not simulated else "simulated",
            "summary": summary,
            "extracted_data": extracted_data,
            "records_count": len(records),
        }
        self._record_in_memory(entry)
        return entry

    def get_ledger(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns the most recent transactions from the ledger."""
        return list(reversed(self._memory_ledger[-limit:]))

    def clear_ledger(self) -> Dict[str, Any]:
        """Clears the transaction ledger."""
        count = len(self._memory_ledger)
        self._memory_ledger.clear()
        return {
            "ok": True,
            "message": f"Se limpiaron {count} registros del libro contable NFC.",
            "cleared_count": count,
        }

    def _record_in_memory(self, item: Dict[str, Any]) -> None:
        """Appends item to memory ledger, keeping up to 200 items."""
        self._memory_ledger.append(item)
        if len(self._memory_ledger) > 200:
            self._memory_ledger = self._memory_ledger[-200:]

    # =========================================================================
    # 10. STATUS & CREATOR NFC MANAGEMENT CENTER
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Returns the operational status and capabilities of the NFC Core Engine."""
        return {
            "engine": "Liseth NFC CORE ENGINE (v2.0 Universal)",
            "supported_protocols": self.SUPPORTED_PROTOCOLS,
            "payment_methods": [
                "Bre-B Interoperable (Colombia)",
                "Nequi / Daviplata Contactless Token",
                "Tokenized Card Tap (EMV / ISO 14443-A)",
                "Wompi / PSE Deep Links",
                "Crypto Contactless Beaming (USDT / BTC / ETH)",
            ],
            "beam_profiles": [
                "Tarjeta de Contacto Personal (vCard 3.0 / 4.0)",
                "Enlace Dinámico de Portafolio / Redes",
                "Disparador de Agente IA (Smart AI Tag)",
                "Intercambio Seguro de Archivos P2P",
                "Cobro Directo Contactless",
                "Llave Criptográfica de Acceso",
            ],
            "hardware_support": "Multiplataforma Universal: Web NFC nativo (Android), QR Dinámico & Universal Links (iOS), Lector PC/SC & Simulador Holográfico (Desktop)",
            "status": "ONLINE",
            "total_transactions": len(self._memory_ledger),
            "registered_tags_count": len(self._registered_tags),
            "dynamic_links_count": len(self._dynamic_links),
        }

    def format_status_report(self, st: Dict[str, Any]) -> str:
        """Formats the status report for Señor Santiago."""
        methods = "\n".join([f"  - {m}" for m in st.get("payment_methods", [])])
        profiles = "\n".join([f"  - {p}" for p in st.get("beam_profiles", [])])
        return (
            "### 📶 Ecosistema NFC CORE — Motor Universal de Comunicación Inalámbrica\n"
            f"- **Motor**: `{st.get('engine')}`\n"
            f"- **Estado**: `ONLINE` | **Hardware**: `{st.get('hardware_support')}`\n"
            f"- **Etiquetas Registradas**: `{st.get('registered_tags_count')}` | **Enlaces Dinámicos**: `{st.get('dynamic_links_count')}`\n\n"
            f"**Métodos de Pago Contactless Habilitados**:\n{methods}\n\n"
            f"**Perfiles de Operación y Transmisión**:\n{profiles}\n\n"
            "Listo para leer, escribir, emitir cobros, transferir tarjetas vCard o activar agentes de IA, señor Santiago."
        )

    def get_creator_dashboard(self) -> Dict[str, Any]:
        """Provides executive telemetry for CREATOR 'NFC Management Center'."""
        active_tags = sum(1 for t in self._registered_tags.values() if t.get("status") == "active")
        revoked_tags = sum(1 for t in self._registered_tags.values() if t.get("status") == "revoked")
        total_taps = sum(t.get("tap_count", 0) for t in self._registered_tags.values())

        return {
            "ok": True,
            "metrics": {
                "total_tags_registered": len(self._registered_tags),
                "active_tags": active_tags,
                "revoked_tags": revoked_tags,
                "total_taps_recorded": total_taps + len(self._memory_ledger),
                "dynamic_links_active": len(self._dynamic_links),
                "file_transfers_active": len(self._file_transfers),
                "merchants_enrolled": len(self._merchant_catalogs),
            },
            "tags": list(self._registered_tags.values()),
            "dynamic_links": list(self._dynamic_links.values()),
            "recent_ledger": self.get_ledger(limit=15),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global singleton instance & backwards-compatible class alias
nfc_service = NFCCoreEngine()
NFCService = NFCCoreEngine
