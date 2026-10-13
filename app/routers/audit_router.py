"""
Audit & Confirmation API Router for JARVIS / Liseth.
Manages confirmation prompts for sensitive Google Workspace and system actions,
allowing the user to approve or reject actions safely.
"""
import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.audit_manager import audit_manager

logger = logging.getLogger("jarvis.audit_router")

router = APIRouter(prefix="/api/audit", tags=["audit"])


class ConfirmationDecisionRequest(BaseModel):
    confirmId: str
    approved: bool


class CreateConfirmationRequest(BaseModel):
    connector: str
    action: str
    params: Dict[str, Any]
    reason: Optional[str] = None


@router.get("/logs")
async def get_audit_logs(limit: int = 100):
    """Returns recent audit log records."""
    logs = await audit_manager.get_logs(limit=limit)
    return {
        "ok": True,
        "logs": logs,
    }


@router.get("/pending")
async def get_pending_confirmations():
    """Returns list of actions awaiting user confirmation."""
    pending = audit_manager.get_pending()
    return {
        "ok": True,
        "pending": pending,
    }


@router.post("/confirm")
async def confirm_action(req: ConfirmationDecisionRequest):
    """
    User endpoint to approve or reject a pending sensitive action.
    Triggers execution if approved.
    """
    try:
        result = await audit_manager.resolve_confirmation(
            confirm_id=req.confirmId,
            approved=req.approved,
        )
        return {
            "ok": True,
            "decision": "approved" if req.approved else "rejected",
            "result": result,
        }
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error procesando confirmación de auditoría: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error resolviendo acción: {str(e)}")


@router.post("/request")
async def request_confirmation(req: CreateConfirmationRequest):
    """
    Programmatically creates a pending confirmation for a sensitive action.
    """
    item = await audit_manager.create_pending_confirmation(
        connector=req.connector,
        action=req.action,
        params=req.params,
        reason=req.reason,
    )
    return {
        "ok": True,
        "confirmation": item,
    }
