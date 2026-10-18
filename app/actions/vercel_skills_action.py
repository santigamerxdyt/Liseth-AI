"""
Vercel Skills Action for JARVIS / Liseth.
Exposes Vercel project deployment, React best practices auditing,
and Web Interface Guidelines compliance to the action dispatcher and brain router.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

from app.services.vercel_skills_service import vercel_skills_service

logger = logging.getLogger("jarvis.vercel_skills_action")


def vercel_skills_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    """
    Synchronous entrypoint for Vercel Skills tools.
    Can be run directly or inside a thread pool executor.
    """
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    target_path = params.get("path") or params.get("project_path") or params.get("file") or "."
    code = params.get("code") or ""
    prod = bool(params.get("prod") or params.get("production") or False)
    token = params.get("token") or os.environ.get("VERCEL_TOKEN")

    try:
        # 1. Status Telemetry
        if action in ["status", "estado", "info"]:
            st = vercel_skills_service.get_status()
            return vercel_skills_service.format_status_report(st)

        # 2. Framework Detection
        if action in ["framework", "detect", "detectar"]:
            resolved = os.path.abspath(target_path)
            res = vercel_skills_service.detect_framework(resolved)
            return (
                f"### 📦 Detección de Framework Web (Vercel Skills)\n"
                f"- **Proyecto**: `{os.path.basename(resolved)}`\n"
                f"- **Framework Identificado**: `{res.get('framework')}`\n"
                f"- **Tipo de Proyecto**: `{res.get('type')}`\n"
                f"- **package.json**: `{'Presente' if res.get('has_package_json') else 'No detectado'}`"
            )

        # 3. Project Packaging (Tarball)
        if action in ["package", "tarball", "empaquetar"]:
            resolved = os.path.abspath(target_path)
            tar_path, size = vercel_skills_service.create_project_tarball(resolved)
            return (
                f"### 📦 Paquete de Despliegue Generado\n"
                f"- **Archivo**: `{tar_path}`\n"
                f"- **Tamaño**: `{size:,} bytes`\n"
                f"- **Exclusiones**: Se ignoraron automáticamente `node_modules`, `.git`, `.next` y cachés locales."
            )

        # 4. Deploy to Vercel
        if action in ["deploy", "desplegar", "publicar", "publish"]:
            resolved = os.path.abspath(target_path)
            res = vercel_skills_service.deploy_project(project_path=resolved, prod=prod, token=token)
            return vercel_skills_service.format_deploy_report(res)

        # 5. React Best Practices Audit
        if action in ["audit_react", "react", "react_best_practices", "optimize_react", "auditar_react"]:
            if code:
                res = vercel_skills_service.audit_react_code(code=code, file_name=params.get("file_name", "Component.tsx"))
            else:
                resolved = os.path.abspath(target_path)
                res = vercel_skills_service.audit_react_file_or_dir(resolved)
            return vercel_skills_service.format_react_audit_report(res)

        # 6. Web Interface Guidelines & UX Audit
        if action in ["audit_design", "design", "ui", "ux", "web_design_guidelines", "auditar_diseño"]:
            if code:
                res = vercel_skills_service.audit_web_design(code, file_name=params.get("file_name", "index.html"))
            else:
                resolved = os.path.abspath(target_path)
                res = vercel_skills_service.audit_web_design(resolved)
            return vercel_skills_service.format_design_audit_report(res)

        return (
            f"Señor Santiago, no se reconoció la acción '{action}'. "
            f"Las acciones soportadas por Vercel Skills son: `status`, `deploy`, `audit_react`, `audit_design`, "
            f"`framework` y `package`."
        )

    except Exception as e:
        logger.error(f"Error in vercel_skills_action '{action}': {e}", exc_info=True)
        return f"Señor Santiago, ocurrió un error ejecutando la acción de Vercel: {str(e)}"
