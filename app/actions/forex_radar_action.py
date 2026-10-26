# -*- coding: utf-8 -*-
"""
Action handler for Forex Radar, Exchange Spreads, and Forward Hedging.
"""

from typing import Any, Dict
from app.services.forex_radar_service import forex_radar_service


def forex_radar_action(parameters: Dict[str, Any]) -> str:
    action_type = parameters.get("action_type", "radar")

    if action_type in ("radar", "trm", "divisas", "dolar", "cotizacion"):
        base_trm = float(parameters.get("base_usd_cop", 4185.0))
        res = forex_radar_service.get_forex_radar(base_usd_cop=base_trm)
        return (
            f"💱 **RADAR CAMBIARIO Y ARBITRAJE DE DIVISAS (COLOMBIA)**\n\n"
            f"• **TRM Oficial BanRep:** ${res['trm_oficial_cop']:,.2f} COP\n"
            f"• **Dólar Cripto USDT (P2P):** ${res['dolar_usdt_p2p_cop']:,.2f} COP\n"
            f"• **Dólar Tarjeta Crédito:** ${res['dolar_tarjeta_cop']:,.2f} COP (Spread: +${res['spread_tarjeta_cop']:,.2f})\n"
            f"• **Euro Oficial (EUR/COP):** ${res['euro_cop']:,.2f} COP\n"
            f"• **Efectivo Ventanilla (Venta/Compra):** ${res['efectivo_venta_cop']:,.2f} / ${res['efectivo_compra_cop']:,.2f} COP\n"
            f"• **Consejo de Eficiencia Cambiaria:** {res['arbitrage_tip']}"
        )

    elif action_type in ("hedge", "forward", "cobertura", "derivado"):
        amount = float(parameters.get("amount_usd", 25000.0))
        spot = float(parameters.get("spot_rate_cop", 4185.0))
        days = int(parameters.get("days_forward", 90))
        r_cop = float(parameters.get("rate_cop_annual_pct", 9.75))
        r_usd = float(parameters.get("rate_usd_annual_pct", 4.50))

        res = forex_radar_service.simulate_forward_hedge(
            amount_usd=amount, spot_rate_cop=spot, days_forward=days,
            rate_cop_annual_pct=r_cop, rate_usd_annual_pct=r_usd
        )
        return (
            f"🛡️ **SIMULADOR DE COBERTURA CAMBIARIA FORWARD (HEDGING)**\n\n"
            f"• **Monto en Riesgo:** ${res['amount_usd']:,.2f} USD ({res['days_forward']} días plazo)\n"
            f"• **Tasa Spot Actual:** ${res['spot_rate_cop']:,.2f} COP\n"
            f"• **Tasa Forward Teórica:** **${res['forward_rate_cop']:,.2f} COP**\n"
            f"• **Prima de Devaluación:** +${res['premium_devaluation_cop']:,.2f} COP (+{res['premium_pct']}%)\n"
            f"• **Desembolso Actual (Spot):** ${res['total_spot_cop']:,.2f} COP\n"
            f"• **Costo Total Cobertura Forward:** ${res['total_forward_cop']:,.2f} COP\n"
            f"• **Dictamen Financiero:** {res['strategic_recommendation']}"
        )

    return f"Acción cambiaria '{action_type}' no reconocida."
