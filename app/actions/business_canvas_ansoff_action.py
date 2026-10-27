# -*- coding: utf-8 -*-
"""
Action handler for Business Model Canvas & Ansoff Growth Strategy.
Synthesizes the 9 Osterwalder blocks, scores strategic consistency,
and details the Ansoff growth matrix roadmap for Señor Santiago.
"""

from typing import Any, Dict
from app.services.business_canvas_ansoff_service import business_canvas_ansoff_service


def business_canvas_ansoff_action(parameters: Dict[str, Any]) -> str:
    project = str(parameters.get("project_name", "Nuevo Proyecto / Modelo")).strip()
    industry = str(parameters.get("industry", "Servicios / Tecnología / Comercio")).strip()
    vp = str(parameters.get("value_proposition", "")).strip()
    cs = str(parameters.get("customer_segments", "")).strip()
    ch = str(parameters.get("channels", "")).strip()
    cr = str(parameters.get("customer_relationships", "")).strip()
    rs = str(parameters.get("revenue_streams", "")).strip()
    kr = str(parameters.get("key_resources", "")).strip()
    ka = str(parameters.get("key_activities", "")).strip()
    kp = str(parameters.get("key_partners", "")).strip()
    cost = str(parameters.get("cost_structure", "")).strip()
    ansoff_quadrant = str(parameters.get("ansoff_quadrant", "market_penetration")).strip()
    budget = float(parameters.get("investment_budget", 30000000.0))
    currency = str(parameters.get("currency", "COP")).strip().upper()

    res = business_canvas_ansoff_service.evaluate_canvas_and_ansoff(
        project_name=project,
        industry=industry,
        value_proposition=vp,
        customer_segments=cs,
        channels=ch,
        customer_relationships=cr,
        revenue_streams=rs,
        key_resources=kr,
        key_activities=ka,
        key_partners=kp,
        cost_structure=cost,
        ansoff_quadrant=ansoff_quadrant,
        investment_budget=budget,
        currency=currency
    )

    b = res["canvas_blocks"]
    a = res["ansoff_strategy"]
    f = res["financials"]

    lines = [
        f"🧭 **MODELO DE NEGOCIO CANVAS & MATRIZ ANSOFF — {res['project_name'].upper()}**\n",
        f"• **Industria / Sector:** {res['industry']}",
        f"• **Score de Coherencia Estratégica:** **{res['coherence_score']} / 100** ({res['coherence_status']})",
        f"• **Presupuesto de Expansión:** {currency} ${f['investment_budget']:,.2f}\n",
        f"🧱 **LOS 9 BLOQUES DEL BUSINESS MODEL CANVAS:**",
        f"  1. **Propuesta de Valor:** {b['value_proposition']}",
        f"  2. **Segmentos de Clientes:** {b['customer_segments']}",
        f"  3. **Canales de Distribución:** {b['channels']}",
        f"  4. **Relaciones con Clientes:** {b['customer_relationships']}",
        f"  5. **Fuentes de Ingresos:** {b['revenue_streams']}",
        f"  6. **Recursos Clave:** {b['key_resources']}",
        f"  7. **Actividades Clave:** {b['key_activities']}",
        f"  8. **Alianzas Clave:** {b['key_partners']}",
        f"  9. **Estructura de Costos:** {b['cost_structure']}\n",
        f"🚀 **ESTRATEGIA DE CRECIMIENTO ANSOFF:**",
        f"• **Cuadrante Activo:** **{a['name']}**",
        f"• **Nivel de Riesgo Operativo:** {a['risk_level']}",
        f"• **Retorno Proyectado (ROI):** +{a['expected_roi_pct']}% (Ganancia neta esperada: {currency} ${f['net_profit_expansion']:,.2f})",
        f"• **Período de Retorno (Payback):** ~{a['payback_months']} meses",
        f"• **Enfoque Primario:** {a['primary_focus']}\n",
        f"📌 **INICIATIVAS TÁCTICAS DEL CUADRANTE:**"
    ]

    for init in a["strategic_initiatives"]:
        lines.append(f"  - {init}")

    lines.append("\n🗺️ **ROADMAP DE EJECUCIÓN (4 TRIMESTRES):**")
    for r in res["roadmap"]:
        lines.append(f"• **{r['phase']}**: {r['focus']} | *Hito:* {r['milestone']}")

    if res["bottlenecks"]:
        lines.append("\n⚠️ **PUNTOS DE ATENCIÓN IDENTIFICADOS:**")
        for bn in res["bottlenecks"]:
            lines.append(f"  - {bn}")

    lines.append("\n*Informe generado bajo el marco metodológico de Osterwalder & Ansoff para la alta dirección.*")
    return "\n".join(lines)
