"""
Action handler for investment_evaluator tool in JARVIS / Liseth.
Bridges Gemini Tool Calls with the Investment Evaluator Service.
"""
from typing import Any, Dict
from app.services.investment_evaluator_service import investment_evaluator_service


def investment_evaluator_action(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates capital investment proposals with NPV, IRR, Payback and Scenarios.
    """
    name = parameters.get("project_name") or parameters.get("name") or "Nuevo Proyecto Stark"
    initial_inv = float(parameters.get("initial_investment") or parameters.get("inversion_inicial") or 50000000.0)
    
    # Extract flows
    raw_flows = parameters.get("cash_flows") or parameters.get("flujos_caja") or [15000000.0, 20000000.0, 25000000.0, 30000000.0]
    if isinstance(raw_flows, str):
        flows = [float(x.strip()) for x in raw_flows.split(",") if x.strip()]
    elif isinstance(raw_flows, list):
        flows = [float(x) for x in raw_flows]
    else:
        flows = [15000000.0, 20000000.0, 25000000.0, 30000000.0]

    discount_rate = float(parameters.get("discount_rate") or parameters.get("tasa_descuento") or 0.12)
    currency = parameters.get("currency") or "COP"

    eval_res = investment_evaluator_service.evaluate_project(
        name=name,
        initial_investment=initial_inv,
        cash_flows=flows,
        discount_rate=discount_rate,
        currency=currency
    )

    markdown_report = investment_evaluator_service.format_markdown_report(eval_res)

    return {
        "status": "success",
        "action": "investment_evaluator",
        "result": eval_res,
        "markdown": markdown_report
    }
