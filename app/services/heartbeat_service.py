"""
HeartbeatService — Autonomous Background Intelligence & Context Sentinel.
Enables Liseth to be partially autonomous without being intrusive:
- Periodic non-blocking background sensor loop (every 30-60s)
- Context Gatekeeper: Respects quiet hours, full-screen/gaming, cooldowns
- Hardware Sentinel: Monitors CPU, RAM, Disk, and GPU; alerts on runaway processes
- Daily Briefing: Delivers morning summary (weather, agenda, priorities)
- Topic Monitor: Watches headlines on user-monitored topics
- Commitment Watcher: Reminds user of scheduled tasks and promises
- Multi-channel delivery: Voice (when opportune), Console HUD, and Telegram
"""
import asyncio
import json
import logging
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx
import psutil

from app.config import settings

logger = logging.getLogger("jarvis.heartbeat")


class Gatekeeper:
    """
    Decides IF, WHEN, and HOW Liseth should communicate proactively.
    Prevents alert fatigue, interruptions during full-screen games/movies, and night disturbance.
    """
    def __init__(
        self,
        voice_cooldown_secs: int = 1800,   # Minimum 30 mins between spontaneous voice speeches
        console_cooldown_secs: int = 300,  # Minimum 5 mins between HUD console notices
        quiet_hours_start: int = 23,       # 11:00 PM
        quiet_hours_end: int = 7,          # 07:00 AM
    ):
        self.voice_cooldown_secs = voice_cooldown_secs
        self.console_cooldown_secs = console_cooldown_secs
        self.quiet_hours_start = quiet_hours_start
        self.quiet_hours_end = quiet_hours_end

        self.last_voice_alert_time: float = 0.0
        self.last_console_alert_time: float = 0.0
        self.last_user_activity_time: float = time.time()
        self.dnd_mode: bool = False

    def enable_dnd(self):
        """Activates Do Not Disturb (DND) / Modo No Molestar."""
        self.dnd_mode = True
        logger.info("[Gatekeeper] Modo No Molestar activado.")

    def disable_dnd(self):
        """Deactivates Do Not Disturb (DND)."""
        self.dnd_mode = False
        logger.info("[Gatekeeper] Modo No Molestar desactivado.")

    def toggle_dnd(self) -> bool:
        """Toggles Do Not Disturb and returns new state."""
        self.dnd_mode = not self.dnd_mode
        logger.info(f"[Gatekeeper] Modo No Molestar alternado a: {self.dnd_mode}")
        return self.dnd_mode

    def update_user_activity(self):
        """Called whenever the user types, clicks, or speaks."""
        self.last_user_activity_time = time.time()

    def is_quiet_hours(self) -> bool:
        """Returns True if current time is within late night quiet hours."""
        hour = datetime.now().hour
        if self.quiet_hours_start > self.quiet_hours_end:
            # e.g., 23:00 to 07:00
            return hour >= self.quiet_hours_start or hour < self.quiet_hours_end
        return self.quiet_hours_start <= hour < self.quiet_hours_end

    def is_fullscreen_or_busy(self) -> bool:
        """
        Detects if user is running a full-screen application (game, movie, presentation).
        Safe on Windows; returns False on errors.
        """
        try:
            if os.name != "nt":
                return False
            import ctypes
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return False

            # Get screen resolution and active window rect
            screen_w = user32.GetSystemMetrics(0)
            screen_h = user32.GetSystemMetrics(1)

            class RECT(ctypes.Structure):
                _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                            ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

            rect = RECT()
            if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                win_w = rect.right - rect.left
                win_h = rect.bottom - rect.top
                # If window covers entire primary display
                if win_w >= screen_w and win_h >= screen_h:
                    return True
        except Exception:
            pass
        return False

    def is_in_call_or_meeting(self) -> bool:
        """
        Detects if user is currently in an active voice call, meeting, or video conference
        (Zoom, Teams, Discord, Google Meet, Skype, Slack, Webex).
        """
        try:
            if os.name != "nt":
                return False
            import ctypes
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return False

            length = user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value.lower()

            call_keywords = ["reunión", "reunion", "meeting", "google meet", "zoom meeting", "llamada", "discord"]
            if any(k in title for k in call_keywords):
                return True

            pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value:
                p = psutil.Process(pid.value)
                pname = p.name().lower()
                if pname in ["zoom.exe", "teams.exe", "discord.exe", "slack.exe", "skype.exe", "webex.exe"]:
                    return True
        except Exception:
            pass
        return False

    def can_speak(self, priority: str = "normal") -> bool:
        """
        Evaluates whether voice speech is allowed at this moment.
        High/urgent priority can bypass cooldowns, but never quiet hours, DND, or active speech.
        """
        # Never speak if Do Not Disturb (DND) is active unless critical emergency
        if self.dnd_mode and priority != "critical":
            return False

        # Never speak if quiet hours unless critical emergency
        if self.is_quiet_hours() and priority != "critical":
            return False

        # Never speak if user is in a call / meeting unless critical
        if self.is_in_call_or_meeting() and priority != "critical":
            return False

        # Never speak if user is in full screen (game/movie) unless critical
        if self.is_fullscreen_or_busy() and priority != "critical":
            return False

        # Never speak if Liseth is already speaking or currently listening
        try:
            from app.services.voice_engine import voice_engine
            if voice_engine.is_speaking or voice_engine.is_thinking:
                return False
        except Exception:
            pass

        now = time.time()
        if priority in ["high", "critical"]:
            return True

        return (now - self.last_voice_alert_time) >= self.voice_cooldown_secs

    def can_notify_console(self, priority: str = "normal") -> bool:
        """Evaluates whether posting an alert card to HUD console is allowed."""
        now = time.time()
        if priority in ["high", "critical"]:
            return True
        return (now - self.last_console_alert_time) >= self.console_cooldown_secs


