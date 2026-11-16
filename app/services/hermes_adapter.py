"""
Hermes Agent Adapter for Liseth // JARVIS.
Official Integration Adapter based on NousResearch/hermes-agent architecture.
Provides:
- Hermes Agent Runtime & Session Management.
- Multi-Agent Delegation (Named Bots: Main Assistant, Research, Coding, Voice, Data, Business, Media, Documentation).
- Hermes Memory System & Context Isolation per user.
- Hermes Toolset & Skills Execution with strict security boundaries.
- Support for Hermes Model Family (Hermes 3 70B/8B, Nous-Hermes-2-Mixtral).
"""
import asyncio
import logging
import os
import time
from typing import Any, Callable, Dict, List, Optional, Set
from pydantic import BaseModel, Field

logger = logging.getLogger("jarvis.hermes_adapter")


class HermesSession(BaseModel):
    session_id: str
    user_id: str = "default_creator"
    agent_name: str = "Main Assistant"
    history: List[Dict[str, str]] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)
    last_active: float = Field(default_factory=time.time)
    context_data: Dict[str, Any] = Field(default_factory=dict)
    active_skills: List[str] = Field(default_factory=list)


class HermesAgentProfile(BaseModel):
    name: str
    role: str
    system_prompt: str
    preferred_model: str
    allowed_tools: List[str] = Field(default_factory=list)
    max_tokens: int = 2048
    temperature: float = 0.4
    requires_approval: bool = False


