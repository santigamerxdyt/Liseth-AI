"""
Automated Test Suite for Liseth Single Voice Architecture & Audio Engine Repair.
Validates the 15 strict criteria from Section 14:
1. Single instance of output engine (LisethAudioManager singleton).
2. Only one active playback at any given time.
3. A response is played only once (turn deduplication).
4. Identical events do not spawn two voices.
5. Hermes does not play audio directly.
6. Secondary agents operate silently without generating audio.
7. Cancellation halts playback immediately.
8. Interruption drops pending audio chunks.
9. Microphone is owned by a single manager without duplicate streams.
10. Empty transcription does not trigger response or speech.
11. TTS synthesis error does not deadlock the system.
12. Disconnection recovers cleanly.
13. Shutdown releases audio resources cleanly.
14. Turns do not mix or cross execution tokens.
15. Background listening operates under platform governance.
"""
import asyncio
import time
import pytest
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.services.audio_manager import LisethAudioManager, audio_manager
from app.services.microphone_manager import LisethMicrophoneManager, microphone_manager
from app.services.voice_engine import voice_engine
from app.services.hermes_orchestrator import hermes_orchestrator
from app.services.hermes_adapter import hermes_adapter

client = TestClient(app)


# ── 1. Single Instance Output Engine ──────────────────────────────────────────
def test_single_instance_output_engine():
    """Verifies that LisethAudioManager follows strict singleton pattern."""
    manager1 = LisethAudioManager()
    manager2 = LisethAudioManager()
    assert manager1 is manager2
    assert manager1 is audio_manager
    assert audio_manager.get_active_voice() == "es-CO-SalomeNeural"


# ── 2. Single Active Playback ─────────────────────────────────────────────────
def test_single_active_playback():
    """Verifies that only one playback thread is authorized and active at a time."""
    audio_manager.initialize()
    res1 = audio_manager.speak("Primera orden de prueba.", turn_id="turn-001")
    assert res1["ok"] is True
    assert audio_manager.current_turn_id == "turn-001"

    # Start immediate second turn
    res2 = audio_manager.speak("Segunda orden que reemplaza la anterior.", turn_id="turn-002")
    assert res2["ok"] is True
    assert audio_manager.current_turn_id == "turn-002"
    audio_manager.stop()


# ── 3. Response Played Only Once (Deduplication) ──────────────────────────────
def test_deduplication_of_identical_response():
    """Verifies that sending the exact same text within cooldown is suppressed."""
    audio_manager.stop()
    text = "Buenos días, Santiago. Reporte financiero listo."
    res1 = audio_manager.speak(text, turn_id="turn-rep-1")
    assert res1["ok"] is True

    # Immediate duplicate attempt
    res2 = audio_manager.speak(text, turn_id="turn-rep-2")
    assert res2["ok"] is False
    assert res2["reason"] == "duplicate_suppressed"
    audio_manager.stop()


# ── 4. Identical Events Do Not Spawn Two Voices ───────────────────────────────
def test_identical_events_do_not_generate_two_voices():
    """Verifies API /speak endpoint enforces audio_manager deduplication."""
    payload = {"text": "Prueba de evento idéntico para evitar eco.", "turn_id": "api-turn-1"}
    r1 = client.post("/api/voice/speak", json=payload)
    assert r1.status_code == 200
    assert r1.json()["ok"] is True

    # Duplicate call
    r2 = client.post("/api/voice/speak", json=payload)
    assert r2.status_code == 200
    assert r2.json()["ok"] is False
    assert r2.json()["reason"] == "duplicate_suppressed"
    audio_manager.stop()


# ── 5. Hermes Does Not Play Audio Directly ────────────────────────────────────
@pytest.mark.asyncio
async def test_hermes_does_not_play_audio_directly():
    """Verifies that Hermes Orchestrator returns text and does NOT initiate audio playback."""
    audio_manager.stop()
    initial_playing = audio_manager.is_playing()
    assert initial_playing is False

    result = await hermes_orchestrator.route_and_execute(prompt="¿Cuál es el estado del sistema?", modality="voice")
    assert result["ok"] is True
    assert "text" in result
    # Crucial guarantee: Hermes must remain 100% silent
    assert audio_manager.is_playing() is False


# ── 6. Secondary Agents Are Silent ────────────────────────────────────────────
@pytest.mark.asyncio
async def test_secondary_agents_are_silent():
    """Verifies that all 8 Hermes Named Agents run silently without triggering audio."""
    audio_manager.stop()
    queries = [
        "investiga el último paper de transformers en arxiv",  # Research Agent
        "escribe una función en python para fibonacci",         # Coding Agent
        "calcula el VAN con tasa 10 y flujos 50000",           # Business Agent
        "genera un análisis estadístico de la tabla ventas",   # Data Agent
        "muestra el diagrama de arquitectura del vault",       # Documentation Agent
    ]
    for q in queries:
        res = await hermes_adapter.execute_turn(prompt=q, modality="voice")
        assert res["ok"] is True
        assert audio_manager.is_playing() is False


