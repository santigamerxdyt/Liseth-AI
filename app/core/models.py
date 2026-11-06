"""
SQLAlchemy ORM models for JARVIS / Liseth SQLite database.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, default=1)
    name = Column(String(100), default="Santiago")
    nickname = Column(String(100), default="Santi")
    created_at = Column(DateTime, default=utcnow)
    memory_facts = Column(JSON, default=list)
    preferences = Column(JSON, default=dict)
    pin_salt = Column(String(64), nullable=True)
    pin_hash = Column(String(128), nullable=True)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), default="default", index=True)
    role = Column(String(30), nullable=False)  # 'user', 'model', 'system'
    parts = Column(JSON, nullable=False)  # [{ "text": "..." }]
    timestamp = Column(DateTime, default=utcnow)
    meta_info = Column(JSON, default=dict)


class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"

    id = Column(String(100), primary_key=True)
    title = Column(String(200), nullable=False)
    type = Column(String(50), nullable=False)  # 'reminder', 'report', 'digest', 'check'
    schedule = Column(String(50), nullable=False)  # 'daily', 'interval', 'cron', etc.
    time_of_day = Column(String(20), nullable=True)
    enabled = Column(Boolean, default=True)
    last_run = Column(String(50), nullable=True)
    next_run = Column(String(50), nullable=True)
    params = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)


class AuditEntry(Base):
    __tablename__ = "audit_entries"

    id = Column(String(100), primary_key=True)
    timestamp = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    status = Column(String(30), nullable=False)  # 'pending', 'approved', 'rejected', 'executed'
    sensitive = Column(Boolean, default=False)
    details = Column(JSON, default=dict)


class TokenUsage(Base):
    __tablename__ = "token_usage"

    id = Column(Integer, primary_key=True, default=1)
    prompt_tokens = Column(Integer, default=0)
    candidates_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    daily_limit = Column(Integer, default=100000)
    alert_threshold_pct = Column(Integer, default=80)
    last_reset_date = Column(String(20), nullable=True)
    last_updated = Column(DateTime, default=utcnow)


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(String(100), primary_key=True)
    name = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    size = Column(Integer, default=0)
    file_type = Column(String(100), default="application/octet-stream")
    uploaded_at = Column(DateTime, default=utcnow)
    url = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)


class AppSetting(Base):
    __tablename__ = "app_settings"

    key = Column(String(100), primary_key=True)
    value = Column(JSON, nullable=False)


class NfcTransaction(Base):
    __tablename__ = "nfc_transactions"

    id = Column(String(100), primary_key=True)
    created_at = Column(DateTime, default=utcnow)
    type = Column(String(50), nullable=False)  # 'payment', 'vcard', 'text', 'url', 'token'
    direction = Column(String(20), default="outgoing")  # 'outgoing' (emitted/beamed) or 'incoming' (read/received)
    amount = Column(Float, nullable=True)
    currency = Column(String(10), default="COP")
    recipient = Column(String(200), nullable=True)
    sender = Column(String(200), nullable=True)
    concept = Column(String(255), nullable=True)
    status = Column(String(30), default="completed")  # 'completed', 'pending', 'simulated'
    payload = Column(JSON, default=dict)


class DigitalInvoice(Base):
    __tablename__ = "digital_invoices"

    id = Column(String(100), primary_key=True)  # e.g. FAC-2026-0001
    created_at = Column(DateTime, default=utcnow)
    issuer_name = Column(String(200), default="Santiago Huerfano Lopez")
    issuer_nit = Column(String(50), default="1000000000-1")
    client_name = Column(String(200), nullable=False)
    client_id = Column(String(50), default="222222222222")
    currency = Column(String(10), default="COP")
    items = Column(JSON, default=list)
    subtotal = Column(Float, default=0.0)
    tax_iva = Column(Float, default=0.0)
    retention = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    payment_method = Column(String(50), default="Bre-B Contactless")
    cufe_hash = Column(String(128), nullable=False)
    qr_payload = Column(Text, nullable=True)
    nfc_tx_id = Column(String(100), nullable=True)
    status = Column(String(30), default="issued")


class NfcSecurityKey(Base):
    __tablename__ = "nfc_security_keys"

    id = Column(String(100), primary_key=True)
    label = Column(String(150), default="Credencial de Santiago")
    created_at = Column(DateTime, default=utcnow)
    last_used = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    secret_hash = Column(String(128), nullable=True)
    permissions = Column(JSON, default=list)


class PersonalFinanceEntry(Base):
    __tablename__ = "personal_finance_entries"

    id = Column(String(100), primary_key=True)
    created_at = Column(DateTime, default=utcnow)
    date = Column(String(20), nullable=False)
    type = Column(String(20), nullable=False)  # 'expense' (gasto) or 'income' (ingreso)
    category = Column(String(50), nullable=False)  # 'Alimentacion', 'Transporte', 'Educacion', 'Servicios', 'Consultoria', 'Entretenimiento', 'Inversion'
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="COP")
    description = Column(String(255), nullable=False)
    payment_method = Column(String(50), default="Efectivo / Contactless")
    nfc_ref = Column(String(100), nullable=True)
    invoice_ref = Column(String(100), nullable=True)


class BudgetPlan(Base):
    __tablename__ = "budget_plans"

    category = Column(String(50), primary_key=True)
    monthly_limit = Column(Float, nullable=False)
    alert_threshold_pct = Column(Integer, default=80)
    currency = Column(String(10), default="COP")
    updated_at = Column(DateTime, default=utcnow)


class LegalContract(Base):
    __tablename__ = "legal_contracts"

    id = Column(String(100), primary_key=True)  # e.g. CONTRATO-2026-XXXX
    created_at = Column(DateTime, default=utcnow)
    type = Column(String(50), nullable=False)  # 'servicios_profesionales', 'nda', 'pagare', 'acta_entrega'
    title = Column(String(255), nullable=False)
    party_a = Column(String(200), default="Santiago Huerfano Lopez")  # Prestador / Emisor
    party_b = Column(String(200), nullable=False)  # Contratante / Cliente
    total_value = Column(Float, default=0.0)
    currency = Column(String(10), default="COP")
    city = Column(String(100), default="Palmira, Valle del Cauca, Colombia")
    content_markdown = Column(Text, nullable=False)
    status = Column(String(30), default="draft")  # 'draft', 'signed', 'active', 'archived'


class CorporateRisk(Base):
    __tablename__ = "corporate_risks"

    id = Column(String(100), primary_key=True)
    created_at = Column(DateTime, default=utcnow)
    title = Column(String(200), nullable=False)
    category = Column(String(50), default="Estrategico")  # Estrategico, Financiero, Operacional, Legal, Ciberseguridad
    probability = Column(Integer, default=3)  # 1 a 5
    impact = Column(Integer, default=3)  # 1 a 5
    inherent_risk = Column(Integer, default=9)  # P * I
    control_description = Column(String(255), default="Controles preventivos y detectivos estándar")
    residual_probability = Column(Integer, default=2)
    residual_impact = Column(Integer, default=2)
    residual_risk = Column(Integer, default=4)
    owner = Column(String(100), default="Santiago / CEO")
    status = Column(String(30), default="active")  # active, mitigated, accepted, archived


class InvestmentProject(Base):
    __tablename__ = "investment_projects"

    id = Column(String(100), primary_key=True)
    created_at = Column(DateTime, default=utcnow)
    name = Column(String(200), nullable=False)
    initial_investment = Column(Float, nullable=False)
    discount_rate = Column(Float, default=0.12)
    cash_flows = Column(JSON, default=list)
    npv = Column(Float, default=0.0)
    irr = Column(Float, default=0.0)
    payback_years = Column(Float, default=0.0)
    discounted_payback_years = Column(Float, default=0.0)
    benefit_cost_ratio = Column(Float, default=0.0)
    decision = Column(String(50), default="VIABLE")
    details = Column(JSON, default=dict)


# ==============================================================================
# SAAS MULTI-USER, MULTI-TENANT, SUBSCRIPTION & MONETIZATION MODELS
# ==============================================================================


class SaasPlan(Base):
    __tablename__ = "saas_plans"

    id = Column(String(50), primary_key=True)
    code = Column(String(30), unique=True, index=True, nullable=False)  # FREE, STARTER, PRO, BUSINESS, ENTERPRISE, CREATOR
    level = Column(Integer, default=0, nullable=False)  # 0..5
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    price_monthly_usd = Column(Float, default=0.0)
    price_annual_usd = Column(Float, default=0.0)
    is_public = Column(Boolean, default=True)  # False for CREATOR
    is_commercializable = Column(Boolean, default=True)  # False for FREE and CREATOR
    max_brains = Column(Integer, default=3)
    max_conversations = Column(Integer, default=5)
    daily_message_limit = Column(Integer, default=25)
    monthly_token_limit = Column(Integer, default=100000)
    monthly_credits = Column(Integer, default=500)
    max_memories = Column(Integer, default=20)
    allowed_skill_tiers = Column(JSON, default=list)
    features = Column(JSON, default=dict)
    priority_level = Column(Integer, default=1)
    trial_days = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow)


class SaasUser(Base):
    __tablename__ = "saas_users"

    id = Column(String(64), primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    password_salt = Column(String(128), nullable=False)
    full_name = Column(String(150), default="")
    nickname = Column(String(100), default="")
    avatar_url = Column(String(500), default="")
    bio = Column(Text, default="")
    role = Column(String(30), default="USER", index=True)  # USER, ADMIN, CREATOR
    plan_code = Column(String(30), default="FREE", index=True)  # FREE, STARTER, PRO, BUSINESS, ENTERPRISE, CREATOR
    is_active = Column(Boolean, default=True)
    is_suspended = Column(Boolean, default=False)
    suspension_reason = Column(String(255), nullable=True)
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String(128), nullable=True)
    reset_token = Column(String(128), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    memory_enabled = Column(Boolean, default=True)
    preferences = Column(JSON, default=dict)
    referral_code = Column(String(40), unique=True, index=True, nullable=False)
    referred_by_id = Column(String(64), nullable=True, index=True)
    stripe_customer_id = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow)
    last_login_at = Column(DateTime, nullable=True)


class SaasSubscription(Base):
    __tablename__ = "saas_subscriptions"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), index=True, nullable=False)
    plan_code = Column(String(30), nullable=False)
    billing_cycle = Column(String(20), default="monthly")  # monthly, annual, lifetime
    status = Column(String(30), default="active", index=True)  # active, trialing, past_due, grace_period, canceled, expired
    price_usd = Column(Float, default=0.0)
    discount_pct = Column(Float, default=0.0)
    promo_code_used = Column(String(50), nullable=True)
    auto_renew = Column(Boolean, default=True)
    cancel_at_period_end = Column(Boolean, default=False)
    current_period_start = Column(DateTime, default=utcnow)
    current_period_end = Column(DateTime, nullable=True)
    grace_period_ends_at = Column(DateTime, nullable=True)
    canceled_at = Column(DateTime, nullable=True)
    stripe_subscription_id = Column(String(120), nullable=True)
    payment_method_summary = Column(String(100), default="Sin tarjeta requerida")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow)


class SaasPayment(Base):
    __tablename__ = "saas_payments"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), index=True, nullable=False)
    subscription_id = Column(String(64), nullable=True)
    plan_code = Column(String(30), nullable=False)
    amount_usd = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    status = Column(String(30), default="succeeded", index=True)  # succeeded, pending, failed, refunded
    provider = Column(String(30), default="stripe")  # stripe, manual, promo
    external_tx_id = Column(String(150), unique=True, index=True, nullable=False)
    payment_method_brand = Column(String(50), default="visa")
    payment_method_last4 = Column(String(4), default="4242")
    failure_reason = Column(String(255), nullable=True)
    refunded_amount_usd = Column(Float, default=0.0)
    refund_reason = Column(String(255), nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)


class SaasInvoice(Base):
    __tablename__ = "saas_invoices"

    id = Column(String(64), primary_key=True)
    invoice_number = Column(String(64), unique=True, index=True, nullable=False)
    user_id = Column(String(64), index=True, nullable=False)
    subscription_id = Column(String(64), nullable=True)
    payment_id = Column(String(64), nullable=True)
    plan_code = Column(String(30), nullable=False)
    billing_cycle = Column(String(20), default="monthly")
    subtotal_usd = Column(Float, default=0.0)
    discount_usd = Column(Float, default=0.0)
    tax_usd = Column(Float, default=0.0)
    total_usd = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    status = Column(String(30), default="paid")  # paid, open, void, refunded, uncollectible
    line_items = Column(JSON, default=list)
    issued_at = Column(DateTime, default=utcnow)
    paid_at = Column(DateTime, nullable=True)


class SaasCreditBalance(Base):
    __tablename__ = "saas_credit_balances"

    user_id = Column(String(64), primary_key=True)
    monthly_credits_allocated = Column(Integer, default=500)
    credits_used = Column(Integer, default=0)
    bonus_credits = Column(Integer, default=0)
    daily_messages_used = Column(Integer, default=0)
    monthly_messages_used = Column(Integer, default=0)
    monthly_tokens_used = Column(Integer, default=0)
    estimated_api_cost_usd = Column(Float, default=0.0)
    alert_80_sent = Column(Boolean, default=False)
    is_quota_blocked = Column(Boolean, default=False)
    last_daily_reset = Column(String(20), default="")
    period_reset_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=utcnow)


class SaasUsageRecord(Base):
    __tablename__ = "saas_usage_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), index=True, nullable=False)
    conversation_id = Column(String(64), index=True, nullable=True)
    brain_used = Column(String(60), default="gemini")
    model_used = Column(String(100), default="gemini-3.1-flash-lite")
    provider = Column(String(50), default="google")
    skill_used = Column(String(100), nullable=True)
    agent_used = Column(String(100), nullable=True)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    credits_charged = Column(Integer, default=1)
    estimated_cost_usd = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utcnow)


class SaasConversation(Base):
    __tablename__ = "saas_conversations"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), index=True, nullable=False)
    title = Column(String(255), default="Nueva conversación")
    is_archived = Column(Boolean, default=False, index=True)
    is_pinned = Column(Boolean, default=False)
    brain_used = Column(String(60), default="gemini")
    model_used = Column(String(100), default="gemini-3.1-flash-lite")
    agent_id = Column(String(64), nullable=True)
    active_skills = Column(JSON, default=list)
    associated_files = Column(JSON, default=list)
    context_metadata = Column(JSON, default=dict)
    summary = Column(Text, default="")
    message_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow)


class SaasMessage(Base):
    __tablename__ = "saas_messages"

    id = Column(String(64), primary_key=True)
    conversation_id = Column(String(64), index=True, nullable=False)
    user_id = Column(String(64), index=True, nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    parts = Column(JSON, default=list)
    brain_used = Column(String(60), nullable=True)
    model_used = Column(String(100), nullable=True)
    skills_invoked = Column(JSON, default=list)
    tokens_used = Column(Integer, default=0)
    credits_used = Column(Integer, default=0)
    meta_info = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)


class SaasUserMemory(Base):
    __tablename__ = "saas_user_memories"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), index=True, nullable=False)
    conversation_id = Column(String(64), index=True, nullable=True)
    scope = Column(String(30), default="personal", index=True)  # personal, contextual, preference, summary, authorized_fact
    title = Column(String(200), default="")
    content = Column(Text, nullable=False)
    keywords = Column(JSON, default=list)
    importance = Column(Integer, default=3)  # 1..5
    is_authorized = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow)


class SaasAIProvider(Base):
    __tablename__ = "saas_ai_providers"

    id = Column(String(64), primary_key=True)
    code = Column(String(40), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    status = Column(String(30), default="active")  # active, maintenance, disabled
    base_url = Column(String(255), default="")
    api_key_env = Column(String(100), default="")
    priority = Column(Integer, default=1)
    config_json = Column(JSON, default=dict)
    updated_at = Column(DateTime, default=utcnow)


class SaasAIModel(Base):
    __tablename__ = "saas_ai_models"

    id = Column(String(80), primary_key=True)
    provider_code = Column(String(40), index=True, nullable=False)
    model_id = Column(String(100), unique=True, index=True, nullable=False)
    display_name = Column(String(120), nullable=False)
    tier_required = Column(Integer, default=0)  # 0..5
    compatible_plans = Column(JSON, default=list)
    credit_cost_per_msg = Column(Integer, default=1)
    cost_per_1k_input_usd = Column(Float, default=0.00015)
    cost_per_1k_output_usd = Column(Float, default=0.0006)
    max_context_tokens = Column(Integer, default=128000)
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    capabilities = Column(JSON, default=list)
    updated_at = Column(DateTime, default=utcnow)


class SaasSkill(Base):
    __tablename__ = "saas_skills"

    id = Column(String(80), primary_key=True)
    code = Column(String(80), unique=True, index=True, nullable=False)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(60), default="general", index=True)
    version = Column(String(20), default="2.0.0")
    status = Column(String(20), default="active")  # active, beta, disabled
    tier = Column(String(30), default="basic", index=True)  # basic, intermediate, advanced, business, enterprise, creator
    min_plan_level = Column(Integer, default=0)
    compatible_plans = Column(JSON, default=list)
    required_permissions = Column(JSON, default=list)
    requirements = Column(JSON, default=list)
    estimated_credit_cost = Column(Integer, default=1)
    estimated_api_cost_usd = Column(Float, default=0.0005)
    is_system = Column(Boolean, default=True)
    created_by_user_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow)


class SaasAgent(Base):
    __tablename__ = "saas_agents"

    id = Column(String(64), primary_key=True)
    owner_user_id = Column(String(64), index=True, nullable=True)
    name = Column(String(120), nullable=False)
    role_title = Column(String(120), default="Agente Especializado")
    description = Column(Text, default="")
    system_prompt = Column(Text, default="")
    preferred_brain = Column(String(60), default="gemini")
    preferred_model = Column(String(100), default="gemini-3.1-flash-lite")
    skill_codes = Column(JSON, default=list)
    min_plan_level = Column(Integer, default=0)
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    avatar_icon = Column(String(40), default="🤖")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow)


class SaasPromoCode(Base):
    __tablename__ = "saas_promo_codes"

    id = Column(String(64), primary_key=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), default="")
    discount_pct = Column(Float, default=0.0)
    discount_fixed_usd = Column(Float, default=0.0)
    bonus_credits = Column(Integer, default=0)
    trial_days_bonus = Column(Integer, default=0)
    applicable_plans = Column(JSON, default=list)
    max_uses = Column(Integer, default=1000)
    current_uses = Column(Integer, default=0)
    valid_from = Column(DateTime, default=utcnow)
    valid_until = Column(DateTime, nullable=True)
    is_welcome_coupon = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)


class SaasReferral(Base):
    __tablename__ = "saas_referrals"

    id = Column(String(64), primary_key=True)
    referrer_user_id = Column(String(64), index=True, nullable=False)
    referred_user_id = Column(String(64), unique=True, index=True, nullable=False)
    referral_code_used = Column(String(40), nullable=False)
    status = Column(String(30), default="pending")  # pending, verified, rewarded, rejected
    referrer_reward_credits = Column(Integer, default=500)
    referred_reward_credits = Column(Integer, default=250)
    verified_at = Column(DateTime, nullable=True)
    rewarded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)


class SaasAuditLog(Base):
    __tablename__ = "saas_audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    actor_user_id = Column(String(64), index=True, nullable=True)
    actor_email = Column(String(255), nullable=True)
    actor_role = Column(String(30), nullable=True)
    target_user_id = Column(String(64), index=True, nullable=True)
    action = Column(String(100), index=True, nullable=False)
    resource_type = Column(String(60), default="system")
    resource_id = Column(String(100), nullable=True)
    ip_address = Column(String(64), default="127.0.0.1")
    severity = Column(String(20), default="info")  # info, warning, critical, security
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)





