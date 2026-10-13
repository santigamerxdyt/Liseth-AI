"""
Audit Manager and Sensitive Action Confirmation System for JARVIS / Liseth.
Intercepts all sensitive external service operations (especially Google Workspace:
Gmail, Calendar, Tasks, Drive, Docs, Sheets), logs actions in SQLite WAL,
and enforces explicit user confirmation before executing any modification or send action.
"""
import logging
import secrets
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.core.models import AuditEntry

logger = logging.getLogger("jarvis.audit")

# Map of sensitive Google actions and human descriptions
GOOGLE_ACTION_DESCRIPTIONS = {
    # Gmail
    "google_send_email": {
        "service": "Gmail",
        "action_title": "Enviar correo electrónico",
        "template": "Estoy a punto de enviar un correo a '{to}' con el asunto '{subject}'. ¿Desea que proceda con el envío?",
    },
    "google_reply_email": {
        "service": "Gmail",
        "action_title": "Responder correo",
        "template": "Estoy a punto de responder al correo con ID '{messageId}'. ¿Desea que envíe esta respuesta?",
    },
    "google_delete_email": {
        "service": "Gmail",
        "action_title": "Eliminar correo",
        "template": "Estoy a punto de mover a la papelera el correo con ID '{messageId}'. Esta acción eliminará el mensaje. ¿Desea continuar?",
    },
    "google_archive_email": {
        "service": "Gmail",
        "action_title": "Archivar correo",
        "template": "Estoy a punto de archivar el correo con ID '{messageId}'. ¿Desea que proceda?",
    },
    # Calendar
    "google_create_event": {
        "service": "Google Calendar",
        "action_title": "Crear evento en calendario",
        "template": "Estoy a punto de agendar el evento '{summary}' desde {startDateTime} hasta {endDateTime}. ¿Desea que lo registre en su calendario?",
    },
    "google_update_event": {
        "service": "Google Calendar",
        "action_title": "Modificar evento",
        "template": "Estoy a punto de modificar el evento de calendario con ID '{eventId}'. ¿Desea que guarde estos cambios?",
    },
    "google_delete_event": {
        "service": "Google Calendar",
        "action_title": "Eliminar evento",
        "template": "Estoy a punto de eliminar permanentemente el evento '{eventId}' de Google Calendar. ¿Desea que proceda?",
    },
    # Tasks
    "google_create_task": {
        "service": "Google Tasks",
        "action_title": "Crear tarea",
        "template": "Estoy a punto de registrar la tarea '{title}' en Google Tasks. ¿Desea que proceda?",
    },
    "google_complete_task": {
        "service": "Google Tasks",
        "action_title": "Completar tarea",
        "template": "Estoy a punto de marcar como completada la tarea con ID '{taskId}'. ¿Desea que la cierre?",
    },
    "google_delete_task": {
        "service": "Google Tasks",
        "action_title": "Eliminar tarea",
        "template": "Estoy a punto de eliminar la tarea '{taskId}' de Google Tasks. ¿Desea que proceda?",
    },
    # Drive & Docs
    "google_upload_file": {
        "service": "Google Drive",
        "action_title": "Subir archivo a Drive",
        "template": "Estoy a punto de subir el archivo '{name}' a su Google Drive. ¿Desea que proceda?",
    },
    "google_delete_file": {
        "service": "Google Drive",
        "action_title": "Eliminar archivo de Drive",
        "template": "Estoy a punto de eliminar el archivo con ID '{fileId}' de su Google Drive. ¿Desea continuar?",
    },
    "google_write_doc": {
        "service": "Google Docs",
        "action_title": "Modificar documento",
        "template": "Estoy a punto de escribir o modificar texto en el documento '{documentId}'. ¿Desea que guarde los cambios?",
    },
}


