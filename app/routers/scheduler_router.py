"""
Scheduler and Cron Tasks API Router for JARVIS / Liseth.
Manages persistent background routines stored in data/scheduled_tasks.json.
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger("jarvis.scheduler_router")

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])

TASKS_FILE = settings.DATA_DIR / "scheduled_tasks.json"

DEFAULT_SCHEDULED_TASKS = [
    {
        "id": "task_daily_morning_summary",
        "title": "Resumen Matutino Diario",
        "type": "daily_summary",
        "schedule": "cron:0 8 * * *",
        "timeOfDay": "08:00",
        "enabled": True,
        "lastRun": None,
        "nextRun": None,
        "params": {"channel": "all"},
    },
    {
        "id": "task_weekly_summary",
        "title": "Resumen Estratégico Semanal",
        "type": "weekly_summary",
        "schedule": "cron:30 8 * * 1",
        "dayOfWeek": 1,
        "timeOfDay": "08:30",
        "enabled": True,
        "lastRun": None,
        "nextRun": None,
        "params": {"channel": "all"},
    },
    {
        "id": "task_calendar_event_check",
        "title": "Verificación Periódica de Calendario y Citas",
        "type": "event_check",
        "schedule": "interval:15m",
        "intervalMinutes": 15,
        "enabled": True,
        "lastRun": None,
        "nextRun": None,
        "params": {"leadTimeMinutes": 30},
    },
    {
        "id": "task_system_process_report",
        "title": "Reporte de Salud del Sistema y Consumo",
        "type": "process_report",
        "schedule": "interval:60m",
        "intervalMinutes": 60,
        "enabled": True,
        "lastRun": None,
        "nextRun": None,
        "params": {"channel": "telegram"},
    },
]


def load_tasks() -> List[Dict[str, Any]]:
    """Loads tasks from data/scheduled_tasks.json or writes default tasks."""
    if not TASKS_FILE.exists():
        save_tasks(DEFAULT_SCHEDULED_TASKS)
        return DEFAULT_SCHEDULED_TASKS

    try:
        content = TASKS_FILE.read_text(encoding="utf-8")
        data = json.loads(content)
        if isinstance(data, list):
            return data
    except Exception as e:
        logger.warning(f"Error leyendo {TASKS_FILE}: {e}")
    return DEFAULT_SCHEDULED_TASKS


def save_tasks(tasks: List[Dict[str, Any]]) -> bool:
    """Persists tasks to data/scheduled_tasks.json."""
    try:
        TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
        TASKS_FILE.write_text(json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except Exception as e:
        logger.error(f"Error guardando {TASKS_FILE}: {e}")
        return False


class TaskTriggerRequest(BaseModel):
    taskId: str


class TaskToggleRequest(BaseModel):
    taskId: str
    enabled: bool


@router.get("/tasks")
async def get_scheduler_tasks():
    """Returns the list of persistent scheduled tasks."""
    tasks = load_tasks()
    return {"ok": True, "tasks": tasks, "count": len(tasks)}


@router.post("/tasks/trigger")
async def trigger_scheduler_task(req: TaskTriggerRequest):
    """
    Manually triggers an immediate execution of a scheduled routine.
    """
    tasks = load_tasks()
    target = next((t for t in tasks if t.get("id") == req.taskId), None)

    if not target:
        raise HTTPException(status_code=404, detail=f"Tarea con ID '{req.taskId}' no encontrada.")

    now_iso = datetime.now(timezone.utc).isoformat()
    target["lastRun"] = now_iso
    save_tasks(tasks)

    # Autonomously dispatch execution through HeartbeatService
    exec_status = "Iniciada"
    try:
        from app.services.heartbeat_service import heartbeat_service
        exec_status = heartbeat_service.execute_scheduled_task(target)
    except Exception as e:
        logger.warning(f"Error despachando tarea programada: {e}")

    return {
        "ok": True,
        "message": f"Tarea '{target.get('title')}' disparada y ejecutada exitosamente. ({exec_status})",
        "task": target,
        "executedAt": now_iso,
    }


@router.post("/tasks/toggle")
async def toggle_scheduler_task(req: TaskToggleRequest):
    """Enables or disables a scheduled routine."""
    tasks = load_tasks()
    target = next((t for t in tasks if t.get("id") == req.taskId), None)

    if not target:
        raise HTTPException(status_code=404, detail=f"Tarea con ID '{req.taskId}' no encontrada.")

    target["enabled"] = req.enabled
    save_tasks(tasks)

    return {"ok": True, "task": target}
