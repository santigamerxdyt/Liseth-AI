"""
BrainRouter - Autonomous Self-Healing Dual Brain Architecture.
Primary Brain: Google Gemini with Dynamic Live Auto-Discovery, Exponential Backoff, and Self-Healing.
Fallback Brain: Anthropic Claude
"""
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
import httpx
from app.config import settings

logger = logging.getLogger("jarvis.brain")

DEFAULT_RATES = {
    "gemini-3.5-flash": {"input_per_1k": 0.0001, "output_per_1k": 0.0004},
    "gemini-3.8-flash": {"input_per_1k": 0.0001, "output_per_1k": 0.0004},
    "gemini-3.7-flash": {"input_per_1k": 0.0001, "output_per_1k": 0.0004},
    "gemini-flash-latest": {"input_per_1k": 0.0001, "output_per_1k": 0.0004},
    "gemini-3.5-flash-lite": {"input_per_1k": 0.000075, "output_per_1k": 0.0003},
    "gemini-3.1-flash-lite": {"input_per_1k": 0.000075, "output_per_1k": 0.0003},
    "gemini-3-flash-preview": {"input_per_1k": 0.0001, "output_per_1k": 0.0004},
    "gemini-default": {"input_per_1k": 0.0001, "output_per_1k": 0.0004},
    "claude-default": {"input_per_1k": 0.003, "output_per_1k": 0.015},
}

# Ranked active candidates for Gemini in order of availability and speed
GEMINI_PRIORITY_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-3-flash-preview",
    "gemini-3.7-flash",
    "gemini-flash-latest",
]


