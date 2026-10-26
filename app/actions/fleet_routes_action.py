"""
Action handler for fleet_routes tool in JARVIS / Liseth.
Bridges Gemini Tool Calls with the Fleet Routes & Freight Logistics Service.
"""
from typing import Any, Dict
from app.services.fleet_routes_service import fleet_routes_service


def fleet_routes_action(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes freight costs, fuel, tolls, and carbon emissions for Colombian routes.
    """
    route = parameters.get("route") or parameters.get("ruta") or "palmira_cali"
    vehicle = parameters.get("vehicle") or parameters.get("vehiculo") or "turbo_4_ton"
    dist = float(parameters.get("distance_km")) if parameters.get("distance_km") else None
    fuel_p = float(parameters.get("fuel_price") or 16500.0)
    weight = float(parameters.get("cargo_weight")) if parameters.get("cargo_weight") else None

    res = fleet_routes_service.calculate_freight(
        route_key=route,
        vehicle_key=vehicle,
        custom_distance_km=dist,
        fuel_price_gallon=fuel_p,
        cargo_weight_tons=weight
    )
    report = fleet_routes_service.format_markdown_report(res)

    return {
        "status": "success",
        "action": "fleet_routes",
        "freight": res,
        "markdown": report
    }
