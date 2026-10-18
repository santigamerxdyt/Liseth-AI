"""
Deep Work & Pomodoro Manager for Liseth.
Provides autonomous focus session tracking, automatic DND synchronization,
and completion alerts with zero CPU overhead.
"""
from __future__ import annotations
import time
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("Liseth.DeepWork")


class DeepWorkManager:
    _instance: Optional[DeepWorkManager] = None

    def __new__(cls) -> DeepWorkManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_state()
        return cls._instance

    def _init_state(self):
        self.is_active: bool = False
        self.start_time: float = 0.0
        self.duration_minutes: int = 50
        self.target_end_time: float = 0.0
        self.task: str = ""
        self.notified_completion: bool = False

    def start_session(self, duration_minutes: int = 50, task: str = "") -> Dict[str, Any]:
        """Starts a deep work focus session and auto-enables DND."""
        now = time.time()
        self.is_active = True
        self.start_time = now
        self.duration_minutes = max(1, int(duration_minutes))
        self.target_end_time = now + (self.duration_minutes * 60)
        self.task = task.strip() if task else ""
        self.notified_completion = False

        # Synchronize with Gatekeeper DND
        try:
            from app.services.heartbeat_service import heartbeat_service
            heartbeat_service.gatekeeper.enable_dnd()
        except Exception as e:
            logger.debug(f"[DEEP_WORK] Could not set DND on gatekeeper: {e}")

        task_desc = f" en '{self.task}'" if self.task else ""
        msg = (
            f"Modo Trabajo Profundo activado por {self.duration_minutes} minutos{task_desc}. "
            "He silenciado todas las interrupciones para que pueda concentrarse plenamente, señor Santiago."
        )
        return {
            "status": "started",
            "duration_minutes": self.duration_minutes,
            "task": self.task,
            "message": msg
        }

    def stop_session(self) -> Dict[str, Any]:
        """Cancels or stops the active deep work session and restores voice alerts."""
        was_active = self.is_active
        self.is_active = False
        self.notified_completion = True

        try:
            from app.services.heartbeat_service import heartbeat_service
            heartbeat_service.gatekeeper.disable_dnd()
        except Exception as e:
            logger.debug(f"[DEEP_WORK] Could not clear DND on gatekeeper: {e}")

        if was_active:
            msg = "Modo Trabajo Profundo finalizado. Notificaciones y voz reactivadas, señor Santiago."
        else:
            msg = "No había ninguna sesión de trabajo profundo activa."

        return {
            "status": "stopped",
            "message": msg
        }

    def get_status(self) -> Dict[str, Any]:
        """Returns the current state and remaining minutes/seconds of the session."""
        if not self.is_active:
            return {
                "is_active": False,
                "message": "No hay ninguna sesión de trabajo profundo activa en este momento."
            }

        now = time.time()
        remaining_secs = max(0, int(self.target_end_time - now))
        remaining_mins = remaining_secs // 60
        rem_seconds = remaining_secs % 60
        elapsed_mins = int((now - self.start_time) // 60)

        task_desc = f" Enfocado en: '{self.task}'." if self.task else ""
        msg = (
            f"Sesión de Trabajo Profundo activa.{task_desc} "
            f"Tiempo restante: {remaining_mins} min {rem_seconds} seg "
            f"(de {self.duration_minutes} min)."
        )

        return {
            "is_active": True,
            "duration_minutes": self.duration_minutes,
            "elapsed_minutes": elapsed_mins,
            "remaining_seconds": remaining_secs,
            "remaining_minutes": remaining_mins,
            "task": self.task,
            "message": msg
        }

    def check_completion(self) -> Optional[str]:
        """
        Called by HeartbeatService patrol loop.
        If target end time reached, disables DND and returns sweet alert text.
        """
        if not self.is_active or self.notified_completion:
            return None

        now = time.time()
        if now >= self.target_end_time:
            self.is_active = False
            self.notified_completion = True

            try:
                from app.services.heartbeat_service import heartbeat_service
                heartbeat_service.gatekeeper.disable_dnd()
            except Exception:
                pass

            task_info = f" en '{self.task}'" if self.task else ""
            return (
                f"Señor Santiago, ha concluido exitosamente su sesión de trabajo profundo de "
                f"{self.duration_minutes} minutos{task_info}. Excelente avance. "
                "Le recomiendo tomar un descanso de 5 a 10 minutos para descansar la vista y recargar energía."
            )

        return None


deep_work_manager = DeepWorkManager()


def deep_work_action(parameters: dict = None) -> str:
    """Action controller entry point for deep work / pomodoro."""
    params = parameters or {}
    action = params.get("action", "start").lower()

    if action in ["start", "iniciar", "comenzar", "activar"]:
        duration = params.get("duration") or params.get("duration_minutes") or 50
        task = params.get("task", "")
        res = deep_work_manager.start_session(duration_minutes=duration, task=task)
        return res["message"]

    elif action in ["stop", "cancel", "terminar", "detener", "cancelar", "desactivar"]:
        res = deep_work_manager.stop_session()
        return res["message"]

    elif action in ["status", "estado", "tiempo", "consultar"]:
        res = deep_work_manager.get_status()
        return res["message"]

    return deep_work_manager.get_status()["message"]
