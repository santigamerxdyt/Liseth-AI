# -*- coding: utf-8 -*-
"""
Talent Management & Organizational Climate Service for Liseth.
Provides 9-Box Grid Talent Matrix, eNPS Employee Net Promoter Score,
and Colombian Turnover Cost Diagnostic (Código Sustantivo del Trabajo).
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("liseth.talent_management")

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
HISTORY_FILE = DATA_DIR / "talent_management_history.json"


class TalentManagementService:
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
            logger.error(f"[TALENT_ERR] Error loading history: {e}")
        return []

    def _save_history(self, history: List[Dict[str, Any]]) -> None:
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[TALENT_ERR] Error saving history: {e}")

    def evaluate_9box(
        self,
        employee_name: str,
        performance_score: float,  # 1.0 to 3.0 (1=Bajo, 2=Medio, 3=Alto)
        potential_score: float,    # 1.0 to 3.0 (1=Bajo, 2=Medio, 3=Alto)
        role: str = "Colaborador",
        department: str = "Operaciones"
    ) -> Dict[str, Any]:
        """
        Maps employee to the official 9-Box Grid quadrant:
        Performance (X axis, 1..3) vs Potential (Y axis, 1..3).
        """
        # Clamp inputs
        p_score = max(1.0, min(3.0, float(performance_score)))
        pot_score = max(1.0, min(3.0, float(potential_score)))

        # Categorize
        p_level = "Alto" if p_score >= 2.5 else ("Medio" if p_score >= 1.7 else "Bajo")
        pot_level = "Alto" if pot_score >= 2.5 else ("Medio" if pot_score >= 1.7 else "Bajo")

        grid_matrix = {
            ("Alto", "Alto"): {
                "quadrant": "1A. Estrella de Alto Valor (Star / Future CEO)",
                "action": "Plan de sucesión inmediato, retención con equity o bono por hitos, proyectos de máxima visibilidad y mentoría ejecutiva.",
                "risk_level": "Riesgo alto de caza de talentos externa (headhunting)."
            },
            ("Medio", "Alto"): {
                "quadrant": "1B. Futuro Líder / Alto Potencial (High Potential)",
                "action": "Asignar retos de mayor complejidad, coaching en habilidades técnicas y liderazgo para elevar su desempeño a Alto.",
                "risk_level": "Puede frustrarse si no recibe aceleración de carrera."
            },
            ("Bajo", "Alto"): {
                "quadrant": "1C. Enigma / Diamante en Bruto (Rough Diamond)",
                "action": "Diagnosticar desajuste de rol o problemas de onboarding. Evaluar rotación de área antes de tomar decisiones drásticas.",
                "risk_level": "Desempeño actual inconsistente pese a brillantez intelectual."
            },
            ("Alto", "Medio"): {
                "quadrant": "2A. Profesional Clave / Alto Desempeño (High Performer)",
                "action": "Reconocimiento continuo, ampliación de responsabilidades y formación en liderazgo estratégico para detonar su potencial.",
                "risk_level": "Pilar operativo indispensable."
            },
            ("Medio", "Medio"): {
                "quadrant": "2B. Profesional Núcleo / Colaborador Pilar (Core Player)",
                "action": "Mantener motivado con metas claras y feedback trimestral. Es la columna vertebral de la estabilidad de la empresa.",
                "risk_level": "Riesgo bajo; requiere reconocimiento para evitar complacencia."
            },
            ("Bajo", "Medio"): {
                "quadrant": "2C. Dilema / Requiere Acompañamiento (Inconsistent)",
                "action": "Plan de mejora de rendimiento (PIP) a 60 días con métricas cuantitativas no negociables.",
                "risk_level": "Sobrecarga al resto del equipo si no mejora."
            },
            ("Alto", "Bajo"): {
                "quadrant": "3A. Especialista Confiable / Caballo de Batalla (Workhorse)",
                "action": "Mantener en su puesto como experto temático. No forzar a roles gerenciales si su vocación es estrictamente técnica.",
                "risk_level": "Satisfecho en su especialidad, resistencia a cambios drásticos."
            },
            ("Medio", "Bajo"): {
                "quadrant": "3B. Rendimiento Efectivo / Especialista en Desarrollo (Effective)",
                "action": "Monitorear cumplimiento de KPIs y verificar si requiere reentrenamiento en nuevas herramientas.",
                "risk_level": "Bajo riesgo, pero sin proyección de ascenso."
            },
            ("Bajo", "Bajo"): {
                "quadrant": "3C. Riesgo de Talento / Desalineado (Underperformer)",
                "action": "Decisión de desvinculación consensuada o transición acordada para no comprometer la moral del equipo.",
                "risk_level": "Drena recursos y desmotiva a compañeros de alto rendimiento."
            }
        }

        classification = grid_matrix.get((p_level, pot_level), grid_matrix[("Medio", "Medio")])

        result = {
            "employee_name": employee_name,
            "role": role,
            "department": department,
            "performance_score": round(p_score, 2),
            "performance_level": p_level,
            "potential_score": round(pot_score, 2),
            "potential_level": pot_level,
            "quadrant": classification["quadrant"],
            "recommended_action": classification["action"],
            "risk_assessment": classification["risk_level"],
            "timestamp": datetime.now().isoformat()
        }

        history = self._load_history()
        history.insert(0, {"type": "9box_evaluation", "data": result})
        self._save_history(history[:50])
        return result

    def calculate_enps(
        self,
        promoters: int,
        passives: int,
        detractors: int
    ) -> Dict[str, Any]:
        """
        Employee Net Promoter Score (eNPS) = % Promoters (9-10) - % Detractors (0-6).
        """
        total = promoters + passives + detractors
        if total <= 0:
            total = 1

        promoters_pct = (promoters / total) * 100.0
        passives_pct = (passives / total) * 100.0
        detractors_pct = (detractors / total) * 100.0
        enps_score = round(promoters_pct - detractors_pct, 1)

        if enps_score >= 50.0:
            climate = "EXCEPCIONAL: Cultura de alta fidelidad, pertenencia y entusiasmo directivo."
            status = "optimal"
        elif enps_score >= 20.0:
            climate = "SALUDABLE: Buen ambiente organizacional con áreas puntuales de escucha activa."
            status = "healthy"
        elif enps_score >= 0.0:
            climate = "NEUTRO / EN RIESGO: Clima pasivo; los colaboradores no recomiendan activamente la empresa."
            status = "warning"
        else:
            climate = "CRÍTICO: Toxicidad o descontento generalizado; alto riesgo de fuga masiva de talento."
            status = "critical"

        result = {
            "total_respondents": total,
            "promoters_count": promoters,
            "promoters_pct": round(promoters_pct, 1),
            "passives_count": passives,
            "passives_pct": round(passives_pct, 1),
            "detractors_count": detractors,
            "detractors_pct": round(detractors_pct, 1),
            "enps_score": enps_score,
            "diagnostic": climate,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }

        history = self._load_history()
        history.insert(0, {"type": "enps_survey", "data": result})
        self._save_history(history[:50])
        return result

    def calculate_turnover_cost(
        self,
        departures: int,
        avg_headcount: int,
        avg_salary_cop: float,
        period_months: int = 12
    ) -> Dict[str, Any]:
        """
        Calculates organizational turnover rate and financial impact (recruiting + training curve).
        In Colombia, replacing an employee costs typically 3 to 6 months of salary.
        """
        if avg_headcount <= 0:
            avg_headcount = 1
        if period_months <= 0:
            period_months = 12

        turnover_rate_pct = (departures / avg_headcount) * 100.0
        annualized_turnover_pct = (turnover_rate_pct / period_months) * 12.0

        # Cost per departure: Recruiting (1 mo) + Ramp-up productivity loss (2 mo) + Legal severance (1 mo) = ~4 salaries
        replacement_multiplier = 4.0
        cost_per_departure = avg_salary_cop * replacement_multiplier
        total_turnover_cost = departures * cost_per_departure

        result = {
            "departures": departures,
            "avg_headcount": avg_headcount,
            "turnover_rate_pct": round(turnover_rate_pct, 2),
            "annualized_turnover_pct": round(annualized_turnover_pct, 2),
            "avg_salary_cop": round(avg_salary_cop, 2),
            "cost_per_departure_cop": round(cost_per_departure, 2),
            "total_turnover_cost_cop": round(total_turnover_cost, 2),
            "turnover_level": "Alto" if annualized_turnover_pct > 18.0 else ("Moderado" if annualized_turnover_pct > 8.0 else "Óptimo"),
            "timestamp": datetime.now().isoformat()
        }

        history = self._load_history()
        history.insert(0, {"type": "turnover_cost", "data": result})
        self._save_history(history[:50])
        return result


talent_management_service = TalentManagementService()
