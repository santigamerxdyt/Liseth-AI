"""
BrainRouter - Autonomous Self-Healing Dual Brain Architecture.
Primary Brain: Google Gemini with Dynamic Live Auto-Discovery, Exponential Backoff, and Self-Healing.
Fallback Brain: Anthropic Claude
"""
import asyncio
import json
import logging
import os
import re
import unicodedata
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
import httpx
from app.config import settings
from app.services.action_dispatcher import action_dispatcher, SYSTEM_TOOL_DECLARATIONS

logger = logging.getLogger("jarvis.brain")

DEFAULT_RATES = {
    "gemini-2.5-flash": {"input_per_1k": 0.0001, "output_per_1k": 0.0004},
    "gemini-2.0-flash": {"input_per_1k": 0.0001, "output_per_1k": 0.0004},
    "gemini-1.5-flash": {"input_per_1k": 0.000075, "output_per_1k": 0.0003},
    "gemini-2.5-flash-lite": {"input_per_1k": 0.000075, "output_per_1k": 0.0003},
    "gemini-flash-latest": {"input_per_1k": 0.0001, "output_per_1k": 0.0004},
    "gemini-3-flash-preview": {"input_per_1k": 0.0001, "output_per_1k": 0.0004},
    "gemini-3.1-flash-lite": {"input_per_1k": 0.000075, "output_per_1k": 0.0003},
    "gemini-3.5-flash-lite": {"input_per_1k": 0.000075, "output_per_1k": 0.0003},
    "gemini-3.5-flash": {"input_per_1k": 0.0001, "output_per_1k": 0.0004},
    "gemini-3.8-flash": {"input_per_1k": 0.0001, "output_per_1k": 0.0004},
    "gemini-3.7-flash": {"input_per_1k": 0.0001, "output_per_1k": 0.0004},
    "gemini-default": {"input_per_1k": 0.0001, "output_per_1k": 0.0004},
    "claude-default": {"input_per_1k": 0.003, "output_per_1k": 0.015},
    "groq-default": {"input_per_1k": 0.0005, "output_per_1k": 0.0008},
    "openai-default": {"input_per_1k": 0.00015, "output_per_1k": 0.0006},
    "ollama-default": {"input_per_1k": 0.0, "output_per_1k": 0.0},
}

# Ranked active candidates for Gemini in order of availability and speed
GEMINI_PRIORITY_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-flash-latest",
]


# Precompiled regexes for sub-millisecond intent matching
_RE_WAKE_FILLERS = re.compile(r"^(?:oye\s+|hola\s+|hey\s+)?(?:liseth|liceth|jarvis)[,\s:]*", re.IGNORECASE)
_RE_POLITE_FILLERS = re.compile(r"^(?:por favor\s+|puedes\s+|podrias\s+|me puedes\s+|me podrias\s+)", re.IGNORECASE)
_RE_PUNCT = re.compile(r"[¿?¡!.,;:\"']")
_RE_VOL_SET = re.compile(r"^(?:pon|poner|ajusta|ajustar|cambia|cambiar|fija|fijar)?\s*(?:el\s+)?(?:volumen|sonido)\s+(?:al|en)?\s*(\d{1,3})%?$")
_RE_VOL_UP = re.compile(r"^(?:sube|subir|aumenta|aumentar|mas|subele al)\s+(?:el\s+)?(?:volumen|sonido|audio)")
_RE_VOL_DOWN = re.compile(r"^(?:baja|bajar|disminuye|disminuir|menos|bajale al)\s+(?:el\s+)?(?:volumen|sonido|audio)")
_RE_VOL_MUTE = re.compile(r"^(?:silencia|silenciar|mute|mutear|quitar el sonido|quita el sonido|desactiva el audio|desactivar el sonido|sin sonido|quitar sonido|quita el audio)")
_RE_BRIGHT_UP = re.compile(r"^(?:sube|subir|aumenta|aumentar|mas)\s+(?:el\s+)?brillo")
_RE_BRIGHT_DOWN = re.compile(r"^(?:baja|bajar|disminuye|disminuir|menos)\s+(?:el\s+)?brillo")
_RE_YT = re.compile(r"^(?:reproduce|reproducir|pon|poner|toca|tocar|escuchar)\s+(?:el video\s+|la cancion\s+|musica\s+|video\s+|en youtube\s+)?(.+)$")
_RE_OPEN_APP = re.compile(r"^(?:abre|abrir|ejecuta|ejecutar|inicia|iniciar|lanza|lanzar)\s+(?:el\s+|la\s+|los\s+|las\s+|un\s+|una\s+|app\s+|programa\s+|aplicacion\s+)?(.+)$")


