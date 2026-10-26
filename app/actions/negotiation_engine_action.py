"""
Action handler for negotiation_engine tool in JARVIS / Liseth.
Bridges Gemini Tool Calls with the Harvard Negotiation Service.
"""
from typing import Any, Dict
from app.services.negotiation_engine_service import negotiation_engine_service


def negotiation_engine_action(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates ZOPA, BATNA, and negotiation tactics under the Harvard Framework.
    """
    buyer_res = float(parameters.get("buyer_reservation_price") or parameters.get("comprador_maximo") or 50000000.0)
    seller_res = float(parameters.get("seller_reservation_price") or parameters.get("vendedor_minimo") or 42000000.0)

    buyer_tgt = float(parameters.get("buyer_target_price")) if parameters.get("buyer_target_price") else None
    seller_tgt = float(parameters.get("seller_target_price")) if parameters.get("seller_target_price") else None

    b_batna = parameters.get("buyer_batna") or parameters.get("batna_comprador")
    s_batna = parameters.get("seller_batna") or parameters.get("batna_vendedor")
    curr = parameters.get("currency") or "COP"

    res = negotiation_engine_service.evaluate_negotiation(
        buyer_reservation_price=buyer_res,
        seller_reservation_price=seller_res,
        buyer_target_price=buyer_tgt,
        seller_target_price=seller_tgt,
        buyer_batna=b_batna,
        seller_batna=s_batna,
        currency=curr
    )

    report = negotiation_engine_service.format_markdown_report(res)

    return {
        "status": "success",
        "action": "negotiation_engine",
        "negotiation": res,
        "markdown": report
    }
