"""
Action handler for pitch_generator tool in JARVIS / Liseth.
Bridges Gemini Tool Calls with the Executive Pitch Deck Generator Service.
"""
from typing import Any, Dict
from app.services.pitch_generator_service import pitch_generator_service


def pitch_generator_action(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a 10-slide executive pitch deck following Guy Kawasaki / Sequoia Capital framework.
    """
    name = parameters.get("business_name") or parameters.get("nombre") or "Stark Ventures Colombia"
    ind = parameters.get("industry") or parameters.get("sector") or "tech_saas"
    prob = parameters.get("problem") or parameters.get("problema")
    sol = parameters.get("solution") or parameters.get("solucion")
    ask = float(parameters.get("funding_ask") or parameters.get("monto_inversion") or 250000000.0)
    curr = parameters.get("currency") or "COP"
    founder = parameters.get("founder") or "Santiago Huerfano Lopez"
    city = parameters.get("city") or "Palmira, Valle del Cauca, Colombia"

    deck = pitch_generator_service.generate_deck(
        business_name=name,
        industry=ind,
        problem_statement=prob,
        solution_value=sol,
        funding_ask=ask,
        currency=curr,
        founder_name=founder,
        city=city
    )

    markdown = pitch_generator_service.format_markdown(deck)

    return {
        "status": "success",
        "action": "pitch_generator",
        "deck": deck,
        "markdown": markdown
    }