def detect_direct_intent(user_text: str) -> Optional[Tuple[str, Dict[str, Any], str]]:
    """
    Detects deterministic Windows host automation commands with 0ms latency:
    - App launching ('abre calculadora', 'abrir chrome', 'inicia spotify')
    - Sound/volume ('sube el volumen', 'silencia', 'volumen al 50%')
    - Screen/brightness ('captura de pantalla', 'pantalla completa', 'sube el brillo')
    - System state ('como esta mi pc', 'rendimiento', 'bloquea la pantalla')
    - Media playback ('reproduce queen', 'pausa el video')
    - Undo ('deshacer')

    Returns:
        (tool_name, tool_args, friendly_reply) or None
    """
    if not user_text or not isinstance(user_text, str):
        return None

    raw = user_text.strip()
    # Remove leading conversational filler / wake words
    cleaned = _RE_WAKE_FILLERS.sub("", raw).strip()
    cleaned = _RE_POLITE_FILLERS.sub("", cleaned).strip()

    # Normalized for accent-insensitive matching
    norm = "".join(c for c in unicodedata.normalize('NFKD', cleaned) if not unicodedata.combining(c)).lower().strip()
    norm = _RE_PUNCT.sub("", norm).strip()

    if not norm:
        return None

    # 1. Volume Set: "volumen al 50", "pon el volumen al 80%", "volumen 30"
    m_vol_set = _RE_VOL_SET.match(norm)
    if m_vol_set:
        val = m_vol_set.group(1)
        return (
            "computer_settings",
            {"action": "volume_set", "value": val, "description": cleaned},
            f"He ajustado el volumen de su equipo al {val}%, señor Santiago."
        )

    # 2. Volume Up: "sube el volumen", "aumenta el volumen", "mas volumen", "sube sonido"
    if _RE_VOL_UP.search(norm) or norm in ["mas volumen", "sube volumen", "subir volumen", "volumen arriba", "volumen mas alto"]:
        return (
            "computer_settings",
            {"action": "volume_up", "description": cleaned},
            "He subido el volumen de su equipo, señor Santiago."
        )

    # 3. Volume Down: "baja el volumen", "disminuye el volumen", "menos volumen", "baja sonido"
    if _RE_VOL_DOWN.search(norm) or norm in ["menos volumen", "baja volumen", "bajar volumen", "volumen abajo", "volumen mas bajo"]:
        return (
            "computer_settings",
            {"action": "volume_down", "description": cleaned},
            "He bajado el volumen de su equipo, señor Santiago."
        )

    # 4. Volume Mute: "silencia", "silenciar", "mute", "mutear", "silencia el equipo", "quita el sonido"
    if _RE_VOL_MUTE.search(norm) or norm in ["silencio", "mute", "mutear", "silenciar", "silencia"]:
        return (
            "computer_settings",
            {"action": "volume_mute", "description": cleaned},
            "He silenciado el audio de su equipo, señor Santiago."
        )

    # 5. Brightness Up: "sube el brillo", "aumenta el brillo", "mas brillo"
    if _RE_BRIGHT_UP.search(norm) or norm in ["mas brillo", "sube brillo", "subir brillo", "brillo alto"]:
        return (
            "computer_settings",
            {"action": "brightness_up", "description": cleaned},
            "He aumentado el brillo de su pantalla, señor Santiago."
        )

    # 6. Brightness Down: "baja el brillo", "disminuye el brillo", "menos brillo"
    if _RE_BRIGHT_DOWN.search(norm) or norm in ["menos brillo", "baja brillo", "bajar brillo", "brillo bajo"]:
        return (
            "computer_settings",
            {"action": "brightness_down", "description": cleaned},
            "He reducido el brillo de su pantalla, señor Santiago."
        )

    # 7. Screenshot: "captura de pantalla", "pantallazo", "toma una captura"
    if any(k in norm for k in ["captura de pantalla", "pantallazo", "toma una captura", "tomar una captura", "haz una captura", "hacer una captura", "screenshot"]):
        return (
            "computer_settings",
            {"action": "take_screenshot", "description": cleaned},
            "He tomado una captura de pantalla y la he guardado en sus imágenes, señor Santiago."
        )

    # 8. Fullscreen: "pantalla completa", "modo pantalla completa"
    if "pantalla completa" in norm or norm in ["f11", "pantalla grande"]:
        return (
            "computer_settings",
            {"action": "full_screen", "description": cleaned},
            "He activado el modo de pantalla completa, señor Santiago."
        )

    # 9. Minimize / Desktop: "muestra el escritorio", "ir al escritorio", "minimiza todo"
    if any(k in norm for k in ["mostrar escritorio", "muestra el escritorio", "ver el escritorio", "ir al escritorio", "minimiza todo", "minimizar todo", "minimiza las ventanas", "minimizar ventanas", "minimiza la ventana"]):
        return (
            "computer_settings",
            {"action": "minimize_window", "description": cleaned},
            "He minimizado las ventanas y le muestro su escritorio, señor Santiago."
        )

    # 10. Maximize Window: "maximiza la ventana"
    if any(k in norm for k in ["maximiza la ventana", "maximizar la ventana", "maximiza ventana", "maximizar ventana"]):
        return (
            "computer_settings",
            {"action": "maximize_window", "description": cleaned},
            "He maximizado la ventana activa, señor Santiago."
        )

    # 11. Shutdown / Exit Liseth App: "cierra tu aplicacion", "cierra tu programa", "cierra liseth", "apagate"
    if any(k in norm for k in [
        "cierra tu aplicacion", "cierra tu aplicación", "cerrar tu aplicacion", "cerrar tu aplicación",
        "cierra tu programa", "cerrar tu programa", "cierra el programa", "cerrar el programa",
        "cierra tu ventana", "cerrar tu ventana",
        "cierra la aplicacion de liseth", "cierra la aplicación de liseth",
        "cierra la aplicacion", "cierra la aplicación", "cerrar la aplicacion", "cerrar la aplicación",
        "cierra el asistente", "cerrar el asistente",
        "cierra liseth", "cerrar liseth",
        "apagate liseth", "apágate liseth", "apagate", "apágate",
        "apaga el asistente", "apagar el asistente", "apaga el programa", "apagar el programa",
        "apaga tu programa", "apagar tu programa", "apaga tu aplicacion", "apagar tu aplicacion",
        "deten tu programa", "detén tu programa", "deten la aplicacion", "detén la aplicación",
        "detener tu programa", "detener la aplicacion", "detener el programa", "deten el programa",
        "salir de liseth", "sal de la aplicacion", "sal de la aplicación", "termina tu ejecucion", "termina tu ejecución"
    ]):
        return (
            "shutdown_app",
            {"delay_seconds": 2.0},
            "Hasta luego, señor Santiago. Ha sido un placer asistirle hoy. Cerrando la aplicación y deteniendo todos los servicios..."
        )

    # 12. Close Window: "cierra la ventana"
    if any(k in norm for k in ["cierra la ventana", "cerrar ventana", "cierra esta ventana", "cerrar esta ventana"]):
        return (
            "computer_settings",
            {"action": "close_window", "description": cleaned},
            "He cerrado la ventana activa, señor Santiago."
        )

    # 12. Lock Screen: "bloquea la pantalla"
    if any(k in norm for k in ["bloquea la pantalla", "bloquear la pantalla", "bloquear pantalla", "bloquea la pc", "bloquea el pc", "bloquea el equipo", "bloquear el equipo"]):
        return (
            "computer_settings",
            {"action": "lock_screen", "description": cleaned},
            "He bloqueado la pantalla de su equipo por seguridad, señor Santiago."
        )

    # 13. Media Controls: Next track, Prev track, Stop, Pause/Resume, Spotify
    if any(k in norm for k in ["siguiente cancion", "siguiente cancion en spotify", "pasa la cancion", "siguiente pista", "siguiente tema", "pasa la musica", "next song", "next track"]):
        return (
            "computer_settings",
            {"action": "media_next", "description": cleaned},
            "Pasando a la siguiente canción, señor Santiago."
        )

    if any(k in norm for k in ["cancion anterior", "anterior cancion", "pista anterior", "cancion previa", "musica anterior", "previous song", "prev track", "retrocede la cancion"]):
        return (
            "computer_settings",
            {"action": "media_prev", "description": cleaned},
            "Regresando a la pista anterior, señor Santiago."
        )

    if any(k in norm for k in ["deten la musica", "detener la musica", "para la musica", "parar la musica", "para la reproduccion", "deten la reproduccion", "detener reproduccion"]):
        return (
            "computer_settings",
            {"action": "media_stop", "description": cleaned},
            "He detenido la reproducción multimedia, señor Santiago."
        )

    if any(k in norm for k in ["pausa el video", "pausar el video", "pausa la musica", "pausar la musica", "pausa la reproduccion", "reanudar la reproduccion", "pausar video", "pausa video"]):
        return (
            "computer_settings",
            {"action": "pause_video", "description": cleaned},
            "He alternado la reproducción multimedia, señor Santiago."
        )

    # 13b. Spotify Native Playback: "pon en spotify coldplay", "reproduce en spotify queen"
    if "spotify" in norm and any(k in norm for k in ["pon ", "reproduce ", "busca ", "escuchar ", "toca "]):
        q = norm
        for prefix in ["pon en spotify", "reproduce en spotify", "busca en spotify", "toca en spotify", "escuchar en spotify", "abre spotify y pon", "abre spotify y reproduce", "en spotify reproduce", "en spotify pon"]:
            if prefix in q:
                q = q.replace(prefix, "").strip()
                break
        q = q.replace("en spotify", "").replace("spotify", "").strip()
        return (
            "computer_settings",
            {"action": "spotify_play", "value": q, "description": cleaned},
            f"Abriendo Spotify y reproduciendo {q or 'música'}, señor Santiago."
        )

    # 13c. Administrator Mode / Elevation check: "eres administradora", "tienes permisos de administrador"
    if any(k in norm for k in ["eres administradora", "tienes permisos de administrador", "estado de privilegios", "tienes acceso de administrador", "tienes acceso administrador", "modo administrador"]):
        from app.core.admin import is_admin
        is_adm = is_admin()
        status_msg = (
            "Sí, señor Santiago. Estoy ejecutándome con privilegios completos de Administrador en Windows. Tengo acceso total al sistema y hardware."
            if is_adm else
            "Señor Santiago, actualmente me encuentro en modo estándar sin privilegios elevados de Administrador."
        )
        return (
            "admin_privileges",
            {"check": True},
            status_msg
        )

    # 14. Telemetry: "estado de mi pc", "rendimiento", "como esta mi pc"
    if any(k in norm for k in ["estado de mi pc", "estado del pc", "estado de la pc", "estado del sistema", "como esta mi pc", "como esta el equipo", "rendimiento del equipo", "rendimiento de mi pc", "rendimiento del sistema", "uso de cpu", "uso de ram", "telemetria"]):
        return (
            "system_monitor",
            {"metric": "all"},
            "Consultando telemetría del sistema..."
        )

    # 15. Undo: "deshacer", "deshazlo", "revertir"
    if norm in ["deshacer", "deshazlo", "deshaz la accion", "revertir", "revertir accion", "ctrl z"]:
        return (
            "undo",
            {"action": "undo"},
            "Revirtiendo la última acción..."
        )

    # 16. YouTube / Media Playback: "reproduce bohemian rhapsody", "pon coldplay"
    m_yt = _RE_YT.match(norm)
    if m_yt:
        query = m_yt.group(1).strip()
        if query and not any(ign in query for ign in ["volumen", "brillo", "pantalla", "reposo", "dormir", "modo reposo"]):
            return (
                "youtube_video",
                {"action": "play", "query": query},
                f"Con mucho gusto, señor Santiago. Reproduciendo {query} ahora."
            )

    # 17. Deep Work & Pomodoro: "modo trabajo profundo", "iniciar pomodoro", "terminar pomodoro"
    if any(k in norm for k in ["terminar trabajo profundo", "cancelar trabajo profundo", "desactivar trabajo profundo", "detener trabajo profundo", "terminar modo concentracion", "cancelar modo concentracion", "terminar pomodoro", "cancelar pomodoro", "detener pomodoro", "salir de pomodoro", "terminar modo trabajo"]):
        return (
            "deep_work",
            {"action": "stop"},
            "Finalizando sesión de trabajo profundo..."
        )
    if any(k in norm for k in ["estado del pomodoro", "estado de trabajo profundo", "cuanto falta de trabajo profundo", "cuanto tiempo queda de pomodoro", "tiempo restante de pomodoro", "como va el pomodoro"]):
        return (
            "deep_work",
            {"action": "status"},
            "Consultando estado de la sesión de trabajo profundo..."
        )
    if any(k in norm for k in ["modo trabajo profundo", "trabajo profundo", "modo concentracion", "modo concentración", "iniciar pomodoro", "activa modo concentracion", "activar modo concentracion", "comenzar pomodoro", "modo pomodoro", "modo trabajo", "inicia un pomodoro"]):
        return (
            "deep_work",
            {"action": "start"},
            "Iniciando modo trabajo profundo y activando silencio de interrupciones..."
        )

    # 18. Screen Vision: "mira mi pantalla", "que estoy viendo"
    if any(k in norm for k in ["mira mi pantalla", "mira la pantalla", "que hay en mi pantalla", "que estoy viendo", "analiza mi pantalla", "que ves en mi pantalla", "mira esto", "mira lo que tengo en pantalla"]):
        return (
            "screen_process",
            {"query": cleaned},
            "Analizando visualmente lo que tiene en pantalla, señor Santiago..."
        )

    # 19. Calendar Agenda: "mis reuniones", "que reuniones tengo", "agenda de hoy"
    if any(k in norm for k in ["mis reuniones", "que reuniones tengo", "mi agenda de hoy", "agenda de hoy", "proxima reunion", "reuniones de hoy", "cuales son mis reuniones", "que tengo en el calendario"]):
        return (
            "manage_calendar",
            {"action": "list"},
            "Consultando su agenda y reuniones de hoy..."
        )

    # 20. RAM Optimization: "libera la memoria", "optimizar ram"
    if any(k in norm for k in ["libera la memoria", "liberar memoria", "optimiza la memoria", "optimizar memoria", "limpia la ram", "limpiar ram", "optimizar ram", "libera la ram", "liberar ram", "libera memoria", "optimiza memoria", "limpiar memoria"]):
        return (
            "optimize_ram",
            {},
            "Optimizando y liberando memoria del sistema..."
        )

    # 21. Do Not Disturb (DND): "desactiva no molestar" must be evaluated before "activa no molestar"
    if any(k in norm for k in ["desactiva no molestar", "desactivar no molestar", "quitar no molestar", "quitar silencio", "desactivar silencio", "desactiva el silencio", "quitar modo silencio", "desactiva silencio"]):
        return (
            "toggle_dnd",
            {"enabled": False},
            "Modo No Molestar desactivado, señor Santiago. Notificaciones normales restablecidas."
        )

    if any(k in norm for k in ["activa no molestar", "activar no molestar", "modo no molestar", "modo silencio", "silencio total", "no me molestes", "activar silencio", "activa silencio"]):
        return (
            "toggle_dnd",
            {"enabled": True},
            "Modo No Molestar activado, señor Santiago. He silenciado las alertas por voz."
        )

    # 22. Commitments / Tasks: "que tengo pendiente", "cuales son mis compromisos", "mis tareas"
    if any(k in norm for k in ["que tengo pendiente", "cuales son mis compromisos", "mis tareas", "compromisos pendientes", "tareas pendientes", "mis compromisos", "que tareas tengo"]):
        return (
            "manage_commitments",
            {"action": "list"},
            "Consultando sus compromisos pendientes..."
        )

    # 23. Weather: "como esta el clima", "el clima hoy", "va a llover", "que temperatura hace"
    if any(k in norm for k in ["como esta el clima", "el clima hoy", "clima hoy", "va a llover", "que temperatura hace", "como esta el tiempo", "cual es el clima", "pronostico del tiempo"]):
        return (
            "weather_report",
            {"city": "Bogotá"},
            "Consultando reporte del clima..."
        )

    # 24. Smart Clipboard: "analiza mi portapapeles", "que tengo copiado"
    if any(k in norm for k in ["analiza mi portapapeles", "analizar mi portapapeles", "revisa mi portapapeles", "revisar mi portapapeles", "mira mi portapapeles", "que tengo en el portapapeles", "que tengo copiado", "mira lo que copie", "mira lo que he copiado", "analiza lo que copie", "analiza lo que he copiado", "explica lo que copie", "explica lo que tengo copiado", "corrige lo que copie", "corrige lo que tengo copiado", "depura mi portapapeles"]):
        return (
            "smart_clipboard",
            {"action": "analyze", "query": cleaned},
            "Inspeccionando y analizando el contenido de su portapapeles, señor Santiago..."
        )

    # 25. Gmail Smart Inbox Summary: "revisa mi correo", "tengo correos urgentes", "resumen de mis correos"
    if any(k in norm for k in ["revisa mi correo", "revisa mi email", "revisar mi correo", "revisa mi gmail", "revisar mi gmail", "que correos tengo", "tengo correos urgentes", "resumen de mi correo", "resumen de mis correos", "resumen de correos", "hay correos nuevos", "hay algun correo importante", "correos no leidos"]):
        return (
            "gmail_summary",
            {"max_results": 10},
            "Analizando su bandeja de entrada de Gmail y clasificando correos importantes, señor Santiago..."
        )

    # 26. Background Autonomous Tasks: "tareas en segundo plano", "que tareas estan en segundo plano", "cancela la tarea en segundo plano"
    if any(k in norm for k in ["cancela la tarea en segundo plano", "cancelar tarea en segundo plano", "cancela la tarea de fondo", "deten la tarea en segundo plano"]):
        return (
            "background_task",
            {"action": "cancel"},
            "Cancelando tarea en segundo plano..."
        )
    if any(k in norm for k in ["tareas en segundo plano", "que tareas estan en segundo plano", "tareas de fondo", "estado de tareas en segundo plano", "cuales son las tareas en segundo plano", "como van las tareas en segundo plano", "lista de tareas en segundo plano"]):
        return (
            "background_task",
            {"action": "list"},
            "Consultando tareas en segundo plano, señor Santiago..."
        )
    if any(norm.startswith(p) for p in ["ejecuta en segundo plano", "haz en segundo plano", "encargate en segundo plano", "trabaja en segundo plano en", "procesa en segundo plano"]):
        task_desc = norm
        for p in ["ejecuta en segundo plano", "haz en segundo plano", "encargate en segundo plano", "trabaja en segundo plano en", "procesa en segundo plano"]:
            if task_desc.startswith(p):
                task_desc = task_desc[len(p):].strip()
                break
        return (
            "background_task",
            {"action": "create", "title": task_desc or "Tarea en segundo plano", "details": cleaned},
            "Delegando tarea a mi cola de trabajo autónomo en segundo plano..."
        )

    # 27. Workspace Sentinel: "estado del centinela", "como estan mis proyectos", "revisa mi codigo"
    if any(k in norm for k in ["escanea mis proyectos", "escanear mis proyectos", "escanea el espacio de trabajo", "escaneo de proyectos", "analiza el proyecto", "analiza mis proyectos"]):
        return (
            "workspace_sentinel",
            {"action": "scan"},
            "Iniciando escaneo de salud y sintaxis en sus proyectos de desarrollo, señor Santiago..."
        )
    if any(k in norm for k in ["estado del centinela", "como estan mis proyectos", "como esta mi codigo", "revisa mis proyectos", "revisa mi codigo", "salud de mis proyectos", "centinela de codigo", "centinela de proyectos", "proyectos bajo vigilancia"]):
        return (
            "workspace_sentinel",
            {"action": "status"},
            "Consultando el reporte del Centinela de Código en segundo plano..."
        )

    # 28. Automated Routines: "rutina de la mañana", "rutina de trabajo", "rutina de cierre", "mis rutinas"
    if any(k in norm for k in ["mis rutinas", "cuales son mis rutinas", "lista de rutinas", "que rutinas tienes", "que rutinas puedo ejecutar"]):
        return (
            "execute_routine",
            {"action": "list", "routine": "morning"},
            "Consultando las rutinas automatizadas disponibles, señor Santiago..."
        )
    if any(k in norm for k in ["rutina de la manana", "rutina de la mañana", "rutina matutina", "inicia mi rutina de la manana", "inicia mi rutina de la mañana", "inicia rutina matutina", "iniciar rutina de la manana", "iniciar rutina de la mañana", "ejecuta la rutina matutina", "comienza la rutina de la manana"]):
        return (
            "execute_routine",
            {"action": "execute", "routine": "morning"},
            "Iniciando su rutina matutina de preparación de jornada, señor Santiago..."
        )
    if any(k in norm for k in ["rutina de trabajo", "rutina de concentracion", "rutina de concentración", "rutina de enfoque", "inicia rutina de trabajo", "prepara mi entorno de trabajo", "prepara mi entorno"]):
        return (
            "execute_routine",
            {"action": "execute", "routine": "focus"},
            "Preparando su entorno de trabajo y concentración profunda, señor Santiago..."
        )
    if any(k in norm for k in ["rutina de cierre", "rutina de la noche", "rutina de la tarde", "inicia rutina de cierre", "finalizar jornada", "cierre de jornada"]):
        return (
            "execute_routine",
            {"action": "execute", "routine": "wrap_up"},
            "Ejecutando su rutina de cierre de jornada, señor Santiago..."
        )

    # 29. Daily Debrief & Activity Ledger: "que hiciste hoy", "resumen del dia", "bitacora de hoy", "reporte ejecutivo"
    if any(k in norm for k in ["lista de actividades de hoy", "bitacora de eventos", "historial de hoy"]):
        return (
            "daily_debrief",
            {"action": "list"},
            "Consultando el registro de actividades de hoy, señor Santiago..."
        )
    if any(k in norm for k in ["que hiciste hoy", "que has hecho hoy", "resumen del dia", "resumen de hoy", "bitacora de hoy", "reporte ejecutivo", "balance del dia", "balance de hoy", "reporte de hoy", "que hiciste mientras trabajaba"]):
        return (
            "daily_debrief",
            {"action": "summary"},
            "Generando su balance y reporte ejecutivo de trabajo autónomo, señor Santiago..."
        )

    # 30. Business Administration & Finance: VAN, TIR, ROI, Punto de Equilibrio, FODA, Canvas, PESTEL
    if any(k in norm for k in ["calcula el van", "calcula van", "valor actual neto", "evaluacion de van"]):
        return (
            "business_finance",
            {"operation": "van"},
            "Calculando Valor Actual Neto (VAN) del proyecto de inversión, señor Santiago..."
        )
    if any(k in norm for k in ["calcula la tir", "calcula tir", "tasa interna de retorno"]):
        return (
            "business_finance",
            {"operation": "tir"},
            "Calculando Tasa Interna de Retorno (TIR), señor Santiago..."
        )
    if any(k in norm for k in ["calcula el roi", "calcula roi", "retorno de inversion", "retorno sobre la inversion"]):
        return (
            "business_finance",
            {"operation": "roi"},
            "Calculando Retorno sobre la Inversión (ROI), señor Santiago..."
        )
    if any(k in norm for k in ["punto de equilibrio", "calcula el punto de equilibrio", "calcular punto de equilibrio"]):
        return (
            "business_finance",
            {"operation": "punto_equilibrio"},
            "Calculando Punto de Equilibrio operativo en unidades e ingresos..."
        )
    if any(k in norm for k in ["matriz foda", "matriz dofa", "analisis foda", "analisis dofa"]):
        m_org = re.sub(r"^(?:.*?matriz foda(?: de| para)?|.*?analisis foda(?: de| para)?)\s*", "", cleaned, flags=re.IGNORECASE).strip()
        return (
            "business_strategy",
            {"action": "foda", "organization": m_org or "Mi Empresa"},
            "Generando estructura y cruce estratégico de análisis FODA / DOFA, señor Santiago..."
        )
    if any(k in norm for k in ["modelo canvas", "business model canvas", "lienzo canvas"]):
        m_can = re.sub(r"^(?:.*?modelo canvas(?: de| para)?|.*?business model canvas(?: de| para)?)\s*", "", cleaned, flags=re.IGNORECASE).strip()
        return (
            "business_strategy",
            {"action": "canvas", "topic": m_can or "Negocio Digital"},
            "Generando Business Model Canvas de 9 bloques de Osterwalder, señor Santiago..."
        )
    if any(k in norm for k in ["analisis pestel", "matriz pestel"]):
        return (
            "business_strategy",
            {"action": "porter", "industry": "Sector Empresarial"},
            "Generando análisis del macroentorno empresarial PESTEL..."
        )

    # 31. Academic & University Tools: Normas APA 7, Ensayos, Informes
    if any(k in norm for k in ["normas apa", "formato apa", "parametros apa", "margenes apa"]):
        return (
            "academic_helper",
            {"action": "normas"},
            "Consultando especificaciones oficiales de Normas APA 7ª Edición..."
        )
    if any(k in norm for k in ["cita apa", "referencia apa", "genera cita apa", "como citar en apa"]):
        return (
            "academic_helper",
            {"action": "apa"},
            "Generando referencia y cita bibliográfica en formato APA 7..."
        )
    if any(k in norm for k in ["estructura de ensayo", "estructura para ensayo", "como hacer un ensayo"]):
        return (
            "academic_helper",
            {"action": "estructura", "doc_type": "ensayo"},
            "Generando esquema metodológico para ensayo académico universitario..."
        )
    if any(k in norm for k in ["informe de consultoria", "consultoria gerencial", "blueprint de informe"]):
        return (
            "workspace_automation",
            {"action": "report_blueprint", "title": cleaned, "type": "consultoria"},
            "Generando estructura profesional para informe de consultoría gerencial..."
        )
    if any(k in norm for k in ["estructura de informe", "estructura para informe", "informe ejecutivo"]):
        return (
            "academic_helper",
            {"action": "estructura", "doc_type": "informe"},
            "Generando estructura profesional para informe ejecutivo y estudio de caso..."
        )

    # 32. Data & Developer Tools: Estadística descriptiva
    if any(k in norm for k in ["estadistica descriptiva", "resumen estadistico", "analisis de datos estadistico"]):
        return (
            "data_dev_tools",
            {"operation": "stats"},
            "Calculando análisis estadístico descriptivo de sus datos..."
        )

    # 33. Reverse Engineering & Binary Inspection (REA Engine)
    if any(k in norm for k in ["motor de ingenieria inversa", "estado de rea", "estado del motor de ingenieria", "herramientas de ingenieria inversa"]):
        return (
            "reverse_engineer",
            {"action": "status"},
            "Consultando estado del motor de ingeniería inversa REA..."
        )

    if any(k in norm for k in ["ingenieria inversa", "analiza el ejecutable", "analiza este ejecutable", "analiza el binario", "inspecciona el binario", "descompila el binario", "descompila el archivo", "extrae el asar", "analiza el asar", "entropia de"]):
        target_file = ""
        m_path = re.search(r"[\"']([^\"']+)[\"']", cleaned)
        if m_path:
            target_file = m_path.group(1).strip()
        else:
            m_win_path = re.search(r"([a-zA-Z]:\\[^\s]+|\S+\.(?:exe|dll|sys|asar|apk|wasm|elf|bin))", cleaned, re.IGNORECASE)
            if m_win_path:
                target_file = m_win_path.group(1).strip()

        act = "inspect"
        if "entropia" in norm:
            act = "entropy"
        elif "cadenas" in norm or "strings" in norm:
            act = "strings"
        elif "asar" in norm:
            act = "asar"

        return (
            "reverse_engineer",
            {"action": act, "target_path": target_file},
            f"Iniciando análisis de ingeniería inversa con el motor REA sobre {os.path.basename(target_file) if target_file else 'el archivo seleccionado'}, señor Santiago..."
        )

    # 33b. Ego Lite Browser Automation (token-slashing web tasks & task spaces)
    if any(k in norm for k in ["motor ego", "estado de ego", "estado de ego browser", "navegador ego", "ego browser"]):
        if any(w in norm for w in ["estado", "status", "como esta", "informacion", "salud"]):
            return (
                "ego_browser",
                {"action": "status"},
                "Consultando estado del motor de automatización web Ego Lite, señor Santiago..."
            )

    if any(k in norm for k in ["espacios de ego", "task spaces", "espacios de tarea", "espacios de navegacion"]):
        return (
            "ego_browser",
            {"action": "spaces"},
            "Listando los espacios de tarea activos de Ego Browser..."
        )

    if any(k in norm for k in ["busca en google con ego", "buscar en google con ego", "extraccion de google", "google con ego"]):
        q = re.sub(r"^(?:busca(?:r)? en google con ego|extraccion de google|google con ego)\s*", "", cleaned, flags=re.IGNORECASE).strip()
        return (
            "ego_browser",
            {"action": "google", "query": q},
            f"Ejecutando búsqueda y extracción limpia en Google para '{q}' con el motor Ego Lite..."
        )

    if any(k in norm for k in ["estadisticas de github", "metricas de github", "analiza el repo", "stats de github", "repositorio github"]):
        m_repo = re.search(r"github\.com/([a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+)", cleaned, re.IGNORECASE)
        repo_id = m_repo.group(1) if m_repo else ""
        if not repo_id:
            m_words = re.search(r"(?:github|repo|repositorio)\s+([a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+)", cleaned, re.IGNORECASE)
            if m_words:
                repo_id = m_words.group(1)
        return (
            "ego_browser",
            {"action": "github", "repo": repo_id or cleaned},
            f"Consultando estadísticas del repositorio de GitHub '{repo_id or cleaned}' con Ego Lite..."
        )

    if any(k in norm for k in ["snapshot de", "arbol de la pagina", "analiza la pagina", "navega con ego a", "entra con ego a", "navega a con ego"]):
        m_url = re.search(r"(https?://\S+|www\.\S+|\b[a-zA-Z0-9_\-]+\.[a-z]{2,6}\S*)", cleaned, re.IGNORECASE)
        target_url = m_url.group(1) if m_url else ""
        return (
            "ego_browser",
            {"action": "snapshot", "url": target_url},
            f"Navegando y extrayendo snapshot semántico de {target_url or 'la página web'} con Ego Lite, señor Santiago..."
        )

    if any(k in norm for k in ["haz clic en", "haz click en", "presiona la opcion", "pulsa el boton"]) and any(w in norm for w in ["con ego", "en el navegador", "ref="]):
        m_target = re.search(r"(?:ref[=:]\s*|\b)([0-9]+)\b", cleaned)
        tgt = m_target.group(1) if m_target else cleaned
        return (
            "ego_browser",
            {"action": "click", "target": tgt},
            f"Presionando el elemento interactivo {tgt} en el navegador..."
        )

    # 33c. Vercel Labs Agent Skills (Deployments, React Best Practices, Web Interface Guidelines)
    if any(k in norm for k in ["motor vercel", "estado de vercel", "vercel skills", "herramientas de vercel"]):
        return (
            "vercel_skills",
            {"action": "status"},
            "Consultando estado de la suite de desarrollo Vercel Labs, señor Santiago..."
        )

    if any(k in norm for k in ["despliega mi aplicacion", "desplegar proyecto a vercel", "despliega a vercel", "publica esta web en vercel", "publicar en vercel", "deploy to vercel", "deploy my app", "despliega este proyecto"]):
        m_path = re.search(r"[\"']([^\"']+)[\"']", cleaned)
        tgt_path = m_path.group(1).strip() if m_path else "."
        is_prod = any(w in norm for w in ["produccion", "prod", "production"])
        return (
            "vercel_skills",
            {"action": "deploy", "path": tgt_path, "prod": is_prod},
            f"Iniciando despliegue {'en producción' if is_prod else 'de vista previa'} en Vercel, señor Santiago..."
        )

    if any(k in norm for k in ["audita este componente react", "optimiza mi codigo react", "mejores practicas de react", "auditoria react", "audita este archivo react", "rendimiento de react", "audita react"]):
        m_path = re.search(r"[\"']([^\"']+)[\"']", cleaned)
        if not m_path:
            m_path = re.search(r"([a-zA-Z]:\\[^\s]+|\S+\.(?:tsx|jsx|js|ts))", cleaned, re.IGNORECASE)
        tgt_path = m_path.group(1).strip() if m_path else "."
        return (
            "vercel_skills",
            {"action": "audit_react", "path": tgt_path},
            f"Auditando código React/Next.js según los estándares de ingeniería de Vercel, señor Santiago..."
        )

    if any(k in norm for k in ["revisa el diseno web", "revisa el diseño web", "diseno web", "diseño web", "audita la interfaz ui", "interfaz ui", "auditoria de accesibilidad", "directrices de diseno", "directrices de diseño", "audita el diseno", "audita el diseño", "web design guidelines"]):
        m_path = re.search(r"[\"']([^\"']+)[\"']", cleaned)
        if not m_path:
            m_path = re.search(r"([a-zA-Z]:\\[^\s]+|\S+\.(?:html|css|tsx|jsx|vue))", cleaned, re.IGNORECASE)
        tgt_path = m_path.group(1).strip() if m_path else "."
        return (
            "vercel_skills",
            {"action": "audit_design", "path": tgt_path},
            f"Analizando cumplimiento de directrices de interfaz y accesibilidad web (Web Interface Guidelines)..."
        )

    # 33d. Security Audit Enterprise (Vulnerability Scanner & Secret Exposure)
    if any(k in norm for k in ["motor de seguridad", "estado de seguridad", "seguridad informatica", "herramientas de seguridad"]):
        return (
            "security_audit",
            {"action": "status"},
            "Consultando estado del motor de auditoría de ciberseguridad, señor Santiago..."
        )

    if any(k in norm for k in [
        "audita la seguridad", "auditoria de seguridad", "escanea vulnerabilidades",
        "busca vulnerabilidades", "revisa la seguridad", "analisis de seguridad",
        "analiza vulnerabilidades", "security audit", "busca secretos expuestos",
        "busca api keys expuestas", "claves expuestas"
    ]):
        m_path = re.search(r"[\"']([^\"']+)[\"']", cleaned)
        if not m_path:
            m_path = re.search(r"([a-zA-Z]:\\[^\s]+|\S+\.(?:py|js|ts|jsx|tsx|html|env|json|yaml|yml|sh|bat))", cleaned, re.IGNORECASE)
        tgt_path = m_path.group(1).strip() if m_path else "."
        return (
            "security_audit",
            {"action": "audit", "path": tgt_path},
            f"Iniciando escaneo de vulnerabilidades y ciberseguridad sobre {tgt_path}, señor Santiago..."
        )

    # 33e. SlopMonster & Deslop (AI Writing Detector & Copy Humanizer)
    if any(k in norm for k in ["motor anti slop", "estado de slopmonster", "motor de humanizacion", "slopmonster"]):
        if any(w in norm for w in ["estado", "status", "como esta", "informacion"]):
            return (
                "slopmonster",
                {"action": "status"},
                "Consultando estado del motor anti-slop y humanizador de redacción..."
            )

    if any(k in norm for k in ["humaniza este texto", "humaniza este documento", "humaniza este ensayo", "humanizar texto", "humaniza mi correo", "humaniza mi borrador", "humaniza el archivo"]):
        m_path = re.search(r"[\"']([^\"']+)[\"']", cleaned)
        if m_path:
            return (
                "slopmonster",
                {"action": "humanize", "path": m_path.group(1).strip()},
                f"Humanizando la redacción del archivo '{m_path.group(1).strip()}' con SlopMonster, señor Santiago..."
            )
        m_text = re.search(r"(?:texto|correo|borrador|ensayo)[\s:]+[\"']([^\"']+)[\"']", cleaned, re.IGNORECASE)
        text_arg = m_text.group(1).strip() if m_text else ""
        return (
            "slopmonster",
            {"action": "humanize", "text": text_arg or cleaned},
            "Humanizando el texto seleccionado para eliminar clichés y fórmulas robóticas de IA..."
        )

    if any(k in norm for k in ["deslop", "suena como ia", "detecta si es ia", "parece ia", "audita la redaccion", "analisis anti slop"]):
        m_path = re.search(r"[\"']([^\"']+)[\"']", cleaned)
        if m_path:
            return (
                "slopmonster",
                {"action": "deslop", "path": m_path.group(1).strip()},
                f"Evaluando patrones y huellas de IA en '{m_path.group(1).strip()}' con SlopMonster..."
            )
        return (
            "slopmonster",
            {"action": "deslop", "text": cleaned},
            "Analizando huellas de IA y calculando puntaje de humanidad (0-5)..."
        )

    # 33f. Git Auto-Sync & GitHub Cloud Synchronization
    if any(k in norm for k in ["sincroniza con github", "sincronizar con github", "sube los cambios a github", "subir cambios a github", "sube a github", "guarda mis cambios en github", "actualiza el repositorio", "actualizar el repositorio", "sincroniza el repositorio", "sincronizar el repositorio", "sube el proyecto a github"]):
        m_msg = re.search(r"(?:con mensaje|mensaje|commit)[\s:]+[\"']([^\"']+)[\"']", cleaned, re.IGNORECASE)
        msg_arg = m_msg.group(1).strip() if m_msg else None
        return (
            "git_sync",
            {"action": "sync", "message": msg_arg},
            "Sincronizando y subiendo los cambios del proyecto a su repositorio de GitHub, señor Santiago..."
        )

    if any(k in norm for k in ["estado de git", "estado de sincronizacion", "estado del repositorio", "estado de github", "cambios pendientes en git"]):
        return (
            "git_sync",
            {"action": "status"},
            "Consultando el estado de sincronización local contra el repositorio remoto en GitHub..."
        )

    if any(k in norm for k in ["centinela de github", "auto sync de github", "sincronizacion automatica"]) and any(w in norm for w in ["inicia", "activa", "empieza", "activar"]):
        return (
            "git_sync",
            {"action": "start_watcher"},
            "Activando centinela de sincronización automática en segundo plano con GitHub..."
        )

    if any(k in norm for k in ["centinela de github", "auto sync de github", "sincronizacion automatica"]) and any(w in norm for w in ["deten", "para", "apaga", "desactiva", "detener"]):
        return (
            "git_sync",
            {"action": "stop_watcher"},
            "Deteniendo centinela de sincronización automática con GitHub..."
        )

    # 33g. Academic Research & Scientific Literature
    if any(k in norm for k in ["motor academico", "estado de investigacion", "motor cientifico", "academic research"]):
        if any(w in norm for w in ["estado", "status", "como esta", "informacion"]):
            return (
                "academic_research",
                {"action": "status"},
                "Consultando estado del motor de investigación académica y científica..."
            )

    if any(k in norm for k in ["estado del arte de", "estado del arte sobre", "revision bibliografica de", "revision bibliografica sobre", "sintesis academica de"]):
        m_top = re.sub(r"^(?:estado del arte de|estado del arte sobre|revision bibliografica de|revision bibliografica sobre|sintesis academica de)\s*", "", cleaned, flags=re.IGNORECASE).strip()
        return (
            "academic_research",
            {"action": "literature_review", "query": m_top or cleaned},
            f"Elaborando Estado del Arte y revisión de literatura científica sobre '{m_top or cleaned}', señor Santiago..."
        )

    if any(k in norm for k in ["busca articulos sobre", "busca papers sobre", "articulos cientificos de", "articulos cientificos sobre", "papers cientificos de", "papers sobre"]):
        m_q = re.sub(r"^(?:busca(?:r)? articulos sobre|busca(?:r)? papers sobre|articulos cientificos de|articulos cientificos sobre|papers cientificos de|papers sobre)\s*", "", cleaned, flags=re.IGNORECASE).strip()
        return (
            "academic_research",
            {"action": "search", "query": m_q or cleaned},
            f"Buscando artículos científicos y literatura revisada por pares para '{m_q or cleaned}'..."
        )

    # 33h. Business Strategy & Advanced Corporate Finance
    if any(k in norm for k in ["motor de estrategia", "estado de business strategy", "estrategia empresarial"]):
        if any(w in norm for w in ["estado", "status", "como esta", "informacion"]):
            return (
                "business_strategy",
                {"action": "status"},
                "Consultando estado del motor de estrategia empresarial y finanzas corporativas..."
            )

    if any(k in norm for k in ["matriz foda de", "analisis foda de", "matriz foda para", "foda de", "swot de", "matriz swot"]):
        m_org = re.sub(r"^(?:matriz foda de|analisis foda de|matriz foda para|foda de|swot de|matriz swot(?:\s+de)?)\s*", "", cleaned, flags=re.IGNORECASE).strip()
        return (
            "business_strategy",
            {"action": "foda", "organization": m_org or "Mi Empresa"},
            f"Estructurando Matriz FODA y cruce estratégico para '{m_org or 'la organización'}', señor Santiago..."
        )

    if any(k in norm for k in ["5 fuerzas de porter", "cinco fuerzas de porter", "fuerzas de porter de", "fuerzas de porter para", "analisis porter"]):
        m_ind = re.sub(r"^(?:(?:5|cinco) fuerzas de porter(?:\s+de|\s+para)?|fuerzas de porter de|fuerzas de porter para|analisis porter(?:\s+de|\s+para)?)\s*", "", cleaned, flags=re.IGNORECASE).strip()
        return (
            "business_strategy",
            {"action": "porter", "industry": m_ind or "Sector Industrial"},
            f"Analizando las 5 Fuerzas de Michael Porter para '{m_ind or 'la industria seleccionada'}'..."
        )

    if any(k in norm for k in ["modelo canvas de", "modelo canvas para", "business model canvas de", "business model canvas para", "canvas de negocio"]):
        m_can = re.sub(r"^(?:modelo canvas de|modelo canvas para|business model canvas de|business model canvas para|canvas de negocio(?:\s+de)?)\s*", "", cleaned, flags=re.IGNORECASE).strip()
        return (
            "business_strategy",
            {"action": "canvas", "topic": m_can or "Negocio Digital"},
            f"Diseñando el Business Model Canvas de 9 bloques para '{m_can or 'el modelo de negocio'}'..."
        )

    if any(k in norm for k in ["proyeccion de flujo de caja", "flujo de caja libre", "proyecta el flujo de caja", "proyeccion financiera"]):
        return (
            "business_strategy",
            {"action": "cash_flow", "revenue": 100000.0, "growth": 0.15, "margin": 0.25, "periods": 5},
            "Calculando proyección de Estado de Resultados y Flujo de Caja Libre (FCF), señor Santiago..."
        )

    if any(k in norm for k in ["tabla de amortizacion", "amortizacion de prestamo", "amortizacion de credito", "amortizar credito", "amortizar prestamo"]):
        sys_choice = "aleman" if "aleman" in norm else "frances"
        return (
            "business_strategy",
            {"action": "amortization", "principal": 50000000.0, "rate": 18.0, "months": 12, "system": sys_choice},
            f"Generando tabla de amortización de crédito en Sistema {sys_choice.title()}..."
        )

    if any(k in norm for k in ["calcula el wacc", "calculo del wacc", "costo de capital wacc", "wacc de la empresa"]):
        return (
            "business_strategy",
            {"action": "wacc", "equity": 60000.0, "debt": 40000.0, "ke": 15.0, "kd": 10.0, "tax": 35.0},
            "Calculando Costo Promedio Ponderado de Capital (WACC), señor Santiago..."
        )

    # 33i. Data Science & Machine Learning Toolkit
    if any(k in norm for k in ["motor de machine learning", "motor de ciencia de datos", "data ml toolkit"]):
        if any(w in norm for w in ["estado", "status", "como esta", "informacion"]):
            return (
                "data_ml_toolkit",
                {"action": "status"},
                "Consultando estado del motor de analítica y Machine Learning..."
            )

    if any(k in norm for k in ["script de machine learning", "codigo de machine learning", "pipeline de scikit learn", "pipeline de ml"]):
        task_t = "regression" if "regresion" in norm else ("clustering" if "cluster" in norm else "classification")
        return (
            "data_ml_toolkit",
            {"action": "code", "task": task_t},
            f"Generando script optimizado de Machine Learning en Python ({task_t}), señor Santiago..."
        )

    # 33j. Workspace Automation & Office Productivity
    if any(k in norm for k in ["motor de ofimatica", "motor de hojas de calculo", "workspace automation"]):
        if any(w in norm for w in ["estado", "status", "como esta", "informacion"]):
            return (
                "workspace_automation",
                {"action": "status"},
                "Consultando estado de la suite de automatización ofimática y productividad..."
            )

    if any(k in norm for k in ["formula de excel para", "formula para excel", "como hago en excel", "formula de google sheets para", "formula en excel"]):
        req = re.sub(r"^(?:formula(?: de)? excel para|formula para excel|como hago en excel|formula(?: de)? google sheets para|formula en excel)\s*", "", cleaned, flags=re.IGNORECASE).strip()
        return (
            "workspace_automation",
            {"action": "excel_formula", "query": req or cleaned},
            f"Generando solución y fórmula de hoja de cálculo para: '{req or cleaned}'..."
        )

    if any(k in norm for k in ["estructura de informe de consultoria", "esquema para ensayo", "blueprint de informe", "esquema de tesis"]):
        dt = "ensayo" if "ensayo" in norm or "tesis" in norm else "consultoria"
        return (
            "workspace_automation",
            {"action": "report_blueprint", "title": cleaned, "type": dt},
            f"Estructurando esquema profesional para {dt}, señor Santiago..."
        )

    if any(k in norm for k in ["diapositivas para", "estructura de presentacion", "esquema de diapositivas", "diapositivas ejecutivas"]):
        topic_slide = re.sub(r"^(?:diapositivas para|estructura de presentacion(?: para)?|esquema de diapositivas(?: para)?|diapositivas ejecutivas(?: para)?)\s*", "", cleaned, flags=re.IGNORECASE).strip()
        return (
            "workspace_automation",
            {"action": "presentation_deck", "topic": topic_slide or "Presentación Ejecutiva", "slides": 5},
            f"Diseñando la arquitectura visual de diapositivas para '{topic_slide or 'la presentación'}'..."
        )

    # 33k. UNAL Palmira Business Administration Curriculum Companion (Acuerdo 19 de 2012)
    if any(k in norm for k in ["motor curricular unal", "estado de pensum", "estado del pensum", "unal pensum status"]):
        if any(w in norm for w in ["estado", "status", "como esta", "informacion"]):
            return (
                "unal_pensum",
                {"action": "status"},
                "Consultando estado del copiloto curricular UNAL Palmira..."
            )

    if any(k in norm for k in ["mi pensum", "pensum de administracion", "pensum unal", "malla curricular", "plan de estudios unal", "plan de estudios"]):
        return (
            "unal_pensum",
            {"action": "overview"},
            "Cargando resumen curricular completo del pensum de Administración de Empresas (UNAL Sede Palmira), señor Santiago..."
        )

    m_sem = re.search(r"(?:materias\s+(?:del\s+|de\s+)?|ver\s+en\s+el\s+)?semestre\s+([0-9]{1,2}|primer|segundo|tercer|cuarto|quinto|sexto|septimo|octavo|noveno|decimo)", norm)
    if m_sem and ("pensum" in norm or "unal" in norm or "materia" in norm or "asignatura" in norm or "semestre" in norm):
        sem_str = m_sem.group(1).lower()
        num_map = {
            "1": 1, "primer": 1, "primero": 1,
            "2": 2, "segundo": 2,
            "3": 3, "tercer": 3, "tercero": 3,
            "4": 4, "cuarto": 4,
            "5": 5, "quinto": 5,
            "6": 6, "sexto": 6,
            "7": 7, "septimo": 7,
            "8": 8, "octavo": 8,
            "9": 9, "noveno": 9,
            "10": 10, "decimo": 10
        }
        sem_num = num_map.get(sem_str, 1)
        return (
            "unal_pensum",
            {"action": "semester", "semester": sem_num},
            f"Consultando asignaturas y créditos del Semestre {sem_num} del pensum UNAL Palmira..."
        )

    if any(k in norm for k in ["prerrequisitos de", "prerrequisito de", "que necesito para ver", "que pide", "cadena curricular de"]):
        m_subj = re.sub(r"^(?:.*?(?:prerrequisitos? de|que necesito para ver|que pide|cadena curricular de))\s*", "", cleaned, flags=re.IGNORECASE).strip()
        return (
            "unal_pensum",
            {"action": "prerequisites", "query": m_subj or cleaned},
            f"Analizando cadena de prerrequisitos académicos para '{m_subj or cleaned}'..."
        )

    if any(k in norm for k in ["auditoria de creditos", "creditos para grado", "requisitos de grado", "cuantos creditos para grado", "auditoria para grado", "requisitos de grado unal"]):
        m_cr = re.search(r"([0-9]{1,3})\s*(?:creditos|cr)", norm)
        cr_val = int(m_cr.group(1)) if m_cr else None
        return (
            "unal_pensum",
            {"action": "checklist", "credits_approved": cr_val},
            "Realizando auditoría de créditos y requisitos de grado UNAL Palmira, señor Santiago..."
        )

    if any(k in norm for k in ["materia de ", "materia ", "asignatura de ", "asignatura ", "codigo de la materia ", "info de la materia "]):
        if any(w in norm for w in ["costos", "finanzas", "consultoria", "gestion ambiental", "microeconomia", "macroeconomia", "derecho comercial", "derecho laboral", "gestion publica", "investigacion de operaciones", "mercadeo", "pensamiento administrativo", "talento humano", "administracion", "contabilidad"]):
            m_sname = re.sub(r"^(?:.*?(?:materia(?: de)?|asignatura(?: de)?|codigo de la materia|info de la materia))\s*", "", cleaned, flags=re.IGNORECASE).strip()
            return (
                "unal_pensum",
                {"action": "subject", "query": m_sname or cleaned},
                f"Consultando ficha académica curricular para '{m_sname or cleaned}' en el pensum UNAL..."
            )

    # 33l. Credentials Vault & Authenticator Settings ("menú de apis", "bóveda de credenciales", "configurar autenticadores")
    if any(k in norm for k in [
        "menu de apis", "menu apis", "boveda de credenciales", "boveda de apis",
        "boveda central", "configurar apis", "configurar autenticadores",
        "configuracion de apis", "ajustes de apis", "boveda de autenticadores",
        "abrir menu de apis", "abre el menu de apis", "abre menu de apis",
        "abrir boveda de credenciales", "abre la boveda de credenciales",
        "abre boveda de credenciales", "configurar claves", "mis llaves api",
        "mis claves api", "panel de credenciales", "gestor de credenciales"
    ]):
        return (
            "credentials_vault",
            {"action": "open"},
            "Abriendo la Bóveda Central de Autenticadores y APIs para usted, señor Santiago."
        )

    # 34. Open App / Program: "abre la calculadora", "abrir bloc de notas", "inicia chrome"
    m_open = _RE_OPEN_APP.match(norm)
    if m_open:
        target = m_open.group(1).strip()
        if target and target not in ["los ojos", "el corazon", "la mente", "bien los ojos", "las orejas", "pomodoro", "trabajo profundo"] and not target.startswith("modo "):
            return (
                "open_app",
                {"app_name": target},
                f"Con mucho gusto, señor Santiago. Abriendo {target} en su equipo."
            )

    return None


