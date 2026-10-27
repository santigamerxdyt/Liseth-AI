# -*- coding: utf-8 -*-
"""
Action handler for Pricing Strategy & Demand Elasticity (PED).
Evaluates price elasticity, Lerner optimal price markup, and simulates revenue/margin curves.
"""

from typing import Any, Dict
from app.services.pricing_elasticity_service import pricing_elasticity_service


def pricing_elasticity_action(parameters: Dict[str, Any]) -> str:
    name = str(parameters.get("product_name", "Producto / Servicio")).strip()
    price = float(parameters.get("current_price", 50000.0))
    mc = float(parameters.get("unit_marginal_cost", 25000.0))
    units = float(parameters.get("current_monthly_units", 1000.0))
    ed = parameters.get("price_elasticity")
    ed_val = float(ed) if ed is not None else None
    test_p = parameters.get("test_price")
    test_p_val = float(test_p) if test_p is not None else None
    test_q = parameters.get("test_volume")
    test_q_val = float(test_q) if test_q is not None else None
    currency = str(parameters.get("currency", "COP")).strip().upper()

    res = pricing_elasticity_service.evaluate_pricing_strategy(
        product_name=name,
        current_price=price,
        unit_marginal_cost=mc,
        current_monthly_units=units,
        price_elasticity=ed_val,
        test_price=test_p_val,
        test_volume=test_q_val,
        currency=currency
    )

    c = res["current_state"]
    e = res["elasticity_analysis"]
    o = res["optimization"]

    lines = [
        f"🏷️ **ESTRATEGIA DE PRECIOS & ELASTICIDAD DE DEMANDA — {res['product_name'].upper()}**\n",
        f"• **Precio Actual:** {currency} ${c['price']:,.2f} | **Costo Marginal:** {currency} ${c['unit_marginal_cost']:,.2f} (Margen: {c['margin_pct']}%)",
        f"• **Volumen Mensual:** {c['monthly_units']:,.0f} unidades | **Ingresos Mensuales:** {currency} ${c['monthly_revenue']:,.2f}\n",
        f"📊 **DIAGNÓSTICO ECONÓMICO DE ELASTICIDAD:**",
        f"• **Coeficiente de Elasticidad (Ed):** **{e['coefficient_ed']}** ({e['classification']})",
        f"• **Comportamiento del Mercado:** {e['diagnosis']}",
        f"• **Plan Estratégico:** {e['action_plan']}\n",
        f"🎯 **OPTIMIZACIÓN DE PRECIO & MARGEN DE CONTRIBUCIÓN:**",
        f"• **Precio Teórico Óptimo (Índice de Lerner):** **{currency} ${o['optimal_theoretical_price']:,.2f}** (Markup óptimo: +{o['optimal_markup_pct']}%)",
        f"• **Ajuste Simulado Recomendado:** **{o['recommended_price_change_pct']:+}%** (Nuevo Precio: {currency} ${o['best_simulated_price']:,.2f})",
        f"• **Ganancia Potencial de Margen Bruto:** **+{currency} ${o['potential_margin_gain']:,.2f}** al mes\n",
        f"📈 **SENSIBILIDAD ANTE VARIACIONES DE PRECIO:**"
    ]

    for sc in res["simulation_curve"]:
        current_tag = " (ACTUAL)" if sc["is_current"] else ""
        lines.append(
            f"  • {sc['price_change_pct']:+}%: Precio ${sc['simulated_price']:,.2f} | Unidades: {sc['projected_units']:,.0f} | "
            f"Margen: ${sc['projected_margin']:,.2f} (Dif: ${sc['delta_margin']:+,.2f}){current_tag}"
        )

    return "\n".join(lines)
