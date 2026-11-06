"""
FastAPI Router for Liseth SaaS Multi-User, Multi-Tenant, Monetizable Platform.
Prefix: /api/saas
Endpoints:
- Auth & Profile: /auth/register, /auth/login, /auth/logout, /auth/verify-email,
  /auth/forgot-password, /auth/reset-password, /profile, /profile/password, /profile/delete
- Plans & Catalog: /plans, /catalog, /agents
- Multi-Tenant Conversations: /conversations, /conversations/{id}, /conversations/{id}/messages
- Individual User Memory Brain: /memories, /memories/search, /memories/{id}
- Billing, Subscriptions, Promo Codes & Webhooks: /billing/checkout, /billing/cancel,
  /billing/history, /billing/promo/validate, /billing/webhook, /referrals
- Usage & Quotas: /usage
- Exclusive CREATOR Superadmin Panel: /admin/dashboard, /admin/users, /admin/users/{id},
  /admin/plans/{code}, /admin/skills, /admin/refunds, /admin/models
"""
import json
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import _get_client_ip
from app.core.database import get_db
from app.core.models import (
    SaasAIModel,
    SaasPromoCode,
    SaasReferral,
    SaasUsageRecord,
)
from app.services.saas_service import saas_service

logger = logging.getLogger("jarvis.saas_router")

router = APIRouter(prefix="/api/saas", tags=["saas"])


# ==============================================================================
# PYDANTIC REQUEST SCHEMAS
# ==============================================================================

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = ""
    referral_code: Optional[str] = None
    plan_code: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class VerifyEmailRequest(BaseModel):
    token: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


classChangePasswordRequest = BaseModel


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class ConversationCreateRequest(BaseModel):
    title: Optional[str] = "Nueva conversación"
    brain_used: Optional[str] = "gemini"
    model_used: Optional[str] = "gemini-3.1-flash-lite"
    active_skills: Optional[List[str]] = Field(default_factory=list)
    associated_files: Optional[List[str]] = Field(default_factory=list)
    agent_id: Optional[str] = None
    context_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MessageSendRequest(BaseModel):
    content: str
    model_id: Optional[str] = None
    skill_code: Optional[str] = None
    use_live_ai: Optional[bool] = False


class MemoryCreateRequest(BaseModel):
    content: str
    scope: Optional[str] = "personal"
    title: Optional[str] = ""
    keywords: Optional[List[str]] = None
    importance: Optional[int] = 3
    conversation_id: Optional[str] = None
    is_authorized: Optional[bool] = True


class AgentCreateRequest(BaseModel):
    name: str
    role_title: Optional[str] = "Especialista IA"
    description: Optional[str] = ""
    system_prompt: Optional[str] = ""
    preferred_brain: Optional[str] = "gemini"
    preferred_model: Optional[str] = "gemini-3.1-flash-lite"
    skill_codes: Optional[List[str]] = Field(default_factory=list)
    avatar_icon: Optional[str] = "🤖"


class CheckoutRequest(BaseModel):
    plan_code: str
    billing_cycle: Optional[str] = "monthly"
    promo_code: Optional[str] = None
    payment_method_brand: Optional[str] = "visa"
    payment_method_last4: Optional[str] = "4242"
    external_tx_id: Optional[str] = None


class CancelSubscriptionRequest(BaseModel):
    immediate: Optional[bool] = False


class PromoValidateRequest(BaseModel):
    code: str
    plan_code: str


class RefundRequest(BaseModel):
    payment_id: str
    reason: Optional[str] = "Reembolso autorizado por Superadmin CREATOR"


class FirebaseAuthRequest(BaseModel):
    mode: Optional[str] = "register"  # "register" or "login"
    email: str
    password: Optional[str] = None
    full_name: Optional[str] = ""
    firebase_uid: Optional[str] = None
    firebase_id_token: Optional[str] = None
    provider: Optional[str] = "password"  # "password" or "google.com"
    selected_plan: Optional[str] = "FREE"
    promo_code: Optional[str] = None
    referral_code: Optional[str] = None


