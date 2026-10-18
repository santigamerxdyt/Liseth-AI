"""
Git Sync Action for JARVIS / Liseth.
Bridges git auto-synchronization and cloud updates to the action dispatcher
and zero-latency brain router.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.services.git_sync_service import git_sync_service

logger = logging.getLogger("jarvis.git_sync_action")


def git_sync_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    """
    Synchronous entrypoint for Git Sync operations.
    Handles 'sync', 'status', 'start_watcher', 'stop_watcher'.
    """
    params = parameters or {}
    action = params.get("action", "sync").lower().strip()
    message = params.get("message")

    try:
        if action in ["status", "estado", "info"]:
            st = git_sync_service.get_status()
            watcher_str = "Activo (Cada 5 min)" if st.get("auto_sync_active") else "Inactivo (Bajo demanda)"
            clean_str = "Limpio (Sin cambios pendientes)" if st.get("clean") else f"{st.get('uncommitted_count')} archivos modificados pendientes de subir"
            return (
                "📊 **Estado de Sincronización con GitHub**:\n"
                f"• **Rama:** `{st.get('branch', 'main')}`\n"
                f"• **Estado Local:** {clean_str}\n"
                f"• **Último Commit:** {st.get('last_commit', 'N/A')}\n"
                f"• **Centinela en Segundo Plano:** {watcher_str}\n"
                f"• **Repositorio:** https://github.com/santigamerxdyt/Liseth-AI\n"
                f"• **Web Pública (GitHub Pages):** https://santigamerxdyt.github.io/Liseth-AI/"
            )

        elif action in ["start_watcher", "iniciar_centinela"]:
            git_sync_service.start_background_watcher(interval_seconds=params.get("interval", 300))
            return "Señor Santiago, he activado el centinela automático de GitHub. Cualquier cambio que realice en el proyecto se subirá automáticamente en segundo plano cada 5 minutos."

        elif action in ["stop_watcher", "detener_centinela"]:
            git_sync_service.stop_background_watcher()
            return "Señor Santiago, he detenido el centinela automático de GitHub. La sincronización se realizará únicamente cuando me lo solicite."

        else:
            # Default: execute sync
            res = git_sync_service.sync_to_github(custom_message=message)
            return git_sync_service.format_report(res)

    except Exception as e:
        logger.error(f"Error in git_sync_action: {e}", exc_info=True)
        return f"Señor Santiago, ocurrió un error durante la sincronización: {str(e)}"
