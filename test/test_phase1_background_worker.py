"""
Tests for Phase 1: BackgroundWorkerService and Task Delegator.
"""
import time
import pytest
from app.services.background_worker_service import BackgroundWorkerService, TaskStatus
from app.actions.task_delegator import delegate_task


def test_background_worker_lifecycle():
    worker = BackgroundWorkerService(max_workers=2)

    def simple_job(x, y):
        return x + y

    task = worker.submit_task("Suma de prueba", simple_job, 10, 25)
    assert task.task_id.startswith("task_")
    assert task.title == "Suma de prueba"

    # Wait briefly for completion
    for _ in range(50):
        if task.status == TaskStatus.COMPLETED:
            break
        time.sleep(0.05)

    assert task.status == TaskStatus.COMPLETED
    assert task.result == 35
    assert task.progress == 100.0
    assert task.completed_at is not None


def test_background_worker_error_handling():
    worker = BackgroundWorkerService(max_workers=2)

    def failing_job():
        raise ValueError("Error de prueba forzado")

    task = worker.submit_task("Tarea fallida", failing_job)
    for _ in range(50):
        if task.status == TaskStatus.FAILED:
            break
        time.sleep(0.05)

    assert task.status == TaskStatus.FAILED
    assert "Error de prueba forzado" in (task.error or "")


def test_background_worker_cancellation():
    worker = BackgroundWorkerService(max_workers=2)

    def long_job():
        time.sleep(10.0)
        return "done"

    task = worker.submit_task("Tarea larga", long_job)
    ok = worker.cancel_task(task.task_id)
    assert ok is True
    assert task.status == TaskStatus.CANCELLED


def test_task_delegator_action():
    # 1. List
    res_list = delegate_task({"action": "list"})
    assert isinstance(res_list, str)
    assert "segundo plano" in res_list.lower()

    # 2. Create
    res_create = delegate_task({"action": "create", "title": "Compilar reporte de ventas"})
    assert "delegado" in res_create.lower()
    assert "Compilar reporte de ventas" in res_create

    # 3. Status
    res_status = delegate_task({"action": "status"})
    assert "segundo plano" in res_status.lower()


def test_background_task_direct_intents():
    from app.services.brain_router import detect_direct_intent

    cases = [
        ("tareas en segundo plano", "background_task", "action", "list"),
        ("que tareas estan en segundo plano", "background_task", "action", "list"),
        ("cuales son las tareas en segundo plano", "background_task", "action", "list"),
        ("cancela la tarea en segundo plano", "background_task", "action", "cancel"),
        ("ejecuta en segundo plano analizar informe", "background_task", "action", "create"),
        ("haz en segundo plano una revision de codigo", "background_task", "action", "create"),
    ]

    for phrase, expected_tool, expected_key, expected_val in cases:
        intent = detect_direct_intent(phrase)
        assert intent is not None, f"Failed for '{phrase}'"
        tool_name, tool_args, _ = intent
        assert tool_name == expected_tool, f"Expected {expected_tool} for '{phrase}', got {tool_name}"
        assert tool_args.get(expected_key) == expected_val

