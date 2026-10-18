"""
Daily Debrief Action for JARVIS / Liseth.
Generates or consults the executive activity ledger of tasks completed autonomously today.
"""
import logging
from typing import Any, Dict, Optional
from app.services.daily_debrief_service import daily_debrief_service

logger = logging.getLogger("jarvis.daily_debrief_action")


def daily_debrief_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    """
    Handles user queries about what Liseth completed today:
    - action: 'summary' | 'list' | 'clear'
    """
    params = parameters or {}
    action = params.get("action", "summary").lower().strip()

    if action in ("summary", "debrief", "report"):
        return daily_debrief_service.generate_debrief()

    elif action == "list":
        entries = daily_debrief_service.get_entries(limit=10)
        if not entries:
            return "No hay actividades registradas en la bitácora de hoy, señor Santiago."
        lines = [f"📜 **Bitácora de Eventos de Hoy** ({len(entries)} registros):"]
        for e in entries:
            time_part = e.timestamp[11:16] if len(e.timestamp) >= 16 else ""
            lines.append(f"• `[{time_part}]` [{e.category.upper()}] **{e.title}**: {e.details}")
        return "\n".join(lines)

    return daily_debrief_service.generate_debrief()
