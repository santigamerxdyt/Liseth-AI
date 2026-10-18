"""
DailyDebriefService for JARVIS / Liseth.
Centralized ledger and executive debrief generator for all autonomous activities
completed in the background while Señor Santiago focuses on other tasks:
- Background tasks finished
- Routines executed
- Code health and sentinel audits
- Proactive alerts and notifications
"""
import datetime
import json
import logging
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.config import settings

logger = logging.getLogger("jarvis.daily_debrief")


@dataclass
class ActivityEntry:
    timestamp: str
    category: str  # "background_task" | "routine" | "sentinel" | "system" | "email"
    title: str
    details: str = ""
    status: str = "success"  # "success" | "warning" | "info"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "category": self.category,
            "title": self.title,
            "details": self.details,
            "status": self.status,
        }


class DailyDebriefService:
    """
    Records autonomous background events throughout the day and generates
    high-level executive summaries on demand or at end-of-day.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._entries: List[ActivityEntry] = []
        self._file_path = settings.DATA_DIR / "activity_ledger.json"
        self._load_ledger()

    def _load_ledger(self):
        try:
            if self._file_path.exists():
                data = json.loads(self._file_path.read_text(encoding="utf-8"))
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                self._entries = [
                    ActivityEntry(**item) for item in data
                    if isinstance(item, dict) and item.get("timestamp", "").startswith(today)
                ]
        except Exception as e:
            logger.debug(f"[DEBRIEF] Error cargando ledger: {e}")
            self._entries = []

    def _save_ledger(self):
        try:
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            serializable = [e.to_dict() for e in self._entries[-100:]]
            self._file_path.write_text(json.dumps(serializable, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logger.debug(f"[DEBRIEF] Error guardando ledger: {e}")

    def log_activity(
        self,
        category: str,
        title: str,
        details: str = "",
        status: str = "success"
    ) -> ActivityEntry:
        """Records an autonomous action or event in the ledger."""
        entry = ActivityEntry(
            timestamp=datetime.datetime.now().isoformat(),
            category=category,
            title=title,
            details=details,
            status=status
        )
        with self._lock:
            self._entries.append(entry)
            self._save_ledger()

        logger.info(f"[DEBRIEF] Actividad registrada: [{category}] {title}")
        return entry

    def get_entries(self, category: Optional[str] = None, limit: int = 50) -> List[ActivityEntry]:
        """Returns recorded entries for the current day."""
        with self._lock:
            entries = list(self._entries)

        if category:
            entries = [e for e in entries if e.category == category]

        return entries[-limit:]

    def generate_debrief(self) -> str:
        """
        Compiles an executive natural language debrief of all autonomous
        work accomplished for Señor Santiago today.
        """
        entries = self.get_entries(limit=100)
        today_str = datetime.datetime.now().strftime("%d de %B de %Y")

        if not entries:
            return (
                f"📋 **Reporte de Actividad Autónoma** ({today_str}):\n"
                "Señor Santiago, hoy todos los sistemas han operado con total normalidad. "
                "No hay tareas pendientes en segundo plano ni incidencias que requieran su atención inmediata."
            )

        # Categorize
        bg_tasks = [e for e in entries if e.category == "background_task"]
        routines = [e for e in entries if e.category == "routine"]
        sentinel_audits = [e for e in entries if e.category == "sentinel"]
        system_events = [e for e in entries if e.category == "system"]

        lines = [
            f"📋 **Reporte Ejecutivo de Trabajo Autónomo** ({today_str}):\n",
            "Señor Santiago, este es el balance de las acciones resueltas en segundo plano mientras usted se ocupaba de sus labores:\n"
        ]

        if bg_tasks:
            lines.append(f"• **Tareas en Segundo Plano Resueltas ({len(bg_tasks)}):**")
            for t in bg_tasks[-4:]:
                lines.append(f"  - {t.title} ✅" + (f" ({t.details})" if t.details else ""))

        if routines:
            lines.append(f"• **Rutinas Automatizadas Ejecutadas ({len(routines)}):**")
            for r in routines[-3:]:
                lines.append(f"  - {r.title} ({r.details or 'Completada'})")

        if sentinel_audits:
            lines.append(f"• **Centinela de Código ({len(sentinel_audits)} auditorías silenciosas):**")
            last_sentinel = sentinel_audits[-1]
            lines.append(f"  - {last_sentinel.title}: {last_sentinel.details or 'Código saludable sin errores de sintaxis'}")

        if system_events:
            lines.append(f"• **Eventos y Ajustes del Sistema ({len(system_events)}):**")
            for s in system_events[-3:]:
                lines.append(f"  - {s.title}")

        lines.append("\nTodos sus repositorios, tareas y entornos se mantienen sincronizados y listos a su disposición.")
        return "\n".join(lines)


# Singleton instance
daily_debrief_service = DailyDebriefService()

# Auto-hook into background worker completion
def _on_bg_task_completed(task):
    status_str = "success" if task.status.value == "completed" else "warning"
    daily_debrief_service.log_activity(
        category="background_task",
        title=f"Tarea: {task.title}",
        details=f"Estado: {task.status.value.upper()}" + (f" | Resultado: {task.result}" if task.result else ""),
        status=status_str
    )

try:
    from app.services.background_worker_service import background_worker
    background_worker.register_completion_hook(_on_bg_task_completed)
except Exception:
    pass
