# -*- coding: utf-8 -*-
"""
Action handler for Dividend Screener & Tight Budget Portfolio Allocator.
Filters high-dividend paying stocks in Colombia (BVC) and Wall Street (US),
optimizing allocation for modest budgets and calculating DRIP compounding.
"""

from typing import Any, Dict
from app.services.dividend_screener_service import dividend_screener_service


def dividend_screener_action(parameters: Dict[str, Any]) -> str:
    market = str(parameters.get("market", "BVC")).strip().upper()
    default_budget = 500000.0 if market == "BVC" else 250.0
    budget = float(parameters.get("budget", default_budget))
    min_yield = float(parameters.get("min_yield_pct", 5.0))
    reinvest = bool(parameters.get("reinvest_dividends", True))
    years = int(parameters.get("projection_years", 5))

    res = dividend_screener_service.screen_dividend_stocks(
        budget=budget,
        market=market,
        min_yield_pct=min_yield,
        reinvest_dividends=reinvest,
        projection_years=years
    )

    cur = res["currency"]
    if res.get("status") == "INSUFFICIENT_BUDGET":
        cheap = res.get("cheapest_alternative", {})
        return (
            f"💰 **RADAR DE ACCIONES CON DIVIDENDOS (PRESUPUESTO AJUSTADO)**\n\n"
            f"⚠️ **Aviso de Capital Insuficiente:**\n"
            f"{res['recommendation']}\n"
            f"• Alternativa más económica: **{cheap.get('ticker')}** a {cur} ${cheap.get('price', 0):,.2f} con dividendo de {cheap.get('dividend_yield_pct', 0)}%."
        )

    summ = res["summary"]
    lines = [
        f"💰 **RADAR DE ACCIONES CON DIVIDENDOS & PORTAFOLIO DE PRESUPUESTO AJUSTADO**\n",
        f"• **Mercado:** {res['market']} | **Presupuesto Asignado:** {cur} ${res['budget']:,.2f}",
        f"• **Capital Invertido:** {cur} ${summ['total_invested']:,.2f} | **Saldo Líquido Remanente:** {cur} ${summ['cash_remaining']:,.2f}",
        f"• **Rendimiento por Dividendo Ponderado:** **{summ['weighted_yield_pct']:.2f}% Anual**",
        f"• **Flujo Anual Estimado de Dividendos:** **{cur} ${summ['expected_annual_dividend']:,.2f}** (Promedio mensual: {cur} ${summ['expected_monthly_average']:,.2f})\n",
        f"📋 **DISTRIBUCIÓN SUGERIDA DE ACCIONES:**"
    ]

    for item in res["portfolio"]:
        lines.append(
            f"  - **{item['ticker']}** ({item['name']}): **{item['shares_to_buy']} acciones** a {cur} ${item['price_per_share']:,.2f} "
            f"(Total: {cur} ${item['total_cost']:,.2f}) | Yield: {item['dividend_yield_pct']}% | Ingreso Anual: {cur} ${item['annual_dividend_income']:,.2f} "
            f"[{item['payout_frequency']}]"
        )

    lines.append("\n📈 **PROYECCIÓN DE INTERÉS COMPUESTO CON REINVERSIÓN (DRIP):**")
    for proj in res["drip_projections"]:
        lines.append(
            f"  • **Año {proj['year']}:** Portafolio Proyectado: {cur} ${proj['projected_portfolio_value']:,.2f} | "
            f"Dividendo Anual ese año: {cur} ${proj['projected_annual_dividend']:,.2f}"
        )

    lines.append(f"\n💡 **Dictamen Estratégico:** {res['strategy_advice']}")
    return "\n".join(lines)
