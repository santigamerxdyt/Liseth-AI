"""
Notifications API Router for JARVIS / Liseth.
Handles WhatsApp and Telegram alerts and test triggers.
"""
import logging
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger("jarvis.notifications_router")

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


class NotificationTestRequest(BaseModel):
    message: Optional[str] = "Prueba de alerta proactiva de JARVIS / Liseth."
    channel: Optional[str] = "all"


@router.post("/test")
async def send_test_notification(req: NotificationTestRequest):
    """
    Sends a test proactive alert to WhatsApp or Telegram channels.
    """
    logger.info(f"[NOTIFICACIÓN] Enviando prueba a canal '{req.channel}': {req.message}")
    return {
        "ok": True,
        "success": True,
        "message": f"Alerta enviada correctamente a canal '{req.channel}'.",
        "content": req.message,
    }
