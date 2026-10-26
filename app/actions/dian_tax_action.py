"""
Action handler for dian_tax tool in JARVIS / Liseth.
Bridges Gemini Tool Calls with the DIAN Tax Compliance & Fiscal Service.
"""
from typing import Any, Dict
from app.services.dian_tax_service import dian_tax_service


def dian_tax_action(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Audits DIAN tax filing obligations, RST vs Ordinario regimes, and calendar deadlines.
    """
    action = parameters.get("action") or "rst_vs_ordinario"

    if action in ("renta_check", "obligado_renta", "topes_renta"):
        patrimonio = float(parameters.get("patrimonio_bruto") or parameters.get("patrimonio") or 0.0)
        ingresos = float(parameters.get("ingresos_brutos") or parameters.get("ingresos") or 0.0)
        tarjeta = float(parameters.get("consumos_tarjeta") or 0.0)
        compras = float(parameters.get("compras_totales") or 0.0)
        consignaciones = float(parameters.get("consignaciones") or 0.0)

        res = dian_tax_service.check_renta_obligation(
            patrimonio_bruto=patrimonio,
            ingresos_brutos=ingresos,
            consumos_tarjeta=tarjeta,
            compras_totales=compras,
            consignaciones_bancarias=consignaciones
        )

        md = [
            "# 🏛️ AUDITORÍA DE OBLIGACIÓN: DECLARACIÓN DE RENTA (PERSONAS NATURALES)",
            f"- **Estado**: **`{res['status']}`**",
            f"- **Criterios Activados**: `{res['triggered_criteria_count']}`",
            ""
        ]
        if res["is_obligated"]:
            md.append("### ⚠️ Causales de Obligación Cumplidas:")
            for r in res["reasons"]:
                md.append(f"- {r}")
        else:
            md.append("> 🟢 **No está obligado a declarar renta**: Ninguno de sus topes financieros supera los límites legales en UVT.")

        return {
            "status": "success",
            "action": "dian_tax.renta_check",
            "result": res,
            "markdown": "\n".join(md)
        }

    elif action in ("calendar", "fechas", "vencimientos"):
        nit = parameters.get("nit") or parameters.get("cedula") or "12345678"
        cal = dian_tax_service.get_tax_deadlines(nit)
        md = [
            f"# 📅 CALENDARIO FISCAL DIAN 2026: NIT / CÉDULA `{cal['nit_or_cedula']}`",
            f"**Dígitos de Control Fiscal**: `{cal['last_two_digits']}`",
            "",
            "| Impuesto | Ventana de Vencimiento Estimada | Requisito / Detalle |",
            "| :--- | :--- | :--- |"
        ]
        for d in cal["deadlines_2026"]:
            md.append(f"| **{d['tax']}** | `{d['estimated_window']}` | {d['requirement']} |")

        return {
            "status": "success",
            "action": "dian_tax.calendar",
            "calendar": cal,
            "markdown": "\n".join(md)
        }

    else:  # rst_vs_ordinario
        ingresos = float(parameters.get("ingresos") or parameters.get("gross_income") or 120000000.0)
        costos = float(parameters.get("costos") or parameters.get("expenses") or 45000000.0)
        actividad = parameters.get("actividad") or parameters.get("activity") or "servicios_profesionales"

        sim = dian_tax_service.simulate_rst_vs_ordinario(
            gross_annual_income=ingresos,
            deductible_expenses=costos,
            activity_type=actividad
        )
        report = dian_tax_service.format_markdown_report(sim)

        return {
            "status": "success",
            "action": "dian_tax.rst_vs_ordinario",
            "simulation": sim,
            "markdown": report
        }
