# -*- coding: utf-8 -*-
"""
Action handler for SAGRILAFT & PTEE Compliance Audit (SuperSociedades Colombia).
Evaluates legal obligation thresholds, LA/FT/FPADM risk matrix, KYC due diligence,
and anti-corruption protocols for Señor Santiago.
"""

from typing import Any, Dict
from app.services.sagrilaft_compliance_service import sagrilaft_compliance_service


def sagrilaft_compliance_action(parameters: Dict[str, Any]) -> str:
    company = str(parameters.get("company_name", "Empresa / Sociedad Comercial")).strip()
    rev_smmlv = float(parameters.get("annual_revenue_smmlv", 32000.0))
    assets_smmlv = float(parameters.get("total_assets_smmlv", 28000.0))
    sector = str(parameters.get("sector", "servicios")).strip()
    officer = bool(parameters.get("has_compliance_officer", True))
    dd_level = str(parameters.get("due_diligence_level", "ordinaria")).strip()
    pep = bool(parameters.get("pep_involvement", False))
    cash_pct = float(parameters.get("cash_intensive_pct", 5.0))
    whistleblower = bool(parameters.get("has_whistleblower_channel", True))
    intl_ops = bool(parameters.get("international_operations", False))

    res = sagrilaft_compliance_service.audit_compliance(
        company_name=company,
        annual_revenue_smmlv=rev_smmlv,
        total_assets_smmlv=assets_smmlv,
        sector=sector,
        has_compliance_officer=officer,
        due_diligence_level=dd_level,
        pep_involvement=pep,
        cash_intensive_pct=cash_pct,
        has_whistleblower_channel=whistleblower,
        international_operations=intl_ops
    )

    f = res["financials"] if "financials" in res else res["financial_thresholds"]
    reg = res["regulatory_status"]
    r = res["risk_assessment"]

    status_emoji = "🟢" if r["semaphore"] == "VERDE" else ("🟡" if r["semaphore"] == "AMARILLO" else "🔴")

    lines = [
        f"🛡️ **AUDITORÍA DE CUMPLIMIENTO SAGRILAFT & PTEE — {res['company_name'].upper()}**\n",
        f"• **Sector Empresarial:** {res['sector'].upper()} | **SMMLV Ref:** ${f['smmlv_reference']:,.0f} COP",
        f"• **Ingresos Anuales:** {f['annual_revenue_smmlv']:,.0f} SMMLV (~${f['annual_revenue_cop']:,.0f} COP)",
        f"• **Activos Totales:** {f['total_assets_smmlv']:,.0f} SMMLV (~${f['total_assets_cop']:,.0f} COP)\n",
        f"⚖️ **ESTADO REGULATORIO (SUPERSOCIEDADES COLOMBIA):**",
        f"• **Obligada SAGRILAFT (Capítulo X):** {'SÍ (OBLIGADA POR LEY)' if reg['is_sagrilaft_obligated'] else 'NO (Régimen de Medidas Mínimas)'}",
        f"• **Obligada PTEE (Capítulo XIII - Anticorrupción):** {'SÍ (OBLIGADA POR LEY)' if reg['is_ptee_obligated'] else 'NO (Buenas Prácticas)'}"
    ]

    for reason in reg["reasons"]:
        lines.append(f"  - {reason}")

    lines.extend([
        f"\n{status_emoji} **MATRIZ DE RIESGO Y SCORE DE MADUREZ:**",
        f"• **Semáforo Institucional:** **{r['semaphore']}** ({r['compliance_status']})",
        f"• **Score de Madurez de Cumplimiento:** **{r['maturity_score']} / 100**",
        f"• **Riesgo Inherente (Bruto):** {r['inherent_risk_score']} / 100",
        f"• **Eficacia de Controles:** {r['control_effectiveness_score']} / 100",
        f"• **Riesgo Residual:** **{r['residual_risk_score']} / 100**\n",
        f"🔍 **CONTROLES OPERACIONALES AUDITADOS:**",
        f"• **Oficial de Cumplimiento Designado:** {'Sí' if officer else 'NO (Hallazgo crítico)'}",
        f"• **Nivel de Debida Diligencia (KYC/KYE/KYP):** {dd_level.upper()}",
        f"• **Presencia de PEPs (Personas Expuestas Políticamente):** {'SÍ (Requiere aprobación de alta gerencia)' if pep else 'No'}",
        f"• **Manejo Intensivo de Efectivo:** {cash_pct}% de las operaciones",
        f"• **Canal Ético y Línea de Denuncias PTEE:** {'Activo' if whistleblower else 'NO DISPONIBLE'}",
        f"• **Operaciones Internacionales:** {'Sí' if intl_ops else 'No'}"
    ])

    if res["red_flags"]:
        lines.append("\n🚩 **SEÑALES DE ALERTA & VULNERABILIDADES:**")
        for flag in res["red_flags"]:
            lines.append(f"  • {flag}")
    else:
        lines.append("\n✅ **No se detectaron señales de alerta graves bajo el perfil actual.**")

    lines.append("\n📋 **PLAN DE ACCIÓN DE CUMPLIMIENTO INMEDIATO:**")
    for act in res["action_plan"]:
        lines.append(f"  {act}")

    lines.append("\n*Auditoría elaborada de conformidad con la Circular Básica Jurídica de la Superintendencia de Sociedades y lineamientos UIAF.*")
    return "\n".join(lines)
