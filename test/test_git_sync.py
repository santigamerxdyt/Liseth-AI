"""
Automated Test Suite for Git Auto-Sync & GitHub Cloud Synchronization.
Verifies repository tracking, git status checks, action dispatcher routing,
and zero-latency intent detection for Señor Santiago.
"""

import pytest
from app.services.git_sync_service import GitSyncService, git_sync_service
from app.actions.git_sync_action import git_sync_action
from app.services.action_dispatcher import action_dispatcher
from app.services.brain_router import detect_direct_intent


class TestGitSyncService:
    """Primitives and telemetry tests for GitSyncService."""

    def test_status_structure(self):
        st = git_sync_service.get_status()
        assert isinstance(st, dict)
        assert "branch" in st
        assert st["branch"] in ["main", "master", "feature/python-migration"]
        assert "remote_url" in st
        assert "Liseth-AI" in st["remote_url"]
        assert "clean" in st
        assert isinstance(st["clean"], bool)

    def test_watcher_lifecycle(self):
        assert not git_sync_service._stop_watcher_event.is_set()
        git_sync_service.start_background_watcher(interval_seconds=3600)
        st = git_sync_service.get_status()
        assert st["auto_sync_active"] is True

        git_sync_service.stop_background_watcher()
        st2 = git_sync_service.get_status()
        assert st2["auto_sync_active"] is False

    def test_format_report_clean(self):
        mock_res = {
            "success": True,
            "action": "none_needed",
            "branch": "main",
            "last_commit": "abc1234 - update"
        }
        report = git_sync_service.format_report(mock_res)
        assert "completamente actualizado" in report
        assert "https://github.com/santigamerxdyt/Liseth-AI" in report

    def test_format_report_synced(self):
        mock_res = {
            "success": True,
            "action": "synced",
            "files_changed": 3,
            "commit_hash": "a1b2c3d",
            "commit_message": "sync: test commit",
            "timestamp": "2026-10-18 17:50:00"
        }
        report = git_sync_service.format_report(mock_res)
        assert "Sincronización con GitHub completada" in report
        assert "a1b2c3d" in report
        assert "https://santigamerxdyt.github.io/Liseth-AI/" in report


class TestGitSyncAction:
    """Action wrapper tests for git_sync_action."""

    def test_action_status(self):
        out = git_sync_action({"action": "status"})
        assert "Estado de Sincronización con GitHub" in out
        assert "Liseth-AI" in out
        assert "https://santigamerxdyt.github.io/Liseth-AI/" in out

    def test_action_watcher_toggle(self):
        out_start = git_sync_action({"action": "start_watcher"})
        assert "activado el centinela" in out_start
        out_stop = git_sync_action({"action": "stop_watcher"})
        assert "detenido el centinela" in out_stop


class TestBrainRouterGitSyncIntegration:
    """Tests zero-latency intent classification in brain_router."""

    def test_sync_intent(self):
        res = detect_direct_intent("Liseth sincroniza con github")
        assert res is not None
        tool, args, prompt = res
        assert tool == "git_sync"
        assert args.get("action") == "sync"

    def test_push_intent(self):
        res = detect_direct_intent("sube los cambios a github")
        assert res is not None
        tool, args, prompt = res
        assert tool == "git_sync"
        assert args.get("action") == "sync"

    def test_status_intent(self):
        res = detect_direct_intent("Liseth como esta el estado de git")
        assert res is not None
        tool, args, prompt = res
        assert tool == "git_sync"
        assert args.get("action") == "status"

    def test_start_watcher_intent(self):
        res = detect_direct_intent("activa el centinela de github")
        assert res is not None
        tool, args, prompt = res
        assert tool == "git_sync"
        assert args.get("action") == "start_watcher"

    def test_stop_watcher_intent(self):
        res = detect_direct_intent("deten el centinela de github")
        assert res is not None
        tool, args, prompt = res
        assert tool == "git_sync"
        assert args.get("action") == "stop_watcher"


@pytest.mark.asyncio
async def test_action_dispatcher_git_sync_integration():
    """Verifies action_dispatcher dispatches git_sync calls."""
    res = await action_dispatcher.execute_tool("git_sync", {"action": "status"})
    assert "Estado de Sincronización con GitHub" in res
