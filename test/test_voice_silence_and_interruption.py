"""
Tests for Liseth Voice Interruption, Silence Commands ("cállate", "deja de hablar"),
and HTTP Client Lifecycle Hardening.
"""
import asyncio
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.brain_router import brain_router, detect_direct_intent, GEMINI_PRIORITY_MODELS
from app.services.action_dispatcher import ActionDispatcher
from app.services.voice_engine import voice_engine

client = TestClient(app)


def test_gemini_priority_models_verified_active():
    """Verify that verified models (3.1-flash-lite, 2.5-flash, 2.0-flash) are prioritized first."""
    assert GEMINI_PRIORITY_MODELS[0] == "gemini-3.1-flash-lite"
    assert "gemini-2.5-flash" in GEMINI_PRIORITY_MODELS[:4]
    assert "gemini-2.0-flash" in GEMINI_PRIORITY_MODELS[:4]


def test_detect_direct_intent_silence_and_callate():
    """Verify 'cállate', 'silencio', 'deja de hablar', etc. trigger immediate stop_speaking intent."""
    triggers = [
        "cállate",
        "callate",
        "cállate ya",
        "callate ya",
        "deja de hablar",
        "para de hablar",
        "no hables",
        "no hables más",
        "silencio liseth",
        "liseth cállate",
        "liseth callate",
        "shh",
        "shhh",
    ]
    for phrase in triggers:
        res = detect_direct_intent(phrase)
        assert res is not None, f"Failed to detect intent for: '{phrase}'"
        tool_name, args, text = res
        assert tool_name == "stop_speaking", f"Expected 'stop_speaking' for '{phrase}', got '{tool_name}'"
        assert args.get("action") == "stop_speaking"


@pytest.mark.asyncio
async def test_action_dispatcher_stop_speaking():
    """Verify ActionDispatcher handles 'stop_speaking' gracefully."""
    dispatcher = ActionDispatcher()
    res = await dispatcher.execute_tool("stop_speaking", {})
    assert "silencio" in res.lower()
    assert voice_engine.is_speaking is False


def test_voice_engine_stop_speaking_method():
    """Verify VoiceEngine.stop_speaking() sets flags and emits SSE event."""
    voice_engine.is_speaking = True
    voice_engine._stop_requested = False

    events = []
    # Temporary broadcast interceptor
    orig_broadcast = voice_engine.broadcast_event
    voice_engine.broadcast_event = lambda ev, data: events.append((ev, data))
    try:
        voice_engine.stop_speaking()
        assert voice_engine.is_speaking is False
        assert voice_engine._stop_requested is True
        event_types = [e[0] for e in events]
        assert "stop_speaking" in event_types
        assert "speaking" in event_types
    finally:
        voice_engine.broadcast_event = orig_broadcast


def test_api_voice_stop_endpoint():
    """Verify POST /api/voice/stop endpoint halts speaking with 200 OK without requiring authentication."""
    voice_engine.is_speaking = True
    res = client.post("/api/voice/stop")
    assert res.status_code == 200
    data = res.json()
    assert data.get("ok") is True
    assert data.get("stopped") is True
    assert voice_engine.is_speaking is False


@pytest.mark.asyncio
async def test_brain_router_client_loop_resilience():
    """Verify get_client handles loop changes without raising unhandled 'Event loop is closed' tasks."""
    c1 = brain_router.get_client()
    assert c1 is not None

    # Simulate loop change or closed loop without creating orphaned task errors
    brain_router._http_client_loop = None
    c2 = brain_router.get_client()
    assert c2 is not None
    assert not c2.is_closed
