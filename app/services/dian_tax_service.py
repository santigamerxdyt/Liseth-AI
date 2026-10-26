"""
DIAN Tax Compliance & Fiscal Calendar Service for Liseth / JARVIS.
Tailored for Colombian Business Administration and Commercial Law (UNAL Palmira):
- Personal Income Tax Obligation Checker (Topes Estatuto Tributario en UVT 2026)
- Régimen Simple de Tributación (RST) vs Régimen Ordinario Tax Burden Simulator
- Corporate & Individual Tax Due Dates by NIT / Cédula Digits
- DIAN Electronic Invoicing & RADAN Event Requirements
"""
from typing import Any, Dict, List, Optional
from app.services.colombia_macro_service import colombia_macro_service

# UVT 2026 Reference
UVT_2026 = 49799.0

# Topes para estar obligado a declarar Renta Persona Natural (Año gravable 2025/2026)
TOPES_RENTA_PN = {
    "patrimonio_bruto_uvt": 4500,  # 4.500 UVT
    "ingresos_brutos_uvt": 1400,    # 1.400 UVT
    "tarjeta_credito_uvt": 1400,    # 1.400 UVT
    "compras_consumos_uvt": 1400,   # 1.400 UVT
    "consignaciones_uvt": 1400      # 1.400 UVT
}

# Tarifas promedio RST (Régimen Simple de Tributación) según Grupo
RST_TARIFAS = {
    "servicios_profesionales": {
        "name": "Servicios Profesionales, Consultoría y Científicos",
        "rate_pct": 5.9,
        "max_income_uvt": 100000
    },
    "comercio_al_por_mayor_menor": {
        "name": "Comercio al por mayor y detal, y Servicios Técnicos",
        "rate_pct": 3.9,
        "max_income_uvt": 100000
    },
    "actividades_industriales": {
        "name": "Actividades Industriales y Agroindustriales",
        "rate_pct": 4.5,
        "max_income_uvt": 100000
    },
    "tiendas_minimercados": {
        "name": "Tiendas pequeñas, mini-mercados y peluquerías",
        "rate_pct": 2.0,
        "max_income_uvt": 100000
    }
}


