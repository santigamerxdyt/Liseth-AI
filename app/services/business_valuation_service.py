"""
Business & Startup Valuation Service for Liseth / JARVIS.
Tailored for Corporate Finance & Business Administration (UNAL Palmira):
- Discounted Cash Flow (DCF / Flujo de Caja Libre Descontado)
- Gordon-Shapiro Terminal Value (Perpetuity Growth Model)
- Enterprise Value (EV) & Equity Value (Valor Patrimonial)
- Comparable Multiples Valuation (EV/EBITDA & EV/Sales by Industry)
- Venture Capital Valuation Method (Pre-Money, Post-Money & Dilution)
"""
import uuid
from typing import Any, Dict, List, Optional

INDUSTRY_MULTIPLES = {
    "tech_saas": {
        "name": "Tecnología, Software & IA (SaaS)",
        "ev_ebitda": 12.0,
        "ev_ebitda_low": 9.0,
        "ev_ebitda_high": 16.0,
        "ev_sales": 4.0
    },
    "consultoria": {
        "name": "Consultoría Estratégica & Servicios Profesionales",
        "ev_ebitda": 6.5,
        "ev_ebitda_low": 5.0,
        "ev_ebitda_high": 8.5,
        "ev_sales": 1.5
    },
    "agroindustria": {
        "name": "Agroindustria & Biotecnología (Valle del Cauca)",
        "ev_ebitda": 5.5,
        "ev_ebitda_low": 4.0,
        "ev_ebitda_high": 7.0,
        "ev_sales": 0.9
    },
    "retail_ecommerce": {
        "name": "Comercio Minorista & E-commerce Digital",
        "ev_ebitda": 6.0,
        "ev_ebitda_low": 4.5,
        "ev_ebitda_high": 8.0,
        "ev_sales": 1.1
    }
}


