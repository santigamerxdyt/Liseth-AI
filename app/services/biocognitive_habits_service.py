"""
Biocognitive Telemetry & Executive Habits Service for Liseth / JARVIS.
Monitors energy rhythms, cognitive stamina, and physiological balance for Señor Santiago:
- Biocognitive Executive Index (0% to 100% Score)
- Chronotype & Peak Focus Window Mapping (Morning Lark vs Night Owl)
- Hydration, Sleep Debt & Cognitive Fatigue Surveillance
- Tactical Ergonomic & Neuro-Productivity Prescriptions
- Persistent Logging in data/biocognitive_habits.json
"""
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

DATA_FILE = os.path.join("data", "biocognitive_habits.json")


class BiocognitiveHabitsService:
    def __init__(self):
        self._ensure_storage()

    def _ensure_storage(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(DATA_FILE):
            default_entry = {
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "sleep_hours": 7.5,
                "water_glasses": 7,
                "deep_work_hours": 4.5,
                "energy_rating": 8,
                "chronotype": "matutino_alondra",
                "biocognitive_index_pct": 86.5,
                "status": "OPTIMO"
            }
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump([default_entry], f, indent=2, ensure_ascii=False)

    def _load(self) -> List[Dict[str, Any]]:
        self._ensure_storage()
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save(self, data: List[Dict[str, Any]]):
        os.makedirs("data", exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def evaluate_habits(
        self,
        sleep_hours: float = 7.5,
        water_glasses: int = 8,
        deep_work_hours: float = 4.0,
        energy_rating: int = 8,
        chronotype: str = "matutino_alondra"
    ) -> Dict[str, Any]:
        """
        Computes the executive biocognitive score and active productivity windows.
        """
        s_hrs = max(0.0, min(14.0, float(sleep_hours)))
        water = max(0, int(water_glasses))
        focus = max(0.0, min(12.0, float(deep_work_hours)))
        energy = max(1, min(10, int(energy_rating)))

        # 1. Sleep score (optimal 7.5 - 8.5)
        if s_hrs >= 7.0 and s_hrs <= 9.0:
            sleep_score = 100.0
        elif s_hrs >= 6.0:
            sleep_score = 80.0
        elif s_hrs >= 5.0:
            sleep_score = 60.0
        else:
            sleep_score = 40.0

        # 2. Water score (optimal 8 glasses = 2 liters)
        water_score = min(100.0, (water / 8.0) * 100.0)

        # 3. Energy score (1-10 -> 10-100)
        energy_score = energy * 10.0

        # 4. Deep work score (optimal 3 - 5 hours)
        focus_score = min(100.0, (focus / 4.0) * 100.0)

        # Weighted index: Sleep 35%, Energy 25%, Water 20%, Focus 20%
        index_val = round((sleep_score * 0.35) + (energy_score * 0.25) + (water_score * 0.20) + (focus_score * 0.20), 1)

        if index_val >= 80.0:
            state = "OPTIMO"
            banner = "Rendimiento cognitivo superior: Máxima claridad mental y vigor para toma de decisiones ejecutivas."
        elif index_val >= 60.0:
            state = "ESTABLE"
            banner = "Rendimiento funcional: Se sugiere una pausa activa o hidratación adicional para sostener el ritmo."
        else:
            state = "FATIGA_DETECTADA"
            banner = "Alerta de sobrecarga cognitiva: El sistema recomienda activar el Modo Foco con campana alfa o descanso breve."

        # Peak hours according to chronotype
        if chronotype == "vespertino_buho":
            peak_window = "16:00 a 20:30 (Tarde / Noche)"
            tactics = "Priorizar reuniones analíticas al final de la tarde; evitar decisiones críticas antes de las 10:00 AM."
        else:
            peak_window = "08:30 a 12:30 (Mañana)"
            tactics = "Dedicar las primeras horas a finanzas, código y estrategia profunda antes de atender mensajería."

        record = {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "sleep_hours": s_hrs,
            "water_glasses": water,
            "deep_work_hours": focus,
            "energy_rating": energy,
            "chronotype": chronotype,
            "biocognitive_index_pct": index_val,
            "status": state,
            "banner": banner,
            "peak_window": peak_window,
            "tactics": tactics
        }

        # Save to persistent history
        history = self._load()
        history.insert(0, record)
        if len(history) > 30:
            history = history[:30]
        self._save(history)

        return record

    def get_latest_status(self) -> Dict[str, Any]:
        history = self._load()
        if history:
            return history[0]
        return self.evaluate_habits()

    def format_markdown_report(self, data: Dict[str, Any]) -> str:
        md = [
            "# 🧠 TELEMETRÍA BIOCOGNITIVA & SALUD EJECUTIVA (CEO)",
            f"- **Índice Biocognitivo**: **`{data['biocognitive_index_pct']}%`** | **Estado**: `{data['status']}`",
            f"- **Descanso Nocturno**: `{data['sleep_hours']} horas`",
            f"- **Hidratación**: `{data['water_glasses']} / 8 vasos`",
            f"- **Bloques de Enfoque Profundo**: `{data['deep_work_hours']} horas`",
            f"- **Nivel de Vigor Percibido**: `{data['energy_rating']} / 10`",
            "",
            f"> 💡 **Diagnóstico de Rendimiento**: {data['banner']}",
            "",
            "### ⏳ Ventana de Máxima Claridad Mental (Peak Flow)",
            f"- **Cronotipo**: `{data['chronotype'].replace('_', ' ').title()}`",
            f"- **Horas Pico Recomendadas**: **`{data['peak_window']}`**",
            f"- **Pauta Táctica**: *{data['tactics']}*"
        ]
        return "\n".join(md)


biocognitive_habits_service = BiocognitiveHabitsService()
