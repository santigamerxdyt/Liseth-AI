"""
Action handler for colombia_macro tool in JARVIS / Liseth.
Bridges Gemini Tool Calls with the Colombia Macroeconomic & Payroll Service.
"""
from typing import Any, Dict
from app.services.colombia_macro_service import colombia_macro_service


def colombia_macro_action(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handles queries for macroeconomic indicators, payroll liquidation, and UVT conversions.
    """
    action = parameters.get("action") or "indicators"

    if action in ("payroll", "nomina", "costo_laboral"):
        salary = float(parameters.get("base_salary") or parameters.get("salario") or 2500000.0)
        risk = int(parameters.get("risk_level") or parameters.get("riesgo_arl") or 1)
        include_trans = parameters.get("include_transport")
        exempt = parameters.get("apply_exemption_114_1")

        payroll = colombia_macro_service.liquidate_payroll(
            base_salary=salary,
            include_transport=include_trans,
            risk_level=risk,
            apply_exemption_114_1=exempt
        )
        report = colombia_macro_service.format_markdown_report(payroll)
        return {
            "status": "success",
            "action": "colombia_macro.payroll",
            "payroll": payroll,
            "markdown": report
        }

    elif action in ("uvt", "convert_uvt"):
        amt = float(parameters.get("amount") or 100.0)
        direction = parameters.get("direction") or "cop_to_uvt"
        res = colombia_macro_service.convert_uvt(amount=amt, direction=direction)
        return {
            "status": "success",
            "action": "colombia_macro.uvt",
            "conversion": res
        }

    else:  # indicators
        indicators = colombia_macro_service.get_macro_indicators()
        md = [
            "# 🇨🇴 RADAR MACROECONÓMICO COLOMBIA (2026)",
            f"- **Dólar TRM Referencial**: `${indicators['trm_cop_usd']:,.2f} COP / USD`",
            f"- **Unidad de Valor Tributario (UVT)**: `${indicators['uvt_cop']:,.2f} COP`",
            f"- **Salario Mínimo Legal Mensual (SMLMV)**: `${indicators['smlmv_cop']:,.2f} COP`",
            f"- **Auxilio de Transporte**: `${indicators['aux_transporte_cop']:,.2f} COP`",
            f"- **Tasa de Intervención BanRep**: `{indicators['banrep_rate_pct']}% E.A.`",
            f"- **Inflación Proyectada (IPC)**: `{indicators['ipc_inflation_pct']}%`",
            f"- **Tasa de Usura Legal**: `{indicators['usury_rate_pct']}% E.A.`",
            "",
            "> 💡 *Para liquidar nómina con recargos y prestaciones, solicita: 'Liquida una nómina con salario base de 3000000'*."
        ]
        return {
            "status": "success",
            "action": "colombia_macro.indicators",
            "indicators": indicators,
            "markdown": "\n".join(md)
        }
