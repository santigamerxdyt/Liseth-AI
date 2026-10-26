"""
Corporate Risk Matrix & 5x5 Heatmap Service for Liseth / JARVIS.
Implements ISO 31000 / COSO ERM standards adapted for Stark Industries executive oversight:
- Inherent Risk Scoring (Probability 1-5 x Impact 1-5 = 1-25)
- Categorization (Estratégico, Financiero, Operacional, Legal, Ciberseguridad)
- Control Actions & Residual Risk Evaluation
- Interactive 5x5 Heatmap Data Generation
- JSON Persistence in data/corporate_risks.json
"""
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

DATA_FILE = os.path.join("data", "corporate_risks.json")


class RiskMatrixService:
    def __init__(self):
        self._ensure_storage()

    def _ensure_storage(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(DATA_FILE):
            default_risks = [
                {
                    "id": "RSK-001",
                    "title": "Volatilidad en Tasa de Cambio (Dólar TRM)",
                    "category": "Financiero",
                    "probability": 4,
                    "impact": 4,
                    "inherent_risk": 16,
                    "inherent_level": "CRITICO",
                    "control": "Coberturas cambiarias foráneas y diversificación multidivisa",
                    "residual_probability": 2,
                    "residual_impact": 3,
                    "residual_risk": 6,
                    "residual_level": "MODERADO",
                    "owner": "Santiago / CFO",
                    "status": "mitigated",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                },
                {
                    "id": "RSK-002",
                    "title": "Brecha de Seguridad / Ataque Ransomware",
                    "category": "Ciberseguridad",
                    "probability": 3,
                    "impact": 5,
                    "inherent_risk": 15,
                    "inherent_level": "ALTO",
                    "control": "Bóveda Stark de alta entropía, 2FA y copias de seguridad aisladas",
                    "residual_probability": 1,
                    "residual_impact": 4,
                    "residual_risk": 4,
                    "residual_level": "BAJO",
                    "owner": "Stark Security Ops",
                    "status": "mitigated",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                },
                {
                    "id": "RSK-003",
                    "title": "Modificaciones en Normativa Tributaria DIAN",
                    "category": "Legal",
                    "probability": 4,
                    "impact": 3,
                    "inherent_risk": 12,
                    "inherent_level": "ALTO",
                    "control": "Auditorías continuas y parametrización ágil en facturación pro-forma",
                    "residual_probability": 2,
                    "residual_impact": 2,
                    "residual_risk": 4,
                    "residual_level": "BAJO",
                    "owner": "Asesor Jurídico UNAL",
                    "status": "active",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                },
                {
                    "id": "RSK-004",
                    "title": "Interrupción de Cadena de Suministro / Proveedores",
                    "category": "Operacional",
                    "probability": 3,
                    "impact": 3,
                    "inherent_risk": 9,
                    "inherent_level": "MODERADO",
                    "control": "Acuerdos de nivel de servicio (SLA) con múltiples proveedores redundantes",
                    "residual_probability": 2,
                    "residual_impact": 2,
                    "residual_risk": 4,
                    "residual_level": "BAJO",
                    "owner": "Gerencia de Operaciones",
                    "status": "active",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            ]
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(default_risks, f, indent=2, ensure_ascii=False)

    def _load(self) -> List[Dict[str, Any]]:
        self._ensure_storage()
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save(self, risks: List[Dict[str, Any]]):
        os.makedirs("data", exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(risks, f, indent=2, ensure_ascii=False)

    @staticmethod
    def classify_level(score: int) -> str:
        if score >= 16:
            return "CRITICO"
        elif score >= 10:
            return "ALTO"
        elif score >= 5:
            return "MODERADO"
        else:
            return "BAJO"

    def list_risks(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        risks = self._load()
        if category:
            cat_lower = category.lower()
            return [r for r in risks if r.get("category", "").lower() == cat_lower]
        return risks

    def add_risk(
        self,
        title: str,
        category: str = "Estrategico",
        probability: int = 3,
        impact: int = 3,
        control: str = "Control preventivo",
        residual_probability: int = 2,
        residual_impact: int = 2,
        owner: str = "Santiago / CEO"
    ) -> Dict[str, Any]:
        risks = self._load()
        prob = max(1, min(5, int(probability)))
        imp = max(1, min(5, int(impact)))
        r_prob = max(1, min(5, int(residual_probability)))
        r_imp = max(1, min(5, int(residual_impact)))

        inh_score = prob * imp
        res_score = r_prob * r_imp

        new_risk = {
            "id": f"RSK-{uuid.uuid4().hex[:4].upper()}",
            "title": title.strip(),
            "category": category.strip().capitalize(),
            "probability": prob,
            "impact": imp,
            "inherent_risk": inh_score,
            "inherent_level": self.classify_level(inh_score),
            "control": control.strip(),
            "residual_probability": r_prob,
            "residual_impact": r_imp,
            "residual_risk": res_score,
            "residual_level": self.classify_level(res_score),
            "owner": owner.strip(),
            "status": "active",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        risks.append(new_risk)
        self._save(risks)
        return new_risk

    def delete_risk(self, risk_id: str) -> bool:
        risks = self._load()
        filtered = [r for r in risks if r.get("id") != risk_id]
        if len(filtered) < len(risks):
            self._save(filtered)
            return True
        return False

    def get_heatmap_5x5(self) -> Dict[str, Any]:
        """
        Builds 5x5 matrix indexed by [impact][probability]
        where 1 is lowest and 5 is highest.
        """
        risks = self._load()
        # grid: rows=impact (5 down to 1), cols=prob (1 to 5)
        cells = {}
        for imp in range(1, 6):
            for prob in range(1, 6):
                key = f"{imp}_{prob}"
                score = imp * prob
                cells[key] = {
                    "impact": imp,
                    "probability": prob,
                    "score": score,
                    "level": self.classify_level(score),
                    "risks": []
                }

        for r in risks:
            key = f"{r['impact']}_{r['probability']}"
            if key in cells:
                cells[key]["risks"].append({
                    "id": r["id"],
                    "title": r["title"],
                    "category": r["category"],
                    "residual_score": r["residual_risk"],
                    "residual_level": r["residual_level"]
                })

        # Summary count
        counts = {"CRITICO": 0, "ALTO": 0, "MODERADO": 0, "BAJO": 0}
        residual_counts = {"CRITICO": 0, "ALTO": 0, "MODERADO": 0, "BAJO": 0}
        for r in risks:
            counts[r.get("inherent_level", "BAJO")] += 1
            residual_counts[r.get("residual_level", "BAJO")] += 1

        return {
            "total_risks": len(risks),
            "inherent_counts": counts,
            "residual_counts": residual_counts,
            "cells": cells,
            "risks": risks
        }

    def format_markdown_report(self) -> str:
        data = self.get_heatmap_5x5()
        risks = data["risks"]
        md = [
            "# 🛡️ MATRIZ DE RIESGOS CORPORATIVOS & MAPA DE CALOR 5x5 (ISO 31000)",
            f"**Total de Riesgos Monitoreados**: `{data['total_risks']}`",
            "",
            "### 📊 Balance Comparativo (Inherente vs Residual)",
            f"- **🔴 Críticos**: {data['inherent_counts']['CRITICO']} inherentes ➔ **{data['residual_counts']['CRITICO']} residuales**",
            f"- **🟡 Altos**: {data['inherent_counts']['ALTO']} inherentes ➔ **{data['residual_counts']['ALTO']} residuales**",
            f"- **🔵 Moderados**: {data['inherent_counts']['MODERADO']} inherentes ➔ **{data['residual_counts']['MODERADO']} residuales**",
            f"- **🟢 Bajos**: {data['inherent_counts']['BAJO']} inherentes ➔ **{data['residual_counts']['BAJO']} residuales**",
            "",
            "### 📋 Catálogo Detallado de Riesgos y Controles",
            "| ID | Título del Riesgo | Categoría | P x I | Inherente | Control Mitigante | P_res x I_res | Residual | Responsable |",
            "| :--- | :--- | :--- | :---: | :---: | :--- | :---: | :---: | :--- |"
        ]

        for r in risks:
            md.append(
                f"| `{r['id']}` | {r['title']} | {r['category']} | {r['probability']}x{r['impact']} | **{r['inherent_level']} ({r['inherent_risk']})** | {r['control']} | {r['residual_probability']}x{r['residual_impact']} | **{r['residual_level']} ({r['residual_risk']})** | {r['owner']} |"
            )

        return "\n".join(md)


risk_matrix_service = RiskMatrixService()
