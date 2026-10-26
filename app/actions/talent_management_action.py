# -*- coding: utf-8 -*-
"""
Action handler for Talent Management, 9-Box Grid, and eNPS.
"""

from typing import Any, Dict
from app.services.talent_management_service import talent_management_service


def talent_management_action(parameters: Dict[str, Any]) -> str:
    action_type = parameters.get("action_type", "9box")

    if action_type in ("9box", "nine_box", "talento", "evaluacion_colaborador"):
        name = parameters.get("employee_name", "Santiago Martínez")
        perf = float(parameters.get("performance_score", 2.8))
        pot = float(parameters.get("potential_score", 2.9))
        role = parameters.get("role", "Gerente de Proyectos")
        dept = parameters.get("department", "Innovación & Operaciones")

        res = talent_management_service.evaluate_9box(
            employee_name=name, performance_score=perf, potential_score=pot, role=role, department=dept
        )
        return (
            f"👤 **EVALUACIÓN MATRIZ 9-BOX (GESTIÓN DE TALENTO HUMANO)**\n\n"
            f"• **Colaborador:** {res['employee_name']} ({res['role']} - {res['department']})\n"
            f"• **Puntuación Desempeño:** {res['performance_score']} / 3.0 (Nivel: **{res['performance_level']}**)\n"
            f"• **Puntuación Potencial:** {res['potential_score']} / 3.0 (Nivel: **{res['potential_level']}**)\n"
            f"• **Cuadrante 9-Box:** **{res['quadrant']}**\n"
            f"• **Plan de Acción Recomendado:** {res['recommended_action']}\n"
            f"• **Diagnóstico de Retención:** {res['risk_assessment']}"
        )

    elif action_type in ("enps", "clima_laboral", "satisfaccion"):
        prom = int(parameters.get("promoters", 42))
        pas = int(parameters.get("passives", 18))
        det = int(parameters.get("detractors", 6))

        res = talent_management_service.calculate_enps(promoters=prom, passives=pas, detractors=det)
        return (
            f"🌟 **DIAGNÓSTICO DE CLIMA ORGANIZACIONAL (eNPS)**\n\n"
            f"• **Total Evaluados:** {res['total_respondents']} colaboradores\n"
            f"• **Promotores (9-10):** {res['promoters_count']} ({res['promoters_pct']}%)\n"
            f"• **Pasivos (7-8):** {res['passives_count']} ({res['passives_pct']}%)\n"
            f"• **Detractores (0-6):** {res['detractors_count']} ({res['detractors_pct']}%)\n"
            f"• **Puntaje eNPS:** **{res['enps_score']} puntos** (Escala -100 a +100)\n"
            f"• **Evaluación de Cultura:** {res['diagnostic']}"
        )

    elif action_type in ("turnover", "rotacion", "costo_rotacion"):
        dep = int(parameters.get("departures", 4))
        head = int(parameters.get("avg_headcount", 50))
        sal = float(parameters.get("avg_salary_cop", 3800000.0))
        period = int(parameters.get("period_months", 12))

        res = talent_management_service.calculate_turnover_cost(
            departures=dep, avg_headcount=head, avg_salary_cop=sal, period_months=period
        )
        return (
            f"📉 **IMPACTO FINANCIERO DE ROTACIÓN DE PERSONAL (TURNOVER)**\n\n"
            f"• **Salidas del Período:** {res['departures']} personas de una plantilla media de {res['avg_headcount']}\n"
            f"• **Tasa de Rotación Anualizada:** **{res['annualized_turnover_pct']}%** (Nivel: {res['turnover_level']})\n"
            f"• **Salario Medio Mensual:** ${res['avg_salary_cop']:,.2f} COP\n"
            f"• **Costo Oculto por Vacante:** ${res['cost_per_departure_cop']:,.2f} COP (Curva aprendizaje + Reclutamiento + Indemnización)\n"
            f"• **Costo Total para la Empresa:** **${res['total_turnover_cost_cop']:,.2f} COP**"
        )

    return f"Acción de talento '{action_type}' no reconocida."
