"""
JARVIS / Liseth - FastAPI Application Entrypoint.
Provides secure API endpoints, authentication middleware, CORS protection, and static file serving.
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.core.auth import is_authenticated
from app.core.database import engine, init_db
from app.core.migrator import run_migration_if_needed
from app.routers.auth_router import router as auth_router
from app.routers.files_router import router as files_router
from app.routers.brain_router import router as brain_router
from app.routers.system_router import router as system_router
from app.routers.audit_router import router as audit_router
from app.routers.tts_router import router as tts_router
from app.routers.google_router import router as google_router
from app.routers.scheduler_router import router as scheduler_router
from app.routers.notifications_router import router as notifications_router

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("jarvis.server")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown routines."""
    logger.info("Iniciando JARVIS / Liseth...")

    # 1. Check security configuration
    try:
        settings.validate_security(strict=False)
    except Exception as e:
        logger.warning(f"Aviso de seguridad en configuración: {e}")

    # 2. Initialize database & migrate legacy JSON if needed
    try:
        migration_stats = await run_migration_if_needed()
        logger.info(f"Base de datos SQLite inicializada. Migración: {migration_stats}")
    except Exception as e:
        logger.error(f"Error inicializando base de datos / migración: {e}", exc_info=True)

    yield

    # Shutdown
    logger.info("Cerrando conexiones de base de datos...")
    await engine.dispose()
    try:
        from app.services.brain_router import brain_router
        await brain_router.close()
    except Exception:
        pass
    logger.info("JARVIS / Liseth detenido correctamente.")


app = FastAPI(
    title="Liseth - AI Personal Assistant",
    description="Sistema de asistencia personal con doble cerebro (Gemini/Claude) y herramientas avanzadas.",
    version="2.0.0",
    lifespan=lifespan,
)

# Configure CORS restricted to own origin and configured origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)


# Security: Whitelist of local loopback client addresses
LOCAL_IPS = {"127.0.0.1", "::1", "localhost", "testclient"}


@app.middleware("http")
async def local_only_guard_middleware(request: Request, call_next):
    """
    Enforces strict local machine access. Rejects any connection from external LAN or remote IPs.
    """
    if settings.LOCAL_ONLY:
        client_host = request.client.host if request.client else None
        if client_host and client_host not in LOCAL_IPS:
            logger.warning(f"Acceso externo no autorizado bloqueado desde IP: {client_host}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "ok": False,
                    "error": "Acceso restringido: Liseth opera exclusivamente en modo local privado para Santiago. Conexiones externas bloqueadas.",
                },
            )
    return await call_next(request)


# Security Authentication Middleware for /api/* routes
# Only auth discovery and liveness checks are exempt; all operational endpoints require valid PIN session
EXEMPT_API_PATHS = {
    "/api/status",
    "/api/auth/login",
    "/api/auth/status",
    "/api/auth/logout",
    "/api/health",
    "/health",
}


@app.middleware("http")
async def api_auth_middleware(request: Request, call_next):
    """
    Protects all /api/* routes by verifying authentication sessions.
    Returns 401 JSON if unauthorized.
    """
    path = request.url.path

    # Check if request targets an API route that is not exempt
    if path.startswith("/api") and path not in EXEMPT_API_PATHS:
        # Preflight OPTIONS requests are handled by CORS middleware
        if request.method != "OPTIONS":
            if not is_authenticated(request):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "ok": False,
                        "authRequired": True,
                        "error": "Acceso restringido. Por favor ingrese su PIN de acceso personal (Santiago).",
                    },
                )

    # Add security headers to response
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# Include Routers
app.include_router(system_router)
app.include_router(audit_router)
app.include_router(auth_router)
app.include_router(files_router)
app.include_router(brain_router)
app.include_router(tts_router)
app.include_router(google_router)
app.include_router(scheduler_router)
app.include_router(notifications_router)


# Mount Static Files
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")


@app.get("/health", tags=["system"])
@app.get("/api/health", tags=["system"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "online",
        "system": "JARVIS / Liseth",
        "version": "2.0.0",
        "database": "sqlite",
    }


@app.get("/", tags=["frontend"])
async def serve_index():
    """Serves the main Liseth frontend HTML with fresh cache headers."""
    index_file = settings.STATIC_DIR / "index.html"
    if not index_file.exists():
        return JSONResponse(
            status_code=500,
            content={"error": "Frontend static file index.html not found"}
        )
    response = FileResponse(index_file)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
