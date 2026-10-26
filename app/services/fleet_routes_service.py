"""
Fleet Routes & Colombian Freight Logistics Service for Liseth / JARVIS.
Tailored for Operations, Supply Chain and Regional Logistics (Valle del Cauca):
- Colombian Highway Network Matrix (Distances, Tolls, Topography)
- Fuel Consumption & Vehicle Sizing (Van, Turbo, Sencillo, Tractomula)
- Direct Freight Cost Breakdown (Fuel, INVIAS Tolls, Wear & Tear, Driver Stipends)
- Carbon Footprint (kg CO2 emissions per route)
"""
from typing import Any, Dict, List, Optional

# Pre-mapped Colombian Highway Routes
COLOMBIAN_ROUTES = {
    "palmira_cali": {"origin": "Palmira", "destination": "Cali", "distance_km": 28.0, "tolls": 1, "avg_toll_cop": 11500.0},
    "palmira_yumbo": {"origin": "Palmira", "destination": "Yumbo (Zona Industrial)", "distance_km": 36.0, "tolls": 1, "avg_toll_cop": 11500.0},
    "palmira_buenaventura": {"origin": "Palmira", "destination": "Buenaventura (Puerto)", "distance_km": 145.0, "tolls": 3, "avg_toll_cop": 14500.0},
    "palmira_pereira": {"origin": "Palmira", "destination": "Pereira (Eje Cafetero)", "distance_km": 195.0, "tolls": 3, "avg_toll_cop": 14000.0},
    "palmira_bogota": {"origin": "Palmira", "destination": "Bogotá D.C. (La Línea)", "distance_km": 480.0, "tolls": 8, "avg_toll_cop": 15000.0},
    "palmira_medellin": {"origin": "Palmira", "destination": "Medellín", "distance_km": 430.0, "tolls": 6, "avg_toll_cop": 14500.0}
}

VEHICLE_SPECS = {
    "van_urbana": {
        "name": "Furgón Urbano / Van (1.5 Tons)",
        "capacity_tons": 1.5,
        "km_per_gallon": 30.0,
        "wear_per_km": 650.0,
        "driver_day_stipend": 75000.0,
        "co2_factor_kg_gal": 8.8
    },
    "turbo_4_ton": {
        "name": "Camión Turbo (4.5 Tons)",
        "capacity_tons": 4.5,
        "km_per_gallon": 18.0,
        "wear_per_km": 1200.0,
        "driver_day_stipend": 95000.0,
        "co2_factor_kg_gal": 10.2
    },
    "sencillo_8_ton": {
        "name": "Camión Sencillo (8.5 Tons)",
        "capacity_tons": 8.5,
        "km_per_gallon": 12.0,
        "wear_per_km": 1850.0,
        "driver_day_stipend": 120000.0,
        "co2_factor_kg_gal": 10.2
    },
    "tractomula_32_ton": {
        "name": "Tractocamión / Mula (32 Tons)",
        "capacity_tons": 32.0,
        "km_per_gallon": 6.5,
        "wear_per_km": 3200.0,
        "driver_day_stipend": 180000.0,
        "co2_factor_kg_gal": 10.2
    }
}


class FleetRoutesService:
    def __init__(self):
        pass

    def calculate_freight(
        self,
        route_key: str = "palmira_cali",
        vehicle_key: str = "turbo_4_ton",
        custom_distance_km: Optional[float] = None,
        fuel_price_gallon: float = 16500.0,
        cargo_weight_tons: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculates freight dispatch cost in Colombia.
        """
        route = COLOMBIAN_ROUTES.get(route_key)
        dist = float(custom_distance_km) if custom_distance_km else (route["distance_km"] if route else 50.0)
        tolls_count = route["tolls"] if route else 1
        avg_toll = route["avg_toll_cop"] if route else 12000.0

        veh = VEHICLE_SPECS.get(vehicle_key, VEHICLE_SPECS["turbo_4_ton"])
        weight = float(cargo_weight_tons) if cargo_weight_tons else veh["capacity_tons"]

        # Calculations
        gallons_needed = round(dist / veh["km_per_gallon"], 2)
        fuel_cost = round(gallons_needed * float(fuel_price_gallon), 2)
        tolls_cost = round(tolls_count * avg_toll, 2)
        wear_cost = round(dist * veh["wear_per_km"], 2)
        driver_cost = veh["driver_day_stipend"]

        total_freight_cost = round(fuel_cost + tolls_cost + wear_cost + driver_cost, 2)
        cost_per_km = round(total_freight_cost / dist, 2) if dist > 0 else 0.0
        cost_per_ton = round(total_freight_cost / weight, 2) if weight > 0 else 0.0
        co2_emissions_kg = round(gallons_needed * veh["co2_factor_kg_gal"], 2)

        return {
            "origin": route["origin"] if route else "Origen",
            "destination": route["destination"] if route else "Destino",
            "distance_km": dist,
            "vehicle": veh["name"],
            "cargo_weight_tons": weight,
            "gallons_consumed": gallons_needed,
            "fuel_cost_cop": fuel_cost,
            "tolls_cost_cop": tolls_cost,
            "wear_and_maintenance_cop": wear_cost,
            "driver_stipend_cop": driver_cost,
            "total_freight_cost_cop": total_freight_cost,
            "cost_per_km": cost_per_km,
            "cost_per_ton": cost_per_ton,
            "co2_emissions_kg": co2_emissions_kg
        }

    def format_markdown_report(self, data: Dict[str, Any]) -> str:
        md = [
            f"# 🚛 LIQUIDACIÓN DE FLETE LOGÍSTICO: {data['origin'].upper()} ➔ {data['destination'].upper()}",
            f"- **Distancia Oficial**: `{data['distance_km']} km` | **Vehículo**: `{data['vehicle']}`",
            f"- **Carga Transportada**: `{data['cargo_weight_tons']} toneladas`",
            "",
            "### ⛽ Desglose de Costos Operativos",
            f"- **Combustible**: `${data['fuel_cost_cop']:,.2f} COP` ({data['gallons_consumed']} galones)",
            f"- **Peajes INVIAS**: `${data['tolls_cost_cop']:,.2f} COP`",
            f"- **Desgaste y Mantenimiento / km**: `${data['wear_and_maintenance_cop']:,.2f} COP`",
            f"- **Viáticos y Mano de Obra**: `${data['driver_stipend_cop']:,.2f} COP`",
            "",
            f"> 💡 **COSTO TOTAL DEL FLETE**: **`${data['total_freight_cost_cop']:,.2f} COP`**  ",
            f"> 📦 **Costo por Kilómetro**: `${data['cost_per_km']:,.2f} COP/km` | **Por Tonelada**: `${data['cost_per_ton']:,.2f} COP/ton`  ",
            f"> 🌿 **Huella de Carbono**: `{data['co2_emissions_kg']} kg de CO₂`"
        ]
        return "\n".join(md)


fleet_routes_service = FleetRoutesService()