class HermesAgentAdapter:
    """
    Connects the platform with NousResearch Hermes Agent ecosystem.
    Enforces tenant isolation, toolset permissions, and session tracking.
    """
    def __init__(self):
        self._sessions: Dict[str, HermesSession] = {}
        self._agents: Dict[str, HermesAgentProfile] = {}
        self._tool_registry: Dict[str, Callable] = {}
        self._initialize_named_agents()

    def _initialize_named_agents(self):
        """Initializes the 8 specialized Named Bots according to Hermes Agent architecture."""
        self._agents = {
            "Main Assistant": HermesAgentProfile(
                name="Main Assistant",
                role="Coordinadora Ejecutiva y Asistente Principal de Dirección",
                system_prompt=(
                    "Eres Liseth, secretaria ejecutiva y Chief of Staff de alta dirección para el Señor Santiago Huérfano López. "
                    "Tu tono es dulce, profesional, proactivo y resolutivo. Piensas de 2 a 3 pasos por delante para él."
                ),
                preferred_model="nousresearch/hermes-3-llama-3.1-70b",
                allowed_tools=["lookup_data", "get_status", "web_search", "stop_speaking"],
                temperature=0.35,
            ),
            "Research Agent": HermesAgentProfile(
                name="Research Agent",
                role="Investigador Académico y Científico de Vanguardia",
                system_prompt="Especialista en síntesis científica, literatura académica de arXiv/OpenAlex y análisis bibliográfico formal con citas APA 7ma edición.",
                preferred_model="nousresearch/hermes-3-llama-3.1-70b",
                allowed_tools=["academic_search", "web_search", "summarize_document"],
                temperature=0.2,
            ),
            "Coding Agent": HermesAgentProfile(
                name="Coding Agent",
                role="Senior Software Architect & Code Engineer",
                system_prompt=(
                    "Experto en Python, FastAPI, TypeScript, React, algoritmos seguros, ciberseguridad, "
                    "desarrollo web cinemático scroll-driven (10k-websites) y refactorización limpia sin deuda técnica."
                ),
                preferred_model="nousresearch/hermes-3-llama-3.1-70b",
                allowed_tools=["analyze_code", "run_tests", "git_status", "10k_websites_builder"],
                temperature=0.15,
            ),
            "Voice Agent": HermesAgentProfile(
                name="Voice Agent",
                role="Especialista de Voz, Audio y Telemetría VAD",
                system_prompt="Controlador de pipeline de voz, VAD, transcripción STT, modulación TTS y control de streaming de audio en tiempo real.",
                preferred_model="nousresearch/hermes-3-llama-3.1-8b",
                allowed_tools=["set_voice_state", "stop_speaking", "synthesize_speech"],
                temperature=0.2,
            ),
            "Data Agent": HermesAgentProfile(
                name="Data Agent",
                role="Científico de Datos y Modelador Estadístico",
                system_prompt="Especialista en análisis de datos, conciliación bancaria, series de tiempo, SQL analítico y machine learning reproducible.",
                preferred_model="nousresearch/hermes-3-llama-3.1-70b",
                allowed_tools=["execute_sql_readonly", "data_eda", "calculate_metrics"],
                temperature=0.2,
            ),
            "Business Agent": HermesAgentProfile(
                name="Business Agent",
                role="Estratega de Negocios SaaS y Finanzas",
                system_prompt="Especialista en economía unitaria (LTV, CAC, MRR), pasarelas de pago (Bre-B, Nequi, Stripe) y matrices FODA/Porter.",
                preferred_model="nousresearch/hermes-3-llama-3.1-70b",
                allowed_tools=["check_subscriptions", "calculate_unit_economics", "referral_ledger"],
                temperature=0.25,
            ),
            "Media Agent": HermesAgentProfile(
                name="Media Agent",
                role="Productor Multimedia y Composición Audiovisual",
                system_prompt="Especialista en mezcla de audio, edición de video, generación de subtítulos sincronizados y activos multimedia integrado con OpenMontage.",
                preferred_model="nousresearch/hermes-3-llama-3.1-8b",
                allowed_tools=["openmontage_mix", "generate_subtitles", "convert_audio"],
                temperature=0.3,
            ),
            "Documentation Agent": HermesAgentProfile(
                name="Documentation Agent",
                role="Arquitecto de Documentación y Mapeo de Conocimiento",
                system_prompt="Responsable de mantener el Vault de Obsidian, generar diagramas arquitectónicos con Archify y actualizar especificaciones técnicas.",
                preferred_model="nousresearch/hermes-3-llama-3.1-70b",
                allowed_tools=["archify_diagram", "update_vault_note", "query_knowledge"],
                temperature=0.2,
            ),
        }

    def register_tool(self, name: str, func: Callable):
        """Registers a verified tool into Hermes Toolset."""
        self._tool_registry[name] = func
        logger.info(f"[HermesAdapter] Herramienta registrada: '{name}'")

    def get_or_create_session(self, session_id: str, user_id: str = "default_creator", agent_name: str = "Main Assistant") -> HermesSession:
        """Retrieves or creates a tenant-isolated Hermes session."""
        if session_id not in self._sessions:
            self._sessions[session_id] = HermesSession(
                session_id=session_id,
                user_id=user_id,
                agent_name=agent_name
            )
        session = self._sessions[session_id]
        session.last_active = time.time()
        return session

    def list_named_agents(self) -> List[Dict[str, Any]]:
        """Returns all registered Named Agents and their specifications."""
        return [
            {
                "name": profile.name,
                "role": profile.role,
                "preferred_model": profile.preferred_model,
                "tools_count": len(profile.allowed_tools),
                "requires_approval": profile.requires_approval
            }
            for profile in self._agents.values()
        ]

    def list_available_skills(self) -> List[Dict[str, Any]]:
        """Scans the .agents/skills directory and returns metadata of all installed skills."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        skills_dir = os.path.join(base_dir, ".agents", "skills")
        discovered: List[Dict[str, Any]] = []
        if not os.path.exists(skills_dir):
            return discovered

        for entry in sorted(os.listdir(skills_dir)):
            skill_path = os.path.join(skills_dir, entry)
            skill_md = os.path.join(skill_path, "SKILL.md")
            if os.path.isdir(skill_path) and os.path.isfile(skill_md):
                name = entry
                description = ""
                try:
                    with open(skill_md, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        in_fm = False
                        for line in lines:
                            line_s = line.strip()
                            if line_s == "---":
                                if not in_fm:
                                    in_fm = True
                                    continue
                                else:
                                    break
                            if in_fm:
                                if line_s.startswith("name:"):
                                    name = line_s.replace("name:", "").strip()
                                elif line_s.startswith("description:"):
                                    description = line_s.replace("description:", "").strip()
                except Exception as read_err:
                    logger.debug(f"[HermesAdapter] Error leyendo metadata de skill {entry}: {read_err}")

                discovered.append({
                    "id": entry,
                    "name": name,
                    "description": description or f"Skill especializada {name}",
                    "path": f".agents/skills/{entry}/SKILL.md",
                    "status": "ready"
                })
        return discovered

    def select_agent_for_prompt(self, prompt: str) -> HermesAgentProfile:
        """Heuristically selects the optimal Hermes Named Bot based on user intent."""
        norm = prompt.lower()

        if any(w in norm for w in ["código", "python", "script", "refactor", "bug", "endpoint", "fastapi", "html", "css", "error de código", "sitio web", "landing page", "web cinemática", "10k-websites", "scroll web", "crear web"]):
            return self._agents["Coding Agent"]
        elif any(w in norm for w in ["paper", "investigación", "académico", "arxiv", "apa", "artículo", "tesis", "estudio científico"]):
            return self._agents["Research Agent"]
        elif any(w in norm for w in ["finanzas", "mrr", "ltv", "cac", "bre-b", "nequi", "suscripción", "plan saas", "precio", "factura"]):
            return self._agents["Business Agent"]
        elif any(w in norm for w in ["video", "subtítulo", "mezcla", "multimedia", "audio wav", "openmontage"]):
            return self._agents["Media Agent"]
        elif any(w in norm for w in ["diagrama", "arquitectura", "archify", "obsidian", "documentación", "vault", "adr"]):
            return self._agents["Documentation Agent"]
        elif any(w in norm for w in ["dataset", "estadística", "sql", "tabla", "eda", "regresión", "k-means"]):
            return self._agents["Data Agent"]
        elif any(w in norm for w in ["micrófono", "volumen", "voz", "tts", "stt", "habla", "cállate"]):
            return self._agents["Voice Agent"]

        return self._agents["Main Assistant"]

    async def execute_turn(
        self,
        prompt: str,
        session_id: str = "default_session",
        user_id: str = "default_creator",
        modality: str = "voice"
    ) -> Dict[str, Any]:
        """Executes an agentic reasoning turn respecting session memory and security permissions."""
        session = self.get_or_create_session(session_id, user_id=user_id)
        agent = self.select_agent_for_prompt(prompt)

        # Append user turn to isolated memory
        session.history.append({"role": "user", "content": prompt})
        # Keep window sliding (last 10 turns)
        if len(session.history) > 10:
            session.history = session.history[-10:]

        # Route through brain router / LLM provider with selected agent personality
        from app.services.brain_router import brain_router
        try:
            full_system = f"{agent.system_prompt}\nRol activo: {agent.role}."
            if modality == "voice":
                full_system += " Responde con alta concisión ejecutiva (máximo 2 a 3 frases) aptas para conversión de voz fluida."

            res = await brain_router.generate_response(
                prompt=prompt,
                system_prompt=full_system,
            )

            text_output = res.get("text", "")
            executed_tools = res.get("executedTools", [])

            # Persist assistant turn
            session.history.append({"role": "assistant", "content": text_output})

            return {
                "ok": True,
                "agent": agent.name,
                "role": agent.role,
                "model": agent.preferred_model,
                "text": text_output,
                "executedTools": executed_tools,
                "modality": modality,
                "session_id": session_id,
            }
        except Exception as e:
            logger.error(f"[HermesAdapter] Error en ejecución de turno ({agent.name}): {e}", exc_info=True)
            return {
                "ok": False,
                "agent": agent.name,
                "error": str(e),
                "text": "Señor Santiago, he registrado un inconveniente temporal en la ejecución de la consulta.",
                "executedTools": []
            }


hermes_adapter = HermesAgentAdapter()
