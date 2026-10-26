"""
Action handler for business_valuation tool in JARVIS / Liseth.
Bridges Gemini Tool Calls with the Business & Startup Valuation Service.
"""
from typing import Any, Dict
from app.services.business_valuation_service import business_valuation_service


def business_valuation_action(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates corporate business valuation using DCF, multiples, or Venture Capital methods.
    """
    method = parameters.get("method") or "dcf"

    if method in ("multiples", "multiplos", "ebitda"):
        ebitda = float(parameters.get("ebitda") or 120000000.0)
        revenue = float(parameters.get("annual_revenue") or parameters.get("ventas") or 500000000.0)
        ind = parameters.get("industry") or parameters.get("sector") or "tech_saas"
        curr = parameters.get("currency") or "COP"

        res = business_valuation_service.valuation_multiples(
            ebitda=ebitda,
            annual_revenue=revenue,
            industry_key=ind,
            currency=curr
        )
        md = [
            f"# 💎 VALUACIÓN POR MÚLTIPLOS COMPARABLES DE MERCADO",
            f"- **Sector**: `{res['industry']}`",
            f"- **EBITDA Base**: `${res['ebitda']:,.2f} {curr}` | **Ingresos**: `${res['annual_revenue']:,.2f} {curr}`",
            f"- **Múltiplo EV/EBITDA Aplicado**: `{res['multiples_used']['ev_ebitda_base']}x`",
            "",
            f"> 🏛️ **VALOR ESTIMADO DE LA EMPRESA (EV)**: **`${res['recommended_fair_value']:,.2f} {curr}`**",
            f"> 📊 **Rango de Valoración**: Desde `${res['valuation_by_ebitda']['low_range']:,.2f}` hasta `${res['valuation_by_ebitda']['high_range']:,.2f} {curr}`"
        ]
        return {
            "status": "success",
            "action": "business_valuation.multiples",
            "valuation": res,
            "markdown": "\n".join(md)
        }

    elif method in ("vc", "venture_capital"):
        exit_val = float(parameters.get("target_exit_value") or 5000000000.0)
        years = int(parameters.get("years_to_exit") or 5)
        roi = float(parameters.get("required_roi_multiple") or 5.0)
        inv = float(parameters.get("investment_amount") or 250000000.0)

        res = business_valuation_service.valuation_venture_capital(
            target_exit_value=exit_val,
            years_to_exit=years,
            required_roi_multiple=roi,
            investment_amount=inv
        )
        md = [
            "# 🚀 VALUACIÓN POR MÉTODO VENTURE CAPITAL (VC)",
            f"- **Valor Objetivo de Salida (Exit)**: `${res['target_exit_value']:,.2f} COP` en {res['years_to_exit']} años",
            f"- **Múltiplo de Retorno Exigido**: `{res['required_roi_multiple']}x`",
            f"- **Inversión Requerida**: `${res['investment_requested']:,.2f} COP`",
            "",
            f"> 💎 **Valuación Post-Money**: **`${res['post_money_valuation']:,.2f} COP`**",
            f"> 💼 **Valuación Pre-Money**: **`${res['pre_money_valuation']:,.2f} COP`**",
            f"> 📈 **Participación Accionaria Inversionistas**: `{res['investor_equity_share_pct']}%` (Fundadores: `{res['founder_equity_share_pct']}%`)"
        ]
        return {
            "status": "success",
            "action": "business_valuation.vc",
            "valuation": res,
            "markdown": "\n".join(md)
        }

    else:  # dcf (default)
        raw_flows = parameters.get("cash_flows") or [60000000.0, 85000000.0, 110000000.0, 140000000.0, 175000000.0]
        if isinstance(raw_flows, str):
            flows = [float(x.strip()) for x in raw_flows.split(",") if x.strip()]
        elif isinstance(raw_flows, list):
            flows = [float(x) for x in raw_flows]
        else:
            flows = [60000000.0, 85000000.0, 110000000.0, 140000000.0, 175000000.0]

        wacc = float(parameters.get("wacc") or parameters.get("discount_rate") or 0.12)
        g = float(parameters.get("terminal_growth_g") or 0.03)
        cash = float(parameters.get("cash") or 0.0)
        debt = float(parameters.get("debt") or 0.0)
        curr = parameters.get("currency") or "COP"

        res = business_valuation_service.valuation_dcf(
            projected_flows=flows,
            wacc_discount_rate=wacc,
            terminal_growth_g=g,
            cash_balance=cash,
            total_debt=debt,
            currency=curr
        )
        report = business_valuation_service.format_markdown_report(res)

        return {
            "status": "success",
            "action": "business_valuation.dcf",
            "valuation": res,
            "markdown": report
        }
