"""
SlopMonster Action for JARVIS / Liseth.
Exposes AI writing pattern detection, scoring (0 to 5), and copy humanization
to the action dispatcher and brain router.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

from app.services.slopmonster_service import slopmonster_service

logger = logging.getLogger("jarvis.slopmonster_action")


def slopmonster_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    """
    Synchronous entrypoint for SlopMonster tools.
    Can be run directly or inside a thread pool executor.
    """
    params = parameters or {}
    action = params.get("action", "deslop").lower().strip()
    target_path = params.get("path") or params.get("file") or ""
    text = params.get("text") or params.get("copy") or params.get("draft") or ""

    try:
        # 1. Status Telemetry
        if action in ["status", "estado", "info"]:
            st = slopmonster_service.get_status()
            return slopmonster_service.format_status_report(st)

        # 2. Extract content from file if path is given
        if target_path and os.path.exists(target_path):
            try:
                with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except Exception as e:
                return f"Señor Santiago, no se pudo leer el archivo '{target_path}': {e}"

        if not text:
            return (
                "Señor Santiago, debe proporcionar el texto a evaluar o la ruta de un archivo "
                "(ejemplo: `text='En el vertiginoso mundo actual...'` o `path='ensayo.txt'`)."
            )

        # 3. Humanize / De-slop rewrite
        if action in ["humanize", "humanizar", "reescribir", "limpiar", "cleanse"]:
            res = slopmonster_service.humanize_text(text)
            return slopmonster_service.format_humanize_report(res)

        # 4. Deslop Analysis & Scoring (Default)
        res = slopmonster_service.deslop_text(text, file_name=os.path.basename(target_path) if target_path else "Texto")
        return slopmonster_service.format_deslop_report(res)

    except Exception as e:
        logger.error(f"Error in slopmonster_action: {e}", exc_info=True)
        return f"Señor Santiago, ocurrió una excepción durante el análisis con SlopMonster: {str(e)}"
