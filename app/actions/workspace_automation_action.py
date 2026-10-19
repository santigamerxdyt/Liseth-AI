"""
Workspace Automation Action for JARVIS / Liseth.
Entrypoint for advanced spreadsheet formulas, report blueprints, and presentation deck architectures.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.services.workspace_automation_service import workspace_automation_service

logger = logging.getLogger("jarvis.workspace_automation_action")


def workspace_automation_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    """
    Synchronous entrypoint for Workspace Automation tool.
    Handles: 'status', 'excel_formula', 'report_blueprint', 'presentation_deck'.
    """
    params = parameters or {}
    action = params.get("action", "status").lower().strip()

    try:
        if action in ["status", "estado", "info"]:
            st = workspace_automation_service.get_status()
            return workspace_automation_service.format_status_report(st)

        if action in ["formula", "excel", "sheets", "excel_formula", "hoja_calculo"]:
            query = params.get("query") or params.get("description") or params.get("text") or ""
            if not query:
                return "Señor Santiago, describa qué cálculo o búsqueda desea realizar en Excel o Google Sheets."
            return workspace_automation_service.generate_excel_formula(query)

        if action in ["report", "informe", "ensayo", "blueprint", "report_blueprint"]:
            title = params.get("title") or params.get("topic") or "Plan de Mejora Continua"
            doc_type = params.get("type") or params.get("doc_type") or "consultoria"
            return workspace_automation_service.generate_report_blueprint(title, doc_type=doc_type)

        if action in ["presentation", "diapositivas", "slides", "deck", "presentation_deck"]:
            topic = params.get("topic") or params.get("title") or "Presentación Ejecutiva"
            slides = int(params.get("slides") or params.get("slide_count") or 5)
            return workspace_automation_service.generate_presentation_deck(topic, slide_count=slides)

        return f"Acción de ofimática '{action}' no reconocida. Opciones: 'excel_formula', 'report_blueprint', 'presentation_deck', 'status'."

    except Exception as e:
        logger.error(f"Error in workspace_automation_action: {e}", exc_info=True)
        return f"Error ejecutando automatización ofimática: {str(e)}"
