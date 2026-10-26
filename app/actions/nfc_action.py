"""
NFC & Contactless Payment Action for JARVIS / Liseth.
Entrypoint for NFC tag reading, writing, contactless payments, and transaction history.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from app.services.nfc_service import nfc_service
from app.services.invoice_service import invoice_service

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

        if action in ["invoice", "factura", "facturar", "crear_factura", "recibo"]:
            client = str(params.get("client") or params.get("client_name") or "Cliente Particular")
            client_id = str(params.get("client_id") or "222222222222")
            amount = float(params.get("amount") or 50000.0)
            concept = str(params.get("concept") or params.get("description") or "Servicios Profesionales de Administración")
            tax_rate = float(params.get("tax_rate") if params.get("tax_rate") is not None else 0.19)
            currency = str(params.get("currency") or "COP").upper()
            method = str(params.get("method") or "Bre-B Contactless")
            nfc_tx = params.get("nfc_tx_id")

            items = [{
                "description": concept,
                "quantity": 1,
                "unit_price": amount
            }]

            inv = invoice_service.generate_invoice(
                client_name=client,
                client_id=client_id,
                items=items,
                tax_rate=tax_rate,
                currency=currency,
                payment_method=method,
                nfc_tx_id=nfc_tx
            )
            return invoice_service.format_invoice_markdown(inv)

        if action in ["convert", "divisas", "crypto", "calcular_divisas", "cambio"]:
            amount = float(params.get("amount") or 1.0)
            from_c = str(params.get("from_currency") or params.get("from") or "USD").upper()
            to_c = str(params.get("to_currency") or params.get("to") or "COP").upper()

            res = nfc_service.convert_currency(amount, from_curr=from_c, to_curr=to_c)
            return (
                f"### 💱 Conversión de Divisas & Criptoactivos\n"
                f"- **Monto Original**: `{res['amount']:,.4f} {res['from_currency']}`\n"
                f"- **Resultado Convertido**: **`{res['converted_amount']:,.4f} {res['to_currency']}`**\n"
                f"- **Tasa de Cambio Base**: `1 {res['from_currency']} = {res['exchange_rate']:,.4f} {res['to_currency']}`\n"
                f"- **Sello de Tiempo**: `{res['timestamp'][:19]}`"
            )

        if action in ["badge", "security_key", "llave", "desbloqueo", "credencial"]:
            uid = str(params.get("uid") or params.get("badge_uid") or "04:STARK:KEY:01")
            sub_action = str(params.get("sub_action") or "verify").lower()
            if sub_action in ("enroll", "registrar"):
                label = str(params.get("label") or "Credencial de Santiago")
                b = nfc_service.enroll_security_badge(uid, label=label)
                return f"Llave de seguridad NFC '{b['label']}' (UID: `{b['id']}`) registrada exitosamente."
            else:
                ver = nfc_service.verify_security_badge(uid)
                return f"Verificación de credencial NFC: {ver['message']} (Autorizado: `{ver['authorized']}`)"

        return (
            f"Acción NFC '{action}' no reconocida. Opciones disponibles: "
            f"'payment_request', 'beam_vcard', 'read_tag', 'invoice', 'convert', 'badge', 'history', 'status'."
        )


    except Exception as e:
        logger.error(f"Error in nfc_action: {e}", exc_info=True)
        return f"Error ejecutando operación NFC/Contactless: {str(e)}"
