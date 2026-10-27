# -*- coding: utf-8 -*-
"""
Pirámide DuPont, Altman Z''-Score (Mercados Emergentes) & Valor Económico Agregado (EVA) Service.
Provides institutional corporate finance diagnostics:
1. 3-Step & 5-Step DuPont ROE Decomposition (Margin, Turnover, Leverage, Tax & Interest Burden)
2. Altman Z''-Score for Non-Manufacturing & Emerging Markets (Ley 1116 de 2006 Solvency Radar)
3. Economic Value Added (EVA = NOPAT - Invested Capital * WACC) & ROIC vs WACC Spread
"""

from datetime import datetime
from typing import Any, Dict, List, Optional


class DupontAltmanService:
    """Motor de diagnóstico financiero DuPont, Altman Z''-Score y EVA."""

    def analyze_corporate_performance(
        self,
        company_name: str = "Grupo Empresarial Andino S.A.S.",
        revenue: float = 1200000000.0,
        ebit: float = 216000000.0,
        ebt: Optional[float] = None,
        net_income: float = 126000000.0,
        total_assets: float = 950000000.0,
        total_equity: float = 475000000.0,
        working_capital: float = 220000000.0,
        retained_earnings: float = 190000000.0,
        invested_capital: Optional[float] = None,
        wacc_pct: float = 12.5,
        effective_tax_rate_pct: float = 35.0,
        currency: str = "COP"
    ) -> Dict[str, Any]:
        rev = max(1.0, float(revenue))
        assets = max(1.0, float(total_assets))
        equity = max(1.0, float(total_equity))
        liabilities = max(1.0, assets - equity)
        ebit_val = float(ebit)
        ebt_val = float(ebt) if ebt is not None else ebit_val * 0.85
        net_inc = float(net_income)
        wc = float(working_capital)
        re = float(retained_earnings)
        inv_cap = float(invested_capital) if invested_capital is not None and invested_capital > 0 else assets * 0.85
        wacc = max(0.1, float(wacc_pct))
        tax_rate = max(0.0, min(90.0, float(effective_tax_rate_pct)))

        # 1. DuPont 3-Step & 5-Step
        net_margin_pct = round((net_inc / rev) * 100.0, 2)
        asset_turnover = round(rev / assets, 3)
        equity_multiplier = round(assets / equity, 3)
        roe_pct = round((net_inc / equity) * 100.0, 2)
        roa_pct = round((net_inc / assets) * 100.0, 2)

        tax_burden = round(net_inc / max(1.0, abs(ebt_val)), 3)
        interest_burden = round(ebt_val / max(1.0, abs(ebit_val)), 3)
        ebit_margin_pct = round((ebit_val / rev) * 100.0, 2)

        if net_margin_pct >= 12.0:
            primary_driver = "Margen Neto (Diferenciación & Pricing Power)"
        elif asset_turnover >= 1.3:
            primary_driver = "Rotación de Activos (Eficiencia Operativa & Volumen)"
        elif equity_multiplier >= 2.2:
            primary_driver = "Apalancamiento Financiero (Multiplicador de Capital)"
        else:
            primary_driver = "Equilibrio Operativo Moderado"

        # 2. Altman Z''-Score (Emerging Markets Model: Z'' = 3.25 + 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4)
        x1 = wc / assets
        x2 = re / assets
        x3 = ebit_val / assets
        x4 = equity / liabilities

        z_double_prime = round(3.25 + (6.56 * x1) + (3.26 * x2) + (6.72 * x3) + (1.05 * x4), 2)

        if z_double_prime > 5.85:
            altman_zone = "ZONA SEGURA (Solvencia Sólida)"
            bankruptcy_risk = "Muy Bajo (< 5%)"
        elif z_double_prime >= 4.15:
            altman_zone = "ZONA GRIS (Vigilancia Preventiva)"
            bankruptcy_risk = "Moderado (15% - 25%)"
        else:
            altman_zone = "ZONA DE ALERTA (Riesgo Ley 1116)"
            bankruptcy_risk = "Alto (> 45%)"

        # 3. Economic Value Added (EVA)
        nopat = round(ebit_val * (1.0 - (tax_rate / 100.0)), 2)
        roic_pct = round((nopat / max(1.0, inv_cap)) * 100.0, 2)
        eva_spread_pct = round(roic_pct - wacc, 2)
        capital_charge = round(inv_cap * (wacc / 100.0), 2)
        eva_amount = round(nopat - capital_charge, 2)

        if eva_amount > 0:
            value_status = "CREACIÓN DE VALOR ECONÓMICO (EVA Positivo)"
        else:
            value_status = "DESTRUCCIÓN DE VALOR ECONÓMICO (ROIC < WACC)"

        # 4. Strategic Recommendations
        recommendations: List[str] = []
        if eva_amount > 0:
            recommendations.append(
                f"Creación de valor confirmada: ROIC ({roic_pct}%) supera el WACC ({wacc}%) en +{eva_spread_pct}% "
                f"generando ${eva_amount:,.0f} {currency} de EVA neto."
            )
        else:
            recommendations.append(
                f"Alerta de EVA negativo (${eva_amount:,.0f} {currency}): Optimizar capital invertido o incrementar "
                f"margen EBIT ({ebit_margin_pct}%) para superar el costo de capital ({wacc}%)."
            )

        if z_double_prime < 5.85:
            recommendations.append(
                f"Fortalecer solvencia Altman Z'' ({z_double_prime}): Incrementar capital de trabajo neto y "
                f"capitalizar utilidades retenidas para blindar liquidez."
            )
        else:
            recommendations.append(
                f"Blindaje patrimonial sobresaliente (Z'' = {z_double_prime}): Capacidad holgada de endeudamiento "
                f"estratégico sin comprometer solvencia."
            )

        recommendations.append(
            f"Palanca DuPont dominante: {primary_driver} (ROE: {roe_pct}% = Margen {net_margin_pct}% × "
            f"Rotación {asset_turnover}x × Apalancamiento {equity_multiplier}x)."
        )

        return {
            "company_name": company_name,
            "currency": currency,
            "dupont_analysis": {
                "roe_pct": roe_pct,
                "roa_pct": roa_pct,
                "net_margin_pct": net_margin_pct,
                "asset_turnover": asset_turnover,
                "equity_multiplier": equity_multiplier,
                "ebit_margin_pct": ebit_margin_pct,
                "tax_burden_ratio": tax_burden,
                "interest_burden_ratio": interest_burden,
                "primary_driver": primary_driver
            },
            "altman_z_score": {
                "z_double_prime": z_double_prime,
                "zone": altman_zone,
                "bankruptcy_probability_estimate": bankruptcy_risk,
                "ratios": {
                    "x1_working_capital_to_assets": round(x1, 3),
                    "x2_retained_earnings_to_assets": round(x2, 3),
                    "x3_ebit_to_assets": round(x3, 3),
                    "x4_equity_to_liabilities": round(x4, 3)
                }
            },
            "eva_analysis": {
                "nopat": nopat,
                "invested_capital": round(inv_cap, 2),
                "wacc_pct": wacc,
                "roic_pct": roic_pct,
                "eva_spread_pct": eva_spread_pct,
                "capital_charge": capital_charge,
                "eva_amount": eva_amount,
                "value_creation_status": value_status
            },
            "strategic_recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }


dupont_altman_service = DupontAltmanService()
