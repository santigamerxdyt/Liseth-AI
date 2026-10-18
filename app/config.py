"""
Configuration module for JARVIS / Liseth
Validates environment variables, enforces security baselines, and prevents startup with insecure defaults.
"""
import os
import secrets
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Insecure default values that MUST NOT be used in production
FORBIDDEN_PINS = {"1234", "0000", "1111", "123456", "admin", "password", ""}
FORBIDDEN_MASTER_KEYS = {
    "jarvis-secret-key-32-chars-change-me",
    "jarvis-liseth-default-secure-key-32b",
    "",
}


class SecurityConfigurationError(Exception):
    """Raised when critical security parameters are missing or set to insecure defaults."""
    pass


class Settings:
    def __init__(self):
        # Security: Local-Only Mode (Private to Santiago, external access blocked)
        self.LOCAL_ONLY: bool = os.getenv("LOCAL_ONLY", "true").lower() in ("true", "1", "yes")

        # Server settings
        self.PORT: int = int(os.getenv("PORT", "3000"))
        if self.LOCAL_ONLY:
            self.HOST: str = "127.0.0.1"
        else:
            self.HOST: str = os.getenv("HOST", "127.0.0.1")
        self.ENV: str = os.getenv("ENV", "development").lower()
        self.DESKTOP_MODE: bool = os.getenv("DESKTOP_MODE", "false").lower() in ("true", "1", "yes")

        # Directories
        self.DATA_DIR: Path = BASE_DIR / "data"
        self.UPLOADS_DIR: Path = BASE_DIR / "uploads"
        self.ARCHIVOS_CREADOS_DIR: Path = BASE_DIR / "archivos_creados"
        self.TOKENS_DIR: Path = BASE_DIR / "tokens"
        self.STATIC_DIR: Path = BASE_DIR / "app" / "static"

        # Ensure directories exist
        for directory in [self.DATA_DIR, self.UPLOADS_DIR, self.ARCHIVOS_CREADOS_DIR, self.TOKENS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

        # Database
        self.DATABASE_URL: str = os.getenv(
            "DATABASE_URL",
            f"sqlite+aiosqlite:///{self.DATA_DIR / 'jarvis.db'}"
        )

        # Security: Access PIN
        self.JARVIS_ACCESS_PIN: str = os.getenv("JARVIS_ACCESS_PIN", "").strip()

        # Security: Master Encryption Key
        self.MASTER_ENCRYPTION_KEY: str = os.getenv("MASTER_ENCRYPTION_KEY", "").strip()

        # Security: Session Secret
        session_secret = os.getenv("SESSION_SECRET", "").strip()
        if not session_secret:
            # Generate or persist a session secret
            secret_file = self.DATA_DIR / ".session_secret"
            if secret_file.exists():
                session_secret = secret_file.read_text(encoding="utf-8").strip()
            else:
                session_secret = secrets.token_hex(32)
                try:
                    secret_file.write_text(session_secret, encoding="utf-8")
                except Exception:
                    pass
        self.SESSION_SECRET: str = session_secret

        # CORS Allowed Origins
        allowed_env = os.getenv("ALLOWED_ORIGINS", "")
        origins: List[str] = [
            f"http://127.0.0.1:{self.PORT}",
            f"http://localhost:{self.PORT}",
            "http://127.0.0.1:3000",
            "http://localhost:3000",
            "http://127.0.0.1:3001",
            "http://localhost:3001",
            "http://127.0.0.1:3002",
            "http://localhost:3002",
            "http://127.0.0.1:8000",
            "http://localhost:8000",
            "http://127.0.0.1:8080",
            "http://localhost:8080",
            "null",
        ]
        # Preserve order and deduplicate
        dedup_origins: List[str] = []
        for orig in origins:
            if orig not in dedup_origins:
                dedup_origins.append(orig)
        origins = dedup_origins

        if not self.LOCAL_ONLY and self.HOST == "0.0.0.0":
            # Allow LAN access only if explicitly configured and NOT in local-only mode
            origins.append("*")
        elif not self.LOCAL_ONLY and allowed_env:
            for item in allowed_env.split(","):
                clean = item.strip()
                if clean and clean not in origins:
                    origins.append(clean)
        self.ALLOWED_ORIGINS: List[str] = origins

        # LLM Brains
        self.GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
        self.ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "").strip()
        self.GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        self.ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022").strip()
        # Auxiliary Brains (Failover Fallbacks)
        self.GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
        self.GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()
        self.OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
        self.OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip()
        self.OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2").strip()
        self.OLLAMA_ENABLED: bool = os.getenv("OLLAMA_ENABLED", "false").lower() in ("true", "1", "yes")

        # Token limits
        self.DAILY_TOKEN_LIMIT: int = int(os.getenv("DAILY_TOKEN_LIMIT", "100000"))
        self.ALERT_THRESHOLD_PCT: int = int(os.getenv("ALERT_THRESHOLD_PCT", "80"))

        # Google OAuth
        self.GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "").strip()
        self.GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
        self.GOOGLE_REDIRECT_URI: str = os.getenv(
            "GOOGLE_REDIRECT_URI",
            f"http://127.0.0.1:{self.PORT}/api/google/oauth2callback"
        ).strip()

        # Notifications
        self.META_WA_PHONE_NUMBER_ID: str = os.getenv("META_WA_PHONE_NUMBER_ID", "").strip()
        self.META_WA_ACCESS_TOKEN: str = os.getenv("META_WA_ACCESS_TOKEN", "").strip()
        self.META_WA_VERIFY_TOKEN: str = os.getenv("META_WA_VERIFY_TOKEN", "").strip()
        self.META_WA_RECIPIENT_PHONE: str = os.getenv("META_WA_RECIPIENT_PHONE", "").strip()

        self.TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        self.TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "").strip()

        # Voice APIs (Optional external providers)
        self.ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "").strip()
        self.ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "").strip()
        self.ELEVENLABS_MODEL_ID: str = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2").strip()
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()

    def validate_security(self, strict: bool = True):
        """
        Validates security credentials to prevent booting with known default/insecure values.
        """
        errors = []

        # Check PIN
        if not self.JARVIS_ACCESS_PIN or self.JARVIS_ACCESS_PIN in FORBIDDEN_PINS:
            errors.append(
                f"JARVIS_ACCESS_PIN es inseguro o utiliza el valor por defecto ('{self.JARVIS_ACCESS_PIN or 'VACÍO'}'). "
                f"Por favor define un PIN seguro en tu archivo .env (diferente de 1234, 0000, etc.)."
            )

        # Check MASTER_ENCRYPTION_KEY
        if not self.MASTER_ENCRYPTION_KEY or self.MASTER_ENCRYPTION_KEY in FORBIDDEN_MASTER_KEYS:
            errors.append(
                "MASTER_ENCRYPTION_KEY es inseguro o utiliza el valor por defecto del ejemplo. "
                "Por favor define una clave de al menos 32 caracteres seguros en tu archivo .env."
            )

        if errors and strict:
            raise SecurityConfigurationError("\n[!] ERROR CRÍTICO DE SEGURIDAD:\n" + "\n".join(f"- {e}" for e in errors))

        return len(errors) == 0


settings = Settings()
