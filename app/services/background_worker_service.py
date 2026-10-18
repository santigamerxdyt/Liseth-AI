"""
BackgroundWorkerService for JARVIS / Liseth.
Provides persistent background job queue, worker thread pool, progress tracking,
and autonomous completion notifications for Señor Santiago.
"""
import concurrent.futures
import datetime
import enum
import logging
import threading
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("jarvis.background_worker")


class TaskStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AutonomousTask:
    task_id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.QUEUED
    progress: float = 0.0
    result: Any = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    notify_user: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "progress": round(self.progress, 1),
            "result": str(self.result) if self.result is not None else None,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "notify_user": self.notify_user,
            "metadata": self.metadata,
        }


class BackgroundWorkerService:
    """
    Manages autonomous tasks executing in the background without blocking
    the user's computer or main conversation flow.
    """

    def __init__(self, max_workers: int = 3):
        self._max_workers = max_workers
        self._tasks: Dict[str, AutonomousTask] = {}
        self._futures: Dict[str, concurrent.futures.Future] = {}
        self._lock = threading.Lock()
        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self._max_workers,
            thread_name_prefix="LisethWorker"
        )
        self._completion_callbacks: List[Callable[[AutonomousTask], None]] = []

    def register_completion_hook(self, callback: Callable[[AutonomousTask], None]) -> None:
        """Adds a callback to be triggered when any background task finishes."""
        with self._lock:
            self._completion_callbacks.append(callback)

    def submit_task(
        self,
        title: str,
        func: Callable,
        *args,
        description: str = "",
        notify_user: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AutonomousTask:
        """
        Enqueues and immediately starts execution of a background task.
        Returns the created AutonomousTask instance.
        """
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task = AutonomousTask(
            task_id=task_id,
            title=title,
            description=description,
            status=TaskStatus.QUEUED,
            notify_user=notify_user,
            metadata=metadata or {},
        )

        with self._lock:
            self._tasks[task_id] = task

        def _runner():
            with self._lock:
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.datetime.now().isoformat()
                task.progress = 10.0

            try:
                logger.info(f"[BACKGROUND_WORKER] Iniciando tarea '{title}' ({task_id})")
                res = func(*args, **kwargs)
                with self._lock:
                    task.status = TaskStatus.COMPLETED
                    task.progress = 100.0
                    task.result = res
                    task.completed_at = datetime.datetime.now().isoformat()
                logger.info(f"[BACKGROUND_WORKER] Tarea '{title}' completada con éxito.")
            except Exception as e:
                logger.error(f"[BACKGROUND_WORKER] Error en tarea '{title}': {e}", exc_info=True)
                with self._lock:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    task.completed_at = datetime.datetime.now().isoformat()

            # Trigger registered completion callbacks
            for cb in list(self._completion_callbacks):
                try:
                    cb(task)
                except Exception as cb_err:
                    logger.warning(f"[BACKGROUND_WORKER] Error en hook de finalización: {cb_err}")

        future = self._executor.submit(_runner)
        with self._lock:
            self._futures[task_id] = future

        return task

    def get_task(self, task_id: str) -> Optional[AutonomousTask]:
        """Returns the task with the given ID if found."""
        with self._lock:
            return self._tasks.get(task_id)

    def list_tasks(self, status: Optional[str] = None, limit: int = 50) -> List[AutonomousTask]:
        """Lists tracked tasks, optionally filtered by status."""
        with self._lock:
            all_tasks = list(self._tasks.values())

        if status:
            status_lower = status.lower()
            all_tasks = [t for t in all_tasks if t.status.value == status_lower]

        # Sort newest first
        all_tasks.sort(key=lambda t: t.created_at, reverse=True)
        return all_tasks[:limit]

    def cancel_task(self, task_id: str) -> bool:
        """Cancels a queued or running task if possible."""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            future = self._futures.get(task_id)
            if future and not future.done():
                cancelled = future.cancel()
                if cancelled or task.status == TaskStatus.QUEUED:
                    task.status = TaskStatus.CANCELLED
                    task.completed_at = datetime.datetime.now().isoformat()
                    return True
            if task.status in (TaskStatus.QUEUED, TaskStatus.RUNNING):
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.datetime.now().isoformat()
                return True
            return False

    def get_summary(self) -> str:
        """Returns a concise executive natural language summary of background jobs."""
        tasks = self.list_tasks(limit=10)
        if not tasks:
            return "No hay tareas en segundo plano registradas en este momento, señor Santiago."

        running = [t for t in tasks if t.status == TaskStatus.RUNNING]
        queued = [t for t in tasks if t.status == TaskStatus.QUEUED]
        completed = [t for t in tasks if t.status == TaskStatus.COMPLETED]
        failed = [t for t in tasks if t.status == TaskStatus.FAILED]

        lines = [f"📋 **Estado de Tareas en Segundo Plano** ({len(tasks)} recientes):"]
        if running:
            lines.append(f"• **En Ejecución ({len(running)}):**")
            for t in running:
                lines.append(f"  - {t.title} [{t.task_id}] ({t.progress:.0f}%)")
        if queued:
            lines.append(f"• **En Cola ({len(queued)}):**")
            for t in queued:
                lines.append(f"  - {t.title} [{t.task_id}]")
        if completed:
            lines.append(f"• **Completadas ({len(completed)}):**")
            for t in completed[:3]:
                lines.append(f"  - {t.title} [{t.task_id}] ✅")
        if failed:
            lines.append(f"• **Con Fallo ({len(failed)}):**")
            for t in failed[:2]:
                lines.append(f"  - {t.title} [{t.task_id}] ⚠️ ({t.error})")

        return "\n".join(lines)


# Singleton instance
background_worker = BackgroundWorkerService()
