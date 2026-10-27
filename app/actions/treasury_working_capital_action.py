# -*- coding: utf-8 -*-
"""
Action handler for Treasury, Working Capital (KTNO), and Factoring.
"""

from typing import Any, Dict
from app.services.treasury_working_capital_service import treasury_working_capital_service


def treasury_working_capital_action(parameters: Dict[str, Any]) -> str:
    action_type = parameters.get("action_type", "ccc")

    if action_type in ("ccc", "ciclo_efectivo", "working_capital", "ktno"):
        dso = float(parameters.get("dso_receivables_days", 45.0))
        dio = float(parameters.get("dio_inventory_days", 35.0))
        dpo = float(parameters.get("dpo_payables_days", 50.0))
        rev = float(parameters.get("annual_revenue_cop", 1500000000.0))
        cogs = float(parameters.get("annual_cogs_cop", 900000000.0))

        res = treasury_working_capital_service.calculate_cash_conversion_cycle(
            dso_receivables_days=dso, dio_inventory_days=dio, dpo_payables_days=dpo,
            annual_revenue_cop=rev, annual_cogs_cop=cogs
        )
        return (
            f"💰 **CICLO DE CONVERSIÓN DE EFECTIVO (CCC) & CAPITAL DE TRABAJO (KTNO)**\n\n"
            f"• **Días de Cobro a Clientes (DSO):** {res['dso_receivables_days']} días (${res['cuentas_por_cobrar_cop']:,.0f} COP)\n"
            f"• **Días de Rotación Inventario (DIO):** {res['dio_inventory_days']} días (${res['inventarios_cop']:,.0f} COP)\n"
            f"• **Días de Pago Proveedores (DPO):** {res['dpo_payables_days']} días (${res['cuentas_por_pagar_cop']:,.0f} COP)\n"
            f"• **Ciclo de Conversión del Efectivo (CCC):** **{res['ccc_days']} días** (Fórmula: DSO + DIO - DPO)\n"
            f"• **Capital de Trabajo Neto Operativo (KTNO):** **${res['ktno_cop']:,.2f} COP**\n"
            f"• **Diagnóstico de Eficiencia de Caja:** {res['efficiency_diagnosis']}"
        )

    elif action_type in ("factoring", "descuento_facturas", "radian", "anticipo"):
        face_val = float(parameters.get("invoice_face_value_cop", 45000000.0))
        days = int(parameters.get("days_to_maturity", 60))
        rate_mo = float(parameters.get("monthly_discount_rate_pct", 1.45))
        fee = float(parameters.get("platform_fee_pct", 0.30))

        res = treasury_working_capital_service.simulate_factoring_discount(
            invoice_face_value_cop=face_val, days_to_maturity=days,
            monthly_discount_rate_pct=rate_mo, platform_fee_pct=fee
        )
        return (
            f"📑 **SIMULADOR DE FACTORING ELECTRÓNICO (DIAN / RADIAN)**\n\n"
            f"• **Valor Nominal de la Factura:** ${res['invoice_face_value_cop']:,.2f} COP\n"
            f"• **Plazo al Vencimiento:** {res['days_to_maturity']} días\n"
            f"• **Tasa de Descuento Mensual:** {res['monthly_discount_rate_pct']}% mensual\n"
            f"• **Costo Financiero de Descuento:** ${res['discount_cost_cop']:,.2f} COP\n"
            f"• **Comisión de Plataforma RADIAN:** ${res['platform_fee_cop']:,.2f} COP\n"
            f"• **Costo Total del Anticipo:** ${res['total_financing_cost_cop']:,.2f} COP\n"
            f"• **Liquidez Neta Recibida Hoy:** **${res['net_cash_received_cop']:,.2f} COP**\n"
            f"• **Tasa Efectiva Anual (E.A.):** **{res['effective_annual_rate_ea_pct']}% E.A.**\n"
            f"• **Dictamen:** {res['recommendation']}"
        )

    return f"Acción de tesorería '{action_type}' no reconocida."