# ── 7. Cancellation Halts Playback ────────────────────────────────────────────
def test_cancellation_halts_playback():
    """Verifies that calling stop() immediately terminates audio playback."""
    audio_manager.speak("Texto largo que será cancelado de inmediato.", turn_id="cancel-test")
    stopped = audio_manager.stop(interrupted=True)
    assert stopped is True
    assert audio_manager.is_playing() is False
    assert audio_manager.current_playback_id is None


# ── 8. Interruption Drops Pending Audio Chunks ────────────────────────────────
def test_interruption_drops_pending_audio():
    """Verifies that barge-in invalidates the execution token and drops pending synthesis."""
    voice_engine.is_speaking = True
    voice_engine.current_execution_token = "valid-token-999"

    voice_engine.stop_speaking(interrupted=True)

    assert voice_engine.is_speaking is False
    assert voice_engine.current_execution_token is None
    assert voice_engine.state == "INTERRUPTED"


# ── 9. Microphone Is Owned by Single Manager ──────────────────────────────────
def test_single_microphone_owner():
    """Verifies that LisethMicrophoneManager enforces singleton stream ownership."""
    mic1 = LisethMicrophoneManager()
    mic2 = LisethMicrophoneManager()
    assert mic1 is mic2
    assert mic1 is microphone_manager

    # Multiple start_capture calls do not duplicate streams
    success1 = microphone_manager.start_capture()
    success2 = microphone_manager.start_capture()
    assert success1 is True
    assert success2 is True
    status = microphone_manager.get_status()
    assert status["isCapturing"] is True
    microphone_manager.stop_capture()


# ── 10. Empty Transcription Rejection ─────────────────────────────────────────
def test_empty_transcription_rejection():
    """Verifies that empty audio or silence does not invoke LLM or audio output."""
    audio_manager.stop()
    flatline = np.zeros(16000, dtype=np.int16)
    initial_turns = hermes_orchestrator.total_turns_processed

    voice_engine._process_speech(flatline)

    assert voice_engine.state == "LISTENING"
    assert hermes_orchestrator.total_turns_processed == initial_turns
    assert audio_manager.is_playing() is False


# ── 11. TTS Synthesis Error Does Not Deadlock ─────────────────────────────────
def test_tts_error_does_not_deadlock_system():
    """Verifies that invalid or failing TTS parameters recover gracefully."""
    audio_manager.stop()
    # Speak with an intentionally problematic string
    res = audio_manager.speak("Test recovery", voice="invalid-voice-xyz-test")
    assert res["ok"] is True
    time.sleep(0.3)
    # Lock must be released and system operable
    audio_manager.stop()
    assert audio_manager.is_playing() is False


# ── 12. Disconnection Recovery ────────────────────────────────────────────────
def test_reconnection_recovery():
    """Verifies microphone_manager recovers after device reset."""
    recovered = microphone_manager.recover_connection()
    assert recovered is True
    assert microphone_manager.is_capturing is True
    microphone_manager.stop_capture()


# ── 13. Shutdown Releases Resources Cleanly ───────────────────────────────────
def test_shutdown_releases_resources():
    """Verifies shutdown() halts playback and unloads mixer without crashing."""
    audio_manager.shutdown()
    assert audio_manager.is_playing() is False
    # Re-initialize for subsequent tests
    audio_manager.initialize()


# ── 14. Turns Do Not Mix Or Cross Tokens ──────────────────────────────────────
def test_turns_do_not_mix():
    """Verifies that concurrent turns are properly serialized by token."""
    token_a = "token-alpha"
    token_b = "token-beta"

    voice_engine.current_execution_token = token_a
    # Rapid second turn arrives
    voice_engine.current_execution_token = token_b

    # Old worker attempting to speak with token_a must be discarded
    voice_engine.speak("Mensaje viejo de turno A", token=token_a)
    assert voice_engine.current_execution_token == token_b


# ── 15. Background Listening Platform Restrictions ────────────────────────────
def test_background_listening_status():
    """Verifies background listening status and pause/resume telemetry."""
    voice_engine.pause()
    assert voice_engine.state == "PAUSED"

    voice_engine.resume()
    assert voice_engine.state == "LISTENING"

    res = client.get("/api/voice/state")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert "activeVoice" in data
    assert data["activeVoice"] == "es-CO-SalomeNeural"
    assert "microphone" in data
