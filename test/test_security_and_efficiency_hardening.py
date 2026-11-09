"""
Security and Efficiency Hardening Test Suite for Liseth (JARVIS).
Validates:
- HTTP Response Security Headers (nosniff, DENY, Referrer-Policy, X-XSS-Protection, Permissions-Policy, COOP)
- Command injection defenses in app actions and system connector
- OS system root directory write & deletion safeguards
- Rate-limiter memory bounds and cache pruning
- Timing attack defenses and .env identifier sanitization in credentials router
"""
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.actions.open_app import _launch_windows
from app.connectors.system_connector import SystemConnector
from app.core.auth import check_rate_limit, record_failed_attempt, _failed_attempts, _lockouts, _prune_ip_cache, MAX_TRACKED_IPS
from app.routers.credentials_router import update_env_file


def test_http_security_headers_enforced():
    """Verifies that all incoming requests return strict security headers."""
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    headers = resp.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert "camera=()" in headers.get("Permissions-Policy", "")
    assert headers.get("Cross-Origin-Opener-Policy") == "same-origin-allow-popups"


def test_open_app_injection_safeguards():
    """Verifies that command injection characters in app_name are immediately rejected."""
    injection_payloads = [
        'calc.exe & echo "pwned"',
        'notepad.exe | whoami',
        'spotify; calc.exe',
        'chrome.exe `dir`',
        'calc.exe $(whoami)',
        'notepad.exe\ncalc.exe',
    ]
    for payload in injection_payloads:
        res = _launch_windows(payload)
        assert res is False, f"Payload should have been rejected: {payload}"


@pytest.mark.asyncio
async def test_system_connector_injection_safeguards():
    """Verifies that SystemConnector rejects injection characters in app_name and args."""
    connector = SystemConnector()
    with pytest.raises(ValueError, match="no permitidos"):
        await connector._exec_open_app({"app_name": "calc.exe; dir"})

    with pytest.raises(ValueError, match="no permitidos"):
        await connector._exec_open_app({"app_name": "calc.exe", "args": ["arg1", "arg2 & whoami"]})


@pytest.mark.asyncio
async def test_system_connector_protected_system_dir_safeguards():
    """Verifies that critical system directories are blocked from deletion and arbitrary writes."""
    connector = SystemConnector()
    import os
    sys_root = os.environ.get("SystemRoot", r"C:\Windows")

    with pytest.raises(PermissionError, match="bloqueada por seguridad"):
        await connector._exec_delete_file({"path": sys_root})

    with pytest.raises(PermissionError, match="bloqueada por seguridad"):
        await connector._exec_write_file({"path": f"{sys_root}\\system32\\malicious.dll", "content": "test"})


def test_auth_rate_limiter_memory_pruning():
    """Verifies that the auth rate limiter bounds memory usage by pruning stale IPs."""
    # Simulate high volume of unique IPs
    for i in range(MAX_TRACKED_IPS + 50):
        fake_ip = f"10.0.{i // 256}.{i % 256}"
        _failed_attempts[fake_ip] = [1000.0]  # Old timestamps
    
    # Prune
    _prune_ip_cache(now=20000.0)
    assert len(_failed_attempts) <= MAX_TRACKED_IPS


def test_credentials_env_key_sanitization():
    """Verifies that only valid uppercase identifiers are written to .env and injections are rejected."""
    import tempfile
    from app.routers import credentials_router
    original_env = credentials_router.ENV_PATH
    with tempfile.TemporaryDirectory() as td:
        try:
            test_env_file = Path(td) / ".env"
            test_env_file.write_text("EXISTING_KEY=old_value\n", encoding="utf-8")
            credentials_router.ENV_PATH = test_env_file

            updates = {
                "VALID_KEY_123": "secret_val",
                "INVALID-KEY!": "bad_val",
                "INJECT\nKEY": "injected_val",
                "SAFE_MULTILINE": "line1\nline2",
            }
            update_env_file(updates)

            content = test_env_file.read_text(encoding="utf-8")
            assert "VALID_KEY_123=secret_val" in content
            assert "INVALID-KEY!" not in content
            assert "INJECT\nKEY" not in content
            assert "\nline2" not in content  # Newlines in value sanitized
        finally:
            credentials_router.ENV_PATH = original_env


def test_sensitive_log_redaction_filter():
    """Verifies that SensitiveLogRedactionFilter redacts Telegram bot tokens and API keys in logs."""
    from app.main import SensitiveLogRedactionFilter

    raw_tg = 'HTTP Request: GET https://api.telegram.org/bot8820455447:AAF432kpgvJugbwzYTW7emzMCi2RspJj2WY/getUpdates?offset=0 "HTTP/1.1 200 OK"'
    redacted_tg = SensitiveLogRedactionFilter.sanitize_text(raw_tg)
    assert "AAF432kpgvJugbwzYTW7emzMCi2RspJj2WY" not in redacted_tg
    assert "[REDACTED_BOT_TOKEN]" in redacted_tg

    raw_gemini = "GET https://generativelanguage.googleapis.com/v1beta/models?key=AIzaSySecretKey123456789"
    redacted_gemini = SensitiveLogRedactionFilter.sanitize_text(raw_gemini)
    assert "AIzaSySecretKey123456789" not in redacted_gemini
    assert "key=[REDACTED]" in redacted_gemini


def test_credentials_unauthenticated_masking_and_test_guard():
    """Verifies unauthenticated callers cannot see secret prefixes/suffixes or probe stored keys."""
    client = TestClient(app)
    resp = client.get("/api/credentials?reveal=true")
    assert resp.status_code == 200
    data = resp.json()
    assert data["authenticated"] is False
    for cat in data["categories"].values():
        for item in cat.get("items", []):
            st = item.get("status", {})
            if "masked" in st and st.get("is_set"):
                assert st.get("value") == "••••••••"
                assert st.get("masked") == "••••••••"

    # Unauthenticated probing of stored server credentials must be blocked with 401
    probe = client.post("/api/credentials/test", json={"provider": "gemini"})
    assert probe.status_code == 401


def test_file_upload_size_limit_and_executable_extension_block():
    """Verifies upload constraints reject dangerous extensions (.exe, .bat) and oversized payloads (>25MB)."""
    from fastapi import HTTPException
    from app.routers.files_router import validate_upload_constraints, MAX_UPLOAD_SIZE_BYTES

    with pytest.raises(HTTPException) as exc_ext:
        validate_upload_constraints("malware.exe", 1024)
    assert exc_ext.value.status_code == 400

    with pytest.raises(HTTPException) as exc_size:
        validate_upload_constraints("large_video.mp4", MAX_UPLOAD_SIZE_BYTES + 1)
    assert exc_size.value.status_code == 413


def test_no_duplicate_static_dom_ids_in_html():
    """Verifies index.html has zero duplicate static HTML element IDs."""
    import re
    from collections import Counter
    from app.config import BASE_DIR

    html = (BASE_DIR / "index.html").read_text(encoding="utf-8")
    html_no_script = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    ids = re.findall(r'\bid=["\']([^"\']+)["\']', html_no_script)
    dup_ids = [(k, v) for k, v in Counter(ids).items() if v > 1 and "${" not in k]
    assert dup_ids == [], f"Duplicate static HTML IDs found: {dup_ids}"

