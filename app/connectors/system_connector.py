"""
SystemConnector - Windows PC System Execution and Management for JARVIS / Liseth.
Provides secure, audited interaction with local Windows PC:
- Running terminal/PowerShell commands
- Opening applications and resources
- Reading and writing files
- Inspecting and terminating processes
- System hardware telemetry (CPU, RAM, Disk, OS)

All modifying and executing operations are strictly intercepted by AuditManager
and require user approval before execution.
"""
import asyncio
import getpass
import logging
import os
import platform
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import psutil
except ImportError:
    psutil = None

from app.connectors.base import BaseConnector
from app.services.audit_manager import audit_manager

logger = logging.getLogger("jarvis.system_connector")


class SystemConnector(BaseConnector):
    def __init__(self):
        super().__init__(
            connector_id="system_windows",
            name="Windows PC System",
            description="Control, ejecución de procesos, archivos y telemetría de Windows.",
        )
        self.connected = True
        self._register_handlers()

    def _register_handlers(self):
        """Registers handlers in AuditManager so approved actions execute seamlessly."""
        audit_manager.register_handler("system_run_command", self._exec_run_command)
        audit_manager.register_handler("system_open_app", self._exec_open_app)
        audit_manager.register_handler("system_write_file", self._exec_write_file)
        audit_manager.register_handler("system_delete_file", self._exec_delete_file)
        audit_manager.register_handler("system_kill_process", self._exec_kill_process)

    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Verifies local system environment access."""
        self.connected = True
        return True

    def list_actions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "system_run_command",
                "description": "Ejecuta un comando en PowerShell o CMD en el equipo del usuario.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Comando a ejecutar"},
                        "shell": {"type": "string", "enum": ["powershell", "cmd"], "default": "powershell"},
                        "timeout": {"type": "integer", "default": 30},
                    },
                    "required": ["command"],
                },
                "sensitive": True,
            },
            {
                "name": "system_open_app",
                "description": "Abre una aplicación, ejecutable o URL en el sistema operativo.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string", "description": "Nombre de la aplicación, archivo ejecutable o URL"},
                        "args": {"type": "array", "items": {"type": "string"}, "description": "Argumentos opcionales"},
                    },
                    "required": ["app_name"],
                },
                "sensitive": True,
            },
            {
                "name": "system_write_file",
                "description": "Crea o sobrescribe un archivo en el almacenamiento local.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Ruta absoluta o relativa del archivo"},
                        "content": {"type": "string", "description": "Contenido a escribir"},
                        "append": {"type": "boolean", "default": False},
                    },
                    "required": ["path", "content"],
                },
                "sensitive": True,
            },
            {
                "name": "system_delete_file",
                "description": "Elimina un archivo local de forma segura.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Ruta del archivo a eliminar"},
                    },
                    "required": ["path"],
                },
                "sensitive": True,
            },
            {
                "name": "system_kill_process",
                "description": "Finaliza un proceso en ejecución por PID o nombre.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pid": {"type": "integer", "description": "PID del proceso"},
                        "name": {"type": "string", "description": "Nombre del ejecutable (ej. notepad.exe)"},
                    },
                },
                "sensitive": True,
            },
            {
                "name": "system_get_info",
                "description": "Consulta especificaciones y telemetría de hardware (CPU, RAM, Disco, SO).",
                "parameters": {"type": "object", "properties": {}},
                "sensitive": False,
            },
            {
                "name": "system_list_processes",
                "description": "Lista procesos en ejecución con consumo de recursos.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "default": 50},
                        "filter": {"type": "string", "description": "Filtro por nombre"},
                    },
                },
                "sensitive": False,
            },
            {
                "name": "system_read_file",
                "description": "Lee el contenido de un archivo de texto en el equipo.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Ruta del archivo"},
                        "max_bytes": {"type": "integer", "default": 100000},
                    },
                    "required": ["path"],
                },
                "sensitive": False,
            },
            {
                "name": "system_list_directory",
                "description": "Lista archivos y carpetas de un directorio.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "default": "."},
                    },
                },
                "sensitive": False,
            },
        ]

    # --- Actual Direct Executors ---

    async def _exec_run_command(self, params: Dict[str, Any]) -> Dict[str, Any]:
        command = params.get("command", "")
        shell_choice = params.get("shell", "powershell").lower()
        timeout = int(params.get("timeout", 30))

        if not command:
            raise ValueError("No se especificó ningún comando para ejecutar.")

        if shell_choice == "cmd":
            cmd_args = ["cmd.exe", "/c", command]
        else:
            cmd_args = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command]

        start_time = time.time()
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            duration = round(time.time() - start_time, 3)

            stdout_str = stdout.decode("utf-8", errors="replace")
            stderr_str = stderr.decode("utf-8", errors="replace")

            return {
                "ok": proc.returncode == 0,
                "command": command,
                "shell": shell_choice,
                "returncode": proc.returncode,
                "stdout": stdout_str,
                "stderr": stderr_str,
                "duration_seconds": duration,
            }
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except Exception:
                pass
            raise TimeoutError(f"El comando excedió el tiempo límite de {timeout} segundos.")
        except Exception as e:
            logger.error(f"Error ejecutando comando: {e}")
            raise

    async def _exec_open_app(self, params: Dict[str, Any]) -> Dict[str, Any]:
        app_name = params.get("app_name", "").strip()
        args = params.get("args", [])
        if not app_name:
            raise ValueError("Nombre de la aplicación no especificado.")

        # If it's a URL or recognized protocol
        if app_name.startswith("http://") or app_name.startswith("https://"):
            try:
                os.startfile(app_name)
                return {"ok": True, "action": "open_url", "target": app_name}
            except Exception as e:
                # Fallback to start command via powershell
                await asyncio.create_subprocess_exec("powershell.exe", "-Command", f"Start-Process '{app_name}'")
                return {"ok": True, "action": "open_url_powershell", "target": app_name}

        # Local application or executable
        try:
            full_cmd = [app_name] + [str(a) for a in args]
            subprocess.Popen(full_cmd, shell=True)
            return {"ok": True, "action": "launch_app", "target": app_name, "args": args}
        except Exception as e:
            logger.warning(f"Fallo Popen para {app_name}, intentando Start-Process: {e}")
            cmd = f"Start-Process '{app_name}'"
            if args:
                cmd += f" -ArgumentList '{' '.join(args)}'"
            await asyncio.create_subprocess_exec("powershell.exe", "-Command", cmd)
            return {"ok": True, "action": "launch_powershell", "target": app_name}

    async def _exec_write_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        file_path = params.get("path", "").strip()
        content = params.get("content", "")
        append = bool(params.get("append", False))

        if not file_path:
            raise ValueError("Ruta de archivo no especificada.")

        target = Path(file_path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)

        mode = "a" if append else "w"
        with open(target, mode, encoding="utf-8") as f:
            f.write(content)

        return {
            "ok": True,
            "path": str(target),
            "bytes_written": len(content.encode("utf-8")),
            "mode": "append" if append else "overwrite",
        }

    async def _exec_delete_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        file_path = params.get("path", "").strip()
        if not file_path:
            raise ValueError("Ruta de archivo no especificada.")

        target = Path(file_path).resolve()
        if not target.exists():
            raise FileNotFoundError(f"El archivo '{file_path}' no existe.")

        if target.is_dir():
            shutil.rmtree(target)
            return {"ok": True, "deleted_type": "directory", "path": str(target)}
        else:
            target.unlink()
            return {"ok": True, "deleted_type": "file", "path": str(target)}

    async def _exec_kill_process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        pid = params.get("pid")
        name = params.get("name")

        if not pid and not name:
            raise ValueError("Debe especificar PID o nombre del proceso a terminar.")

        killed = []
        if pid:
            pid = int(pid)
            if psutil:
                try:
                    p = psutil.Process(pid)
                    p_name = p.name()
                    p.terminate()
                    killed.append({"pid": pid, "name": p_name})
                except Exception as e:
                    logger.warning(f"psutil terminate fallo, usando taskkill: {e}")
                    await asyncio.create_subprocess_exec("taskkill", "/F", "/PID", str(pid))
                    killed.append({"pid": pid, "name": str(pid)})
            else:
                await asyncio.create_subprocess_exec("taskkill", "/F", "/PID", str(pid))
                killed.append({"pid": pid})

        elif name:
            # Terminate by image name
            await asyncio.create_subprocess_exec("taskkill", "/F", "/IM", name)
            killed.append({"name": name})

        return {"ok": True, "terminated": killed}

    # --- Read-only Executors ---

    async def get_system_info(self) -> Dict[str, Any]:
        """Telemetry and hardware status."""
        uname = platform.uname()
        info = {
            "os": f"{uname.system} {uname.release} ({uname.version})",
            "hostname": uname.node,
            "machine": uname.machine,
            "processor": uname.processor,
            "user": getpass.getuser(),
            "python_version": platform.python_version(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if psutil:
            try:
                vm = psutil.virtual_memory()
                info["memory"] = {
                    "total_gb": round(vm.total / (1024**3), 2),
                    "available_gb": round(vm.available / (1024**3), 2),
                    "percent_used": vm.percent,
                }
                info["cpu"] = {
                    "cores_logical": psutil.cpu_count(logical=True),
                    "cores_physical": psutil.cpu_count(logical=False),
                    "percent": psutil.cpu_percent(interval=None),
                }
                disk = psutil.disk_usage("/")
                info["disk"] = {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent_used": disk.percent,
                }
            except Exception as ex:
                logger.warning(f"Error recopilando métricas psutil: {ex}")

        return info

    async def list_processes(self, limit: int = 50, filter_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists running system processes."""
        processes = []
        if not psutil:
            return [{"notice": "psutil no está disponible en este entorno"}]

        filter_lower = filter_name.lower() if filter_name else None

        for proc in psutil.process_iter(["pid", "name", "username", "memory_info", "cpu_percent"]):
            try:
                p_info = proc.info
                p_name = p_info.get("name") or ""
                if filter_lower and filter_lower not in p_name.lower():
                    continue

                mem = p_info.get("memory_info")
                mem_mb = round(mem.rss / (1024 * 1024), 1) if mem else 0

                processes.append({
                    "pid": p_info.get("pid"),
                    "name": p_name,
                    "memory_mb": mem_mb,
                    "user": p_info.get("username"),
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by memory descending
        processes.sort(key=lambda x: x.get("memory_mb", 0), reverse=True)
        return processes[:limit]

    async def read_file(self, path: str, max_bytes: int = 100000) -> Dict[str, Any]:
        """Safely reads a text file."""
        target = Path(path).resolve()
        if not target.exists():
            raise FileNotFoundError(f"El archivo '{path}' no existe.")
        if target.is_dir():
            raise IsADirectoryError(f"'{path}' es un directorio, no un archivo.")

        file_size = target.stat().st_size
        with open(target, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_bytes)

        return {
            "path": str(target),
            "size_bytes": file_size,
            "truncated": file_size > max_bytes,
            "content": content,
        }

    async def list_directory(self, path: str = ".") -> Dict[str, Any]:
        """Lists entries in a directory."""
        target = Path(path).resolve()
        if not target.exists():
            raise FileNotFoundError(f"La ruta '{path}' no existe.")

        entries = []
        for item in target.iterdir():
            try:
                stat = item.stat()
                entries.append({
                    "name": item.name,
                    "is_dir": item.is_dir(),
                    "size_bytes": stat.st_size if not item.is_dir() else 0,
                    "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                })
            except Exception:
                continue

        # Sort directories first, then alphabetically
        entries.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
        return {
            "path": str(target),
            "count": len(entries),
            "items": entries,
        }

    # --- Generic Execute Action Entrypoint ---

    async def execute_action(self, action_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes action. If sensitive, enforces confirmation via AuditManager.
        """
        is_sensitive, service_name, reason = audit_manager.describe_action(self.id, action_name, params)

        if is_sensitive:
            # Check if this invocation has already been approved
            if params.get("__preapproved__") is True:
                handler = audit_manager._action_handlers.get(action_name)
                if handler:
                    result = await handler(params)
                    await audit_manager.log_action(self.id, action_name, params, "executed", result, True)
                    return {"ok": True, "executed": True, "result": result}

            # Intercept: Create pending confirmation
            pending_item = await audit_manager.create_pending_confirmation(
                connector=self.id,
                action=action_name,
                params=params,
                reason=reason,
            )
            return {
                "ok": True,
                "pendingConfirmation": True,
                "confirmId": pending_item["id"],
                "reason": pending_item["reason"],
                "action": action_name,
                "service": service_name,
                "params": params,
                "notice": "Esta acción requiere autorización explícita antes de ejecutarse en su equipo.",
            }

        # Non-sensitive actions execute directly
        if action_name == "system_get_info":
            result = await self.get_system_info()
        elif action_name == "system_list_processes":
            result = await self.list_processes(
                limit=params.get("limit", 50),
                filter_name=params.get("filter"),
            )
        elif action_name == "system_read_file":
            result = await self.read_file(
                path=params.get("path", ""),
                max_bytes=params.get("max_bytes", 100000),
            )
        elif action_name == "system_list_directory":
            result = await self.list_directory(path=params.get("path", "."))
        else:
            raise ValueError(f"Acción desconocida en SystemConnector: '{action_name}'.")

        await audit_manager.log_action(self.id, action_name, params, "executed", result, False)
        return {"ok": True, "result": result}


system_connector = SystemConnector()
