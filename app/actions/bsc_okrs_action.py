"""
Action handler for bsc_okrs tool in JARVIS / Liseth.
Bridges Gemini Tool Calls with the Balanced Scorecard & OKRs Service.
"""
from typing import Any, Dict
from app.services.bsc_okrs_service import bsc_okrs_service


def bsc_okrs_action(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Manages Balanced Scorecard 4 Perspectives and updates Key Results progress.
    """
    action = parameters.get("action") or "dashboard"

    if action in ("update", "actualizar", "set_progress"):
        kr_id = parameters.get("kr_id") or "KR-01"
        new_val = float(parameters.get("value") or parameters.get("nuevo_valor") or 0.0)

        ok = bsc_okrs_service.update_kr_progress(kr_id, new_val)
        dash = bsc_okrs_service.get_dashboard()
        report = bsc_okrs_service.format_markdown_report()

        return {
            "status": "success" if ok else "not_found",
            "action": "bsc_okrs.update",
            "updated": ok,
            "kr_id": kr_id,
            "dashboard": dash,
            "markdown": report
        }

    else:  # dashboard, summary
        dash = bsc_okrs_service.get_dashboard()
        report = bsc_okrs_service.format_markdown_report()

        return {
            "status": "success",
            "action": "bsc_okrs.dashboard",
            "dashboard": dash,
            "markdown": report
        }
