"""
Voice Router Master Overhaul for Liseth // JARVIS.
Exposes REST and SSE endpoints for:
- 16-state voice state machine telemetry.
- Barge-In speech cancellation and stop speaking.
- Audio buffer ingestion and STT transcription via Hermes AI Orchestrator.
- Multi-agent inspection and OmniRoute gateway status.
- Real-time Server-Sent Events (SSE) stream for HUD synchronization.
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
from app.services.audio_manager import audio_manager
from app.services.microphone_manager import microphone_manager
from app.services.hermes_orchestrator import hermes_orchestrator
from app.services.hermes_adapter import hermes_adapter
from app.services.omniroute_gateway import omniroute_gateway
from app.services.archify_service import archify_service

logger = logging.getLogger("jarvis.voice_router")

router = APIRouter(prefix="/api/voice", tags=["voice"])


class StateChangeRequest(BaseModel):
    state: str  # Any valid 16-state value e.g. "LISTENING", "PAUSED", "IDLE"


class AudioProcessRequest(BaseModel):
    text: str
    session_id: Optional[str] = "default_session"
    modality: Optional[str] = "voice"


class SpeakRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    turn_id: Optional[str] = None


@router.post("/stop")
async def stop_voice_speaking():
    """Immediately halts active speech output (Barge-In) and notifies connected clients."""
    voice_engine.stop_speaking(interrupted=True)
    return {"ok": True, "stopped": True, "state": voice_engine.state}


@router.get("/state")
async def get_voice_state():
    """Returns current 16-state machine value, activity indicators, and single audio manager status."""
    return {
        "ok": True,
        "state": voice_engine.state,
        "isRunning": voice_engine.is_running,
        "isSpeaking": voice_engine.is_speaking or audio_manager.is_playing(),
        "isThinking": voice_engine.is_thinking,
        "activeVoice": audio_manager.get_active_voice(),
        "lastTranscript": voice_engine.last_transcript,
        "lastError": voice_engine.last_error,
        "energyThreshold": voice_engine.energy_threshold,
        "microphone": microphone_manager.get_status(),
        "currentTurnId": audio_manager.current_turn_id,
        "currentPlaybackId": audio_manager.current_playback_id,
    }


@router.post("/speak")
async def speak_text_endpoint(req: SpeakRequest):
    """Routes explicit text speech through the single authorized LisethAudioManager."""
    res = audio_manager.speak(
        text=req.text,
        voice=req.voice or audio_manager.official_voice,
        turn_id=req.turn_id
    )
    return res


@router.post("/toggle")
async def toggle_voice_state():
    """Toggles voice engine between LISTENING, PAUSED, and IDLE."""
    if not voice_engine.is_running:
        voice_engine.start()
        voice_engine.set_state("LISTENING", play_chime=True)
    elif voice_engine.state in ["LISTENING", "RECORDING", "SPEECH_DETECTED"]:
        voice_engine.pause()
    elif voice_engine.state == "PAUSED":
        voice_engine.resume()
    else:
        voice_engine.set_state("LISTENING", play_chime=True)

    return {
        "ok": True,
        "state": voice_engine.state,
        "isRunning": voice_engine.is_running,
    }


@router.post("/state")
async def set_voice_state(req: StateChangeRequest):
    """Sets voice assistant state explicitly."""
    target = req.state.upper().strip()
    from app.services.voice_engine import VALID_STATES
    if target not in VALID_STATES:
        raise HTTPException(
            status_code=400,
            detail=f"Estado inválido. Opciones válidas: {sorted(list(VALID_STATES))}"
        )

    if target == "IDLE":
        voice_engine.stop()
    elif target == "PAUSED":
        voice_engine.pause()
    else:
        if not voice_engine.is_running:
            voice_engine.start()
        voice_engine.set_state(target, play_chime=True)

    return {"ok": True, "state": voice_engine.state}


@router.post("/execute")
async def execute_voice_command(req: AudioProcessRequest):
    """
    Direct endpoint to process command text through Hermes AI Orchestrator
    and return structured response, agent metadata, and tools.
    """
    res = await hermes_orchestrator.route_and_execute(
        prompt=req.text,
        session_id=req.session_id or "default_session",
        modality=req.modality or "voice"
    )
    return res


@router.post("/transcribe")
async def transcribe_audio_file(file: UploadFile = File(...)):
    """
    Transcribes uploaded audio buffer (e.g. from browser MediaRecorder)
    and executes command through Hermes AI Orchestrator.
    """
    try:
        import speech_recognition as sr
        audio_bytes = await file.read()

        if len(audio_bytes) < 400:
            return {"ok": False, "error": "Audio vacío o demasiado corto"}

        r = sr.Recognizer()
        audio_file = io.BytesIO(audio_bytes)
        try:
            with sr.AudioFile(audio_file) as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data, language="es-CO")
        except Exception:
            # Fallback direct recognition if raw pcm
            audio_data = sr.AudioData(audio_bytes, 16000, 2)
            text = r.recognize_google(audio_data, language="es-CO")

        text = text.strip()
        if text:
            res = await hermes_orchestrator.route_and_execute(prompt=text, modality="voice")
            return {
                "ok": True,
                "text": text,
                "agent": res.get("agent", "Main Assistant"),
                "response": res.get("text", ""),
                "executedTools": res.get("executedTools", []),
            }
        return {"ok": False, "error": "No se detectó habla en el audio."}
    except Exception as e:
        logger.warning(f"Error procesando audio subido: {e}")
        return {"ok": False, "error": str(e)}


@router.get("/agents")
async def get_hermes_agents():
    """Returns catalog of registered Hermes Named Agents."""
    return {"ok": True, "agents": hermes_adapter.list_named_agents()}


@router.get("/skills")
async def get_hermes_skills():
    """Returns catalog of active skills available to Hermes and Liseth."""
    return {"ok": True, "skills": hermes_adapter.list_available_skills()}


@router.get("/gateway")
async def get_omniroute_status():
    """Returns OmniRoute AI Gateway health status and latency telemetry."""
    return {"ok": True, "gateway": omniroute_gateway.get_provider_status()}


@router.get("/diagram")
async def get_architecture_diagram():
    """Returns Mermaid architecture diagram generated via Archify."""
    return {
        "ok": True,
        "voice_pipeline": archify_service.generate_voice_pipeline_diagram(),
        "multiagent": archify_service.generate_hermes_multiagent_diagram(),
        "topology": archify_service.generate_system_topology()
    }


@router.get("/events")
async def voice_events_sse(request: Request):
    """
    Server-Sent Events (SSE) stream for real-time synchronization between the native
    Python voice engine and the Web/Desktop Cyber-HUD.
    """
    queue = voice_engine.subscribe()

    async def event_generator():
        initial = {
            "type": "state_change",
            "state": voice_engine.state,
            "isRunning": voice_engine.is_running,
            "isSpeaking": voice_engine.is_speaking or audio_manager.is_playing(),
            "singleVoiceActive": True,
            "officialVoice": audio_manager.get_active_voice(),
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
