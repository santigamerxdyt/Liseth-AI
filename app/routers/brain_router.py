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
        from app.services.soul_service import soul_service
        enriched_system_instruction = soul_service.build_system_instruction(req.systemInstruction)

        res = await brain_router.generate_response(
            prompt=req.prompt,
            contents=req.contents,
            system_prompt=enriched_system_instruction,
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


@router.get("/status")
@router.get("/stats")
async def get_brain_stats():
    """Returns token consumption, limits, and active brain stats."""
    return {
        "ok": True,
        "activeBrain": brain_router.active_brain,
        "activeGeminiModel": brain_router.active_gemini_model,
        "forcedBrain": brain_router.forced_brain,
        "lastFailover": brain_router.last_failover,
        "stats": brain_router.stats,
    }


@router.get("/test-models")
async def test_models_endpoint(key: Optional[str] = None):
    """
    Checks candidate models one by one against the Google API,
    finds the first working model, and returns the verification report.
    """
    from app.config import settings
    api_key = key or settings.GEMINI_API_KEY
    if not api_key:
        raise HTTPException(status_code=400, detail="No hay API key de Gemini para comprobar.")

    results = await brain_router.probe_candidate_models(api_key)
    return {
        "ok": True,
        "activeModel": brain_router.active_gemini_model,
        "results": results,
    }


@router.post("/switch")
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


class SoulUpdateRequest(BaseModel):
    content: str


class MemoryAddRequest(BaseModel):
    note: str
    target: str = "memory"


@router.get("/soul")
async def get_soul_endpoint():
    """Returns the current SOUL identity and active memories."""
    from app.services.soul_service import soul_service
    return {
        "ok": True,
        "soul": soul_service.get_soul(),
        "userMemory": soul_service.get_user_memory(),
        "systemMemory": soul_service.get_system_memory(),
    }


@router.post("/soul")
async def update_soul_endpoint(req: SoulUpdateRequest):
    """Updates the contents of SOUL.md."""
    from app.services.soul_service import soul_service
    success = soul_service.save_soul(req.content)
    if not success:
        raise HTTPException(status_code=500, detail="No se pudo guardar el archivo SOUL.md")
    return {"ok": True, "message": "SOUL.md actualizado correctamente."}


@router.post("/memories/remember")
async def add_memory_endpoint(req: MemoryAddRequest):
    """Appends a new memory note to USER.md or MEMORY.md."""
    from app.services.soul_service import soul_service
    success = soul_service.append_memory(req.note, req.target)
    if not success:
        raise HTTPException(status_code=500, detail="No se pudo guardar la nota de memoria")
    return {"ok": True, "message": f"Nota guardada en memoria ({req.target})."}


@router.get("/skills")
async def get_skills_endpoint():
    """Lists all modular skills discovered in skills/*/SKILL.md."""
    from app.services.soul_service import soul_service
    return {
        "ok": True,
        "skills": soul_service.list_skills(),
    }

