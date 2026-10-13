"""
Unit tests for path traversal prevention and file sanitization.
"""
from pathlib import Path
import pytest
from fastapi import HTTPException
from app.config import settings
from app.routers.files_router import sanitize_filename, verify_path_safe


def test_sanitize_filename():
    assert sanitize_filename("normal.pdf") == "normal.pdf"
    assert sanitize_filename("../../../etc/passwd") == "passwd"
    assert sanitize_filename("..\\..\\windows\\system32\\cmd.exe") == "cmd.exe"
    assert sanitize_filename("archivo con espacios (1).png") == "archivo_con_espacios__1_.png"


def test_verify_path_safe_valid():
    safe_path = settings.UPLOADS_DIR / "documento.pdf"
    resolved = verify_path_safe(safe_path, settings.UPLOADS_DIR)
    assert resolved == safe_path.resolve()


def test_verify_path_safe_traversal_blocked():
    malicious_path = settings.UPLOADS_DIR / ".." / ".." / "windows" / "system.ini"
    with pytest.raises(HTTPException) as exc_info:
        verify_path_safe(malicious_path, settings.UPLOADS_DIR)
    assert exc_info.value.status_code == 400
    assert "Path Traversal" in exc_info.value.detail
