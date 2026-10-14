"""
Tests for TTS endpoint and synthesis.
"""
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_tts_endpoint_success():
    fake_audio = b"\xff\xfb\x90\x00" * 50  # MP3 frame simulation
    with patch("app.routers.tts_router.synthesize_speech", new=AsyncMock(return_value=fake_audio)):
        response = client.get("/api/tts?text=Hola+Santiago&voice=es-MX-DaliaNeural")
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"
        assert response.content == fake_audio


def test_tts_endpoint_empty_text():
    response = client.get("/api/tts?text=")
    assert response.status_code == 422  # validation error for min_length=1
