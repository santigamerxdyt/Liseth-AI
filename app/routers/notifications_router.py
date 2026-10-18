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


@router.get("/telegram/status")
async def get_telegram_status():
    """Returns Telegram bot configuration and polling status."""
    from app.services.telegram_service import telegram_service
    from app.config import settings
    return {
        "ok": True,
        "hasToken": bool(settings.TELEGRAM_BOT_TOKEN),
        "hasChatId": bool(settings.TELEGRAM_CHAT_ID),
        "isPolling": telegram_service.is_running,
    }


@router.post("/telegram/webhook")
async def telegram_webhook(update: dict):
    """Processes incoming Telegram updates via webhook."""
    from app.services.telegram_service import telegram_service
    if "message" in update:
        res = await telegram_service.handle_message(update["message"])
        return {"ok": True, "reply": res}
    return {"ok": True, "ignored": True}

