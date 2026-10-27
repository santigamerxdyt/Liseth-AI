# -*- coding: utf-8 -*-
"""
Action handler for Executive Prioritizer & CEO High-Impact Focus (Eisenhower 2.0).
"""

from typing import Any, Dict
from app.services.executive_prioritizer_service import executive_prioritizer_service


def executive_prioritizer_action(parameters: Dict[str, Any]) -> str:
    ceo_name = parameters.get("ceo_name", "Santiago Huerfano")
    items = parameters.get("items", None)
    hours = float(parameters.get("working_hours_day", 9.0))

    res = executive_prioritizer_service.evaluate_priorities(
        ceo_name=ceo_name,
        items=items,
        working_hours_day=hours
    )

    m = res["metrics"]
    q = res["quadrants"]
    dirs = "\n".join([f"  • {d}" for d in res["directives"]])

    q1_titles = ", ".join([i["title"] for i in q["q1_urgent_critical"]["items"]]) or "Ninguna"
    q2_titles = ", ".join([i["title"] for i in q["q2_strategic_high_value"]["items"]]) or "Ninguna"
    q3_titles = ", ".join([i["title"] for i in q["q3_urgent_delegate"]["items"]]) or "Ninguna"

    return (
        f"🎯 **MATRIZ DE PRIORIZACIÓN CEO EISENHOWER 2.0 & FOCO ESTRATÉGICO**\n\n"
        f"• **Líder:** {res['ceo_name']}\n"
        f"• **Índice de Foco Estratégico (Q2):** **{m['strategic_focus_index_pct']}%** ({m['status_color']} • {m['diagnostic']})\n"
        f"• **Índice de Trampa de Urgencia:** {m['urgency_trap_index_pct']}%\n"
        f"• **Carga Total:** {m['total_workload_hours']}h / {m['planned_day_capacity_hours']}h capacidad ({m['workload_utilization_pct']}%)\n\n"
        f"**DESGLOSE POR CUADRANTES DIRECTIVOS:**\n"
        f"• **Q1 Urgente & Crítico ({q['q1_urgent_critical']['hours']}h):** {q1_titles}\n"
        f"• **Q2 Estratégico & Alto Retorno ({q['q2_strategic_high_value']['hours']}h):** {q2_titles}\n"
        f"• **Q3 Operativo Delegable ({q['q3_urgent_delegate']['hours']}h):** {q3_titles}\n\n"
        f"**DIRECTIVAS DE DESBLOQUEO DE AGENDA:**\n{dirs}"
    )
