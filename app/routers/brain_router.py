"""
Brain Router API Endpoints for JARVIS / Liseth.
Routes chat requests to the dual AI brains (Gemini primary, Claude failover),
tracks token metrics, and reports brain status.
"""
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Request, Response, status

from app.services.brain_router import brain_router

logger = logging.getLogger("jarvis.brain_router")

router = APIRouter(prefix="/api/brain", tags=["brain"])


class ChatRequest(BaseModel):
    contents: Optional[List[Dict[str, Any]]] = None
    prompt: Optional[str] = None
    systemInstruction: Optional[str] = None
    apiKey: Optional[str] = None
    tools: Optional[List[Dict[str, Any]]] = None


class ForceBrainRequest(BaseModel):
    brain: Optional[str] = Field(None, description="'gemini', 'claude' o null")


@router.post("/chat")
async def chat_endpoint(req: ChatRequest):
    """
    Unified chat endpoint.
    Attempts primary brain (Gemini with automatic model fallback).
    If Gemini is unavailable, automatically fails over to Claude.
    """
    try:
        res = await brain_router.generate_response(
            prompt=req.prompt,
            contents=req.contents,
            system_prompt=req.systemInstruction,
            tools=req.tools,
            api_key_gemini=req.apiKey,
        )

        return {
            "ok": True,
            "text": res["text"],
            "brainUsed": res["brain"],
            "failoverNotice": res.get("failover", False),
            "usage": res.get("usage", {}),
            "model": res.get("model", ""),
        }
    except ValueError as ve:
        # Token limit exceeded or validation error
        logger.warning(f"Aviso en chat: {ve}")
        return {
            "ok": False,
            "error": str(ve),
            "text": f"⚠️ **Aviso del Sistema:** {str(ve)}",
        }
    except Exception as e:
        logger.error(f"Error procesando chat: {e}", exc_info=True)
        return {
            "ok": False,
            "error": str(e),
            "text": f"⚠️ **Inconveniente en la comunicación:** No se pudo obtener respuesta de los cerebros IA ({str(e)}).",
        }


@router.get("/stats")
async def get_brain_stats():
    """Returns token consumption, limits, and active brain stats."""
    return {
        "ok": True,
        "activeBrain": brain_router.active_brain,
        "forcedBrain": brain_router.forced_brain,
        "lastFailover": brain_router.last_failover,
        "stats": brain_router.stats,
    }


@router.post("/force")
async def force_brain(req: ForceBrainRequest):
    """Forces the active brain to a specific provider or returns to auto."""
    if req.brain in ["gemini", "claude", None]:
        brain_router.forced_brain = req.brain
        if req.brain:
            brain_router.active_brain = req.brain
        return {
            "ok": True,
            "forcedBrain": brain_router.forced_brain,
            "message": f"Cerebro fijado a: {brain_router.forced_brain or 'Automático (Failover)'}",
        }
    raise HTTPException(status_code=400, detail="Cerebro no válido. Usa 'gemini', 'claude' o null.")
