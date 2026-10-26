"""
Colombia Macroeconomic Radar & Payroll Cost Liquidation Service for Liseth / JARVIS.
Tailored for Colombian Business Administration (UNAL Palmira):
- Key Macro Indicators (TRM, UVT, SMLMV, Auxilio de Transporte, BanRep Rate, Inflation IPC)
- Full Employer Payroll Cost Breakdown (Aportes parafiscales, Seguridad Social, Prestaciones Sociales)
- Art. 114-1 E.T. Parafiscal Exemption (SENA, ICBF, Salud patronal for workers < 10 SMLMV)
- Statutory UVT Tax Threshold & Penalty Conversion
"""
from typing import Any, Dict, List, Optional

# Macroeconomic constants (Colombia 2026 Reference Baseline)
MACRO_DEFAULTS = {
    "trm_cop_usd": 4185.50,
    "uvt_cop": 49799.0,
    "smlmv_cop": 1423500.0,
    "aux_transporte_cop": 162000.0,
    "banrep_rate_pct": 9.25,
    "ipc_inflation_pct": 5.30,
    "usury_rate_pct": 28.50,
    "year": 2026
}

ARL_RISK_RATES = {
    1: 0.00522,  # Administrativo / Financiero
    2: 0.01044,  # Comercial / Manufactura ligera
    3: 0.02436,  # Procesos industriales / Agroindustria
    4: 0.04350,  # Transporte pesado / Aceites
    5: 0.06960   # Construcción / Minería / Alto riesgo
}


