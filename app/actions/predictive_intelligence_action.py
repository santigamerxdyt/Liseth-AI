# -*- coding: utf-8 -*-
"""
Action handler for Predictive Intelligence & Anticipatory 3-Step Execution.
Allows Liseth to articulate and execute proactive steps for Señor Santiago.
"""

from typing import Any, Dict
from app.services.predictive_intelligence_service import predictive_intelligence_service


def predictive_intelligence_action(parameters: Dict[str, Any]) -> str:
    ctx = str(parameters.get("context", "")).strip()
    res = predictive_intelligence_service.get_anticipatory_plan(context=ctx if ctx else None)

    p = res["persona_status"]
    steps = res["steps"]

    lines = [
        "🔮 **INTELIGENCIA PREDICTIVA LISETH — PENSANDO 3 PASOS ADELANTE**\n",
        f"• **Fase Actual:** {res['phase_name']} | **Índice de Confianza:** {res['confidence_score']}%",
        f"• **Rol:** {p['role']} ({p['demeanor']})",
        f"• **Consigna:** *\"{res['anticipatory_motto']}\"*\n",
        "🎯 **PLAN ANTICIPATORIO SECUENCIAL (PRÓXIMOS 3 PASOS):**"
    ]

    for s in steps:
        lines.append(
            f"  {s['step_num']}. **[{s['tag']}] {s['title']}** ({s['timing']})\n"
            f"     ↳ {s['description']}\n"
            f"     ↳ *Orden sugerida:* \"{s['action_prompt']}\""
        )

    lines.append("\n*¿Desea que proceda de inmediato con el Paso 1, Señor Santiago?*")
    return "\n".join(lines)
