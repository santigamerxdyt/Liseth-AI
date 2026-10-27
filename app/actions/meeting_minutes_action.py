# -*- coding: utf-8 -*-
"""
Action handler for AI Meeting Minutes & Action Items Extractor.
"""

from typing import Any, Dict
from app.services.meeting_minutes_service import meeting_minutes_service


def meeting_minutes_action(parameters: Dict[str, Any]) -> str:
    title = parameters.get("meeting_title", "Comité Directivo")
    attendees = parameters.get("attendees", "Santiago Huerfano (CEO), Equipo Directivo")
    notes = parameters.get("notes", parameters.get("transcript", ""))

    res = meeting_minutes_service.extract_minutes_and_actions(
        meeting_title=title,
        attendees=attendees,
        raw_notes_or_transcript=notes
    )

    summary_str = "\n".join([f"  • {s}" for s in res["executive_summary"]])
    decisions_str = "\n".join([f"  ✓ {d}" for d in res["approved_decisions"]])
    actions_str = "\n".join([f"  ⚡ [{a['id']}] {a['owner']}: {a['task']} (Fecha: {a['deadline']} | {a['priority']})" for a in res["action_items"]])
    risks_str = "\n".join([f"  ⚠️ {r}" for r in res["risk_flags"]])

    return (
        f"📋 **ACTA EJECUTIVA CON IA & EXTRACTOR DE COMPROMISOS (MINUTES & ACTIONS)**\n\n"
        f"• **Reunión:** {res['meeting_title']} ({res['meeting_date']})\n"
        f"• **Asistentes:** {res['attendees']}\n\n"
        f"**RESUMEN EJECUTIVO (3 TAKEAWAYS):**\n{summary_str}\n\n"
        f"**DECISIONES APROBADAS:**\n{decisions_str}\n\n"
        f"**MATRIZ DE ACCIÓN & RESPONSABLES ({res['total_actions_count']} compromisos):**\n{actions_str}\n\n"
        f"**SEÑALES DE ALERTA & RIESGOS:**\n{risks_str}\n\n"
        f"**BORRADOR DE CORREO DE SEGUIMIENTO (PRE-REDACTADO):**\n```text\n{res['follow_up_email_draft']}\n```"
    )
