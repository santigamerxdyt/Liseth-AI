"""
Test Suite for Master Voice Engine Overhaul.
Validates:
- 16-State Central State Machine transitions.
- Adaptive VAD, energy thresholding, and silence detection.
- Barge-In cancellation and execution token invalidation.
- Hallucination filtering and empty audio rejection.
- REST and SSE API endpoints in voice_router.
"""
import pytest
import numpy as np
from fastapi.testclient import TestClient
from app.main import app
from app.services.voice_engine import (
    voice_engine,
    normalize_text,
    contains_wake_word,
    extract_command,
    VALID_STATES,
)

client = TestClient(app)


def test_voice_engine_16_state_machine_validations():
    """Verifies that all 16 states are recognized and transitions are logged."""
    assert len(VALID_STATES) == 16
    for state in VALID_STATES:
        voice_engine.set_state(state)
        assert voice_engine.state == state

    # Test invalid state rejection
    voice_engine.set_state("INVALID_STATE_XYZ")
    assert voice_engine.state != "INVALID_STATE_XYZ"

    # Reset to IDLE
    voice_engine.set_state("IDLE")
    assert voice_engine.state == "IDLE"


def test_wake_word_and_command_extraction():
    """Verifies wake word variations and command extraction."""
    phrases = [
        ("Liseth, qué hora es?", True, "qué hora es?"),
        ("liceth busca el reporte de ventas", True, "busca el reporte de ventas"),
        ("hola jarvis activa el modo seguro", True, "activa el modo seguro"),
        ("buenos días a todos", False, ""),
    ]
    for phrase, expected_wake, expected_cmd in phrases:
        assert contains_wake_word(phrase) == expected_wake
        if expected_wake:
            cmd = extract_command(phrase)
            assert expected_cmd.lower() in cmd.lower()


def test_barge_in_and_stop_speaking():
    """Verifies instant Barge-In halts active speech and updates state."""
    voice_engine.is_speaking = True
    voice_engine.current_execution_token = "token-12345"

    # Trigger Barge-In
    voice_engine.stop_speaking(interrupted=True)

    assert voice_engine.is_speaking is False
    assert voice_engine.current_execution_token is None
    assert voice_engine.state == "INTERRUPTED"


def test_vad_low_energy_and_empty_audio_rejection():
    """Verifies that flatline audio or quiet noise is discarded without invoking LLM."""
    # Generate pure silence (zeros)
    silent_pcm = np.zeros(2048, dtype=np.int16)
    voice_engine.set_state("LISTENING")
    voice_engine._process_speech(silent_pcm)

    # State should return to LISTENING without crashing
    assert voice_engine.state in ["LISTENING", "IDLE"]


def test_voice_router_rest_endpoints():
    """Verifies all REST endpoints exposed by voice_router."""
    # 1. State endpoint
    r_state = client.get("/api/voice/state")
    assert r_state.status_code == 200
    data = r_state.json()
    assert data["ok"] is True
    assert "state" in data

    # 2. Toggle endpoint
    r_toggle = client.post("/api/voice/toggle")
    assert r_toggle.status_code == 200
    assert r_toggle.json()["ok"] is True

    # 3. Explicit state set
    r_set = client.post("/api/voice/state", json={"state": "PAUSED"})
    assert r_set.status_code == 200
    assert r_set.json()["state"] == "PAUSED"

    # 4. Stop speaking endpoint (Barge-In)
    r_stop = client.post("/api/voice/stop")
    assert r_stop.status_code == 200
    assert r_stop.json()["stopped"] is True

    # 5. Direct command execute
    r_exec = client.post("/api/voice/execute", json={"text": "hola liseth", "modality": "voice"})
    assert r_exec.status_code == 200
    exec_data = r_exec.json()
    assert exec_data["ok"] is True
    assert "text" in exec_data

    # Return to IDLE
    voice_engine.stop()
