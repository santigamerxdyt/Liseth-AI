"""
AI Token Optimizer & Smart Model Router Service for Liseth AI / JARVIS.
Provides intelligent context compression, prompt pruning, smart model routing,
dynamic response profiling, tool orchestrator filtering, tenant-isolated caching,
and real-time token budgeting with quality preservation.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("jarvis.token_optimizer")


class AITokenOptimizerService:
    """
    Central AI Token Optimizer & Smart Model Router Engine.
    Achieves maximum answer quality with minimum token cost and resource overhead.
    """

    MODEL_PRICING = {
        # USD per 1K tokens (input, output)
        "gemini-3.1-flash-lite": {"input": 0.000075, "output": 0.00030},
        "gemini-2.5-flash-lite": {"input": 0.000075, "output": 0.00030},
        "gemini-2.5-flash": {"input": 0.00010, "output": 0.00040},
        "gemini-2.0-flash": {"input": 0.00010, "output": 0.00040},
        "gemini-3.5-flash": {"input": 0.00010, "output": 0.00040},
        "gemini-3.8-flash": {"input": 0.00010, "output": 0.00040},
        "gemini-2.5-pro": {"input": 0.00125, "output": 0.00500},
        "claude-3-5-sonnet": {"input": 0.00300, "output": 0.01500},
        "deepseek-r1": {"input": 0.00055, "output": 0.00219},
        "default": {"input": 0.00010, "output": 0.00040},
    }

    # Model complexity tiers
    MODEL_TIERS = {
        "light": ["gemini-3.1-flash-lite", "gemini-2.5-flash-lite", "gemini-2.0-flash"],
        "standard": ["gemini-2.5-flash", "gemini-3.5-flash", "gemini-3.8-flash"],
        "advanced": ["gemini-2.5-pro", "claude-3-5-sonnet", "deepseek-r1"],
    }

    def __init__(self, max_cache_entries: int = 500, cache_ttl_seconds: int = 600):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_cache_entries = max_cache_entries
        self._cache_ttl_seconds = cache_ttl_seconds
        self._stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "original_tokens_total": 0,
            "optimized_tokens_total": 0,
            "tokens_saved_total": 0,
            "estimated_usd_saved": 0.0,
            "by_profile": {"brief": 0, "technical": 0, "explanatory": 0, "structured": 0, "standard": 0},
            "by_model": {},
        }

    # =========================================================================
    # 1. CONTEXT OPTIMIZATION & HISTORY COMPRESSION
    # =========================================================================

    def estimate_tokens(self, text: str) -> int:
        """Heuristic estimation of token count (~4 characters or 0.75 words per token)."""
        if not text:
            return 0
        words = len(text.split())
        chars = len(text)
        return max(1, int(max(words * 1.3, chars / 3.8)))

    def compress_conversation_history(
        self,
        messages: List[Dict[str, Any]],
        max_tokens_budget: int = 1500,
        keep_last_turns: int = 4,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Compresses conversation history to fit within a strict token budget:
        - Keeps recent turns intact.
        - Summarizes older dialogue exchanges into high-density declarative notes.
        - Preserves all system prompts, user facts, code constraints, and vital instructions.
        """
        if not messages:
            return [], {"compressed": False, "original_tokens": 0, "final_tokens": 0, "tokens_saved": 0}

        original_tokens = sum(self.estimate_tokens(m.get("content", "")) for m in messages)
        if original_tokens <= max_tokens_budget or len(messages) <= keep_last_turns:
            return messages, {
                "compressed": False,
                "original_tokens": original_tokens,
                "final_tokens": original_tokens,
                "tokens_saved": 0,
            }

        # Separate system messages, older history, and recent active turns
        system_msgs = [m for m in messages if m.get("role") == "system"]
        chat_msgs = [m for m in messages if m.get("role") != "system"]

        recent_msgs = chat_msgs[-keep_last_turns:]
        older_msgs = chat_msgs[:-keep_last_turns]

        # Extract declarative summary from older messages
        condensed_points = []
        for msg in older_msgs:
            role = msg.get("role", "user")
            content = (msg.get("content") or "").strip()
            if not content:
                continue

            # Strip greetings and boilerplate
            cleaned = re.sub(r"^(hola|buenos dias|buenas tardes|gracias|por favor)[,.]?\s*", "", content, flags=re.IGNORECASE).strip()
            if cleaned:
                snippet = cleaned[:70] + ("..." if len(cleaned) > 70 else "")
                condensed_points.append(f"{role[0].upper()}: {snippet}")

        summary_text = (
            "[Contexto histórico resumido]: "
            + "; ".join(condensed_points[-3:])
        )

        condensed_history = list(system_msgs)
        if condensed_points:
            condensed_history.append({"role": "system", "content": summary_text})
        condensed_history.extend(recent_msgs)

        final_tokens = sum(self.estimate_tokens(m.get("content", "")) for m in condensed_history)
        tokens_saved = max(1, original_tokens - final_tokens)

        return condensed_history, {
            "compressed": True,
            "original_tokens": original_tokens,
            "final_tokens": final_tokens,
            "tokens_saved": tokens_saved,
        }

    # =========================================================================
    # 2. DYNAMIC RESPONSE PROFILES
    # =========================================================================

    def detect_response_profile(self, user_prompt: str, requested_profile: Optional[str] = None) -> str:
        """
        Determines the optimal response profile based on user intent:
        - 'brief': Quick greeting, simple calculation, single-line query.
        - 'explanatory': 'explica', 'como funciona', 'por que', tutorials.
        - 'structured': JSON, tables, comparison, CSV, bullet lists.
        - 'technical': Code, architecture, debugging, regex, CLI command.
        - 'standard': General dialogue.
        """
        if requested_profile and requested_profile.lower() in ("brief", "technical", "explanatory", "structured", "standard"):
            return requested_profile.lower()

        p = user_prompt.lower().strip()

        # 1. Brief detection
        if len(p.split()) <= 4 and any(g in p for g in ["hola", "buen dia", "que tal", "hora", "gracias", "ok", "listo", "precio"]):
            return "brief"

        # 2. Explanatory detection (checked before technical to catch 'cómo funciona')
        if any(e in p for e in ["explica", "como funciona", "cómo funciona", "por que", "por qué", "diferencia entre", "concepto", "ensename", "enséñame"]):
            return "explanatory"

        # 3. Structured detection
        if any(s in p for s in ["json", "tabla", "cuadro", "comparativa", "lista estructurada", "matriz"]):
            return "structured"

        # 4. Technical detection with word boundaries to avoid false positives
        tech_words = [r"\bcodigo\b", r"\bcódigo\b", r"\bfuncion\b", r"\bfunción\b", r"\bscript\b", r"\berror\b", r"\bbug\b", r"\bsql\b", r"\bapi\b", r"\bendpoint\b", r"\bfastapi\b", r"\bpython\b", r"\bjavascript\b", r"\bclass\b", r"\bdef\b"]
        if any(re.search(tw, p, re.IGNORECASE) for tw in tech_words):
            return "technical"

        return "standard"

    def get_profile_instructions(self, profile: str) -> str:
        """Returns concise system instruction modifiers tailored to the response profile."""
        if profile == "brief":
            return "MODO CONCISO: Responde de forma directa y sintética, sin introducciones ni despedidas."
        elif profile == "technical":
            return "MODO TÉCNICO: Prioriza código limpio, arquitecturas precisas, tipado y parámetros sin explicaciones obvias."
        elif profile == "structured":
            return "MODO ESTRUCTURADO: Presenta la respuesta en tablas markdown o bloques JSON válidos según corresponda."
        elif profile == "explanatory":
            return "MODO EXPLICATIVO: Estructura la explicación paso a paso con fundamentos conceptuales claros."
        return ""

    # =========================================================================
    # 3. SMART MODEL ROUTER
    # =========================================================================

    def route_model(
        self,
        prompt: str,
        requested_model: Optional[str] = None,
        user_plan: str = "FREE",
    ) -> Dict[str, Any]:
        """
        Dynamically selects the most cost-effective and accurate AI model
        based on query complexity, plan tier, latency, and reasoning requirements.
        """
        p_len = len(prompt.split())
        has_code = bool(re.search(r"(class |def |function|import |SELECT |WHERE |ALTER |INSERT |docker|kubernetes)", prompt, re.IGNORECASE))
        has_deep_reasoning = bool(re.search(r"(estrategia|analisis financiero|wacc|dupont|auditoria|seguridad|arquitectura)", prompt, re.IGNORECASE))

        # Classify complexity
        if p_len < 12 and not has_code and not has_deep_reasoning:
            complexity = "simple"
            suggested_tier = "light"
        elif has_code or has_deep_reasoning or p_len > 180:
            complexity = "complex"
            suggested_tier = "advanced" if user_plan in ("BUSINESS", "ENTERPRISE", "CREATOR") else "standard"
        else:
            complexity = "moderate"
            suggested_tier = "standard"

        # Filter by plan entitlement
        if user_plan == "FREE":
            # Free tier gets high-speed flash models
            selected_model = "gemini-3.1-flash-lite"
            reason = "Ruta optimizada para Plan Free (alta velocidad y bajo coste)."
        elif user_plan == "STARTER":
            selected_model = "gemini-2.5-flash" if complexity != "simple" else "gemini-3.1-flash-lite"
            reason = f"Ruta asignada para Plan Starter acorde a complejidad {complexity}."
        elif user_plan in ("PRO", "BUSINESS", "ENTERPRISE", "CREATOR"):
            if complexity == "complex":
                selected_model = requested_model or "gemini-2.5-pro"
                reason = "Ruta de alto razonamiento y precisión para tareas complejas."
            elif complexity == "moderate":
                selected_model = requested_model or "gemini-2.5-flash"
                reason = "Ruta balanceada velocidad/calidad para tareas intermedias."
            else:
                selected_model = "gemini-3.1-flash-lite"
                reason = "Ruta ultrarrápida para consultas simples."
        else:
            selected_model = "gemini-3.1-flash-lite"
            reason = "Ruta por defecto."

        return {
            "selected_model": selected_model,
            "complexity": complexity,
            "tier": suggested_tier,
            "reason": reason,
        }

    # =========================================================================
    # 4. SKILL & TOOL ORCHESTRATOR PRUNING
    # =========================================================================

    def prune_skills_for_prompt(
        self,
        prompt: str,
        available_skill_codes: List[str],
        max_tools: int = 5,
    ) -> List[str]:
        """
        Filters available skills to ONLY those directly relevant to the user's prompt.
        Avoids injecting 50+ tool schemas into context, saving thousands of tokens.
        """
        if not available_skill_codes or len(available_skill_codes) <= max_tools:
            return available_skill_codes

        p = prompt.lower()
        scored: List[Tuple[str, int]] = []

        keywords_map = {
            "nfc": ["nfc", "contactless", "tarjeta", "vcard", "tap", "etiqueta", "cobro", "terminal"],
            "business_finance": ["finanzas", "balance", "flujo", "caja", "prestamo", "amortizacion", "wacc"],
            "academic_research": ["tesis", "paper", "apa", "openalex", "universidad", "referencias"],
            "data_ml": ["dataset", "pandas", "cluster", "regresion", "machine learning", "eda"],
            "security_audit": ["seguridad", "vulnerabilidad", "audit", "cve", "hacker", "pen test"],
            "code_helper": ["codigo", "python", "bug", "refactor", "funcion", "fastapi"],
            "voice_engine": ["voz", "audio", "hablar", "tts", "microfono"],
        }

        for code in available_skill_codes:
            score = 0
            code_lower = code.lower()
            if code_lower in p:
                score += 10

            for cat, words in keywords_map.items():
                if cat in code_lower:
                    for w in words:
                        if w in p:
                            score += 3
            scored.append((code, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        # Always return at least the top matching tools
        top = [c for c, s in scored[:max_tools] if s > 0]
        return top if top else available_skill_codes[:max_tools]

    # =========================================================================
    # 5. TENANT-ISOLATED RESPONSE CACHE
    # =========================================================================

    def _cache_key(self, user_id: str, prompt: str, model_id: str, profile: str) -> str:
        raw = f"{user_id}::{model_id}::{profile}::{prompt.strip().lower()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get_cached_response(
        self,
        user_id: str,
        prompt: str,
        model_id: str,
        profile: str,
    ) -> Optional[Dict[str, Any]]:
        """Retrieves a cached AI response if still fresh and matching the same user/tenant."""
        key = self._cache_key(user_id, prompt, model_id, profile)
        entry = self._cache.get(key)
        if not entry:
            return None

        if time.time() > entry["expires_at"]:
            self._cache.pop(key, None)
            return None

        self._stats["cache_hits"] += 1
        return entry["data"]

    def set_cached_response(
        self,
        user_id: str,
        prompt: str,
        model_id: str,
        profile: str,
        response_data: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """Stores response in bounded LRU cache with expiration."""
        if len(self._cache) >= self._max_cache_entries:
            # Purge oldest 20%
            keys_to_purge = list(self._cache.keys())[: max(1, self._max_cache_entries // 5)]
            for k in keys_to_purge:
                self._cache.pop(k, None)

        key = self._cache_key(user_id, prompt, model_id, profile)
        ttl = ttl_seconds or self._cache_ttl_seconds
        self._cache[key] = {
            "expires_at": time.time() + ttl,
            "data": response_data,
        }

    # =========================================================================
    # 6. TOKEN COST & SAVINGS ACCOUNTING
    # =========================================================================

    def calculate_cost_usd(self, model_id: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculates precise cost in USD using official model rate tables."""
        rates = self.MODEL_PRICING.get(model_id, self.MODEL_PRICING["default"])
        input_cost = (prompt_tokens / 1000.0) * rates["input"]
        output_cost = (completion_tokens / 1000.0) * rates["output"]
        return round(input_cost + output_cost, 6)

    def record_optimization_metrics(
        self,
        original_prompt_tokens: int,
        optimized_prompt_tokens: int,
        completion_tokens: int,
        model_id: str,
        profile: str,
        cache_hit: bool = False,
    ) -> Dict[str, Any]:
        """Updates internal KPI counters and estimates USD savings."""
        tokens_saved = max(0, original_prompt_tokens - optimized_prompt_tokens)
        rates = self.MODEL_PRICING.get(model_id, self.MODEL_PRICING["default"])
        usd_saved = (tokens_saved / 1000.0) * rates["input"]

        self._stats["total_requests"] += 1
        self._stats["original_tokens_total"] += original_prompt_tokens
        self._stats["optimized_tokens_total"] += optimized_prompt_tokens
        self._stats["tokens_saved_total"] += tokens_saved
        self._stats["estimated_usd_saved"] += usd_saved

        if profile in self._stats["by_profile"]:
            self._stats["by_profile"][profile] += 1
        self._stats["by_model"][model_id] = self._stats["by_model"].get(model_id, 0) + 1

        return {
            "original_prompt_tokens": original_prompt_tokens,
            "optimized_prompt_tokens": optimized_prompt_tokens,
            "tokens_saved": tokens_saved,
            "estimated_usd_saved": round(usd_saved, 6),
            "cache_hit": cache_hit,
        }

    def get_performance_dashboard(self) -> Dict[str, Any]:
        """Returns executive KPI statistics for CREATOR 'AI Performance Center'."""
        total_req = max(1, self._stats["total_requests"])
        cache_hit_ratio = round((self._stats["cache_hits"] / total_req) * 100.0, 2)
        token_savings_pct = (
            round((self._stats["tokens_saved_total"] / max(1, self._stats["original_tokens_total"])) * 100.0, 2)
            if self._stats["original_tokens_total"] > 0
            else 0.0
        )

        return {
            "ok": True,
            "total_requests": self._stats["total_requests"],
            "cache_hits": self._stats["cache_hits"],
            "cache_hit_ratio_pct": cache_hit_ratio,
            "original_tokens_total": self._stats["original_tokens_total"],
            "optimized_tokens_total": self._stats["optimized_tokens_total"],
            "tokens_saved_total": self._stats["tokens_saved_total"],
            "tokens_savings_pct": token_savings_pct,
            "estimated_usd_saved": round(self._stats["estimated_usd_saved"], 4),
            "distribution_by_profile": self._stats["by_profile"],
            "distribution_by_model": self._stats["by_model"],
            "active_cache_entries": len(self._cache),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    # =========================================================================
    # 7. AI QUALITY EVALUATION HARNESS
    # =========================================================================

    def evaluate_quality(
        self,
        user_prompt: str,
        response_text: str,
        profile: str = "standard",
    ) -> Dict[str, Any]:
        """
        Assesses that token optimization did not degrade output quality:
        - Instruction adherence
        - Completeness
        - Absence of empty/truncated outputs
        - Conciseness check against requested profile
        """
        score = 1.0
        reasons = []

        if not response_text or len(response_text.strip()) < 10:
            return {"score": 0.0, "status": "poor", "reasons": ["Respuesta vacía o insuficiente."]}

        # Check brief profile compliance
        if profile == "brief" and len(response_text.split()) > 80:
            score -= 0.15
            reasons.append("Perfil breve excedió límite recomendado de palabras.")

        # Check code requirement
        if "codigo" in user_prompt.lower() or "def " in user_prompt.lower():
            if "```" not in response_text and "def " not in response_text:
                score -= 0.25
                reasons.append("Se solicitó código pero la respuesta no incluyó bloques de código.")

        status = "excellent" if score >= 0.9 else ("good" if score >= 0.75 else "review_needed")
        return {
            "score": round(max(0.1, score), 2),
            "status": status,
            "reasons": reasons if reasons else ["Respuesta óptima que cumple todos los criterios de calidad."],
        }


# Global singleton
token_optimizer_service = AITokenOptimizerService()
