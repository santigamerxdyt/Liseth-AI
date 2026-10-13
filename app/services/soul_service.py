"""
SOUL & Memory Service for JARVIS / Liseth.
Inspired by the agentic architecture (Hermes Agent / Nino Director 9-step guide):
- Manages SOUL.md (identity, ethics, tone, and strict confirmation rules).
- Manages persistent memories (data/memories/USER.md and MEMORY.md).
- Discovers and loads modular skills (skills/*/SKILL.md).
- Injects full context dynamically into Gemini and Claude system prompts.
"""
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from app.config import settings

logger = logging.getLogger("jarvis.soul")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SOUL_FILE = BASE_DIR / "SOUL.md"
MEMORIES_DIR = BASE_DIR / "data" / "memories"
USER_FILE = MEMORIES_DIR / "USER.md"
MEMORY_FILE = MEMORIES_DIR / "MEMORY.md"
SKILLS_DIR = BASE_DIR / "skills"


class SoulService:
    def __init__(self):
        MEMORIES_DIR.mkdir(parents=True, exist_ok=True)
        SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    def get_soul(self) -> str:
        """Reads SOUL.md or returns the default identity."""
        if SOUL_FILE.exists():
            try:
                return SOUL_FILE.read_text(encoding="utf-8").strip()
            except Exception as e:
                logger.warning(f"Error leyendo SOUL.md: {e}")
        return (
            "Eres Liseth, la asistente personal de IA de Santiago Huerfano Lopez. "
            "Responde de forma concisa, dulce y altamente profesional. "
            "Pide confirmación antes de cualquier acción destructiva o de envío de correos."
        )

    def save_soul(self, content: str) -> bool:
        """Saves updated content to SOUL.md."""
        try:
            SOUL_FILE.write_text(content.strip(), encoding="utf-8")
            return True
        except Exception as e:
            logger.error(f"Error guardando SOUL.md: {e}")
            return False

    def get_user_memory(self) -> str:
        """Reads USER.md memory."""
        if USER_FILE.exists():
            try:
                return USER_FILE.read_text(encoding="utf-8").strip()
            except Exception:
                pass
        return ""

    def get_system_memory(self) -> str:
        """Reads MEMORY.md memory."""
        if MEMORY_FILE.exists():
            try:
                return MEMORY_FILE.read_text(encoding="utf-8").strip()
            except Exception:
                pass
        return ""

    def append_memory(self, note: str, target: str = "memory") -> bool:
        """Appends a new fact or preference to MEMORY.md or USER.md."""
        filepath = USER_FILE if target == "user" else MEMORY_FILE
        try:
            current = filepath.read_text(encoding="utf-8") if filepath.exists() else ""
            if note not in current:
                with open(filepath, "a", encoding="utf-8") as f:
                    f.write(f"\n- {note.strip()}")
            return True
        except Exception as e:
            logger.error(f"Error agregando memoria a {target}: {e}")
            return False

    def list_skills(self) -> List[Dict[str, str]]:
        """Discovers and parses all skills in skills/*/SKILL.md."""
        skills = []
        if not SKILLS_DIR.exists():
            return skills

        for skill_path in SKILLS_DIR.glob("*/SKILL.md"):
            try:
                text = skill_path.read_text(encoding="utf-8")
                # Parse frontmatter
                name = skill_path.parent.name
                desc = "Habilidad de Liseth"
                body = text

                if text.startswith("---"):
                    parts = text.split("---", 2)
                    if len(parts) >= 3:
                        fm = yaml.safe_load(parts[1])
                        if isinstance(fm, dict):
                            name = fm.get("name", name)
                            desc = fm.get("description", desc)
                        body = parts[2].strip()

                skills.append({
                    "id": skill_path.parent.name,
                    "name": name,
                    "description": desc,
                    "procedure": body,
                    "path": str(skill_path.relative_to(BASE_DIR)),
                })
            except Exception as e:
                logger.warning(f"Error leyendo skill {skill_path}: {e}")

        return skills

    def build_system_instruction(self, custom_prompt: Optional[str] = None) -> str:
        """
        Builds the unified, rich system prompt combining:
        1. Core SOUL (identity, tone, rules)
        2. User Profile (USER.md)
        3. Persistent Memory (MEMORY.md)
        4. Available Skills
        5. Any custom or incoming prompt
        """
        sections = []

        # 1. SOUL
        soul = self.get_soul()
        if soul:
            sections.append(f"### IDENTIDAD Y REGLAS DE LISETH (SOUL):\n{soul}")

        # 2. USER.md
        user_mem = self.get_user_memory()
        if user_mem:
            sections.append(f"### INFORMACIÓN SOBRE TU USUARIO (USER):\n{user_mem}")

        # 3. MEMORY.md
        sys_mem = self.get_system_memory()
        if sys_mem:
            sections.append(f"### MEMORIA PERSISTENTE ACUMULADA:\n{sys_mem}")

        # 4. SKILLS
        skills = self.list_skills()
        if skills:
            skills_summary = ["### HABILIDADES (SKILLS) DISPONIBLES:"]
            for s in skills:
                skills_summary.append(f"- **{s['name']}**: {s['description']}")
            sections.append("\n".join(skills_summary))

        # 5. Custom instruction
        if custom_prompt:
            sections.append(f"### INSTRUCCIONES ESPECÍFICAS DE LA CONSULTA:\n{custom_prompt}")

        return "\n\n".join(sections)


soul_service = SoulService()
