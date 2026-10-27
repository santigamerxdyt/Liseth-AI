# -*- coding: utf-8 -*-
"""
ESG Governance & Sustainability Service for Liseth.
Provides corporate evaluations across Environmental, Social, and Governance pillars
conforming to international IFRS S1/S2 and GRI standards for Colombian & global enterprises.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("liseth.esg_governance")

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
HISTORY_FILE = DATA_DIR / "esg_governance_history.json"


class EsgGovernanceService:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not HISTORY_FILE.exists():
            self._save_history([])

    def _load_history(self) -> List[Dict[str, Any]]:
        try:
            if HISTORY_FILE.exists():
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"[ESG_ERR] Error loading history: {e}")
        return []

    def _save_history(self, history: List[Dict[str, Any]]) -> None:
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[ESG_ERR] Error saving history: {e}")

    def evaluate_esg(
        self,
        company_name: str,
        environmental_score: float,  # 0 to 100
        social_score: float,         # 0 to 100
        governance_score: float,     # 0 to 100
        sector: str = "Servicios / Tecnología",
        headcount: int = 50
    ) -> Dict[str, Any]:
        """
        Calculates composite ESG score and risk tier:
        - Environmental (35% weight): Energy efficiency, carbon emissions, circular economy.
        - Social (35% weight): Workplace safety, fair wages, diversity, community impact.
        - Governance (30% weight): Transparency, anti-corruption, board independence, compliance.
        """
        e = max(0.0, min(100.0, float(environmental_score)))
        s = max(0.0, min(100.0, float(social_score)))
        g = max(0.0, min(100.0, float(governance_score)))

        # Weighted composite score
        composite_score = (e * 0.35) + (s * 0.35) + (g * 0.30)
        composite_score = round(composite_score, 1)

        # Risk Classification (aligned with MSCI & Sustainalytics benchmarks)
        if composite_score >= 80.0:
            rating = "AAA (Líder ESG / Inversión Sostenible)"
            risk_tier = "Riesgo Despreciable / Óptimo"
            status = "optimal"
        elif composite_score >= 65.0:
            rating = "AA (Sólido / Cumplimiento Avanzado)"
            risk_tier = "Riesgo Bajo"
            status = "healthy"
        elif composite_score >= 50.0:
            rating = "BBB (Promedio / En Transición)"
            risk_tier = "Riesgo Moderado"
            status = "warning"
        elif composite_score >= 35.0:
            rating = "BB (Rezago / Vulnerabilidad Regulatoria)"
            risk_tier = "Riesgo Alto"
            status = "warning"
        else:
            rating = "CCC (Crítico / No Apto para Fondos ESG)"
            risk_tier = "Riesgo Severo"
            status = "critical"

        # Actionable recommendations per pillar
        actions = []
        if e < 70.0:
            actions.append("Ambiental (E): Implementar auditoría de huella de carbono Alcance 1 y 2, y transición a energía renovable certificada.")
        if s < 70.0:
            actions.append("Social (S): Formalizar políticas de bienestar, igualdad salarial e inclusión laboral según estándares OIT.")
        if g < 70.0:
            actions.append("Gobernanza (G): Fortalecer el código de ética, línea de denuncia anónima y comités de auditoría independientes.")

        if not actions:
            actions.append("Mantener el estándar de excelencia y aspirar a certificación de Empresa B (B Corp) en Colombia.")

        result = {
            "company_name": company_name,
            "sector": sector,
            "headcount": headcount,
            "environmental_score": round(e, 1),
            "social_score": round(s, 1),
            "governance_score": round(g, 1),
            "composite_esg_score": composite_score,
            "esg_rating": rating,
            "risk_tier": risk_tier,
            "status": status,
            "strategic_recommendations": actions,
            "timestamp": datetime.now().isoformat()
        }

        history = self._load_history()
        history.insert(0, {"type": "esg_evaluation", "data": result})
        self._save_history(history[:50])
        return result


esg_governance_service = EsgGovernanceService()
