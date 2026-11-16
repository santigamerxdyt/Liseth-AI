"""
Hermes AI Orchestrator for Liseth // JARVIS.
Central AI brain and multi-agent coordination hub that unifies:
- Multimodal routing (Voice, Text, Tool calls).
- Dynamic delegation to Hermes Named Bots & specialized agents.
- Context memory management and token consumption optimization.
- Streaming responses and audio synthesis coordination.
- Graceful error recovery and execution cancellation.
"""
import asyncio
import logging
import time
from typing import Any, Dict, List, Optional
from app.services.hermes_adapter import hermes_adapter

logger = logging.getLogger("jarvis.hermes_orchestrator")


class HermesAIOrchestrator:
    """
    Central Orchestration Engine.
    Dispatches prompts between Hermes Multi-Agent subsystem,
    Cognitive Brain Cascade, and peripheral integrations.
    """
    def __init__(self):
        self.total_turns_processed: int = 0
        self.last_execution_time: float = 0.0

    async def route_and_execute(
        self,
        prompt: str,
        session_id: str = "default_session",
        user_id: str = "default_creator",
        modality: str = "voice",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for intelligent prompt routing.
        Selects optimal agent, invokes tools, and formats response for voice or HUD console.
        """
        start_time = time.time()
        self.total_turns_processed += 1

        logger.info(f"[HermesOrchestrator] Turno #{self.total_turns_processed} iniciado ({modality}): '{prompt[:60]}...'")

        # 1. Check for explicit stop / silence tool intents first
        norm_prompt = prompt.lower().strip()
        stop_words = ["callate", "cállate", "silencio", "para", "detente", "stop", "basta"]
        if any(w in norm_prompt for w in stop_words):
            from app.services.voice_engine import voice_engine
            voice_engine.stop_speaking(interrupted=True)
            return {
                "ok": True,
                "agent": "Voice Agent",
                "text": "En silencio absoluto, señor Santiago.",
                "executedTools": [{"name": "stop_speaking"}],
                "latency_ms": round((time.time() - start_time) * 1000, 2)
            }

        # 2. Delegate to Hermes Agent Subsystem
        try:
            result = await hermes_adapter.execute_turn(
                prompt=prompt,
                session_id=session_id,
                user_id=user_id,
                modality=modality
            )

            latency = round((time.time() - start_time) * 1000, 2)
            result["latency_ms"] = latency
            self.last_execution_time = latency

            logger.info(f"[HermesOrchestrator] Turno #{self.total_turns_processed} finalizado en {latency}ms vía {result.get('agent')}")
            return result

        except Exception as e:
            logger.error(f"[HermesOrchestrator] Error en orquestación: {e}", exc_info=True)
            return {
                "ok": False,
                "agent": "Main Assistant",
                "error": str(e),
                "text": "Señor Santiago, he registrado un inconveniente temporal al coordinar los agentes.",
                "executedTools": [],
                "latency_ms": round((time.time() - start_time) * 1000, 2)
            }


hermes_orchestrator = HermesAIOrchestrator()