class ColombiaMacroService:
    def __init__(self):
        self.macro = dict(MACRO_DEFAULTS)

    def get_macro_indicators(self) -> Dict[str, Any]:
        """
        Returns snapshot of macroeconomic indicators for Colombian executive decision-making.
        """
        return {
            "year": self.macro["year"],
            "trm_cop_usd": self.macro["trm_cop_usd"],
            "uvt_cop": self.macro["uvt_cop"],
            "smlmv_cop": self.macro["smlmv_cop"],
            "aux_transporte_cop": self.macro["aux_transporte_cop"],
            "banrep_rate_pct": self.macro["banrep_rate_pct"],
            "ipc_inflation_pct": self.macro["ipc_inflation_pct"],
            "usury_rate_pct": self.macro["usury_rate_pct"],
            "two_smlmv_threshold": self.macro["smlmv_cop"] * 2.0,
            "ten_smlmv_threshold": self.macro["smlmv_cop"] * 10.0
        }

    def convert_uvt(self, amount: float, direction: str = "cop_to_uvt") -> Dict[str, Any]:
        """
        Converts between COP and UVT.
        """
        uvt_val = self.macro["uvt_cop"]
        amt = float(amount)
        if direction == "uvt_to_cop":
            cop_res = amt * uvt_val
            return {
                "uvt": amt,
                "cop": round(cop_res, 2),
                "uvt_value_used": uvt_val,
                "direction": direction
            }
        else:
            uvt_res = amt / uvt_val if uvt_val > 0 else 0
            return {
                "cop": amt,
                "uvt": round(uvt_res, 2),
                "uvt_value_used": uvt_val,
                "direction": direction
            }

    def liquidate_payroll(
        self,
        base_salary: float,
        include_transport: Optional[bool] = None,
        risk_level: int = 1,
        apply_exemption_114_1: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Computes the complete payroll liquidation for an employee in Colombia:
        - Employee net take-home pay
        - Employer social security & parafiscal burdens
        - Statutory benefit accruals (Cesantías, Intereses, Prima, Vacaciones)
        - Total company hiring cost & employer surcharge multiplier
        """
        smlmv = self.macro["smlmv_cop"]
        aux_trans = self.macro["aux_transporte_cop"]
        salary = float(base_salary)

        # Automatic transport allowance rule: <= 2 SMLMV
        if include_transport is None:
            has_transport = salary <= (smlmv * 2.0)
        else:
            has_transport = include_transport

        transport_amt = aux_trans if has_transport else 0.0

        # Automatic Art. 114-1 E.T. exemption rule: worker salary < 10 SMLMV
        if apply_exemption_114_1 is None:
            is_exempt = salary < (smlmv * 10.0)
        else:
            is_exempt = apply_exemption_114_1

        # ARL Rate
        arl_pct = ARL_RISK_RATES.get(risk_level, 0.00522)

        # --- DEDUCCIONES AL EMPLEADO ---
        emp_health = round(salary * 0.04, 2)
        emp_pension = round(salary * 0.04, 2)
        emp_solidarity = round(salary * 0.01, 2) if salary >= (smlmv * 4.0) else 0.0
        total_emp_deductions = round(emp_health + emp_pension + emp_solidarity, 2)

        net_employee_pay = round((salary + transport_amt) - total_emp_deductions, 2)

        # --- APORTES PATRONALES (SEGURIDAD SOCIAL) ---
        # Health: 8.5% unless exempt by Art. 114-1 E.T.
        pat_health = 0.0 if is_exempt else round(salary * 0.085, 2)
        # Pension: 12.0%
        pat_pension = round(salary * 0.12, 2)
        # ARL: based on risk class
        pat_arl = round(salary * arl_pct, 2)

        total_pat_social_sec = round(pat_health + pat_pension + pat_arl, 2)

        # --- APORTES PARAFISCALES ---
        # CCF: 4.0% (never exempt)
        pat_ccf = round(salary * 0.04, 2)
        # SENA: 2.0% (exempt if Art. 114-1)
        pat_sena = 0.0 if is_exempt else round(salary * 0.02, 2)
        # ICBF: 3.0% (exempt if Art. 114-1)
        pat_icbf = 0.0 if is_exempt else round(salary * 0.03, 2)

        total_parafiscales = round(pat_ccf + pat_sena + pat_icbf, 2)

        # --- PRESTACIONES SOCIALES (PROVISIONES LEGALES MENSUALES) ---
        # Prima: 8.33% of (salary + transport)
        base_with_trans = salary + transport_amt
        prov_prima = round(base_with_trans * (1.0 / 12.0), 2)  # ~8.333%
        # Cesantías: 8.33% of (salary + transport)
        prov_cesantias = round(base_with_trans * (1.0 / 12.0), 2)
        # Intereses Cesantías: 1% monthly of Cesantías provision
        prov_int_cesantias = round(prov_cesantias * 0.12, 2)
        # Vacaciones: 4.17% of salary (does NOT include transport)
        prov_vacaciones = round(salary * (15.0 / 360.0), 2)  # 4.166%

        total_prestaciones = round(prov_prima + prov_cesantias + prov_int_cesantias + prov_vacaciones, 2)

        # --- COSTO TOTAL EMPRESA ---
        total_company_cost = round(
            salary + transport_amt + total_pat_social_sec + total_parafiscales + total_prestaciones,
            2
        )
        multiplier = round(total_company_cost / salary, 3) if salary > 0 else 1.0

        return {
            "base_salary": salary,
            "transport_allowance": transport_amt,
            "has_transport": has_transport,
            "is_exempt_art_114_1": is_exempt,
            "risk_level": risk_level,
            "arl_rate_pct": round(arl_pct * 100, 3),
            "employee": {
                "health_deduction": emp_health,
                "pension_deduction": emp_pension,
                "solidarity_fund": emp_solidarity,
                "total_deductions": total_emp_deductions,
                "net_pay": net_employee_pay
            },
            "employer_social_security": {
                "health": pat_health,
                "pension": pat_pension,
                "arl": pat_arl,
                "subtotal": total_pat_social_sec
            },
            "parafiscales": {
                "caja_compensacion": pat_ccf,
                "sena": pat_sena,
                "icbf": pat_icbf,
                "subtotal": total_parafiscales
            },
            "statutory_benefits_provisions": {
                "prima_de_servicios": prov_prima,
                "cesantias": prov_cesantias,
                "intereses_cesantias": prov_int_cesantias,
                "vacaciones": prov_vacaciones,
                "subtotal": total_prestaciones
            },
            "total_company_cost": total_company_cost,
            "cost_multiplier": multiplier
        }

    def format_markdown_report(self, payroll_data: Dict[str, Any]) -> str:
        s = payroll_data["base_salary"]
        trans = payroll_data["transport_allowance"]
        net = payroll_data["employee"]["net_pay"]
        emp_ded = payroll_data["employee"]["total_deductions"]
        soc = payroll_data["employer_social_security"]["subtotal"]
        par = payroll_data["parafiscales"]["subtotal"]
        pres = payroll_data["statutory_benefits_provisions"]["subtotal"]
        tot = payroll_data["total_company_cost"]
        mult = payroll_data["cost_multiplier"]
        exempt_tag = "SÍ (Exonerado SENA, ICBF y Salud patronal)" if payroll_data["is_exempt_art_114_1"] else "NO (Plena tarifa)"

        md = [
            "# 🇨🇴 LIQUIDACIÓN LABORAL Y COSTO EMPRESA (COLOMBIA)",
            f"- **Salario Base Mensual**: `${s:,.2f} COP`",
            f"- **Auxilio de Transporte**: `${trans:,.2f} COP`",
            f"- **Exoneración Art. 114-1 E.T.**: `{exempt_tag}`",
            f"- **Clase de Riesgo ARL**: `Nivel {payroll_data['risk_level']} ({payroll_data['arl_rate_pct']}%)`",
            "",
            "### 👤 Trabajador: Neto a Recibir",
            f"- **Total Devengado**: `${s + trans:,.2f} COP`",
            f"- **Deducciones (Salud 4% + Pensión 4% + FSP)**: `-${emp_ded:,.2f} COP`",
            f"- **💵 Salario Neto a Pagar**: **`${net:,.2f} COP`**",
            "",
            "### 🏢 Empleador: Desglose de Cargas Mensuales",
            f"- **Seguridad Social Patronal**: `${soc:,.2f} COP` (Pensión 12%, ARL, Salud)",
            f"- **Aportes Parafiscales**: `${par:,.2f} COP` (Caja Compensación 4%, SENA, ICBF)",
            f"- **Provisiones Prestaciones Sociales**: `${pres:,.2f} COP` (Prima 8.33%, Cesantías 8.33%, Intereses 1%, Vacaciones 4.17%)",
            "",
            f"> 💡 **COSTO TOTAL MENSUAL PARA LA EMPRESA**: **`${tot:,.2f} COP`**  ",
            f"> 📈 **Factor Multiplicador Real**: **`{mult}x`** *(Por cada peso de salario base, la empresa eroga {mult} pesos)*"
        ]
        return "\n".join(md)


colombia_macro_service = ColombiaMacroService()
