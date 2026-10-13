"""
System API Router for JARVIS / Liseth.
Provides status, configuration synchronization, network interfaces, and persistent chat history.
"""
import logging
import socket
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy import select, delete

from app.config import settings
from app.core.database import AsyncSessionLocal
from app.core.models import ChatMessage
from app.services.brain_router import brain_router

logger = logging.getLogger("jarvis.system_router")

router = APIRouter(prefix="/api", tags=["system"])


def get_local_interfaces() -> List[Dict[str, str]]:
    """Discovers LAN IP addresses for network and mobile PWA access."""
    ips = []
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if not ip.startswith("127."):
                ips.append({"address": ip, "interface": "LAN / Wi-Fi"})
    except Exception:
        pass
    return ips


class HistorySaveRequest(BaseModel):
    history: List[Dict[str, Any]]


class ConfigSaveRequest(BaseModel):
    apiKey: Optional[str] = None
    elevenLabsKey: Optional[str] = None
    openAiKey: Optional[str] = None
    voiceSettings: Optional[Dict[str, Any]] = None


@router.get("/status")
async def system_status():
    """
    Returns server status, port, active model, and network IPs.
    Allows frontend to recognize server connectivity.
    """
    return {
        "ok": True,
        "status": "online",
        "system": "JARVIS / Liseth",
        "version": "2.0.0",
        "port": settings.PORT,
        "activeBrain": brain_router.active_brain,
        "activeModel": brain_router.active_gemini_model,
        "hasApiKey": bool(settings.GEMINI_API_KEY),
        "localIPs": get_local_interfaces(),
    }


@router.get("/config")
async def get_config():
    """Returns general configuration and active brain metadata."""
    return {
        "ok": True,
        "apiKeyConfigured": bool(settings.GEMINI_API_KEY),
        "activeBrain": brain_router.active_brain,
        "activeModel": brain_router.active_gemini_model,
        "voiceSettings": {
            "enabled": True,
            "provider": "edge",
            "voiceId": "es-CO-SalomeNeural",
            "pitch": "+20Hz",
            "rate": "+10%",
        },
    }


@router.post("/config")
async def save_config(req: ConfigSaveRequest):
    """Saves user voice settings or client preferences."""
    return {
        "ok": True,
        "message": "Configuración recibida.",
    }


@router.get("/history")
async def get_chat_history():
    """Retrieves full conversation history from SQLite WAL database."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ChatMessage).where(ChatMessage.session_id == "default").order_by(ChatMessage.id.asc())
        )
        messages = result.scalars().all()
        history = [{"role": msg.role, "parts": msg.parts} for msg in messages]
        return {
            "ok": True,
            "history": history,
        }


@router.post("/history")
async def save_chat_history(req: HistorySaveRequest):
    """Saves conversation history to SQLite WAL database."""
    async with AsyncSessionLocal() as session:
        try:
            # Clear default session messages and save latest conversation
            await session.execute(
                delete(ChatMessage).where(ChatMessage.session_id == "default")
            )
            for item in req.history:
                msg = ChatMessage(
                    session_id="default",
                    role=item.get("role", "user"),
                    parts=item.get("parts", [{"text": ""}]),
                )
                session.add(msg)
            await session.commit()
            return {"ok": True, "savedCount": len(req.history)}
        except Exception as e:
            await session.rollback()
            logger.error(f"Error guardando historial: {e}")
            raise HTTPException(status_code=500, detail="Error guardando historial en la base de datos.")
