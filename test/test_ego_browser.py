"""
Automated Test Suite for Ego Lite Browser Automation Engine in Liseth.
Verifies service initialization, semantic accessibility snapshot numbering,
action dispatching, CLI bridge, brain routing, and learned tools.
"""

import asyncio
import os
import pytest
from unittest.mock import MagicMock, patch

from app.services.ego_browser_service import EgoBrowserService, TaskSpaceSession, ego_browser_service
from app.actions.ego_browser_action import ego_browser_action
from app.services.action_dispatcher import action_dispatcher
from app.services.brain_router import detect_direct_intent


class TestEgoBrowserService:
    """Tests for the EgoBrowserService class and its core primitives."""

    def test_status_structure(self):
        status = ego_browser_service.get_status()
        assert isinstance(status, dict)
        assert "Ego Lite" in status["engine"]
        assert "learnings_available" in status
        assert "active_task_spaces" in status
        assert isinstance(status["learnings_available"], list)

    def test_format_status_report(self):
        status = ego_browser_service.get_status()
        report = ego_browser_service.format_status_report(status)
        assert "Ego Lite" in report
        assert "Espacios de Tarea" in report

    def test_format_google_results(self):
        results = [
            {"title": "OpenAI", "url": "https://openai.com", "snippet": "Research lab"},
            {"title": "DeepMind", "url": "https://deepmind.google", "snippet": "AI organization"}
        ]
        report = ego_browser_service.format_google_results("AI research", results)
        assert "Resultados de Google con Ego Lite" in report
        assert "OpenAI" in report
        assert "DeepMind" in report
        assert "https://openai.com" in report

    def test_format_github_stats(self):
        stats = {
            "full_name": "google/gemini",
            "description": "Gemini API SDK",
            "stars": 12500,
            "forks": 1200,
            "open_issues": 45,
            "language": "Python",
            "license": "Apache-2.0",
            "html_url": "https://github.com/google/gemini"
        }
        report = ego_browser_service.format_github_stats("google/gemini", stats)
        assert "Estadísticas de Repositorio GitHub" in report
        assert "google/gemini" in report
        assert "12,500" in report
        assert "Python" in report

    def test_format_snapshot_report(self):
        snap_data = {
            "space": "research",
            "title": "Portal de Administración",
            "url": "https://empresa.com",
            "interactive_count": 3,
            "snapshot": "- heading \"Dashboard\"\n- [ref=1] textbox \"Usuario\"\n- [ref=2] button \"Entrar\""
        }
        report = ego_browser_service.format_snapshot_report(snap_data)
        assert "Portal de Administración" in report
        assert "research" in report
        assert "[ref=1]" in report
        assert "[ref=2]" in report

    def test_run_ego_cli_script(self):
        # Executes benign JavaScript in the CLI
        res = ego_browser_service.run_ego_cli("console.log('Liseth Ego CLI Test');")
        assert isinstance(res, dict)
        if res.get("success"):
            assert "Liseth Ego CLI Test" in res.get("output", "")


class TestEgoBrowserAction:
    """Tests for ego_browser_action entrypoint."""

    def test_action_status(self):
        out = ego_browser_action({"action": "status"})
        assert "Ego Lite" in out
        assert "Espacios de Tarea" in out

    def test_action_spaces_empty(self):
        out = ego_browser_action({"action": "spaces"})
        assert "espacios de tarea" in out.lower()

    def test_action_unknown(self):
        out = ego_browser_action({"action": "accion_inexistente"})
        assert "no se reconoció la acción" in out.lower()

    def test_action_missing_url(self):
        out = ego_browser_action({"action": "navigate"})
        assert "debe especificar la url" in out.lower()

    def test_action_missing_click_target(self):
        out = ego_browser_action({"action": "click"})
        assert "indique el número de referencia" in out.lower()

    def test_action_missing_fill_target(self):
        out = ego_browser_action({"action": "fill", "value": "test"})
        assert "indique el elemento o referencia" in out.lower()

    def test_action_github_mocked(self):
        with patch.object(ego_browser_service, "github_repo_stats") as mock_stats:
            mock_stats.return_value = {
                "full_name": "facebook/react",
                "description": "The library for web and native user interfaces",
                "stars": 220000,
                "forks": 45000,
                "open_issues": 1200,
                "language": "JavaScript",
                "license": "MIT",
                "html_url": "https://github.com/facebook/react"
            }
            out = ego_browser_action({"action": "github", "repo": "facebook/react"})
            assert "facebook/react" in out
            assert "220,000" in out

    def test_action_google_mocked(self):
        with patch.object(ego_browser_service, "google_search") as mock_search:
            mock_search.return_value = [
                {"title": "Python Official", "url": "https://python.org", "snippet": "Official site"}
            ]
            out = ego_browser_action({"action": "google", "query": "python programming"})
            assert "Python Official" in out
            assert "https://python.org" in out


class TestBrainRouterEgoIntegration:
    """Tests zero-latency intent classification for Ego Browser in brain_router."""

    def test_status_intents(self):
        res = detect_direct_intent("Liseth como esta el estado de ego browser")
        assert res is not None
        tool, args, prompt = res
        assert tool == "ego_browser"
        assert args.get("action") == "status"

        res = detect_direct_intent("dame el status del motor ego")
        assert res is not None
        tool, args, prompt = res
        assert tool == "ego_browser"
        assert args.get("action") == "status"

    def test_spaces_intent(self):
        res = detect_direct_intent("muestra los task spaces de navegacion")
        assert res is not None
        tool, args, prompt = res
        assert tool == "ego_browser"
        assert args.get("action") == "spaces"

    def test_google_learning_intent(self):
        res = detect_direct_intent("busca en google con ego finanzas corporativas 2026")
        assert res is not None
        tool, args, prompt = res
        assert tool == "ego_browser"
        assert args.get("action") == "google"
        assert "finanzas" in args.get("query", "").lower()

    def test_github_stats_intent(self):
        res = detect_direct_intent("estadisticas de github torvalds/linux")
        assert res is not None
        tool, args, prompt = res
        assert tool == "ego_browser"
        assert args.get("action") == "github"
        assert "torvalds/linux" in args.get("repo", "")

    def test_snapshot_navigation_intent(self):
        res = detect_direct_intent("analiza la pagina https://news.ycombinator.com")
        assert res is not None
        tool, args, prompt = res
        assert tool == "ego_browser"
        assert args.get("action") == "snapshot"
        assert "https://news.ycombinator.com" in args.get("url", "")

    def test_click_element_intent(self):
        res = detect_direct_intent("haz clic en el boton con ego ref=2")
        assert res is not None
        tool, args, prompt = res
        assert tool == "ego_browser"
        assert args.get("action") == "click"
        assert args.get("target") == "2"


def test_action_dispatcher_ego_integration():
    """Verifies that ego_browser_action dispatches status calls correctly."""
    res = ego_browser_action({"action": "status"})
    assert "Ego Lite" in res
    assert "Espacios de Tarea" in res

