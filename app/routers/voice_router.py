"""
Voice Router for JARVIS / Liseth.
Provides API endpoints and Server-Sent Events (SSE) for the native voice engine,
allowing both the web HUD and native desktop window to stay perfectly synchronized.
"""
import asyncio
import io
import json
import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, File, HTTPException, Request, Response, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.voice_engine import voice_engine

logger = logging.getLogger("jarvis.voice_router")

router = APIRouter(prefix="/api/voice", tags=["voice"])


class StateChangeRequest(BaseModel):
    state: str  # "active" | "standby" | "off"


@router.get("/state")
async def get_voice_state():
    """Returns current voice engine state and activity telemetry."""
    return {
        "ok": True,
        "state": voice_engine.state,
        "isRunning": voice_engine.is_running,
        "isSpeaking": voice_engine.is_speaking,
        "isThinking": voice_engine.is_thinking,
        "lastTranscript": voice_engine.last_transcript,
    }


@router.post("/toggle")
async def toggle_voice_state():
    """
    Toggles voice state:
    - off -> active
    - active -> standby
    - standby -> active
    """
    if not voice_engine.is_running:
        voice_engine.start()
        voice_engine.set_state("active", play_chime=True)
    elif voice_engine.state == "active":
        voice_engine.set_state("standby", play_chime=True)
    elif voice_engine.state == "standby":
        voice_engine.set_state("active", play_chime=True)
    else:
        voice_engine.set_state("active", play_chime=True)

    return {
        "ok": True,
        "state": voice_engine.state,
        "isRunning": voice_engine.is_running,
    }


@router.post("/state")
async def set_voice_state(req: StateChangeRequest):
    """Sets voice assistant state explicitly."""
    target = req.state.lower().strip()
    if target not in ["active", "standby", "off"]:
        raise HTTPException(status_code=400, detail="Estado inválido. Use 'active', 'standby' u 'off'.")

    if target == "off":
        voice_engine.stop()
    else:
        if not voice_engine.is_running:
            voice_engine.start()
        voice_engine.set_state(target, play_chime=True)

    return {"ok": True, "state": voice_engine.state}


@router.post("/transcribe")
async def transcribe_audio_file(file: UploadFile = File(...)):
    """
    Fallback endpoint: transcribes and executes audio uploaded directly from
    browser MediaRecorder (useful when client browser lacks SpeechRecognition).
    """
    try:
        import speech_recognition as sr
        audio_bytes = await file.read()
        r = sr.Recognizer()

        # Try to read audio file format
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="es-CO")

        text = text.strip()
        if text:
            # Execute command
            from app.services.brain_router import brain_router
            from app.services.soul_service import soul_service
            sys_inst = soul_service.build_system_instruction()
            res = await brain_router.generate_response(prompt=text, system_prompt=sys_inst)
            return {
                "ok": True,
                "text": text,
                "response": res.get("text", ""),
                "executedTools": res.get("executedTools", []),
            }
        return {"ok": False, "error": "No se detectó habla en el audio."}
    except Exception as e:
        logger.warning(f"Error procesando audio subido: {e}")
        return {"ok": False, "error": str(e)}


@router.get("/events")
async def voice_events_sse(request: Request):
    """
    Server-Sent Events (SSE) stream for real-time synchronization between the native
    Python voice engine and the Web/Desktop HUD (orb, transcript, subtitles, state).
    """
    queue = voice_engine.subscribe()

    async def event_generator():
        # Send initial state immediately
        initial = {
            "type": "state_change",
            "state": voice_engine.state,
            "isRunning": voice_engine.is_running,
            "isSpeaking": voice_engine.is_speaking,
        }
        yield f"data: {json.dumps(initial)}\n\n"

        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event_data = await asyncio.wait_for(queue.get(), timeout=20.0)
                    yield f"data: {json.dumps(event_data)}\n\n"
                except asyncio.TimeoutError:
                    # Keep-alive heartbeat
                    yield ": ping\n\n"
        finally:
            voice_engine.unsubscribe(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
