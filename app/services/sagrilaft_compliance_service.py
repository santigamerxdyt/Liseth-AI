"""
SAGRILAFT & PTEE Compliance Audit Service for JARVIS / Liseth.
Implements institutional compliance auditing under Superintendencia de Sociedades guidelines
(Circular Básica Jurídica Capítulo X - SAGRILAFT & Capítulo XIII - PTEE / Ley 2195 de 2022).
Protects corporate operations against money laundering (LA), terrorism financing (FT),
weapons proliferation financing (FPADM), and transnational bribery / corruption.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvis.sagrilaft_compliance")


class SagrilaftComplianceService:
    """
    Comprehensive SAGRILAFT & PTEE compliance audit engine for Colombian corporations,
    executives, and investors.
    """

    # SMMLV 2026 reference (Colombia: ~1.423.500 COP)
    SMMLV_VALUE_COP = 1423500.0

    # Sector risk classifications
    HIGH_RISK_SECTORS = [
        "inmobiliario", "construccion", "metales_preciosos", "joyeria",
        "factoring", "vehiculos", "comercio_internacional", "juegos_azar",
        "activos_virtuales", "cripto", "cambio_divisas"
    ]

    def audit_compliance(
        self,
        company_name: str,
        annual_revenue_smmlv: float,
        total_assets_smmlv: float,
        sector: str = "servicios",
        has_compliance_officer: bool = True,
        due_diligence_level: str = "ordinaria",
        pep_involvement: bool = False,
        cash_intensive_pct: float = 5.0,
        has_whistleblower_channel: bool = True,
        international_operations: bool = False
    ) -> Dict[str, Any]:
        """
        Conducts a comprehensive SAGRILAFT and PTEE risk audit, evaluates regulatory obligation,
        and computes residual risk scores with prescriptive remediation actions.
        """
        sector_clean = sector.lower().strip().replace(" ", "_")
        is_high_risk_sector = any(s in sector_clean for s in self.HIGH_RISK_SECTORS)

        # 1. Legal Obligation Thresholds (SuperSociedades Circular Básica Jurídica)
        # General rule: Revenue or Assets >= 30,000 SMMLV (or 40,000 SMMLV in certain chapters).
        # Special sector rule: Real estate, factoring, precious metals >= 3,000 or 5,000 SMMLV.
        is_sagrilaft_obligated = False
        is_ptee_obligated = False
        obligation_reasons = []

        if annual_revenue_smmlv >= 30000.0 or total_assets_smmlv >= 30000.0:
            is_sagrilaft_obligated = True
            obligation_reasons.append("Supera el umbral general de 30.000 SMMLV en ingresos o activos totales.")

        if is_high_risk_sector and (annual_revenue_smmlv >= 3000.0 or total_assets_smmlv >= 5000.0):
            is_sagrilaft_obligated = True
            obligation_reasons.append(f"Sector regulado de alto riesgo ({sector}) superando umbral específico sectorial.")

        if annual_revenue_smmlv >= 30000.0 or international_operations:
            is_ptee_obligated = True

        if not is_sagrilaft_obligated:
            obligation_reasons.append("Bajo el umbral legal obligatorio; el sistema aplica como Régimen de Medidas Mínimas voluntario / preventiva.")

        # 2. Risk Matrix Computation: Inherente vs Residual
        # Inherent Risk Factors (0 to 100)
        inherent_risk = 35.0

        if is_high_risk_sector:
            inherent_risk += 20.0
        if cash_intensive_pct > 15.0:
            inherent_risk += 15.0
        elif cash_intensive_pct > 5.0:
            inherent_risk += 8.0
        if pep_involvement:
            inherent_risk += 15.0
        if international_operations:
            inherent_risk += 12.0

        inherent_risk = min(98.0, inherent_risk)

        # Control Effectiveness (0 to 100)
        control_score = 20.0  # Baseline
        if has_compliance_officer:
            control_score += 30.0
        if due_diligence_level.lower() in ["intensificada", "avanzada"]:
            control_score += 25.0
        elif due_diligence_level.lower() in ["ordinaria", "estandar"]:
            control_score += 15.0
        if has_whistleblower_channel:
            control_score += 15.0

        control_score = min(95.0, control_score)

        # Residual Risk: Inherent * (1 - Control / 100)
        residual_risk = inherent_risk * (1.0 - (control_score / 115.0))
        residual_risk = round(max(5.0, residual_risk), 1)

        # 3. Compliance Maturity Score (0 to 100)
        # Higher is better
        maturity_score = round(control_score * 0.7 + (100.0 - residual_risk) * 0.3, 1)

        if maturity_score >= 80.0:
            status = "CONFORME / RIESGO CONTROLADO"
            semaphore = "VERDE"
        elif maturity_score >= 60.0:
            status = "ALERTA PREVENTIVA / BRECHAS MODERADAS"
            semaphore = "AMARILLO"
        else:
            status = "CRÍTICO / ALTO RIESGO DE SANCIÓN"
            semaphore = "ROJO"

        # 4. Red Flags & Vulnerabilities
        red_flags = []
        if pep_involvement and due_diligence_level.lower() != "intensificada":
            red_flags.append("Presencia de PEP (Persona Expuesta Políticamente) sin Debida Diligencia Intensificada aprobada por alta gerencia.")
        if cash_intensive_pct > 15.0:
            red_flags.append(f"Manejo de efectivo ({cash_intensive_pct}%) supera el umbral de alerta UIAF (típico < 10%).")
        if not has_compliance_officer and is_sagrilaft_obligated:
            red_flags.append("Empresa obligada que carece de Oficial de Cumplimiento designado y registrado en SuperSociedades.")
        if not has_whistleblower_channel and is_ptee_obligated:
            red_flags.append("Incumplimiento PTEE: Falta canal ético confidencial y protocolo de protección al denunciante.")
        if international_operations and not has_whistleblower_channel:
            red_flags.append("Riesgo de soborno transnacional sin cláusulas anticorrupción específicas en contratos internacionales.")

        # 5. Immediate Action Plan (5 steps)
        action_plan = [
            "1. Formalización del Oficial de Cumplimiento con certificado de idoneidad y designación por Junta Directiva.",
            "2. Implementación de software de screening para cruce diario automático en listas vinculantes (ONU, OFAC, Interpol, Procuraduría).",
            "3. Actualización de formularios de conocimiento de contraparte (KYC/KYP/KYE) con identificación de Beneficiario Final (RUB).",
            "4. Protocolo de reporte interno y determinación de operaciones inusuales para envío de ROS a la UIAF dentro del plazo legal.",
            "5. Divulgación y capacitación anual obligatoria del Manual SAGRILAFT y Código de Ética PTEE a todo el personal."
        ]

        return {
            "company_name": company_name,
            "sector": sector,
            "financial_thresholds": {
                "annual_revenue_smmlv": annual_revenue_smmlv,
                "total_assets_smmlv": total_assets_smmlv,
                "annual_revenue_cop": annual_revenue_smmlv * self.SMMLV_VALUE_COP,
                "total_assets_cop": total_assets_smmlv * self.SMMLV_VALUE_COP,
                "smmlv_reference": self.SMMLV_VALUE_COP
            },
            "regulatory_status": {
                "is_sagrilaft_obligated": is_sagrilaft_obligated,
                "is_ptee_obligated": is_ptee_obligated,
                "reasons": obligation_reasons
            },
            "risk_assessment": {
                "inherent_risk_score": round(inherent_risk, 1),
                "control_effectiveness_score": round(control_score, 1),
                "residual_risk_score": residual_risk,
                "maturity_score": maturity_score,
                "semaphore": semaphore,
                "compliance_status": status
            },
            "controls_audited": {
                "has_compliance_officer": has_compliance_officer,
                "due_diligence_level": due_diligence_level,
                "pep_involvement": pep_involvement,
                "cash_intensive_pct": cash_intensive_pct,
                "has_whistleblower_channel": has_whistleblower_channel,
                "international_operations": international_operations
            },
            "red_flags": red_flags,
            "action_plan": action_plan
        }


sagrilaft_compliance_service = SagrilaftComplianceService()
