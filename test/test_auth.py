"""
Unit tests for app.core.auth module.
"""
import time
import pytest
from app.core.auth import (
    check_rate_limit,
    record_failed_attempt,
    reset_failed_attempts,
    sign_session_token,
    verify_session_token,
    _lockouts,
    _failed_attempts,
)


def test_sign_and_verify_session_token():
    session_id = "test-session-123"
    client_ip = "127.0.0.1"

    token = sign_session_token(session_id, client_ip)
    assert "." in token

    payload = verify_session_token(token)
    assert payload is not None
    assert payload["sid"] == session_id
    assert payload["ip"] == client_ip
    assert payload["exp"] > time.time()


def test_tampered_session_token():
    session_id = "test-session-123"
    client_ip = "127.0.0.1"
    token = sign_session_token(session_id, client_ip)
    parts = token.split(".")

    # Tamper payload
    tampered_token = f"dGVzdA.{parts[1]}"
    assert verify_session_token(tampered_token) is None

    # Tamper signature
    tampered_sig = f"{parts[0]}.0000000000000000"
    assert verify_session_token(tampered_sig) is None


def test_rate_limiter_brute_force_protection():
    test_ip = "192.168.1.99"
    reset_failed_attempts(test_ip)

    # 4 attempts should not lock out
    for _ in range(4):
        record_failed_attempt(test_ip)
        blocked, _ = check_rate_limit(test_ip)
        assert blocked is False

    # 5th attempt locks out
    record_failed_attempt(test_ip)
    blocked, remaining = check_rate_limit(test_ip)
    assert blocked is True
    assert remaining > 0

    # Reset clears lockout
    reset_failed_attempts(test_ip)
    blocked, _ = check_rate_limit(test_ip)
    assert blocked is False
