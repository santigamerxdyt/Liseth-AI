"""
Authentication and Session Management for JARVIS / Liseth.
Features:
- Scrypt PIN hashing and constant-time verification.
- HMAC-signed session tokens with expiration.
- Brute-force rate limiting per IP address.
- HttpOnly cookie and Bearer token support.
- FastAPI dependency for route protection.
"""
import base64
import hashlib
import hmac
import json
import logging
import time
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from fastapi import Cookie, Depends, HTTPException, Header, Request, Response, status
from app.config import settings
from app.core.crypto import hash_pin, verify_pin

logger = logging.getLogger("jarvis.auth")

# Rate limiter in-memory storage: ip -> list of failed attempt timestamps
_failed_attempts: Dict[str, List[float]] = defaultdict(list)
_lockouts: Dict[str, float] = {}

MAX_ATTEMPTS = 5
LOCKOUT_WINDOW_SECONDS = 300  # 5 minutes
SESSION_EXPIRATION_SECONDS = 86400 * 7  # 7 days
MAX_TRACKED_IPS = 1000  # Cap rate-limiter in-memory storage to prevent unbounded growth


def _prune_ip_cache(now: float) -> None:
    if len(_failed_attempts) > MAX_TRACKED_IPS:
        stale_ips = [
            ip for ip, times in _failed_attempts.items()
            if not times or (now - max(times) >= LOCKOUT_WINDOW_SECONDS)
        ]
        for ip in stale_ips:
            _failed_attempts.pop(ip, None)
            _lockouts.pop(ip, None)


def _get_client_ip(request: Request) -> str:
    """Extracts client IP address safely from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    client = request.client
    return client.host if client else "127.0.0.1"


def check_rate_limit(ip: str) -> Tuple[bool, int]:
    """
    Checks if an IP is currently locked out.
    Returns: (is_blocked, remaining_seconds)
    """
    now = time.time()
    _prune_ip_cache(now)
    lockout_expiry = _lockouts.get(ip, 0)
    if now < lockout_expiry:
        return True, int(lockout_expiry - now)

    # Clean old attempts outside the window
    _failed_attempts[ip] = [t for t in _failed_attempts[ip] if now - t < LOCKOUT_WINDOW_SECONDS]
    if len(_failed_attempts[ip]) >= MAX_ATTEMPTS:
        _lockouts[ip] = now + LOCKOUT_WINDOW_SECONDS
        return True, LOCKOUT_WINDOW_SECONDS

    return False, 0


def record_failed_attempt(ip: str):
    """Records a failed login attempt for an IP."""
    now = time.time()
    _failed_attempts[ip].append(now)
    if len(_failed_attempts[ip]) >= MAX_ATTEMPTS:
        _lockouts[ip] = now + LOCKOUT_WINDOW_SECONDS


def reset_failed_attempts(ip: str):
    """Resets failed attempts after a successful login."""
    _failed_attempts.pop(ip, None)
    _lockouts.pop(ip, None)


# --- Cryptographic Session Tokens ---

def sign_session_token(session_id: str, client_ip: str) -> str:
    """
    Creates an HMAC-SHA256 signed session token.
    Token structure: base64(payload).signature_hex
    """
    now = int(time.time())
    payload = {
        "sid": session_id,
        "ip": client_ip,
        "iat": now,
        "exp": now + SESSION_EXPIRATION_SECONDS,
    }
    raw_json = json.dumps(payload, separators=(",", ":"))
    payload_b64 = base64.urlsafe_b64encode(raw_json.encode("utf-8")).decode("utf-8").rstrip("=")

    signature = hmac.new(
        settings.SESSION_SECRET.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return f"{payload_b64}.{signature}"


def verify_session_token(token: str) -> Optional[dict]:
    """
    Verifies an HMAC-SHA256 session token.
    Returns the payload dictionary if valid and not expired, else None.
    """
    if not token or "." not in token:
        return None

    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None

        payload_b64, signature = parts
        # Verify HMAC signature in constant time
        expected_sig = hmac.new(
            settings.SESSION_SECRET.encode("utf-8"),
            payload_b64.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_sig):
            return None

        # Decode payload
        padding = "=" * ((4 - len(payload_b64) % 4) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Verify expiration
        now = int(time.time())
        if payload.get("exp", 0) < now:
            return None

        return payload
    except Exception as e:
        logger.warning(f"Error verificando token de sesión: {e}")
        return None


# --- Authentication Checks & FastAPI Middleware / Dependencies ---

def extract_token_from_request(request: Request) -> Optional[str]:
    """
    Extracts session token from Cookie 'liseth_session' or Header 'Authorization: Bearer <token>'.
    """
    # 1. Check Cookie
    token = request.cookies.get("liseth_session")
    if token:
        return token

    # 2. Check Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:].strip()

    # 3. Check X-Session-Token header
    token = request.headers.get("X-Session-Token")
    if token:
        return token

    # 4. Check query parameter 'token' (vital for cross-origin <a download> and window.open)
    token = request.query_params.get("token")
    if token:
        return token

    return None


def is_authenticated(request: Request) -> bool:
    """Checks if request has a valid session token."""
    token = extract_token_from_request(request)
    if not token:
        return False
    payload = verify_session_token(token)
    return payload is not None


async def require_auth(request: Request) -> dict:
    """
    FastAPI dependency that enforces authentication.
    Raises HTTPException(401) if not authenticated.
    """
    token = extract_token_from_request(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida. Introduce tu PIN de acceso.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_session_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada o token inválido.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload
