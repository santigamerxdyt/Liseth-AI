"""
Ego Browser Action for JARVIS / Liseth.
Exposes autonomous, token-efficient web navigation, accessibility snapshots,
element interactions, and site learnings to the action dispatcher and brain router.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

from app.services.ego_browser_service import ego_browser_service

logger = logging.getLogger("jarvis.ego_browser_action")


def ego_browser_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    """
    Synchronous entrypoint for Ego Browser automation tool.
    Can be called directly or run inside a thread pool executor.
    """
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    url = params.get("url") or params.get("link") or ""
    target = params.get("target") or params.get("element") or params.get("ref") or ""
    value = params.get("value") or params.get("text") or ""
    space = params.get("space") or params.get("task_space") or "default"
    query = params.get("query") or params.get("q") or ""
    repo = params.get("repo") or params.get("repository") or ""
    script = params.get("script") or params.get("code") or ""

    try:
        # 1. Status query
        if action in ["status", "estado", "info"]:
            st = ego_browser_service.get_status()
            return ego_browser_service.format_status_report(st)

        # 2. List spaces
        if action in ["spaces", "list_spaces", "espacios"]:
            spaces = ego_browser_service.list_spaces()
            if not spaces:
                return "Señor Santiago, no hay espacios de tarea (`taskSpaces`) activos en este momento."
            lines = ["### 🗂️ Espacios de Tarea Activos en Ego Browser:"]
            for s in spaces:
                lines.append(f"- **`{s['name']}`**: `{s['url']}` ({s['title']}) — {s['interactive_count']} refs")
            return "\n".join(lines)

        # 3. Close space
        if action in ["close_space", "cerrar_espacio"]:
            target_space = space if space != "default" else (params.get("name") or "default")
            closed = ego_browser_service.close_space(target_space)
            if closed:
                return f"Señor Santiago, el espacio de tarea `{target_space}` ha sido cerrado y sus recursos liberados."
            return f"Señor Santiago, el espacio `{target_space}` no estaba activo."

        # 4. Navigate / Open URL
        if action in ["navigate", "nav", "open", "ir", "abrir"]:
            if not url:
                return "Señor Santiago, debe especificar la URL a la cual desea navegar (ejemplo: `url='https://news.ycombinator.com'`)."
            res = ego_browser_service.navigate(url=url, space_name=space)
            return ego_browser_service.format_snapshot_report(res)

        # 5. Snapshot / Accessibility Tree
        if action in ["snapshot", "snap", "arbol", "tree"]:
            if url:
                res = ego_browser_service.navigate(url=url, space_name=space)
            else:
                res = ego_browser_service.snapshot(space_name=space)
            return ego_browser_service.format_snapshot_report(res)

        # 6. Click on element
        if action in ["click", "clic", "presionar", "pulsar"]:
            if not target:
                return "Señor Santiago, indique el número de referencia [ref=N] o selector del elemento que desea presionar."
            res = ego_browser_service.click(target=target, space_name=space)
            return (
                f"### ✅ Acción Completada en Ego Browser\n"
                f"- **Acción**: Clic en {res.get('target')}\n"
                f"- **Espacio**: `{space}`\n"
                f"- **Nueva URL**: `{res.get('url')}`\n"
                f"- **Título**: {res.get('title')}\n\n"
                f"**Snapshot Actualizado:**\n"
                f"```yaml\n{res.get('snapshot', '')[:2000]}\n```"
            )

        # 7. Fill input
        if action in ["fill", "escribe", "escribir", "type"]:
            if not target:
                return "Señor Santiago, indique el elemento o referencia [ref=N] donde desea escribir."
            res = ego_browser_service.fill(target=target, value=value, space_name=space)
            return (
                f"### ✍️ Texto Ingresado en Ego Browser\n"
                f"- **Campo**: {res.get('target')}\n"
                f"- **Texto**: `{value}`\n"
                f"- **Espacio**: `{space}`\n\n"
                f"**Snapshot Actualizado:**\n"
                f"```yaml\n{res.get('snapshot', '')[:2000]}\n```"
            )

        # 8. Screenshot
        if action in ["screenshot", "captura", "pantallazo"]:
            if url:
                ego_browser_service.navigate(url=url, space_name=space)
            path = ego_browser_service.screenshot(space_name=space, output_path=params.get("output_path"))
            return (
                f"### 📸 Captura de Pantalla Tomada\n"
                f"- **Espacio**: `{space}`\n"
                f"- **Archivo Guardado**: `{path}`\n\n"
                f"La captura ha sido generada exitosamente en alta definición, señor Santiago."
            )

        # 9. Learned: Google Search
        if action in ["google", "google_search", "buscar_google"]:
            search_query = query or value or url
            if not search_query:
                return "Señor Santiago, proporcione los términos de búsqueda que desea consultar en Google."
            max_r = int(params.get("max_results") or 10)
            results = ego_browser_service.google_search(query=search_query, max_results=max_r)
            return ego_browser_service.format_google_results(search_query, results)

        # 10. Learned: GitHub Repo Stats
        if action in ["github", "github_stats", "repo_stats"]:
            target_repo = repo or query or url
            if not target_repo:
                return "Señor Santiago, especifique el repositorio de GitHub (ejemplo: `facebook/react` o `torvalds/linux`)."
            stats = ego_browser_service.github_repo_stats(target_repo)
            return ego_browser_service.format_github_stats(target_repo, stats)

        # 11. Run CLI Script (ego-browser.cmd bridge)
        if action in ["cli", "script", "js", "run"]:
            if not script:
                return "Señor Santiago, proporcione el script en JavaScript que desea ejecutar en el motor Ego Lite."
            res = ego_browser_service.run_ego_cli(script)
            if res.get("success"):
                return (
                    f"### ⚡ Script Ejecutado en Ego CLI\n"
                    f"```text\n{res.get('output') or 'Ejecución exitosa sin salida en stdout'}\n```"
                )
            else:
                return (
                    f"### ⚠️ Error en Ejecución de Script Ego CLI\n"
                    f"- **Error**: `{res.get('error')}`\n"
                    f"- **Código de Salida**: `{res.get('exit_code')}`"
                )

        # Default fallback
        if url:
            res = ego_browser_service.navigate(url=url, space_name=space)
            return ego_browser_service.format_snapshot_report(res)

        return (
            f"Señor Santiago, no se reconoció la acción '{action}'. "
            f"Las acciones soportadas por Ego Browser son: `status`, `navigate`, `snapshot`, `click`, `fill`, "
            f"`screenshot`, `google`, `github`, `spaces`, `close_space` y `script`."
        )

    except Exception as e:
        logger.error(f"Error executing ego_browser_action '{action}': {e}", exc_info=True)
        return f"Señor Santiago, ocurrió una excepción durante la ejecución de Ego Browser: {str(e)}"
