"""
System API Router for JARVIS / Liseth.
Provides status, hardware telemetry, process management, audited Windows execution,
personalization configuration synchronization, network interfaces, and persistent chat history.
"""
import logging
import socket
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from pydantic import BaseModel
from sqlalchemy import select, delete, update

from app.config import settings
from app.connectors.system_connector import system_connector
from app.core.database import AsyncSessionLocal
from app.core.models import AppSetting, ChatMessage, UserProfile
from app.services.brain_router import brain_router
from app.services.soul_service import soul_service

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
    # User personalization
    userName: Optional[str] = None
    userTitle: Optional[str] = None
    userTone: Optional[str] = None
    customGreeting: Optional[str] = None
    theme: Optional[str] = None
    sphereStyle: Optional[str] = None


class SystemExecuteRequest(BaseModel):
    action: str
    params: Dict[str, Any] = {}


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
    """Returns general configuration, personalization settings, and active brain metadata."""
    personalization = {
        "userTitle": "Señor Santiago",
        "userName": "Santiago",
        "userTone": "formal",
        "customGreeting": "A sus órdenes, Señor Santiago. Todos los sistemas en línea.",
        "theme": "arc_cyan",
        "sphereStyle": "arc_reactor",
    }

    # Fetch persisted preferences from SQLite
    async with AsyncSessionLocal() as session:
        try:
            res = await session.execute(select(UserProfile).where(UserProfile.id == 1))
            profile = res.scalar_one_or_none()
            if profile:
                prefs = profile.preferences or {}
                personalization["userTitle"] = prefs.get("userTitle", profile.nickname or "Señor Santiago")
                personalization["userName"] = profile.name or "Santiago"
                personalization["userTone"] = prefs.get("userTone", "formal")
                personalization["customGreeting"] = prefs.get("customGreeting", personalization["customGreeting"])
                personalization["theme"] = prefs.get("theme", "arc_cyan")
                personalization["sphereStyle"] = prefs.get("sphereStyle", "arc_reactor")
        except Exception as e:
            logger.warning(f"Error cargando personalización de BD: {e}")

    return {
        "ok": True,
        "apiKeyConfigured": bool(settings.GEMINI_API_KEY),
        "activeBrain": brain_router.active_brain,
        "activeModel": brain_router.active_gemini_model,
        "personalization": personalization,
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
    """Saves user voice settings, API keys, and personalization preferences."""
    async with AsyncSessionLocal() as session:
        try:
            res = await session.execute(select(UserProfile).where(UserProfile.id == 1))
            profile = res.scalar_one_or_none()
            if not profile:
                profile = UserProfile(id=1, name="Santiago", nickname="Señor Santiago", preferences={})
                session.add(profile)

            prefs = dict(profile.preferences or {})
            if req.userTitle is not None:
                prefs["userTitle"] = req.userTitle.strip()
                profile.nickname = req.userTitle.strip()
            if req.userName is not None:
                prefs["userName"] = req.userName.strip()
                profile.name = req.userName.strip()
            if req.userTone is not None:
                prefs["userTone"] = req.userTone
            if req.customGreeting is not None:
                prefs["customGreeting"] = req.customGreeting
            if req.theme is not None:
                prefs["theme"] = req.theme
            if req.sphereStyle is not None:
                prefs["sphereStyle"] = req.sphereStyle

            profile.preferences = prefs
            await session.commit()

            # If userTitle changed, reflect in USER.md memory
            if req.userTitle:
                soul_service.append_memory(f"Trato preferido actualizado a: {req.userTitle.strip()}", target="user")

            return {
                "ok": True,
                "message": "Configuración y personalización actualizadas correctamente.",
                "preferences": prefs,
            }
        except Exception as e:
            await session.rollback()
            logger.error(f"Error guardando configuración: {e}")
            raise HTTPException(status_code=500, detail="Error guardando configuración en base de datos.")


@router.get("/system/info")
async def get_system_telemetry():
    """Returns hardware telemetry and OS status from the user's PC."""
    try:
        info = await system_connector.get_system_info()
        return {"ok": True, "data": info}
    except Exception as e:
        logger.error(f"Error obteniendo información de sistema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/processes")
async def get_system_processes(limit: int = Query(50, ge=1, le=200), filter: Optional[str] = None):
    """Lists running processes with CPU/memory consumption."""
    try:
        processes = await system_connector.list_processes(limit=limit, filter_name=filter)
        return {"ok": True, "count": len(processes), "processes": processes}
    except Exception as e:
        logger.error(f"Error listando procesos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/search")
async def search_system_files(
    q: str = Query(..., min_length=1),
    path: str = Query(".", description="Ruta base para buscar"),
    limit: int = Query(50, ge=1, le=200)
):
    """Searches files by name or extension on Santiago's PC for the Dynamic Viewer."""
    try:
        results = await system_connector.search_files(query=q, root_path=path, max_results=limit)
        return {"ok": True, "data": results}
    except Exception as e:
        logger.error(f"Error buscando archivos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/read")
async def read_system_file(
    path: str = Query(..., description="Ruta del archivo a leer"),
    max_bytes: int = Query(250000, ge=100, le=1000000)
):
    """Reads file content safely from the local system for the Dynamic Viewer."""
    try:
        file_data = await system_connector.read_file(path=path, max_bytes=max_bytes)
        return {"ok": True, "data": file_data}
    except Exception as e:
        logger.error(f"Error leyendo archivo de sistema: {e}")
        raise HTTPException(status_code=400, detail=str(e))



@router.post("/system/execute")
async def execute_system_action(req: SystemExecuteRequest):
    """
    Executes or requests confirmation for Windows PC actions:
    - Commands (system_run_command)
    - Applications (system_open_app)
    - Files (system_write_file, system_delete_file, system_read_file)
    - Processes (system_kill_process)
    - Telemetry (system_get_info)

    Modifying/executing actions require explicit user confirmation.
    """
    try:
        result = await system_connector.execute_action(req.action, req.params)
        return result
    except Exception as e:
        logger.error(f"Error en ejecución de acción de sistema '{req.action}': {e}")
        raise HTTPException(status_code=400, detail=str(e))


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