class AuditManager:
    def __init__(self):
        # Pending confirmations in memory: confirm_id -> dict
        self._pending_confirmations: Dict[str, Dict[str, Any]] = {}
        # Registered execution handlers: action_name -> async callable
        self._action_handlers: Dict[str, Callable] = {}

    def register_handler(self, action_name: str, handler: Callable):
        """Registers an asynchronous executor for a confirmed action."""
        self._action_handlers[action_name] = handler

    def describe_action(self, connector: str, action_name: str, params: Dict[str, Any]) -> Tuple[bool, str, str]:
        """
        Determines if an action is sensitive and builds an explicit description of what it is about to do.
        Returns: (is_sensitive, service_name, descriptive_reason)
        """
        # Check predefined Google actions
        if action_name in GOOGLE_ACTION_DESCRIPTIONS:
            meta = GOOGLE_ACTION_DESCRIPTIONS[action_name]
            service = meta["service"]
            template = meta["template"]
            try:
                # Format parameters safely
                safe_params = {k: str(v) for k, v in params.items()}
                # Fill missing keys with empty or placeholder
                for key in ["to", "subject", "summary", "startDateTime", "endDateTime", "messageId", "title", "taskId", "name", "fileId", "documentId"]:
                    safe_params.setdefault(key, params.get(key, "(sin especificar)"))
                reason = template.format(**safe_params)
            except Exception:
                reason = f"Estoy a punto de ejecutar '{meta['action_title']}' en {service} con los parámetros: {params}. ¿Desea que proceda?"
            return True, service, reason

        # General sensitive actions heuristics (create, send, delete, update, modify)
        sensitive_keywords = ["send", "create", "delete", "remove", "update", "write", "post", "publish", "drop"]
        action_lower = action_name.lower()
        is_sensitive = any(w in action_lower for w in sensitive_keywords)

        service_name = connector.replace("_", " ").title()
        if is_sensitive:
            reason = (
                f"Estoy a punto de realizar la acción '{action_name}' en su servicio {service_name} "
                f"con los siguientes parámetros: {params}. ¿Desea autorizar esta operación?"
            )
        else:
            reason = f"Acción '{action_name}' en {service_name}."

        return is_sensitive, service_name, reason

    async def create_pending_confirmation(
        self,
        connector: str,
        action: str,
        params: Dict[str, Any],
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates a pending confirmation request, logs it in SQLite, and returns confirmation metadata.
        """
        is_sensitive, service_name, default_reason = self.describe_action(connector, action, params)
        final_reason = reason or default_reason

        confirm_id = f"req_{int(time.time() * 1000)}_{secrets.token_hex(3)}"
        now_str = datetime.now(timezone.utc).isoformat()

        item = {
            "id": confirm_id,
            "connector": connector,
            "service": service_name,
            "action": action,
            "params": params,
            "reason": final_reason,
            "status": "pending_confirmation",
            "createdAt": now_str,
        }

        self._pending_confirmations[confirm_id] = item

        # Persist in SQLite
        async with AsyncSessionLocal() as session:
            try:
                entry = AuditEntry(
                    id=confirm_id,
                    timestamp=now_str,
                    action=action,
                    category=connector,
                    status="pending_confirmation",
                    sensitive=True,
                    details={
                        "params": params,
                        "service": service_name,
                        "reason": final_reason,
                    },
                )
                session.add(entry)
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.warning(f"Error registrando auditoría en base de datos: {e}")

        logger.info(f"[AUDIT] Confirmación requerida para {action} ({confirm_id}): {final_reason}")
        return item

    async def resolve_confirmation(self, confirm_id: str, approved: bool) -> Dict[str, Any]:
        """
        Resolves a pending confirmation.
        If approved: executes the registered handler and logs execution.
        If rejected: marks as rejected.
        """
        pending = self._pending_confirmations.get(confirm_id)
        if not pending:
            # Check SQLite if not in memory
            async with AsyncSessionLocal() as session:
                res = await session.execute(select(AuditEntry).where(AuditEntry.id == confirm_id))
                db_entry = res.scalar_one_or_none()
                if not db_entry:
                    raise ValueError(f"No se encontró la solicitud de confirmación '{confirm_id}'.")
                details = db_entry.details or {}
                pending = {
                    "id": confirm_id,
                    "connector": db_entry.category,
                    "action": db_entry.action,
                    "params": details.get("params", {}),
                    "reason": details.get("reason", ""),
                    "createdAt": db_entry.timestamp,
                }

        # Remove from active pending
        self._pending_confirmations.pop(confirm_id, None)

        now_str = datetime.now(timezone.utc).isoformat()
        execution_result = None
        error_message = None

        if approved:
            status_str = "approved"
            # Execute registered handler if available
            action = pending["action"]
            handler = self._action_handlers.get(action)
            if handler:
                try:
                    logger.info(f"[AUDIT] Ejecutando acción aprobada: {action}...")
                    execution_result = await handler(pending["params"])
                    status_str = "executed"
                except Exception as ex:
                    logger.error(f"[AUDIT] Error ejecutando acción aprobada {action}: {ex}")
                    error_message = str(ex)
                    status_str = "failed"
            else:
                execution_result = {"simulated": True, "notice": "Acción aprobada por el usuario."}
                status_str = "approved"
        else:
            status_str = "rejected"
            logger.info(f"[AUDIT] Acción rechazada por el usuario: {pending['action']} ({confirm_id})")

        # Update SQLite record
        async with AsyncSessionLocal() as session:
            try:
                await session.execute(
                    update(AuditEntry)
                    .where(AuditEntry.id == confirm_id)
                    .values(
                        status=status_str,
                        details={
                            **pending.get("params", {}),
                            "resolvedAt": now_str,
                            "approved": approved,
                            "result": execution_result,
                            "error": error_message,
                        },
                    )
                )
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Error actualizando registro de auditoría {confirm_id}: {e}")

        return {
            "confirmId": confirm_id,
            "approved": approved,
            "status": status_str,
            "action": pending["action"],
            "result": execution_result,
            "error": error_message,
        }

    async def log_action(
        self,
        connector: str,
        action: str,
        params: Dict[str, Any],
        status: str = "executed",
        result: Optional[Any] = None,
        sensitive: bool = False,
    ) -> str:
        """Records an action directly in the audit log."""
        log_id = f"audit_{int(time.time() * 1000)}_{secrets.token_hex(2)}"
        now_str = datetime.now(timezone.utc).isoformat()

        async with AsyncSessionLocal() as session:
            try:
                entry = AuditEntry(
                    id=log_id,
                    timestamp=now_str,
                    action=action,
                    category=connector,
                    status=status,
                    sensitive=sensitive,
                    details={"params": params, "result": result},
                )
                session.add(entry)
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.warning(f"Error registrando log de auditoría: {e}")

        return log_id

    async def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Returns the most recent audit log entries."""
        async with AsyncSessionLocal() as session:
            res = await session.execute(
                select(AuditEntry).order_by(AuditEntry.timestamp.desc()).limit(limit)
            )
            entries = res.scalars().all()
            return [
                {
                    "id": e.id,
                    "timestamp": e.timestamp,
                    "action": e.action,
                    "connector": e.category,
                    "status": e.status,
                    "sensitive": e.sensitive,
                    "details": e.details or {},
                }
                for e in entries
            ]

    def get_pending(self) -> List[Dict[str, Any]]:
        """Returns all currently pending confirmations in memory."""
        return list(self._pending_confirmations.values())


audit_manager = AuditManager()
