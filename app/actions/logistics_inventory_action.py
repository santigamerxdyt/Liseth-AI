"""
Action handler for logistics_inventory tool in JARVIS / Liseth.
Bridges Gemini Tool Calls with the Logistics & Inventory Service.
"""
from typing import Any, Dict
from app.services.logistics_inventory_service import logistics_inventory_service


def logistics_inventory_action(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes EOQ optimal order quantity, ROP safety stock, and ABC classification.
    """
    action = parameters.get("action") or "eoq"

    if action in ("rop", "reorder_point", "stock_seguridad"):
        daily_d = float(parameters.get("daily_demand") or parameters.get("demanda_diaria") or 25.0)
        lt = float(parameters.get("lead_time") or parameters.get("tiempo_entrega") or 7.0)
        sl = float(parameters.get("service_level") or parameters.get("nivel_servicio") or 95.0)
        sigma = float(parameters.get("std_dev") or parameters.get("desviacion") or 4.0)

        rop = logistics_inventory_service.calculate_rop(
            daily_demand=daily_d,
            lead_time_days=lt,
            service_level_pct=sl,
            std_dev_daily_demand=sigma
        )
        md = [
            "# 🚨 PUNTO DE REORDEN (ROP) & STOCK DE SEGURIDAD",
            f"- **Demanda Diaria ($d$)**: `{rop['daily_demand']} unidades`",
            f"- **Tiempo de Entrega Proveedor ($L$)**: `{rop['lead_time_days']} días`",
            f"- **Nivel de Servicio Exigido**: `{rop['service_level_pct']}%`",
            f"- **Stock de Seguridad ($SS$)**: **`{rop['safety_stock_units']} unidades`**",
            f"- **PUNTO DE REORDEN ÓPTIMO ($ROP$)**: **`{rop['reorder_point_rop_units']} unidades`**",
            "",
            f"> 💡 *Generar orden de compra al llegar a {rop['reorder_point_rop_units']} unidades en almacén.*"
        ]
        return {
            "status": "success",
            "action": "logistics_inventory.rop",
            "rop": rop,
            "markdown": "\n".join(md)
        }

    elif action in ("abc", "pareto", "clasificacion_abc"):
        raw_items = parameters.get("items") or [
            {"code": "SKU-01", "name": "Servidor IA Stark Edge", "demand": 120, "cost": 4500000},
            {"code": "SKU-02", "name": "Llavero Criptográfico NFC", "demand": 1200, "cost": 65000},
            {"code": "SKU-03", "name": "Terminal Contactless Bre-B", "demand": 450, "cost": 320000},
            {"code": "SKU-04", "name": "Manual Técnico Impreso", "demand": 80, "cost": 25000}
        ]
        abc = logistics_inventory_service.classify_abc(raw_items)
        md = [
            "# 📊 CLASIFICACIÓN DE INVENTARIOS ABC (LEY DE PARETO)",
            f"- **Total SKUs**: `{abc['total_skus']}` | **Valor Total Anual**: `${abc['total_value']:,.2f} COP`",
            f"- **Zona A (Estratégicos)**: `{abc['zone_counts']['A']} SKUs`",
            f"- **Zona B (Moderados)**: `{abc['zone_counts']['B']} SKUs`",
            f"- **Zona C (Menores)**: `{abc['zone_counts']['C']} SKUs`",
            "",
            "| SKU | Producto | Valor Anual | % Valor | % Acumulado | Zona |",
            "| :--- | :--- | :--- | :---: | :---: | :---: |"
        ]
        for it in abc["classified_items"]:
            md.append(f"| `{it['code']}` | {it['name']} | ${it['annual_value']:,.2f} | {it['value_pct']}% | {it['cumulative_pct']}% | **Zona {it['zone']}** |")

        return {
            "status": "success",
            "action": "logistics_inventory.abc",
            "abc": abc,
            "markdown": "\n".join(md)
        }

    else:  # eoq
        d = float(parameters.get("annual_demand") or parameters.get("demanda_anual") or 5000.0)
        s = float(parameters.get("order_cost") or parameters.get("costo_pedido") or 150000.0)
        h = float(parameters.get("holding_cost") or parameters.get("costo_mantenimiento") or 12000.0)
        c = float(parameters.get("unit_cost") or parameters.get("costo_unitario") or 85000.0)

        eoq = logistics_inventory_service.calculate_eoq(
            annual_demand=d,
            order_cost=s,
            holding_cost=h,
            unit_cost=c
        )
        report = logistics_inventory_service.format_markdown_report(eoq)
        return {
            "status": "success",
            "action": "logistics_inventory.eoq",
            "eoq": eoq,
            "markdown": report
        }