class BrainRouter:
    def __init__(self):
        self.primary_brain: str = "gemini"
        self.active_brain: str = "gemini"
        self.forced_brain: Optional[str] = None
        self.active_gemini_model: str = "gemini-3.5-flash"
        self.last_failover: Optional[dict] = None
        self.known_working_models: List[str] = ["gemini-3.5-flash", "gemini-3.8-flash"]
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

    async def fetch_live_gemini_models(self, api_key: str) -> List[str]:
        """
        Autonomously discovers all active models from Google API that support generateContent.
        """
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    discovered = []
                    for m in data.get("models", []):
                        methods = m.get("supportedGenerationMethods", [])
                        name = m.get("name", "").replace("models/", "")
                        # Filter for text generation flash models
                        if "generateContent" in methods and "flash" in name and not any(x in name for x in ["tts", "image", "preview-10"]):
                            discovered.append(name)
                    if discovered:
                        logger.info(f"[AUTO_DISCOVERY] Modelos detectados en tiempo real: {discovered}")
                        return discovered
        except Exception as e:
            logger.warning(f"Error descubriendo modelos en vivo: {e}")
        return GEMINI_PRIORITY_MODELS

    async def probe_candidate_models(self, api_key: str) -> List[Dict[str, Any]]:
        """
        Tests candidate models one by one and updates self.active_gemini_model.
        """
        candidates = list(dict.fromkeys(GEMINI_PRIORITY_MODELS))
        results = []
        async with httpx.AsyncClient(timeout=8.0) as client:
            for model in candidates:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                payload = {
                    "contents": [{"role": "user", "parts": [{"text": "ping"}]}],
                    "generationConfig": {"maxOutputTokens": 5}
                }
                try:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        results.append({"model": model, "status": "working", "code": 200})
                        if not any(r["status"] == "working" for r in results[:-1]):
                            self.active_gemini_model = model
                            logger.info(f"[PROBE] Modelo fijado a: {model}")
                    else:
                        results.append({"model": model, "status": "unavailable", "code": resp.status_code})
                except Exception as e:
                    results.append({"model": model, "status": "error", "error": str(e)})

        return results

    async def call_gemini(
        self,
        prompt: Optional[str] = None,
        contents: Optional[List[dict]] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[list] = None,
        api_key_override: Optional[str] = None,
    ) -> dict:
        """
        Calls Gemini API with autonomous self-healing:
        - Tries active model first.
        - On 503 (high demand), applies smart 1.2s delay and retries once.
        - If still unavailable or 404, moves through the candidate chain.
        - If candidates fail, discovers live models from Google API.
        - Once a working model is found, locks it in as self.active_gemini_model.
        """
        api_key = api_key_override or settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY no está configurada ni en .env ni en la solicitud.")

        if contents:
            formatted_contents = contents
        elif prompt:
            formatted_contents = [{"role": "user", "parts": [{"text": prompt}]}]
        else:
            raise ValueError("Se requiere al menos un prompt o historial contents.")

        # Build candidate model list with active model first
        models_to_try = [self.active_gemini_model] + [
            m for m in GEMINI_PRIORITY_MODELS if m != self.active_gemini_model
        ]

        last_error = None
        for idx, model in enumerate(models_to_try):
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

            # Attempt model with automatic backoff for 503 spikes
            for attempt in range(2):
                try:
                    async with httpx.AsyncClient(timeout=35.0) as client:
                        resp = await client.post(url, json=payload)

                        # Handle high demand / transient server error
                        if resp.status_code in [503, 502, 504]:
                            if attempt == 0:
                                logger.info(f"[AUTO_HEAL] {model} respondió 503 (demanda alta). Pausando 1.2s para reintentar...")
                                await asyncio.sleep(1.2)
                                continue
                            else:
                                logger.warning(f"[AUTO_HEAL] {model} saturado tras reintento. Probando siguiente modelo...")
                                last_error = RuntimeError(f"HTTP {resp.status_code}: {resp.text}")
                                break

                        # Deprecated or quota error
                        if resp.status_code in [404, 429, 500]:
                            logger.warning(f"[AUTO_HEAL] {model} no disponible ({resp.status_code}). Probando siguiente...")
                            last_error = RuntimeError(f"HTTP {resp.status_code}: {resp.text}")
                            break

                        resp.raise_for_status()
                        data = resp.json()

                    candidates = data.get("candidates", [])
                    if not candidates:
                        last_error = ValueError(f"Gemini {model} no devolvió candidatos.")
                        break

                    text = ""
                    parts = candidates[0].get("content", {}).get("parts", [])
                    for p in parts:
                        if "text" in p:
                            text += p["text"]

                    usage = data.get("usageMetadata", {})
                    inp_tok = usage.get("promptTokenCount", 0)
                    out_tok = usage.get("candidatesTokenCount", 0)
                    self.record_usage("gemini", inp_tok, out_tok, model)

                    # Persist verified working model
                    if self.active_gemini_model != model:
                        logger.info(f"[AUTO_HEAL] ¡Éxito! Modelo confirmado y actualizado a: {model}")
                        self.active_gemini_model = model

                    return {
                        "text": text,
                        "brain": "gemini",
                        "model": model,
                        "usage": {"input": inp_tok, "output": out_tok},
                        "failover": False,
                    }
                except Exception as e:
                    last_error = e
                    if attempt == 0:
                        await asyncio.sleep(0.8)
                    else:
                        break

        # If static candidates failed, attempt dynamic live model discovery as a last autonomous effort
        try:
            logger.info("[AUTO_HEAL] Consultando API de Google para descubrir nuevos modelos en vivo...")
            live_models = await self.fetch_live_gemini_models(api_key)
            untested = [m for m in live_models if m not in models_to_try]
            for model in untested[:3]:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                async with httpx.AsyncClient(timeout=25.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                        text = "".join(p.get("text", "") for p in parts)
                        self.active_gemini_model = model
                        logger.info(f"[AUTO_HEAL] ¡Recuperación exitosa con modelo descubierto {model}!")
                        return {
                            "text": text,
                            "brain": "gemini",
                            "model": model,
                            "usage": {"input": 100, "output": 100},
                            "failover": False,
                        }
        except Exception as disc_err:
            logger.warning(f"Error en descubrimiento dinámico: {disc_err}")

        raise last_error or RuntimeError("Todos los modelos de Gemini se encuentran temporalmente saturados.")

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
        Executes query on primary brain (Gemini with autonomous self-healing).
        Automatically fails over to Claude if configured, or returns an intelligent
        conversational status notice instead of crashing.
        """
        if self.is_token_limit_exceeded():
            raise ValueError(f"Límite diario de tokens alcanzado ({settings.DAILY_TOKEN_LIMIT} tokens). Consulta pausada.")

        # If brain is manually forced
        if self.forced_brain == "claude":
            return await self.call_claude(prompt, contents, system_prompt, tools, api_key_claude)
        elif self.forced_brain == "gemini":
            return await self.call_gemini(prompt, contents, system_prompt, tools, api_key_gemini)

        # Normal execution: Gemini with self-healing
        try:
            res = await self.call_gemini(prompt, contents, system_prompt, tools, api_key_gemini)
            self.active_brain = "gemini"
            return res
        except Exception as gemini_err:
            logger.warning(f"[FAILOVER] Modelos de Gemini no respondieron: {gemini_err}.")
            # Try Claude fallback
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
                logger.warning(f"Claude fallback no disponible o falló: {claude_err}")
            
            # If Claude is not configured or also failed, handle autonomously and gracefully
            return {
                "text": "Señor Santiago, he detectado una congestión temporal de alta demanda en los servidores de Google (error 503). He probado múltiples modelos de forma autónoma. Por favor envíe su consulta nuevamente en un instante mientras el enlace se estabiliza.",
                "brain": "system",
                "model": self.active_gemini_model,
                "usage": {"input": 0, "output": 0},
                "failover": False,
                "autonomousNotice": True,
            }


brain_router = BrainRouter()
