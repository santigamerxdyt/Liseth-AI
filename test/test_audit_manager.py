"""
Unit tests for AuditManager, Google Workspace confirmation flow, and /api/audit endpoints.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.audit_manager import audit_manager
from app.connectors.google_workspace import google_connector

client = TestClient(app)


def test_describe_action_gmail_sensitive():
    is_sensitive, service, reason = audit_manager.describe_action(
        connector="google_workspace",
        action_name="google_send_email",
        params={"to": "cliente@ejemplo.com", "subject": "Propuesta Comercial", "body": "Detalle..."},
    )
    assert is_sensitive is True
    assert service == "Gmail"
    assert "cliente@ejemplo.com" in reason
    assert "Propuesta Comercial" in reason
    assert "Estoy a punto de enviar un correo" in reason


def test_describe_action_calendar_sensitive():
    is_sensitive, service, reason = audit_manager.describe_action(
        connector="google_workspace",
        action_name="google_create_event",
        params={"summary": "Reunión de Estrategia", "startDateTime": "2026-10-15T10:00:00", "endDateTime": "2026-10-15T11:00:00"},
    )
    assert is_sensitive is True
    assert service == "Google Calendar"
    assert "Reunión de Estrategia" in reason
    assert "Estoy a punto de agendar el evento" in reason


def test_describe_action_read_safe():
    is_sensitive, service, reason = audit_manager.describe_action(
        connector="google_workspace",
        action_name="google_list_emails",
        params={"maxResults": 5},
    )
    assert is_sensitive is False


@pytest.mark.asyncio
async def test_google_connector_enforces_confirmation():
    # Calling a sensitive action without prior confirmation must be paused and request approval
    res = await google_connector.execute_action(
        action_name="google_send_email",
        params={"to": "socio@negocio.com", "subject": "Contrato Listo"},
    )
    assert res["requiresConfirmation"] is True
    assert "confirmation" in res
    assert res["confirmation"]["action"] == "google_send_email"
    assert "Estoy a punto de enviar un correo" in res["message"]


@pytest.mark.asyncio
async def test_audit_manager_pending_and_resolution():
    # Create pending
    pending = await audit_manager.create_pending_confirmation(
        connector="google_workspace",
        action="google_delete_event",
        params={"eventId": "evt_9988"},
    )
    confirm_id = pending["id"]
    assert pending["status"] == "pending_confirmation"

    # Resolve with rejection
    res_reject = await audit_manager.resolve_confirmation(confirm_id, approved=False)
    assert res_reject["approved"] is False
    assert res_reject["status"] == "rejected"

    # Create another and approve
    pending2 = await audit_manager.create_pending_confirmation(
        connector="google_workspace",
        action="google_create_task",
        params={"title": "Comprar insumos"},
    )
    confirm_id2 = pending2["id"]
    res_approve = await audit_manager.resolve_confirmation(confirm_id2, approved=True)
    assert res_approve["approved"] is True
    assert res_approve["status"] in ["approved", "executed"]


def test_audit_api_endpoints():
    # 1. Request confirmation via API
    req_res = client.post(
        "/api/audit/request",
        json={
            "connector": "google_workspace",
            "action": "google_send_email",
            "params": {"to": "test@api.com", "subject": "Test API"},
        },
    )
    assert req_res.status_code == 200
    conf_data = req_res.json()["confirmation"]
    confirm_id = conf_data["id"]

    # 2. Check pending
    pending_res = client.get("/api/audit/pending")
    assert pending_res.status_code == 200

    # 3. Confirm decision
    decision_res = client.post(
        "/api/audit/confirm",
        json={"confirmId": confirm_id, "approved": True},
    )
    assert decision_res.status_code == 200
    assert decision_res.json()["ok"] is True
    assert decision_res.json()["decision"] == "approved"

    # 4. Check logs
    logs_res = client.get("/api/audit/logs")
    assert logs_res.status_code == 200
    assert logs_res.json()["ok"] is True
    assert len(logs_res.json()["logs"]) > 0