class BusinessValuationService:
    def __init__(self):
        pass

    def valuation_dcf(
        self,
        projected_flows: List[float],
        wacc_discount_rate: float = 0.12,
        terminal_growth_g: float = 0.03,
        cash_balance: float = 0.0,
        total_debt: float = 0.0,
        currency: str = "COP"
    ) -> Dict[str, Any]:
        """
        Computes enterprise valuation via Discounted Free Cash Flow (DCF).
        """
        flows = [float(f) for f in projected_flows]
        k = float(wacc_discount_rate)
        g = float(terminal_growth_g)
        n = len(flows)

        if k <= g:
            raise ValueError("El costo de capital WACC debe ser estrictamente mayor a la tasa de crecimiento terminal (g).")

        # 1. Present value of explicit projection period
        pv_flows = 0.0
        annual_pv_table = []
        for t, flow in enumerate(flows, start=1):
            factor = 1.0 / ((1.0 + k) ** t)
            pv_f = flow * factor
            pv_flows += pv_f
            annual_pv_table.append({
                "year": t,
                "free_cash_flow": flow,
                "discount_factor": round(factor, 4),
                "discounted_value": round(pv_f, 2)
            })

        # 2. Terminal Value (Gordon-Shapiro)
        last_fcf = flows[-1] if flows else 0.0
        terminal_value = (last_fcf * (1.0 + g)) / (k - g)
        pv_terminal_value = terminal_value / ((1.0 + k) ** n)

        # 3. Enterprise Value & Equity Value
        enterprise_value = round(pv_flows + pv_terminal_value, 2)
        equity_value = round(enterprise_value + float(cash_balance) - float(total_debt), 2)

        return {
            "method": "DCF (Flujo de Caja Libre Descontado)",
            "currency": currency,
            "projection_years": n,
            "wacc_pct": round(k * 100, 2),
            "terminal_growth_g_pct": round(g * 100, 2),
            "pv_explicit_flows": round(pv_flows, 2),
            "terminal_value": round(terminal_value, 2),
            "pv_terminal_value": round(pv_terminal_value, 2),
            "enterprise_value_ev": enterprise_value,
            "cash_balance": round(float(cash_balance), 2),
            "total_debt": round(float(total_debt), 2),
            "equity_value": equity_value,
            "terminal_value_share_pct": round((pv_terminal_value / enterprise_value * 100.0), 1) if enterprise_value > 0 else 0,
            "annual_table": annual_pv_table
        }

    def valuation_multiples(
        self,
        ebitda: float,
        annual_revenue: float,
        industry_key: str = "tech_saas",
        currency: str = "COP"
    ) -> Dict[str, Any]:
        """
        Estimates company valuation based on industry EV/EBITDA and EV/Sales multiples.
        """
        ind = INDUSTRY_MULTIPLES.get(industry_key, INDUSTRY_MULTIPLES["tech_saas"])
        eb = max(0.0, float(ebitda))
        rev = max(0.0, float(annual_revenue))

        val_ebitda_base = round(eb * ind["ev_ebitda"], 2)
        val_ebitda_low = round(eb * ind["ev_ebitda_low"], 2)
        val_ebitda_high = round(eb * ind["ev_ebitda_high"], 2)

        val_sales = round(rev * ind["ev_sales"], 2)

        return {
            "method": "Múltiplos Comparables de Mercado",
            "industry": ind["name"],
            "currency": currency,
            "ebitda": eb,
            "annual_revenue": rev,
            "multiples_used": {
                "ev_ebitda_base": ind["ev_ebitda"],
                "ev_sales": ind["ev_sales"]
            },
            "valuation_by_ebitda": {
                "base": val_ebitda_base,
                "low_range": val_ebitda_low,
                "high_range": val_ebitda_high
            },
            "valuation_by_revenue": val_sales,
            "recommended_fair_value": val_ebitda_base if eb > 0 else val_sales
        }

    def valuation_venture_capital(
        self,
        target_exit_value: float,
        years_to_exit: int = 5,
        required_roi_multiple: float = 5.0,
        investment_amount: float = 200000000.0,
        currency: str = "COP"
    ) -> Dict[str, Any]:
        """
        VC Method: Calculates Post-Money and Pre-Money valuation from target exit price.
        """
        exit_val = float(target_exit_value)
        roi_mult = float(required_roi_multiple)
        inv = float(investment_amount)

        post_money = round(exit_val / roi_mult, 2) if roi_mult > 0 else 0.0
        pre_money = round(post_money - inv, 2)
        equity_share_pct = round((inv / post_money * 100.0), 2) if post_money > 0 else 0.0

        return {
            "method": "Venture Capital Method (VC)",
            "currency": currency,
            "target_exit_value": exit_val,
            "years_to_exit": int(years_to_exit),
            "required_roi_multiple": roi_mult,
            "investment_requested": inv,
            "post_money_valuation": post_money,
            "pre_money_valuation": pre_money,
            "investor_equity_share_pct": equity_share_pct,
            "founder_equity_share_pct": round(100.0 - equity_share_pct, 2)
        }

    def format_markdown_report(self, dcf_data: Dict[str, Any]) -> str:
        curr = dcf_data["currency"]
        md = [
            "# 💎 VALUACIÓN FINANCIERA DE EMPRESAS (MÉTODO DCF)",
            f"- **Valor de la Empresa (Enterprise Value - EV)**: **`${dcf_data['enterprise_value_ev']:,.2f} {curr}`**",
            f"- **Valor Patrimonial de los Accionistas (Equity Value)**: **`${dcf_data['equity_value']:,.2f} {curr}`**",
            f"- **Tasa de Descuento (WACC)**: `{dcf_data['wacc_pct']}%`",
            f"- **Tasa de Crecimiento a Perpetuidad ($g$)**: `{dcf_data['terminal_growth_g_pct']}%`",
            f"- **Valor Presente de Flujos Explícitos**: `${dcf_data['pv_explicit_flows']:,.2f} {curr}`",
            f"- **Valor Terminal Descontado**: `${dcf_data['pv_terminal_value']:,.2f} {curr}` ({dcf_data['terminal_value_share_pct']}% del EV)",
            f"- **Caja Neta / Deuda**: Caja `${dcf_data['cash_balance']:,.2f}` | Deuda `${dcf_data['total_debt']:,.2f}`",
            "",
            "> 💡 *Este valor representa el precio teórico de referencia para venta de acciones o entrada de socios capitalistas.*"
        ]
        return "\n".join(md)


business_valuation_service = BusinessValuationService()
