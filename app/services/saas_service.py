"""
SaaS Multi-User, Multi-Tenant, Subscription, Memory & Creator Superadmin Service for Liseth.
Implements:
- User Registration, Login, Password Recovery, Email Verification, Profile & Account Lifecycle
- 6-Tier Plan Hierarchy (FREE, STARTER, PRO, BUSINESS, ENTERPRISE, CREATOR) & Strict Server-Side RBAC
- Multi-Tenant Conversation Workspace with Strict User Isolation (user_id)
- Individual User Memory Brain (Personal + Contextual + Summaries + Semantic/Keyword Retrieval)
- Centralized AI Providers, Models, Skills & Specialized Agents Registry
- Monetization, Subscriptions, Invoices, Stripe Webhook Idempotency, Grace Periods & Refunds
- Credit & Token Quota Engine (80% Warning Alert, 100% Temporary Block, Billing Cycle Reset)
- Promo Codes, Welcome Coupons & Verified Referral Rewards Program
- Exclusive CREATOR Superadmin Analytics & Control Center (MRR, ARR, ARPU, API Costs, Audit Trail)
"""
import base64
import hashlib
import hmac
import json
import logging
import re
import secrets
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException, Request, status
from sqlalchemy import and_, delete, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.auth import extract_token_from_request, verify_session_token
from app.core.database import AsyncSessionLocal, init_db
from app.core.models import (
    SaasAgent,
    SaasAIModel,
    SaasAIProvider,
    SaasAuditLog,
    SaasConversation,
    SaasCreditBalance,
    SaasInvoice,
    SaasMessage,
    SaasPayment,
    SaasPlan,
    SaasPromoCode,
    SaasReferral,
    SaasSkill,
    SaasSubscription,
    SaasUsageRecord,
    SaasUser,
    SaasUserMemory,
)

logger = logging.getLogger("jarvis.saas")

CREATOR_USER_ID = "user_creator_santiago"
CREATOR_EMAIL = "santiago@liseth.ai"

PLAN_LEVELS: Dict[str, int] = {
    "FREE": 0,
    "STARTER": 1,
    "PRO": 2,
    "BUSINESS": 3,
    "ENTERPRISE": 4,
    "CREATOR": 5,
}

PUBLIC_PURCHASABLE_PLANS = {"STARTER", "PRO", "BUSINESS", "ENTERPRISE"}
PUBLIC_VISIBLE_PLANS = {"FREE", "STARTER", "PRO", "BUSINESS", "ENTERPRISE"}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


# ==============================================================================
# CRYPTOGRAPHIC PASSWORD HASHING & SAAS TOKEN SIGNING
# ==============================================================================

def hash_user_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Hashes a user password using PBKDF2-HMAC-SHA256 (200,000 iterations) with a unique salt."""
    if not salt:
        salt = secrets.token_hex(32)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200_000,
    )
    return derived.hex(), salt


def verify_user_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verifies a user password in constant time."""
    if not password or not stored_hash or not salt:
        return False
    computed_hash, _ = hash_user_password(password, salt)
    return hmac.compare_digest(computed_hash, stored_hash)


def sign_saas_token(
    user_id: str,
    email: str,
    role: str,
    plan_code: str,
    expires_in: int = 86400 * 7,
) -> str:
    """Creates an HMAC-SHA256 signed SaaS session token."""
    now = int(time.time())
    payload = {
        "type": "saas_user",
        "uid": user_id,
        "email": email,
        "role": role,
        "plan": plan_code,
        "iat": now,
        "exp": now + expires_in,
        "jti": secrets.token_hex(8),
    }
    raw_json = json.dumps(payload, separators=(",", ":"))
    payload_b64 = base64.urlsafe_b64encode(raw_json.encode("utf-8")).decode("utf-8").rstrip("=")
    signature = hmac.new(
        settings.SESSION_SECRET.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload_b64}.{signature}"


