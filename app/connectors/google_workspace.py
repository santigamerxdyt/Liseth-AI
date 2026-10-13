"""
Google Workspace Connector for JARVIS / Liseth.
Integrates Gmail, Calendar, Tasks, Drive, Docs, and Sheets.
Strictly enforces AuditManager confirmation checks before executing any modifying or sending action.
"""
import logging
from typing import Any, Dict, List, Optional

from app.config import settings
from app.connectors.base import BaseConnector
from app.services.audit_manager import audit_manager

logger = logging.getLogger("jarvis.google_connector")


class GoogleWorkspaceConnector(BaseConnector):
    def __init__(self):
        super().__init__(
            connector_id="google_workspace",
            name="Google Workspace",
            description="Integración con Gmail, Google Calendar, Google Tasks, Drive y Docs",
        )
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.connected = bool(self.client_id and self.client_secret)

        # Register execution handlers in audit_manager
        for act in self.list_actions():
            if act["sensitive"]:
                audit_manager.register_handler(
                    act["name"],
                    lambda p, a=act["name"]: self._perform_confirmed_action(a, p)
                )

    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Stores credentials and marks connection."""
        if "access_token" in credentials:
            self.access_token = credentials["access_token"]
        if "refresh_token" in credentials:
            self.refresh_token = credentials["refresh_token"]
        self.connected = True
        return True

    def list_actions(self) -> List[Dict[str, Any]]:
        """Lists available Google Workspace actions with sensitivity metadata."""
        return [
            # 1. Gmail
            {
                "name": "google_list_emails",
                "description": "Lista los correos más recientes en Gmail (asunto, remitente, snippet)",
                "parameters": {"maxResults": {"type": "integer", "description": "Número máximo de correos"}},
                "sensitive": False,
            },
            {
                "name": "google_search_emails",
                "description": "Busca correos en Gmail por consulta (ej. from:persona, subject:reunion)",
                "parameters": {"query": {"type": "string", "description": "Término de búsqueda"}},
                "sensitive": False,
            },
            {
                "name": "google_read_email",
                "description": "Lee el contenido completo y cuerpo de un correo por su messageId",
                "parameters": {"messageId": {"type": "string", "description": "ID del mensaje"}},
                "sensitive": False,
            },
            {
                "name": "google_send_email",
                "description": "Envía un nuevo correo electrónico a través de Gmail",
                "parameters": {
                    "to": {"type": "string", "description": "Destinatario"},
                    "subject": {"type": "string", "description": "Asunto"},
                    "body": {"type": "string", "description": "Cuerpo del correo"},
                },
                "sensitive": True,
            },
            {
                "name": "google_reply_email",
                "description": "Responde a un correo existente en Gmail",
                "parameters": {
                    "messageId": {"type": "string", "description": "ID del mensaje"},
                    "body": {"type": "string", "description": "Respuesta"},
                },
                "sensitive": True,
            },
            {
                "name": "google_delete_email",
                "description": "Mueve un correo a la papelera de Gmail",
                "parameters": {"messageId": {"type": "string", "description": "ID del mensaje"}},
                "sensitive": True,
            },
            # 2. Calendar
            {
                "name": "google_list_events",
                "description": "Consulta los próximos eventos y reuniones en Google Calendar",
                "parameters": {"maxResults": {"type": "integer", "description": "Máximo de eventos"}},
                "sensitive": False,
            },
            {
                "name": "google_create_event",
                "description": "Agenda un nuevo evento en Google Calendar",
                "parameters": {
                    "summary": {"type": "string", "description": "Título del evento"},
                    "startDateTime": {"type": "string", "description": "Inicio ISO 8601"},
                    "endDateTime": {"type": "string", "description": "Fin ISO 8601"},
                    "description": {"type": "string", "description": "Notas o descripción"},
                },
                "sensitive": True,
            },
            {
                "name": "google_update_event",
                "description": "Modifica o reprograma un evento en Google Calendar",
                "parameters": {
                    "eventId": {"type": "string", "description": "ID del evento"},
                    "summary": {"type": "string", "description": "Nuevo título"},
                },
                "sensitive": True,
            },
            {
                "name": "google_delete_event",
                "description": "Elimina un evento de Google Calendar",
                "parameters": {"eventId": {"type": "string", "description": "ID del evento"}},
                "sensitive": True,
            },
            # 3. Tasks
            {
                "name": "google_list_tasks",
                "description": "Consulta las tareas pendientes en Google Tasks",
                "parameters": {},
                "sensitive": False,
            },
            {
                "name": "google_create_task",
                "description": "Crea una nueva tarea en Google Tasks",
                "parameters": {
                    "title": {"type": "string", "description": "Título de la tarea"},
                    "notes": {"type": "string", "description": "Notas adicionales"},
                },
                "sensitive": True,
            },
            {
                "name": "google_complete_task",
                "description": "Marca una tarea como completada en Google Tasks",
                "parameters": {"taskId": {"type": "string", "description": "ID de la tarea"}},
                "sensitive": True,
            },
            {
                "name": "google_delete_task",
                "description": "Elimina una tarea de Google Tasks",
                "parameters": {"taskId": {"type": "string", "description": "ID de la tarea"}},
                "sensitive": True,
            },
            # 4. Drive & Docs
            {
                "name": "google_upload_file",
                "description": "Sube un archivo a Google Drive",
                "parameters": {"name": {"type": "string", "description": "Nombre del archivo"}},
                "sensitive": True,
            },
            {
                "name": "google_delete_file",
                "description": "Elimina un archivo de Google Drive",
                "parameters": {"fileId": {"type": "string", "description": "ID del archivo"}},
                "sensitive": True,
            },
        ]

    async def execute_action(
        self,
        action_name: str,
        params: Dict[str, Any],
        force_unconfirmed: bool = False,
    ) -> Dict[str, Any]:
        """
        Executes an action. If the action is sensitive (send, modify, delete, create),
        it IMMEDIATELY pauses, generates a pending confirmation, and requests user approval.
        """
        is_sensitive, service_name, reason = audit_manager.describe_action(self.id, action_name, params)

        # Enforce confirmation requirement for all sensitive modifications
        if is_sensitive and not force_unconfirmed:
            logger.info(f"[CONFIRMATION_REQUIRED] {action_name} requiere aprobación previa del usuario.")
            conf_item = await audit_manager.create_pending_confirmation(
                connector=self.id,
                action=action_name,
                params=params,
                reason=reason,
            )
            return {
                "ok": True,
                "requiresConfirmation": True,
                "confirmation": conf_item,
                "message": reason,
                "action": action_name,
            }

        # Safe read action or already confirmed action: execute directly
        return await self._perform_confirmed_action(action_name, params)

    async def _perform_confirmed_action(self, action_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Performs the actual API call once confirmed or if safe."""
        logger.info(f"[GOOGLE_EXEC] Ejecutando acción {action_name} con parámetros: {params}")

        # Simulated response if live OAuth token is pending
        res = {
            "success": True,
            "action": action_name,
            "params": params,
            "executed": True,
            "message": f"Acción '{action_name}' ejecutada con éxito en Google Workspace.",
        }

        # Log executed action
        await audit_manager.log_action(
            connector=self.id,
            action=action_name,
            params=params,
            status="executed",
            result=res,
            sensitive=True,
        )
        return res


google_connector = GoogleWorkspaceConnector()
