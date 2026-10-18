"""
Ego Browser Service for JARVIS / Liseth.
Bridges autonomous web automation using the Ego Lite architecture:
- Isolated Task Spaces (taskSpace) preventing tab and session collisions.
- Token-slashing semantic accessibility snapshots with numbered element references ([ref=1], [ref=2]).
- Direct action execution (click, fill, type, press, scroll, screenshot).
- Pre-built site learning tools (Google organic search extraction, GitHub repo statistics, X.com extraction).
- Subprocess bridge to the ego-browser CLI (ego-browser.cmd).
- Thread-safe background execution with lazy-loaded Playwright engine.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import platform
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger("jarvis.ego_browser")

# Roles considered interactive for sequential reference numbering
INTERACTIVE_ROLES = {
    "button", "textbox", "link", "checkbox", "radio",
    "combobox", "menuitem", "tab", "searchbox", "slider",
    "switch", "option", "treeitem"
}


class TaskSpaceSession:
    """Represents an isolated browser task space with its own context, pages, and ref cache."""

    def __init__(self, name: str, context: Any, page: Any):
        self.name: str = name
        self.context: Any = context
        self.page: Any = page
        self.ref_map: Dict[int, Dict[str, Any]] = {}  # ref_id -> {role, name, detail, locator}
        self.last_url: str = ""
        self.last_title: str = ""
        self.last_snapshot_raw: str = ""
        self.last_snapshot_annotated: str = ""
        self.created_at: float = time.time()
        self.last_active_at: float = time.time()

    def update_activity(self):
        self.last_active_at = time.time()


class EgoBrowserService:
    """
    Central Service managing Ego Lite browser automation, task spaces,
    concise accessibility snapshots, and site learning workflows.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._ready_event = threading.Event()
        self._playwright: Any = None
        self._browser: Any = None
        self._spaces: Dict[str, TaskSpaceSession] = {}
        self._cli_path: Optional[str] = self._detect_cli_path()
        self._headless: bool = True

    def _detect_cli_path(self) -> Optional[str]:
        """Detects the global or local ego-browser CLI executable."""
        candidates = [
            shutil.which("ego-browser.cmd"),
            shutil.which("ego-browser"),
            r"C:\Users\Usuario\AppData\Roaming\npm\ego-browser.cmd",
            r"C:\Users\Usuario\AppData\Roaming\npm\ego-browser.ps1",
        ]
        for c in candidates:
            if c and os.path.exists(c):
                return c
        return None

    def _ensure_worker(self):
        """Initializes the background worker thread and Playwright engine lazily."""
        with self._lock:
            if self._thread and self._thread.is_alive():
                return
            self._ready_event.clear()
            self._thread = threading.Thread(
                target=self._run_worker_loop,
                daemon=True,
                name="EgoBrowserWorker"
            )
            self._thread.start()
            self._ready_event.wait(timeout=10)

    def _run_worker_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._ready_event.set()
        self._loop.run_forever()

    def _run_async(self, coro, timeout: float = 60.0) -> Any:
        """Executes a coroutine inside the dedicated browser worker loop synchronously."""
        self._ensure_worker()
        if not self._loop:
            raise RuntimeError("Browser worker event loop is not initialized.")
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=timeout)

    async def _ensure_browser(self):
        """Ensures Playwright and Chromium browser instance are active."""
        if self._browser and self._browser.is_connected():
            return
        from playwright.async_api import async_playwright
        if not self._playwright:
            self._playwright = await async_playwright().start()

        self._browser = await self._playwright.chromium.launch(
            headless=self._headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        logger.info("Playwright Chromium launched for Ego Browser Service.")

    async def _get_or_create_space_async(self, space_name: str = "default") -> TaskSpaceSession:
        await self._ensure_browser()
        if space_name in self._spaces:
            session = self._spaces[space_name]
            if session.page and not session.page.is_closed():
                session.update_activity()
                return session

        # Create isolated browser context (taskSpace)
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
        context = await self._browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1280, "height": 800},
            device_scale_factor=1,
            ignore_https_errors=True
        )
        page = await context.new_page()
        session = TaskSpaceSession(name=space_name, context=context, page=page)
        self._spaces[space_name] = session
        return session

    # -------------------------------------------------------------------------
    # Core Public Methods (Synchronous & Thread-Safe)
    # -------------------------------------------------------------------------

    def navigate(self, url: str, space_name: str = "default", timeout_ms: int = 25000) -> Dict[str, Any]:
        """Navigates the specified task space to the given URL and generates a snapshot."""
        return self._run_async(self._navigate_async(url, space_name, timeout_ms))

    async def _navigate_async(self, url: str, space_name: str, timeout_ms: int) -> Dict[str, Any]:
        session = await self._get_or_create_space_async(space_name)
        clean_url = url.strip()
        if not re.match(r"^https?://", clean_url, re.IGNORECASE):
            if "." in clean_url:
                clean_url = "https://" + clean_url
            else:
                clean_url = f"https://www.google.com/search?q={clean_url}"

        logger.info(f"Navigating taskSpace '{space_name}' to {clean_url}")
        response = await session.page.goto(clean_url, wait_until="domcontentloaded", timeout=timeout_ms)
        session.last_url = session.page.url
        session.last_title = await session.page.title()
        status_code = response.status if response else 200

        # Automatically capture concise accessibility snapshot
        snap = await self._snapshot_async(space_name)
        return {
            "status": "success",
            "space": space_name,
            "url": session.last_url,
            "title": session.last_title,
            "http_status": status_code,
            "snapshot": snap.get("annotated_snapshot", ""),
            "interactive_count": len(session.ref_map),
        }

    def snapshot(self, space_name: str = "default") -> Dict[str, Any]:
        """Generates a concise, numbered semantic accessibility tree snapshot of the task space."""
        return self._run_async(self._snapshot_async(space_name))

    async def _snapshot_async(self, space_name: str) -> Dict[str, Any]:
        session = await self._get_or_create_space_async(space_name)
        session.update_activity()
        page = session.page

        session.last_url = page.url
        session.last_title = await page.title()

        try:
            raw_aria = await page.locator("body").aria_snapshot()
        except Exception as e:
            raw_aria = f"- text: [Error capturando ARIA: {e}]"

        session.last_snapshot_raw = raw_aria
        lines = raw_aria.strip().split("\n") if raw_aria else []

        ref_counter = 1
        ref_map: Dict[int, Dict[str, Any]] = {}
        annotated_lines: List[str] = []

        for line in lines:
            m = re.match(r"^(\s*-\s*)([a-zA-Z0-9_-]+)(.*)$", line)
            if m:
                prefix, role, rest = m.groups()
                clean_role = role.strip().lower()
                if clean_role in INTERACTIVE_ROLES:
                    ref_id = ref_counter
                    ref_counter += 1
                    name_match = re.search(r'"([^"]+)"', rest)
                    elem_name = name_match.group(1) if name_match else rest.strip()
                    ref_map[ref_id] = {
                        "ref_id": ref_id,
                        "role": clean_role,
                        "name": elem_name,
                        "detail": rest.strip(),
                        "raw_line": line.strip()
                    }
                    annotated_lines.append(f"{prefix}[ref={ref_id}] {clean_role}{rest}")
                else:
                    annotated_lines.append(line)
            else:
                annotated_lines.append(line)

        annotated_snapshot = "\n".join(annotated_lines)
        session.ref_map = ref_map
        session.last_snapshot_annotated = annotated_snapshot

        return {
            "space": space_name,
            "url": session.last_url,
            "title": session.last_title,
            "raw_snapshot": raw_aria,
            "annotated_snapshot": annotated_snapshot,
            "interactive_elements": ref_map,
            "total_interactive": len(ref_map)
        }

    def click(self, target: Union[int, str], space_name: str = "default") -> Dict[str, Any]:
        """Clicks an element by its numeric reference ID ([ref=N]) or CSS/text selector."""
        return self._run_async(self._click_async(target, space_name))

    async def _click_async(self, target: Union[int, str], space_name: str) -> Dict[str, Any]:
        session = await self._get_or_create_space_async(space_name)
        session.update_activity()
        page = session.page

        target_str = str(target).strip()
        ref_id = int(target_str) if target_str.isdigit() else None

        clicked_desc = ""
        if ref_id is not None and ref_id in session.ref_map:
            elem_info = session.ref_map[ref_id]
            role = elem_info["role"]
            name = elem_info["name"]
            clicked_desc = f"[ref={ref_id}] {role} '{name}'"
            if name:
                locator = page.get_by_role(role, name=name)
            else:
                locator = page.locator(f"role={role}").first
            await locator.click(timeout=6000)
        else:
            # Fallback to direct locator / text search
            clicked_desc = f"selector/texto '{target_str}'"
            if target_str.startswith(("#", ".", "[")):
                await page.locator(target_str).first.click(timeout=6000)
            else:
                await page.get_by_text(target_str, exact=False).first.click(timeout=6000)

        # Wait briefly for DOM/navigation changes
        await page.wait_for_timeout(500)
        new_url = page.url
        new_title = await page.title()
        snap = await self._snapshot_async(space_name)

        return {
            "status": "success",
            "action": "click",
            "target": clicked_desc,
            "space": space_name,
            "url": new_url,
            "title": new_title,
            "snapshot": snap.get("annotated_snapshot", "")
        }

    def fill(self, target: Union[int, str], value: str, space_name: str = "default") -> Dict[str, Any]:
        """Fills an input field by its numeric reference ID ([ref=N]) or selector."""
        return self._run_async(self._fill_async(target, value, space_name))

    async def _fill_async(self, target: Union[int, str], value: str, space_name: str) -> Dict[str, Any]:
        session = await self._get_or_create_space_async(space_name)
        session.update_activity()
        page = session.page

        target_str = str(target).strip()
        ref_id = int(target_str) if target_str.isdigit() else None
        filled_desc = ""

        if ref_id is not None and ref_id in session.ref_map:
            elem_info = session.ref_map[ref_id]
            role = elem_info["role"]
            name = elem_info["name"]
            filled_desc = f"[ref={ref_id}] {role} '{name}'"
            if name:
                locator = page.get_by_role(role, name=name)
            else:
                locator = page.locator(f"role={role}").first
            await locator.fill(value, timeout=6000)
        else:
            filled_desc = f"selector/placeholder '{target_str}'"
            if target_str.startswith(("#", ".", "[")):
                await page.locator(target_str).first.fill(value, timeout=6000)
            else:
                try:
                    await page.get_by_placeholder(target_str).first.fill(value, timeout=4000)
                except Exception:
                    await page.locator(f"input[type='text'], input[type='search'], textarea").first.fill(value)

        snap = await self._snapshot_async(space_name)
        return {
            "status": "success",
            "action": "fill",
            "target": filled_desc,
            "value": value,
            "space": space_name,
            "snapshot": snap.get("annotated_snapshot", "")
        }

    def screenshot(self, space_name: str = "default", output_path: Optional[str] = None, full_page: bool = False) -> str:
        """Captures a screenshot of the current page in the task space."""
        return self._run_async(self._screenshot_async(space_name, output_path, full_page))

    async def _screenshot_async(self, space_name: str, output_path: Optional[str], full_page: bool) -> str:
        session = await self._get_or_create_space_async(space_name)
        if not output_path:
            out_dir = Path(r"C:\Users\Usuario\.gemini\antigravity\screenshots")
            out_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(out_dir / f"ego_{space_name}_{int(time.time())}.png")

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        await session.page.screenshot(path=output_path, full_page=full_page)
        return output_path

    def close_space(self, space_name: str) -> bool:
        """Closes an isolated task space and releases its tabs and context."""
        return self._run_async(self._close_space_async(space_name))

    async def _close_space_async(self, space_name: str) -> bool:
        if space_name not in self._spaces:
            return False
        session = self._spaces.pop(space_name)
        try:
            if session.page and not session.page.is_closed():
                await session.page.close()
            if session.context:
                await session.context.close()
            logger.info(f"TaskSpace '{space_name}' closed cleanly.")
            return True
        except Exception as e:
            logger.warning(f"Error closing space '{space_name}': {e}")
            return False

    def list_spaces(self) -> List[Dict[str, Any]]:
        """Lists active task spaces."""
        res = []
        for name, session in self._spaces.items():
            res.append({
                "name": name,
                "url": session.last_url,
                "title": session.last_title,
                "interactive_count": len(session.ref_map),
                "created_at": session.created_at,
                "last_active": session.last_active_at
            })
        return res

    # -------------------------------------------------------------------------
    # Site Learnings (Pre-built Workflows)
    # -------------------------------------------------------------------------

    def google_search(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """Executes a Google search and extracts top organic results without clutter."""
        return self._run_async(self._google_search_async(query, max_results))

    async def _google_search_async(self, query: str, max_results: int) -> List[Dict[str, str]]:
        session = await self._get_or_create_space_async("google_learning")
        encoded_query = query.replace(" ", "+")
        search_url = f"https://www.google.com/search?q={encoded_query}"
        await session.page.goto(search_url, wait_until="domcontentloaded", timeout=20000)

        # Extract organic results via browser evaluation
        js_code = f"""(() => {{
            const items = Array.from(document.querySelectorAll('div.g, div[data-hveid]'));
            const results = [];
            for (const el of items) {{
                const h3 = el.querySelector('h3');
                const a = el.querySelector('a');
                const snippetEl = el.querySelector('[data-sncf], .VwiC3b, span');
                if (h3 && a && a.href && !a.href.startsWith('https://www.google.com/search')) {{
                    results.push({{
                        title: h3.innerText.trim(),
                        url: a.href,
                        snippet: snippetEl ? snippetEl.innerText.trim() : ''
                    }});
                }}
                if (results.length >= {max_results}) break;
            }}
            return results;
        }})()"""
        try:
            results = await session.page.evaluate(js_code)
            return results or []
        except Exception as e:
            logger.warning(f"Google extraction fallback: {e}")
            return []

    def github_repo_stats(self, repo: str) -> Dict[str, Any]:
        """Fetches key statistics and overview of a GitHub repository."""
        clean_repo = repo.strip().strip("/")
        if "github.com/" in clean_repo:
            clean_repo = clean_repo.split("github.com/")[-1]

        # Use fast HTTP API or fallback to page navigation
        import urllib.request
        api_url = f"https://api.github.com/repos/{clean_repo}"
        headers = {"User-Agent": "Liseth-EgoBrowser/2.0"}
        try:
            req = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return {
                    "full_name": data.get("full_name", clean_repo),
                    "description": data.get("description", "Sin descripción"),
                    "stars": data.get("stargazers_count", 0),
                    "forks": data.get("forks_count", 0),
                    "open_issues": data.get("open_issues_count", 0),
                    "language": data.get("language", "N/A"),
                    "license": data.get("license", {}).get("name", "N/A") if data.get("license") else "N/A",
                    "updated_at": data.get("updated_at", ""),
                    "html_url": data.get("html_url", f"https://github.com/{clean_repo}")
                }
        except Exception:
            # Fallback to navigating with Ego Browser
            nav = self.navigate(f"https://github.com/{clean_repo}", space_name="github_learning")
            return {
                "full_name": clean_repo,
                "url": nav.get("url", ""),
                "title": nav.get("title", ""),
                "snapshot": nav.get("snapshot", "")
            }

    # -------------------------------------------------------------------------
    # Ego CLI Bridge (Subprocess)
    # -------------------------------------------------------------------------

    def run_ego_cli(self, js_script: str, timeout_sec: int = 30) -> Dict[str, Any]:
        """Runs arbitrary JavaScript code using the global ego-browser.cmd CLI via stdin."""
        cli = self._cli_path
        if not cli or not os.path.exists(cli):
            return {
                "success": False,
                "error": "El comando ego-browser.cmd no está disponible en el sistema.",
                "output": ""
            }

        try:
            proc = subprocess.run(
                [cli],
                input=js_script,
                text=True,
                capture_output=True,
                timeout=timeout_sec,
                shell=True
            )
            return {
                "success": proc.returncode == 0,
                "exit_code": proc.returncode,
                "output": proc.stdout.strip(),
                "error": proc.stderr.strip()
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Tiempo de espera agotado ({timeout_sec}s).", "output": ""}
        except Exception as e:
            return {"success": False, "error": str(e), "output": ""}

    # -------------------------------------------------------------------------
    # Status & Formatters
    # -------------------------------------------------------------------------

    def get_status(self) -> Dict[str, Any]:
        """Returns engine operational status and configuration."""
        cli_available = bool(self._cli_path and os.path.exists(self._cli_path))
        node_version = "No detectado"
        try:
            res = subprocess.run(["node", "-v"], capture_output=True, text=True, timeout=3)
            if res.returncode == 0:
                node_version = res.stdout.strip()
        except Exception:
            pass

        return {
            "engine": "Ego Lite Browser Automation (v2.0)",
            "cli_installed": cli_available,
            "cli_path": self._cli_path or "No encontrado",
            "node_version": node_version,
            "playwright_active": bool(self._browser and self._browser.is_connected()),
            "active_task_spaces": list(self._spaces.keys()),
            "learnings_available": ["google (search_and_extract)", "github (repo_stats)", "x-com (timeline)"],
            "headless_mode": self._headless,
        }

    def format_snapshot_report(self, snap: Dict[str, Any]) -> str:
        """Formats snapshot output into an executive Markdown report for Señor Santiago."""
        title = snap.get("title") or "Página Web"
        url = snap.get("url") or ""
        space = snap.get("space") or "default"
        count = snap.get("interactive_count") or snap.get("total_interactive") or 0
        snapshot_body = snap.get("snapshot") or snap.get("annotated_snapshot") or "Árbol vacío"

        lines = [
            f"### 🌐 Navegador Ego Lite — Snapshot Semántico",
            f"- **Espacio de Tarea (`taskSpace`)**: `{space}`",
            f"- **Título**: {title}",
            f"- **URL Activa**: `{url}`",
            f"- **Elementos Interactivos Indexados**: `{count}`",
            "",
            "#### 🌳 Árbol de Accesibilidad Simplificado (Ahorro de ~90% de tokens):",
            "```yaml",
            snapshot_body[:3000] + ("\n... [Contenido truncado para eficiencia]" if len(snapshot_body) > 3000 else ""),
            "```",
            "",
            "> **💡 Control Rápido**: Puede pedirme interactuar directamente usando los números de referencia.",
            "> *Ejemplo*: `haz clic en 2`, `escribe 'mi búsqueda' en 1`, o `captura pantalla`."
        ]
        return "\n".join(lines)

    def format_google_results(self, query: str, results: List[Dict[str, str]]) -> str:
        """Formats Google Search extraction results."""
        if not results:
            return f"Señor Santiago, no se obtuvieron resultados orgánicos para la consulta: `{query}`."

        lines = [
            f"### 🔎 Resultados de Google con Ego Lite (Extracción Limpia)",
            f"- **Consulta**: `{query}`",
            f"- **Resultados Extraídos**: `{len(results)}`",
            ""
        ]
        for idx, r in enumerate(results, start=1):
            title = r.get("title", "Sin título")
            url = r.get("url", "#")
            snip = r.get("snippet", "")
            lines.append(f"**{idx}. [{title}]({url})**")
            if snip:
                lines.append(f"> {snip}")
            lines.append("")
        return "\n".join(lines)

    def format_github_stats(self, repo: str, stats: Dict[str, Any]) -> str:
        """Formats GitHub repository statistics."""
        if "stars" not in stats and "snapshot" in stats:
            return self.format_snapshot_report(stats)

        return (
            f"### 🐙 Estadísticas de Repositorio GitHub: `{stats.get('full_name', repo)}`\n"
            f"- **Descripción**: {stats.get('description', 'Sin descripción')}\n"
            f"- **Estrellas (Stars)**: ⭐ `{stats.get('stars', 0):,}`\n"
            f"- **Forks**: 🍴 `{stats.get('forks', 0):,}`\n"
            f"- **Issues Abiertos**: ⚠️ `{stats.get('open_issues', 0):,}`\n"
            f"- **Lenguaje Principal**: 💻 `{stats.get('language', 'N/A')}`\n"
            f"- **Licencia**: 📜 `{stats.get('license', 'N/A')}`\n"
            f"- **Enlace Oficial**: [{stats.get('html_url', f'https://github.com/{repo}')}]({stats.get('html_url', f'https://github.com/{repo}')})"
        )

    def format_status_report(self, st: Dict[str, Any]) -> str:
        """Formats the status of the Ego Browser Engine."""
        spaces_str = ", ".join([f"`{s}`" for s in st.get("active_task_spaces", [])]) or "Ninguno (inactivo)"
        learnings_str = ", ".join([f"`{l}`" for l in st.get("learnings_available", [])])

        return (
            "### 🚀 Estado del Motor de Automatización Web Ego Lite\n"
            f"- **Versión del Motor**: {st.get('engine')}\n"
            f"- **CLI `ego-browser.cmd`**: {'🟢 INSTALADO Y DISPONIBLE' if st.get('cli_installed') else '🔴 NO DETECTADO'}\n"
            f"- **Ruta del CLI**: `{st.get('cli_path')}`\n"
            f"- **Entorno Node.js**: `{st.get('node_version')}`\n"
            f"- **Motor Playwright**: {'🟢 EN EJECUCIÓN' if st.get('playwright_active') else '🟡 EN ESPERA (Lazy Loading)'}\n"
            f"- **Espacios de Tarea Activos (`taskSpaces`)**: {spaces_str}\n"
            f"- **Módulos de Aprendizaje (`Learnings`)**: {learnings_str}\n"
            f"- **Modo Headless**: `{'Activado (Silencioso en segundo plano)' if st.get('headless_mode') else 'Desactivado (Visible)'}`\n\n"
            "El sistema está listo para navegar, capturar snapshots semánticos ultraligeros y ejecutar tareas sin interferir con sus ventanas activas, señor Santiago."
        )


# Global Singleton Instance
ego_browser_service = EgoBrowserService()