def verify_saas_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifies an HMAC-SHA256 signed SaaS token or legacy PIN session token."""
    payload = verify_session_token(token)
    if not payload:
        return None
    return payload


# ==============================================================================
# DEFAULT CATALOG DEFINITIONS (PLANS, PROVIDERS, MODELS, SKILLS, AGENTS, PROMOS)
# ==============================================================================

DEFAULT_PLANS: List[Dict[str, Any]] = [
    {
        "id": "plan_free",
        "code": "FREE",
        "level": 0,
        "name": "Plan Free",
        "description": "Uso básico del asistente con acceso inicial a cerebros, memoria personal limitada y skills esenciales.",
        "price_monthly_usd": 0.0,
        "price_annual_usd": 0.0,
        "is_public": True,
        "is_commercializable": False,
        "max_brains": 3,
        "max_conversations": 5,
        "daily_message_limit": 25,
        "monthly_token_limit": 100_000,
        "monthly_credits": 500,
        "max_memories": 20,
        "allowed_skill_tiers": ["basic"],
        "features": {
            "basic_assistant": True,
            "full_history": False,
            "persistent_memory": False,
            "agent_customization": False,
            "custom_agents": False,
            "automations": False,
            "advanced_automations": False,
            "enterprise_tools": False,
            "api_access": False,
            "priority_processing": False,
            "priority_support": False,
            "superadmin_access": False,
        },
        "priority_level": 1,
        "trial_days": 0,
    },
    {
        "id": "plan_starter",
        "code": "STARTER",
        "level": 1,
        "name": "Plan Level 1 — Starter",
        "description": "Ideal para profesionales independientes: 5 cerebros de IA, historial completo, memoria ampliada y skills intermedias.",
        "price_monthly_usd": 10.0,
        "price_annual_usd": 96.0,
        "is_public": True,
        "is_commercializable": True,
        "max_brains": 5,
        "max_conversations": 25,
        "daily_message_limit": 150,
        "monthly_token_limit": 750_000,
        "monthly_credits": 2_500,
        "max_memories": 100,
        "allowed_skill_tiers": ["basic", "intermediate"],
        "features": {
            "basic_assistant": True,
            "full_history": True,
            "persistent_memory": False,
            "agent_customization": False,
            "custom_agents": False,
            "automations": False,
            "advanced_automations": False,
            "enterprise_tools": False,
            "api_access": False,
            "priority_processing": False,
            "priority_support": False,
            "superadmin_access": False,
        },
        "priority_level": 2,
        "trial_days": 7,
    },
    {
        "id": "plan_pro",
        "code": "PRO",
        "level": 2,
        "name": "Plan Level 2 — Pro",
        "description": "Potencia avanzada: 15 cerebros de IA, skills avanzadas, memoria persistente, personalización de agentes y prioridad.",
        "price_monthly_usd": 30.0,
        "price_annual_usd": 288.0,
        "is_public": True,
        "is_commercializable": True,
        "max_brains": 15,
        "max_conversations": 100,
        "daily_message_limit": 500,
        "monthly_token_limit": 3_000_000,
        "monthly_credits": 10_000,
        "max_memories": 500,
        "allowed_skill_tiers": ["basic", "intermediate", "advanced"],
        "features": {
            "basic_assistant": True,
            "full_history": True,
            "persistent_memory": True,
            "agent_customization": True,
            "custom_agents": False,
            "automations": False,
            "advanced_automations": False,
            "enterprise_tools": False,
            "api_access": False,
            "priority_processing": True,
            "priority_support": False,
            "superadmin_access": False,
        },
        "priority_level": 3,
        "trial_days": 7,
    },
    {
        "id": "plan_business",
        "code": "BUSINESS",
        "level": 3,
        "name": "Plan Level 3 — Business",
        "description": "Para equipos y empresas en crecimiento: 30 cerebros, creación de agentes personalizados, automatizaciones y herramientas ejecutivas.",
        "price_monthly_usd": 75.0,
        "price_annual_usd": 720.0,
        "is_public": True,
        "is_commercializable": True,
        "max_brains": 30,
        "max_conversations": 500,
        "daily_message_limit": 2_000,
        "monthly_token_limit": 10_000_000,
        "monthly_credits": 30_000,
        "max_memories": 2_000,
        "allowed_skill_tiers": ["basic", "intermediate", "advanced", "business"],
        "features": {
            "basic_assistant": True,
            "full_history": True,
            "persistent_memory": True,
            "agent_customization": True,
            "custom_agents": True,
            "automations": True,
            "advanced_automations": False,
            "enterprise_tools": True,
            "api_access": False,
            "priority_processing": True,
            "priority_support": False,
            "superadmin_access": False,
        },
        "priority_level": 4,
        "trial_days": 14,
    },
    {
        "id": "plan_enterprise",
        "code": "ENTERPRISE",
        "level": 4,
        "name": "Plan Level 4 — Enterprise",
        "description": "Capacidad corporativa total: todos los cerebros públicos, agentes especializados, automatizaciones avanzadas, API y soporte prioritario.",
        "price_monthly_usd": 200.0,
        "price_annual_usd": 1920.0,
        "is_public": True,
        "is_commercializable": True,
        "max_brains": 999,
        "max_conversations": 5_000,
        "daily_message_limit": 10_000,
        "monthly_token_limit": 50_000_000,
        "monthly_credits": 100_000,
        "max_memories": 10_000,
        "allowed_skill_tiers": ["basic", "intermediate", "advanced", "business", "enterprise"],
        "features": {
            "basic_assistant": True,
            "full_history": True,
            "persistent_memory": True,
            "agent_customization": True,
            "custom_agents": True,
            "automations": True,
            "advanced_automations": True,
            "enterprise_tools": True,
            "api_access": True,
            "priority_processing": True,
            "priority_support": True,
            "superadmin_access": False,
        },
        "priority_level": 5,
        "trial_days": 14,
    },
    {
        "id": "plan_creator",
        "code": "CREATOR",
        "level": 5,
        "name": "Plan Level 5 — Creator (Exclusivo Propietario)",
        "description": "Exclusivo y no comercializable. Pertenece únicamente al creador original de la plataforma (Señor Santiago) con control absoluto del sistema.",
        "price_monthly_usd": 0.0,
        "price_annual_usd": 0.0,
        "is_public": False,
        "is_commercializable": False,
        "max_brains": 9_999,
        "max_conversations": 999_999,
        "daily_message_limit": 999_999,
        "monthly_token_limit": 999_999_999,
        "monthly_credits": 9_999_999,
        "max_memories": 999_999,
        "allowed_skill_tiers": ["basic", "intermediate", "advanced", "business", "enterprise", "creator"],
        "features": {
            "basic_assistant": True,
            "full_history": True,
            "persistent_memory": True,
            "agent_customization": True,
            "custom_agents": True,
            "automations": True,
            "advanced_automations": True,
            "enterprise_tools": True,
            "api_access": True,
            "priority_processing": True,
            "priority_support": True,
            "superadmin_access": True,
            "experimental_features": True,
            "skill_crud": True,
            "user_admin": True,
            "plan_admin": True,
            "revenue_control": True,
        },
        "priority_level": 6,
        "trial_days": 0,
    },
]

DEFAULT_PROVIDERS: List[Dict[str, Any]] = [
    {"id": "prov_google", "code": "google", "name": "Google Gemini AI", "status": "active", "api_key_env": "GEMINI_API_KEY", "priority": 1},
    {"id": "prov_anthropic", "code": "anthropic", "name": "Anthropic Claude", "status": "active", "api_key_env": "CLAUDE_API_KEY", "priority": 2},
    {"id": "prov_groq", "code": "groq", "name": "Groq LPU Ultra-Fast", "status": "active", "api_key_env": "GROQ_API_KEY", "priority": 3},
    {"id": "prov_openai", "code": "openai", "name": "OpenAI GPT / o-Series", "status": "active", "api_key_env": "OPENAI_API_KEY", "priority": 4},
    {"id": "prov_ollama", "code": "ollama", "name": "Ollama Local Neural Engine", "status": "active", "api_key_env": "OLLAMA_HOST", "priority": 5},
]

DEFAULT_MODELS: List[Dict[str, Any]] = [
    # Tier 0 - FREE (3 models available)
    {"id": "mdl_gemini_31_flash_lite", "provider_code": "google", "model_id": "gemini-3.1-flash-lite", "display_name": "Gemini 3.1 Flash Lite", "tier_required": 0, "compatible_plans": ["FREE", "STARTER", "PRO", "BUSINESS", "ENTERPRISE", "CREATOR"], "credit_cost_per_msg": 1, "cost_per_1k_input_usd": 0.000075, "cost_per_1k_output_usd": 0.0003, "is_default": True, "is_public": True},
    {"id": "mdl_gemini_25_flash_lite", "provider_code": "google", "model_id": "gemini-2.5-flash-lite", "display_name": "Gemini 2.5 Flash Lite", "tier_required": 0, "compatible_plans": ["FREE", "STARTER", "PRO", "BUSINESS", "ENTERPRISE", "CREATOR"], "credit_cost_per_msg": 1, "cost_per_1k_input_usd": 0.000075, "cost_per_1k_output_usd": 0.0003, "is_default": False, "is_public": True},
    {"id": "mdl_llama_31_8b_instant", "provider_code": "groq", "model_id": "llama-3.1-8b-instant", "display_name": "Llama 3.1 8B Instant (Groq)", "tier_required": 0, "compatible_plans": ["FREE", "STARTER", "PRO", "BUSINESS", "ENTERPRISE", "CREATOR"], "credit_cost_per_msg": 1, "cost_per_1k_input_usd": 0.00005, "cost_per_1k_output_usd": 0.00008, "is_default": False, "is_public": True},
    # Tier 1 - STARTER (5 models total)
    {"id": "mdl_gemini_25_flash", "provider_code": "google", "model_id": "gemini-2.5-flash", "display_name": "Gemini 2.5 Flash", "tier_required": 1, "compatible_plans": ["STARTER", "PRO", "BUSINESS", "ENTERPRISE", "CREATOR"], "credit_cost_per_msg": 2, "cost_per_1k_input_usd": 0.00015, "cost_per_1k_output_usd": 0.0006, "is_default": False, "is_public": True},
    {"id": "mdl_claude_35_haiku", "provider_code": "anthropic", "model_id": "claude-3-5-haiku-latest", "display_name": "Claude 3.5 Haiku", "tier_required": 1, "compatible_plans": ["STARTER", "PRO", "BUSINESS", "ENTERPRISE", "CREATOR"], "credit_cost_per_msg": 2, "cost_per_1k_input_usd": 0.0008, "cost_per_1k_output_usd": 0.004, "is_default": False, "is_public": True},
    # Tier 2 - PRO (up to 15 models)
    {"id": "mdl_gemini_25_pro", "provider_code": "google", "model_id": "gemini-2.5-pro", "display_name": "Gemini 2.5 Pro Reasoning", "tier_required": 2, "compatible_plans": ["PRO", "BUSINESS", "ENTERPRISE", "CREATOR"], "credit_cost_per_msg": 5, "cost_per_1k_input_usd": 0.00125, "cost_per_1k_output_usd": 0.005, "is_default": False, "is_public": True},
    {"id": "mdl_claude_sonnet_4", "provider_code": "anthropic", "model_id": "claude-sonnet-4-20250514", "display_name": "Claude Sonnet 4", "tier_required": 2, "compatible_plans": ["PRO", "BUSINESS", "ENTERPRISE", "CREATOR"], "credit_cost_per_msg": 6, "cost_per_1k_input_usd": 0.003, "cost_per_1k_output_usd": 0.015, "is_default": False, "is_public": True},
    {"id": "mdl_llama_33_70b", "provider_code": "groq", "model_id": "llama-3.3-70b-versatile", "display_name": "Llama 3.3 70B Versatile", "tier_required": 2, "compatible_plans": ["PRO", "BUSINESS", "ENTERPRISE", "CREATOR"], "credit_cost_per_msg": 3, "cost_per_1k_input_usd": 0.00059, "cost_per_1k_output_usd": 0.00079, "is_default": False, "is_public": True},
    {"id": "mdl_gpt_4o_mini", "provider_code": "openai", "model_id": "gpt-4o-mini", "display_name": "GPT-4o Mini", "tier_required": 2, "compatible_plans": ["PRO", "BUSINESS", "ENTERPRISE", "CREATOR"], "credit_cost_per_msg": 2, "cost_per_1k_input_usd": 0.00015, "cost_per_1k_output_usd": 0.0006, "is_default": False, "is_public": True},
    # Tier 3 - BUSINESS
    {"id": "mdl_gpt_4o", "provider_code": "openai", "model_id": "gpt-4o", "display_name": "GPT-4o Flagship", "tier_required": 3, "compatible_plans": ["BUSINESS", "ENTERPRISE", "CREATOR"], "credit_cost_per_msg": 8, "cost_per_1k_input_usd": 0.0025, "cost_per_1k_output_usd": 0.01, "is_default": False, "is_public": True},
    {"id": "mdl_claude_37_sonnet", "provider_code": "anthropic", "model_id": "claude-3-7-sonnet-latest", "display_name": "Claude 3.7 Sonnet Hybrid Thinking", "tier_required": 3, "compatible_plans": ["BUSINESS", "ENTERPRISE", "CREATOR"], "credit_cost_per_msg": 8, "cost_per_1k_input_usd": 0.003, "cost_per_1k_output_usd": 0.015, "is_default": False, "is_public": True},
    # Tier 4 - ENTERPRISE
    {"id": "mdl_claude_opus_4", "provider_code": "anthropic", "model_id": "claude-opus-4-20250514", "display_name": "Claude Opus 4 Enterprise", "tier_required": 4, "compatible_plans": ["ENTERPRISE", "CREATOR"], "credit_cost_per_msg": 15, "cost_per_1k_input_usd": 0.015, "cost_per_1k_output_usd": 0.075, "is_default": False, "is_public": True},
    # Tier 5 - CREATOR (Private / Experimental)
    {"id": "mdl_liseth_creator_sovereign", "provider_code": "google", "model_id": "liseth-sovereign-creator-v2", "display_name": "Liseth Sovereign Creator Core (Private)", "tier_required": 5, "compatible_plans": ["CREATOR"], "credit_cost_per_msg": 0, "cost_per_1k_input_usd": 0.0, "cost_per_1k_output_usd": 0.0, "is_default": False, "is_public": False},
]

DEFAULT_SKILLS: List[Dict[str, Any]] = [
    {
        "id": "sk_web_search",
        "code": "web_search_realtime",
        "name": "Búsqueda Web Verídica en Tiempo Real",
        "description": "Consulta fuentes verificadas de internet, noticias actuales y referencias con citas.",
        "category": "research",
        "tier": "basic",
        "min_plan_level": 0,
        "compatible_plans": ["FREE", "STARTER", "PRO", "BUSINESS", "ENTERPRISE", "CREATOR"],
        "estimated_credit_cost": 1,
        "estimated_api_cost_usd": 0.0002,
    },
    {
        "id": "sk_task_notes",
        "code": "task_and_notes_manager",
        "name": "Gestión de Tareas, Recordatorios y Notas",
        "description": "Organiza agenda, recordatorios inteligentes y notas rápidas del usuario.",
        "category": "productivity",
        "tier": "basic",
        "min_plan_level": 0,
        "compatible_plans": ["FREE", "STARTER", "PRO", "BUSINESS", "ENTERPRISE", "CREATOR"],
        "estimated_credit_cost": 1,
        "estimated_api_cost_usd": 0.0001,
    },
    {
        "id": "sk_academic_researcher",
        "code": "academic_researcher_apa7",
        "name": "Investigador Académico & Citas APA 7",
        "description": "Búsqueda de literatura científica (OpenAlex, arXiv), extracción de DOIs y síntesis académica.",
        "category": "research",
        "tier": "intermediate",
        "min_plan_level": 1,
        "compatible_plans": ["STARTER", "PRO", "BUSINESS", "ENTERPRISE", "CREATOR"],
        "estimated_credit_cost": 2,
        "estimated_api_cost_usd": 0.0005,
    },
    {
        "id": "sk_workspace_docs",
        "code": "workspace_document_generator",
        "name": "Generador de Documentos PDF, Excel y Presentaciones",
        "description": "Generación automatizada de reportes PDF profesionales, hojas de cálculo y presentaciones.",
        "category": "productivity",
        "tier": "intermediate",
        "min_plan_level": 1,
        "compatible_plans": ["STARTER", "PRO", "BUSINESS", "ENTERPRISE", "CREATOR"],
        "estimated_credit_cost": 2,
        "estimated_api_cost_usd": 0.0006,
    },
    {
        "id": "sk_data_ml_toolkit",
        "code": "data_science_ml_toolkit",
        "name": "Data Science, EDA & Machine Learning Toolkit",
        "description": "Limpieza de datos, análisis estadístico, regresiones, series de tiempo y clustering.",
        "category": "coding",
        "tier": "advanced",
        "min_plan_level": 2,
        "compatible_plans": ["PRO", "BUSINESS", "ENTERPRISE", "CREATOR"],
        "estimated_credit_cost": 4,
        "estimated_api_cost_usd": 0.0012,
    },
    {
        "id": "sk_voice_3d_avatar",
        "code": "voice_3d_holographic_avatar",
        "name": "Interacción Vocal Neural & Avatar 3D Holográfico",
        "description": "Síntesis de voz neural fluida, barge-in en tiempo real y sincronización labial 3D.",
        "category": "voice_3d",
        "tier": "advanced",
        "min_plan_level": 2,
        "compatible_plans": ["PRO", "BUSINESS", "ENTERPRISE", "CREATOR"],
        "estimated_credit_cost": 3,
        "estimated_api_cost_usd": 0.0010,
    },
    {
        "id": "sk_business_strategist",
        "code": "business_strategist_cfo",
        "name": "Estratega Empresarial & Modelado Financiero CFO",
        "description": "Matrices FODA/Porter/PESTEL/Ansoff, flujo de caja descontado (DCF), VPN/TIR, WACC y DuPont-Altman.",
        "category": "business",
        "tier": "business",
        "min_plan_level": 3,
        "compatible_plans": ["BUSINESS", "ENTERPRISE", "CREATOR"],
        "estimated_credit_cost": 5,
        "estimated_api_cost_usd": 0.0020,
    },
    {
        "id": "sk_workflow_automations",
        "code": "autonomous_workflow_automations",
        "name": "Automatizaciones y Flujos Programados",
        "description": "Ejecución programada de reportes, alertas financieras y flujos multi-etapa.",
        "category": "automation",
        "tier": "business",
        "min_plan_level": 3,
        "compatible_plans": ["BUSINESS", "ENTERPRISE", "CREATOR"],
        "estimated_credit_cost": 5,
        "estimated_api_cost_usd": 0.0018,
    },
    {
        "id": "sk_enterprise_compliance",
        "code": "enterprise_sagrilaft_tax_audit",
        "name": "Auditoría Corporativa, SAGRILAFT, DIAN & Riesgos",
        "description": "Cumplimiento normativo, simulación Monte Carlo, valoración corporativa y blindaje legal.",
        "category": "enterprise",
        "tier": "enterprise",
        "min_plan_level": 4,
        "compatible_plans": ["ENTERPRISE", "CREATOR"],
        "estimated_credit_cost": 8,
        "estimated_api_cost_usd": 0.0035,
    },
    {
        "id": "sk_creator_system_control",
        "code": "creator_sovereign_system_control",
        "name": "Control Soberano del Sistema & Hardware Local (Exclusivo Creator)",
        "description": "Control nativo del sistema operativo, terminal, procesos y configuración global del servidor.",
        "category": "system_creator",
        "tier": "creator",
        "min_plan_level": 5,
        "compatible_plans": ["CREATOR"],
        "estimated_credit_cost": 0,
        "estimated_api_cost_usd": 0.0,
    },
]

DEFAULT_AGENTS: List[Dict[str, Any]] = [
    {
        "id": "agt_liseth_core",
        "owner_user_id": None,
        "name": "Liseth Core Assistant",
        "role_title": "Asistente Ejecutiva & Polímata Universal",
        "description": "Agente principal con equilibrio entre velocidad, investigación verídica y productividad.",
        "system_prompt": "Eres Liseth, asistente ejecutiva inteligente, precisa, cálida y altamente resolutiva.",
        "preferred_brain": "gemini",
        "preferred_model": "gemini-3.1-flash-lite",
        "skill_codes": ["web_search_realtime", "task_and_notes_manager"],
        "min_plan_level": 0,
        "is_public": True,
        "avatar_icon": "✨",
    },
    {
        "id": "agt_academic_scholar",
        "owner_user_id": None,
        "name": "Dr. Atlas — Investigador Científico",
        "role_title": "Especialista en Literatura Científica y Tesis APA 7",
        "description": "Sintetiza papers arbitrados, verifica referencias y estructura marcos teóricos.",
        "system_prompt": "Actúa como investigador académico senior riguroso en metodología científica y normas APA 7.",
        "preferred_brain": "gemini",
        "preferred_model": "gemini-2.5-flash",
        "skill_codes": ["web_search_realtime", "academic_researcher_apa7", "workspace_document_generator"],
        "min_plan_level": 1,
        "is_public": True,
        "avatar_icon": "🎓",
    },
    {
        "id": "agt_cfo_strategist",
        "owner_user_id": None,
        "name": "Valeria CFO — Estrategia & Finanzas Corporativas",
        "role_title": "Directora Financiera y Estratega de Negocios",
        "description": "Domina valoración DCF, WACC, planeación tributaria, riesgos y simulaciones Monte Carlo.",
        "system_prompt": "Actúa como CFO y consultora estratégica McKinsey/BCG enfocada en rentabilidad y mitigación de riesgos.",
        "preferred_brain": "gemini",
        "preferred_model": "gemini-2.5-pro",
        "skill_codes": ["business_strategist_cfo", "data_science_ml_toolkit", "workspace_document_generator"],
        "min_plan_level": 2,
        "is_public": True,
        "avatar_icon": "📈",
    },
    {
        "id": "agt_enterprise_auditor",
        "owner_user_id": None,
        "name": "Sentinel — Auditor Corporativo & Compliance",
        "role_title": "Oficial de Cumplimiento, Ciberseguridad y LegalTech",
        "description": "Audita contratos, riesgos corporativos, SAGRILAFT y arquitecturas empresariales.",
        "system_prompt": "Actúa como oficial de cumplimiento corporativo, auditor forense y arquitecto de seguridad.",
        "preferred_brain": "claude",
        "preferred_model": "claude-sonnet-4-20250514",
        "skill_codes": ["enterprise_sagrilaft_tax_audit", "business_strategist_cfo", "autonomous_workflow_automations"],
        "min_plan_level": 4,
        "is_public": True,
        "avatar_icon": "🛡️",
    },
]

DEFAULT_PROMO_CODES: List[Dict[str, Any]] = [
    {
        "id": "promo_welcome20",
        "code": "WELCOME20",
        "description": "Cupón de bienvenida: 20% de descuento + 500 créditos extra",
        "discount_pct": 20.0,
        "bonus_credits": 500,
        "trial_days_bonus": 0,
        "applicable_plans": ["STARTER", "PRO", "BUSINESS", "ENTERPRISE"],
        "max_uses": 10_000,
        "is_welcome_coupon": True,
    },
    {
        "id": "promo_lisethpro",
        "code": "LISETHPRO",
        "description": "Promoción lanzamiento Pro & Business: 25% de descuento + 1,000 créditos",
        "discount_pct": 25.0,
        "bonus_credits": 1_000,
        "trial_days_bonus": 7,
        "applicable_plans": ["PRO", "BUSINESS", "ENTERPRISE"],
        "max_uses": 5_000,
        "is_welcome_coupon": False,
    },
    {
        "id": "promo_founder50",
        "code": "FOUNDER50",
        "description": "Descuento especial Early Adopter 50% en el primer ciclo",
        "discount_pct": 50.0,
        "bonus_credits": 2_000,
        "trial_days_bonus": 14,
        "applicable_plans": ["STARTER", "PRO", "BUSINESS"],
        "max_uses": 500,
        "is_welcome_coupon": False,
    },
]


# ==============================================================================
# SAAS PLATFORM SERVICE
# ==============================================================================

class SaasPlatformService:
    def __init__(self) -> None:
        self._seeded = False

    async def ensure_seeded(self, db: Optional[AsyncSession] = None) -> None:
        """Idempotently initializes tables and seeds plans, owner CREATOR account, models, skills, agents, and promo codes."""
        if self._seeded:
            return
        await init_db()
        own_session = False
        if db is None:
            session = AsyncSessionLocal()
            own_session = True
        else:
            session = db

        try:
            # 1. Seed Plans
            existing_plans_res = await session.execute(select(SaasPlan.code))
            existing_plan_codes = {r[0] for r in existing_plans_res.all()}
            for p_data in DEFAULT_PLANS:
                if p_data["code"] not in existing_plan_codes:
                    session.add(SaasPlan(**p_data))

            # 2. Seed Creator Account (Señor Santiago)
            creator_res = await session.execute(
                select(SaasUser).where(
                    or_(SaasUser.id == CREATOR_USER_ID, SaasUser.email == CREATOR_EMAIL)
                )
            )
            creator_user = creator_res.scalars().first()
            if not creator_user:
                pw_hash, pw_salt = hash_user_password(settings.JARVIS_ACCESS_PIN or "SantiagoCreator2026!")
                creator_user = SaasUser(
                    id=CREATOR_USER_ID,
                    email=CREATOR_EMAIL,
                    password_hash=pw_hash,
                    password_salt=pw_salt,
                    full_name="Señor Santiago Huérfano López",
                    nickname="Señor Santiago",
                    bio="Propietario y Creador Original de la Plataforma Liseth AI.",
                    role="CREATOR",
                    plan_code="CREATOR",
                    is_active=True,
                    is_suspended=False,
                    email_verified=True,
                    memory_enabled=True,
                    referral_code="SANTIAGO-CREATOR",
                    preferences={"theme": "cyber-hud", "language": "es", "voice_enabled": True},
                )
                session.add(creator_user)
            else:
                # Always enforce that the owner account keeps CREATOR role and plan
                creator_user.role = "CREATOR"
                creator_user.plan_code = "CREATOR"
                creator_user.is_active = True
                creator_user.is_suspended = False

            # Ensure Creator has subscription & credit balance
            sub_res = await session.execute(
                select(SaasSubscription).where(SaasSubscription.user_id == CREATOR_USER_ID)
            )
            if not sub_res.scalars().first():
                session.add(
                    SaasSubscription(
                        id="sub_creator_lifetime",
                        user_id=CREATOR_USER_ID,
                        plan_code="CREATOR",
                        billing_cycle="lifetime",
                        status="active",
                        price_usd=0.0,
                        auto_renew=True,
                        current_period_start=utcnow(),
                        current_period_end=utcnow() + timedelta(days=36500),
                        payment_method_summary="Sovereign Creator License (No comercializable)",
                    )
                )

            bal_res = await session.execute(
                select(SaasCreditBalance).where(SaasCreditBalance.user_id == CREATOR_USER_ID)
            )
            if not bal_res.scalars().first():
                session.add(
                    SaasCreditBalance(
                        user_id=CREATOR_USER_ID,
                        monthly_credits_allocated=9_999_999,
                        credits_used=0,
                        bonus_credits=999_999,
                        daily_messages_used=0,
                        monthly_messages_used=0,
                        monthly_tokens_used=0,
                        last_daily_reset=utcnow().strftime("%Y-%m-%d"),
                        period_reset_at=utcnow() + timedelta(days=36500),
                    )
                )

            # 3. Seed AI Providers
            prov_res = await session.execute(select(SaasAIProvider.code))
            existing_provs = {r[0] for r in prov_res.all()}
            for prov in DEFAULT_PROVIDERS:
                if prov["code"] not in existing_provs:
                    session.add(SaasAIProvider(**prov))

            # 4. Seed AI Models
            mdl_res = await session.execute(select(SaasAIModel.model_id))
            existing_mdls = {r[0] for r in mdl_res.all()}
            for mdl in DEFAULT_MODELS:
                if mdl["model_id"] not in existing_mdls:
                    session.add(SaasAIModel(**mdl))

            # 5. Seed Skills
            sk_res = await session.execute(select(SaasSkill.code))
            existing_sks = {r[0] for r in sk_res.all()}
            for sk in DEFAULT_SKILLS:
                if sk["code"] not in existing_sks:
                    session.add(SaasSkill(**sk))

            # 6. Seed Agents
            agt_res = await session.execute(select(SaasAgent.id))
            existing_agts = {r[0] for r in agt_res.all()}
            for agt in DEFAULT_AGENTS:
                if agt["id"] not in existing_agts:
                    session.add(SaasAgent(**agt))

            # 7. Seed Promo Codes
            pr_res = await session.execute(select(SaasPromoCode.code))
            existing_promos = {r[0] for r in pr_res.all()}
            for pr in DEFAULT_PROMO_CODES:
                if pr["code"] not in existing_promos:
                    session.add(SaasPromoCode(**pr))

            await session.commit()
            self._seeded = True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error seeding SaaS defaults: {e}", exc_info=True)
            raise
        finally:
            if own_session:
                await session.close()

    # ==========================================================================
    # AUDIT TRAIL HELPER
    # ==========================================================================

    async def log_audit(
        self,
        db: AsyncSession,
        action: str,
        actor_user: Optional[SaasUser] = None,
        target_user_id: Optional[str] = None,
        resource_type: str = "system",
        resource_id: Optional[str] = None,
        ip_address: str = "127.0.0.1",
        severity: str = "info",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        entry = SaasAuditLog(
            actor_user_id=actor_user.id if actor_user else None,
            actor_email=actor_user.email if actor_user else None,
            actor_role=actor_user.role if actor_user else None,
            target_user_id=target_user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            severity=severity,
            details=details or {},
        )
        db.add(entry)

    # ==========================================================================
    # AUTHENTICATION & USER RESOLUTION (SERVER-SIDE RBAC)
    # ==========================================================================

    def extract_saas_token(self, request: Request) -> Optional[str]:
        """Extracts SaaS token prioritizing explicit headers (X-SaaS-Token, Authorization Bearer) over cookies."""
        saas_header = request.headers.get("X-SaaS-Token")
        if saas_header:
            return saas_header.strip()

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:].strip()

        session_header = request.headers.get("X-Session-Token")
        if session_header:
            return session_header.strip()

        saas_cookie = request.cookies.get("liseth_saas_session")
        if saas_cookie:
            return saas_cookie.strip()

        return extract_token_from_request(request)

    async def get_current_user(self, request: Request, db: AsyncSession) -> SaasUser:
        """
        Resolves and validates the current authenticated SaaS user from DB.
        Never trusts client-side role or plan claims without DB verification.
        Bridges legacy PIN auth ('santiago_admin') directly to Señor Santiago's CREATOR account.
        """
        await self.ensure_seeded(db)
        token = self.extract_saas_token(request)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Autenticación requerida. Inicia sesión en tu cuenta de Liseth SaaS.",
            )

        payload = verify_saas_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesión expirada o token inválido.",
            )

        # Check if token is a SaaS user token or legacy PIN session for Señor Santiago
        if payload.get("type") == "saas_user" and payload.get("uid"):
            user_id = payload["uid"]
        elif payload.get("sid"):
            user_id = CREATOR_USER_ID
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de sesión no reconocido.",
            )

        res = await db.execute(select(SaasUser).where(SaasUser.id == user_id))
        user = res.scalars().first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="La cuenta de usuario no existe o ha sido eliminada.",
            )
        if user.is_suspended:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cuenta suspendida: {user.suspension_reason or 'Contacte a soporte.'}",
            )
        return user

    async def require_creator(self, request: Request, db: AsyncSession) -> SaasUser:
        """
        Strict server-side guard for the CREATOR Superadmin Panel.
        Blocks any user whose DB-verified role != 'CREATOR' or plan_code != 'CREATOR'.
        """
        user = await self.get_current_user(request, db)
        if user.role != "CREATOR" or user.plan_code != "CREATOR" or user.id != CREATOR_USER_ID:
            await self.log_audit(
                db=db,
                action="unauthorized_creator_access_attempt",
                actor_user=user,
                resource_type="creator_panel",
                severity="security",
                details={"attempted_path": str(request.url.path)},
            )
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado: Este panel y operación son exclusivos del propietario CREATOR (Señor Santiago).",
            )
        return user

    # ==========================================================================
    # PLAN & QUOTA ENFORCEMENT ENGINE
    # ==========================================================================

    async def get_plan(self, db: AsyncSession, plan_code: str) -> SaasPlan:
        await self.ensure_seeded(db)
        res = await db.execute(select(SaasPlan).where(SaasPlan.code == plan_code.upper()))
        plan = res.scalars().first()
        if not plan:
            res = await db.execute(select(SaasPlan).where(SaasPlan.code == "FREE"))
            plan = res.scalars().first()
        return plan

    async def get_or_create_credit_balance(self, db: AsyncSession, user: SaasUser) -> SaasCreditBalance:
        plan = await self.get_plan(db, user.plan_code)
        res = await db.execute(select(SaasCreditBalance).where(SaasCreditBalance.user_id == user.id))
        balance = res.scalars().first()
        today_str = utcnow().strftime("%Y-%m-%d")

        if not balance:
            balance = SaasCreditBalance(
                user_id=user.id,
                monthly_credits_allocated=plan.monthly_credits,
                credits_used=0,
                bonus_credits=0,
                daily_messages_used=0,
                monthly_messages_used=0,
                monthly_tokens_used=0,
                last_daily_reset=today_str,
                period_reset_at=utcnow() + timedelta(days=30),
            )
            db.add(balance)
            await db.flush()
            return balance

        # Daily reset check
        if balance.last_daily_reset != today_str:
            balance.daily_messages_used = 0
            balance.last_daily_reset = today_str

        # Monthly billing cycle reset check
        now_dt = utcnow()
        period_reset = balance.period_reset_at
        if period_reset and period_reset.tzinfo is None:
            period_reset = period_reset.replace(tzinfo=timezone.utc)
        if period_reset and now_dt >= period_reset:
            balance.monthly_credits_allocated = plan.monthly_credits
            balance.credits_used = 0
            balance.monthly_messages_used = 0
            balance.monthly_tokens_used = 0
            balance.alert_80_sent = False
            balance.is_quota_blocked = False
            balance.period_reset_at = now_dt + timedelta(days=30)

        return balance

    def serialize_user(self, user: SaasUser, plan: Optional[SaasPlan] = None, balance: Optional[SaasCreditBalance] = None) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "nickname": user.nickname or user.full_name,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "role": user.role,
            "plan_code": user.plan_code,
            "is_creator": user.role == "CREATOR" and user.plan_code == "CREATOR",
            "is_active": user.is_active,
            "is_suspended": user.is_suspended,
            "email_verified": user.email_verified,
            "memory_enabled": user.memory_enabled,
            "preferences": user.preferences or {},
            "referral_code": user.referral_code,
            "referred_by_id": user.referred_by_id,
            "created_at": _iso(user.created_at),
            "last_login_at": _iso(user.last_login_at),
        }
        if plan:
            data["plan"] = self.serialize_plan(plan)
        if balance:
            total_avail = balance.monthly_credits_allocated + balance.bonus_credits
            rem = max(0, total_avail - balance.credits_used)
            pct = round((balance.credits_used / total_avail) * 100, 1) if total_avail > 0 else 0.0
            data["usage"] = {
                "monthly_credits_allocated": balance.monthly_credits_allocated,
                "bonus_credits": balance.bonus_credits,
                "total_credits_available": total_avail,
                "credits_used": balance.credits_used,
                "credits_remaining": rem,
                "consumption_pct": pct,
                "alert_80_triggered": pct >= 80.0,
                "is_quota_blocked": balance.is_quota_blocked,
                "daily_messages_used": balance.daily_messages_used,
                "daily_message_limit": plan.daily_message_limit if plan else 25,
                "monthly_messages_used": balance.monthly_messages_used,
                "monthly_tokens_used": balance.monthly_tokens_used,
                "monthly_token_limit": plan.monthly_token_limit if plan else 100_000,
                "period_reset_at": _iso(balance.period_reset_at),
            }
        return data

    def serialize_plan(self, plan: SaasPlan) -> Dict[str, Any]:
        return {
            "id": plan.id,
            "code": plan.code,
            "level": plan.level,
            "name": plan.name,
            "description": plan.description,
            "price_monthly_usd": plan.price_monthly_usd,
            "price_annual_usd": plan.price_annual_usd,
            "is_public": plan.is_public,
            "is_commercializable": plan.is_commercializable,
            "max_brains": plan.max_brains,
            "max_conversations": plan.max_conversations,
            "daily_message_limit": plan.daily_message_limit,
            "monthly_token_limit": plan.monthly_token_limit,
            "monthly_credits": plan.monthly_credits,
            "max_memories": plan.max_memories,
            "allowed_skill_tiers": plan.allowed_skill_tiers or [],
            "features": plan.features or {},
            "priority_level": plan.priority_level,
            "trial_days": plan.trial_days,
            "is_active": plan.is_active,
        }

    def recommend_upgrade_plan(self, current_plan_code: str) -> str:
        order = ["FREE", "STARTER", "PRO", "BUSINESS", "ENTERPRISE"]
        if current_plan_code in order:
            idx = order.index(current_plan_code)
            if idx + 1 < len(order):
                return order[idx + 1]
        return "ENTERPRISE"

    async def check_and_consume_quota(
        self,
        db: AsyncSession,
        user: SaasUser,
        model_id: str = "gemini-3.1-flash-lite",
        skill_code: Optional[str] = None,
        prompt_tokens: int = 120,
        completion_tokens: int = 280,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validates plan access to the requested model & skill, checks daily message limit,
        monthly token limit, and available credits, and records usage.
        Raises HTTP 403/429 with an explicit upgrade recommendation if blocked.
        """
        plan = await self.get_plan(db, user.plan_code)
        balance = await self.get_or_create_credit_balance(db, user)
        upgrade_to = self.recommend_upgrade_plan(plan.code)

        # 1. Verify subscription grace period / status
        sub_res = await db.execute(
            select(SaasSubscription).where(SaasSubscription.user_id == user.id).order_by(desc(SaasSubscription.created_at))
        )
        sub = sub_res.scalars().first()
        if sub and sub.status == "past_due":
            grace_end = sub.grace_period_ends_at
            if grace_end and grace_end.tzinfo is None:
                grace_end = grace_end.replace(tzinfo=timezone.utc)
            if grace_end and utcnow() > grace_end:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail={
                        "error": "Período de gracia expirado por pago pendiente.",
                        "current_plan": plan.code,
                        "action_required": "Actualiza tu método de pago para reactivar los beneficios de tu plan.",
                    },
                )

        # 2. Verify Model Access
        mdl_res = await db.execute(select(SaasAIModel).where(SaasAIModel.model_id == model_id))
        mdl = mdl_res.scalars().first()
        credit_cost = 1
        est_cost_usd = 0.0002
        provider_code = "google"

        if mdl:
            if not mdl.is_active:
                raise HTTPException(status_code=403, detail=f"El modelo '{mdl.display_name}' está deshabilitado temporalmente.")
            if not mdl.is_public and user.plan_code != "CREATOR":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": f"El cerebro '{mdl.display_name}' es privado y exclusivo del nivel CREATOR.",
                        "locked_feature": "private_creator_model",
                        "current_plan": plan.code,
                    },
                )
            if plan.level < mdl.tier_required and plan.code not in (mdl.compatible_plans or []):
                required_plan_name = next((k for k, v in PLAN_LEVELS.items() if v == mdl.tier_required), upgrade_to)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": f"El cerebro '{mdl.display_name}' requiere el plan {required_plan_name} o superior.",
                        "locked_feature": "ai_brain_tier",
                        "current_plan": plan.code,
                        "recommended_plan": required_plan_name,
                        "upgrade_benefit": f"Desbloquea hasta {mdl.display_name} y capacidades avanzadas de razonamiento.",
                    },
                )
            credit_cost = mdl.credit_cost_per_msg
            provider_code = mdl.provider_code
            est_cost_usd = (
                (prompt_tokens / 1000.0) * mdl.cost_per_1k_input_usd
                + (completion_tokens / 1000.0) * mdl.cost_per_1k_output_usd
            )

        # 3. Verify Skill Access if requested
        if skill_code:
            sk_res = await db.execute(select(SaasSkill).where(SaasSkill.code == skill_code))
            skill = sk_res.scalars().first()
            if skill:
                if skill.status != "active":
                    raise HTTPException(status_code=403, detail=f"La skill '{skill.name}' no está activa.")
                if skill.tier == "creator" and user.plan_code != "CREATOR":
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail={
                            "error": f"La skill '{skill.name}' es exclusiva del propietario CREATOR.",
                            "locked_feature": skill.code,
                            "current_plan": plan.code,
                        },
                    )
                if skill.tier not in (plan.allowed_skill_tiers or []) and plan.level < skill.min_plan_level:
                    req_plan = next((k for k, v in PLAN_LEVELS.items() if v == skill.min_plan_level), upgrade_to)
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail={
                            "error": f"La skill '{skill.name}' pertenece al nivel '{skill.tier}' y requiere el plan {req_plan}.",
                            "locked_feature": skill.code,
                            "current_plan": plan.code,
                            "recommended_plan": req_plan,
                            "upgrade_benefit": f"Actualiza a {req_plan} para ejecutar {skill.name}.",
                        },
                    )
                credit_cost += skill.estimated_credit_cost
                est_cost_usd += skill.estimated_api_cost_usd

        # 4. Check Daily Message Limit (CREATOR is exempt)
        if user.plan_code != "CREATOR":
            if balance.daily_messages_used >= plan.daily_message_limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": f"Has alcanzado tu límite diario de {plan.daily_message_limit} mensajes en el plan {plan.code}.",
                        "quota_type": "daily_message_limit",
                        "current_plan": plan.code,
                        "recommended_plan": upgrade_to,
                        "upgrade_benefit": f"Actualiza al plan {upgrade_to} para multiplicar tu capacidad diaria de mensajes.",
                    },
                )

            # 5. Check Monthly Credits & Token Limit
            total_credits_avail = balance.monthly_credits_allocated + balance.bonus_credits
            if balance.credits_used + credit_cost > total_credits_avail:
                balance.is_quota_blocked = True
                await db.flush()
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": f"Créditos mensuales agotados ({balance.credits_used}/{total_credits_avail}).",
                        "quota_type": "monthly_credits",
                        "current_plan": plan.code,
                        "recommended_plan": upgrade_to,
                        "upgrade_benefit": f"Actualiza al plan {upgrade_to} para recibir más créditos mensuales y tokens de alta prioridad.",
                    },
                )

            total_tokens = prompt_tokens + completion_tokens
            if balance.monthly_tokens_used + total_tokens > plan.monthly_token_limit:
                balance.is_quota_blocked = True
                await db.flush()
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": f"Límite mensual de tokens alcanzado ({balance.monthly_tokens_used}/{plan.monthly_token_limit}).",
                        "quota_type": "monthly_tokens",
                        "current_plan": plan.code,
                        "recommended_plan": upgrade_to,
                    },
                )

        # 6. Deduct Credits & Record Usage
        total_tokens = prompt_tokens + completion_tokens
        if user.plan_code != "CREATOR":
            balance.credits_used += credit_cost
        balance.daily_messages_used += 1
        balance.monthly_messages_used += 1
        balance.monthly_tokens_used += total_tokens
        balance.estimated_api_cost_usd = round(balance.estimated_api_cost_usd + est_cost_usd, 6)
        balance.updated_at = utcnow()

        total_avail = balance.monthly_credits_allocated + balance.bonus_credits
        consumption_pct = round((balance.credits_used / total_avail) * 100, 1) if total_avail > 0 else 0.0
        alert_80 = False
        if consumption_pct >= 80.0 and user.plan_code != "CREATOR":
            balance.alert_80_sent = True
            alert_80 = True

        usage_rec = SaasUsageRecord(
            user_id=user.id,
            conversation_id=conversation_id,
            brain_used=provider_code,
            model_used=model_id,
            provider=provider_code,
            skill_used=skill_code,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            credits_charged=0 if user.plan_code == "CREATOR" else credit_cost,
            estimated_cost_usd=est_cost_usd,
        )
        db.add(usage_rec)
        await db.flush()

        return {
            "credits_charged": 0 if user.plan_code == "CREATOR" else credit_cost,
            "credits_remaining": max(0, total_avail - balance.credits_used),
            "consumption_pct": consumption_pct,
            "alert_80_triggered": alert_80,
            "alert_message": (
                f"Aviso de consumo: Has utilizado el {consumption_pct}% de tus créditos mensuales en el plan {plan.code}."
                if alert_80
                else None
            ),
            "daily_messages_used": balance.daily_messages_used,
            "daily_message_limit": plan.daily_message_limit,
            "tokens_charged": total_tokens,
        }

    # ==========================================================================
    # 1. USER REGISTRATION, AUTH, PROFILE & ACCOUNT LIFECYCLE
    # ==========================================================================

    async def register_user(
        self,
        db: AsyncSession,
        email: str,
        password: str,
        full_name: str = "",
        referral_code_used: Optional[str] = None,
        ip_address: str = "127.0.0.1",
        requested_plan: Optional[str] = None,
        requested_role: Optional[str] = None,
    ) -> Dict[str, Any]:
        await self.ensure_seeded(db)
        clean_email = (email or "").strip().lower()
        if not clean_email or "@" not in clean_email or "." not in clean_email.split("@")[-1]:
            raise HTTPException(status_code=400, detail="Dirección de correo electrónico inválida.")

        if len(password or "") < 8:
            raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres.")

        # Block any attempt to self-assign CREATOR or privileged roles during registration
        if (requested_plan and requested_plan.upper() == "CREATOR") or (
            requested_role and requested_role.upper() in {"CREATOR", "ADMIN"}
        ):
            await self.log_audit(
                db=db,
                action="blocked_privilege_escalation_on_register",
                resource_type="user",
                ip_address=ip_address,
                severity="security",
                details={"email": clean_email, "requested_plan": requested_plan, "requested_role": requested_role},
            )
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operación bloqueada: No es posible asignar el plan o rol CREATOR desde el registro.",
            )

        existing = await db.execute(select(SaasUser).where(SaasUser.email == clean_email))
        if existing.scalars().first():
            raise HTTPException(status_code=409, detail="Ya existe una cuenta registrada con este correo electrónico.")

        pw_hash, pw_salt = hash_user_password(password)
        user_id = f"usr_{uuid.uuid4().hex[:16]}"
        my_ref_code = f"LISETH-{secrets.token_hex(3).upper()}"
        verif_token = secrets.token_urlsafe(24)

        referred_by_id: Optional[str] = None
        referrer_user: Optional[SaasUser] = None
        if referral_code_used:
            ref_res = await db.execute(
                select(SaasUser).where(SaasUser.referral_code == referral_code_used.strip().upper())
            )
            referrer_user = ref_res.scalars().first()
            if referrer_user:
                referred_by_id = referrer_user.id

        new_user = SaasUser(
            id=user_id,
            email=clean_email,
            password_hash=pw_hash,
            password_salt=pw_salt,
            full_name=(full_name or clean_email.split("@")[0]).strip(),
            nickname=(full_name or clean_email.split("@")[0]).strip(),
            role="USER",
            plan_code="FREE",
            is_active=True,
            is_suspended=False,
            email_verified=False,
            verification_token=verif_token,
            memory_enabled=True,
            referral_code=my_ref_code,
            referred_by_id=referred_by_id,
            preferences={"theme": "cyber-hud", "language": "es"},
            last_login_at=utcnow(),
        )
        db.add(new_user)

        # Create initial FREE subscription
        sub = SaasSubscription(
            id=f"sub_{uuid.uuid4().hex[:14]}",
            user_id=user_id,
            plan_code="FREE",
            billing_cycle="monthly",
            status="active",
            price_usd=0.0,
            auto_renew=True,
            current_period_start=utcnow(),
            current_period_end=utcnow() + timedelta(days=30),
        )
        db.add(sub)

        # Create initial credit balance
        free_plan = await self.get_plan(db, "FREE")
        balance = SaasCreditBalance(
            user_id=user_id,
            monthly_credits_allocated=free_plan.monthly_credits,
            credits_used=0,
            bonus_credits=100 if referrer_user else 0,  # Initial referral signup bonus
            daily_messages_used=0,
            monthly_messages_used=0,
            monthly_tokens_used=0,
            last_daily_reset=utcnow().strftime("%Y-%m-%d"),
            period_reset_at=utcnow() + timedelta(days=30),
        )
        db.add(balance)

        # Create referral record if invited
        if referrer_user:
            ref_record = SaasReferral(
                id=f"ref_{uuid.uuid4().hex[:14]}",
                referrer_user_id=referrer_user.id,
                referred_user_id=user_id,
                referral_code_used=referrer_user.referral_code,
                status="pending",
                referrer_reward_credits=500,
                referred_reward_credits=250,
            )
            db.add(ref_record)

        await self.log_audit(
            db=db,
            action="user_registered",
            actor_user=new_user,
            target_user_id=user_id,
            resource_type="user",
            resource_id=user_id,
            ip_address=ip_address,
            details={"email": clean_email, "referred_by": referred_by_id},
        )
        await db.commit()

        token = sign_saas_token(new_user.id, new_user.email, new_user.role, new_user.plan_code)
        return {
            "ok": True,
            "token": token,
            "verification_token": verif_token,
            "user": self.serialize_user(new_user, free_plan, balance),
        }

    async def login_user(
        self,
        db: AsyncSession,
        email: str,
        password: str,
        ip_address: str = "127.0.0.1",
    ) -> Dict[str, Any]:
        await self.ensure_seeded(db)
        clean_email = (email or "").strip().lower()
        res = await db.execute(select(SaasUser).where(SaasUser.email == clean_email))
        user = res.scalars().first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="Credenciales inválidas.")

        if not verify_user_password(password, user.password_hash, user.password_salt):
            await self.log_audit(
                db=db,
                action="login_failed",
                target_user_id=user.id,
                resource_type="auth",
                ip_address=ip_address,
                severity="warning",
                details={"email": clean_email},
            )
            await db.commit()
            raise HTTPException(status_code=401, detail="Credenciales inválidas.")

        if user.is_suspended:
            raise HTTPException(
                status_code=403,
                detail=f"Tu cuenta está suspendida: {user.suspension_reason or 'Contacta al administrador.'}",
            )

        user.last_login_at = utcnow()
        plan = await self.get_plan(db, user.plan_code)
        balance = await self.get_or_create_credit_balance(db, user)
        await self.log_audit(
            db=db,
            action="user_login",
            actor_user=user,
            target_user_id=user.id,
            resource_type="auth",
            ip_address=ip_address,
        )
        await db.commit()

        token = sign_saas_token(user.id, user.email, user.role, user.plan_code)
        return {
            "ok": True,
            "token": token,
            "user": self.serialize_user(user, plan, balance),
        }

    async def verify_email(self, db: AsyncSession, verification_token: str) -> Dict[str, Any]:
        await self.ensure_seeded(db)
        res = await db.execute(
            select(SaasUser).where(SaasUser.verification_token == verification_token.strip())
        )
        user = res.scalars().first()
        if not user:
            raise HTTPException(status_code=400, detail="Token de verificación inválido o expirado.")

        user.email_verified = True
        user.verification_token = None
        user.updated_at = utcnow()

        # Check if user has a pending referral to verify & reward
        ref_res = await db.execute(
            select(SaasReferral).where(
                and_(SaasReferral.referred_user_id == user.id, SaasReferral.status == "pending")
            )
        )
        referral = ref_res.scalars().first()
        reward_granted = False
        if referral:
            referral.status = "rewarded"
            referral.verified_at = utcnow()
            referral.rewarded_at = utcnow()

            # Grant credits to referrer
            referrer_res = await db.execute(select(SaasUser).where(SaasUser.id == referral.referrer_user_id))
            referrer = referrer_res.scalars().first()
            if referrer:
                ref_bal = await self.get_or_create_credit_balance(db, referrer)
                ref_bal.bonus_credits += referral.referrer_reward_credits

            # Grant credits to referred user
            usr_bal = await self.get_or_create_credit_balance(db, user)
            usr_bal.bonus_credits += referral.referred_reward_credits
            reward_granted = True

        await db.commit()
        return {
            "ok": True,
            "email_verified": True,
            "referral_reward_granted": reward_granted,
            "message": "Correo verificado correctamente.",
        }

    async def request_password_reset(self, db: AsyncSession, email: str) -> Dict[str, Any]:
        await self.ensure_seeded(db)
        clean_email = (email or "").strip().lower()
        res = await db.execute(select(SaasUser).where(SaasUser.email == clean_email))
        user = res.scalars().first()
        if not user or not user.is_active:
            # Return generic success to prevent email enumeration
            return {"ok": True, "message": "Si el correo existe, se ha generado un enlace de recuperación."}

        reset_token = secrets.token_urlsafe(24)
        user.reset_token = reset_token
        user.reset_token_expires = utcnow() + timedelta(hours=2)
        await db.commit()
        return {
            "ok": True,
            "reset_token": reset_token,
            "message": "Token de recuperación generado (válido por 2 horas).",
        }

    async def reset_password(self, db: AsyncSession, reset_token: str, new_password: str) -> Dict[str, Any]:
        await self.ensure_seeded(db)
        if len(new_password or "") < 8:
            raise HTTPException(status_code=400, detail="La nueva contraseña debe tener al menos 8 caracteres.")

        res = await db.execute(select(SaasUser).where(SaasUser.reset_token == reset_token.strip()))
        user = res.scalars().first()
        if not user:
            raise HTTPException(status_code=400, detail="Token de recuperación inválido.")

        exp = user.reset_token_expires
        if exp and exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if not exp or utcnow() > exp:
            raise HTTPException(status_code=400, detail="El token de recuperación ha expirado.")

        pw_hash, pw_salt = hash_user_password(new_password)
        user.password_hash = pw_hash
        user.password_salt = pw_salt
        user.reset_token = None
        user.reset_token_expires = None
        user.updated_at = utcnow()
        await db.commit()
        return {"ok": True, "message": "Contraseña restablecida exitosamente."}

    async def update_profile(
        self,
        db: AsyncSession,
        user: SaasUser,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        # Strictly forbid changing role, plan_code, id, or email via profile update
        forbidden_keys = {"role", "plan_code", "id", "is_creator", "password_hash", "password_salt"}
        attempted_forbidden = forbidden_keys.intersection(set(updates.keys()))
        if attempted_forbidden:
            await self.log_audit(
                db=db,
                action="blocked_profile_privilege_tampering",
                actor_user=user,
                target_user_id=user.id,
                resource_type="user",
                severity="security",
                details={"attempted_fields": list(attempted_forbidden)},
            )
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No está permitido modificar el rol o plan desde la edición de perfil.",
            )

        if "full_name" in updates and updates["full_name"] is not None:
            user.full_name = str(updates["full_name"]).strip()[:150]
        if "nickname" in updates and updates["nickname"] is not None:
            user.nickname = str(updates["nickname"]).strip()[:100]
        if "bio" in updates and updates["bio"] is not None:
            user.bio = str(updates["bio"]).strip()[:1000]
        if "avatar_url" in updates and updates["avatar_url"] is not None:
            user.avatar_url = str(updates["avatar_url"]).strip()[:500]
        if "memory_enabled" in updates and updates["memory_enabled"] is not None:
            user.memory_enabled = bool(updates["memory_enabled"])
        if "preferences" in updates and isinstance(updates["preferences"], dict):
            merged = dict(user.preferences or {})
            merged.update(updates["preferences"])
            user.preferences = merged

        user.updated_at = utcnow()
        plan = await self.get_plan(db, user.plan_code)
        balance = await self.get_or_create_credit_balance(db, user)
        await db.commit()
        return {"ok": True, "user": self.serialize_user(user, plan, balance)}

    async def change_password(
        self,
        db: AsyncSession,
        user: SaasUser,
        current_password: str,
        new_password: str,
    ) -> Dict[str, Any]:
        if not verify_user_password(current_password, user.password_hash, user.password_salt):
            raise HTTPException(status_code=401, detail="La contraseña actual no es correcta.")
        if len(new_password or "") < 8:
            raise HTTPException(status_code=400, detail="La nueva contraseña debe tener al menos 8 caracteres.")

        pw_hash, pw_salt = hash_user_password(new_password)
        user.password_hash = pw_hash
        user.password_salt = pw_salt
        user.updated_at = utcnow()
        await self.log_audit(
            db=db,
            action="password_changed",
            actor_user=user,
            target_user_id=user.id,
            resource_type="user",
        )
        await db.commit()
        return {"ok": True, "message": "Contraseña actualizada correctamente."}

    async def delete_own_account(self, db: AsyncSession, user: SaasUser) -> Dict[str, Any]:
        if user.id == CREATOR_USER_ID or user.role == "CREATOR":
            raise HTTPException(
                status_code=403,
                detail="La cuenta soberana CREATOR (Señor Santiago) no puede ser eliminada.",
            )

        # Cascade delete private conversations, messages, memories
        await db.execute(delete(SaasMessage).where(SaasMessage.user_id == user.id))
        await db.execute(delete(SaasConversation).where(SaasConversation.user_id == user.id))
        await db.execute(delete(SaasUserMemory).where(SaasUserMemory.user_id == user.id))
        await db.execute(delete(SaasAgent).where(SaasAgent.owner_user_id == user.id))
        user.is_active = False
        user.email = f"deleted_{user.id}@deleted.liseth.ai"
        user.updated_at = utcnow()
        await self.log_audit(
            db=db,
            action="account_deleted_by_user",
            actor_user=user,
            target_user_id=user.id,
            resource_type="user",
        )
        await db.commit()
        return {"ok": True, "message": "Tu cuenta y todos tus datos privados han sido eliminados."}

    # ==========================================================================
    # 2. MULTI-TENANT CONVERSATION WORKSPACE (STRICT ISOLATION BY user_id)
    # ==========================================================================

    def serialize_conversation(self, conv: SaasConversation, include_messages: Optional[List[SaasMessage]] = None) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "id": conv.id,
            "user_id": conv.user_id,
            "title": conv.title,
            "is_archived": conv.is_archived,
            "is_pinned": conv.is_pinned,
            "brain_used": conv.brain_used,
            "model_used": conv.model_used,
            "agent_id": conv.agent_id,
            "active_skills": conv.active_skills or [],
            "associated_files": conv.associated_files or [],
            "context_metadata": conv.context_metadata or {},
            "summary": conv.summary or "",
            "message_count": conv.message_count,
            "created_at": _iso(conv.created_at),
            "updated_at": _iso(conv.updated_at),
        }
        if include_messages is not None:
            data["messages"] = [
                {
                    "id": m.id,
                    "conversation_id": m.conversation_id,
                    "user_id": m.user_id,
                    "role": m.role,
                    "content": m.content,
                    "brain_used": m.brain_used,
                    "model_used": m.model_used,
                    "skills_invoked": m.skills_invoked or [],
                    "tokens_used": m.tokens_used,
                    "credits_used": m.credits_used,
                    "created_at": _iso(m.created_at),
                }
                for m in include_messages
            ]
        return data

    async def create_conversation(
        self,
        db: AsyncSession,
        user: SaasUser,
        title: str = "Nueva conversación",
        brain_used: str = "gemini",
        model_used: str = "gemini-3.1-flash-lite",
        active_skills: Optional[List[str]] = None,
        associated_files: Optional[List[str]] = None,
        agent_id: Optional[str] = None,
        context_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        plan = await self.get_plan(db, user.plan_code)

        # Count active (non-archived) conversations for this user
        cnt_res = await db.execute(
            select(func.count(SaasConversation.id)).where(
                and_(SaasConversation.user_id == user.id, SaasConversation.is_archived == False)  # noqa: E712
            )
        )
        active_count = cnt_res.scalar() or 0
        if user.plan_code != "CREATOR" and active_count >= plan.max_conversations:
            upgrade_to = self.recommend_upgrade_plan(plan.code)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": f"Has alcanzado el máximo de {plan.max_conversations} conversaciones activas permitidas en el plan {plan.code}.",
                    "locked_feature": "max_conversations",
                    "current_plan": plan.code,
                    "recommended_plan": upgrade_to,
                    "upgrade_benefit": f"Archiva una conversación existente o actualiza al plan {upgrade_to} para tener más conversaciones simultáneas.",
                },
            )

        conv = SaasConversation(
            id=f"conv_{uuid.uuid4().hex[:16]}",
            user_id=user.id,
            title=(title or "Nueva conversación").strip()[:250],
            is_archived=False,
            is_pinned=False,
            brain_used=brain_used,
            model_used=model_used,
            agent_id=agent_id,
            active_skills=active_skills or [],
            associated_files=associated_files or [],
            context_metadata=context_metadata or {},
            summary="",
            message_count=0,
        )
        db.add(conv)
        await db.commit()
        return {"ok": True, "conversation": self.serialize_conversation(conv, [])}

    async def list_conversations(
        self,
        db: AsyncSession,
        user: SaasUser,
        include_archived: bool = False,
        search_query: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        page = max(1, page)
        page_size = max(1, min(100, page_size))

        conditions = [SaasConversation.user_id == user.id]
        if not include_archived:
            conditions.append(SaasConversation.is_archived == False)  # noqa: E712
        if search_query and search_query.strip():
            q = f"%{search_query.strip()}%"
            conditions.append(
                or_(SaasConversation.title.ilike(q), SaasConversation.summary.ilike(q))
            )

        total_res = await db.execute(
            select(func.count(SaasConversation.id)).where(and_(*conditions))
        )
        total = total_res.scalar() or 0

        stmt = (
            select(SaasConversation)
            .where(and_(*conditions))
            .order_by(desc(SaasConversation.is_pinned), desc(SaasConversation.updated_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await db.execute(stmt)).scalars().all()
        return {
            "ok": True,
            "total": total,
            "page": page,
            "page_size": page_size,
            "conversations": [self.serialize_conversation(c) for c in rows],
        }

    async def _get_owned_conversation(
        self,
        db: AsyncSession,
        user: SaasUser,
        conversation_id: str,
    ) -> SaasConversation:
        res = await db.execute(
            select(SaasConversation).where(SaasConversation.id == conversation_id)
        )
        conv = res.scalars().first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversación no encontrada.")
        if conv.user_id != user.id:
            await self.log_audit(
                db=db,
                action="cross_tenant_conversation_access_blocked",
                actor_user=user,
                target_user_id=conv.user_id,
                resource_type="conversation",
                resource_id=conversation_id,
                severity="security",
            )
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado: No tienes permiso para acceder a conversaciones de otro usuario.",
            )
        return conv

    async def get_conversation(
        self,
        db: AsyncSession,
        user: SaasUser,
        conversation_id: str,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        conv = await self._get_owned_conversation(db, user, conversation_id)
        page = max(1, page)
        page_size = max(1, min(200, page_size))

        msg_stmt = (
            select(SaasMessage)
            .where(
                and_(
                    SaasMessage.conversation_id == conv.id,
                    SaasMessage.user_id == user.id,
                )
            )
            .order_by(SaasMessage.created_at.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        msgs = (await db.execute(msg_stmt)).scalars().all()
        return {
            "ok": True,
            "conversation": self.serialize_conversation(conv, list(msgs)),
            "page": page,
            "page_size": page_size,
        }

    async def update_conversation(
        self,
        db: AsyncSession,
        user: SaasUser,
        conversation_id: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        conv = await self._get_owned_conversation(db, user, conversation_id)
        if "title" in updates and updates["title"] is not None:
            conv.title = str(updates["title"]).strip()[:250]
        if "is_archived" in updates and updates["is_archived"] is not None:
            conv.is_archived = bool(updates["is_archived"])
        if "is_pinned" in updates and updates["is_pinned"] is not None:
            conv.is_pinned = bool(updates["is_pinned"])
        if "active_skills" in updates and isinstance(updates["active_skills"], list):
            conv.active_skills = updates["active_skills"]
        if "associated_files" in updates and isinstance(updates["associated_files"], list):
            conv.associated_files = updates["associated_files"]
        if "model_used" in updates and updates["model_used"]:
            conv.model_used = str(updates["model_used"])
        if "brain_used" in updates and updates["brain_used"]:
            conv.brain_used = str(updates["brain_used"])

        conv.updated_at = utcnow()
        await db.commit()
        return {"ok": True, "conversation": self.serialize_conversation(conv)}

    async def delete_conversation(
        self,
        db: AsyncSession,
        user: SaasUser,
        conversation_id: str,
    ) -> Dict[str, Any]:
        conv = await self._get_owned_conversation(db, user, conversation_id)
        await db.execute(
            delete(SaasMessage).where(
                and_(SaasMessage.conversation_id == conv.id, SaasMessage.user_id == user.id)
            )
        )
        await db.delete(conv)
        await db.commit()
        return {"ok": True, "deleted_id": conversation_id}

    async def add_message_and_respond(
        self,
        db: AsyncSession,
        user: SaasUser,
        conversation_id: str,
        content: str,
        model_id: Optional[str] = None,
        skill_code: Optional[str] = None,
        use_live_ai: bool = False,
    ) -> Dict[str, Any]:
        """
        Appends a user message to an owned conversation, enforces plan/credit quotas,
        retrieves user-isolated contextual memory, generates or synthesizes the assistant response,
        auto-extracts durable user memories when appropriate, and updates the conversation summary.
        """
        conv = await self._get_owned_conversation(db, user, conversation_id)
        clean_content = (content or "").strip()
        if not clean_content:
            raise HTTPException(status_code=400, detail="El contenido del mensaje no puede estar vacío.")

        chosen_model = model_id or conv.model_used or "gemini-3.1-flash-lite"
        est_prompt_tokens = max(25, len(clean_content.split()) * 3)
        est_completion_tokens = 160

        # 1. Enforce plan & quota BEFORE processing
        quota_report = await self.check_and_consume_quota(
            db=db,
            user=user,
            model_id=chosen_model,
            skill_code=skill_code,
            prompt_tokens=est_prompt_tokens,
            completion_tokens=est_completion_tokens,
            conversation_id=conv.id,
        )

        # 2. Retrieve contextual memories for this user if memory_enabled
        injected_memories: List[Dict[str, Any]] = []
        if user.memory_enabled:
            injected_memories = await self.retrieve_contextual_memories(db, user, clean_content, limit=4)

        # 3. Store user message
        user_msg = SaasMessage(
            id=f"msg_{uuid.uuid4().hex[:16]}",
            conversation_id=conv.id,
            user_id=user.id,
            role="user",
            content=clean_content,
            brain_used=conv.brain_used,
            model_used=chosen_model,
            skills_invoked=[skill_code] if skill_code else [],
            tokens_used=est_prompt_tokens,
            credits_used=0,
        )
        db.add(user_msg)

        # 4. Auto-extract durable memory if user states a personal fact or preference
        extracted_memory: Optional[Dict[str, Any]] = None
        if user.memory_enabled:
            candidate_fact = self.extract_useful_memory_from_text(clean_content)
            if candidate_fact:
                try:
                    mem_res = await self.create_memory(
                        db=db,
                        user=user,
                        content=candidate_fact["content"],
                        scope=candidate_fact["scope"],
                        title=candidate_fact["title"],
                        keywords=candidate_fact["keywords"],
                        importance=candidate_fact["importance"],
                        conversation_id=conv.id,
                        commit=False,
                    )
                    extracted_memory = mem_res.get("memory")
                except HTTPException:
                    # If user hit max_memories limit on FREE plan, don't fail the chat message
                    pass

        # 5. Generate assistant reply
        mem_context_note = ""
        if injected_memories:
            mem_snippets = "; ".join(m["content"] for m in injected_memories[:2])
            mem_context_note = f" [Memoria contextual aplicada: {mem_snippets}]"

        reply_text = ""
        if use_live_ai:
            try:
                from app.services.brain_router import brain_router
                sys_prompt = f"Usuario autenticado: {user.nickname or user.full_name} (Plan {user.plan_code})."
                if mem_context_note:
                    sys_prompt += f" Recuerdos relevantes del usuario: {mem_context_note}"
                ai_res = await brain_router.generate_response(
                    prompt=clean_content,
                    system_prompt=sys_prompt,
                )
                reply_text = ai_res.get("text") or ""
            except Exception as e:
                logger.warning(f"Fallback en chat SaaS: {e}")

        if not reply_text:
            reply_text = (
                f"Respuesta procesada por **{chosen_model}** para **{user.nickname or user.full_name}** "
                f"(Plan `{user.plan_code}`).{mem_context_note}"
            )

        assistant_msg = SaasMessage(
            id=f"msg_{uuid.uuid4().hex[:16]}",
            conversation_id=conv.id,
            user_id=user.id,
            role="assistant",
            content=reply_text,
            brain_used=conv.brain_used,
            model_used=chosen_model,
            skills_invoked=[skill_code] if skill_code else [],
            tokens_used=est_completion_tokens,
            credits_used=quota_report["credits_charged"],
            meta_info={"memories_used": [m["id"] for m in injected_memories]},
        )
        db.add(assistant_msg)

        # 6. Update conversation metadata & automatic summary
        conv.message_count = (conv.message_count or 0) + 2
        conv.model_used = chosen_model
        if skill_code and skill_code not in (conv.active_skills or []):
            conv.active_skills = list(conv.active_skills or []) + [skill_code]
        if conv.title == "Nueva conversación" and len(clean_content) > 3:
            conv.title = clean_content[:60]
        conv.summary = f"Último tema: {clean_content[:120]}"
        conv.updated_at = utcnow()

        await db.commit()
        return {
            "ok": True,
            "conversation_id": conv.id,
            "user_message": {
                "id": user_msg.id,
                "role": "user",
                "content": user_msg.content,
                "created_at": _iso(user_msg.created_at),
            },
            "assistant_message": {
                "id": assistant_msg.id,
                "role": "assistant",
                "content": assistant_msg.content,
                "model_used": chosen_model,
                "created_at": _iso(assistant_msg.created_at),
            },
            "memories_injected": injected_memories,
            "memory_auto_extracted": extracted_memory,
            "quota": quota_report,
        }

    # ==========================================================================
    # 3. INDIVIDUAL USER MEMORY BRAIN (PERSONAL + CONTEXTUAL + SEMANTIC SEARCH)
    # ==========================================================================

    def extract_useful_memory_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Distinguishes durable user facts, preferences, or explicit memory requests
        from casual conversation history.
        """
        clean = (text or "").strip()
        if len(clean) < 10:
            return None

        lower = clean.lower()
        patterns = [
            (r"(?:recuerda que|guarda en memoria que|ten en cuenta que)\s+(.+)", "authorized_fact", "Recuerdo explícito", 5),
            (r"(?:prefiero|me gusta que|mi preferencia es)\s+(.+)", "preference", "Preferencia del usuario", 4),
            (r"(?:mi empresa se llama|trabajo en|soy director de|mi profesión es|mi proyecto es)\s+(.+)", "personal", "Perfil profesional", 4),
            (r"(?:mi objetivo es|mi meta es)\s+(.+)", "contextual", "Objetivo estratégico", 4),
        ]
        for pat, scope, title, importance in patterns:
            m = re.search(pat, lower)
            if m:
                words = [w for w in re.findall(r"[a-záéíóúñ0-9]{4,}", lower) if len(w) >= 4][:8]
                return {
                    "scope": scope,
                    "title": title,
                    "content": clean[:500],
                    "keywords": words,
                    "importance": importance,
                }
        return None

    def serialize_memory(self, mem: SaasUserMemory) -> Dict[str, Any]:
        return {
            "id": mem.id,
            "user_id": mem.user_id,
            "conversation_id": mem.conversation_id,
            "scope": mem.scope,
            "title": mem.title,
            "content": mem.content,
            "keywords": mem.keywords or [],
            "importance": mem.importance,
            "is_authorized": mem.is_authorized,
            "is_active": mem.is_active,
            "created_at": _iso(mem.created_at),
            "updated_at": _iso(mem.updated_at),
        }

    async def create_memory(
        self,
        db: AsyncSession,
        user: SaasUser,
        content: str,
        scope: str = "personal",
        title: str = "",
        keywords: Optional[List[str]] = None,
        importance: int = 3,
        conversation_id: Optional[str] = None,
        is_authorized: bool = True,
        commit: bool = True,
    ) -> Dict[str, Any]:
        plan = await self.get_plan(db, user.plan_code)
        cnt_res = await db.execute(
            select(func.count(SaasUserMemory.id)).where(SaasUserMemory.user_id == user.id)
        )
        current_count = cnt_res.scalar() or 0
        if user.plan_code != "CREATOR" and current_count >= plan.max_memories:
            upgrade_to = self.recommend_upgrade_plan(plan.code)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": f"Has alcanzado el límite de {plan.max_memories} memorias personales en el plan {plan.code}.",
                    "locked_feature": "max_memories",
                    "current_plan": plan.code,
                    "recommended_plan": upgrade_to,
                    "upgrade_benefit": f"Actualiza al plan {upgrade_to} para ampliar tu cerebro de memoria persistente.",
                },
            )

        clean_content = (content or "").strip()
        if not clean_content:
            raise HTTPException(status_code=400, detail="El contenido de la memoria no puede estar vacío.")

        if not keywords:
            keywords = [w for w in re.findall(r"[a-záéíóúñ0-9]{4,}", clean_content.lower())][:10]

        mem = SaasUserMemory(
            id=f"mem_{uuid.uuid4().hex[:16]}",
            user_id=user.id,
            conversation_id=conversation_id,
            scope=scope,
            title=(title or clean_content[:45]).strip(),
            content=clean_content,
            keywords=keywords,
            importance=max(1, min(5, int(importance))),
            is_authorized=is_authorized,
            is_active=True,
        )
        db.add(mem)
        if commit:
            await db.commit()
        else:
            await db.flush()
        return {"ok": True, "memory": self.serialize_memory(mem)}

    async def list_memories(
        self,
        db: AsyncSession,
        user: SaasUser,
        scope: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> Dict[str, Any]:
        conditions = [SaasUserMemory.user_id == user.id]
        if scope:
            conditions.append(SaasUserMemory.scope == scope)
        if search_query and search_query.strip():
            q = f"%{search_query.strip()}%"
            conditions.append(or_(SaasUserMemory.content.ilike(q), SaasUserMemory.title.ilike(q)))

        stmt = (
            select(SaasUserMemory)
            .where(and_(*conditions))
            .order_by(desc(SaasUserMemory.importance), desc(SaasUserMemory.updated_at))
        )
        rows = (await db.execute(stmt)).scalars().all()
        return {
            "ok": True,
            "memory_enabled": user.memory_enabled,
            "total": len(rows),
            "memories": [self.serialize_memory(m) for m in rows],
        }

    async def retrieve_contextual_memories(
        self,
        db: AsyncSession,
        user: SaasUser,
        query_text: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Semantic/keyword overlap scorer strictly isolated to `user.id`."""
        if not user.memory_enabled:
            return []
        stmt = select(SaasUserMemory).where(
            and_(SaasUserMemory.user_id == user.id, SaasUserMemory.is_active == True)  # noqa: E712
        )
        all_mems = (await db.execute(stmt)).scalars().all()
        if not all_mems:
            return []

        q_tokens = set(re.findall(r"[a-záéíóúñ0-9]{3,}", (query_text or "").lower()))
        scored: List[Tuple[float, SaasUserMemory]] = []
        for m in all_mems:
            m_tokens = set(re.findall(r"[a-záéíóúñ0-9]{3,}", (m.content + " " + m.title).lower()))
            m_tokens.update(str(k).lower() for k in (m.keywords or []))
            overlap = len(q_tokens.intersection(m_tokens))
            score = (overlap * 3.0) + (m.importance * 0.5)
            scored.append((score, m))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [self.serialize_memory(item[1]) for item in scored[:limit]]

    async def update_memory(
        self,
        db: AsyncSession,
        user: SaasUser,
        memory_id: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        res = await db.execute(select(SaasUserMemory).where(SaasUserMemory.id == memory_id))
        mem = res.scalars().first()
        if not mem:
            raise HTTPException(status_code=404, detail="Memoria no encontrada.")
        if mem.user_id != user.id:
            raise HTTPException(status_code=403, detail="Acceso denegado: No puedes modificar memorias de otro usuario.")

        if "content" in updates and updates["content"]:
            mem.content = str(updates["content"]).strip()
        if "title" in updates and updates["title"] is not None:
            mem.title = str(updates["title"]).strip()[:200]
        if "scope" in updates and updates["scope"]:
            mem.scope = str(updates["scope"])
        if "importance" in updates and updates["importance"] is not None:
            mem.importance = max(1, min(5, int(updates["importance"])))
        if "is_active" in updates and updates["is_active"] is not None:
            mem.is_active = bool(updates["is_active"])

        mem.updated_at = utcnow()
        await db.commit()
        return {"ok": True, "memory": self.serialize_memory(mem)}

    async def delete_memory(
        self,
        db: AsyncSession,
        user: SaasUser,
        memory_id: str,
    ) -> Dict[str, Any]:
        res = await db.execute(select(SaasUserMemory).where(SaasUserMemory.id == memory_id))
        mem = res.scalars().first()
        if not mem:
            raise HTTPException(status_code=404, detail="Memoria no encontrada.")
        if mem.user_id != user.id:
            raise HTTPException(status_code=403, detail="Acceso denegado: No puedes eliminar memorias de otro usuario.")

        await db.delete(mem)
        await db.commit()
        return {"ok": True, "deleted_id": memory_id}

    # ==========================================================================
    # 4. CENTRALIZED SKILLS, AI BRAINS, MODELS & SPECIALIZED AGENTS REGISTRY
    # ==========================================================================

    async def get_catalog_for_user(self, db: AsyncSession, user: SaasUser) -> Dict[str, Any]:
        plan = await self.get_plan(db, user.plan_code)
        is_creator = user.plan_code == "CREATOR" and user.role == "CREATOR"

        # Providers
        provs = (await db.execute(select(SaasAIProvider).order_by(SaasAIProvider.priority))).scalars().all()

        # Models (hide private models from non-CREATOR)
        mdl_stmt = select(SaasAIModel).order_by(SaasAIModel.tier_required, SaasAIModel.display_name)
        all_models = (await db.execute(mdl_stmt)).scalars().all()
        models_out = []
        for idx, m in enumerate(all_models):
            if not m.is_public and not is_creator:
                continue
            unlocked = is_creator or (
                m.is_active
                and (plan.level >= m.tier_required or plan.code in (m.compatible_plans or []))
                and idx < plan.max_brains
            )
            req_plan = next((k for k, v in PLAN_LEVELS.items() if v == m.tier_required), "PRO")
            models_out.append({
                "id": m.id,
                "provider_code": m.provider_code,
                "model_id": m.model_id,
                "display_name": m.display_name,
                "tier_required": m.tier_required,
                "compatible_plans": m.compatible_plans or [],
                "credit_cost_per_msg": m.credit_cost_per_msg,
                "is_default": m.is_default,
                "is_public": m.is_public,
                "is_active": m.is_active,
                "unlocked": unlocked,
                "required_plan": req_plan if not unlocked else plan.code,
                "locked_reason": None if unlocked else f"Disponible a partir del plan {req_plan}.",
            })

        # Skills
        sk_stmt = select(SaasSkill).order_by(SaasSkill.min_plan_level, SaasSkill.name)
        all_skills = (await db.execute(sk_stmt)).scalars().all()
        skills_out = []
        for s in all_skills:
            if s.tier == "creator" and not is_creator:
                continue
            unlocked = is_creator or (
                s.status == "active"
                and (s.tier in (plan.allowed_skill_tiers or []) or plan.level >= s.min_plan_level)
            )
            req_plan = next((k for k, v in PLAN_LEVELS.items() if v == s.min_plan_level), "STARTER")
            skills_out.append({
                "id": s.id,
                "code": s.code,
                "name": s.name,
                "description": s.description,
                "category": s.category,
                "version": s.version,
                "status": s.status,
                "tier": s.tier,
                "min_plan_level": s.min_plan_level,
                "compatible_plans": s.compatible_plans or [],
                "estimated_credit_cost": s.estimated_credit_cost,
                "unlocked": unlocked,
                "required_plan": req_plan if not unlocked else plan.code,
                "locked_reason": None if unlocked else f"Requiere el plan {req_plan} (nivel '{s.tier}').",
            })

        # Agents (public platform agents + user's own custom agents)
        agt_stmt = select(SaasAgent).where(
            or_(SaasAgent.is_public == True, SaasAgent.owner_user_id == user.id)  # noqa: E712
        )
        all_agents = (await db.execute(agt_stmt)).scalars().all()
        agents_out = []
        for a in all_agents:
            unlocked = is_creator or a.owner_user_id == user.id or plan.level >= a.min_plan_level
            req_plan = next((k for k, v in PLAN_LEVELS.items() if v == a.min_plan_level), "PRO")
            agents_out.append({
                "id": a.id,
                "owner_user_id": a.owner_user_id,
                "is_custom": a.owner_user_id == user.id,
                "name": a.name,
                "role_title": a.role_title,
                "description": a.description,
                "system_prompt": a.system_prompt,
                "preferred_brain": a.preferred_brain,
                "preferred_model": a.preferred_model,
                "skill_codes": a.skill_codes or [],
                "min_plan_level": a.min_plan_level,
                "avatar_icon": a.avatar_icon,
                "unlocked": unlocked,
                "required_plan": req_plan if not unlocked else plan.code,
            })

        return {
            "ok": True,
            "current_plan": plan.code,
            "max_brains_allowed": plan.max_brains,
            "providers": [
                {"code": p.code, "name": p.name, "status": p.status, "priority": p.priority}
                for p in provs
            ],
            "models": models_out,
            "skills": skills_out,
            "agents": agents_out,
        }

    async def create_custom_agent(
        self,
        db: AsyncSession,
        user: SaasUser,
        name: str,
        role_title: str,
        description: str,
        system_prompt: str,
        preferred_brain: str = "gemini",
        preferred_model: str = "gemini-3.1-flash-lite",
        skill_codes: Optional[List[str]] = None,
        avatar_icon: str = "🤖",
    ) -> Dict[str, Any]:
        plan = await self.get_plan(db, user.plan_code)
        features = plan.features or {}
        if user.plan_code != "CREATOR" and not features.get("custom_agents", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": f"La creación de agentes personalizados no está incluida en tu plan actual ({plan.code}).",
                    "locked_feature": "custom_agents",
                    "current_plan": plan.code,
                    "recommended_plan": "BUSINESS",
                    "upgrade_benefit": "Actualiza al plan BUSINESS ($75/mes) o ENTERPRISE ($200/mes) para crear tus propios agentes especializados con skills combinadas.",
                },
            )

        agt = SaasAgent(
            id=f"agt_{uuid.uuid4().hex[:14]}",
            owner_user_id=user.id,
            name=(name or "Agente Personalizado").strip()[:120],
            role_title=(role_title or "Especialista IA").strip()[:120],
            description=(description or "").strip(),
            system_prompt=(system_prompt or "").strip(),
            preferred_brain=preferred_brain,
            preferred_model=preferred_model,
            skill_codes=skill_codes or [],
            min_plan_level=plan.level,
            is_public=False,
            is_active=True,
            avatar_icon=avatar_icon or "🤖",
        )
        db.add(agt)
        await db.commit()
        return {
            "ok": True,
            "agent": {
                "id": agt.id,
                "owner_user_id": agt.owner_user_id,
                "name": agt.name,
                "role_title": agt.role_title,
                "description": agt.description,
                "system_prompt": agt.system_prompt,
                "preferred_brain": agt.preferred_brain,
                "preferred_model": agt.preferred_model,
                "skill_codes": agt.skill_codes,
                "avatar_icon": agt.avatar_icon,
            },
        }

    # ==========================================================================
    # 5. MONETIZATION, SUBSCRIPTIONS, CHECKOUT, INVOICES & STRIPE WEBHOOKS
    # ==========================================================================

    async def list_public_plans(self, db: AsyncSession, include_creator: bool = False) -> List[Dict[str, Any]]:
        await self.ensure_seeded(db)
        stmt = select(SaasPlan).where(SaasPlan.is_active == True).order_by(SaasPlan.level)  # noqa: E712
        plans = (await db.execute(stmt)).scalars().all()
        result = []
        for p in plans:
            if p.code == "CREATOR" and not include_creator:
                continue
            result.append(self.serialize_plan(p))
        return result

    async def validate_promo_code(
        self,
        db: AsyncSession,
        code: str,
        target_plan_code: str,
    ) -> SaasPromoCode:
        clean_code = (code or "").strip().upper()
        res = await db.execute(select(SaasPromoCode).where(SaasPromoCode.code == clean_code))
        promo = res.scalars().first()
        if not promo or not promo.is_active:
            raise HTTPException(status_code=400, detail="El código promocional no existe o no está activo.")
        if promo.current_uses >= promo.max_uses:
            raise HTTPException(status_code=400, detail="Este código promocional ha agotado su límite de usos.")
        if promo.valid_until:
            vu = promo.valid_until
            if vu.tzinfo is None:
                vu = vu.replace(tzinfo=timezone.utc)
            if utcnow() > vu:
                raise HTTPException(status_code=400, detail="El código promocional ha expirado.")
        if promo.applicable_plans and target_plan_code.upper() not in promo.applicable_plans:
            raise HTTPException(
                status_code=400,
                detail=f"El cupón {clean_code} no aplica para el plan {target_plan_code}.",
            )
        return promo

    async def checkout_subscription(
        self,
        db: AsyncSession,
        user: SaasUser,
        target_plan_code: str,
        billing_cycle: str = "monthly",
        promo_code: Optional[str] = None,
        payment_method_brand: str = "visa",
        payment_method_last4: str = "4242",
        external_tx_id: Optional[str] = None,
        ip_address: str = "127.0.0.1",
        payment_gateway: str = "stripe",
    ) -> Dict[str, Any]:
        """
        Processes a subscription purchase, upgrade, or downgrade.
        - Strictly blocks purchasing CREATOR.
        - Always reads plan prices from the database (`SaasPlan`), never from the client request!
        - Enforces idempotency via `external_tx_id` so duplicate requests never charge twice.
        - Never stores raw credit card numbers (only tokenized brand + 4 digits).
        - Supports Stripe (international card), Wompi/MercadoPago (Nequi/PSE/Bancolombia), PayPal, and Direct Transfer.
        """
        await self.ensure_seeded(db)
        plan_code_up = (target_plan_code or "").strip().upper()

        # CRITICAL: CREATOR plan can NEVER be purchased or acquired via checkout
        if plan_code_up == "CREATOR":
            await self.log_audit(
                db=db,
                action="blocked_creator_plan_purchase_attempt",
                actor_user=user,
                target_user_id=user.id,
                resource_type="subscription",
                ip_address=ip_address,
                severity="security",
            )
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operación prohibida: El plan CREATOR es exclusivo del propietario original y no es comercializable.",
            )

        if user.role == "CREATOR" and user.id == CREATOR_USER_ID:
            raise HTTPException(
                status_code=400,
                detail="La cuenta CREATOR ya posee privilegios soberanos permanentes e ilimitados.",
            )

        target_plan = await self.get_plan(db, plan_code_up)
        if not target_plan or target_plan.code != plan_code_up:
            raise HTTPException(status_code=404, detail=f"El plan '{plan_code_up}' no existe.")

        cycle = billing_cycle.lower() if billing_cycle in {"monthly", "annual"} else "monthly"
        gw_clean = (payment_gateway or "stripe").strip().lower()
        if gw_clean not in {"stripe", "wompi_pse_nequi", "paypal", "direct_transfer"}:
            gw_clean = "stripe"

        # Check idempotency if external_tx_id is provided
        tx_id = external_tx_id or f"tx_{uuid.uuid4().hex[:18]}"
        dup_res = await db.execute(select(SaasPayment).where(SaasPayment.external_tx_id == tx_id))
        existing_payment = dup_res.scalars().first()
        if existing_payment:
            return {
                "ok": True,
                "idempotent_duplicate": True,
                "payment_id": existing_payment.id,
                "plan_code": existing_payment.plan_code,
                "amount_usd": existing_payment.amount_usd,
                "message": "Transacción previamente procesada (idempotencia garantizada).",
            }

        # Calculate price from DB truth
        base_price = target_plan.price_annual_usd if cycle == "annual" else target_plan.price_monthly_usd
        discount_pct = 0.0
        discount_usd = 0.0
        bonus_credits = 0
        applied_promo_code: Optional[str] = None

        if promo_code and promo_code.strip():
            promo = await self.validate_promo_code(db, promo_code, plan_code_up)
            discount_pct = promo.discount_pct
            discount_usd = round((base_price * (discount_pct / 100.0)) + promo.discount_fixed_usd, 2)
            discount_usd = min(base_price, discount_usd)
            bonus_credits = promo.bonus_credits
            applied_promo_code = promo.code
            promo.current_uses += 1

        final_amount = round(max(0.0, base_price - discount_usd), 2)
        safe_last4 = re.sub(r"\D", "", payment_method_last4 or "4242")[-4:] or "4242"

        gw_cfg = self.get_payment_gateways_config(include_secrets=False)
        trm_usd_cop = float(gw_cfg.get("trm_usd_cop") or 4200.0)
        final_amount_cop = int(round(final_amount * trm_usd_cop))
        gw_info = (gw_cfg.get("gateways") or {}).get(gw_clean, {})
        external_payment_link = ((gw_info.get("payment_links") or {}).get(target_plan.code) or "").strip()

        gw_labels = {
            "stripe": f"{(payment_method_brand or 'VISA').upper()} •••• {safe_last4} (Stripe)",
            "wompi_pse_nequi": f"PSE / NEQUI •••• {safe_last4} (Wompi Colombia)",
            "paypal": f"PAYPAL •••• {safe_last4} (Express)",
            "direct_transfer": f"TRANSFERENCIA NEQUI/BANCOLOMBIA •••• {safe_last4}",
        }
        method_summary = "Sin tarjeta requerida" if target_plan.code == "FREE" else gw_labels.get(gw_clean, f"{payment_method_brand.upper()} •••• {safe_last4}")

        # Record Payment
        payment = SaasPayment(
            id=f"pay_{uuid.uuid4().hex[:16]}",
            user_id=user.id,
            plan_code=target_plan.code,
            amount_usd=final_amount,
            currency="USD",
            status="succeeded",
            provider=gw_clean,
            external_tx_id=tx_id,
            payment_method_brand=(payment_method_brand or gw_clean)[:30],
            payment_method_last4=safe_last4,
            metadata_json={
                "billing_cycle": cycle,
                "promo_code": applied_promo_code,
                "payment_gateway": gw_clean,
                "amount_cop": final_amount_cop,
                "trm_usd_cop": trm_usd_cop,
                "external_payment_link": external_payment_link,
            },
        )
        db.add(payment)

        # Create or update Subscription
        sub_res = await db.execute(
            select(SaasSubscription).where(SaasSubscription.user_id == user.id).order_by(desc(SaasSubscription.created_at))
        )
        sub = sub_res.scalars().first()
        period_days = 365 if cycle == "annual" else 30
        now_dt = utcnow()
        if not sub:
            sub = SaasSubscription(
                id=f"sub_{uuid.uuid4().hex[:14]}",
                user_id=user.id,
                plan_code=target_plan.code,
                billing_cycle=cycle,
                status="active",
                price_usd=final_amount,
                discount_pct=discount_pct,
                promo_code_used=applied_promo_code,
                auto_renew=True,
                cancel_at_period_end=False,
                current_period_start=now_dt,
                current_period_end=now_dt + timedelta(days=period_days),
                payment_method_summary=method_summary,
            )
            db.add(sub)
        else:
            sub.plan_code = target_plan.code
            sub.billing_cycle = cycle
            sub.status = "active"
            sub.price_usd = final_amount
            sub.discount_pct = discount_pct
            sub.promo_code_used = applied_promo_code
            sub.auto_renew = True
            sub.cancel_at_period_end = False
            sub.grace_period_ends_at = None
            sub.current_period_start = now_dt
            sub.current_period_end = now_dt + timedelta(days=period_days)
            sub.payment_method_summary = method_summary
            sub.updated_at = now_dt

        payment.subscription_id = sub.id

        # Generate Invoice
        inv_num = f"INV-{now_dt.strftime('%Y%m')}-{secrets.token_hex(3).upper()}"
        invoice = SaasInvoice(
            id=f"inv_{uuid.uuid4().hex[:14]}",
            invoice_number=inv_num,
            user_id=user.id,
            subscription_id=sub.id,
            payment_id=payment.id,
            plan_code=target_plan.code,
            billing_cycle=cycle,
            subtotal_usd=base_price,
            discount_usd=discount_usd,
            tax_usd=0.0,
            total_usd=final_amount,
            currency="USD",
            status="paid",
            line_items=[
                {
                    "description": f"Suscripción {target_plan.name} ({cycle}) vía {gw_clean.upper()}",
                    "subtotal_usd": base_price,
                    "discount_usd": discount_usd,
                    "total_usd": final_amount,
                    "total_cop": final_amount_cop,
                    "trm_usd_cop": trm_usd_cop,
                    "payment_gateway": gw_clean,
                }
            ],
            issued_at=now_dt,
            paid_at=now_dt,
        )
        db.add(invoice)

        # Upgrade user's plan_code & allocate plan credits
        old_plan = user.plan_code
        user.plan_code = target_plan.code
        user.updated_at = now_dt

        balance = await self.get_or_create_credit_balance(db, user)
        balance.monthly_credits_allocated = target_plan.monthly_credits
        balance.credits_used = 0
        balance.bonus_credits += bonus_credits
        balance.is_quota_blocked = False
        balance.alert_80_sent = False
        balance.period_reset_at = now_dt + timedelta(days=period_days)

        await self.log_audit(
            db=db,
            action="subscription_plan_changed",
            actor_user=user,
            target_user_id=user.id,
            resource_type="subscription",
            resource_id=sub.id,
            ip_address=ip_address,
            details={
                "old_plan": old_plan,
                "new_plan": target_plan.code,
                "billing_cycle": cycle,
                "payment_gateway": gw_clean,
                "amount_usd": final_amount,
                "amount_cop": final_amount_cop,
                "promo_code": applied_promo_code,
            },
        )
        await db.commit()

        return {
            "ok": True,
            "idempotent_duplicate": False,
            "payment_gateway": gw_clean,
            "external_payment_link": external_payment_link,
            "subscription": {
                "id": sub.id,
                "plan_code": sub.plan_code,
                "billing_cycle": sub.billing_cycle,
                "status": sub.status,
                "price_usd": sub.price_usd,
                "price_cop": final_amount_cop,
                "discount_pct": sub.discount_pct,
                "current_period_end": _iso(sub.current_period_end),
                "payment_method_summary": sub.payment_method_summary,
            },
            "invoice": {
                "id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "subtotal_usd": invoice.subtotal_usd,
                "discount_usd": invoice.discount_usd,
                "total_usd": invoice.total_usd,
                "total_cop": final_amount_cop,
                "trm_usd_cop": trm_usd_cop,
                "payment_gateway": gw_clean,
                "status": invoice.status,
                "issued_at": _iso(invoice.issued_at),
            },
            "payment_id": payment.id,
            "user": self.serialize_user(user, target_plan, balance),
        }

    async def cancel_subscription(
        self,
        db: AsyncSession,
        user: SaasUser,
        immediate: bool = False,
    ) -> Dict[str, Any]:
        if user.plan_code == "CREATOR":
            raise HTTPException(status_code=400, detail="El plan CREATOR no es una suscripción cancelable.")

        sub_res = await db.execute(
            select(SaasSubscription).where(SaasSubscription.user_id == user.id).order_by(desc(SaasSubscription.created_at))
        )
        sub = sub_res.scalars().first()
        if not sub:
            raise HTTPException(status_code=404, detail="No tienes una suscripción activa.")

        now_dt = utcnow()
        sub.auto_renew = False
        sub.canceled_at = now_dt
        if immediate:
            sub.status = "canceled"
            sub.plan_code = "FREE"
            user.plan_code = "FREE"
            free_plan = await self.get_plan(db, "FREE")
            bal = await self.get_or_create_credit_balance(db, user)
            bal.monthly_credits_allocated = free_plan.monthly_credits
        else:
            sub.cancel_at_period_end = True

        await self.log_audit(
            db=db,
            action="subscription_canceled",
            actor_user=user,
            target_user_id=user.id,
            resource_type="subscription",
            resource_id=sub.id,
            details={"immediate": immediate},
        )
        await db.commit()
        return {
            "ok": True,
            "status": sub.status,
            "cancel_at_period_end": sub.cancel_at_period_end,
            "current_period_end": _iso(sub.current_period_end),
            "current_plan": user.plan_code,
        }

    async def list_billing_history(self, db: AsyncSession, user: SaasUser) -> Dict[str, Any]:
        sub_res = await db.execute(
            select(SaasSubscription).where(SaasSubscription.user_id == user.id).order_by(desc(SaasSubscription.created_at))
        )
        sub = sub_res.scalars().first()

        pay_res = await db.execute(
            select(SaasPayment).where(SaasPayment.user_id == user.id).order_by(desc(SaasPayment.created_at))
        )
        payments = pay_res.scalars().all()

        inv_res = await db.execute(
            select(SaasInvoice).where(SaasInvoice.user_id == user.id).order_by(desc(SaasInvoice.issued_at))
        )
        invoices = inv_res.scalars().all()

        return {
            "ok": True,
            "subscription": (
                {
                    "id": sub.id,
                    "plan_code": sub.plan_code,
                    "billing_cycle": sub.billing_cycle,
                    "status": sub.status,
                    "price_usd": sub.price_usd,
                    "auto_renew": sub.auto_renew,
                    "cancel_at_period_end": sub.cancel_at_period_end,
                    "current_period_start": _iso(sub.current_period_start),
                    "current_period_end": _iso(sub.current_period_end),
                    "grace_period_ends_at": _iso(sub.grace_period_ends_at),
                    "payment_method_summary": sub.payment_method_summary,
                }
                if sub
                else None
            ),
            "payments": [
                {
                    "id": p.id,
                    "plan_code": p.plan_code,
                    "amount_usd": p.amount_usd,
                    "currency": p.currency,
                    "status": p.status,
                    "provider": p.provider,
                    "external_tx_id": p.external_tx_id,
                    "payment_method": f"{p.payment_method_brand.upper()} •••• {p.payment_method_last4}",
                    "refunded_amount_usd": p.refunded_amount_usd,
                    "created_at": _iso(p.created_at),
                }
                for p in payments
            ],
            "invoices": [
                {
                    "id": inv.id,
                    "invoice_number": inv.invoice_number,
                    "plan_code": inv.plan_code,
                    "billing_cycle": inv.billing_cycle,
                    "subtotal_usd": inv.subtotal_usd,
                    "discount_usd": inv.discount_usd,
                    "total_usd": inv.total_usd,
                    "status": inv.status,
                    "line_items": inv.line_items or [],
                    "issued_at": _iso(inv.issued_at),
                }
                for inv in invoices
            ],
        }

    async def process_payment_webhook(
        self,
        db: AsyncSession,
        raw_body: bytes,
        signature_header: Optional[str],
        event_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Stripe-compatible webhook processor with HMAC signature validation and idempotency.
        Handles payment success, failed payments (activating a 5-day grace period), and cancellations.
        """
        await self.ensure_seeded(db)
        webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "") or ""
        if webhook_secret:
            if not signature_header:
                raise HTTPException(status_code=400, detail="Falta cabecera de firma del webhook (Stripe-Signature).")
            expected_sig = hmac.new(
                webhook_secret.encode("utf-8"),
                raw_body,
                hashlib.sha256,
            ).hexdigest()
            if not hmac.compare_digest(signature_header.strip(), expected_sig):
                raise HTTPException(status_code=400, detail="Firma criptográfica del webhook inválida.")

        event_id = str(event_payload.get("id") or "").strip()
        event_type = str(event_payload.get("type") or "").strip()
        data_obj = event_payload.get("data", {}).get("object", {}) or {}

        if not event_id or not event_type:
            raise HTTPException(status_code=400, detail="Payload de webhook incompleto.")

        # Idempotency check on event_id
        dup = await db.execute(select(SaasPayment).where(SaasPayment.external_tx_id == event_id))
        if dup.scalars().first():
            return {"ok": True, "idempotent_duplicate": True, "event_id": event_id}

        user_id = str(data_obj.get("user_id") or data_obj.get("client_reference_id") or "").strip()
        target_plan = str(data_obj.get("plan_code") or "PRO").strip().upper()
        if target_plan == "CREATOR":
            raise HTTPException(status_code=403, detail="Webhook rechazado: Plan CREATOR no permitido.")

        usr_res = await db.execute(select(SaasUser).where(SaasUser.id == user_id))
        user = usr_res.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario del webhook no encontrado.")

        if event_type in {"checkout.session.completed", "invoice.payment_succeeded"}:
            res = await self.checkout_subscription(
                db=db,
                user=user,
                target_plan_code=target_plan,
                billing_cycle=str(data_obj.get("billing_cycle") or "monthly"),
                external_tx_id=event_id,
            )
            return {"ok": True, "idempotent_duplicate": res.get("idempotent_duplicate", False), "event_type": event_type}

        elif event_type == "invoice.payment_failed":
            # Activate 5-day grace period and record failed payment
            failed_pay = SaasPayment(
                id=f"pay_{uuid.uuid4().hex[:16]}",
                user_id=user.id,
                plan_code=target_plan,
                amount_usd=float(data_obj.get("amount_usd") or 0.0),
                status="failed",
                provider="stripe",
                external_tx_id=event_id,
                failure_reason=str(data_obj.get("failure_reason") or "Fondos insuficientes / tarjeta rechazada"),
            )
            db.add(failed_pay)

            sub_res = await db.execute(
                select(SaasSubscription).where(SaasSubscription.user_id == user.id).order_by(desc(SaasSubscription.created_at))
            )
            sub = sub_res.scalars().first()
            grace_end = utcnow() + timedelta(days=5)
            if sub:
                sub.status = "past_due"
                sub.grace_period_ends_at = grace_end

            await db.commit()
            return {
                "ok": True,
                "event_type": event_type,
                "status": "past_due",
                "grace_period_ends_at": _iso(grace_end),
            }

        return {"ok": True, "event_type": event_type, "handled": True}

    # ==========================================================================
    # 6. EXCLUSIVE CREATOR SUPERADMIN CONTROL CENTER (SEÑOR SANTIAGO ONLY)
    # ==========================================================================

    async def get_creator_dashboard(self, db: AsyncSession, creator: SaasUser) -> Dict[str, Any]:
        """
        Computes executive SaaS telemetry for Señor Santiago's CREATOR dashboard:
        - Registered, active, suspended, free vs. paid users
        - Active & canceled subscriptions
        - Monthly Recurring Revenue (MRR), Annual Run Rate (ARR), ARPU
        - Total estimated API costs & Net Estimated Profit
        - Breakdown by plan tier
        """
        all_users = (await db.execute(select(SaasUser))).scalars().all()
        total_users = len(all_users)
        active_users = sum(1 for u in all_users if u.is_active and not u.is_suspended)
        suspended_users = sum(1 for u in all_users if u.is_suspended)
        free_users = sum(1 for u in all_users if u.plan_code == "FREE" and u.is_active)
        paid_users = sum(1 for u in all_users if u.plan_code in PUBLIC_PURCHASABLE_PLANS and u.is_active)

        all_subs = (await db.execute(select(SaasSubscription))).scalars().all()
        active_subs = [s for s in all_subs if s.status in {"active", "trialing"}]
        canceled_subs = [s for s in all_subs if s.status == "canceled" or s.cancel_at_period_end]

        mrr_usd = 0.0
        for s in active_subs:
            if s.plan_code in PUBLIC_PURCHASABLE_PLANS:
                if s.billing_cycle == "annual":
                    mrr_usd += round(s.price_usd / 12.0, 2)
                else:
                    mrr_usd += s.price_usd

        arr_usd = round(mrr_usd * 12.0, 2)
        arpu_usd = round(mrr_usd / paid_users, 2) if paid_users > 0 else 0.0

        # Total API cost across all usage records
        cost_res = await db.execute(select(func.sum(SaasUsageRecord.estimated_cost_usd)))
        total_api_cost_usd = round(float(cost_res.scalar() or 0.0), 4)

        tok_res = await db.execute(select(func.sum(SaasUsageRecord.total_tokens)))
        total_tokens_consumed = int(tok_res.scalar() or 0)

        rev_res = await db.execute(
            select(func.sum(SaasPayment.amount_usd - SaasPayment.refunded_amount_usd)).where(
                SaasPayment.status == "succeeded"
            )
        )
        total_collected_revenue_usd = round(float(rev_res.scalar() or 0.0), 2)
        estimated_profit_usd = round(mrr_usd - total_api_cost_usd, 2)

        plan_distribution: Dict[str, int] = {}
        for u in all_users:
            if u.is_active:
                plan_distribution[u.plan_code] = plan_distribution.get(u.plan_code, 0) + 1

        # Recent audit logs
        logs_res = await db.execute(select(SaasAuditLog).order_by(desc(SaasAuditLog.created_at)).limit(25))
        recent_logs = [
            {
                "id": l.id,
                "actor_email": l.actor_email,
                "actor_role": l.actor_role,
                "target_user_id": l.target_user_id,
                "action": l.action,
                "resource_type": l.resource_type,
                "severity": l.severity,
                "details": l.details or {},
                "created_at": _iso(l.created_at),
            }
            for l in logs_res.scalars().all()
        ]

        return {
            "ok": True,
            "creator_owner": creator.full_name,
            "metrics": {
                "total_users": total_users,
                "active_users": active_users,
                "suspended_users": suspended_users,
                "free_users": free_users,
                "paid_users": paid_users,
                "active_subscriptions": len(active_subs),
                "canceled_subscriptions": len(canceled_subs),
                "mrr_usd": round(mrr_usd, 2),
                "arr_usd": arr_usd,
                "arpu_usd": arpu_usd,
                "total_collected_revenue_usd": total_collected_revenue_usd,
                "total_api_cost_usd": total_api_cost_usd,
                "estimated_monthly_profit_usd": estimated_profit_usd,
                "total_tokens_consumed": total_tokens_consumed,
                "plan_distribution": plan_distribution,
            },
            "recent_audit_logs": recent_logs,
        }

    async def admin_list_users(
        self,
        db: AsyncSession,
        search: Optional[str] = None,
        plan_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        conditions = []
        if search and search.strip():
            q = f"%{search.strip()}%"
            conditions.append(or_(SaasUser.email.ilike(q), SaasUser.full_name.ilike(q)))
        if plan_filter and plan_filter.strip():
            conditions.append(SaasUser.plan_code == plan_filter.strip().upper())

        stmt = select(SaasUser).order_by(desc(SaasUser.created_at))
        if conditions:
            stmt = stmt.where(and_(*conditions))

        users = (await db.execute(stmt)).scalars().all()
        out = []
        for u in users:
            plan = await self.get_plan(db, u.plan_code)
            bal = await self.get_or_create_credit_balance(db, u)
            out.append(self.serialize_user(u, plan, bal))
        return {"ok": True, "total": len(out), "users": out}

    async def admin_update_user(
        self,
        db: AsyncSession,
        creator: SaasUser,
        target_user_id: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        res = await db.execute(select(SaasUser).where(SaasUser.id == target_user_id))
        target = res.scalars().first()
        if not target:
            raise HTTPException(status_code=404, detail="Usuario objetivo no encontrado.")

        # Protect CREATOR account from accidental downgrade or suspension
        if target.id == CREATOR_USER_ID:
            if updates.get("is_suspended") or (updates.get("plan_code") and updates["plan_code"] != "CREATOR"):
                raise HTTPException(status_code=403, detail="No se puede suspender ni degradar la cuenta CREATOR principal.")

        if "plan_code" in updates and updates["plan_code"]:
            new_plan_code = str(updates["plan_code"]).upper()
            if new_plan_code == "CREATOR" and target.id != CREATOR_USER_ID:
                raise HTTPException(status_code=403, detail="El plan CREATOR es exclusivo del propietario original.")
            plan_obj = await self.get_plan(db, new_plan_code)
            target.plan_code = plan_obj.code
            bal = await self.get_or_create_credit_balance(db, target)
            bal.monthly_credits_allocated = plan_obj.monthly_credits
            bal.is_quota_blocked = False

        if "is_suspended" in updates and updates["is_suspended"] is not None:
            target.is_suspended = bool(updates["is_suspended"])
            target.suspension_reason = str(updates.get("suspension_reason") or "Suspendido por el administrador CREATOR") if target.is_suspended else None

        if "bonus_credits" in updates and updates["bonus_credits"] is not None:
            bal = await self.get_or_create_credit_balance(db, target)
            bal.bonus_credits = max(0, int(updates["bonus_credits"]))

        target.updated_at = utcnow()
        await self.log_audit(
            db=db,
            action="creator_updated_user",
            actor_user=creator,
            target_user_id=target.id,
            resource_type="user",
            resource_id=target.id,
            details=updates,
        )
        await db.commit()
        plan = await self.get_plan(db, target.plan_code)
        bal = await self.get_or_create_credit_balance(db, target)
        return {"ok": True, "user": self.serialize_user(target, plan, bal)}

    async def admin_update_plan(
        self,
        db: AsyncSession,
        creator: SaasUser,
        plan_code: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        res = await db.execute(select(SaasPlan).where(SaasPlan.code == plan_code.upper()))
        plan = res.scalars().first()
        if not plan:
            raise HTTPException(status_code=404, detail="Plan no encontrado.")

        for field in [
            "name",
            "description",
            "price_monthly_usd",
            "price_annual_usd",
            "max_brains",
            "max_conversations",
            "daily_message_limit",
            "monthly_token_limit",
            "monthly_credits",
            "max_memories",
            "trial_days",
            "is_active",
        ]:
            if field in updates and updates[field] is not None:
                setattr(plan, field, updates[field])

        if "features" in updates and isinstance(updates["features"], dict):
            merged = dict(plan.features or {})
            merged.update(updates["features"])
            plan.features = merged

        if "allowed_skill_tiers" in updates and isinstance(updates["allowed_skill_tiers"], list):
            plan.allowed_skill_tiers = updates["allowed_skill_tiers"]

        # Never allow CREATOR plan to become public/commercializable
        if plan.code == "CREATOR":
            plan.is_public = False
            plan.is_commercializable = False

        plan.updated_at = utcnow()
        await self.log_audit(
            db=db,
            action="creator_updated_plan",
            actor_user=creator,
            resource_type="plan",
            resource_id=plan.code,
            details=updates,
        )
        await db.commit()
        return {"ok": True, "plan": self.serialize_plan(plan)}

    async def admin_upsert_skill(
        self,
        db: AsyncSession,
        creator: SaasUser,
        skill_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        code = str(skill_data.get("code") or "").strip().lower()
        if not code:
            raise HTTPException(status_code=400, detail="El código de la skill es obligatorio.")

        res = await db.execute(select(SaasSkill).where(SaasSkill.code == code))
        sk = res.scalars().first()
        if not sk:
            sk = SaasSkill(
                id=f"sk_{uuid.uuid4().hex[:12]}",
                code=code,
                name=str(skill_data.get("name") or code),
                description=str(skill_data.get("description") or ""),
                category=str(skill_data.get("category") or "general"),
                version=str(skill_data.get("version") or "2.0.0"),
                status=str(skill_data.get("status") or "active"),
                tier=str(skill_data.get("tier") or "basic"),
                min_plan_level=int(skill_data.get("min_plan_level") or 0),
                compatible_plans=skill_data.get("compatible_plans") or ["FREE", "STARTER", "PRO", "BUSINESS", "ENTERPRISE", "CREATOR"],
                estimated_credit_cost=int(skill_data.get("estimated_credit_cost") or 1),
                created_by_user_id=creator.id,
            )
            db.add(sk)
        else:
            for k in ["name", "description", "category", "version", "status", "tier", "min_plan_level", "compatible_plans", "estimated_credit_cost"]:
                if k in skill_data and skill_data[k] is not None:
                    setattr(sk, k, skill_data[k])
            sk.updated_at = utcnow()

        await self.log_audit(
            db=db,
            action="creator_upserted_skill",
            actor_user=creator,
            resource_type="skill",
            resource_id=code,
            details=skill_data,
        )
        await db.commit()
        return {
            "ok": True,
            "skill": {
                "id": sk.id,
                "code": sk.code,
                "name": sk.name,
                "description": sk.description,
                "category": sk.category,
                "tier": sk.tier,
                "status": sk.status,
                "min_plan_level": sk.min_plan_level,
                "estimated_credit_cost": sk.estimated_credit_cost,
            },
        }

    async def admin_issue_refund(
        self,
        db: AsyncSession,
        creator: SaasUser,
        payment_id: str,
        reason: str = "Reembolso autorizado por Superadmin CREATOR",
    ) -> Dict[str, Any]:
        res = await db.execute(select(SaasPayment).where(SaasPayment.id == payment_id))
        payment = res.scalars().first()
        if not payment:
            raise HTTPException(status_code=404, detail="Pago no encontrado.")
        if payment.status == "refunded":
            raise HTTPException(status_code=400, detail="Este pago ya fue reembolsado.")

        payment.status = "refunded"
        payment.refunded_amount_usd = payment.amount_usd
        payment.refund_reason = reason

        inv_res = await db.execute(select(SaasInvoice).where(SaasInvoice.payment_id == payment.id))
        inv = inv_res.scalars().first()
        if inv:
            inv.status = "refunded"

        await self.log_audit(
            db=db,
            action="creator_issued_refund",
            actor_user=creator,
            target_user_id=payment.user_id,
            resource_type="payment",
            resource_id=payment.id,
            details={"amount_usd": payment.amount_usd, "reason": reason},
        )
        await db.commit()
        return {
            "ok": True,
            "payment_id": payment.id,
            "status": payment.status,
            "refunded_amount_usd": payment.refunded_amount_usd,
        }

    # ==========================================================================
    # 7. FIREBASE PROJECT LINKING & FIREBASE AUTHENTICATION BRIDGE
    # ==========================================================================

    def get_firebase_config(self) -> Dict[str, Any]:
        """Returns the linked Firebase project configuration from data/firebase_config.json or .env."""
        cfg_file = settings.DATA_DIR / "firebase_config.json"
        saved: Dict[str, Any] = {}
        if cfg_file.exists():
            try:
                saved = json.loads(cfg_file.read_text(encoding="utf-8"))
            except Exception:
                saved = {}

        project_id = str(saved.get("projectId") or getattr(settings, "FIREBASE_PROJECT_ID", "liseth-saas-ai") or "liseth-saas-ai").strip()
        api_key = str(saved.get("apiKey") or getattr(settings, "FIREBASE_API_KEY", "") or "").strip()
        auth_domain = str(saved.get("authDomain") or getattr(settings, "FIREBASE_AUTH_DOMAIN", "") or f"{project_id}.firebaseapp.com").strip()
        storage_bucket = str(saved.get("storageBucket") or getattr(settings, "FIREBASE_STORAGE_BUCKET", "") or f"{project_id}.firebasestorage.app").strip()
        messaging_sender_id = str(saved.get("messagingSenderId") or getattr(settings, "FIREBASE_MESSAGING_SENDER_ID", "") or "108492039481").strip()
        app_id = str(saved.get("appId") or getattr(settings, "FIREBASE_APP_ID", "") or f"1:{messaging_sender_id}:web:lisethsaas2026").strip()

        return {
            "ok": True,
            "isLinked": True,
            "hasClientSdkKey": bool(api_key),
            "projectId": project_id,
            "apiKey": api_key,
            "authDomain": auth_domain,
            "storageBucket": storage_bucket,
            "messagingSenderId": messaging_sender_id,
            "appId": app_id,
            "providers": ["emailPassword", "google.com"],
        }

    def save_firebase_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Saves and links a Firebase project configuration to data/firebase_config.json and .firebaserc."""
        current = self.get_firebase_config()
        project_id = str(config_data.get("projectId") or current["projectId"]).strip() or "liseth-saas-ai"
        updated = {
            "projectId": project_id,
            "apiKey": str(config_data.get("apiKey") if config_data.get("apiKey") is not None else current["apiKey"]).strip(),
            "authDomain": str(config_data.get("authDomain") or f"{project_id}.firebaseapp.com").strip(),
            "storageBucket": str(config_data.get("storageBucket") or f"{project_id}.firebasestorage.app").strip(),
            "messagingSenderId": str(config_data.get("messagingSenderId") or current["messagingSenderId"]).strip(),
            "appId": str(config_data.get("appId") or current["appId"]).strip(),
        }
        cfg_file = settings.DATA_DIR / "firebase_config.json"
        cfg_file.write_text(json.dumps(updated, indent=2), encoding="utf-8")

        # Also keep .firebaserc in sync
        try:
            firebaserc = settings.BASE_DIR / ".firebaserc"
            firebaserc.write_text(
                json.dumps({"projects": {"default": project_id}}, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

        return self.get_firebase_config()

    # ==========================================================================
    # 7. PAYMENT GATEWAYS CONFIGURATION & LIVE PLAN SALES QUOTE ENGINE
    # ==========================================================================

    def get_payment_gateways_config(self, include_secrets: bool = False) -> Dict[str, Any]:
        """
        Returns the active payment gateways configuration for selling SaaS plans.
        Reads from `data/payment_gateways_config.json` (with mtime cache) merged with `.env` defaults.
        """
        cfg_file = settings.DATA_DIR / "payment_gateways_config.json"
        saved: Dict[str, Any] = {}
        if cfg_file.exists():
            try:
                mtime = cfg_file.stat().st_mtime_ns
                if getattr(self, "_pay_cfg_mtime", None) == mtime and getattr(self, "_pay_cfg_raw", None) is not None:
                    saved = self._pay_cfg_raw
                else:
                    saved = json.loads(cfg_file.read_text(encoding="utf-8"))
                    self._pay_cfg_mtime = mtime
                    self._pay_cfg_raw = saved
            except Exception:
                saved = {}

        trm_usd_cop = float(saved.get("trm_usd_cop") or getattr(settings, "TRM_USD_COP", 4200.0) or 4200.0)
        saved_gws = saved.get("gateways") or {}

        # 1. Stripe (International Credit/Debit Cards)
        st_saved = saved_gws.get("stripe") or {}
        st_pub = str(st_saved.get("publishable_key") or getattr(settings, "STRIPE_PUBLISHABLE_KEY", "")).strip()
        st_sec = str(st_saved.get("secret_key") or getattr(settings, "STRIPE_SECRET_KEY", "")).strip()
        st_wh = str(st_saved.get("webhook_secret") or getattr(settings, "STRIPE_WEBHOOK_SECRET", "")).strip()
        st_links = st_saved.get("payment_links") or {"STARTER": "", "PRO": "", "BUSINESS": "", "ENTERPRISE": ""}

        # 2. Wompi / MercadoPago (PSE, Nequi, Bancolombia, Tarjetas Colombia)
        wp_saved = saved_gws.get("wompi_pse_nequi") or {}
        wp_pub = str(wp_saved.get("wompi_public_key") or getattr(settings, "WOMPI_PUBLIC_KEY", "")).strip()
        wp_sec = str(wp_saved.get("wompi_integrity_secret") or getattr(settings, "WOMPI_INTEGRITY_SECRET", "")).strip()
        mp_pub = str(wp_saved.get("mercadopago_public_key") or getattr(settings, "MERCADOPAGO_PUBLIC_KEY", "")).strip()
        mp_sec = str(wp_saved.get("mercadopago_access_token") or getattr(settings, "MERCADOPAGO_ACCESS_TOKEN", "")).strip()
        wp_links = wp_saved.get("payment_links") or {"STARTER": "", "PRO": "", "BUSINESS": "", "ENTERPRISE": ""}

        # 3. PayPal Express Checkout
        pp_saved = saved_gws.get("paypal") or {}
        pp_cid = str(pp_saved.get("client_id") or getattr(settings, "PAYPAL_CLIENT_ID", "")).strip()
        pp_email = str(pp_saved.get("business_email") or getattr(settings, "PAYPAL_BUSINESS_EMAIL", "")).strip()
        pp_links = pp_saved.get("payment_links") or {"STARTER": "", "PRO": "", "BUSINESS": "", "ENTERPRISE": ""}

        # 4. Direct Transfer (Nequi / Bancolombia / Llave Bre-B / WhatsApp)
        dt_saved = saved_gws.get("direct_transfer") or {}
        raw_nequi = str(dt_saved.get("nequi_number") or "").strip()
        if not raw_nequi or raw_nequi == "300 000 0000":
            nequi_num = getattr(settings, "NEQUI_NUMBER", "3122376474") or "3122376474"
        else:
            nequi_num = raw_nequi
        bancolombia_acc = str(
            dt_saved.get("bancolombia_account") or getattr(settings, "BANCOLOMBIA_ACCOUNT", "Ahorros Bancolombia 000-000000-00")
        ).strip()
        bre_b_key = str(dt_saved.get("bre_b_key") or getattr(settings, "BRE_B_KEY", "@santiagoliseth")).strip()
        raw_wa = str(dt_saved.get("whatsapp_sales_phone") or "").strip()
        if not raw_wa or raw_wa in {"+57 300 000 0000", "+573000000000"}:
            wa_phone = getattr(settings, "WHATSAPP_SALES_PHONE", "+573122376474") or "+573122376474"
        else:
            wa_phone = raw_wa
        account_holder = str(dt_saved.get("account_holder") or "Santiago (Propietario & Creador Liseth AI)").strip()
        dt_instructions = str(
            dt_saved.get("instructions")
            or "Realiza la transferencia por Nequi, Bancolombia o Llave Bre-B por el valor en COP e ingresa los últimos 4 dígitos del comprobante para activar tu plan al instante."
        ).strip()

        config: Dict[str, Any] = {
            "ok": True,
            "trm_usd_cop": trm_usd_cop,
            "currency_primary": "USD",
            "currency_secondary": "COP",
            "annual_discount_pct": 20.0,
            "config_file_path": str(cfg_file),
            "env_file_path": str(settings.BASE_DIR / ".env"),
            "gateways": {
                "stripe": {
                    "id": "stripe",
                    "enabled": bool(st_saved.get("enabled", True)),
                    "label": "Tarjeta Crédito / Débito Internacional (Stripe)",
                    "short_label": "💳 Tarjeta (Stripe)",
                    "icon": "💳",
                    "publishable_key": st_pub,
                    "configured": bool(st_pub or any(st_links.values())),
                    "payment_links": st_links,
                    "supported_methods": ["Visa", "Mastercard", "Amex", "Apple Pay", "Google Pay"],
                },
                "wompi_pse_nequi": {
                    "id": "wompi_pse_nequi",
                    "enabled": bool(wp_saved.get("enabled", True)),
                    "label": "PSE / Nequi / Bancolombia (Wompi / MercadoPago)",
                    "short_label": "🏦 PSE / Nequi (Wompi)",
                    "icon": "🏦",
                    "wompi_public_key": wp_pub,
                    "mercadopago_public_key": mp_pub,
                    "configured": bool(wp_pub or mp_pub or any(wp_links.values())),
                    "payment_links": wp_links,
                    "supported_methods": ["PSE Todos los Bancos", "Nequi Push", "Boton Bancolombia", "DaviPlata"],
                },
                "paypal": {
                    "id": "paypal",
                    "enabled": bool(pp_saved.get("enabled", True)),
                    "label": "PayPal Express Checkout Internacional",
                    "short_label": "🅿️ PayPal",
                    "icon": "🅿️",
                    "client_id": pp_cid,
                    "business_email": pp_email,
                    "configured": bool(pp_cid or pp_email or any(pp_links.values())),
                    "payment_links": pp_links,
                    "supported_methods": ["Saldo PayPal", "Tarjeta vinculada a PayPal"],
                },
                "direct_transfer": {
                    "id": "direct_transfer",
                    "enabled": bool(dt_saved.get("enabled", True)),
                    "label": "Transferencia Directa (Nequi / Bancolombia / Llave Bre-B)",
                    "short_label": "📲 Nequi / Bancolombia Directo",
                    "icon": "📲",
                    "nequi_number": nequi_num,
                    "bancolombia_account": bancolombia_acc,
                    "bre_b_key": bre_b_key,
                    "account_holder": account_holder,
                    "whatsapp_sales_phone": wa_phone,
                    "instructions": dt_instructions,
                    "configured": bool(nequi_num or bancolombia_acc or bre_b_key),
                    "supported_methods": ["Nequi", "Bancolombia", "Llave Bre-B", "Transfiya"],
                },
            },
        }

        if include_secrets:
            config["gateways"]["stripe"]["secret_key"] = st_sec
            config["gateways"]["stripe"]["webhook_secret"] = st_wh
            config["gateways"]["wompi_pse_nequi"]["wompi_integrity_secret"] = wp_sec
            config["gateways"]["wompi_pse_nequi"]["mercadopago_access_token"] = mp_sec

        return config

    async def save_payment_gateways_config(
        self,
        db: AsyncSession,
        creator: SaasUser,
        config_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Persists Señor Santiago's payment gateway configuration to `data/payment_gateways_config.json`.
        Restricted strictly to CREATOR superadmin.
        """
        current = self.get_payment_gateways_config(include_secrets=True)
        cur_gws = current["gateways"]
        in_gws = config_data.get("gateways") or {}

        try:
            trm = float(config_data.get("trm_usd_cop") or current.get("trm_usd_cop") or 4200.0)
            if trm <= 0:
                trm = 4200.0
        except (ValueError, TypeError):
            trm = 4200.0

        def _merge_links(old_links: Dict[str, Any], new_links: Optional[Dict[str, Any]]) -> Dict[str, str]:
            merged = dict(old_links or {"STARTER": "", "PRO": "", "BUSINESS": "", "ENTERPRISE": ""})
            if isinstance(new_links, dict):
                for k in ("STARTER", "PRO", "BUSINESS", "ENTERPRISE"):
                    if k in new_links and new_links[k] is not None:
                        merged[k] = str(new_links[k]).strip()
            return merged

        st_in = in_gws.get("stripe") or {}
        wp_in = in_gws.get("wompi_pse_nequi") or {}
        pp_in = in_gws.get("paypal") or {}
        dt_in = in_gws.get("direct_transfer") or {}

        updated_payload = {
            "trm_usd_cop": trm,
            "updated_at": _iso(utcnow()),
            "updated_by": creator.email,
            "gateways": {
                "stripe": {
                    "enabled": bool(st_in.get("enabled", cur_gws["stripe"]["enabled"])),
                    "publishable_key": str(
                        st_in.get("publishable_key")
                        if st_in.get("publishable_key") is not None
                        else cur_gws["stripe"].get("publishable_key", "")
                    ).strip(),
                    "secret_key": str(
                        st_in.get("secret_key")
                        if st_in.get("secret_key") is not None
                        else cur_gws["stripe"].get("secret_key", "")
                    ).strip(),
                    "webhook_secret": str(
                        st_in.get("webhook_secret")
                        if st_in.get("webhook_secret") is not None
                        else cur_gws["stripe"].get("webhook_secret", "")
                    ).strip(),
                    "payment_links": _merge_links(cur_gws["stripe"].get("payment_links", {}), st_in.get("payment_links")),
                },
                "wompi_pse_nequi": {
                    "enabled": bool(wp_in.get("enabled", cur_gws["wompi_pse_nequi"]["enabled"])),
                    "wompi_public_key": str(
                        wp_in.get("wompi_public_key")
                        if wp_in.get("wompi_public_key") is not None
                        else cur_gws["wompi_pse_nequi"].get("wompi_public_key", "")
                    ).strip(),
                    "wompi_integrity_secret": str(
                        wp_in.get("wompi_integrity_secret")
                        if wp_in.get("wompi_integrity_secret") is not None
                        else cur_gws["wompi_pse_nequi"].get("wompi_integrity_secret", "")
                    ).strip(),
                    "mercadopago_public_key": str(
                        wp_in.get("mercadopago_public_key")
                        if wp_in.get("mercadopago_public_key") is not None
                        else cur_gws["wompi_pse_nequi"].get("mercadopago_public_key", "")
                    ).strip(),
                    "mercadopago_access_token": str(
                        wp_in.get("mercadopago_access_token")
                        if wp_in.get("mercadopago_access_token") is not None
                        else cur_gws["wompi_pse_nequi"].get("mercadopago_access_token", "")
                    ).strip(),
                    "payment_links": _merge_links(
                        cur_gws["wompi_pse_nequi"].get("payment_links", {}), wp_in.get("payment_links")
                    ),
                },
                "paypal": {
                    "enabled": bool(pp_in.get("enabled", cur_gws["paypal"]["enabled"])),
                    "client_id": str(
                        pp_in.get("client_id")
                        if pp_in.get("client_id") is not None
                        else cur_gws["paypal"].get("client_id", "")
                    ).strip(),
                    "business_email": str(
                        pp_in.get("business_email")
                        if pp_in.get("business_email") is not None
                        else cur_gws["paypal"].get("business_email", "")
                    ).strip(),
                    "payment_links": _merge_links(cur_gws["paypal"].get("payment_links", {}), pp_in.get("payment_links")),
                },
                "direct_transfer": {
                    "enabled": bool(dt_in.get("enabled", cur_gws["direct_transfer"]["enabled"])),
                    "nequi_number": str(
                        dt_in.get("nequi_number")
                        if dt_in.get("nequi_number") is not None
                        else cur_gws["direct_transfer"].get("nequi_number", "")
                    ).strip(),
                    "bancolombia_account": str(
                        dt_in.get("bancolombia_account")
                        if dt_in.get("bancolombia_account") is not None
                        else cur_gws["direct_transfer"].get("bancolombia_account", "")
                    ).strip(),
                    "bre_b_key": str(
                        dt_in.get("bre_b_key")
                        if dt_in.get("bre_b_key") is not None
                        else cur_gws["direct_transfer"].get("bre_b_key", "")
                    ).strip(),
                    "account_holder": str(
                        dt_in.get("account_holder")
                        if dt_in.get("account_holder") is not None
                        else cur_gws["direct_transfer"].get("account_holder", "")
                    ).strip(),
                    "whatsapp_sales_phone": str(
                        dt_in.get("whatsapp_sales_phone")
                        if dt_in.get("whatsapp_sales_phone") is not None
                        else cur_gws["direct_transfer"].get("whatsapp_sales_phone", "")
                    ).strip(),
                    "instructions": str(
                        dt_in.get("instructions")
                        if dt_in.get("instructions") is not None
                        else cur_gws["direct_transfer"].get("instructions", "")
                    ).strip(),
                },
            },
        }

        cfg_file = settings.DATA_DIR / "payment_gateways_config.json"
        cfg_file.write_text(json.dumps(updated_payload, indent=2, ensure_ascii=False), encoding="utf-8")

        await self.log_audit(
            db=db,
            action="creator_updated_payment_gateways",
            actor_user=creator,
            resource_type="payment_gateways",
            resource_id="payment_gateways_config",
            details={"trm_usd_cop": trm},
        )
        await db.commit()
        return self.get_payment_gateways_config(include_secrets=True)

    async def quote_plan_purchase(
        self,
        db: AsyncSession,
        plan_code: str,
        billing_cycle: str = "monthly",
        promo_code: Optional[str] = None,
        payment_gateway: str = "stripe",
    ) -> Dict[str, Any]:
        """
        Calculates a real-time sales quote in USD and COP for any public SaaS plan,
        including annual billing savings (20% off / 2 months free), promo code discounts,
        bonus AI credits, and gateway checkout links.
        """
        await self.ensure_seeded(db)
        code_up = (plan_code or "STARTER").strip().upper()
        if code_up == "CREATOR":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El plan CREATOR es exclusivo del propietario original y no está a la venta.",
            )

        plan = await self.get_plan(db, code_up)
        if not plan or plan.code != code_up:
            raise HTTPException(status_code=404, detail=f"El plan '{code_up}' no existe.")

        cycle = "annual" if (billing_cycle or "").strip().lower() == "annual" else "monthly"
        gw_clean = (payment_gateway or "stripe").strip().lower()
        if gw_clean not in {"stripe", "wompi_pse_nequi", "paypal", "direct_transfer"}:
            gw_clean = "stripe"

        gw_cfg = self.get_payment_gateways_config(include_secrets=False)
        trm = float(gw_cfg.get("trm_usd_cop") or 4200.0)

        monthly_ref_usd = round(plan.price_monthly_usd * (12 if cycle == "annual" else 1), 2)
        base_price_usd = round(plan.price_annual_usd if cycle == "annual" else plan.price_monthly_usd, 2)
        annual_savings_usd = round(max(0.0, monthly_ref_usd - base_price_usd), 2)

        promo_valid = False
        promo_msg = ""
        promo_discount_pct = 0.0
        promo_discount_usd = 0.0
        bonus_credits = 0
        applied_promo = None

        if promo_code and promo_code.strip():
            try:
                promo = await self.validate_promo_code(db, promo_code.strip(), code_up)
                promo_valid = True
                applied_promo = promo.code
                promo_discount_pct = promo.discount_pct
                promo_discount_usd = round((base_price_usd * (promo.discount_pct / 100.0)) + promo.discount_fixed_usd, 2)
                promo_discount_usd = min(base_price_usd, promo_discount_usd)
                bonus_credits = promo.bonus_credits
                promo_msg = f"Cupón {promo.code} aplicado (-{promo.discount_pct:.0f}%)"
            except HTTPException as exc:
                promo_valid = False
                promo_msg = str(exc.detail)

        total_usd = round(max(0.0, base_price_usd - promo_discount_usd), 2)
        subtotal_cop = int(round(base_price_usd * trm))
        discount_cop = int(round(promo_discount_usd * trm))
        total_cop = int(round(total_usd * trm))
        monthly_eq_usd = round(total_usd / 12.0, 2) if cycle == "annual" else total_usd
        monthly_eq_cop = int(round(monthly_eq_usd * trm))

        gw_info = (gw_cfg.get("gateways") or {}).get(gw_clean, {})
        external_link = ((gw_info.get("payment_links") or {}).get(code_up) or "").strip()

        return {
            "ok": True,
            "plan": self.serialize_plan(plan),
            "quote": {
                "plan_code": plan.code,
                "plan_name": plan.name,
                "billing_cycle": cycle,
                "payment_gateway": gw_clean,
                "payment_gateway_label": gw_info.get("label", gw_clean),
                "trm_usd_cop": trm,
                "monthly_reference_usd": monthly_ref_usd,
                "subtotal_usd": base_price_usd,
                "annual_savings_usd": annual_savings_usd,
                "promo_code": applied_promo,
                "promo_valid": promo_valid,
                "promo_message": promo_msg,
                "promo_discount_pct": promo_discount_pct,
                "promo_discount_usd": promo_discount_usd,
                "total_usd": total_usd,
                "subtotal_cop": subtotal_cop,
                "discount_cop": discount_cop,
                "total_cop": total_cop,
                "monthly_equivalent_usd": monthly_eq_usd,
                "monthly_equivalent_cop": monthly_eq_cop,
                "base_credits": plan.monthly_credits,
                "bonus_credits": bonus_credits,
                "total_credits_granted": plan.monthly_credits + bonus_credits,
                "external_payment_link": external_link,
                "direct_transfer_details": gw_cfg["gateways"]["direct_transfer"],
            },
        }

    async def authenticate_with_firebase(
        self,
        db: AsyncSession,
        mode: str,
        email: str,
        password: Optional[str] = None,
        full_name: str = "",
        firebase_uid: Optional[str] = None,
        firebase_id_token: Optional[str] = None,
        provider: str = "password",
        selected_plan: str = "FREE",
        promo_code: Optional[str] = None,
        referral_code: Optional[str] = None,
        ip_address: str = "127.0.0.1",
        billing_cycle: str = "monthly",
        payment_gateway: str = "stripe",
        payment_method_brand: str = "visa",
        payment_method_last4: str = "4242",
    ) -> Dict[str, Any]:
        """
        Registers or logs in a user linked to the configured Firebase project,
        synchronizing their Firebase UID, auth provider, and chosen subscription plan.
        Strictly forbids selecting or assigning the CREATOR plan.
        """
        await self.ensure_seeded(db)
        fb_cfg = self.get_firebase_config()
        project_id = fb_cfg["projectId"]
        clean_email = (email or "").strip().lower()
        target_plan = (selected_plan or "FREE").strip().upper()

        if target_plan == "CREATOR":
            await self.log_audit(
                db=db,
                action="blocked_firebase_creator_plan_attempt",
                resource_type="firebase_auth",
                ip_address=ip_address,
                severity="security",
                details={"email": clean_email, "mode": mode},
            )
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El plan CREATOR es exclusivo del propietario original y no puede seleccionarse al crear cuenta.",
            )

        # Resolve or generate deterministic Firebase UID linked to the Firebase project
        resolved_fb_uid = (firebase_uid or "").strip()
        if not resolved_fb_uid and clean_email:
            digest = hashlib.sha256(f"{project_id}:{clean_email}".encode("utf-8")).hexdigest()[:24]
            resolved_fb_uid = f"fb_{digest}"

        clean_mode = (mode or "register").strip().lower()

        if clean_mode == "register":
            reg_res = await self.register_user(
                db=db,
                email=clean_email,
                password=password or secrets.token_urlsafe(12),
                full_name=full_name,
                referral_code_used=referral_code,
                ip_address=ip_address,
                requested_plan="FREE",
            )
            res_u = await db.execute(select(SaasUser).where(SaasUser.email == clean_email))
            user = res_u.scalars().first()
            if user:
                prefs = dict(user.preferences or {})
                prefs["firebase_uid"] = resolved_fb_uid
                prefs["firebase_project_id"] = project_id
                prefs["firebase_provider"] = provider
                user.preferences = prefs
                await db.commit()

                # If user picked a commercial plan (STARTER, PRO, BUSINESS, ENTERPRISE) on the startup screen, activate it
                checkout_info = None
                if target_plan in PUBLIC_PURCHASABLE_PLANS:
                    checkout_info = await self.checkout_subscription(
                        db=db,
                        user=user,
                        target_plan_code=target_plan,
                        billing_cycle=billing_cycle or "monthly",
                        promo_code=promo_code,
                        payment_method_brand=payment_method_brand or "visa",
                        payment_method_last4=payment_method_last4 or "4242",
                        ip_address=ip_address,
                        payment_gateway=payment_gateway or "stripe",
                    )

                plan_obj = await self.get_plan(db, user.plan_code)
                bal_obj = await self.get_or_create_credit_balance(db, user)
                token = sign_saas_token(user.id, user.email, user.role, user.plan_code)
                return {
                    "ok": True,
                    "token": token,
                    "firebase": {
                        "uid": resolved_fb_uid,
                        "projectId": project_id,
                        "provider": provider,
                        "linked": True,
                    },
                    "checkout": checkout_info,
                    "user": self.serialize_user(user, plan_obj, bal_obj),
                }
            return reg_res

        # Login or Google OAuth mode
        res_u = await db.execute(select(SaasUser).where(SaasUser.email == clean_email))
        existing_user = res_u.scalars().first()

        if not existing_user and provider == "google.com":
            # Auto-provision Google OAuth user on first sign-in
            return await self.authenticate_with_firebase(
                db=db,
                mode="register",
                email=clean_email,
                password=secrets.token_urlsafe(16),
                full_name=full_name or clean_email.split("@")[0],
                firebase_uid=resolved_fb_uid,
                firebase_id_token=firebase_id_token,
                provider="google.com",
                selected_plan=target_plan,
                promo_code=promo_code,
                referral_code=referral_code,
                ip_address=ip_address,
                billing_cycle=billing_cycle,
                payment_gateway=payment_gateway,
                payment_method_brand=payment_method_brand,
                payment_method_last4=payment_method_last4,
            )

        login_res = await self.login_user(
            db=db,
            email=clean_email,
            password=password or "",
            ip_address=ip_address,
        )
        res_u = await db.execute(select(SaasUser).where(SaasUser.email == clean_email))
        user = res_u.scalars().first()
        if user:
            prefs = dict(user.preferences or {})
            prefs["firebase_uid"] = prefs.get("firebase_uid") or resolved_fb_uid
            prefs["firebase_project_id"] = project_id
            prefs["firebase_provider"] = provider
            user.preferences = prefs
            await db.commit()
            plan_obj = await self.get_plan(db, user.plan_code)
            bal_obj = await self.get_or_create_credit_balance(db, user)
            login_res["user"] = self.serialize_user(user, plan_obj, bal_obj)
            login_res["firebase"] = {
                "uid": prefs["firebase_uid"],
                "projectId": project_id,
                "provider": provider,
                "linked": True,
            }
        return login_res


saas_service = SaasPlatformService()

