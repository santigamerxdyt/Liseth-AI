"""
Workspace Sentinel Action for JARVIS / Liseth.
Wraps WorkspaceSentinel queries and manual scan requests.
"""
import logging
from typing import Any, Dict, Optional
from app.services.workspace_sentinel import workspace_sentinel

logger = logging.getLogger("jarvis.workspace_sentinel_action")


def workspace_sentinel_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    """
    Handles user requests regarding workspace sentinel:
    - action: 'status' | 'scan' | 'watch' | 'list'
    - path: directory path to watch or scan
    """
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    path = params.get("path", "").strip()

    if action in ("status", "check"):
        return workspace_sentinel.get_status_summary()

    elif action in ("scan", "force_scan"):
        rep = workspace_sentinel.scan_workspace(workspace_path=path or None, force=True)
        if rep.healthy:
            return (
                f"Escaneo de centinela completado en `{rep.workspace_path}`:\n"
                f"• {rep.files_scanned} archivos analizados.\n"
                f"• Cero errores encontrados. Su código está en perfecto estado, señor Santiago. ✅"
            )
        else:
            return rep.format_alert()

    elif action == "watch":
        if not path:
            return "Por favor especifique la ruta de la carpeta o repositorio que desea vigilar, señor Santiago."
        ok = workspace_sentinel.watch_directory(path)
        if ok:
            return f"He agregado `{path}` a la vigilancia en segundo plano de mi Centinela, señor Santiago."
        return f"No pude encontrar el directorio `{path}` en su sistema."

    elif action == "list":
        watched = workspace_sentinel.list_watched()
        if not watched:
            return "No hay proyectos en vigilancia actualmente, señor Santiago."
        items = "\n".join([f"• `{p}`" for p in watched])
        return f"📁 **Proyectos bajo vigilancia del Centinela**:\n{items}"

    return workspace_sentinel.get_status_summary()
