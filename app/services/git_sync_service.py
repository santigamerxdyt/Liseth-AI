"""
Git Auto-Sync Service for Liseth AI / JARVIS.
Automatically detects project changes, creates safe commits, and pushes to GitHub:
- Respects .gitignore strictly (never commits .env, config/api_keys.json, tokens or databases).
- Reads GitHub credentials securely from Windows Credential Manager.
- Supports on-demand vocal/text sync and autonomous background interval sync.
- Generates structured telemetry reports on repository health and commits.
"""

from __future__ import annotations

import datetime
import logging
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvis.git_sync")


class GitSyncService:
    """Manages Git operations, repository tracking, and GitHub cloud synchronization."""

    def __init__(self, repo_dir: Optional[str] = None):
        self.repo_dir = Path(repo_dir or r"c:\Users\Usuario\Desktop\MI LISEHT").resolve()
        self._sync_lock = threading.Lock()
        self._watcher_thread: Optional[threading.Thread] = None
        self._stop_watcher_event = threading.Event()
        self.auto_sync_interval_seconds = 300  # Default: every 5 minutes in background
        self.last_sync_time: Optional[str] = None
        self.last_commit_hash: Optional[str] = None

    def get_status(self) -> Dict[str, Any]:
        """Checks the local working tree status and branch against remote origin."""
        try:
            # Check current branch
            branch_res = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=str(self.repo_dir),
                capture_output=True,
                text=True,
                check=False
            )
            current_branch = branch_res.stdout.strip() or "main"

            # Check uncommitted status
            status_res = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(self.repo_dir),
                capture_output=True,
                text=True,
                check=False
            )
            raw_status = status_res.stdout.strip()
            changed_files = [line.strip() for line in raw_status.split("\n") if line.strip()]

            # Check remote URL
            remote_res = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=str(self.repo_dir),
                capture_output=True,
                text=True,
                check=False
            )
            remote_url = remote_res.stdout.strip()

            # Check latest commit
            log_res = subprocess.run(
                ["git", "log", "-1", "--format=%h - %s (%cr)"],
                cwd=str(self.repo_dir),
                capture_output=True,
                text=True,
                check=False
            )
            last_commit = log_res.stdout.strip()

            return {
                "branch": current_branch,
                "remote_url": remote_url,
                "clean": len(changed_files) == 0,
                "uncommitted_count": len(changed_files),
                "uncommitted_files": changed_files[:20],
                "last_commit": last_commit,
                "last_sync_time": self.last_sync_time,
                "auto_sync_active": self._watcher_thread is not None and self._watcher_thread.is_alive()
            }
        except Exception as e:
            logger.error(f"Error checking git status: {e}", exc_info=True)
            return {"error": str(e), "clean": False, "uncommitted_count": 0}

    def _get_github_token(self) -> Optional[str]:
        """Safely retrieves the GitHub token from Windows Credential Manager."""
        try:
            import ctypes
            from ctypes import wintypes
            CRED_TYPE_GENERIC = 1
            class CREDENTIAL(ctypes.Structure):
                _fields_ = [('Flags', wintypes.DWORD), ('Type', wintypes.DWORD), ('TargetName', wintypes.LPWSTR), ('Comment', wintypes.LPWSTR), ('LastWritten', wintypes.FILETIME), ('CredentialBlobSize', wintypes.DWORD), ('CredentialBlob', ctypes.POINTER(ctypes.c_byte)), ('Persist', wintypes.DWORD), ('AttributeCount', wintypes.DWORD), ('Attributes', ctypes.c_void_p), ('TargetAlias', wintypes.LPWSTR), ('UserName', wintypes.LPWSTR)]
            PCREDENTIAL = ctypes.POINTER(CREDENTIAL)
            advapi32 = ctypes.WinDLL('advapi32.dll', use_last_error=True)
            CredReadW = advapi32.CredReadW
            CredReadW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(PCREDENTIAL)]
            CredReadW.restype = wintypes.BOOL
            CredFree = advapi32.CredFree
            CredFree.argtypes = [ctypes.c_void_p]

            pcred = PCREDENTIAL()
            if CredReadW('GitHub - https://api.github.com/santigamerxdyt', CRED_TYPE_GENERIC, 0, ctypes.byref(pcred)):
                cred = pcred.contents
                raw = bytes(ctypes.string_at(cred.CredentialBlob, cred.CredentialBlobSize))
                token = raw.decode('utf-8', errors='ignore').strip('\x00\r\n ')
                CredFree(pcred)
                return token
        except Exception as e:
            logger.debug(f"Could not read credential via CredReadW: {e}")
        return os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")

    def sync_to_github(self, custom_message: Optional[str] = None) -> Dict[str, Any]:
        """
        Stages all allowed changes, commits, and pushes to GitHub.
        Thread-safe to prevent concurrent git lock collisions.
        """
        with self._sync_lock:
            status = self.get_status()
            if status.get("clean"):
                return {
                    "success": True,
                    "action": "none_needed",
                    "message": "El repositorio ya se encuentra 100% al día con GitHub. No hay cambios pendientes por subir.",
                    "branch": status.get("branch", "main"),
                    "last_commit": status.get("last_commit")
                }

            try:
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                commit_msg = custom_message or f"sync: Actualización automática del proyecto [{now_str}]"

                # 1. Stage all changes (strictly honoring .gitignore)
                add_res = subprocess.run(
                    ["git", "add", "-A"],
                    cwd=str(self.repo_dir),
                    capture_output=True,
                    text=True,
                    check=False
                )
                if add_res.returncode != 0:
                    return {"success": False, "error": f"Error en git add: {add_res.stderr.strip()}"}

                # 2. Commit
                commit_res = subprocess.run(
                    ["git", "commit", "-m", commit_msg],
                    cwd=str(self.repo_dir),
                    capture_output=True,
                    text=True,
                    check=False
                )
                if commit_res.returncode != 0 and "nothing to commit" not in commit_res.stdout.lower():
                    return {"success": False, "error": f"Error en git commit: {commit_res.stderr.strip()}"}

                # 3. Push to origin main (using token if available for zero-prompt background pushes)
                branch = status.get("branch", "main")
                token = self._get_github_token()
                push_target = f"https://{token}@github.com/santigamerxdyt/Liseth-AI.git" if token else "origin"

                push_res = subprocess.run(
                    ["git", "push", push_target, f"{branch}:{branch}"],
                    cwd=str(self.repo_dir),
                    capture_output=True,
                    text=True,
                    check=False
                )

                if push_res.returncode != 0:
                    # Retry with plain origin if token failed
                    push_res = subprocess.run(
                        ["git", "push", "origin", branch],
                        cwd=str(self.repo_dir),
                        capture_output=True,
                        text=True,
                        check=False
                    )

                if push_res.returncode != 0:
                    return {
                        "success": False,
                        "error": f"Error al subir a GitHub: {push_res.stderr.strip()}",
                        "details": push_res.stderr
                    }

                # 4. Update telemetry
                self.last_sync_time = now_str
                log_res = subprocess.run(
                    ["git", "log", "-1", "--format=%h"],
                    cwd=str(self.repo_dir),
                    capture_output=True,
                    text=True,
                    check=False
                )
                self.last_commit_hash = log_res.stdout.strip()

                return {
                    "success": True,
                    "action": "synced",
                    "files_changed": status.get("uncommitted_count", 0),
                    "commit_hash": self.last_commit_hash,
                    "commit_message": commit_msg,
                    "timestamp": now_str,
                    "remote_url": "https://github.com/santigamerxdyt/Liseth-AI",
                    "message": f"Se sincronizaron y subieron {status.get('uncommitted_count', 0)} archivos modificados a GitHub con éxito."
                }

            except Exception as e:
                logger.error(f"Error during git sync: {e}", exc_info=True)
                return {"success": False, "error": str(e)}

    def start_background_watcher(self, interval_seconds: int = 300):
        """Starts an automatic background watcher that syncs every N seconds if changes exist."""
        if self._watcher_thread is not None and self._watcher_thread.is_alive():
            logger.info("El sincronizador automático de GitHub ya está en ejecución.")
            return

        self.auto_sync_interval_seconds = interval_seconds
        self._stop_watcher_event.clear()

        def _watcher_loop():
            logger.info(f"Iniciando centinela de sincronización Git cada {interval_seconds}s...")
            while not self._stop_watcher_event.is_set():
                time.sleep(self.auto_sync_interval_seconds)
                if self._stop_watcher_event.is_set():
                    break
                try:
                    st = self.get_status()
                    if not st.get("clean"):
                        logger.info("Cambios detectados en el proyecto. Sincronizando con GitHub en segundo plano...")
                        res = self.sync_to_github()
                        if res.get("success"):
                            logger.info(f"Sincronización automática completada: {res.get('commit_hash')}")
                        else:
                            logger.warning(f"Sincronización automática falló: {res.get('error')}")
                except Exception as e:
                    logger.error(f"Error en bucle de sincronización automática: {e}")

        self._watcher_thread = threading.Thread(target=_watcher_loop, daemon=True, name="LisethGitSyncWatcher")
        self._watcher_thread.start()

    def stop_background_watcher(self):
        """Stops the background auto-sync thread."""
        self._stop_watcher_event.set()
        if self._watcher_thread:
            self._watcher_thread.join(timeout=2.0)
            self._watcher_thread = None

    def format_report(self, sync_res: Dict[str, Any]) -> str:
        """Formats the sync result as an executive message for Señor Santiago."""
        if not sync_res.get("success"):
            return f"Señor Santiago, no se pudo completar la sincronización con GitHub: {sync_res.get('error')}"

        if sync_res.get("action") == "none_needed":
            return (
                "Señor Santiago, su repositorio en GitHub ya se encuentra completamente actualizado.\n"
                f"• Rama activa: `{sync_res.get('branch', 'main')}`\n"
                f"• Último commit: {sync_res.get('last_commit', 'Al día')}\n"
                "• Repositorio: https://github.com/santigamerxdyt/Liseth-AI"
            )

        return (
            "✅ **Sincronización con GitHub completada con éxito**, Señor Santiago:\n"
            f"• **Archivos actualizados:** {sync_res.get('files_changed', 0)}\n"
            f"• **Commit ID:** `{sync_res.get('commit_hash', 'N/A')}`\n"
            f"• **Mensaje:** {sync_res.get('commit_message')}\n"
            f"• **Hora:** {sync_res.get('timestamp')}\n"
            f"• **Repositorio Público:** https://github.com/santigamerxdyt/Liseth-AI\n"
            f"• **Enlace Web (GitHub Pages):** https://santigamerxdyt.github.io/Liseth-AI/"
        )


git_sync_service = GitSyncService()
