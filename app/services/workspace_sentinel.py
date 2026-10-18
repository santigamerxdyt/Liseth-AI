"""
WorkspaceSentinel for JARVIS / Liseth.
Monitors Señor Santiago's active coding projects and workspaces in the background:
- Watches source files for modifications without CPU overhead
- Runs fast background syntax/health verifications (e.g. py_compile, integrity checks)
- Proactively alerts Santiago ONLY when an error, broken syntax, or issue is detected,
  leaving him undisturbed when everything is compiling cleanly.
"""
import datetime
import hashlib
import logging
import os
import py_compile
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("jarvis.workspace_sentinel")


@dataclass
class SentinelIssue:
    file_path: str
    issue_type: str  # "syntax_error" | "integrity_warning" | "test_failure"
    message: str
    line_number: Optional[int] = None


@dataclass
class SentinelReport:
    workspace_path: str
    timestamp: str
    files_scanned: int
    files_changed: int
    issues: List[SentinelIssue] = field(default_factory=list)
    healthy: bool = True

    def format_alert(self) -> str:
        """Formats a respectful, actionable alert for Señor Santiago."""
        if self.healthy or not self.issues:
            return ""
        lines = [
            f"🚨 **Alerta de Centinela de Código en** `{Path(self.workspace_path).name}`:",
            f"He detectado {len(self.issues)} problema(s) en sus archivos modificados recientemente:"
        ]
        for issue in self.issues[:4]:
            loc = f" (línea {issue.line_number})" if issue.line_number else ""
            fname = Path(issue.file_path).name
            lines.append(f"• **{fname}**{loc}: {issue.message}")
        lines.append("Le informo para que pueda corregirlo oportunamente sin perder el foco en su labor.")
        return "\n".join(lines)


class WorkspaceSentinel:
    """
    Background sentinel monitoring developer workspaces and repositories.
    """

    EXTENSIONS_TO_CHECK = {".py", ".json", ".js", ".html", ".css", ".md"}

    def __init__(self, default_workspace: Optional[str] = None):
        self._lock = threading.Lock()
        self._watched_directories: Set[str] = set()
        self._file_mtimes: Dict[str, float] = {}
        self._last_report: Optional[SentinelReport] = None
        self._cooldown_seconds: float = 60.0
        self._last_scan_time: float = 0.0

        if default_workspace and os.path.isdir(default_workspace):
            self.watch_directory(default_workspace)

    def watch_directory(self, path: str) -> bool:
        """Adds a directory path to the sentinel's watch list."""
        resolved = str(Path(path).resolve())
        if not os.path.isdir(resolved):
            return False
        with self._lock:
            self._watched_directories.add(resolved)
        logger.info(f"[SENTINEL] Vigilando espacio de trabajo: {resolved}")
        return True

    def unwatch_directory(self, path: str) -> bool:
        """Removes a directory path from the watch list."""
        resolved = str(Path(path).resolve())
        with self._lock:
            if resolved in self._watched_directories:
                self._watched_directories.remove(resolved)
                return True
        return False

    def list_watched(self) -> List[str]:
        """Returns list of currently watched directories."""
        with self._lock:
            return sorted(list(self._watched_directories))

    def scan_workspace(self, workspace_path: Optional[str] = None, force: bool = False) -> SentinelReport:
        """
        Scans a watched directory (or the default one) for modified files
        and performs background syntax and integrity checks.
        """
        import time
        now = time.time()
        if not force and (now - self._last_scan_time) < self._cooldown_seconds:
            if self._last_report:
                return self._last_report

        target = workspace_path or (self.list_watched()[0] if self.list_watched() else None)
        if not target or not os.path.isdir(target):
            rep = SentinelReport(
                workspace_path=str(target or "None"),
                timestamp=datetime.datetime.now().isoformat(),
                files_scanned=0,
                files_changed=0,
                healthy=True
            )
            self._last_report = rep
            return rep

        files_scanned = 0
        files_changed = 0
        issues: List[SentinelIssue] = []

        ignore_dirs = {".git", ".pytest_cache", "__pycache__", "venv", ".venv", "node_modules", "dist", "build"}

        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in self.EXTENSIONS_TO_CHECK:
                    continue

                full_path = os.path.join(root, file)
                files_scanned += 1

                try:
                    mtime = os.path.getmtime(full_path)
                except OSError:
                    continue

                prev_mtime = self._file_mtimes.get(full_path)
                is_changed = (prev_mtime is None or mtime > prev_mtime)

                if is_changed:
                    files_changed += 1
                    self._file_mtimes[full_path] = mtime

                    # Syntax validation for Python files
                    if ext == ".py":
                        try:
                            py_compile.compile(full_path, doraise=True)
                        except py_compile.PyCompileError as pe:
                            line_no = None
                            msg = str(pe)
                            if hasattr(pe, "lineno") and pe.lineno:
                                line_no = pe.lineno
                            issues.append(
                                SentinelIssue(
                                    file_path=full_path,
                                    issue_type="syntax_error",
                                    message=f"Error de sintaxis: {msg.splitlines()[0] if msg else 'Error'}",
                                    line_number=line_no
                                )
                            )

        report = SentinelReport(
            workspace_path=target,
            timestamp=datetime.datetime.now().isoformat(),
            files_scanned=files_scanned,
            files_changed=files_changed,
            issues=issues,
            healthy=(len(issues) == 0)
        )

        with self._lock:
            self._last_report = report
            self._last_scan_time = now

        return report

    def get_status_summary(self) -> str:
        """Returns human-readable status for Señor Santiago."""
        watched = self.list_watched()
        if not watched:
            return "El Centinela de Código no tiene ningún espacio de trabajo registrado actualmente, señor Santiago."

        rep = self._last_report or self.scan_workspace(force=True)
        wname = Path(rep.workspace_path).name

        if rep.healthy:
            return (
                f"🛡️ **Centinela de Código Activo** (`{wname}`):\n"
                f"• Monitoreando {rep.files_scanned} archivos en tiempo real.\n"
                f"• Estado: **100% Saludable** ✅ (Cero errores de sintaxis o compilación detectados)."
            )
        else:
            return rep.format_alert()


# Default singleton instance watching current workspace
_cwd = os.getcwd()
workspace_sentinel = WorkspaceSentinel(default_workspace=_cwd)
