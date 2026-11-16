"""
Test Suite for Hermes Multi-Agent System & 4 Integrated Repositories.
Validates:
- Hermes Agent Adapter, Session Isolation, and Named Agents.
- Central Hermes AI Orchestrator.
- Archify Architecture Diagram Generator.
- OpenMontage Media Adapter (Subtitles & Audio Mixing).
- OmniRoute AI Gateway (Health, Fallbacks & Token Compression).
- Diffin Binary & Artifact Analysis.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.hermes_adapter import hermes_adapter
from app.services.hermes_orchestrator import hermes_orchestrator
from app.services.archify_service import archify_service
from app.services.openmontage_adapter import openmontage_adapter
from app.services.omniroute_gateway import omniroute_gateway
from app.services.diffin_service import diffin_service


def test_hermes_named_agents_catalog():
    """Verifies all 8 Hermes Named Agents are initialized with distinct profiles."""
    agents = hermes_adapter.list_named_agents()
    assert len(agents) == 8
    agent_names = {a["name"] for a in agents}
    expected = {
        "Main Assistant", "Research Agent", "Coding Agent", "Voice Agent",
        "Data Agent", "Business Agent", "Media Agent", "Documentation Agent"
    }
    assert agent_names == expected


def test_hermes_dynamic_agent_selection():
    """Verifies heuristic prompt routing maps to the correct specialized agent."""
    cases = [
        ("Corrige este error en el script de Python", "Coding Agent"),
        ("Busca papers de investigación en ArXiv con formato APA", "Research Agent"),
        ("Analiza el MRR y la economía unitaria de los planes", "Business Agent"),
        ("Genera subtítulos y mezcla el audio de este video", "Media Agent"),
        ("Dibuja un diagrama de arquitectura con Archify", "Documentation Agent"),
        ("Calcula la media y dispersión de este dataset", "Data Agent"),
        ("Sube el volumen del micrófono", "Voice Agent"),
        ("Buenos días, organízame la agenda de hoy", "Main Assistant"),
    ]
    for prompt, expected_agent in cases:
        selected = hermes_adapter.select_agent_for_prompt(prompt)
        assert selected.name == expected_agent, f"Failed routing for '{prompt}': got {selected.name}"


@pytest.mark.asyncio
async def test_hermes_orchestrator_execution():
    """Verifies end-to-end execution of Hermes AI Orchestrator."""
    res = await hermes_orchestrator.route_and_execute(
        prompt="Hola Liseth, reporte de estado",
        session_id="test_session_123",
        modality="voice"
    )
    assert res["ok"] is True
    assert "agent" in res
    assert "text" in res
    assert res["latency_ms"] >= 0.0


def test_archify_diagram_generation():
    """Verifies Archify code-to-diagram generators produce valid Mermaid code."""
    v_diag = archify_service.generate_voice_pipeline_diagram()
    assert "flowchart TD" in v_diag
    assert "Hardware Microphone" in v_diag
    assert "Barge-In" in v_diag

    m_diag = archify_service.generate_hermes_multiagent_diagram()
    assert "graph TD" in m_diag
    assert "Hermes Named Agents" in m_diag

    t_diag = archify_service.generate_system_topology()
    assert "flowchart LR" in t_diag
    assert "Cyber-HUD" in t_diag


def test_openmontage_subtitles_and_audio_mixing():
    """Verifies OpenMontage WebVTT, SRT, and audio mixing."""
    segments = [
        {"start": 0.0, "end": 1.5, "text": "Buenos días, Señor Santiago."},
        {"start": 1.5, "end": 3.8, "text": "Todos los sistemas de Liseth están operativos."},
    ]
    vtt = openmontage_adapter.generate_subtitles_vtt(segments)
    assert "WEBVTT" in vtt
    assert "00:00:00.000 --> 00:00:01.500" in vtt
    assert "Señor Santiago" in vtt

    srt = openmontage_adapter.generate_subtitles_srt(segments)
    assert "00:00:00,000 --> 00:00:01,500" in srt
    assert "1" in srt and "2" in srt

    # Audio track mixing
    dummy_voice = b"\x00\x10" * 100
    dummy_bg = b"\x00\x05" * 100
    mixed = openmontage_adapter.mix_audio_tracks(dummy_voice, dummy_bg, voice_gain=1.0, bg_gain=0.3)
    assert len(mixed) == len(dummy_voice)


def test_omniroute_gateway_and_compression():
    """Verifies OmniRoute route selection, health tracking, and token compression."""
    status = omniroute_gateway.get_provider_status()
    assert "groq" in status
    assert "gemini" in status

    best_speed = omniroute_gateway.select_best_route("speed")
    assert best_speed in ["groq", "gemini"]

    # Compression test
    uncompressed = "Buenos días a todos.   \n\n\n\n   Esta es una prueba de optimización.   "
    compressed = omniroute_gateway.compress_prompt_conservatively(uncompressed)
    assert "  " not in compressed
    assert "\n\n\n" not in compressed
    assert "prueba de optimización" in compressed

    # Code protection in compression
    code_text = "def test():\n    print('keep indent')"
    assert omniroute_gateway.compress_prompt_conservatively(code_text) == code_text


def test_diffin_binary_hash_and_audio_inspection():
    """Verifies Diffin hash calculation and audio header validation."""
    dummy_data = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00"
    hashes = diffin_service.compute_hashes(dummy_data)
    assert "sha256" in hashes
    assert "md5" in hashes

    header_info = diffin_service.inspect_audio_header(dummy_data)
    assert header_info["valid"] is True
    assert header_info["format"] == "WAV/RIFF"

    # Compare identical artifacts
    comp_same = diffin_service.compare_binary_artifacts(dummy_data, dummy_data)
    assert comp_same["identical"] is True
    assert comp_same["similarity_ratio"] == 1.0

    # Compare different artifacts
    comp_diff = diffin_service.compare_binary_artifacts(dummy_data, b"COMPLETELY DIFFERENT")
    assert comp_diff["identical"] is False
    assert comp_diff["similarity_ratio"] < 1.0


def test_hermes_skills_catalog_and_endpoint():
    """Verifies that hermes_adapter discovers installed skills including 10k-websites and serves them via API."""
    skills = hermes_adapter.list_available_skills()
    assert len(skills) > 0
    k10 = [s for s in skills if s["id"] == "10k-websites"]
    assert len(k10) == 1
    assert k10[0]["status"] == "ready"

    # API endpoint check
    client = TestClient(app)
    res = client.get("/api/voice/skills")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert any(s["id"] == "10k-websites" for s in data["skills"])