class HeartbeatService:
    def __init__(self):
        self.is_running: bool = False
        self._thread: Optional[threading.Thread] = None
        self._loop_event = threading.Event()
        self.gatekeeper = Gatekeeper()

        self.check_interval_seconds: int = 30
        self.last_hardware_check: float = 0.0
        self.last_briefing_date: str = ""
        self.last_topics_check: float = 0.0

        # Health sentinel tracking
        self._high_ram_streak: int = 0
        self._high_cpu_streak: int = 0
        self._last_notified_hardware: float = 0.0

    def start(self):
        """Starts the autonomous background thread."""
        if self.is_running:
            return
        self.is_running = True
        self._loop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="HeartbeatDaemon")
        self._thread.start()
        logger.info("[Heartbeat] Centinela autónomo iniciado correctamente.")

    def stop(self):
        """Stops the autonomous background thread."""
        self.is_running = False
        self._loop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        logger.info("[Heartbeat] Centinela autónomo detenido.")

    def get_status(self) -> Dict[str, Any]:
        """Returns current state and sensor loop health."""
        return {
            "active": self.is_running,
            "interval_seconds": self.check_interval_seconds,
            "dnd_mode": self.gatekeeper.dnd_mode if self.gatekeeper else False,
            "last_hardware_check": self.last_hardware_check
        }

    def _run_loop(self):
        """Background sensor check loop executing every check_interval_seconds."""
        logger.info(f"[Heartbeat] Bucle activo con intervalo de {self.check_interval_seconds}s.")
        while self.is_running:
            try:
                # 1. Run Hardware Sentinel (every ~60s)
                now = time.time()
                if now - self.last_hardware_check >= 60.0:
                    self.last_hardware_check = now
                    self._check_hardware_sentinel()

                # 2. Run Daily Morning Briefing check (once per day, around 8am or first check)
                self._check_daily_briefing()

                # 3. Run Monitored Topics check (every ~4 hours)
                if now - self.last_topics_check >= 14400.0:
                    self.last_topics_check = now
                    self._check_topic_monitors()

                # 4. Run Calendar Meetings check (10-15m advance warning)
                self._check_calendar_events()

                # 5. Run Commitments & Follow-ups check
                self._check_commitments()

                # 6. Run Scheduled Tasks check
                self._check_scheduled_tasks()

                # 7. Run Deep Work / Pomodoro completion check
                self._check_deep_work_session()

                # 8. Run Workspace Sentinel code health check
                self._check_workspace_sentinel()

            except Exception as e:
                logger.error(f"[Heartbeat] Error en ciclo autónomo: {e}", exc_info=True)

            # Wait for next cycle or shutdown signal
            self._loop_event.wait(timeout=self.check_interval_seconds)

    # ── Sensor 1: Hardware Sentinel ───────────────────────────────────────────

    def _check_hardware_sentinel(self):
        """Monitors system resources and detects runaway processes."""
        try:
            ram = psutil.virtual_memory().percent
            cpu = psutil.cpu_percent(interval=None)

            # Primary disk
            drive = os.path.splitdrive(os.getcwd())[0] or "/"
            disk_free_gb = 0
            if hasattr(psutil, "disk_usage"):
                disk_free_gb = psutil.disk_usage(drive).free / (1024 ** 3)

            # Streak counters
            if ram >= 90.0:
                self._high_ram_streak += 1
            else:
                self._high_ram_streak = 0

            if cpu >= 92.0:
                self._high_cpu_streak += 1
            else:
                self._high_cpu_streak = 0

            now = time.time()
            # Cooldown of 20 mins between hardware alerts unless emergency
            if (now - self._last_notified_hardware) < 1200.0:
                return

            alert_msg = None
            priority = "normal"

            if self._high_ram_streak >= 2:
                # Find the culprit process
                top_proc = self._get_top_resource_process("memory")
                alert_msg = (
                    f"Santiago, la memoria RAM de su equipo se encuentra al {ram:.0f}%. "
                    f"El proceso principal en consumo es '{top_proc}'. ¿Desea que lo libere?"
                )
                priority = "high"

            elif self._high_cpu_streak >= 3:
                top_proc = self._get_top_resource_process("cpu")
                alert_msg = (
                    f"Santiago, el procesador está trabajando intensamente al {cpu:.0f}%. "
                    f"El proceso '{top_proc}' está demandando la mayor carga."
                )
                priority = "normal"

            elif disk_free_gb > 0 and disk_free_gb < 10.0:
                alert_msg = (
                    f"Aviso de almacenamiento: El disco principal ({drive}) tiene menos de {disk_free_gb:.1f} GB libres. "
                    "Podemos organizar o limpiar temporales si lo desea."
                )
                priority = "high"

            if alert_msg:
                self._last_notified_hardware = now
                self.dispatch_proactive_alert(
                    title="Centinela de Recursos",
                    message=alert_msg,
                    priority=priority,
                    allow_voice=True,
                )

        except Exception as e:
            logger.debug(f"[Heartbeat] Error en verificación de hardware: {e}")

    def _get_top_resource_process(self, resource_type: str = "memory") -> str:
        """Finds the name of the process consuming the most memory or CPU."""
        try:
            procs = []
            for p in psutil.process_iter(['name', 'memory_percent', 'cpu_percent']):
                try:
                    info = p.info
                    procs.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if resource_type == "memory":
                top = max(procs, key=lambda x: x.get('memory_percent') or 0.0, default=None)
                if top:
                    return f"{top['name']} ({top.get('memory_percent', 0):.1f}% RAM)"
            else:
                top = max(procs, key=lambda x: x.get('cpu_percent') or 0.0, default=None)
                if top:
                    return f"{top['name']} ({top.get('cpu_percent', 0):.1f}% CPU)"
        except Exception:
            pass
        return "Desconocido"

    # ── Sensor 2: Daily Morning Briefing ──────────────────────────────────────

    def _check_daily_briefing(self):
        """Delivers a proactive morning summary once per day between 08:00 and 11:30 AM."""
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")

        if self.last_briefing_date == today_str:
            return  # Already delivered today

        # Between 8:00 AM and 11:30 AM
        if 8 <= now.hour < 12:
            self.last_briefing_date = today_str
            threading.Thread(target=self._synthesize_and_send_briefing, daemon=True).start()

    def _synthesize_and_send_briefing(self):
        """Compiles agenda, tasks, real weather, and memories, and sends morning greeting."""
        try:
            from app.services.soul_service import soul_service
            from app.actions.weather_report import fetch_weather_report
            from app.services.calendar_service import calendar_service
            from app.services.commitment_service import commitment_service

            # Gather weather
            weather_data = fetch_weather_report("Bogotá")
            weather_summary = weather_data.get("summary", "El clima en Bogotá se encuentra templado.")

            # Gather calendar agenda
            agenda_summary = calendar_service.format_daily_agenda()

            # Gather commitments/tasks
            comm_summary = commitment_service.format_commitments_summary()

            # Compose briefing
            briefing_parts = [
                "Buenos días, señor Santiago. Le deseo un excelente y productivo día.",
                weather_summary,
                agenda_summary,
                comm_summary,
                "Sus sistemas están en óptimas condiciones, el centinela de hardware se encuentra activo y quedo a su entera disposición."
            ]
            briefing_text = " ".join([p for p in briefing_parts if p])

            self.dispatch_proactive_alert(
                title="Resumen Matutino",
                message=briefing_text,
                priority="normal",
                allow_voice=True,
            )
            logger.info("[Heartbeat] Resumen matutino generado y despachado.")

        except Exception as e:
            logger.warning(f"[Heartbeat] Error en generación de resumen matutino: {e}")

    # ── Sensor 3: Topic Monitors ──────────────────────────────────────────────

    def _check_topic_monitors(self):
        """Checks news headlines on user monitored topics."""
        try:
            from app.actions.background_monitor import check_all
            alerts = check_all()
            if alerts:
                for a in alerts[:2]:
                    self.dispatch_proactive_alert(
                        title="Noticias Monitoreadas",
                        message=a,
                        priority="normal",
                        allow_voice=False,  # News alerts are silent in console by default
                    )
        except Exception as e:
            logger.debug(f"[Heartbeat] Error revisando temas en segundo plano: {e}")

    # ── Sensor 4: Calendar Meetings & Events ──────────────────────────────────

    def _check_calendar_events(self):
        """Checks upcoming calendar meetings and notifies 10-15 minutes in advance."""
        try:
            from app.services.calendar_service import calendar_service
            upcoming = calendar_service.check_upcoming_events(lead_minutes=15)
            for evt in upcoming:
                calendar_service.mark_alerted(evt["id"])
                link = evt.get("meeting_link")
                link_text = f" Enlace para unirse: {link}" if link else ""
                summary = evt.get("summary", "Reunión programada")
                st = evt.get("start_time", "")
                time_str = st.split("T")[1][:5] if "T" in st else st[-5:]

                msg = (
                    f"Santiago, en aproximadamente 10 minutos inicia su evento: '{summary}' "
                    f"a las {time_str}.{link_text}"
                )
                self.dispatch_proactive_alert(
                    title="Aviso de Reunión",
                    message=msg,
                    priority="high",
                    allow_voice=True,
                )
        except Exception as e:
            logger.debug(f"[Heartbeat] Error en verificación de calendario: {e}")

    # ── Sensor 5: Commitments and Follow-ups ───────────────────────────────────

    def _check_commitments(self):
        """Checks pending commitments and proactivally alerts if due soon."""
        try:
            from app.services.commitment_service import commitment_service
            due_items = commitment_service.check_due_commitments(lead_minutes=25)
            for item in due_items:
                commitment_service.mark_reminded(item["id"])
                prio = "high" if item.get("priority") == "high" else "normal"
                msg = (
                    f"Santiago, recuerdo que tiene pendiente: '{item['text']}' "
                    f"programado para las {item.get('due_time', 'hoy')}. ¿Desea que prepare algo?"
                )
                self.dispatch_proactive_alert(
                    title="Recordatorio de Compromiso",
                    message=msg,
                    priority=prio,
                    allow_voice=True,
                )
        except Exception as e:
            logger.debug(f"[Heartbeat] Error en verificación de compromisos: {e}")

    # ── Sensor 6: Scheduled Tasks ─────────────────────────────────────────────

    def _check_scheduled_tasks(self):
        """Checks data/scheduled_tasks.json for tasks due to run."""
        try:
            tasks_file = settings.DATA_DIR / "scheduled_tasks.json"
            if not tasks_file.exists():
                return
            tasks = json.loads(tasks_file.read_text(encoding="utf-8"))
            if not isinstance(tasks, list):
                return

            now = datetime.now()
            updated = False
            for t in tasks:
                if not t.get("enabled", True):
                    continue

                # Check if task is due (e.g. interval or timeOfDay)
                time_of_day = t.get("timeOfDay")
                if time_of_day:
                    hh, mm = map(int, time_of_day.split(":"))
                    if now.hour == hh and now.minute == mm:
                        # Avoid firing multiple times in same minute
                        last_run = t.get("lastRun", "")
                        today_prefix = now.strftime("%Y-%m-%d")
                        if not last_run or not last_run.startswith(today_prefix):
                            self.execute_scheduled_task(t)
                            t["lastRun"] = now.isoformat()
                            updated = True

            if updated:
                tasks_file.write_text(json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logger.debug(f"[Heartbeat] Error en tareas programadas: {e}")

    def execute_scheduled_task(self, task: Dict[str, Any]) -> str:
        """Executes a scheduled task immediately."""
        task_type = task.get("type")
        task_title = task.get("title", "Tarea programada")
        logger.info(f"[Heartbeat] Ejecutando tarea programada: {task_title} ({task_type})")

        if task_type in ["daily_summary", "morning_briefing"]:
            threading.Thread(target=self._synthesize_and_send_briefing, daemon=True).start()
            return "Resumen matutino iniciado."

        elif task_type in ["process_report", "hardware_report"]:
            self._check_hardware_sentinel()
            return "Verificación de hardware ejecutada."

        elif task_type in ["event_check", "commitments_check", "calendar_check"]:
            self._check_calendar_events()
            self._check_commitments()
            return "Verificación de calendario y compromisos ejecutada."

        elif task_type in ["weekly_summary"]:
            from app.services.commitment_service import commitment_service
            summary = commitment_service.format_commitments_summary()
            self.dispatch_proactive_alert(
                title="Resumen Semanal",
                message=f"Santiago, este es su resumen de inicio de semana: {summary}",
                priority="normal",
                allow_voice=True,
            )
            return "Resumen semanal ejecutado."

        return f"Tarea '{task_title}' procesada."

    def _check_deep_work_session(self):
        """Checks if active deep work session has ended, restores sound and announces completion."""
        try:
            from app.actions.deep_work import deep_work_manager
            alert = deep_work_manager.check_completion()
            if alert:
                self.dispatch_proactive_alert(
                    title="Sesión de Trabajo Profundo Completada",
                    message=alert,
                    priority="high",
                    allow_voice=True,
                )
        except Exception as e:
            logger.debug(f"[Heartbeat] Error en verificación de trabajo profundo: {e}")

    def _check_workspace_sentinel(self):
        """Silently scans watched workspaces; alerts user ONLY if syntax/compilation issues exist."""
        try:
            from app.services.workspace_sentinel import workspace_sentinel
            rep = workspace_sentinel.scan_workspace()
            if not rep.healthy and rep.issues:
                alert = rep.format_alert()
                if alert:
                    self.dispatch_proactive_alert(
                        title="Centinela de Código",
                        message=alert,
                        priority="normal",
                        allow_voice=False,
                    )
        except Exception as e:
            logger.debug(f"[Heartbeat] Error en centinela de espacio de trabajo: {e}")

    # ── Event Dispatcher ──────────────────────────────────────────────────────

    def dispatch_proactive_alert(
        self,
        title: str,
        message: str,
        priority: str = "normal",
        allow_voice: bool = True,
    ):
        """
        Dispatches an autonomous proactive alert across available channels:
        1. Emits real-time SSE event to Web & Desktop HUD
        2. Persists turn to SQLite database for Console visibility
        3. Speaks aloud if Gatekeeper allows voice
        4. Sends Telegram message if configured
        """
        logger.info(f"[PROACTIVE_ALERT] [{priority.upper()}] {title}: {message}")

        # 1. Broadcast SSE event to HUD
        try:
            from app.services.voice_engine import voice_engine
            voice_engine.broadcast_event("proactive_alert", {
                "title": title,
                "text": message,
                "priority": priority,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        except Exception as e:
            logger.debug(f"[Heartbeat] Error emitiendo evento SSE: {e}")

        # 2. Persist turn to SQLite database for the Console History
        try:
            def _save():
                from app.core.database import AsyncSessionLocal
                from app.core.models import ChatMessage

                async def _do():
                    async with AsyncSessionLocal() as session:
                        session.add(
                            ChatMessage(
                                session_id="default",
                                role="model",
                                parts=[{"text": f"💡 **[{title}]** {message}"}],
                            )
                        )
                        await session.commit()

                asyncio.run(_do())

            threading.Thread(target=_save, daemon=True).start()
            self.gatekeeper.last_console_alert_time = time.time()
        except Exception as e:
            logger.debug(f"[Heartbeat] Error persistiendo alerta en BD: {e}")

        # 3. Voice audio speech if allowed by Gatekeeper
        if allow_voice and self.gatekeeper.can_speak(priority):
            try:
                from app.services.voice_engine import voice_engine
                voice_engine.speak(message)
                self.gatekeeper.last_voice_alert_time = time.time()
            except Exception as e:
                logger.debug(f"[Heartbeat] Error hablando alerta proactiva: {e}")

        # 4. Telegram alert if configured
        if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
            self._send_telegram_async(f"🔔 *{title}*\n\n{message}")

    def _send_telegram_async(self, text: str):
        """Sends message to Santiago's Telegram bot in a detached thread."""
        def _do():
            try:
                url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
                payload = {
                    "chat_id": settings.TELEGRAM_CHAT_ID,
                    "text": text,
                    "parse_mode": "Markdown",
                }
                with httpx.Client(timeout=10.0) as client:
                    client.post(url, json=payload)
            except Exception as e:
                logger.debug(f"[Heartbeat] Error enviando a Telegram: {e}")

        threading.Thread(target=_do, daemon=True).start()


# Global singleton instance
heartbeat_service = HeartbeatService()
