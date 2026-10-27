"""
Unit tests for BrainRouter failover and cost tracking with mocks.
"""
from unittest.mock import AsyncMock, patch
import pytest
from app.services.brain_router import BrainRouter


@pytest.mark.asyncio
async def test_brain_router_normal_gemini_success():
    router = BrainRouter()
    router.call_gemini = AsyncMock(return_value={
        "text": "Respuesta desde Gemini",
        "brain": "gemini",
        "model": "gemini-2.0-flash",
        "usage": {"input": 15, "output": 25},
        "failover": False,
    })
    router.call_claude = AsyncMock()

    result = await router.generate_response("Hola Liseth")
    assert result["text"] == "Respuesta desde Gemini"
    assert result["brain"] == "gemini"
    assert result["failover"] is False
    assert router.active_brain == "gemini"
    router.call_gemini.assert_awaited_once()
    router.call_claude.assert_not_awaited()


@pytest.mark.asyncio
async def test_brain_router_failover_to_claude():
    router = BrainRouter()
    router.call_gemini = AsyncMock(side_effect=Exception("Gemini 503 Overloaded"))
    router.call_groq = AsyncMock(side_effect=Exception("Groq unavailable"))
    router.call_claude = AsyncMock(return_value={
        "text": "Respuesta desde Claude de respaldo",
        "brain": "claude",
        "model": "claude-3-5-sonnet",
        "usage": {"input": 15, "output": 30},
        "failover": True,
    })

    result = await router.generate_response("Hola Liseth en contingencia")
    assert result["text"] == "Respuesta desde Claude de respaldo"
    assert result["brain"] == "claude"
    assert result["failover"] is True
    assert router.active_brain == "claude"
    assert router.last_failover is not None
    assert "Gemini 503 Overloaded" in router.last_failover["reason"]

    router.call_gemini.assert_awaited_once()
    router.call_claude.assert_awaited_once()


def test_brain_router_token_cost_tracking():
    router = BrainRouter()
    initial_cost = router.stats["today"]["cost_estimate"]

    router.record_usage("gemini", input_tokens=1000, output_tokens=1000, model="gemini-2.0-flash")
    new_cost = router.stats["today"]["cost_estimate"]
    assert new_cost > initial_cost
    assert round(new_cost - initial_cost, 6) == 0.0005


@pytest.mark.asyncio
async def test_brain_router_failover_to_groq():
    router = BrainRouter()
    router.call_gemini = AsyncMock(side_effect=Exception("Gemini 503 Overloaded"))
    router.call_groq = AsyncMock(return_value={
        "text": "Respuesta desde Groq Llama 3.3",
        "brain": "groq",
        "model": "llama-3.3-70b-versatile",
        "usage": {"input": 12, "output": 24},
        "failover": True,
    })

    result = await router.generate_response("Hola Liseth con Groq")
    assert result["text"] == "Respuesta desde Groq Llama 3.3"
    assert result["brain"] == "groq"
    assert router.active_brain == "groq"
    router.call_gemini.assert_awaited_once()
    router.call_groq.assert_awaited_once()


@pytest.mark.asyncio
async def test_brain_router_failover_cascade_all_down_graceful_notice():
    router = BrainRouter()
    router.call_gemini = AsyncMock(side_effect=Exception("Gemini 503 Overloaded"))
    router.call_groq = AsyncMock(side_effect=Exception("Groq unavailable"))
    router.call_claude = AsyncMock(side_effect=Exception("Claude unavailable"))
    router.call_openai = AsyncMock(side_effect=Exception("OpenAI unavailable"))
    router.call_ollama = AsyncMock(side_effect=Exception("Ollama unavailable"))
    router.call_pollinations_free = AsyncMock(side_effect=Exception("Pollinations 503"))

    with patch("app.services.embedded_brain.embedded_engine.process", side_effect=Exception("Embedded core down")):
        result = await router.generate_response("Hola Liseth en corte total")
        assert result["brain"] == "system"
        assert result.get("autonomousNotice") is True
        assert "503" in result["text"]


@pytest.mark.asyncio
async def test_brain_router_failover_to_embedded_core():
    router = BrainRouter()
    router.call_gemini = AsyncMock(side_effect=Exception("Gemini 503 Overloaded"))
    router.call_groq = AsyncMock(side_effect=Exception("Groq unavailable"))
    router.call_claude = AsyncMock(side_effect=Exception("Claude unavailable"))
    router.call_openai = AsyncMock(side_effect=Exception("OpenAI unavailable"))
    router.call_ollama = AsyncMock(side_effect=Exception("Ollama unavailable"))
    router.call_pollinations_free = AsyncMock(side_effect=Exception("Pollinations 503"))

    result = await router.generate_response("Hola Liseth en contingencia offline")
    assert result["brain"] == "liseth-embedded-core"
    assert router.active_brain == "embedded-cognitive"
