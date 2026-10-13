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


# Security Authentication Middleware for /api/* routes
EXEMPT_API_PATHS = {
    "/api/auth/login",
    "/api/auth/status",
    "/api/auth/logout",
    "/api/health",
    "/api/webhook/whatsapp",
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
                        "error": "Acceso restringido. Por favor ingrese su PIN de acceso.",
                    },
                )

    # Add security headers to response
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# Include Routers
app.include_router(auth_router)
app.include_router(files_router)


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
    """Serves the main Liseth frontend HTML."""
    index_file = settings.STATIC_DIR / "index.html"
    if not index_file.exists():
        return JSONResponse(
            status_code=500,
            content={"error": "Frontend static file index.html not found"}
        )
    return FileResponse(index_file)
