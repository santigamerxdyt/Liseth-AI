"""
Test suite for Administrator Privilege Management & Elevation in Liseth.
Verifies is_admin(), get_elevation_status(), and ensure_admin() handling.
"""
import sys
from unittest.mock import MagicMock, patch
import pytest
from app.core.admin import is_admin, ensure_admin, get_elevation_status


def test_is_admin_returns_bool():
    """is_admin must return a valid boolean without errors."""
    res = is_admin()
    assert isinstance(res, bool)


def test_get_elevation_status_structure():
    """get_elevation_status must provide telemetry dictionary."""
    status = get_elevation_status()
    assert isinstance(status, dict)
    assert "is_admin" in status
    assert "mode" in status
    assert "can_access_hardware" in status
    assert "can_manage_services" in status
    assert isinstance(status["is_admin"], bool)
    if status["is_admin"]:
        assert "ADMINISTRADOR" in status["mode"]
    else:
        assert "USUARIO ESTANDAR" in status["mode"]


def test_ensure_admin_when_already_admin():
    """If already admin, ensure_admin() returns True immediately without exiting."""
    with patch("app.core.admin.is_admin", return_value=True):
        assert ensure_admin(force=True) is True
        assert ensure_admin(force=False) is True


def test_ensure_admin_no_force():
    """If not admin and force is False, returns False without attempting elevation."""
    with patch("app.core.admin.is_admin", return_value=False):
        assert ensure_admin(force=False) is False


def test_ensure_admin_non_win32():
    """If not win32 and not root, ensure_admin returns False."""
    with patch("app.core.admin.is_admin", return_value=False), patch("sys.platform", "linux"):
        assert ensure_admin(force=True) is False


def test_ensure_admin_win32_elevation_declined():
    """If user declines Windows UAC prompt (hinstance <= 32), ensure_admin returns False."""
    mock_shell32 = MagicMock()
    mock_shell32.ShellExecuteW.return_value = 5  # Error/Cancel code

    with patch("app.core.admin.is_admin", return_value=False), \
         patch("sys.platform", "win32"), \
         patch.dict("sys.modules", {"ctypes": MagicMock(windll=MagicMock(shell32=mock_shell32))}):
        result = ensure_admin(force=True)
        assert result is False
        mock_shell32.ShellExecuteW.assert_called_once()
        args = mock_shell32.ShellExecuteW.call_args[0]
        assert args[1] == "runas"  # Elevation verb


def test_ensure_admin_win32_elevation_success_exits():
    """If user approves UAC (hinstance > 32), the unprivileged parent exits with sys.exit(0)."""
    mock_shell32 = MagicMock()
    mock_shell32.ShellExecuteW.return_value = 42  # Success code > 32

    with patch("app.core.admin.is_admin", return_value=False), \
         patch("sys.platform", "win32"), \
         patch.dict("sys.modules", {"ctypes": MagicMock(windll=MagicMock(shell32=mock_shell32))}), \
         pytest.raises(SystemExit) as exc_info:
        ensure_admin(force=True)

    assert exc_info.value.code == 0
