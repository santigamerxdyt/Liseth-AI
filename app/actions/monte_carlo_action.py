# -*- coding: utf-8 -*-
"""
Action handler for Stochastic Monte Carlo Simulation & Capital Stress Testing.
Simulates thousands of trials for corporate investment projects, calculating
probability of positive NPV (VAN > 0), Value at Risk (VaR 95% & 99%), and capital resilience.
"""

from typing import Any, Dict
from app.services.monte_carlo_service import monte_carlo_service


def monte_carlo_action(parameters: Dict[str, Any]) -> str:
    name = str(parameters.get("project_name", "Proyecto Estratégico")).strip()
    inv = float(parameters.get("initial_investment", 50000000.0))
    mean_rev = float(parameters.get("mean_annual_revenue", 32000000.0))
    std_rev = float(parameters.get("std_annual_revenue", 6000000.0))
    fixed_costs = float(parameters.get("fixed_operating_costs", 10000000.0))
    var_ratio = float(parameters.get("variable_costs_ratio", 0.25))
    wacc = float(parameters.get("discount_rate_wacc", 0.12))
    years = int(parameters.get("project_years", 5))
    trials = int(parameters.get("simulations_count", 5000))
    currency = str(parameters.get("currency", "COP")).strip().upper()

    res = monte_carlo_service.simulate_project_capital(
        project_name=name,
        initial_investment=inv,
        mean_annual_revenue=mean_rev,
        std_annual_revenue=std_rev,
        fixed_operating_costs=fixed_costs,
        variable_costs_ratio=var_ratio,
        discount_rate_wacc=wacc,
        project_years=years,
        simulations_count=trials,
        currency=currency
    )

    m = res["metrics"]
    p = res["percentiles"]
    r = res["risk_assessment"]

    return (
        f"🎲 **SIMULACIÓN ESTOCÁSTICA MONTE CARLO & STRESS TESTING — {res['project_name'].upper()}**\n\n"
        f"• **Iteraciones Ejecutadas:** {res['simulations_count']:,} simulaciones a {res['project_years']} años | WACC: {res['parameters']['discount_rate_wacc_pct']}%\n"
        f"• **Inversión Inicial:** {currency} ${res['parameters']['initial_investment']:,.2f}\n"
        f"• **Ingreso Anual Esperado:** {currency} ${res['parameters']['mean_annual_revenue']:,.2f} (± Desv: ${res['parameters']['std_annual_revenue']:,.2f})\n\n"
        f"🎯 **DICTAMEN DE RIESGO & RESILIENCIA DE CAPITAL:**\n"
        f"• **Estado:** **{r['resilience_status']}** [{r['risk_tier']}]\n"
        f"• **Probabilidad de VAN Positivo [P(VAN > 0)]:** **{m['prob_positive_npv_pct']}%**\n"
        f"• **VAN Promedio (Esperado):** **{currency} ${m['expected_npv_mean']:,.2f}**\n"
        f"• **VAN Mediana:** {currency} ${m['median_npv']:,.2f}\n"
        f"• **Volatilidad / Desviación Estándar:** {currency} ${m['std_dev_npv']:,.2f}\n\n"
        f"🛡️ **MÉTRICAS DE COLA & VALUE AT RISK (VaR):**\n"
        f"• **Peor Escenario 5% (Percentil 5 - Bearish):** {currency} ${p['p5_bearish']:,.2f}\n"
        f"• **Value at Risk (VaR 95% Confianza):** **{currency} ${m['var_95_cop']:,.2f}**\n"
        f"• **Value at Risk Extremo (VaR 99% Confianza):** {currency} ${m['var_99_cop']:,.2f}\n"
        f"• **Escenario Favorable 95% (Percentil 95 - Bullish):** {currency} ${p['p95_bullish']:,.2f}\n\n"
        f"💡 **Recomendación Estratégica:** {r['strategic_advice']}"
    )
