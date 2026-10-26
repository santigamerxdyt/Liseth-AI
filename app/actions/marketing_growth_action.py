# -*- coding: utf-8 -*-
"""
Action handler for Marketing & Digital Growth Engine.
"""

from typing import Any, Dict
from app.services.marketing_growth_service import marketing_growth_service


def marketing_growth_action(parameters: Dict[str, Any]) -> str:
    action_type = parameters.get("action_type", "unit_economics")

    if action_type in ("unit_economics", "cac_ltv", "saas_metrics"):
        cac = float(parameters.get("cac", 150000.0))
        arpu = float(parameters.get("arpu", 85000.0))
        churn = float(parameters.get("churn_monthly_pct", 3.5))
        margin = float(parameters.get("gross_margin_pct", 80.0))
        currency = parameters.get("currency", "COP")

        res = marketing_growth_service.calculate_unit_economics(
            cac=cac, arpu=arpu, churn_monthly_pct=churn, gross_margin_pct=margin, currency=currency
        )
        return (
            f"📈 **DIAGNÓSTICO DE UNIT ECONOMICS & CRECIMIENTO (MKT 360)**\n\n"
            f"• **CAC (Costo Adquisición):** {res['cac']:,.2f} {currency}\n"
            f"• **ARPU Mensual:** {res['arpu']:,.2f} {currency} (Margen Bruto: {res['gross_margin_pct']}%)\n"
            f"• **Churn Mensual:** {res['churn_monthly_pct']}% (Churn Anualizado: {res['annual_churn_pct']}%)\n"
            f"• **Vida Media del Cliente:** {res['customer_lifetime_months']} meses\n"
            f"• **LTV (Lifetime Value):** {res['ltv']:,.2f} {currency}\n"
            f"• **Ratio LTV / CAC:** **{res['ltv_cac_ratio']}x** (Benchmark ideal: > 3.0x)\n"
            f"• **Recuperación de CAC (Payback):** **{res['cac_payback_months']} meses**\n"
            f"• **Estado:** {res['diagnostic']}"
        )

    elif action_type in ("funnel", "embudo_ventas", "conversion"):
        impr = int(parameters.get("impressions", 50000))
        clicks = int(parameters.get("clicks", 1800))
        mql = int(parameters.get("leads_mql", 160))
        sql = int(parameters.get("opportunities_sql", 48))
        won = int(parameters.get("closed_won", 16))

        res = marketing_growth_service.diagnose_funnel(
            impressions=impr, clicks=clicks, leads_mql=mql, opportunities_sql=sql, closed_won=won
        )
        rates = res["conversion_rates"]
        return (
            f"🎯 **AUDITORÍA DE EMBUDO DE CONVERSIÓN & VENTAS (FUNNEL)**\n\n"
            f"• **Atracción (CTR):** {rates['ctr_pct']}% ({clicks:,} clics / {impr:,} impresiones)\n"
            f"• **Captura (Click a MQL):** {rates['click_to_mql_pct']}% ({mql:,} leads)\n"
            f"• **Calificación (MQL a SQL):** {rates['mql_to_sql_pct']}% ({sql:,} oportunidades calificados)\n"
            f"• **Cierre (Win Rate SQL):** {rates['sql_to_won_pct']}% ({won:,} ventas cerradas)\n"
            f"• **Conversión Global:** {rates['overall_conversion_pct']}%\n"
            f"• **Diagnóstico de Cuello de Botella:** {res['bottleneck_summary']}"
        )

    elif action_type in ("roas", "pauta", "canales", "attribution"):
        channels = parameters.get("channels", [
            {"channel": "Google Search Ads", "spend": 2500000, "revenue": 10500000, "conversions": 35},
            {"channel": "Meta Ads (Instagram)", "spend": 1800000, "revenue": 5400000, "conversions": 24},
            {"channel": "LinkedIn B2B", "spend": 1200000, "revenue": 4800000, "conversions": 8}
        ])
        res = marketing_growth_service.calculate_roas_and_attribution(channels=channels)
        ch_lines = "\n".join([
            f"  - **{c['channel']}:** Gasto: ${c['spend']:,.0f} | Retorno: ${c['revenue']:,.0f} | **ROAS: {c['roas']}x** | CPA: ${c['cpa']:,.0f}"
            for c in res["channels"]
        ])
        return (
            f"📊 **ATRIBUCIÓN DE PUTA & ROAS MULTICANAL**\n\n"
            f"• **Inversión Total:** ${res['total_spend']:,.2f} COP\n"
            f"• **Ingresos Generados:** ${res['total_revenue']:,.2f} COP\n"
            f"• **ROAS Consolidado (Blended):** **{res['blended_roas']}x**\n"
            f"• **CAC Consolidado:** ${res['blended_cac']:,.2f} COP por cliente\n"
            f"• **Desglose por Canal:**\n{ch_lines}\n"
            f"• **Dictamen:** {res['recommendation']}"
        )

    return f"Acción de marketing '{action_type}' no reconocida."
