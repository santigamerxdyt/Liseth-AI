# -*- coding: utf-8 -*-
"""
Centralized Credentials & Authenticators Router for JARVIS / Liseth.
Provides secure endpoints to view status, update, test, and synchronize
all API keys, tokens, OAuth configurations, and security authenticators.
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.config import BASE_DIR, ENV_PATH, settings
from app.core.auth import is_authenticated

logger = logging.getLogger("jarvis.credentials_router")

router = APIRouter(prefix="/api/credentials", tags=["credentials"])

# Mask helper
def mask_secret(val: Optional[str]) -> str:
    """Masks secret keys while revealing enough prefix/suffix for identification."""
    if not val:
        return ""
    val = val.strip()
    if len(val) <= 8:
        return "••••••••"
    return f"{val[:4]}••••••••{val[-4:]}"


def update_env_file(updates: Dict[str, str]) -> None:
    """
    Safely updates or appends environment variables to .env on disk.
    Preserves existing structure and comments.
    """
    env_file = Path(ENV_PATH)
    lines = []
    if env_file.exists():
        lines = env_file.read_text(encoding="utf-8").splitlines()

    updated_keys = set()
    new_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in line:
            key, _ = line.split("=", 1)
            key = key.strip()
            if key in updates:
                new_lines.append(f"{key}={updates[key]}")
                updated_keys.add(key)
                continue
        new_lines.append(line)

    # Append any keys that weren't present in .env
    for key, val in updates.items():
        if key not in updated_keys and val is not None:
            new_lines.append(f"{key}={val}")

    temp_file = env_file.with_suffix(".tmp")
    temp_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    temp_file.replace(env_file)

    # Synchronize in-memory settings & os.environ
    for k, v in updates.items():
        if v is not None:
            os.environ[k] = str(v)
            if hasattr(settings, k):
                # Type cast if boolean or int
                orig_val = getattr(settings, k)
                if isinstance(orig_val, bool):
                    setattr(settings, k, str(v).lower() in ("true", "1", "yes"))
                elif isinstance(orig_val, int):
                    try:
                        setattr(settings, k, int(v))
                    except ValueError:
                        pass
                else:
                    setattr(settings, k, str(v))


class CredentialsUpdateRequest(BaseModel):
    credentials: Dict[str, Any] = Field(..., description="Map of environment key to secret or config value")


class CredentialTestRequest(BaseModel):
    provider: str = Field(..., description="gemini | claude | groq | openai | telegram | github | elevenlabs | weather | spotify")
    key: Optional[str] = Field(None, description="API Key or token to test")
    extra: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional parameters (e.g. chat_id, model)")


@router.get("")
def get_credentials(request: Request, reveal: bool = False):
    """
    Returns the comprehensive inventory of all configurable APIs and authenticators.
    Secrets are masked by default. If 'reveal=true' is requested, user must be authenticated.
    """
    user_auth = is_authenticated(request)
    allow_full = reveal and user_auth

    def format_val(key_name: str, current_val: str) -> Dict[str, Any]:
        val = (current_val or os.getenv(key_name, "")).strip()
        return {
            "key": key_name,
            "is_set": bool(val),
            "masked": mask_secret(val),
            "value": val if allow_full else (mask_secret(val) if val else "")
        }

    inventory = {
        "ok": True,
        "authenticated": user_auth,
        "categories": {
            "llm": {
                "title": "🧠 Inteligencia Artificial y Modelos LLM (Cerebros)",
                "description": "Configuración de modelos generativos, claves de API y cascada de respaldo autónoma.",
                "items": [
                    {
                        "id": "GEMINI_API_KEY",
                        "label": "Google Gemini API Key (Cerebro Primario)",
                        "description": "Clave de Google AI Studio para Gemini 3.8 / 3.5 Flash / Pro (multimodal, razonamiento y voz).",
                        "doc_url": "https://aistudio.google.com/app/apikey",
                        "status": format_val("GEMINI_API_KEY", settings.GEMINI_API_KEY),
                        "model_key": "GEMINI_MODEL",
                        "model_val": settings.GEMINI_MODEL,
                        "model_options": ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.1-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"]
                    },
                    {
                        "id": "ANTHROPIC_API_KEY",
                        "label": "Anthropic Claude API Key (Cerebro de Respaldo)",
                        "description": "Clave para Claude 3.5 Sonnet / Haiku (análisis de código, redacción y razonamiento profundo).",
                        "doc_url": "https://console.anthropic.com/settings/keys",
                        "status": format_val("ANTHROPIC_API_KEY", settings.ANTHROPIC_API_KEY),
                        "model_key": "ANTHROPIC_MODEL",
                        "model_val": settings.ANTHROPIC_MODEL,
                        "model_options": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"]
                    },
                    {
                        "id": "GROQ_API_KEY",
                        "label": "Groq Cloud API Key (LLaMA Ultra-Rápido)",
                        "description": "Inferencia de velocidad extrema (500+ tok/s) con LLaMA 3.3 70B para fallover instantáneo.",
                        "doc_url": "https://console.groq.com/keys",
                        "status": format_val("GROQ_API_KEY", settings.GROQ_API_KEY),
                        "model_key": "GROQ_MODEL",
                        "model_val": settings.GROQ_MODEL,
                        "model_options": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "llama-3.1-8b-instant"]
                    },
                    {
                        "id": "OPENAI_API_KEY",
                        "label": "OpenAI API Key (GPT-4o)",
                        "description": "Modelos de OpenAI para razonamiento y compatibilidad con herramientas universales.",
                        "doc_url": "https://platform.openai.com/api-keys",
                        "status": format_val("OPENAI_API_KEY", settings.OPENAI_API_KEY),
                        "model_key": "OPENAI_MODEL",
                        "model_val": settings.OPENAI_MODEL,
                        "model_options": ["gpt-4o-mini", "gpt-4o", "o1-mini"]
                    },
                    {
                        "id": "OLLAMA_ENABLED",
                        "label": "Ollama (Modelos Locales 100% Offline en Windows)",
                        "description": "Permite ejecutar IA en su propio computador sin internet mediante Ollama.",
                        "doc_url": "https://ollama.com",
                        "is_toggle": True,
                        "status": {
                            "key": "OLLAMA_ENABLED",
                            "is_set": settings.OLLAMA_ENABLED,
                            "value": settings.OLLAMA_ENABLED
                        },
                        "base_url_key": "OLLAMA_BASE_URL",
                        "base_url_val": settings.OLLAMA_BASE_URL,
                        "model_key": "OLLAMA_MODEL",
                        "model_val": settings.OLLAMA_MODEL
                    },
                    {
                        "id": "OPENROUTER_API_KEY",
                        "label": "OpenRouter API Key (Opcional)",
                        "description": "Pasarela universal para acceder a cientos de modelos abiertos y propietarios.",
                        "doc_url": "https://openrouter.ai/keys",
                        "status": format_val("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", ""))
                    }
                ]
            },
            "voice": {
                "title": "🎙️ Motores de Voz y Síntesis Neuronal (TTS)",
                "description": "Voces humanas, entonación, modulación y detección de palabra de activación (wake-word).",
                "items": [
                    {
                        "id": "ELEVENLABS_API_KEY",
                        "label": "ElevenLabs API Key (Voz Hiperrealista)",
                        "description": "Síntesis de voz con expresividad humana de calidad cinematográfica.",
                        "doc_url": "https://elevenlabs.io",
                        "status": format_val("ELEVENLABS_API_KEY", settings.ELEVENLABS_API_KEY),
                        "voice_id_key": "ELEVENLABS_VOICE_ID",
                        "voice_id_val": settings.ELEVENLABS_VOICE_ID or "21m00Tcm4TlvDq8ikWAM"
                    },
                    {
                        "id": "PORCUPINE_ACCESS_KEY",
                        "label": "Picovoice Porcupine Access Key (Wake-Word)",
                        "description": "Detección local ultraligera de la palabra de activación 'Liseth' / 'Jarvis' sin consumo de CPU.",
                        "doc_url": "https://console.picovoice.ai",
                        "status": format_val("PORCUPINE_ACCESS_KEY", os.getenv("PORCUPINE_ACCESS_KEY", ""))
                    },
                    {
                        "id": "AZURE_SPEECH_KEY",
                        "label": "Azure Cognitive Services Speech Key (Opcional)",
                        "description": "Motor de reconocimiento de voz y TTS en la nube de Microsoft Azure.",
                        "doc_url": "https://portal.azure.com",
                        "status": format_val("AZURE_SPEECH_KEY", os.getenv("AZURE_SPEECH_KEY", "")),
                        "region_key": "AZURE_SPEECH_REGION",
                        "region_val": os.getenv("AZURE_SPEECH_REGION", "eastus")
                    }
                ]
            },
            "google": {
                "title": "🌐 Google Workspace & OAuth 2.0 (Gmail, Calendar, Drive)",
                "description": "Conexión autorizada con su ecosistema de Google para leer correos, agendar citas y gestionar archivos.",
                "items": [
                    {
                        "id": "GOOGLE_CLIENT_ID",
                        "label": "Google Client ID (OAuth 2.0)",
                        "description": "Identificador de aplicación obtenido en Google Cloud Console.",
                        "doc_url": "https://console.cloud.google.com/apis/credentials",
                        "status": format_val("GOOGLE_CLIENT_ID", settings.GOOGLE_CLIENT_ID)
                    },
                    {
                        "id": "GOOGLE_CLIENT_SECRET",
                        "label": "Google Client Secret (OAuth 2.0)",
                        "description": "Clave secreta del cliente OAuth de Google Workspace.",
                        "doc_url": "https://console.cloud.google.com/apis/credentials",
                        "status": format_val("GOOGLE_CLIENT_SECRET", settings.GOOGLE_CLIENT_SECRET)
                    },
                    {
                        "id": "GOOGLE_REDIRECT_URI",
                        "label": "URI de Redirección OAuth",
                        "description": "URL de retorno para el flujo OAuth de Google.",
                        "status": {
                            "key": "GOOGLE_REDIRECT_URI",
                            "is_set": True,
                            "value": settings.GOOGLE_REDIRECT_URI
                        }
                    }
                ]
            },
            "messaging": {
                "title": "📱 Notificaciones y Mensajería Externa (Telegram & WhatsApp)",
                "description": "Envío de recordatorios automáticos matutinos, cierres de jornada y alertas al celular.",
                "items": [
                    {
                        "id": "TELEGRAM_BOT_TOKEN",
                        "label": "Telegram Bot Token",
                        "description": "Token de autenticación generado por @BotFather en Telegram (100% gratuito e ilimitado).",
                        "doc_url": "https://t.me/BotFather",
                        "status": format_val("TELEGRAM_BOT_TOKEN", settings.TELEGRAM_BOT_TOKEN)
                    },
                    {
                        "id": "TELEGRAM_CHAT_ID",
                        "label": "Telegram Chat ID de Santiago",
                        "description": "ID numérico de su chat personal de Telegram (obtenible mediante @userinfobot).",
                        "doc_url": "https://t.me/userinfobot",
                        "status": format_val("TELEGRAM_CHAT_ID", settings.TELEGRAM_CHAT_ID)
                    },
                    {
                        "id": "META_WA_ACCESS_TOKEN",
                        "label": "WhatsApp Business Cloud Access Token (Meta)",
                        "description": "Token permanente de Meta Developers para la API oficial de WhatsApp Cloud.",
                        "doc_url": "https://developers.facebook.com",
                        "status": format_val("META_WA_ACCESS_TOKEN", settings.META_WA_ACCESS_TOKEN)
                    },
                    {
                        "id": "META_WA_PHONE_NUMBER_ID",
                        "label": "WhatsApp Phone Number ID (Meta)",
                        "description": "Identificador numérico del número de teléfono asignado en Meta Developers.",
                        "status": format_val("META_WA_PHONE_NUMBER_ID", settings.META_WA_PHONE_NUMBER_ID)
                    },
                    {
                        "id": "META_WA_RECIPIENT_PHONE",
                        "label": "Teléfono de Destino (Celular de Santiago)",
                        "description": "Número con prefijo internacional para recibir las notificaciones (ej: +57310xxxxxxx).",
                        "status": format_val("META_WA_RECIPIENT_PHONE", settings.META_WA_RECIPIENT_PHONE)
                    }
                ]
            },
            "search_academic": {
                "title": "🔍 Búsqueda Web, Academia e Investigación Científica",
                "description": "Conexión a buscadores en vivo y bases de datos académicas internacionales.",
                "items": [
                    {
                        "id": "SERPAPI_API_KEY",
                        "label": "SerpAPI API Key (Búsqueda Web en Vivo)",
                        "description": "Búsquedas en Google en tiempo real con extracción estructurada de resultados.",
                        "doc_url": "https://serpapi.com",
                        "status": format_val("SERPAPI_API_KEY", os.getenv("SERPAPI_API_KEY", ""))
                    },
                    {
                        "id": "OPENALEX_EMAIL",
                        "label": "Correo Polite Pool para OpenAlex (Investigación Científica)",
                        "description": "Proporcionar su correo electrónico activa el pool prioritario de OpenAlex para 100,000 req/día gratuitas.",
                        "doc_url": "https://openalex.org",
                        "status": format_val("OPENALEX_EMAIL", os.getenv("OPENALEX_EMAIL", "santiago@unal.edu.co"))
                    },
                    {
                        "id": "GOOGLE_SEARCH_API_KEY",
                        "label": "Google Custom Search JSON API Key",
                        "description": "Clave de API para el motor de búsqueda programable de Google.",
                        "status": format_val("GOOGLE_SEARCH_API_KEY", os.getenv("GOOGLE_SEARCH_API_KEY", "")),
                        "cse_key": "GOOGLE_CSE_ID",
                        "cse_val": os.getenv("GOOGLE_CSE_ID", "")
                    }
                ]
            },
            "git_cloud": {
                "title": "🚀 Respaldo Git, GitHub y Despliegue Vercel",
                "description": "Sincronización automática de código, ramas y despliegue a producción.",
                "items": [
                    {
                        "id": "GITHUB_TOKEN",
                        "label": "GitHub Personal Access Token (PAT)",
                        "description": "Token con permisos de 'repo' y 'workflow' para respaldar cambios y actualizar GitHub Pages automáticamente.",
                        "doc_url": "https://github.com/settings/tokens",
                        "status": format_val("GITHUB_TOKEN", os.getenv("GITHUB_TOKEN", ""))
                    },
                    {
                        "id": "VERCEL_TOKEN",
                        "label": "Vercel Access Token (Despliegue Rápido)",
                        "description": "Token para publicar proyectos frontend instantáneamente con vercel-deploy.",
                        "doc_url": "https://vercel.com/account/tokens",
                        "status": format_val("VERCEL_TOKEN", os.getenv("VERCEL_TOKEN", ""))
                    }
                ]
            },
            "security": {
                "title": "🛡️ Seguridad del Sistema y Autenticadores Locales",
                "description": "Credenciales maestras de blindaje y cifrado de datos de Santiago.",
                "items": [
                    {
                        "id": "JARVIS_ACCESS_PIN",
                        "label": "PIN de Acceso Personal de Santiago",
                        "description": "PIN numérico secreto para desbloquear la sesión de Liseth y autorizar acciones de alto impacto.",
                        "status": format_val("JARVIS_ACCESS_PIN", settings.JARVIS_ACCESS_PIN)
                    },
                    {
                        "id": "MASTER_ENCRYPTION_KEY",
                        "label": "Clave Maestra de Cifrado AES-256",
                        "description": "Clave criptográfica de 32+ caracteres empleada para proteger credenciales en la base de datos.",
                        "status": format_val("MASTER_ENCRYPTION_KEY", settings.MASTER_ENCRYPTION_KEY)
                    },
                    {
                        "id": "DAILY_TOKEN_LIMIT",
                        "label": "Límite Preventivo Diario de Tokens",
                        "description": "Tope máximo diario de consumo para evitar sobrecostos accidentales en APIs externas.",
                        "status": {
                            "key": "DAILY_TOKEN_LIMIT",
                            "is_set": True,
                            "value": settings.DAILY_TOKEN_LIMIT
                        }
                    }
                ]
            }
        }
    }
    return inventory


@router.post("")
async def update_credentials(req: CredentialsUpdateRequest, request: Request):
    """
    Saves and persists credential updates to .env and runtime system configuration.
    Requires authenticated session or valid access PIN.
    """
    if not is_authenticated(request):
        # Allow initial setup if PIN is provided in payload
        payload_pin = req.credentials.get("JARVIS_ACCESS_PIN")
        if not payload_pin or payload_pin != settings.JARVIS_ACCESS_PIN:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Se requiere autorización o PIN válido para guardar credenciales en el servidor."
            )

    updates = {}
    for key, val in req.credentials.items():
        if val is not None and not str(val).startswith("••••••••"):
            updates[key] = str(val).strip()

    if updates:
        try:
            update_env_file(updates)
            logger.info(f"[CREDENTIALS] Actualizadas {len(updates)} variables de entorno en .env")

            # Update brain router if model or key updated
            if any(k in updates for k in ["GEMINI_API_KEY", "ANTHROPIC_API_KEY", "GROQ_API_KEY", "OPENAI_API_KEY", "GEMINI_MODEL"]):
                from app.services.brain_router import brain_router
                if "GEMINI_MODEL" in updates:
                    brain_router.active_gemini_model = updates["GEMINI_MODEL"]

            return {
                "ok": True,
                "message": f"Se han guardado y sincronizado {len(updates)} credenciales con éxito en su servidor.",
                "updated_keys": list(updates.keys())
            }
        except Exception as e:
            logger.error(f"[CREDENTIALS_ERR] Error escribiendo .env: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error guardando archivo de credenciales: {str(e)}")

    return {"ok": True, "message": "No se realizaron modificaciones.", "updated_keys": []}


@router.post("/test")
async def test_credential(req: CredentialTestRequest):
    """
    Executes a fast test ping to verify whether an API key or service token is valid.
    """
    provider = req.provider.lower().strip()
    key = (req.key or "").strip()

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # 1. Google Gemini
            if provider == "gemini":
                api_key = key or settings.GEMINI_API_KEY
                if not api_key:
                    return {"ok": False, "error": "No se suministró una API Key de Google Gemini."}
                url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                resp = await client.get(url)
                if resp.status_code == 200:
                    return {"ok": True, "message": "✓ Conexión exitosa con Google Gemini API (modelos disponibles)."}
                return {"ok": False, "error": f"Error {resp.status_code}: {resp.text[:120]}"}

            # 2. Groq
            elif provider == "groq":
                api_key = key or settings.GROQ_API_KEY
                if not api_key:
                    return {"ok": False, "error": "No se suministró una API Key de Groq."}
                url = "https://api.groq.com/openai/v1/models"
                resp = await client.get(url, headers={"Authorization": f"Bearer {api_key}"})
                if resp.status_code == 200:
                    return {"ok": True, "message": "✓ Conexión exitosa con Groq Cloud (inferencia ultra-rápida lista)."}
                return {"ok": False, "error": f"Error {resp.status_code}: {resp.text[:120]}"}

            # 3. OpenAI
            elif provider == "openai":
                api_key = key or settings.OPENAI_API_KEY
                if not api_key:
                    return {"ok": False, "error": "No se suministró una API Key de OpenAI."}
                url = "https://api.openai.com/v1/models"
                resp = await client.get(url, headers={"Authorization": f"Bearer {api_key}"})
                if resp.status_code == 200:
                    return {"ok": True, "message": "✓ Conexión exitosa con OpenAI API."}
                return {"ok": False, "error": f"Error {resp.status_code}: {resp.text[:120]}"}

            # 4. Telegram
            elif provider == "telegram":
                token = key or settings.TELEGRAM_BOT_TOKEN
                if not token:
                    return {"ok": False, "error": "No se suministró un Token de Bot de Telegram."}
                url = f"https://api.telegram.org/bot{token}/getMe"
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    bot_name = data.get("result", {}).get("username", "Bot")
                    return {"ok": True, "message": f"✓ Bot de Telegram activo: @{bot_name}"}
                return {"ok": False, "error": f"Error {resp.status_code}: {resp.text[:120]}"}

            # 5. GitHub
            elif provider == "github":
                token = key or os.getenv("GITHUB_TOKEN", "")
                if not token:
                    return {"ok": False, "error": "No se suministró un Token de GitHub."}
                url = "https://api.github.com/user"
                resp = await client.get(url, headers={"Authorization": f"Bearer {token}", "User-Agent": "Liseth-AI"})
                if resp.status_code == 200:
                    user_data = resp.json()
                    login = user_data.get("login", "Usuario")
                    return {"ok": True, "message": f"✓ Autenticado exitosamente en GitHub como @{login}."}
                return {"ok": False, "error": f"Error {resp.status_code}: {resp.text[:120]}"}

            # 6. ElevenLabs
            elif provider == "elevenlabs":
                api_key = key or settings.ELEVENLABS_API_KEY
                if not api_key:
                    return {"ok": False, "error": "No se suministró una API Key de ElevenLabs."}
                url = "https://api.elevenlabs.io/v1/voices"
                resp = await client.get(url, headers={"xi-api-key": api_key})
                if resp.status_code == 200:
                    return {"ok": True, "message": "✓ Conexión exitosa con ElevenLabs (voces neuronales disponibles)."}
                return {"ok": False, "error": f"Error {resp.status_code}: {resp.text[:120]}"}

            # 7. Claude (Anthropic)
            elif provider == "claude" or provider == "anthropic":
                api_key = key or settings.ANTHROPIC_API_KEY
                if not api_key:
                    return {"ok": False, "error": "No se suministró una API Key de Anthropic Claude."}
                url = "https://api.anthropic.com/v1/models"
                resp = await client.get(url, headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"})
                if resp.status_code == 200:
                    return {"ok": True, "message": "✓ Conexión exitosa con Anthropic Claude API."}
                return {"ok": False, "error": f"Error {resp.status_code}: {resp.text[:120]}"}

            else:
                return {"ok": False, "error": f"Proveedor '{provider}' no cuenta con prueba automática."}

        except Exception as ex:
            logger.warning(f"[CREDENTIALS_TEST_ERR] Error probando {provider}: {ex}")
            return {"ok": False, "error": f"Fallo al conectar con {provider}: {str(ex)}"}
