"""
Action handler for risk_matrix tool in JARVIS / Liseth.
Bridges Gemini Tool Calls with the Corporate Risk Matrix Service.
"""
from typing import Any, Dict
from app.services.risk_matrix_service import risk_matrix_service


def risk_matrix_action(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Manages corporate risks and generates 5x5 heatmap summaries.
    """
    action = parameters.get("action") or "summary"

    if action in ("add", "create", "nuevo"):
        title = parameters.get("title") or parameters.get("titulo") or "Riesgo no especificado"
        cat = parameters.get("category") or parameters.get("categoria") or "Estrategico"
        prob = int(parameters.get("probability") or parameters.get("probabilidad") or 3)
        imp = int(parameters.get("impact") or parameters.get("impacto") or 3)
        ctrl = parameters.get("control") or "Controles de supervisión directa"
        r_prob = int(parameters.get("residual_probability") or 2)
        r_imp = int(parameters.get("residual_impact") or 2)
        owner = parameters.get("owner") or "Santiago / CEO"

        new_risk = risk_matrix_service.add_risk(
            title=title,
            category=cat,
            probability=prob,
            impact=imp,
            control=ctrl,
            residual_probability=r_prob,
            residual_impact=r_imp,
            owner=owner
        )
        report = risk_matrix_service.format_markdown_report()
        return {
            "status": "success",
            "action": "risk_matrix.add",
            "risk": new_risk,
            "markdown": report
        }

    elif action in ("delete", "remove", "eliminar"):
        risk_id = parameters.get("risk_id") or parameters.get("id") or ""
        deleted = risk_matrix_service.delete_risk(risk_id)
        report = risk_matrix_service.format_markdown_report()
        return {
            "status": "success" if deleted else "not_found",
            "action": "risk_matrix.delete",
            "deleted": deleted,
            "markdown": report
        }

    else:  # summary, list, heatmap
        data = risk_matrix_service.get_heatmap_5x5()
        report = risk_matrix_service.format_markdown_report()
        return {
            "status": "success",
            "action": "risk_matrix.summary",
            "heatmap": data,
            "markdown": report
        }
