# -*- coding: utf-8 -*-
"""
Tests for Centralized Credentials and Authenticators Router.
Verifies secret masking, inventory generation, environment variable updates,
and credential validation.
"""

import os
from unittest.mock import MagicMock
from app.routers.credentials_router import mask_secret, update_env_file, router
from app.config import settings


def test_mask_secret():
    """Verify secrets are masked properly without leaking full content."""
    assert mask_secret("") == ""
    assert mask_secret(None) == ""
    assert mask_secret("12345") == "••••••••"
    assert mask_secret("AIzaSy1234567890abcdef") == "AIza••••••••cdef"
    assert mask_secret("sk-proj-supersecretkeyhere9999") == "sk-p••••••••9999"


def test_update_env_file(tmp_path, monkeypatch):
    """Verify safe updates and appending of keys to .env."""
    test_env = tmp_path / ".env.test"
    test_env.write_text("# Test environment file\nPORT=3000\nGEMINI_API_KEY=old_gemini\n", encoding="utf-8")

    monkeypatch.setattr("app.routers.credentials_router.ENV_PATH", test_env)

    update_env_file({
        "GEMINI_API_KEY": "new_gemini_key",
        "GROQ_API_KEY": "gsk_test_groq",
        "DAILY_TOKEN_LIMIT": 150000
    })

    content = test_env.read_text(encoding="utf-8")
    assert "GEMINI_API_KEY=new_gemini_key" in content
    assert "old_gemini" not in content
    assert "GROQ_API_KEY=gsk_test_groq" in content
    assert "DAILY_TOKEN_LIMIT=150000" in content
    assert "PORT=3000" in content


def test_credentials_inventory_structure():
    """Verify inventory contains all required categories and fields."""
    from fastapi import Request
    from app.routers.credentials_router import get_credentials

    req = MagicMock(spec=Request)
    req.cookies = {}
    req.headers = {}

    res = get_credentials(req, reveal=False)
    assert res["ok"] is True
    categories = res["categories"]

    assert "llm" in categories
    assert "voice" in categories
    assert "google" in categories
    assert "messaging" in categories
    assert "search_academic" in categories
    assert "git_cloud" in categories
    assert "security" in categories

    llm_items = {item["id"]: item for item in categories["llm"]["items"]}
    assert "GEMINI_API_KEY" in llm_items
    assert "ANTHROPIC_API_KEY" in llm_items
    assert "GROQ_API_KEY" in llm_items
    assert "OPENAI_API_KEY" in llm_items
    assert "OLLAMA_ENABLED" in llm_items

    msg_items = {item["id"]: item for item in categories["messaging"]["items"]}
    assert "TELEGRAM_BOT_TOKEN" in msg_items
    assert "META_WA_ACCESS_TOKEN" in msg_items

    git_items = {item["id"]: item for item in categories["git_cloud"]["items"]}
    assert "GITHUB_TOKEN" in git_items


def test_credentials_vault_intent():
    """Verify brain_router accurately detects credentials vault opening intent."""
    from app.services.brain_router import detect_direct_intent

    queries = [
        "abre el menú de apis",
        "menu de apis",
        "bóveda de credenciales",
        "configurar autenticadores",
        "mis claves api"
    ]
    for q in queries:
        res = detect_direct_intent(q)
        assert res is not None, f"Failed to match query: {q}"
        tool_name, tool_args, reply = res
        assert tool_name == "credentials_vault"
        assert tool_args["action"] == "open"
        assert "Santiago" in reply

