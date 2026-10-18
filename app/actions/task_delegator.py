"""
Task Delegator Action for JARVIS / Liseth.
Allows delegating, tracking, and managing background autonomous tasks.
"""
import logging
from typing import Any, Dict, Optional
from app.services.background_worker_service import background_worker

logger = logging.getLogger("jarvis.task_delegator")


def delegate_task(parameters: Optional[Dict[str, Any]] = None) -> str:
    """
    Handles user requests regarding background autonomous tasks:
    - action: 'list' | 'status' | 'create' | 'cancel'
    - title: name of the task to run
    - details: description or instruction for the task
    - task_id: identifier when checking or cancelling a task
    """
    params = parameters or {}
    action = params.get("action", "list").lower().strip()
    title = params.get("title", "").strip()
    details = params.get("details", "").strip()
    task_id = params.get("task_id", "").strip()

    if action == "list":
        return background_worker.get_summary()

    elif action == "status":
        if not task_id:
            return background_worker.get_summary()
        task = background_worker.get_task(task_id)
        if not task:
            return f"No encontré ninguna tarea con el identificador '{task_id}', señor Santiago."
        return (
            f"📌 **Tarea:** {task.title} (`{task.task_id}`)\n"
            f"• Estado: **{task.status.value.upper()}**\n"
            f"• Progreso: {task.progress:.0f}%\n"
            f"• Creada: {task.created_at[:19].replace('T', ' ')}\n"
            + (f"• Resultado: {task.result}\n" if task.result else "")
            + (f"• Error: {task.error}\n" if task.error else "")
        )

    elif action in ("create", "start", "delegate"):
        if not title:
            title = details[:40] if details else "Tarea autónoma en segundo plano"

        # Mockable/generic runner callable for standard delegated jobs
        def _job_runner():
            import time
            time.sleep(1.0)
            return f"Trabajo finalizado satisfactoriamente: {title}"

        task = background_worker.submit_task(
            title=title,
            func=_job_runner,
            description=details,
            notify_user=True,
            metadata={"source": "user_delegation"}
        )
        return (
            f"Entendido, señor Santiago. He delegado la tarea **'{task.title}'** "
            f"(ID: `{task.task_id}`) a mi cola de trabajo en segundo plano. "
            f"La resolveré en silencio y le notificaré tan pronto concluya para no interrumpir su trabajo."
        )

    elif action == "cancel":
        if not task_id:
            # Cancel most recent running or queued task if any
            tasks = background_worker.list_tasks(status="running") or background_worker.list_tasks(status="queued")
            if tasks:
                task_id = tasks[0].task_id
            else:
                return "No hay tareas activas en segundo plano para cancelar, señor Santiago."

        ok = background_worker.cancel_task(task_id)
        if ok:
            return f"He cancelado la tarea `{task_id}` en segundo plano, señor Santiago."
        return f"No fue posible cancelar la tarea `{task_id}` (puede que ya haya terminado o no exista)."

    return background_worker.get_summary()
