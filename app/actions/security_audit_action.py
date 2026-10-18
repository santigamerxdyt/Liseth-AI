"""
Security Audit Action for JARVIS / Liseth.
Exposes vulnerability scanning, secret detection, and cybersecurity reporting
to the action dispatcher and brain router.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

from app.services.security_audit_service import security_audit_service

logger = logging.getLogger("jarvis.security_audit_action")


def security_audit_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    """
    Synchronous entrypoint for Security Audit tools.
    Can be run directly or inside a thread pool executor.
    """
    params = parameters or {}
    action = params.get("action", "audit").lower().strip()
    target_path = params.get("path") or params.get("target_path") or params.get("file") or "."
    code = params.get("code") or ""

    try:
        # 1. Status Telemetry
        if action in ["status", "estado", "info", "motores"]:
            st = security_audit_service.get_status()
            return security_audit_service.format_status_report(st)

        # 2. Audit Code Snippet or File/Directory (Default)
        if code:
            res = security_audit_service.audit_code_snippet(code, file_name=params.get("file_name", "snippet.py"))
            return security_audit_service.format_audit_report(res)

        resolved = os.path.abspath(target_path)
        res = security_audit_service.audit_path(resolved)
        return security_audit_service.format_audit_report(res)

    except Exception as e:
        logger.error(f"Error in security_audit_action: {e}", exc_info=True)
        return f"Señor Santiago, ocurrió una excepción durante la auditoría de seguridad: {str(e)}"
