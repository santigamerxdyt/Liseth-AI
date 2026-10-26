"""
Action handler for biocognitive_habits tool in JARVIS / Liseth.
Bridges Gemini Tool Calls with the Biocognitive Telemetry & Habits Service.
"""
from typing import Any, Dict
from app.services.biocognitive_habits_service import biocognitive_habits_service


def biocognitive_habits_action(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates CEO biocognitive health, hydration, chronotype, and peak cognitive windows.
    """
    action = parameters.get("action") or "status"

    if action in ("log", "eval", "evaluar"):
        sleep = float(parameters.get("sleep_hours") or 7.5)
        water = int(parameters.get("water_glasses") or 8)
        focus = float(parameters.get("deep_work_hours") or 4.0)
        energy = int(parameters.get("energy_rating") or 8)
        chrono = parameters.get("chronotype") or "matutino_alondra"

        res = biocognitive_habits_service.evaluate_habits(
            sleep_hours=sleep,
            water_glasses=water,
            deep_work_hours=focus,
            energy_rating=energy,
            chronotype=chrono
        )
        report = biocognitive_habits_service.format_markdown_report(res)

        return {
            "status": "success",
            "action": "biocognitive_habits.eval",
            "biocognitive": res,
            "markdown": report
        }

    else:  # status
        res = biocognitive_habits_service.get_latest_status()
        report = biocognitive_habits_service.format_markdown_report(res)

        return {
            "status": "success",
            "action": "biocognitive_habits.status",
            "biocognitive": res,
            "markdown": report
        }
