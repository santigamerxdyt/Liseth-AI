"""
BrainRouter - Dual Brain Architecture with Automatic Failover, Model Redundancy, and Token Cost Tracking.
Primary Brain: Google Gemini (with model fallback: gemini-2.0-flash -> gemini-1.5-flash)
Fallback Brain: Anthropic Claude
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
import httpx
from app.config import settings

logger = logging.getLogger("jarvis.brain")

DEFAULT_RATES = {
    "gemini-2.0-flash": {"input_per_1k": 0.0001, "output_per_1k": 0.0004},
    "gemini-1.5-flash": {"input_per_1k": 0.000075, "output_per_1k": 0.0003},
    "gemini-1.5-pro": {"input_per_1k": 0.00125, "output_per_1k": 0.005},
    "gemini-2.5-flash": {"input_per_1k": 0.0001, "output_per_1k": 0.0004},
    "claude-3-5-sonnet-20241022": {"input_per_1k": 0.003, "output_per_1k": 0.015},
    "claude-3-5-sonnet": {"input_per_1k": 0.003, "output_per_1k": 0.015},
    "claude-3-5-haiku-20241022": {"input_per_1k": 0.0008, "output_per_1k": 0.004},
    "claude-3-5-haiku": {"input_per_1k": 0.0008, "output_per_1k": 0.004},
    "gemini-default": {"input_per_1k": 0.0001, "output_per_1k": 0.0004},
    "claude-default": {"input_per_1k": 0.003, "output_per_1k": 0.015},
}

# Reliable fallback chain for Gemini
GEMINI_MODELS_CHAIN = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]


class BrainRouter:
    def __init__(self):
        self.primary_brain: str = "gemini"
        self.active_brain: str = "gemini"
        self.forced_brain: Optional[str] = None
        self.last_failover: Optional[dict] = None
        self.stats: dict = {
            "today_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "today": {
                "input": 0,
                "output": 0,
                "cost_estimate": 0.0,
                "by_brain": {
                    "gemini": {"input": 0, "output": 0, "cost_estimate": 0.0},
                    "claude": {"input": 0, "output": 0, "cost_estimate": 0.0},
                },
            },
            "month": {"input": 0, "output": 0, "cost_estimate": 0.0},
        }

    def _check_daily_rollover(self):
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if self.stats.get("today_date") != today_str:
            self.stats["today_date"] = today_str
            self.stats["today"] = {
                "input": 0,
                "output": 0,
                "cost_estimate": 0.0,
                "by_brain": {
                    "gemini": {"input": 0, "output": 0, "cost_estimate": 0.0},
                    "claude": {"input": 0, "output": 0, "cost_estimate": 0.0},
                },
            }

    def record_usage(self, brain: str, input_tokens: int, output_tokens: int, model: Optional[str] = None):
        """Records token consumption and estimates cost."""
        self._check_daily_rollover()
        rates = DEFAULT_RATES.get(model or f"{brain}-default", DEFAULT_RATES[f"{brain}-default"])
        cost = (input_tokens / 1000.0 * rates["input_per_1k"]) + (output_tokens / 1000.0 * rates["output_per_1k"])

        self.stats["today"]["input"] += input_tokens
        self.stats["today"]["output"] += output_tokens
        self.stats["today"]["cost_estimate"] += cost

        brain_stats = self.stats["today"]["by_brain"].setdefault(brain, {"input": 0, "output": 0, "cost_estimate": 0.0})
        brain_stats["input"] += input_tokens
        brain_stats["output"] += output_tokens
        brain_stats["cost_estimate"] += cost

        self.stats["month"]["input"] += input_tokens
        self.stats["month"]["output"] += output_tokens
        self.stats["month"]["cost_estimate"] += cost

    def is_token_limit_exceeded(self) -> bool:
        """Checks if daily token usage exceeds the configured ceiling."""
        self._check_daily_rollover()
        total_today = self.stats["today"]["input"] + self.stats["today"]["output"]
        return total_today >= settings.DAILY_TOKEN_LIMIT

    async def call_gemini(
        self,
        prompt: Optional[str] = None,
        contents: Optional[List[dict]] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[list] = None,
        api_key_override: Optional[str] = None,
    ) -> dict:
        """
        Calls Gemini API with automatic model retry (gemini-2.0-flash -> gemini-1.5-flash)
        if Google returns 503 Unavailable / High Demand.
        """
        api_key = api_key_override or settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY no está configurada ni en .env ni en la solicitud.")

        # Prepare contents
        if contents:
            formatted_contents = contents
        elif prompt:
            formatted_contents = [{"role": "user", "parts": [{"text": prompt}]}]
        else:
            raise ValueError("Se requiere al menos un prompt o historial contents.")

        preferred_model = settings.GEMINI_MODEL
        models_to_try = [preferred_model] + [m for m in GEMINI_MODELS_CHAIN if m != preferred_model]

        last_error = None
        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload: Dict[str, Any] = {
                "contents": formatted_contents,
                "generationConfig": {
                    "temperature": 0.75,
                    "maxOutputTokens": 3000,
                }
            }
            if system_prompt:
                payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

            try:
                async with httpx.AsyncClient(timeout=45.0) as client:
                    resp = await client.post(url, json=payload)

                    if resp.status_code in [503, 429, 500, 502, 504]:
                        logger.warning(f"Gemini {model} respondió con estado {resp.status_code}. Probando siguiente modelo...")
                        last_error = RuntimeError(f"HTTP {resp.status_code}: {resp.text}")
                        continue

                    resp.raise_for_status()
                    data = resp.json()

                candidates = data.get("candidates", [])
                if not candidates:
                    last_error = ValueError(f"Gemini {model} no devolvió candidatos válidos.")
                    continue

                text = ""
                parts = candidates[0].get("content", {}).get("parts", [])
                for p in parts:
                    if "text" in p:
                        text += p["text"]

                usage = data.get("usageMetadata", {})
                inp_tok = usage.get("promptTokenCount", 0)
                out_tok = usage.get("candidatesTokenCount", 0)
                self.record_usage("gemini", inp_tok, out_tok, model)

                return {
                    "text": text,
                    "brain": "gemini",
                    "model": model,
                    "usage": {"input": inp_tok, "output": out_tok},
                    "failover": False,
                }
            except Exception as e:
                logger.warning(f"Error con modelo {model}: {e}")
                last_error = e
                continue

        raise last_error or RuntimeError("Todos los modelos de Gemini fallaron.")

    async def call_claude(
        self,
        prompt: Optional[str] = None,
        contents: Optional[List[dict]] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[list] = None,
        api_key_override: Optional[str] = None,
    ) -> dict:
        """Calls Anthropic Claude API using httpx."""
        api_key = api_key_override or settings.ANTHROPIC_API_KEY
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY no está configurada para failover.")

        model = settings.ANTHROPIC_MODEL
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        # Convert contents to Claude format if needed
        claude_messages = []
        if contents:
            for item in contents:
                role = "assistant" if item.get("role") in ["model", "assistant"] else "user"
                parts = item.get("parts", [])
                text_part = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
                if text_part:
                    claude_messages.append({"role": role, "content": text_part})
        elif prompt:
            claude_messages.append({"role": "user", "content": prompt})

        if not claude_messages:
            claude_messages.append({"role": "user", "content": "Hola"})

        payload: Dict[str, Any] = {
            "model": model,
            "max_tokens": 4096,
            "messages": claude_messages,
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        text = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                text += block.get("text", "")

        usage = data.get("usage", {})
        inp_tok = usage.get("input_tokens", 0)
        out_tok = usage.get("output_tokens", 0)
        self.record_usage("claude", inp_tok, out_tok, model)

        return {
            "text": text,
            "brain": "claude",
            "model": model,
            "usage": {"input": inp_tok, "output": out_tok},
            "failover": True,
        }

    async def generate_response(
        self,
        prompt: Optional[str] = None,
        contents: Optional[List[dict]] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[list] = None,
        api_key_gemini: Optional[str] = None,
        api_key_claude: Optional[str] = None,
    ) -> dict:
        """
        Executes query on primary brain (Gemini).
        Automatically fails over to Claude if Gemini fails.
        """
        if self.is_token_limit_exceeded():
            raise ValueError(f"Límite diario de tokens alcanzado ({settings.DAILY_TOKEN_LIMIT} tokens). Consulta pausada.")

        # If brain is manually forced
        if self.forced_brain == "claude":
            return await self.call_claude(prompt, contents, system_prompt, tools, api_key_claude)
        elif self.forced_brain == "gemini":
            return await self.call_gemini(prompt, contents, system_prompt, tools, api_key_gemini)

        # Normal execution: Gemini first
        try:
            res = await self.call_gemini(prompt, contents, system_prompt, tools, api_key_gemini)
            self.active_brain = "gemini"
            return res
        except Exception as gemini_err:
            logger.warning(f"[FAILOVER] Gemini falló: {gemini_err}. Conmutando a Claude de respaldo...")
            try:
                res = await self.call_claude(prompt, contents, system_prompt, tools, api_key_claude)
                self.active_brain = "claude"
                self.last_failover = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "reason": str(gemini_err),
                    "fallback": "claude",
                }
                return res
            except Exception as claude_err:
                logger.error(f"Ambos cerebros fallaron: Gemini ({gemini_err}) | Claude ({claude_err})")
                raise RuntimeError(f"Falla total de IA: Gemini ({gemini_err}) | Claude ({claude_err})")


brain_router = BrainRouter()
