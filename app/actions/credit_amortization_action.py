# -*- coding: utf-8 -*-
"""
Action handler for Advanced Credit Amortization & Debt Optimization.
Calculates French vs German schedules, usury compliance in Colombia, and extra prepayment savings.
"""

from typing import Any, Dict
from app.services.credit_amortization_service import credit_amortization_service


def credit_amortization_action(parameters: Dict[str, Any]) -> str:
    name = str(parameters.get("loan_name", "Crédito Comercial / Libre Inversión")).strip()
    principal = float(parameters.get("principal_amount", 30000000.0))
    rate_ea = float(parameters.get("annual_interest_rate_ea_pct", 19.5))
    term = int(parameters.get("term_months", 36))
    sys_type = str(parameters.get("amortization_system", "french")).strip()
    extra_pay = float(parameters.get("extra_monthly_prepayment", 0.0))
    strategy = str(parameters.get("prepayment_strategy", "reduce_term")).strip()
    currency = str(parameters.get("currency", "COP")).strip().upper()

    res = credit_amortization_service.calculate_amortization(
        loan_name=name,
        principal_amount=principal,
        annual_interest_rate_ea_pct=rate_ea,
        term_months=term,
        amortization_system=sys_type,
        extra_monthly_prepayment=extra_pay,
        prepayment_strategy=strategy,
        currency=currency
    )

    t = res["loan_terms"]
    u = res["usury_compliance"]
    p = res["payment_summary"]
    prep = res["prepayment_optimization"]
    comp = res["system_comparison"]

    lines = [
        f"💳 **SIMULADOR DE CRÉDITO & OPTIMIZACIÓN DE DEUDA — {res['loan_name'].upper()}**\n",
        f"• **Monto del Préstamo:** {currency} ${t['principal_amount']:,.2f} | **Sistema:** {res['amortization_system']}",
        f"• **Tasa de Interés:** **{t['annual_interest_rate_ea_pct']}% E.A.** (Tasa mensual periódica: {t['monthly_periodic_rate_pct']}%)",
        f"• **Plazo Contratado:** {t['contracted_term_months']} meses | **Plazo Efectivo con Abonos:** **{t['effective_term_months']} meses**",
        f"• **Conformidad Legal (SuperFinanciera):** {u['status_note']}\n",
        f"📋 **RESUMEN FINANCIERO DEL CRÉDITO:**",
        f"• **Cuota Mensual Inicial:** **{currency} ${p['initial_monthly_payment']:,.2f}**",
        f"• **Total Capital Amortizado:** {currency} ${p['total_principal_paid']:,.2f}",
        f"• **Total Intereses Pagados:** **{currency} ${p['total_interest_paid']:,.2f}** (Sobrecosto financiero: {p['interest_to_principal_ratio_pct']}%)",
        f"• **Desembolso Total Acumulado:** {currency} ${p['total_repayment_amount']:,.2f}\n",
        f"💡 **ESTRATEGIA DE PREPAGOS & ALIVIO DE DEUDA:**",
        f"• {prep['advice']}\n",
        f"⚖️ **COMPARATIVO DE SISTEMAS (FRANCÉS VS ALEMÁN):**",
        f"• Intereses Totales Francés (Cuota Fija): {currency} ${comp['french_total_interest']:,.2f}",
        f"• Intereses Totales Alemán (Abono Constante): {currency} ${comp['german_total_interest']:,.2f}",
        f"• {comp['verdict']}"
    ]

    return "\n".join(lines)
