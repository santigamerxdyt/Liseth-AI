"""
Authentication endpoints for JARVIS / Liseth.
Handles PIN verification, rate limiting, session cookies, and logout.
"""
import hmac
import json
import uuid
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from app.config import settings
from app.core.auth import (
    _get_client_ip,
    check_rate_limit,
    extract_token_from_request,
    is_authenticated,
    record_failed_attempt,
    reset_failed_attempts,
    revoke_session_token,
    sign_session_token,
    verify_session_token,
    SESSION_EXPIRATION_SECONDS,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    pin: str = Field(..., min_length=1, max_length=64, description="PIN de acceso")
    launch_code: Optional[str] = Field(None, description="Código de verificación de inicio para confirmar identidad")


class VerifyLaunchCodeRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=64, description="Código de verificación de inicio")


@router.post("/login")
async def login(req: LoginRequest, request: Request, response: Response):
    """
    Validates user PIN with brute-force rate limiting.
    Issues an HMAC-signed session cookie and bearer token.
    """
    client_ip = _get_client_ip(request)

    # 1. Check rate limit
    is_blocked, remaining = check_rate_limit(client_ip)
    if is_blocked:
        return Response(
            content=json.dumps({"ok": False, "error": f"Demasiados intentos fallidos. Bloqueado por seguridad ({remaining}s)."}),
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            media_type="application/json"
        )

    # 2. Verify PIN using constant-time comparison
    expected_pin = settings.JARVIS_ACCESS_PIN.strip()
    provided_pin = req.pin.strip()

    if not expected_pin:
        return Response(
            content=json.dumps({"ok": False, "error": "No hay un PIN configurado en el servidor."}),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            media_type="application/json"
        )

    is_valid = hmac.compare_digest(provided_pin.encode("utf-8"), expected_pin.encode("utf-8"))

    if not is_valid:
        record_failed_attempt(client_ip)
        return Response(
            content=json.dumps({"ok": False, "error": "PIN de acceso incorrecto."}),
            status_code=status.HTTP_401_UNAUTHORIZED,
            media_type="application/json"
        )

    # 3. Success: Reset rate limiter & issue token
    reset_failed_attempts(client_ip)
    session_id = str(uuid.uuid4())
    token = sign_session_token(session_id, client_ip)

    # Set secure HttpOnly cookie
    response.set_cookie(
        key="liseth_session",
        value=token,
        max_age=SESSION_EXPIRATION_SECONDS,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )

    return {
        "ok": True,
        "success": True,
        "authenticated": True,
        "token": token,
        "message": "Autenticación exitosa. Bienvenido a Liseth.",
    }


@router.get("/status")
async def auth_status(request: Request):
    """
    Checks if current session or bearer token is authenticated.
    """
    authenticated = is_authenticated(request)
    return {
        "authenticated": authenticated
    }


@router.post("/verify-launch-code")
async def verify_launch_code_endpoint(req: VerifyLaunchCodeRequest, request: Request):
    """
    Verifies that the person launching the application or web interface has the
    legitimate identity verification code (Código de Verificación de Inicio).
    """
    client_ip = _get_client_ip(request)
    is_blocked, remaining = check_rate_limit(client_ip)
    if is_blocked:
        return Response(
            content=json.dumps({"ok": False, "error": f"Demasiados intentos fallidos. Bloqueado temporalmente ({remaining}s)."}),
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            media_type="application/json",
        )

    expected_pin = settings.JARVIS_ACCESS_PIN.strip()
    provided_code = req.code.strip()

    if not expected_pin:
        return Response(
            content=json.dumps({"ok": False, "error": "No hay un código de acceso configurado en el servidor."}),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            media_type="application/json",
        )

    is_valid = hmac.compare_digest(provided_code.encode("utf-8"), expected_pin.encode("utf-8"))
    if not is_valid:
        record_failed_attempt(client_ip)
        return Response(
            content=json.dumps({"ok": False, "valid": False, "error": "Código de verificación de inicio inválido. Se requiere el código para confirmar tu identidad."}),
            status_code=status.HTTP_401_UNAUTHORIZED,
            media_type="application/json",
        )

    reset_failed_attempts(client_ip)
    return {
        "ok": True,
        "valid": True,
        "message": "Código de verificación verificado correctamente. Identidad confirmada.",
    }


@router.post("/logout")
async def logout(request: Request, response: Response):
    """
    Revokes the active session token and clears the authentication session cookie.
    """
    token = extract_token_from_request(request)
    if token:
        revoke_session_token(token)
    response.delete_cookie(
        key="liseth_session",
        path="/",
    )
    return {
        "success": True,
        "authenticated": False,
        "message": "Sesión cerrada correctamente."
    }
