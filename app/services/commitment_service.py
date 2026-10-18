"""
CommitmentService — Santiago's Autonomous Task & Follow-up Tracker.
Stores commitments, promises, and scheduled follow-ups in data/commitments.json.
Enables Liseth to autonomously keep track of what Santiago needs to do,
remind him proactivally when due, and review pending priorities during the morning briefing.
"""
import json
import logging
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import settings

logger = logging.getLogger("jarvis.commitments")

COMMITMENTS_FILE = settings.DATA_DIR / "commitments.json"


class CommitmentService:
    def __init__(self):
        self._lock = threading.Lock()
        COMMITMENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not COMMITMENTS_FILE.exists():
            self._save_raw([])

    def _load_raw(self) -> List[Dict[str, Any]]:
        with self._lock:
            if not COMMITMENTS_FILE.exists():
                return []
            try:
                data = json.loads(COMMITMENTS_FILE.read_text(encoding="utf-8"))
                return data if isinstance(data, list) else []
            except Exception as e:
                logger.error(f"[Commitments] Error leyendo {COMMITMENTS_FILE}: {e}")
                return []

    def _save_raw(self, items: List[Dict[str, Any]]) -> bool:
        with self._lock:
            try:
                temp_file = COMMITMENTS_FILE.with_suffix(".tmp")
                temp_file.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
                temp_file.replace(COMMITMENTS_FILE)
                return True
            except Exception as e:
                logger.error(f"[Commitments] Error guardando {COMMITMENTS_FILE}: {e}")
                return False

    def add_commitment(
        self,
        text: str,
        due_date: Optional[str] = None,
        due_time: Optional[str] = None,
        priority: str = "normal",
    ) -> Dict[str, Any]:
        """Adds a new commitment or promise to track."""
        now = datetime.now()
        if not due_date:
            due_date = now.strftime("%Y-%m-%d")
        if not due_time:
            due_time = "18:00"  # Default end of business day

        comm_id = f"comm_{int(time.time() * 1000)}"
        new_item = {
            "id": comm_id,
            "text": text.strip(),
            "due_date": due_date.strip(),
            "due_time": due_time.strip(),
            "priority": priority,
            "status": "pending",
            "reminded": False,
            "created_at": now.isoformat(),
        }

        items = self._load_raw()
        items.append(new_item)
        self._save_raw(items)
        logger.info(f"[Commitments] Compromiso añadido: {new_item['text']} (para {due_date} {due_time})")
        return new_item

    def list_commitments(self, status: Optional[str] = "pending") -> List[Dict[str, Any]]:
        """Lists commitments filtered by status ('pending', 'completed', or None for all)."""
        items = self._load_raw()
        if status:
            return [it for it in items if it.get("status") == status]
        return items

    def complete_commitment(self, id_or_text: str) -> bool:
        """Marks a commitment as completed by ID or substring match."""
        items = self._load_raw()
        target = None
        for it in items:
            if it.get("id") == id_or_text or id_or_text.lower() in it.get("text", "").lower():
                target = it
                break

        if target:
            target["status"] = "completed"
            target["completed_at"] = datetime.now().isoformat()
            self._save_raw(items)
            logger.info(f"[Commitments] Compromiso completado: {target['text']}")
            return True
        return False

    def delete_commitment(self, id_or_text: str) -> bool:
        """Deletes a commitment from tracking."""
        items = self._load_raw()
        initial_len = len(items)
        items = [it for it in items if it.get("id") != id_or_text and id_or_text.lower() not in it.get("text", "").lower()]
        if len(items) < initial_len:
            self._save_raw(items)
            return True
        return False

    def check_due_commitments(self, lead_minutes: int = 30) -> List[Dict[str, Any]]:
        """
        Returns pending commitments due within lead_minutes or overdue that haven't been reminded yet.
        """
        now = datetime.now()
        items = self._load_raw()
        due_items = []

        for it in items:
            if it.get("status") != "pending" or it.get("reminded", False):
                continue

            d_str = it.get("due_date", "")
            t_str = it.get("due_time", "")
            if not d_str or not t_str:
                continue

            try:
                # Handle HH:MM or HH:MM:SS
                if len(t_str) == 5:
                    target_dt = datetime.strptime(f"{d_str} {t_str}", "%Y-%m-%d %H:%M")
                else:
                    target_dt = datetime.strptime(f"{d_str} {t_str[:5]}", "%Y-%m-%d %H:%M")

                delta_seconds = (target_dt - now).total_seconds()
                # If overdue (up to 4 hours) or due within lead_minutes
                if -14400 <= delta_seconds <= (lead_minutes * 60):
                    due_items.append(it)
            except Exception as e:
                logger.debug(f"[Commitments] Error parseando fecha {d_str} {t_str}: {e}")

        return due_items

    def mark_reminded(self, commitment_id: str) -> None:
        """Marks a commitment as reminded so it doesn't alert repeatedly."""
        items = self._load_raw()
        for it in items:
            if it.get("id") == commitment_id:
                it["reminded"] = True
                it["last_reminded_at"] = datetime.now().isoformat()
                break
        self._save_raw(items)

    def format_commitments_summary(self) -> str:
        """Returns a natural Spanish summary of pending tasks for morning briefing."""
        pending = self.list_commitments(status="pending")
        if not pending:
            return "No tiene compromisos pendientes programados para hoy."

        today_str = datetime.now().strftime("%Y-%m-%d")
        today_tasks = [t for t in pending if t.get("due_date") == today_str]
        other_tasks = [t for t in pending if t.get("due_date") != today_str]

        lines = []
        if today_tasks:
            lines.append(f"Tiene {len(today_tasks)} compromiso(s) para hoy:")
            for t in today_tasks[:4]:
                lines.append(f"- {t['text']} (a las {t.get('due_time', '18:00')})")
        if other_tasks and not today_tasks:
            lines.append(f"Tiene {len(other_tasks)} tarea(s) pendiente(s) en su lista general.")

        return "\n".join(lines)


# Global singleton
commitment_service = CommitmentService()
