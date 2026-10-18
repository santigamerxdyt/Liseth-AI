"""
Tests for Phase 2: WorkspaceSentinel and Code Health Monitoring.
"""
import os
import tempfile
import pytest
from app.services.workspace_sentinel import WorkspaceSentinel
from app.actions.workspace_sentinel_action import workspace_sentinel_action


def test_sentinel_clean_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a valid Python file
        valid_py = os.path.join(tmpdir, "valid.py")
        with open(valid_py, "w", encoding="utf-8") as f:
            f.write("def saludo():\n    return 'Hola Santiago'\n")

        sentinel = WorkspaceSentinel(default_workspace=tmpdir)
        report = sentinel.scan_workspace(workspace_path=tmpdir, force=True)

        assert report.healthy is True
        assert len(report.issues) == 0
        assert report.files_scanned >= 1


def test_sentinel_detects_syntax_error():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create an invalid Python file with broken syntax
        broken_py = os.path.join(tmpdir, "broken.py")
        with open(broken_py, "w", encoding="utf-8") as f:
            f.write("def broken_syntax(\n    return 42\n")  # Unclosed paren

        sentinel = WorkspaceSentinel(default_workspace=tmpdir)
        report = sentinel.scan_workspace(workspace_path=tmpdir, force=True)

        assert report.healthy is False
        assert len(report.issues) == 1
        assert report.issues[0].issue_type == "syntax_error"
        assert "broken.py" in report.issues[0].file_path
        alert = report.format_alert()
        assert "Alerta de Centinela" in alert
        assert "broken.py" in alert


def test_sentinel_watch_and_unwatch():
    sentinel = WorkspaceSentinel()
    with tempfile.TemporaryDirectory() as tmpdir:
        ok = sentinel.watch_directory(tmpdir)
        assert ok is True
        assert tmpdir in sentinel.list_watched()

        ok_unwatch = sentinel.unwatch_directory(tmpdir)
        assert ok_unwatch is True
        assert tmpdir not in sentinel.list_watched()


def test_sentinel_action_wrapper():
    res = workspace_sentinel_action({"action": "status"})
    assert isinstance(res, str)
    assert len(res) > 0


def test_sentinel_direct_intents():
    from app.services.brain_router import detect_direct_intent

    cases = [
        ("estado del centinela", "workspace_sentinel", "action", "status"),
        ("como estan mis proyectos", "workspace_sentinel", "action", "status"),
        ("revisa mi codigo", "workspace_sentinel", "action", "status"),
        ("escanea mis proyectos", "workspace_sentinel", "action", "scan"),
        ("analiza el proyecto", "workspace_sentinel", "action", "scan"),
    ]

    for phrase, expected_tool, expected_key, expected_val in cases:
        intent = detect_direct_intent(phrase)
        assert intent is not None, f"Failed for '{phrase}'"
        tool_name, tool_args, _ = intent
        assert tool_name == expected_tool, f"Expected {expected_tool} for '{phrase}', got {tool_name}"
        assert tool_args.get(expected_key) == expected_val

