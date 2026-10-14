"""
Unit tests for SystemConnector and system execution endpoints in JARVIS / Liseth.
Verifies hardware telemetry, process query, and mandatory confirmation interception
for modifying/executing actions (commands, apps, files).
"""
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.connectors.system_connector import system_connector
from app.services.audit_manager import audit_manager

from app.config import settings

client = TestClient(app)
client.post("/api/auth/login", json={"pin": settings.JARVIS_ACCESS_PIN})


@pytest.mark.asyncio
async def test_system_info_telemetry():
    info = await system_connector.get_system_info()
    assert "os" in info
    assert "hostname" in info
    assert "user" in info
    assert "python_version" in info


@pytest.mark.asyncio
async def test_system_read_file_and_list_dir(tmp_path):
    test_file = tmp_path / "test_note.txt"
    test_file.write_text("Hola Santiago desde test", encoding="utf-8")

    read_res = await system_connector.read_file(str(test_file))
    assert read_res["content"] == "Hola Santiago desde test"
    assert read_res["size_bytes"] > 0

    dir_res = await system_connector.list_directory(str(tmp_path))
    assert dir_res["count"] >= 1
    assert any(item["name"] == "test_note.txt" for item in dir_res["items"])


@pytest.mark.asyncio
async def test_sensitive_command_intercepted_by_audit():
    # Calling system_run_command must generate a pending confirmation, not execute immediately
    res = await system_connector.execute_action(
        "system_run_command",
        {"command": "echo 'Prueba de seguridad'", "shell": "powershell"},
    )
    assert res.get("pendingConfirmation") is True
    assert "confirmId" in res
    assert "reason" in res
    assert "Prueba de seguridad" in res["reason"]

    # Verify that it is in pending list
    pending = audit_manager.get_pending()
    assert any(p["id"] == res["confirmId"] for p in pending)

    # Approve and execute via audit manager
    resolve_res = await audit_manager.resolve_confirmation(res["confirmId"], approved=True)
    assert resolve_res["approved"] is True
    assert resolve_res["status"] == "executed"
    assert resolve_res["result"] is not None
    assert "Prueba de seguridad" in resolve_res["result"]["stdout"]


@pytest.mark.asyncio
async def test_sensitive_write_file_intercepted_and_executed(tmp_path):
    target_file = tmp_path / "audit_created.txt"
    res = await system_connector.execute_action(
        "system_write_file",
        {"path": str(target_file), "content": "Contenido protegido"},
    )
    assert res.get("pendingConfirmation") is True
    confirm_id = res["confirmId"]

    # Resolve approval
    resolve_res = await audit_manager.resolve_confirmation(confirm_id, approved=True)
    assert resolve_res["approved"] is True
    assert resolve_res["status"] == "executed"

    # Verify file actually created on disk
    assert target_file.exists()
    assert target_file.read_text(encoding="utf-8") == "Contenido protegido"


def test_api_system_info_endpoint():
    res = client.get("/api/system/info")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert "data" in data
    assert "os" in data["data"]


def test_api_system_processes_endpoint():
    res = client.get("/api/system/processes?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert "processes" in data
    assert len(data["processes"]) <= 10


def test_api_system_execute_endpoint():
    # Execute non-sensitive get_info
    res = client.post("/api/system/execute", json={"action": "system_get_info", "params": {}})
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True

    # Execute sensitive run_command
    res2 = client.post(
        "/api/system/execute",
        json={"action": "system_run_command", "params": {"command": "dir", "shell": "cmd"}},
    )
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["pendingConfirmation"] is True
    assert "confirmId" in data2


def test_personalization_config_save_and_retrieve():
    # Save custom personalization
    update_data = {
        "userTitle": "Señor Santiago Stark",
        "userName": "Santiago",
        "userTone": "formal",
        "customGreeting": "Sistemas de combate y análisis listos, Señor Santiago.",
        "theme": "stark_gold",
        "sphereStyle": "quantum_rings",
    }
    post_res = client.post("/api/config", json=update_data)
    assert post_res.status_code == 200
    assert post_res.json()["ok"] is True

    # Retrieve and verify
    get_res = client.get("/api/config")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["ok"] is True
    assert "personalization" in data
    assert data["personalization"]["userTitle"] == "Señor Santiago Stark"
    assert data["personalization"]["theme"] == "stark_gold"
    assert data["personalization"]["sphereStyle"] == "quantum_rings"


@pytest.mark.asyncio
async def test_system_search_files():
    search_res = await system_connector.search_files(query="config", root_path="app", max_results=5)
    assert search_res["count"] >= 1
    assert any("config.py" in r["name"] for r in search_res["results"])


def test_api_system_search_and_read():
    search_res = client.get("/api/system/search?q=config&path=app")
    assert search_res.status_code == 200
    data = search_res.json()
    assert data["ok"] is True
    assert data["data"]["count"] >= 1

    read_res = client.get("/api/system/read?path=app/config.py")
    assert read_res.status_code == 200
    read_data = read_res.json()
    assert read_data["ok"] is True
    assert "content" in read_data["data"]
    assert "Settings" in read_data["data"]["content"]


def test_api_files_catalog():
    res = client.get("/api/files/catalog")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert "files" in data
    assert isinstance(data["files"], list)

