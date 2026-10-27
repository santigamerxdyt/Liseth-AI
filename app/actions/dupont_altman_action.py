# -*- coding: utf-8 -*-
"""
Action handler for DuPont ROE Pyramid, Altman Z''-Score, and Economic Value Added (EVA).
"""

from typing import Any, Dict
from app.services.dupont_altman_service import dupont_altman_service


def dupont_altman_action(parameters: Dict[str, Any]) -> str:
    company_name = parameters.get("company_name", "Grupo Empresarial Andino S.A.S.")
    revenue = float(parameters.get("revenue", 1200000000.0))
    ebit = float(parameters.get("ebit", 216000000.0))
    net_income = float(parameters.get("net_income", 126000000.0))
    total_assets = float(parameters.get("total_assets", 950000000.0))
    total_equity = float(parameters.get("total_equity", 475000000.0))
    working_capital = float(parameters.get("working_capital", 220000000.0))
    retained_earnings = float(parameters.get("retained_earnings", 190000000.0))
    wacc_pct = float(parameters.get("wacc_pct", 12.5))
    currency = parameters.get("currency", "COP")

    res = dupont_altman_service.analyze_corporate_performance(
        company_name=company_name,
        revenue=revenue,
        ebit=ebit,
        net_income=net_income,
        total_assets=total_assets,
        total_equity=total_equity,
        working_capital=working_capital,
        retained_earnings=retained_earnings,
        wacc_pct=wacc_pct,
        currency=currency
    )

    dup = res["dupont_analysis"]
    alt = res["altman_z_score"]
    eva = res["eva_analysis"]
    recs = "\n".join([f"  • {r}" for r in res["strategic_recommendations"]])

    return (
        f"🏛️ **PIRÁMIDE DUPONT, ALTMAN Z''-SCORE & VALOR ECONÓMICO AGREGADO (EVA)**\n\n"
        f"• **Compañía:** {res['company_name']}\n"
        f"• **ROE DuPont:** **{dup['roe_pct']}%** (ROA: {dup['roa_pct']}% | Driver: {dup['primary_driver']})\n"
        f"• **Descomposición 3-Factores:** Margen Neto {dup['net_margin_pct']}% × Rotación {dup['asset_turnover']}x × Apalancamiento {dup['equity_multiplier']}x\n"
        f"• **Altman Z''-Score (Emergentes):** **{alt['z_double_prime']}** → **{alt['zone']}** (Riesgo Insolvencia: {alt['bankruptcy_probability_estimate']})\n"
        f"• **EVA (Valor Económico Agregado):** **${eva['eva_amount']:,.2f} {currency}** ({eva['value_creation_status']})\n"
        f"• **Spread de Rentabilidad:** ROIC {eva['roic_pct']}% vs WACC {eva['wacc_pct']}% (Spread: {eva['eva_spread_pct']:+}%)\n"
        f"• **Dictamen Ejecutivo:**\n{recs}"
    )
