"""
Tests for Scheduler and Tasks API endpoints.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_scheduler_tasks():
    res = client.get("/api/scheduler/tasks")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert "tasks" in data
    assert isinstance(data["tasks"], list)
    assert len(data["tasks"]) >= 1


def test_trigger_scheduler_task():
    res = client.post("/api/scheduler/tasks/trigger", json={"taskId": "task_daily_morning_summary"})
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert data["task"]["id"] == "task_daily_morning_summary"
    assert data["task"]["lastRun"] is not None


def test_trigger_nonexistent_scheduler_task():
    res = client.post("/api/scheduler/tasks/trigger", json={"taskId": "nonexistent_task_999"})
    assert res.status_code == 404