# ==============================================================================
# 0. FIREBASE PROJECT LINKING & FIREBASE AUTHENTICATION ENDPOINTS
# ==============================================================================

@router.get("/firebase/config")
async def get_firebase_config_endpoint():
    return saas_service.get_firebase_config()


@router.post("/firebase/config")
async def save_firebase_config_endpoint(
    config_data: Dict[str, Any],
):
    return saas_service.save_firebase_config(config_data)


@router.post("/auth/firebase")
async def firebase_auth_endpoint(
    req: FirebaseAuthRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    res = await saas_service.authenticate_with_firebase(
        db=db,
        mode=req.mode or "register",
        email=req.email,
        password=req.password,
        full_name=req.full_name or "",
        firebase_uid=req.firebase_uid,
        firebase_id_token=req.firebase_id_token,
        provider=req.provider or "password",
        selected_plan=req.selected_plan or "FREE",
        promo_code=req.promo_code,
        referral_code=req.referral_code,
        ip_address=_get_client_ip(request),
    )
    for cookie_name in ("liseth_saas_session", "liseth_session"):
        response.set_cookie(
            key=cookie_name,
            value=res["token"],
            httponly=True,
            samesite="lax",
            max_age=86400 * 7,
            path="/",
        )
    return res


# ==============================================================================
# 1. AUTHENTICATION & USER PROFILE ENDPOINTS
# ==============================================================================

@router.post("/auth/register")
async def register_endpoint(
    req: RegisterRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    res = await saas_service.register_user(
        db=db,
        email=req.email,
        password=req.password,
        full_name=req.full_name or "",
        referral_code_used=req.referral_code,
        ip_address=_get_client_ip(request),
        requested_plan=req.plan_code,
        requested_role=req.role,
    )
    for cookie_name in ("liseth_saas_session", "liseth_session"):
        response.set_cookie(
            key=cookie_name,
            value=res["token"],
            httponly=True,
            samesite="lax",
            max_age=86400 * 7,
            path="/",
        )
    return res


@router.post("/auth/login")
async def login_endpoint(
    req: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    res = await saas_service.login_user(
        db=db,
        email=req.email,
        password=req.password,
        ip_address=_get_client_ip(request),
    )
    for cookie_name in ("liseth_saas_session", "liseth_session"):
        response.set_cookie(
            key=cookie_name,
            value=res["token"],
            httponly=True,
            samesite="lax",
            max_age=86400 * 7,
            path="/",
        )
    return res


@router.post("/auth/logout")
async def logout_endpoint(response: Response):
    response.delete_cookie(key="liseth_saas_session", path="/")
    response.delete_cookie(key="liseth_session", path="/")
    return {"ok": True, "message": "Sesión SaaS cerrada correctamente."}


@router.post("/auth/verify-email")
async def verify_email_endpoint(
    req: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    return await saas_service.verify_email(db, req.token)


@router.post("/auth/forgot-password")
async def forgot_password_endpoint(
    req: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    return await saas_service.request_password_reset(db, req.email)


@router.post("/auth/reset-password")
async def reset_password_endpoint(
    req: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    return await saas_service.reset_password(db, req.token, req.new_password)


@router.get("/profile")
async def get_profile_endpoint(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    plan = await saas_service.get_plan(db, user.plan_code)
    balance = await saas_service.get_or_create_credit_balance(db, user)
    return {
        "ok": True,
        "user": saas_service.serialize_user(user, plan, balance),
    }


@router.put("/profile")
@router.patch("/profile")
async def update_profile_endpoint(
    request: Request,
    updates: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    return await saas_service.update_profile(db, user, updates)


@router.post("/profile/password")
async def change_password_endpoint(
    req: PasswordChangeRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    return await saas_service.change_password(db, user, req.current_password, req.new_password)


@router.delete("/profile")
@router.post("/profile/delete")
async def delete_profile_endpoint(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    res = await saas_service.delete_own_account(db, user)
    response.delete_cookie(key="liseth_saas_session", path="/")
    return res


# ==============================================================================
# 2. PLANS, CATALOG (MODELS, SKILLS, AGENTS) & CUSTOM AGENTS
# ==============================================================================

@router.get("/plans")
async def list_plans_endpoint(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # Check if caller is CREATOR to optionally show CREATOR badge metadata, while public pricing only lists public plans
    include_creator = False
    try:
        user = await saas_service.get_current_user(request, db)
        if user.role == "CREATOR" and user.plan_code == "CREATOR":
            include_creator = True
    except Exception:
        pass
    plans = await saas_service.list_public_plans(db, include_creator=include_creator)
    return {"ok": True, "plans": plans}


@router.get("/catalog")
async def get_catalog_endpoint(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    return await saas_service.get_catalog_for_user(db, user)


@router.post("/agents")
async def create_custom_agent_endpoint(
    req: AgentCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    return await saas_service.create_custom_agent(
        db=db,
        user=user,
        name=req.name,
        role_title=req.role_title or "Especialista IA",
        description=req.description or "",
        system_prompt=req.system_prompt or "",
        preferred_brain=req.preferred_brain or "gemini",
        preferred_model=req.preferred_model or "gemini-3.1-flash-lite",
        skill_codes=req.skill_codes,
        avatar_icon=req.avatar_icon or "🤖",
    )


# ==============================================================================
# 3. MULTI-TENANT CONVERSATIONS WORKSPACE
# ==============================================================================

@router.post("/conversations")
async def create_conversation_endpoint(
    req: ConversationCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    return await saas_service.create_conversation(
        db=db,
        user=user,
        title=req.title or "Nueva conversación",
        brain_used=req.brain_used or "gemini",
        model_used=req.model_used or "gemini-3.1-flash-lite",
        active_skills=req.active_skills,
        associated_files=req.associated_files,
        agent_id=req.agent_id,
        context_metadata=req.context_metadata,
    )


@router.get("/conversations")
async def list_conversations_endpoint(
    request: Request,
    include_archived: bool = Query(False),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    return await saas_service.list_conversations(
        db=db,
        user=user,
        include_archived=include_archived,
        search_query=search,
        page=page,
        page_size=page_size,
    )


@router.get("/conversations/{conversation_id}")
async def get_conversation_endpoint(
    conversation_id: str,
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    return await saas_service.get_conversation(
        db=db,
        user=user,
        conversation_id=conversation_id,
        page=page,
        page_size=page_size,
    )


@router.put("/conversations/{conversation_id}")
@router.patch("/conversations/{conversation_id}")
async def update_conversation_endpoint(
    conversation_id: str,
    updates: Dict[str, Any],
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    return await saas_service.update_conversation(db, user, conversation_id, updates)


@router.delete("/conversations/{conversation_id}")
async def delete_conversation_endpoint(
    conversation_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    return await saas_service.delete_conversation(db, user, conversation_id)


@router.post("/conversations/{conversation_id}/messages")
async def send_message_endpoint(
    conversation_id: str,
    req: MessageSendRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    return await saas_service.add_message_and_respond(
        db=db,
        user=user,
        conversation_id=conversation_id,
        content=req.content,
        model_id=req.model_id,
        skill_code=req.skill_code,
        use_live_ai=bool(req.use_live_ai),
    )


# ==============================================================================
# 4. INDIVIDUAL USER MEMORY BRAIN
# ==============================================================================

@router.post("/memories")
async def create_memory_endpoint(
    req: MemoryCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    return await saas_service.create_memory(
        db=db,
        user=user,
        content=req.content,
        scope=req.scope or "personal",
        title=req.title or "",
        keywords=req.keywords,
        importance=req.importance or 3,
        conversation_id=req.conversation_id,
        is_authorized=True if req.is_authorized is None else req.is_authorized,
    )


@router.get("/memories")
async def list_memories_endpoint(
    request: Request,
    scope: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    return await saas_service.list_memories(db, user, scope=scope, search_query=search)


@router.get("/memories/contextual")
async def retrieve_contextual_memories_endpoint(
    request: Request,
    query: str = Query(...),
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    memories = await saas_service.retrieve_contextual_memories(db, user, query, limit=limit)
    return {"ok": True, "memories": memories}


@router.put("/memories/{memory_id}")
@router.patch("/memories/{memory_id}")
async def update_memory_endpoint(
    memory_id: str,
    updates: Dict[str, Any],
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    return await saas_service.update_memory(db, user, memory_id, updates)


@router.delete("/memories/{memory_id}")
async def delete_memory_endpoint(
    memory_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    return await saas_service.delete_memory(db, user, memory_id)


# ==============================================================================
# 5. BILLING, SUBSCRIPTIONS, PROMO CODES, REFERRALS & USAGE
# ==============================================================================

@router.post("/billing/promo/validate")
async def validate_promo_endpoint(
    req: PromoValidateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await saas_service.get_current_user(request, db)
    promo = await saas_service.validate_promo_code(db, req.code, req.plan_code)
    return {
        "ok": True,
        "promo": {
            "code": promo.code,
            "description": promo.description,
            "discount_pct": promo.discount_pct,
            "discount_fixed_usd": promo.discount_fixed_usd,
            "bonus_credits": promo.bonus_credits,
            "trial_days_bonus": promo.trial_days_bonus,
        },
    }


@router.post("/billing/checkout")
async def checkout_endpoint(
    req: CheckoutRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    return await saas_service.checkout_subscription(
        db=db,
        user=user,
        target_plan_code=req.plan_code,
        billing_cycle=req.billing_cycle or "monthly",
        promo_code=req.promo_code,
        payment_method_brand=req.payment_method_brand or "visa",
        payment_method_last4=req.payment_method_last4 or "4242",
        external_tx_id=req.external_tx_id,
        ip_address=_get_client_ip(request),
    )


@router.post("/billing/cancel")
async def cancel_subscription_endpoint(
    req: CancelSubscriptionRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    return await saas_service.cancel_subscription(db, user, immediate=bool(req.immediate))


@router.get("/billing/history")
async def billing_history_endpoint(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    return await saas_service.list_billing_history(db, user)


@router.post("/billing/webhook")
async def stripe_webhook_endpoint(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    raw_body = await request.body()
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="JSON de webhook inválido.")
    sig = request.headers.get("Stripe-Signature")
    return await saas_service.process_payment_webhook(db, raw_body, sig, payload)


@router.get("/usage")
async def get_usage_details_endpoint(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    plan = await saas_service.get_plan(db, user.plan_code)
    balance = await saas_service.get_or_create_credit_balance(db, user)

    recs_res = await db.execute(
        select(SaasUsageRecord)
        .where(SaasUsageRecord.user_id == user.id)
        .order_by(desc(SaasUsageRecord.created_at))
        .limit(50)
    )
    records = recs_res.scalars().all()

    by_model: Dict[str, int] = {}
    by_skill: Dict[str, int] = {}
    for r in records:
        by_model[r.model_used] = by_model.get(r.model_used, 0) + r.credits_charged
        if r.skill_used:
            by_skill[r.skill_used] = by_skill.get(r.skill_used, 0) + r.credits_charged

    user_serialized = saas_service.serialize_user(user, plan, balance)
    return {
        "ok": True,
        "plan_code": plan.code,
        "summary": user_serialized["usage"],
        "consumption_by_model": by_model,
        "consumption_by_skill": by_skill,
        "recent_requests": [
            {
                "id": r.id,
                "model_used": r.model_used,
                "skill_used": r.skill_used,
                "total_tokens": r.total_tokens,
                "credits_charged": r.credits_charged,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records[:20]
        ],
    }


@router.get("/referrals")
async def get_referrals_endpoint(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await saas_service.get_current_user(request, db)
    refs_res = await db.execute(
        select(SaasReferral).where(SaasReferral.referrer_user_id == user.id).order_by(desc(SaasReferral.created_at))
    )
    referrals = refs_res.scalars().all()
    return {
        "ok": True,
        "referral_code": user.referral_code,
        "total_referrals": len(referrals),
        "rewarded_referrals": sum(1 for r in referrals if r.status == "rewarded"),
        "total_credits_earned": sum(r.referrer_reward_credits for r in referrals if r.status == "rewarded"),
        "referrals": [
            {
                "id": r.id,
                "referred_user_id": r.referred_user_id,
                "status": r.status,
                "reward_credits": r.referrer_reward_credits,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in referrals
        ],
    }


# ==============================================================================
# 6. EXCLUSIVE CREATOR SUPERADMIN ENDPOINTS (SEÑOR SANTIAGO ONLY)
# ==============================================================================

@router.get("/admin/dashboard")
async def creator_dashboard_endpoint(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    creator = await saas_service.require_creator(request, db)
    return await saas_service.get_creator_dashboard(db, creator)


@router.get("/admin/users")
async def creator_list_users_endpoint(
    request: Request,
    search: Optional[str] = Query(None),
    plan: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    await saas_service.require_creator(request, db)
    return await saas_service.admin_list_users(db, search=search, plan_filter=plan)


@router.put("/admin/users/{target_user_id}")
@router.patch("/admin/users/{target_user_id}")
async def creator_update_user_endpoint(
    target_user_id: str,
    updates: Dict[str, Any],
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    creator = await saas_service.require_creator(request, db)
    return await saas_service.admin_update_user(db, creator, target_user_id, updates)


@router.put("/admin/plans/{plan_code}")
@router.patch("/admin/plans/{plan_code}")
async def creator_update_plan_endpoint(
    plan_code: str,
    updates: Dict[str, Any],
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    creator = await saas_service.require_creator(request, db)
    return await saas_service.admin_update_plan(db, creator, plan_code, updates)


@router.post("/admin/skills")
async def creator_upsert_skill_endpoint(
    skill_data: Dict[str, Any],
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    creator = await saas_service.require_creator(request, db)
    return await saas_service.admin_upsert_skill(db, creator, skill_data)


@router.post("/admin/refunds")
async def creator_issue_refund_endpoint(
    req: RefundRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    creator = await saas_service.require_creator(request, db)
    return await saas_service.admin_issue_refund(db, creator, req.payment_id, req.reason or "")


@router.post("/admin/promos")
async def creator_create_promo_endpoint(
    promo_data: Dict[str, Any],
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    creator = await saas_service.require_creator(request, db)
    code = str(promo_data.get("code") or "").strip().upper()
    if not code:
        raise HTTPException(status_code=400, detail="Código promocional requerido.")
    import uuid
    promo = SaasPromoCode(
        id=f"promo_{uuid.uuid4().hex[:12]}",
        code=code,
        description=str(promo_data.get("description") or ""),
        discount_pct=float(promo_data.get("discount_pct") or 10.0),
        discount_fixed_usd=float(promo_data.get("discount_fixed_usd") or 0.0),
        bonus_credits=int(promo_data.get("bonus_credits") or 0),
        applicable_plans=promo_data.get("applicable_plans") or ["STARTER", "PRO", "BUSINESS", "ENTERPRISE"],
        max_uses=int(promo_data.get("max_uses") or 500),
        is_active=True,
    )
    db.add(promo)
    await saas_service.log_audit(
        db=db,
        action="creator_created_promo",
        actor_user=creator,
        resource_type="promo",
        resource_id=code,
        details=promo_data,
    )
    await db.commit()
    return {"ok": True, "code": promo.code, "discount_pct": promo.discount_pct}