class DianTaxService:
    def __init__(self):
        self.uvt = UVT_2026

    def check_renta_obligation(
        self,
        patrimonio_bruto: float,
        ingresos_brutos: float,
        consumos_tarjeta: float = 0.0,
        compras_totales: float = 0.0,
        consignaciones_bancarias: float = 0.0
    ) -> Dict[str, Any]:
        """
        Determines whether an individual is obligated to file income tax return in Colombia.
        """
        uvt = self.uvt
        lim_patrimonio = TOPES_RENTA_PN["patrimonio_bruto_uvt"] * uvt
        lim_ingresos = TOPES_RENTA_PN["ingresos_brutos_uvt"] * uvt
        lim_tarjeta = TOPES_RENTA_PN["tarjeta_credito_uvt"] * uvt
        lim_compras = TOPES_RENTA_PN["compras_consumos_uvt"] * uvt
        lim_consigna = TOPES_RENTA_PN["consignaciones_uvt"] * uvt

        reasons = []
        if patrimonio_bruto >= lim_patrimonio:
            reasons.append(f"Patrimonio bruto (${patrimonio_bruto:,.2f}) supera el tope de 4.500 UVT (${lim_patrimonio:,.2f})")
        if ingresos_brutos >= lim_ingresos:
            reasons.append(f"Ingresos brutos (${ingresos_brutos:,.2f}) superan el tope de 1.400 UVT (${lim_ingresos:,.2f})")
        if consumos_tarjeta >= lim_tarjeta:
            reasons.append(f"Consumos con tarjeta de crédito (${consumos_tarjeta:,.2f}) superan el tope de 1.400 UVT (${lim_tarjeta:,.2f})")
        if compras_totales >= lim_compras:
            reasons.append(f"Compras y consumos totales (${compras_totales:,.2f}) superan el tope de 1.400 UVT (${lim_compras:,.2f})")
        if consignaciones_bancarias >= lim_consigna:
            reasons.append(f"Consignaciones y depósitos (${consignaciones_bancarias:,.2f}) superan el tope de 1.400 UVT (${lim_consigna:,.2f})")

        is_obligated = len(reasons) > 0

        return {
            "uvt_applied": uvt,
            "is_obligated": is_obligated,
            "status": "OBLIGADO_A_DECLARAR" if is_obligated else "NO_OBLIGADO",
            "triggered_criteria_count": len(reasons),
            "reasons": reasons,
            "thresholds_cop": {
                "patrimonio_bruto_limit": lim_patrimonio,
                "ingresos_brutos_limit": lim_ingresos,
                "tarjeta_credito_limit": lim_tarjeta,
                "compras_totales_limit": lim_compras,
                "consignaciones_limit": lim_consigna
            }
        }

    def simulate_rst_vs_ordinario(
        self,
        gross_annual_income: float,
        deductible_expenses: float,
        activity_type: str = "servicios_profesionales"
    ) -> Dict[str, Any]:
        """
        Simulates and compares total tax liability:
        - Régimen Simple de Tributación (RST)
        - Régimen Ordinario (35% corporate tax on net taxable income)
        """
        inc = float(gross_annual_income)
        exp = float(deductible_expenses)
        net_taxable_income = max(0.0, inc - exp)

        # 1. Régimen Ordinario (35% tarifa general PJ)
        ordinario_tax = round(net_taxable_income * 0.35, 2)
        ica_ordinario = round(inc * 0.00966, 2)  # Promedio ICA 9.66 por mil
        total_ordinario = round(ordinario_tax + ica_ordinario, 2)
        effective_rate_ordinario = round((total_ordinario / inc * 100.0), 2) if inc > 0 else 0.0

        # 2. Régimen Simple (RST)
        group_info = RST_TARIFAS.get(activity_type, RST_TARIFAS["servicios_profesionales"])
        rst_rate = group_info["rate_pct"] / 100.0
        # En el RST el impuesto consolida Renta + ICA municipal
        rst_tax = round(inc * rst_rate, 2)
        effective_rate_rst = round((rst_tax / inc * 100.0), 2) if inc > 0 else 0.0

        savings = round(total_ordinario - rst_tax, 2)
        better_regime = "REGIMEN_SIMPLE" if savings > 0 else "REGIMEN_ORDINARIO"

        return {
            "gross_annual_income": inc,
            "deductible_expenses": exp,
            "net_taxable_income": net_taxable_income,
            "activity": group_info["name"],
            "ordinario": {
                "income_tax_35pct": ordinario_tax,
                "ica_municipal_est": ica_ordinario,
                "total_liability": total_ordinario,
                "effective_rate_pct": effective_rate_ordinario
            },
            "regimen_simple": {
                "consolidated_rate_pct": group_info["rate_pct"],
                "total_liability": rst_tax,
                "effective_rate_pct": effective_rate_rst
            },
            "estimated_savings_cop": abs(savings),
            "recommendation": better_regime,
            "verdict": (
                f"El {better_regime.replace('_', ' ')} resulta más eficiente económicamente, "
                f"generando un ahorro tributario proyectado de ${abs(savings):,.2f} COP anuales."
            )
        }

    def get_tax_deadlines(self, nit_or_cedula: str) -> Dict[str, Any]:
        """
        Estimates tax filing deadlines in 2026 based on last 2 digits of NIT/Cédula.
        If a verification digit (-DV) is provided, it is stripped per DIAN norms.
        """
        raw = str(nit_or_cedula).strip()
        if "-" in raw:
            base_part = raw.split("-")[0]
        else:
            base_part = raw

        digits = "".join(filter(str.isdigit, base_part))
        last_two = int(digits[-2:]) if len(digits) >= 2 else (int(digits) if digits else 0)


        # Estimation based on DIAN distribution
        # Digits 01-20: mid-August; 21-50: early September; 51-80: mid September; 81-00: October
        if last_two <= 25:
            renta_date = "12 al 26 de Agosto de 2026"
        elif last_two <= 50:
            renta_date = "27 de Agosto al 11 de Septiembre de 2026"
        elif last_two <= 75:
            renta_date = "12 al 28 de Septiembre de 2026"
        else:
            renta_date = "29 de Septiembre al 19 de Octubre de 2026"

        return {
            "nit_or_cedula": nit_or_cedula,
            "last_two_digits": f"{last_two:02d}",
            "deadlines_2026": [
                {
                    "tax": "Declaración de Renta Persona Natural",
                    "estimated_window": renta_date,
                    "requirement": "Obligatorio si superó 1.400 UVT de ingresos o 4.500 UVT de patrimonio"
                },
                {
                    "tax": "Retención en la Fuente Mensual",
                    "estimated_window": "Día hábil 7 al 14 de cada mes",
                    "requirement": "Declaración y pago mensual simultáneo"
                },
                {
                    "tax": "IVA Bimestral (Grandes y Comunes)",
                    "estimated_window": "Mayo, Julio, Septiembre, Noviembre",
                    "requirement": "Bimestres enero-febrero, marzo-abril, mayo-junio..."
                },
                {
                    "tax": "Anticipo Régimen Simple (RST)",
                    "estimated_window": "Bimestral en formulario 2593",
                    "requirement": "Pago de anticipo consolidado Renta + ICA"
                }
            ]
        }

    def format_markdown_report(self, rst_data: Dict[str, Any]) -> str:
        md = [
            "# 🏛️ AUDITORÍA TRIBUTARIA DIAN: RÉGIMEN SIMPLE (RST) VS ORDINARIO",
            f"- **Ingresos Brutos Anuales**: `${rst_data['gross_annual_income']:,.2f} COP`",
            f"- **Costos y Deducciones**: `${rst_data['deductible_expenses']:,.2f} COP`",
            f"- **Renta Líquida Gravable**: `${rst_data['net_taxable_income']:,.2f} COP`",
            f"- **Actividad Económica**: *{rst_data['activity']}*",
            "",
            "### ⚖️ Comparativa de Carga Impositiva",
            "| Régimen | Tarifa Nominal | Carga Total Estimada | Tasa Efectiva Real |",
            "| :--- | :---: | :---: | :---: |",
            f"| 🏢 Régimen Ordinario (35% + ICA) | 35% Renta + 0.966% ICA | `${rst_data['ordinario']['total_liability']:,.2f} COP` | **{rst_data['ordinario']['effective_rate_pct']}%** |",
            f"| 🚀 Régimen Simple (RST Consolidado) | {rst_data['regimen_simple']['consolidated_rate_pct']}% Consolidado | `${rst_data['regimen_simple']['total_liability']:,.2f} COP` | **{rst_data['regimen_simple']['effective_rate_pct']}%** |",
            "",
            f"> 💡 **Dictamen**: {rst_data['verdict']}",
            f"> 💰 **Ahorro Fiscal Anual Proyectado**: **`${rst_data['estimated_savings_cop']:,.2f} COP`**"
        ]
        return "\n".join(md)


dian_tax_service = DianTaxService()
