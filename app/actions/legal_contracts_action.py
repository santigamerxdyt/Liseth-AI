"""
Legal Contracts Action for JARVIS / Liseth.
Entrypoint for generating commercial agreements, NDAs, and promissory notes.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.services.legal_contracts_service import legal_contracts_service

logger = logging.getLogger("jarvis.legal_contracts_action")


def legal_contracts_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    params = parameters or {}
    action = str(params.get("action") or "draft").lower().strip()

    try:
        if action in ["templates", "list", "plantillas", "modelos"]:
            tmps = legal_contracts_service.get_supported_templates()
            lines = ["### 📜 Minutas Legales y Contratos Comerciales Disponibles:"]
            for t in tmps:
                lines.append(f"- **{t['name']}** (`{t['id']}`): {t['description']}")
            return "\n".join(lines)

        if action in ["draft", "generar", "contrato", "crear_contrato", "nda", "pagare"]:
            template = str(params.get("template") or params.get("type") or "servicios_profesionales")
            client = str(params.get("client") or params.get("party_b") or "Cliente / Empresa Contratante")
            client_id = str(params.get("client_id") or params.get("nit") or "900.000.000-1")
            amount = float(params.get("amount") or 2500000.0)
            scope = str(params.get("scope") or "Servicios de Asesoría y Consultoría en Administración")
            city = str(params.get("city") or "Palmira, Valle del Cauca")

            doc = legal_contracts_service.generate_contract(
                template_type=template,
                party_b_name=client,
                party_b_id=client_id,
                amount=amount,
                scope=scope,
                city=city
            )
            return (
                f"### 📄 Documento Legal Generado: `{doc['id']}`\n"
                f"- **Título**: {doc['title']}\n"
                f"- **Contratante**: {doc['party_b']}\n"
                f"- **Monto**: `${doc['amount']:,.2f} {doc['currency']}`\n"
                f"- **Ciudad**: {doc['city']}\n\n"
                f"{doc['content_markdown']}"
            )

        return f"Acción de contratos '{action}' no reconocida. Opciones: 'draft', 'templates'."

    except Exception as e:
        logger.error(f"Error in legal_contracts_action: {e}", exc_info=True)
        return f"Error generando minuta legal: {str(e)}"
