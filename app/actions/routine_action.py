"""
Routine Action for JARVIS / Liseth.
Provides invocation and management of routines:
- morning (Rutina matutina)
- focus (Rutina de trabajo y concentración)
- wrap_up (Rutina de cierre de jornada)
"""
import logging
from typing import Any, Dict, Optional
from app.services.routine_engine import routine_engine

logger = logging.getLogger("jarvis.routine_action")


def routine_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    """
    Handles user requests regarding automated routines:
    - action: 'execute' | 'list' | 'history'
    - routine: 'morning' | 'focus' | 'wrap_up'
    """
    params = parameters or {}
    action = params.get("action", "execute").lower().strip()
    routine = params.get("routine", "morning").lower().strip()

    if action == "list":
        routines = routine_engine.list_available_routines()
        lines = ["📋 **Rutinas Automatizadas Disponibles** para usted, señor Santiago:"]
        for r in routines:
            lines.append(f"• **{r['name']}** (`{r['id']}`): {r['description']}")
        lines.append("\nPuede activarlas diciendo por ejemplo: *'inicia mi rutina de la mañana'* o *'modo concentración'*.")
        return "\n".join(lines)

    elif action == "history":
        hist = routine_engine.get_history(limit=5)
        if not hist:
            return "Aún no se han ejecutado rutinas en esta sesión, señor Santiago."
        lines = [f"📜 **Historial de Rutinas Recientes** ({len(hist)}):"]
        for h in hist:
            status = "Exitosa ✅" if h.success else "Con advertencias ⚠️"
            lines.append(f"• **{h.routine_name.capitalize()}** — {status} ({h.started_at[:19].replace('T', ' ')})")
        return "\n".join(lines)

    elif action in ("execute", "start", "run"):
        result = routine_engine.execute_routine(routine)
        return result.summary

    return routine_engine.execute_routine(routine).summary
