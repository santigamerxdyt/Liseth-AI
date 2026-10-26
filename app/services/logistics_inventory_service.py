"""
Logistics & Inventory Supply Chain Service for Liseth / JARVIS.
Tailored for Business Administration & Operations Management (UNAL Palmira):
- Economic Order Quantity (EOQ / Wilson Model)
- Optimal Reorder Point (ROP) with Safety Stock (SS) across Service Levels (Z)
- ABC Inventory Classification (Pareto 80/20 Analysis)
- Annual Inventory Holding vs Ordering Cost Optimization
"""
import math
from typing import Any, Dict, List, Optional

Z_SCORES = {
    85: 1.04,
    90: 1.28,
    95: 1.645,
    98: 2.05,
    99: 2.33,
    99.9: 3.09
}


class LogisticsInventoryService:
    def __init__(self):
        pass

    def calculate_eoq(
        self,
        annual_demand: float,
        order_cost: float,
        holding_cost: float,
        unit_cost: float = 0.0
    ) -> Dict[str, Any]:
        """
        Computes the Wilson Economic Order Quantity:
        Q* = sqrt((2 * D * S) / H)
        """
        d = float(annual_demand)
        s = float(order_cost)
        h = float(holding_cost)
        c = float(unit_cost)

        if d <= 0 or s <= 0 or h <= 0:
            raise ValueError("Demanda, costo de orden y costo de mantenimiento deben ser mayores a 0")

        eoq = math.sqrt((2.0 * d * s) / h)
        optimal_q = round(eoq, 2)
        orders_per_year = round(d / optimal_q, 2) if optimal_q > 0 else 0
        cycle_days = round(365.0 / orders_per_year, 1) if orders_per_year > 0 else 0

        annual_order_cost = round(orders_per_year * s, 2)
        annual_holding_cost = round((optimal_q / 2.0) * h, 2)
        annual_inventory_cost = round(annual_order_cost + annual_holding_cost, 2)
        annual_purchase_cost = round(d * c, 2)
        total_supply_cost = round(annual_inventory_cost + annual_purchase_cost, 2)

        return {
            "annual_demand": d,
            "order_cost_per_order": s,
            "holding_cost_per_unit_year": h,
            "unit_cost": c,
            "optimal_order_quantity_eoq": optimal_q,
            "orders_per_year": orders_per_year,
            "cycle_days_between_orders": cycle_days,
            "annual_ordering_cost": annual_order_cost,
            "annual_holding_cost": annual_holding_cost,
            "total_inventory_cost": annual_inventory_cost,
            "annual_purchase_cost": annual_purchase_cost,
            "total_supply_chain_cost": total_supply_cost
        }

    def calculate_rop(
        self,
        daily_demand: float,
        lead_time_days: float,
        service_level_pct: float = 95.0,
        std_dev_daily_demand: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculates Reorder Point (ROP) and Safety Stock:
        ROP = (d * L) + SS
        SS = Z * sigma_d * sqrt(L)
        """
        d = float(daily_demand)
        lead_time = float(lead_time_days)
        sl = float(service_level_pct)
        sigma = float(std_dev_daily_demand)

        # Approximate Z score
        z = Z_SCORES.get(int(sl), 1.645)
        if sl >= 99:
            z = 2.33
        elif sl >= 98:
            z = 2.05
        elif sl >= 95:
            z = 1.645
        elif sl >= 90:
            z = 1.28

        lead_time_demand = round(d * lead_time, 2)
        safety_stock = round(z * sigma * math.sqrt(lead_time), 2) if (sigma > 0 and lead_time > 0) else 0.0
        rop = round(lead_time_demand + safety_stock, 2)

        return {
            "daily_demand": d,
            "lead_time_days": lead_time,
            "service_level_pct": sl,
            "z_score": z,
            "std_dev_daily_demand": sigma,
            "lead_time_demand": lead_time_demand,
            "safety_stock_units": safety_stock,
            "reorder_point_rop_units": rop
        }

    def classify_abc(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Classifies SKUs by ABC Pareto analysis:
        Zone A: top ~80% of value
        Zone B: next ~15% of value
        Zone C: remaining ~5% of value
        """
        if not items:
            return {"total_skus": 0, "total_value": 0, "classified_items": []}

        # Calculate annual value per SKU
        processed = []
        total_val = 0.0
        for it in items:
            code = str(it.get("code") or it.get("sku") or "SKU")
            name = str(it.get("name") or "Producto")
            demand = float(it.get("annual_demand") or it.get("demand") or 0.0)
            unit_c = float(it.get("unit_cost") or it.get("cost") or 0.0)
            val = round(demand * unit_c, 2)
            total_val += val
            processed.append({
                "code": code,
                "name": name,
                "annual_demand": demand,
                "unit_cost": unit_c,
                "annual_value": val
            })

        # Sort descending by annual value
        processed.sort(key=lambda x: x["annual_value"], reverse=True)

        cumulative_val = 0.0
        classified = []
        for it in processed:
            cumulative_val += it["annual_value"]
            pct = (it["annual_value"] / total_val * 100.0) if total_val > 0 else 0.0
            cum_pct = (cumulative_val / total_val * 100.0) if total_val > 0 else 0.0

            if cum_pct <= 80.0 or len(classified) == 0:
                zone = "A"
            elif cum_pct <= 95.0:
                zone = "B"
            else:
                zone = "C"

            classified.append({
                **it,
                "value_pct": round(pct, 2),
                "cumulative_pct": round(cum_pct, 2),
                "zone": zone
            })

        count_a = sum(1 for x in classified if x["zone"] == "A")
        count_b = sum(1 for x in classified if x["zone"] == "B")
        count_c = sum(1 for x in classified if x["zone"] == "C")

        return {
            "total_skus": len(classified),
            "total_value": round(total_val, 2),
            "zone_counts": {"A": count_a, "B": count_b, "C": count_c},
            "classified_items": classified
        }

    def format_markdown_report(self, eoq_data: Dict[str, Any], rop_data: Optional[Dict[str, Any]] = None) -> str:
        md = [
            "# 📦 AUDITORÍA DE INVENTARIOS & MODELO EOQ (WILSON)",
            f"- **Demanda Anual ($D$)**: `{eoq_data['annual_demand']:,.0f} unidades/año`",
            f"- **Costo por Pedir ($S$)**: `${eoq_data['order_cost_per_order']:,.2f} COP`",
            f"- **Costo Mantenimiento ($H$)**: `${eoq_data['holding_cost_per_unit_year']:,.2f} COP/unidad-año`",
            "",
            "### 🎯 Cantidad Óptima de Pedido (EOQ)",
            f"- **Lote Económico Óptimo ($Q^*$)**: **`{eoq_data['optimal_order_quantity_eoq']:,.1f} unidades`**",
            f"- **Pedidos al Año ($N$)**: `{eoq_data['orders_per_year']} pedidos`",
            f"- **Frecuencia del Ciclo**: Cada `{eoq_data['cycle_days_between_orders']} días`",
            f"- **Costo Anual de Ordenar**: `${eoq_data['annual_ordering_cost']:,.2f} COP`",
            f"- **Costo Anual de Mantener**: `${eoq_data['annual_holding_cost']:,.2f} COP`",
            f"- **Costo Total de Gestión de Inventario**: **`${eoq_data['total_inventory_cost']:,.2f} COP`**",
            ""
        ]

        if rop_data:
            md.extend([
                "### 🚨 Punto de Reorden (ROP) & Stock de Seguridad",
                f"- **Demanda Diaria ($d$)**: `{rop_data['daily_demand']} unidades/día`",
                f"- **Lead Time del Proveedor ($L$)**: `{rop_data['lead_time_days']} días`",
                f"- **Nivel de Servicio Exigido**: `{rop_data['service_level_pct']}% (Z = {rop_data['z_score']})`",
                f"- **Stock de Seguridad ($SS$)**: `{rop_data['safety_stock_units']} unidades`",
                f"- **Punto de Reorden ($ROP$)**: **`{rop_data['reorder_point_rop_units']} unidades`**",
                f"> 💡 *Dispare la orden de compra tan pronto el inventario físico descienda a {rop_data['reorder_point_rop_units']} unidades.*"
            ])

        return "\n".join(md)


logistics_inventory_service = LogisticsInventoryService()
