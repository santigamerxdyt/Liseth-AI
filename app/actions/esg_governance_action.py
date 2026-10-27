# -*- coding: utf-8 -*-
"""
Action handler for ESG Governance & Sustainability.
"""

from typing import Any, Dict
from app.services.esg_governance_service import esg_governance_service


def esg_governance_action(parameters: Dict[str, Any]) -> str:
    company = parameters.get("company_name", "Empresa de Santiago")
    env = float(parameters.get("environmental_score", 78.0))
    soc = float(parameters.get("social_score", 82.0))
    gov = float(parameters.get("governance_score", 85.0))
    sector = parameters.get("sector", "Agroindustria / Servicios Valle del Cauca")
    headcount = int(parameters.get("headcount", 60))

    res = esg_governance_service.evaluate_esg(
        company_name=company,
        environmental_score=env,
        social_score=soc,
        governance_score=gov,
        sector=sector,
        headcount=headcount
    )

    recs = "\n".join([f"  • {r}" for r in res["strategic_recommendations"]])

    return (
        f"🌱 **EVALUACIÓN DE GOBIERNO CORPORATIVO & SOSTENIBILIDAD ESG**\n\n"
        f"• **Empresa:** {res['company_name']} ({res['sector']} - {res['headcount']} colaboradores)\n"
        f"• **Pilar Ambiental (E - 35%):** {res['environmental_score']} / 100\n"
        f"• **Pilar Social (S - 35%):** {res['social_score']} / 100\n"
        f"• **Pilar Gobernanza (G - 30%):** {res['governance_score']} / 100\n"
        f"• **Puntaje Compuesto ESG:** **{res['composite_esg_score']} / 100**\n"
        f"• **Calificación Oficial:** **{res['esg_rating']}**\n"
        f"• **Nivel de Riesgo ESG:** {res['risk_tier']}\n"
        f"• **Hoja de Ruta Estratégica:**\n{recs}"
    )
