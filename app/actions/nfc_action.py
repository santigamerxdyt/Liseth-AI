"""
NFC & Contactless Payment Action for JARVIS / Liseth.
Entrypoint for NFC tag reading, writing, contactless payments, and transaction history.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from app.services.nfc_service import nfc_service

logger = logging.getLogger("jarvis.nfc_action")


def nfc_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    """
    Synchronous entrypoint for NFC & Contactless operations.
    Handles:
      - 'status': reports capabilities and hardware state
      - 'payment_request' / 'cobro': creates a tokenized contactless payment payload
      - 'beam_vcard' / 'tarjeta': creates digital contact card for NFC beaming
      - 'read_tag' / 'leer': processes a tag or simulated tap
      - 'history' / 'historial': returns recent contactless ledger entries
      - 'clear_history': resets the ledger
    """
    params = parameters or {}
    action = params.get("action", "status").lower().strip()

    try:
        if action in ["status", "estado", "info"]:
            st = nfc_service.get_status()
            return nfc_service.format_status_report(st)

        if action in ["payment_request", "cobro", "pago", "pay", "crear_cobro"]:
            amount = float(params.get("amount") or 0.0)
            currency = str(params.get("currency") or "COP").upper()
            concept = str(params.get("concept") or params.get("description") or "Cobro por contacto")
            recipient = str(params.get("recipient") or "Santiago")
            method = str(params.get("method") or "bre_b")

            if amount <= 0:
                return "Señor Santiago, por favor especifique un monto mayor a cero para el cobro contactless."

            res = nfc_service.create_payment_payload(
                amount=amount,
                currency=currency,
                concept=concept,
                recipient=recipient,
                method=method
            )
            return (
                f"### 💳 Solicitud de Cobro Contactless Generada\n"
                f"- **ID de Transacción**: `{res['id']}`\n"
                f"- **Monto**: `{res['currency']} ${res['amount']:,.2f}`\n"
                f"- **Concepto**: {res['concept']}\n"
                f"- **Destinatario**: {res['recipient']}\n"
                f"- **Método**: `{res['method'].upper()}`\n"
                f"- **Firma Criptográfica**: `{res['signature']}`\n"
                f"- **Deep Link de Pago**: `{res['deep_link']}`\n\n"
                f"Terminal de pago lista en pantalla. Acerque el teléfono o tarjeta NFC para completar la transacción."
            )

        if action in ["beam_vcard", "vcard", "tarjeta", "contacto", "compartir_contacto"]:
            name = str(params.get("name") or "Santiago")
            role = str(params.get("role") or "Administrador de Empresas / CEO")
            org = str(params.get("organization") or "Universidad Nacional de Colombia - Sede Palmira")
            phone = str(params.get("phone") or "+57 300 000 0000")
            email = str(params.get("email") or "santiago@unal.edu.co")
            url = str(params.get("url") or "https://github.com/santigamerxdyt/Liseth-AI")

            res = nfc_service.create_vcard_payload(
                name=name,
                role=role,
                organization=org,
                phone=phone,
                email=email,
                url=url
            )
            return (
                f"### 📇 Tarjeta de Contacto Digital (vCard) Lista para Transmitir (Beam)\n"
                f"- **Nombre**: {name}\n"
                f"- **Cargo**: {role}\n"
                f"- **Organización**: {org}\n"
                f"- **Enlace de Contacto**: {url}\n\n"
                f"Transmisor NFC activo. Acerque el dispositivo receptor para transferir su tarjeta al instante, señor Santiago."
            )

        if action in ["read_tag", "leer", "escanear", "tap", "simular_tap"]:
            text = params.get("text") or params.get("raw_text")
            records = params.get("records")
            simulated = bool(params.get("simulated", True))

            res = nfc_service.process_incoming_tap(
                raw_text=text,
                records=records,
                simulated=simulated
            )
            return (
                f"### 📶 Lectura de Contacto NFC Registrada\n"
                f"- **ID de Operación**: `{res['id']}`\n"
                f"- **Tipo de Carga**: `{res['type'].upper()}`\n"
                f"- **Resumen**: {res['summary']}\n"
                f"- **Estado**: `{res['status']}`\n"
                f"- **Datos Extraídos**: `{json.dumps(res['extracted_data'], ensure_ascii=False)}`"
            )

        if action in ["history", "historial", "ledger", "transacciones"]:
            limit = int(params.get("limit") or 10)
            items = nfc_service.get_ledger(limit=limit)
            if not items:
                return "No hay transacciones registradas en el libro contable de contacto NFC actualmente, señor Santiago."

            lines = ["### 📜 Historial de Transacciones Contactless (NFC)"]
            for it in items:
                lines.append(
                    f"- **[{it.get('created_at', '')[:19]}]** `{it.get('id', '')}` | Tipo: `{it.get('type', '')}` | Estado: `{it.get('status', '')}` | {it.get('concept', it.get('summary', ''))}"
                )
            return "\n".join(lines)

        if action in ["clear_history", "limpiar_historial", "reset_ledger"]:
            res = nfc_service.clear_ledger()
            return f"Operación completada: {res['message']}"

        return (
            f"Acción NFC '{action}' no reconocida. Opciones disponibles: "
            f"'payment_request', 'beam_vcard', 'read_tag', 'history', 'status'."
        )

    except Exception as e:
        logger.error(f"Error in nfc_action: {e}", exc_info=True)
        return f"Error ejecutando operación NFC/Contactless: {str(e)}"