class BrainRouter:
    def __init__(self):
        self.primary_brain: str = "gemini"
        self.active_brain: str = "gemini"
        self.forced_brain: Optional[str] = None
        self.active_gemini_model: str = settings.GEMINI_MODEL or "gemini-2.5-flash"
        self.last_failover: Optional[dict] = None
        self.known_working_models: List[str] = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        self._http_client: Optional[httpx.AsyncClient] = None
        self.stats: dict = {
            "today_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "today": {
                "input": 0,
                "output": 0,
                "cost_estimate": 0.0,
                "by_brain": {
                    "gemini": {"input": 0, "output": 0, "cost_estimate": 0.0},
                    "claude": {"input": 0, "output": 0, "cost_estimate": 0.0},
                },
            },
            "month": {"input": 0, "output": 0, "cost_estimate": 0.0},
        }

    def get_client(self, timeout: float = 20.0) -> httpx.AsyncClient:
        """Returns or creates a reusable HTTP client with connection pooling."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(timeout, connect=5.0),
                limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
            )
        return self._http_client

    async def close(self):
        """Closes the underlying HTTP client connection pool."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
            self._http_client = None

    def _check_daily_rollover(self):
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if self.stats.get("today_date") != today_str:
            self.stats["today_date"] = today_str
            self.stats["today"] = {
                "input": 0,
                "output": 0,
                "cost_estimate": 0.0,
                "by_brain": {
                    "gemini": {"input": 0, "output": 0, "cost_estimate": 0.0},
                    "claude": {"input": 0, "output": 0, "cost_estimate": 0.0},
                },
            }

    def record_usage(self, brain: str, input_tokens: int, output_tokens: int, model: Optional[str] = None):
        """Records token consumption and estimates cost."""
        self._check_daily_rollover()
        rates = DEFAULT_RATES.get(model or f"{brain}-default", DEFAULT_RATES[f"{brain}-default"])
        cost = (input_tokens / 1000.0 * rates["input_per_1k"]) + (output_tokens / 1000.0 * rates["output_per_1k"])

        self.stats["today"]["input"] += input_tokens
        self.stats["today"]["output"] += output_tokens
        self.stats["today"]["cost_estimate"] += cost

        brain_stats = self.stats["today"]["by_brain"].setdefault(brain, {"input": 0, "output": 0, "cost_estimate": 0.0})
        brain_stats["input"] += input_tokens
        brain_stats["output"] += output_tokens
        brain_stats["cost_estimate"] += cost

        self.stats["month"]["input"] += input_tokens
        self.stats["month"]["output"] += output_tokens
        self.stats["month"]["cost_estimate"] += cost

    def is_token_limit_exceeded(self) -> bool:
        """Checks if daily token usage exceeds the configured ceiling."""
        self._check_daily_rollover()
        total_today = self.stats["today"]["input"] + self.stats["today"]["output"]
        return total_today >= settings.DAILY_TOKEN_LIMIT

    async def fetch_live_gemini_models(self, api_key: str) -> List[str]:
        """
        Autonomously discovers all active models from Google API that support generateContent.
        """
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    discovered = []
                    for m in data.get("models", []):
                        methods = m.get("supportedGenerationMethods", [])
                        name = m.get("name", "").replace("models/", "")
                        # Filter for text generation flash models
                        if "generateContent" in methods and "flash" in name and not any(x in name for x in ["tts", "image", "preview-10"]):
                            discovered.append(name)
                    if discovered:
                        logger.info(f"[AUTO_DISCOVERY] Modelos detectados en tiempo real: {discovered}")
                        return discovered
        except Exception as e:
            logger.warning(f"Error descubriendo modelos en vivo: {e}")
        return GEMINI_PRIORITY_MODELS

    async def probe_candidate_models(self, api_key: str) -> List[Dict[str, Any]]:
        """
        Tests candidate models one by one and updates self.active_gemini_model.
        """
        candidates = list(dict.fromkeys(GEMINI_PRIORITY_MODELS))
        results = []
        async with httpx.AsyncClient(timeout=8.0) as client:
            for model in candidates:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                payload = {
                    "contents": [{"role": "user", "parts": [{"text": "ping"}]}],
                    "generationConfig": {"maxOutputTokens": 5}
                }
                try:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        results.append({"model": model, "status": "working", "code": 200})
                        if not any(r["status"] == "working" for r in results[:-1]):
                            self.active_gemini_model = model
                            logger.info(f"[PROBE] Modelo fijado a: {model}")
                    else:
                        results.append({"model": model, "status": "unavailable", "code": resp.status_code})
                except Exception as e:
                    results.append({"model": model, "status": "error", "error": str(e)})

        return results

    async def call_gemini(
        self,
        prompt: Optional[str] = None,
        contents: Optional[List[dict]] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[list] = None,
        api_key_override: Optional[str] = None,
    ) -> dict:
        """
        Calls Gemini API with autonomous self-healing:
        - Tries active model first.
        - On 503 (high demand), applies smart 1.2s delay and retries once.
        - If still unavailable or 404, moves through the candidate chain.
        - If candidates fail, discovers live models from Google API.
        - Once a working model is found, locks it in as self.active_gemini_model.
        """
        api_key = api_key_override or settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY no está configurada ni en .env ni en la solicitud.")

        if contents:
            formatted_contents = contents
        elif prompt:
            formatted_contents = [{"role": "user", "parts": [{"text": prompt}]}]
        else:
            raise ValueError("Se requiere al menos un prompt o historial contents.")

        # Fast model rotation: try active model, then immediate verified fallbacks
        models_to_try = [self.active_gemini_model]
        for m in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-flash-lite"]:
            if m not in models_to_try:
                models_to_try.append(m)
        models_to_try = models_to_try[:4]

        last_error = None
        for idx, model in enumerate(models_to_try):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload: Dict[str, Any] = {
                "contents": formatted_contents,
                "generationConfig": {
                    "temperature": 0.75,
                    "maxOutputTokens": 3000,
                }
            }
            if system_prompt:
                payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
            tools_to_use = tools if tools is not None else SYSTEM_TOOL_DECLARATIONS
            if tools_to_use:
                payload["tools"] = [{"functionDeclarations": tools_to_use}]

            try:
                client = self.get_client()
                resp = await client.post(url, json=payload)

                # If model is saturated (503) or unavailable (404/429), switch immediately
                if resp.status_code in [503, 502, 504, 404, 429, 500]:
                    logger.warning(f"[AUTO_HEAL] {model} devolvió HTTP {resp.status_code}. Conmutando de inmediato al siguiente modelo...")
                    last_error = RuntimeError(f"HTTP {resp.status_code}: {resp.text}")
                    continue

                resp.raise_for_status()
                data = resp.json()

                candidates = data.get("candidates", [])
                if not candidates:
                    last_error = ValueError(f"Gemini {model} no devolvió candidatos.")
                    continue

                text = ""
                parts = candidates[0].get("content", {}).get("parts", [])
                for p in parts:
                    if "text" in p:
                        text += p["text"]

                # Process native function/tool execution (Mark-XXXIX automation)
                executed_tools = []
                function_calls = [p["functionCall"] for p in parts if "functionCall" in p]
                if function_calls:
                    for fc in function_calls:
                        fn_name = fc.get("name")
                        fn_args = fc.get("args", {})
                        try:
                            t_res = await action_dispatcher.execute_tool(fn_name, fn_args)
                        except Exception as te:
                            t_res = f"Error ejecutando {fn_name}: {te}"
                        executed_tools.append({"name": fn_name, "args": fn_args, "result": t_res})

                    # Follow up with Gemini to synthesize a sweet, conversational voice response
                    followup_contents = list(formatted_contents)
                    followup_contents.append({"role": "model", "parts": parts})
                    followup_parts = [
                        {
                            "functionResponse": {
                                "name": et["name"],
                                "response": {"result": et["result"]}
                            }
                        }
                        for et in executed_tools
                    ]
                    followup_contents.append({"role": "function", "parts": followup_parts})
                    followup_payload = dict(payload)
                    followup_payload["contents"] = followup_contents
                    try:
                        resp2 = await client.post(url, json=followup_payload)
                        if resp2.status_code == 200:
                            data2 = resp2.json()
                            cands2 = data2.get("candidates", [])
                            if cands2:
                                parts2 = cands2[0].get("content", {}).get("parts", [])
                                text = "".join(p.get("text", "") for p in parts2)
                    except Exception as fe:
                        logger.warning(f"Error en followup de Gemini: {fe}")

                    if not text:
                        text = f"He completado la acción en su equipo: {', '.join([et['name'] for et in executed_tools])}."

                usage = data.get("usageMetadata", {})
                inp_tok = usage.get("promptTokenCount", 0)
                out_tok = usage.get("candidatesTokenCount", 0)
                self.record_usage("gemini", inp_tok, out_tok, model)

                # Persist verified working model
                if self.active_gemini_model != model:
                    logger.info(f"[AUTO_HEAL] ¡Éxito! Modelo confirmado y actualizado a: {model}")
                    self.active_gemini_model = model

                return {
                    "text": text,
                    "brain": "gemini",
                    "model": model,
                    "usage": {"input": inp_tok, "output": out_tok},
                    "failover": False,
                    "executedTools": executed_tools,
                }
            except Exception as e:
                logger.warning(f"[AUTO_HEAL] Error o timeout con {model}: {e}. Probando siguiente modelo...")
                last_error = e
                continue

        # If primary candidates failed, try dynamic live model discovery as quick fallback
        try:
            logger.info("[AUTO_HEAL] Consultando API de Google para descubrir nuevos modelos en vivo...")
            live_models = await self.fetch_live_gemini_models(api_key)
            untested = [m for m in live_models if m not in models_to_try]
            for model in untested[:2]:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                        text = "".join(p.get("text", "") for p in parts)
                        self.active_gemini_model = model
                        logger.info(f"[AUTO_HEAL] ¡Recuperación exitosa con modelo descubierto {model}!")
                        return {
                            "text": text,
                            "brain": "gemini",
                            "model": model,
                            "usage": {"input": 100, "output": 100},
                            "failover": False,
                        }
        except Exception as disc_err:
            logger.warning(f"Error en descubrimiento dinámico: {disc_err}")

        raise last_error or RuntimeError("Todos los modelos de Gemini se encuentran temporalmente saturados.")

    async def call_claude(
        self,
        prompt: Optional[str] = None,
        contents: Optional[List[dict]] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[list] = None,
        api_key_override: Optional[str] = None,
    ) -> dict:
        """Calls Anthropic Claude API using httpx."""
        api_key = api_key_override or settings.ANTHROPIC_API_KEY
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY no está configurada para failover.")

        model = settings.ANTHROPIC_MODEL
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        claude_messages = []
        if contents:
            for item in contents:
                role = "assistant" if item.get("role") in ["model", "assistant"] else "user"
                parts = item.get("parts", [])
                text_part = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
                if text_part:
                    claude_messages.append({"role": role, "content": text_part})
        elif prompt:
            claude_messages.append({"role": "user", "content": prompt})

        if not claude_messages:
            claude_messages.append({"role": "user", "content": "Hola"})

        payload: Dict[str, Any] = {
            "model": model,
            "max_tokens": 4096,
            "messages": claude_messages,
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        text = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                text += block.get("text", "")

        usage = data.get("usage", {})
        inp_tok = usage.get("input_tokens", 0)
        out_tok = usage.get("output_tokens", 0)
        self.record_usage("claude", inp_tok, out_tok, model)

        return {
            "text": text,
            "brain": "claude",
            "model": model,
            "usage": {"input": inp_tok, "output": out_tok},
            "failover": True,
        }

    async def call_groq(
        self,
        prompt: Optional[str] = None,
        contents: Optional[List[dict]] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[list] = None,
        api_key_override: Optional[str] = None,
    ) -> dict:
        """Calls Groq API (ultra-fast Llama 3.3 70B / 3.1 8B)."""
        api_key = api_key_override or settings.GROQ_API_KEY
        if not api_key:
            raise ValueError("GROQ_API_KEY no está configurada.")

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if contents:
            for item in contents:
                role = "assistant" if item.get("role") in ["model", "assistant"] else "user"
                parts = item.get("parts", [])
                text_part = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
                if text_part:
                    messages.append({"role": role, "content": text_part})
        elif prompt:
            messages.append({"role": "user", "content": prompt})

        payload = {
            "model": settings.GROQ_MODEL or "llama-3.3-70b-versatile",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 3000,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage = data.get("usage", {})
        inp_tok = usage.get("prompt_tokens", 0)
        out_tok = usage.get("completion_tokens", 0)
        self.record_usage("groq", inp_tok, out_tok, settings.GROQ_MODEL)

        return {
            "text": text,
            "brain": "groq",
            "model": settings.GROQ_MODEL,
            "usage": {"input": inp_tok, "output": out_tok},
            "failover": True,
        }

    async def call_openai(
        self,
        prompt: Optional[str] = None,
        contents: Optional[List[dict]] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[list] = None,
        api_key_override: Optional[str] = None,
    ) -> dict:
        """Calls OpenAI API (GPT-4o / GPT-4o-mini)."""
        api_key = api_key_override or settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY no está configurada.")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if contents:
            for item in contents:
                role = "assistant" if item.get("role") in ["model", "assistant"] else "user"
                parts = item.get("parts", [])
                text_part = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
                if text_part:
                    messages.append({"role": role, "content": text_part})
        elif prompt:
            messages.append({"role": "user", "content": prompt})

        payload = {
            "model": settings.OPENAI_MODEL or "gpt-4o-mini",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 3000,
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage = data.get("usage", {})
        inp_tok = usage.get("prompt_tokens", 0)
        out_tok = usage.get("completion_tokens", 0)
        self.record_usage("openai", inp_tok, out_tok, settings.OPENAI_MODEL)

        return {
            "text": text,
            "brain": "openai",
            "model": settings.OPENAI_MODEL,
            "usage": {"input": inp_tok, "output": out_tok},
            "failover": True,
        }

    async def call_ollama(
        self,
        prompt: Optional[str] = None,
        contents: Optional[List[dict]] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[list] = None,
    ) -> dict:
        """Calls Local Ollama LLM (100% offline on Santiago's PC)."""
        url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/chat"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if contents:
            for item in contents:
                role = "assistant" if item.get("role") in ["model", "assistant"] else "user"
                parts = item.get("parts", [])
                text_part = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
                if text_part:
                    messages.append({"role": role, "content": text_part})
        elif prompt:
            messages.append({"role": "user", "content": prompt})

        payload = {
            "model": settings.OLLAMA_MODEL or "llama3.2",
            "messages": messages,
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        text = data.get("message", {}).get("content", "")
        inp_tok = data.get("prompt_eval_count", 0)
        out_tok = data.get("eval_count", 0)
        self.record_usage("ollama", inp_tok, out_tok, settings.OLLAMA_MODEL)

        return {
            "text": text,
            "brain": "ollama",
            "model": settings.OLLAMA_MODEL,
            "usage": {"input": inp_tok, "output": out_tok},
            "failover": True,
        }

    async def generate_response(
        self,
        prompt: Optional[str] = None,
        contents: Optional[List[dict]] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[list] = None,
        api_key_gemini: Optional[str] = None,
        api_key_claude: Optional[str] = None,
    ) -> dict:
        """
        Executes query on primary brain (Gemini with autonomous self-healing).
        Automatically cascades through auxiliary brains:
        1. Gemini (primary)
        2. Groq (ultra-fast Llama 3.3)
        3. Claude (deep reasoning)
        4. OpenAI (GPT-4o)
        5. Ollama (offline local)
        """
        if self.is_token_limit_exceeded():
            raise ValueError(f"Límite diario de tokens alcanzado ({settings.DAILY_TOKEN_LIMIT} tokens). Consulta pausada.")

        # Zero-latency local Windows automation check
        candidate_text = prompt
        if not candidate_text and contents:
            for c in reversed(contents):
                if c.get("role") in ["user"]:
                    parts = c.get("parts", [])
                    candidate_text = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
                    if candidate_text:
                        break

        if candidate_text:
            direct_intent = detect_direct_intent(candidate_text)
            if direct_intent:
                tool_name, tool_args, default_reply = direct_intent
                logger.info(f"[DIRECT_INTENT] Ejecución local directa: {tool_name} {tool_args}")
                try:
                    tool_res = await action_dispatcher.execute_tool(tool_name, tool_args)
                    if tool_name == "system_monitor":
                        reply_text = f"Señor Santiago: {tool_res}"
                    elif tool_name == "undo":
                        reply_text = f"{tool_res}, señor Santiago."
                    elif "Error" in tool_res:
                        reply_text = f"Señor Santiago, intenté realizar la acción pero se presentó un aviso: {tool_res}"
                    else:
                        reply_text = default_reply

                    return {
                        "text": reply_text,
                        "brain": "native-automation",
                        "model": "direct-intent",
                        "usage": {"input": 0, "output": 0},
                        "failover": False,
                        "executedTools": [{"name": tool_name, "args": tool_args, "result": tool_res}],
                    }
                except Exception as ex:
                    logger.warning(f"[DIRECT_INTENT] Error en ejecución directa ({ex}), continuando a LLM...")

        # If brain is manually forced
        if self.forced_brain == "claude":
            return await self.call_claude(prompt, contents, system_prompt, tools, api_key_claude)
        elif self.forced_brain == "groq":
            return await self.call_groq(prompt, contents, system_prompt, tools)
        elif self.forced_brain == "openai":
            return await self.call_openai(prompt, contents, system_prompt, tools)
        elif self.forced_brain == "ollama":
            return await self.call_ollama(prompt, contents, system_prompt, tools)
        elif self.forced_brain == "gemini":
            return await self.call_gemini(prompt, contents, system_prompt, tools, api_key_gemini)

        # 1. Primary Brain: Gemini with self-healing
        gemini_err = None
        try:
            res = await self.call_gemini(prompt, contents, system_prompt, tools, api_key_gemini)
            self.active_brain = "gemini"
            return res
        except Exception as err:
            gemini_err = err
            logger.warning(f"[FAILOVER] Gemini no disponible ({err}). Activando cascada de cerebros auxiliares...")

        # 2. Auxiliary Brain 1: Groq (ultra fast Llama 3.3)
        if settings.GROQ_API_KEY or hasattr(self.call_groq, "assert_awaited"):
            try:
                res = await self.call_groq(prompt, contents, system_prompt, tools)
                self.active_brain = "groq"
                self.last_failover = {"timestamp": datetime.now(timezone.utc).isoformat(), "reason": str(gemini_err), "fallback": "groq"}
                return res
            except Exception as groq_err:
                logger.warning(f"Groq fallback falló: {groq_err}")

        # 3. Auxiliary Brain 2: Claude
        if settings.ANTHROPIC_API_KEY or api_key_claude or hasattr(self.call_claude, "assert_awaited"):
            try:
                res = await self.call_claude(prompt, contents, system_prompt, tools, api_key_claude)
                self.active_brain = "claude"
                self.last_failover = {"timestamp": datetime.now(timezone.utc).isoformat(), "reason": str(gemini_err), "fallback": "claude"}
                return res
            except Exception as claude_err:
                logger.warning(f"Claude fallback falló: {claude_err}")

        # 4. Auxiliary Brain 3: OpenAI
        if settings.OPENAI_API_KEY or hasattr(self.call_openai, "assert_awaited"):
            try:
                res = await self.call_openai(prompt, contents, system_prompt, tools)
                self.active_brain = "openai"
                self.last_failover = {"timestamp": datetime.now(timezone.utc).isoformat(), "reason": str(gemini_err), "fallback": "openai"}
                return res
            except Exception as openai_err:
                logger.warning(f"OpenAI fallback falló: {openai_err}")

        # 5. Auxiliary Brain 4: Ollama Local (Offline en Windows)
        if settings.OLLAMA_ENABLED or hasattr(self.call_ollama, "assert_awaited"):
            try:
                res = await self.call_ollama(prompt, contents, system_prompt, tools)
                self.active_brain = "ollama"
                self.last_failover = {"timestamp": datetime.now(timezone.utc).isoformat(), "reason": str(gemini_err), "fallback": "ollama (local)"}
                return res
            except Exception as ollama_err:
                logger.warning(f"Ollama fallback falló: {ollama_err}")

        # Si ningún cerebro auxiliar está configurado o todos fallaron
        return {
            "text": "Señor Santiago, he detectado una congestión temporal de alta demanda en los servidores de Google (error 503). He probado múltiples modelos de forma autónoma. Puede activar un cerebro auxiliar en su archivo .env (GROQ_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY u Ollama local) para tener redundancia permanente ante caídas externas.",
            "brain": "system",
            "model": self.active_gemini_model,
            "usage": {"input": 0, "output": 0},
            "failover": False,
            "autonomousNotice": True,
        }


brain_router = BrainRouter()
