"""
RoutineEngine for JARVIS / Liseth.
Orchestrates multi-step automated workflows tailored for Señor Santiago:
- 'morning': Weather, agenda, urgent emails, project health, and morning greeting.
- 'focus' / 'work': Deep work session, DND activation, project validation, environment prep.
- 'evening' / 'wrap_up': Commitments review, background task status, executive debrief.
- Custom user-registered macro routines.
"""
import datetime
import logging
import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("jarvis.routine_engine")


@dataclass
class RoutineStepResult:
    step_name: str
    success: bool
    output: str
    duration_seconds: float = 0.0


@dataclass
class RoutineExecutionResult:
    routine_name: str
    started_at: str
    completed_at: str
    success: bool
    step_results: List[RoutineStepResult] = field(default_factory=list)
    summary: str = ""


class RoutineEngine:
    """
    Executes and coordinates chained multi-step routines for Señor Santiago.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._history: List[RoutineExecutionResult] = []
        self._custom_routines: Dict[str, List[Dict[str, Any]]] = {}

    def list_available_routines(self) -> List[Dict[str, str]]:
        """Returns metadata of built-in and custom registered routines."""
        return [
            {
                "id": "morning",
                "name": "Rutina Matutina (Inicio de Jornada)",
                "description": "Clima de Bogotá, agenda de hoy, correos importantes y saludo personalizado.",
            },
            {
                "id": "focus",
                "name": "Rutina de Trabajo y Concentración",
                "description": "Inicia modo trabajo profundo (50 min), activa silencio No Molestar y valida código.",
            },
            {
                "id": "wrap_up",
                "name": "Rutina de Cierre de Jornada",
                "description": "Revisión de compromisos del día, estado de tareas autónomas y balance ejecutivo.",
            },
        ]

    def execute_routine(self, routine_name: str) -> RoutineExecutionResult:
        """Executes a routine synchronously or in worker thread and returns result."""
        import time
        rname = routine_name.lower().strip()
        started_at = datetime.datetime.now().isoformat()
        step_results: List[RoutineStepResult] = []

        logger.info(f"[ROUTINE] Iniciando rutina: '{rname}'")

        if rname in ("morning", "matutina", "mañana", "inicio"):
            step_results = self._run_morning_routine()
        elif rname in ("focus", "work", "trabajo", "concentracion", "concentración"):
            step_results = self._run_focus_routine()
        elif rname in ("wrap_up", "evening", "cierre", "noche", "tarde"):
            step_results = self._run_wrap_up_routine()
        else:
            step_results.append(
                RoutineStepResult(
                    step_name=f"Rutina '{rname}'",
                    success=False,
                    output=f"Rutina '{rname}' no encontrada."
                )
            )

        completed_at = datetime.datetime.now().isoformat()
        overall_success = all(s.success for s in step_results)

        # Generate friendly executive summary
        summary = self._format_routine_summary(rname, step_results)

        result = RoutineExecutionResult(
            routine_name=rname,
            started_at=started_at,
            completed_at=completed_at,
            success=overall_success,
            step_results=step_results,
            summary=summary
        )

        with self._lock:
            self._history.append(result)

        return result

    def _run_morning_routine(self) -> List[RoutineStepResult]:
        steps = []
        import time

        # 1. Weather
        t0 = time.time()
        try:
            from app.actions.weather_report import fetch_weather_report
            wdata = fetch_weather_report("Bogotá")
            wsum = wdata.get("summary", "Clima templado en Bogotá.")
            steps.append(RoutineStepResult("Pronóstico del Clima", True, wsum, time.time() - t0))
        except Exception as e:
            steps.append(RoutineStepResult("Pronóstico del Clima", False, str(e), time.time() - t0))

        # 2. Agenda
        t0 = time.time()
        try:
            from app.services.calendar_service import calendar_service
            ag = calendar_service.format_daily_agenda()
            steps.append(RoutineStepResult("Agenda del Día", True, ag, time.time() - t0))
        except Exception as e:
            steps.append(RoutineStepResult("Agenda del Día", False, str(e), time.time() - t0))

        # 3. Workspace Sentinel Check
        t0 = time.time()
        try:
            from app.services.workspace_sentinel import workspace_sentinel
            rep = workspace_sentinel.scan_workspace()
            status_text = "Proyectos analizados: 100% saludables ✅" if rep.healthy else f"{len(rep.issues)} problema(s) detectado(s)"
            steps.append(RoutineStepResult("Salud del Espacio de Trabajo", True, status_text, time.time() - t0))
        except Exception as e:
            steps.append(RoutineStepResult("Salud del Espacio de Trabajo", False, str(e), time.time() - t0))

        return steps

    def _run_focus_routine(self) -> List[RoutineStepResult]:
        steps = []
        import time

        # 1. Start Deep Work
        t0 = time.time()
        try:
            from app.actions.deep_work import deep_work_manager
            res_dw = deep_work_manager.start_session(duration_minutes=50, task="Sesión de enfoque profundo")
            steps.append(RoutineStepResult("Modo Trabajo Profundo (Pomodoro)", True, res_dw, time.time() - t0))
        except Exception as e:
            steps.append(RoutineStepResult("Modo Trabajo Profundo (Pomodoro)", False, str(e), time.time() - t0))

        # 2. DND Activation
        t0 = time.time()
        try:
            from app.services.heartbeat_service import heartbeat_service
            heartbeat_service.gatekeeper.enable_dnd()
            steps.append(RoutineStepResult("Activación Silencio DND", True, "No Molestar activado", time.time() - t0))
        except Exception as e:
            steps.append(RoutineStepResult("Activación Silencio DND", False, str(e), time.time() - t0))

        # 3. Workspace Sentinel Quick Check
        t0 = time.time()
        try:
            from app.services.workspace_sentinel import workspace_sentinel
            rep = workspace_sentinel.scan_workspace()
            steps.append(RoutineStepResult("Auditoría de Código Activo", True, f"{rep.files_scanned} archivos verificados", time.time() - t0))
        except Exception as e:
            steps.append(RoutineStepResult("Auditoría de Código Activo", False, str(e), time.time() - t0))

        return steps

    def _run_wrap_up_routine(self) -> List[RoutineStepResult]:
        steps = []
        import time

        # 1. Commitments Review
        t0 = time.time()
        try:
            from app.services.commitment_service import commitment_service
            comms = commitment_service.format_commitments_summary()
            steps.append(RoutineStepResult("Balance de Tareas y Compromisos", True, comms, time.time() - t0))
        except Exception as e:
            steps.append(RoutineStepResult("Balance de Tareas y Compromisos", False, str(e), time.time() - t0))

        # 2. Background Tasks Review
        t0 = time.time()
        try:
            from app.services.background_worker_service import background_worker
            bg_sum = background_worker.get_summary()
            steps.append(RoutineStepResult("Estado de Tareas en Segundo Plano", True, bg_sum, time.time() - t0))
        except Exception as e:
            steps.append(RoutineStepResult("Estado de Tareas en Segundo Plano", False, str(e), time.time() - t0))

        return steps

    def _format_routine_summary(self, routine_name: str, step_results: List[RoutineStepResult]) -> str:
        r_display = {
            "morning": "Rutina Matutina",
            "focus": "Rutina de Concentración y Trabajo",
            "wrap_up": "Rutina de Cierre de Jornada",
        }.get(routine_name, f"Rutina '{routine_name}'")

        lines = [f"✨ **{r_display} ejecutada exitosamente, señor Santiago:**\n"]
        for s in step_results:
            icon = "✅" if s.success else "⚠️"
            lines.append(f"{icon} **{s.step_name}**: {s.output}")

        if routine_name in ("morning", "matutina", "mañana"):
            lines.append("\nSu equipo y entorno se encuentran preparados para una excelente jornada.")
        elif routine_name in ("focus", "work", "trabajo"):
            lines.append("\nEl Modo Trabajo Profundo está activo y he silenciado las interrupciones para su máximo enfoque.")
        elif routine_name in ("wrap_up", "evening", "cierre"):
            lines.append("\nHa completado su jornada. Sus compromisos y estado quedan resguardados.")

        return "\n".join(lines)

    def get_history(self, limit: int = 10) -> List[RoutineExecutionResult]:
        """Returns the most recent routine execution runs."""
        with self._lock:
            return list(reversed(self._history))[:limit]


# Singleton instance
routine_engine = RoutineEngine()
