"""
ActionDispatcher for JARVIS / Liseth.
Bridges Google Gemini AI function calling with native Windows system automation actions
ported from Mark-XXXIX:
- open_app: Opens applications, websites, and programs
- computer_settings: Volume, brightness, window state, media controls, system shortcuts
- computer_control: Keyboard, mouse, typing, clicking, and screenshots
- desktop_control: Desktop cleaning, organizing, and listing
- file_controller: File and folder operations (create, delete, move, copy, search)
- file_processor: Document and code analysis
- screen_process: Screen capture and visual inspection
- web_search: Web search
- youtube_video: Play and summarize YouTube videos
- reminder: Native Windows scheduled reminders
"""
import asyncio
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvis.action_dispatcher")

# Gemini Function Declarations for Tool Calling
SYSTEM_TOOL_DECLARATIONS: List[Dict[str, Any]] = [
    {
        "name": "open_app",
        "description": (
            "Opens any application or program on the user's computer. "
            "Use this whenever the user asks to open, launch, or start any app, "
            "website, or program (e.g. 'Spotify', 'Chrome', 'Calculadora', 'WhatsApp', 'Visual Studio Code', 'Word', 'Excel'). "
            "Always call this tool — never just claim you opened it."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "app_name": {
                    "type": "STRING",
                    "description": "Exact name of the application or program (e.g. 'spotify', 'chrome', 'calc', 'whatsapp', 'notepad')"
                }
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "computer_settings",
        "description": (
            "Controls computer settings and system state: volume (volume_up, volume_down, volume_mute, volume_set), "
            "brightness (brightness_up, brightness_down), window controls (minimize_window, maximize_window, full_screen, close_window), "
            "keyboard shortcuts (copy, paste, undo, redo, select_all, save_file), "
            "typing text on screen, lock screen (lock_screen), dark mode, media pause/play (pause_video), "
            "page reload/refresh, and system power (restart_computer, shutdown_computer). "
            "Always call this tool for system hardware and window adjustments."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {
                    "type": "STRING",
                    "description": "Action name, e.g. 'volume_up', 'volume_down', 'volume_mute', 'brightness_up', 'lock_screen', 'take_screenshot', 'minimize_window', 'maximize_window'"
                },
                "description": {
                    "type": "STRING",
                    "description": "Natural language description of what to do (e.g. 'sube el volumen', 'silencia el equipo', 'bloquea la pantalla')"
                },
                "value": {
                    "type": "STRING",
                    "description": "Optional value, e.g. volume percentage (0-100) or text to type"
                }
            },
            "required": []
        }
    },
    {
        "name": "computer_control",
        "description": (
            "Low-level mouse and keyboard automation: click at coordinates, double click, right click, "
            "type text, press hotkeys (e.g. win+d, alt+tab, ctrl+c), scroll screen, and capture screenshot."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {
                    "type": "STRING",
                    "description": "click | double_click | right_click | type | hotkey | press | scroll | screenshot | move | drag"
                },
                "x": {"type": "INTEGER", "description": "X screen coordinate"},
                "y": {"type": "INTEGER", "description": "Y screen coordinate"},
                "text": {"type": "STRING", "description": "Text to type"},
                "keys": {"type": "STRING", "description": "Keys separated by plus, e.g. 'win+d', 'ctrl+shift+esc'"},
                "direction": {"type": "STRING", "description": "up | down for scrolling"},
                "amount": {"type": "INTEGER", "description": "Scroll amount"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "desktop_control",
        "description": (
            "Controls and manages the desktop: organize files by type, clean temporary files, "
            "list all items on desktop, get desktop stats, or set custom wallpaper."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {
                    "type": "STRING",
                    "description": "organize | clean | list | stats | set_wallpaper"
                },
                "mode": {"type": "STRING", "description": "by_type | by_date | by_project (for organize)"},
                "image_path": {"type": "STRING", "description": "Path or URL for wallpaper"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "file_controller",
        "description": (
            "Manages files and directories on the computer: find/search files, create file/folder, "
            "delete file, move, copy, rename, read file content, write file content, and check disk usage."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {
                    "type": "STRING",
                    "description": "find | list | create_file | create_folder | delete | move | copy | rename | read | write | disk_usage"
                },
                "path": {"type": "STRING", "description": "File or folder path"},
                "name": {"type": "STRING", "description": "File name or search query to find"},
                "extension": {"type": "STRING", "description": "Extension filter (e.g. '.pdf', '.txt')"},
                "content": {"type": "STRING", "description": "Text content for writing/creating file"},
                "destination": {"type": "STRING", "description": "Target path for move/copy"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "web_search",
        "description": "Searches the web for up-to-date real-time information, news, documentation, or answers.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "Search query keywords"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "youtube_video",
        "description": "Controls YouTube: plays video directly in browser, summarizes content, or searches videos.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "play | summarize | get_info | trending (default: play)"},
                "query": {"type": "STRING", "description": "Song, artist, or video title to play or search"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "reminder",
        "description": "Sets a scheduled reminder or timer with notification.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "message": {"type": "STRING", "description": "Reminder text"},
                "time": {"type": "STRING", "description": "Time in HH:MM format (24h)"},
                "date": {"type": "STRING", "description": "Date in YYYY-MM-DD format (optional)"}
            },
            "required": ["message", "time"]
        }
    },
    {
        "name": "system_monitor",
        "description": "Checks real-time system performance and hardware telemetry: CPU load, RAM usage, GPU usage and temperature, and disk space.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "metric": {"type": "STRING", "description": "all | cpu | ram | gpu | temp | disk (default: all)"}
            },
            "required": []
        }
    },
    {
        "name": "undo",
        "description": "Reverses or undoes the most recent action performed by Liseth (volume changes, moved/created files, or system settings).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "undo | list (default: undo)"}
            },
            "required": []
        }
    },
    {
        "name": "video_player",
        "description": "Plays a video or music on the display/screen (YouTube search, YouTube link, direct media URL, or local video file) or controls playback (mute, unmute, stop).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "play | stop | mute | unmute (default: play)"},
                "source": {"type": "STRING", "description": "Song/video title to search, YouTube URL, or local video file path"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "background_monitor",
        "description": (
            "Monitors topics, news, or subjects in the background for updates and alerts. "
            "Allows adding, removing, or listing topics to monitor."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "add | remove | list"},
                "topic": {"type": "STRING", "description": "Topic or keyword to monitor"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "weather_report",
        "description": "Obtiene el clima en tiempo real, temperatura, probabilidad de lluvia y pronóstico para cualquier ciudad (por defecto Bogotá).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "city": {"type": "STRING", "description": "Nombre de la ciudad (ej. 'Bogotá', 'Medellín', 'Madrid')"}
            },
            "required": []
        }
    },
    {
        "name": "manage_commitments",
        "description": "Gestiona la lista autónoma de compromisos, promesas y tareas pendientes de Santiago: agregar, listar, completar o eliminar compromisos.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "add | list | complete | delete"},
                "text": {"type": "STRING", "description": "Descripción del compromiso o tarea"},
                "time": {"type": "STRING", "description": "Hora estimada en formato HH:MM (opcional)"},
                "date": {"type": "STRING", "description": "Fecha en formato YYYY-MM-DD (opcional)"},
                "id": {"type": "STRING", "description": "ID del compromiso para completar o eliminar"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "optimize_ram",
        "description": "Optimiza y libera la memoria RAM del sistema cerrando procesos saturados o vaciando conjuntos de trabajo (working sets).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "target_process": {"type": "STRING", "description": "Nombre opcional del proceso específico a cerrar (ej. 'chrome.exe')"}
            },
            "required": []
        }
    },
    {
        "name": "manage_calendar",
        "description": "Gestiona el calendario, reuniones y eventos de Santiago: agendar eventos, listar agenda del día o eliminar eventos.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "add | list | delete"},
                "summary": {"type": "STRING", "description": "Título o descripción de la reunión"},
                "start_time": {"type": "STRING", "description": "Hora (HH:MM) o fecha/hora ISO (ej. 2026-10-16T15:00:00)"},
                "meeting_link": {"type": "STRING", "description": "Enlace opcional de la videollamada (Meet, Zoom, Teams)"},
                "id": {"type": "STRING", "description": "ID del evento para eliminar"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "toggle_dnd",
        "description": "Activa o desactiva el Modo No Molestar (DND) / Silencio Total de Liseth para evitar interrupciones por voz.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "enabled": {"type": "BOOLEAN", "description": "True para activar silencio, False para desactivar"}
            },
            "required": []
        }
    },
    {
        "name": "screen_process",
        "description": "Captura y analiza visualmente la pantalla actual de Santiago usando visión multimodal de Gemini para explicar errores, bugs o contenido visual.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "Pregunta o instrucción sobre lo que se observa en pantalla"}
            },
            "required": []
        }
    },
    {
        "name": "deep_work",
        "description": "Inicia, detiene o consulta el estado del Modo Trabajo Profundo / Pomodoro de concentración con sincronización automática de No Molestar (DND).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "start | stop | status"},
                "duration": {"type": "INTEGER", "description": "Duración de la sesión en minutos (por defecto 50)"},
                "task": {"type": "STRING", "description": "Descripción u objetivo de la sesión de trabajo"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "smart_clipboard",
        "description": "Lee, analiza y explica el contenido del portapapeles de Santiago (errores, código, JSON o texto) y ofrece soluciones de depuración.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "analyze | read | fix"},
                "query": {"type": "STRING", "description": "Pregunta o instrucción opcional sobre el contenido copiado"}
            },
            "required": []
        }
    },
    {
        "name": "gmail_summary",
        "description": "Filtra inteligentemente la bandeja de entrada de Gmail de Santiago, separando correos urgentes que requieren atención de boletines o promociones.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "max_results": {"type": "INTEGER", "description": "Máximo número de correos a analizar (por defecto 10)"}
            },
            "required": []
        }
    },
    {
        "name": "shutdown_app",
        "description": "Cierra y detiene completamente la aplicación de Liseth, liberando recursos y finalizando todos los servicios en segundo plano a petición de Santiago.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "delay_seconds": {"type": "NUMBER", "description": "Segundos de retraso antes de salir para emitir despedida (por defecto 2.0)"}
            },
            "required": []
        }
    },
    {
        "name": "background_task",
        "description": "Gestiona tareas autónomas asíncronas en segundo plano mientras el usuario realiza otras actividades: encolar, consultar estado, listar o cancelar.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "list | status | create | cancel"},
                "title": {"type": "STRING", "description": "Título o descripción de la tarea a ejecutar"},
                "task_id": {"type": "STRING", "description": "ID de la tarea al consultar o cancelar"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "workspace_sentinel",
        "description": "Monitorea la salud de los proyectos y código de Santiago en segundo plano (sintaxis, compilación, integridad) y alerta de forma no invasiva si hay errores.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "status | scan | watch | list"},
                "path": {"type": "STRING", "description": "Ruta de la carpeta a escanear o vigilar"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "execute_routine",
        "description": "Ejecuta rutinas y flujos de trabajo automatizados para Santiago: 'morning' (clima, agenda, noticias, salud de proyectos), 'focus' (trabajo profundo, silencio DND), 'wrap_up' (cierre del día).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "routine": {"type": "STRING", "description": "morning | focus | wrap_up"},
                "action": {"type": "STRING", "description": "execute | list | history"}
            },
            "required": ["routine"]
        }
    },
    {
        "name": "daily_debrief",
        "description": "Presenta el reporte ejecutivo y balance de actividades resueltas en segundo plano por Liseth hoy (tareas, rutinas, auditorías de código y alertas).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "summary | list"}
            },
            "required": []
        }
    },
    {
        "name": "business_finance",
        "description": "Herramienta financiera y de administración de empresas: evaluación de proyectos (VAN/NPV, TIR/IRR, Payback, ROI, WACC), punto de equilibrio y matrices estratégicas (FODA, Canvas, PESTEL).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "operation": {"type": "STRING", "description": "van | tir | roi | punto_equilibrio | wacc | foda | canvas | pestel"},
                "rate": {"type": "NUMBER", "description": "Tasa de descuento exigida (%) para VAN"},
                "initial_investment": {"type": "NUMBER", "description": "Monto de inversión inicial"},
                "cash_flows": {"type": "ARRAY", "description": "Lista de flujos de caja proyectados", "items": {"type": "NUMBER"}},
                "fixed_costs": {"type": "NUMBER", "description": "Costos fijos para punto de equilibrio"},
                "price": {"type": "NUMBER", "description": "Precio unitario de venta"},
                "variable_cost": {"type": "NUMBER", "description": "Costo variable unitario"}
            },
            "required": ["operation"]
        }
    },
    {
        "name": "academic_helper",
        "description": "Asistente universitario y académico: generación de referencias y citas en Normas APA 7ª Edición (libros, artículos, páginas web, tesis) y esquemas para ensayos e informes.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "apa | estructura | normas"},
                "source_type": {"type": "STRING", "description": "book | journal | web | thesis"},
                "authors": {"type": "STRING", "description": "Nombres y apellidos de los autores"},
                "year": {"type": "STRING", "description": "Año de publicación"},
                "title": {"type": "STRING", "description": "Título de la obra o artículo"},
                "publisher": {"type": "STRING", "description": "Editorial o nombre del sitio web"},
                "journal": {"type": "STRING", "description": "Nombre de la revista científica"},
                "url": {"type": "STRING", "description": "Enlace web o DOI"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "data_dev_tools",
        "description": "Herramientas de productividad para programación y ciencia de datos: estadística descriptiva (media, mediana, desviación estándar), conversión JSON a tabla Markdown y CSV a sentencias SQL.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "operation": {"type": "STRING", "description": "stats | json_table | sql"},
                "data": {"type": "STRING", "description": "Datos a procesar (números separados por comas, JSON o CSV)"},
                "table_name": {"type": "STRING", "description": "Nombre de la tabla para sentencias SQL"}
            },
            "required": ["operation"]
        }
    },
    {
        "name": "reverse_engineer",
        "description": "Inspecciona y realiza ingeniería inversa sobre binarios ejecutables (EXE, DLL, ELF, Mach-O), paquetes (APK, ASAR, ZIP, WASM) y bases de datos. Extrae arquitectura, mitigaciones de seguridad (ASLR, DEP, CFG), entropía de Shannon (detección de empaquetadores/cifrado), cadenas e indicadores de compromiso.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "inspect | entropy | strings | asar | status"},
                "target_path": {"type": "STRING", "description": "Ruta absoluta o relativa del archivo binario a analizar"}
            },
            "required": []
        }
    },
    {
        "name": "ego_browser",
        "description": "Automatización web autónoma avanzada (Motor Ego Lite). Navega por la web en espacios de trabajo aislados (taskSpace) sin interrumpir las ventanas del usuario, genera snapshots semánticos ultraligeros de accesibilidad con referencias numeradas ([ref=1], [ref=2]), hace clics, llena formularios, toma capturas y ejecuta herramientas aprendidas (búsqueda limpia en Google, métricas de GitHub, etc.).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {
                    "type": "STRING",
                    "description": "status | navigate | snapshot | click | fill | screenshot | google | github | spaces | close_space | script"
                },
                "url": {"type": "STRING", "description": "URL de destino para navegar o capturar"},
                "target": {"type": "STRING", "description": "Número de referencia [ref=N] o selector del elemento sobre el cual actuar"},
                "value": {"type": "STRING", "description": "Texto a ingresar en el campo seleccionado"},
                "space": {"type": "STRING", "description": "Nombre del espacio de tarea aislado (taskSpace, por defecto 'default')"},
                "query": {"type": "STRING", "description": "Consulta de búsqueda (para Google o X)"},
                "repo": {"type": "STRING", "description": "Repositorio de GitHub en formato 'usuario/repo'"},
                "script": {"type": "STRING", "description": "Código JavaScript para ejecutar directamente en Ego Lite CLI"}
            },
            "required": []
        }
    },
    {
        "name": "vercel_skills",
        "description": "Herramientas de desarrollo Vercel Labs: despliegue instantáneo de aplicaciones web en Vercel (Next.js, Vite, React, Astro, HTML), auditoría de código con las 45+ mejores prácticas de ingeniería de React/Next.js (eliminación de waterfalls, bundle size, re-renders, JS performance), y auditoría de directrices de diseño web (Web Interface Guidelines, accesibilidad, estados de foco y UX móvil).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {
                    "type": "STRING",
                    "description": "status | deploy | audit_react | audit_design | framework | package"
                },
                "path": {"type": "STRING", "description": "Ruta del proyecto, archivo o directorio a procesar"},
                "code": {"type": "STRING", "description": "Fragmento de código React/Next.js/HTML a auditar directamente"},
                "prod": {"type": "BOOLEAN", "description": "True para desplegar directamente a producción"},
                "token": {"type": "STRING", "description": "Token opcional de autenticación de Vercel"}
            },
            "required": []
        }
    },
    {
        "name": "security_audit",
        "description": "Auditoría integral de ciberseguridad y análisis estático de vulnerabilidades (OWASP Top 10, CWE Top 25, SANS). Detecta inyecciones SQL/comandos/código, exposición de claves y secretos API (AWS, Google, GitHub, DBs), path traversal, deserialización insegura, vulnerabilidades en LLMs/IA y genera informes ejecutivos con puntuación de riesgo.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "status | audit | secrets | owasp"},
                "path": {"type": "STRING", "description": "Ruta del archivo o proyecto a auditar"},
                "code": {"type": "STRING", "description": "Fragmento de código a analizar directamente"}
            },
            "required": []
        }
    },
    {
        "name": "slopmonster",
        "description": "Detector de huellas de inteligencia artificial y humanizador de redacción (SlopMonster & Deslop). Evalúa textos contra 5 categorías de escritura robótica (vocabulario trillado, fórmulas sintácticas repetitivas, abuso de guiones largos em-dash, listas triples y conclusiones vacías) en español e inglés, asignando un puntaje de 0 a 5 y reescribiendo el texto en prosa humana, directa y profesional.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "status | deslop | humanize"},
                "text": {"type": "STRING", "description": "Texto, borrador, ensayo o correo a evaluar o humanizar"},
                "path": {"type": "STRING", "description": "Ruta de archivo de texto (.txt, .md, .html) a procesar"}
            },
            "required": []
        }
    },
    {
        "name": "git_sync",
        "description": "Sincronizador automático de código y repositorio con GitHub: detecta archivos modificados, crea commits semánticos y sube los cambios a la rama principal de https://github.com/santigamerxdyt/Liseth-AI. También gestiona el centinela en segundo plano.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "sync | status | start_watcher | stop_watcher"},
                "message": {"type": "STRING", "description": "Mensaje personalizado opcional para el commit de Git"}
            },
            "required": []
        }
    }
]


class ActionDispatcher:
    def __init__(self):
        self._actions_loaded = False

    async def execute_tool(self, name: str, args: Dict[str, Any]) -> str:
        """Executes a requested system tool asynchronously on the host PC."""
        logger.info(f"[ACTION] Ejecutando herramienta de sistema '{name}' con args: {args}")
        loop = asyncio.get_running_loop()

        try:
            if name == "open_app":
                from app.actions.open_app import open_app
                res = await loop.run_in_executor(None, lambda: open_app(parameters=args))
                return res or f"Aplicación {args.get('app_name')} iniciada exitosamente."

            elif name == "computer_settings":
                from app.actions.computer_settings import computer_settings
                res = await loop.run_in_executor(None, lambda: computer_settings(parameters=args))
                return res or "Ajuste de sistema completado."

            elif name == "computer_control":
                from app.actions.computer_control import computer_control
                res = await loop.run_in_executor(None, lambda: computer_control(parameters=args))
                return res or "Acción de control completada."

            elif name == "desktop_control":
                from app.actions.desktop import desktop_control
                res = await loop.run_in_executor(None, lambda: desktop_control(parameters=args))
                return res or "Acción en el escritorio completada."

            elif name == "file_controller":
                from app.actions.file_controller import file_controller
                res = await loop.run_in_executor(None, lambda: file_controller(parameters=args))
                return res or "Operación de archivos realizada con éxito."

            elif name == "file_processor":
                from app.actions.file_processor import file_processor
                res = await loop.run_in_executor(None, lambda: file_processor(parameters=args))
                return res or "Archivo procesado."

            elif name == "screen_process":
                from app.actions.screen_processor import screen_process
                if asyncio.iscoroutinefunction(screen_process):
                    res = await screen_process(parameters=args)
                else:
                    res = await loop.run_in_executor(None, lambda: screen_process(parameters=args))
                return res or "Pantalla capturada y analizada."

            elif name == "web_search":
                from app.actions.web_search import web_search
                res = await loop.run_in_executor(None, lambda: web_search(parameters=args))
                return res or "Búsqueda web completada."

            elif name == "youtube_video":
                from app.actions.youtube_video import youtube_video
                res = await loop.run_in_executor(None, lambda: youtube_video(parameters=args))
                return res or "Video solicitado en YouTube."

            elif name == "video_player":
                from app.actions.video_player import video_player
                res = await loop.run_in_executor(None, lambda: video_player(parameters=args))
                return res or "Reproduciendo video en pantalla."

            elif name == "system_monitor":
                def _get_telemetry():
                    import psutil
                    import os
                    cpu = psutil.cpu_percent(interval=None)
                    ram = psutil.virtual_memory().percent
                    drive = os.path.splitdrive(os.getcwd())[0] or "/"
                    disk = psutil.disk_usage(drive).percent if hasattr(psutil, "disk_usage") else 0
                    try:
                        from app.actions.system_monitor import _get_gpu_usage, _get_cpu_temp
                        gpu = _get_gpu_usage()
                        temp = _get_cpu_temp()
                    except Exception:
                        gpu, temp = -1.0, 0.0
                    gpu_str = f", GPU al {gpu:.0f}%" if gpu >= 0 else ""
                    temp_str = f", Temperatura {temp:.1f}°C" if temp > 0 else ""
                    return f"Telemetría actual del sistema: CPU al {cpu:.1f}%, RAM al {ram:.1f}%, Disco al {disk:.1f}%{gpu_str}{temp_str}."
                res = await loop.run_in_executor(None, _get_telemetry)
                return res

            elif name == "undo":
                from app.core.undo import undo_last, can_undo, history
                act = (args or {}).get("action", "undo")
                if act == "list":
                    h = history()
                    return f"Historial de acciones reversibles: {', '.join(h)}" if h else "No hay historial de acciones."
                if not can_undo():
                    return "No hay ninguna acción reciente que se pueda revertir."
                res = undo_last()
                return f"Acción deshecha con éxito: {res}"

            elif name == "reminder":
                from app.actions.reminder import reminder
                res = await loop.run_in_executor(None, lambda: reminder(parameters=args))
                return res or "Recordatorio programado."

            elif name == "background_monitor":
                from app.actions.background_monitor import add_monitor, remove_monitor, list_monitors
                act = (args or {}).get("action", "list")
                top = (args or {}).get("topic", "")
                if act == "add":
                    res = await loop.run_in_executor(None, lambda: add_monitor(top))
                    return res
                elif act == "remove":
                    res = await loop.run_in_executor(None, lambda: remove_monitor(top))
                    return res
                else:
                    mons = await loop.run_in_executor(None, list_monitors)
                    return f"Temas en monitoreo de noticias: {', '.join(mons)}" if mons else "No hay temas activos en monitoreo."

            elif name == "weather_report":
                from app.actions.weather_report import weather_action
                res = await loop.run_in_executor(None, lambda: weather_action(parameters=args))
                return res or "Reporte del clima obtenido."

            elif name == "manage_commitments":
                from app.services.commitment_service import commitment_service
                act = (args or {}).get("action", "list")
                if act == "add":
                    txt = (args or {}).get("text", "")
                    if not txt:
                        return "Debe especificar la descripción del compromiso."
                    due_t = (args or {}).get("time")
                    due_d = (args or {}).get("date")
                    item = commitment_service.add_commitment(text=txt, due_date=due_d, due_time=due_t)
                    return f"Compromiso guardado: '{item['text']}' para las {item['due_time']}."
                elif act in ["complete", "done"]:
                    target_id = (args or {}).get("id") or (args or {}).get("text", "")
                    ok = commitment_service.complete_commitment(target_id)
                    return "Compromiso marcado como completado." if ok else "No encontré el compromiso especificado."
                elif act in ["delete", "remove"]:
                    target_id = (args or {}).get("id") or (args or {}).get("text", "")
                    ok = commitment_service.delete_commitment(target_id)
                    return "Compromiso eliminado de la lista." if ok else "No encontré el compromiso a eliminar."
                else:
                    items = commitment_service.list_commitments(status="pending")
                    if not items:
                        return "No tiene compromisos pendientes en este momento, señor Santiago."
                    lines = ["Compromisos y tareas pendientes:"]
                    for it in items:
                        lines.append(f"- [{it['id']}] {it['text']} ({it.get('due_date')} {it.get('due_time')})")
                    return "\n".join(lines)

            elif name == "optimize_ram":
                from app.actions.system_monitor import optimize_memory
                target = (args or {}).get("target_process")
                res = await loop.run_in_executor(None, lambda: optimize_memory(target))
                return res

            elif name == "manage_calendar":
                from app.services.calendar_service import calendar_service
                act = (args or {}).get("action", "list")
                if act == "add":
                    summ = (args or {}).get("summary", "")
                    st = (args or {}).get("start_time", "")
                    if not summ or not st:
                        return "Debe especificar el título y la hora de inicio de la reunión."
                    link = (args or {}).get("meeting_link")
                    item = calendar_service.add_event(summary=summ, start_time=st, meeting_link=link)
                    link_msg = f" con enlace {link}" if link else ""
                    return f"Evento agendado con éxito: '{summ}' a las {st}{link_msg}."
                elif act in ["delete", "remove"]:
                    t_id = (args or {}).get("id", "")
                    ok = calendar_service.delete_event(t_id)
                    return "Evento eliminado del calendario." if ok else "No encontré el evento a eliminar."
                else:
                    return calendar_service.format_daily_agenda()

            elif name == "toggle_dnd":
                from app.services.heartbeat_service import heartbeat_service
                en = (args or {}).get("enabled")
                if en is None:
                    state = heartbeat_service.gatekeeper.toggle_dnd()
                else:
                    if en:
                        heartbeat_service.gatekeeper.enable_dnd()
                    else:
                        heartbeat_service.gatekeeper.disable_dnd()
                    state = heartbeat_service.gatekeeper.dnd_mode
                return f"Modo No Molestar {'activado' if state else 'desactivado'}, señor Santiago."

            elif name == "screen_process":
                from app.actions.screen_processor import screen_process
                res = await screen_process(parameters=args)
                return res or "Análisis visual de pantalla completado."

            elif name == "deep_work":
                from app.actions.deep_work import deep_work_action
                res = await loop.run_in_executor(None, lambda: deep_work_action(parameters=args))
                return res

            elif name == "smart_clipboard":
                from app.actions.clipboard_helper import smart_clipboard_action
                res = await smart_clipboard_action(parameters=args)
                return res or "Análisis del portapapeles completado."

            elif name == "gmail_summary":
                from app.connectors.google_workspace import google_connector
                max_r = int((args or {}).get("max_results") or 10)
                res = await google_connector.get_smart_inbox_summary(max_results=max_r)
                return res

            elif name == "shutdown_app":
                from app.actions.system_shutdown import shutdown_liseth
                delay = float((args or {}).get("delay_seconds") or 2.0)
                exec_exit = bool((args or {}).get("execute_exit", True))
                res = shutdown_liseth(delay_seconds=delay, execute_exit=exec_exit)
                return res

            elif name == "background_task":
                from app.actions.task_delegator import delegate_task
                res = await loop.run_in_executor(None, lambda: delegate_task(parameters=args))
                return res

            elif name == "workspace_sentinel":
                from app.actions.workspace_sentinel_action import workspace_sentinel_action
                res = await loop.run_in_executor(None, lambda: workspace_sentinel_action(parameters=args))
                return res

            elif name in ("execute_routine", "routine"):
                from app.actions.routine_action import routine_action
                res = await loop.run_in_executor(None, lambda: routine_action(parameters=args))
                return res

            elif name == "daily_debrief":
                from app.actions.daily_debrief_action import daily_debrief_action
                res = await loop.run_in_executor(None, lambda: daily_debrief_action(parameters=args))
                return res

            elif name in ("business_finance", "finance", "business"):
                from app.actions.business_finance import business_finance_action
                res = await loop.run_in_executor(None, lambda: business_finance_action(parameters=args))
                return res

            elif name in ("academic_helper", "academic", "apa"):
                from app.actions.academic_helper import academic_helper_action
                res = await loop.run_in_executor(None, lambda: academic_helper_action(parameters=args))
                return res

            elif name in ("data_dev_tools", "data_tools", "dev_tools"):
                from app.actions.data_dev_tools import data_dev_tools_action
                res = await loop.run_in_executor(None, lambda: data_dev_tools_action(parameters=args))
                return res

            elif name in ("admin_privileges", "system_privileges", "admin_status"):
                from app.core.admin import get_elevation_status
                status = get_elevation_status()
                if status["is_admin"]:
                    return "Privilegios de Windows: ADMINISTRADOR (Acceso Total al Sistema). Liseth cuenta con control total sobre servicios, hardware y procesos."
                else:
                    return "Privilegios de Windows: USUARIO ESTANDAR. Para habilitar acceso total, inicie Liseth desde iniciar_liseth.bat con elevación UAC."

            elif name in ("reverse_engineer", "reverse_engineering", "rea", "inspect_binary"):
                from app.actions.reverse_engineering_action import reverse_engineering_action
                res = await loop.run_in_executor(None, lambda: reverse_engineering_action(parameters=args))
                return res

            elif name in ("ego_browser", "ego", "browser_automation", "fast_browser", "ego_lite"):
                from app.actions.ego_browser_action import ego_browser_action
                res = await loop.run_in_executor(None, lambda: ego_browser_action(parameters=args))
                return res

            elif name in ("vercel_skills", "vercel", "react_best_practices", "web_design_guidelines", "deploy_app", "vercel_deploy"):
                from app.actions.vercel_skills_action import vercel_skills_action
                res = await loop.run_in_executor(None, lambda: vercel_skills_action(parameters=args))
                return res

            elif name in ("security_audit", "security", "vulnerability_scan", "cve_audit", "owasp_audit"):
                from app.actions.security_audit_action import security_audit_action
                res = await loop.run_in_executor(None, lambda: security_audit_action(parameters=args))
                return res

            elif name in ("slopmonster", "deslop", "humanize_copy", "anti_slop", "humanize_text"):
                from app.actions.slopmonster_action import slopmonster_action
                res = await loop.run_in_executor(None, lambda: slopmonster_action(parameters=args))
                return res

            elif name in ("git_sync", "sync_github", "github_sync", "git_push", "repo_sync"):
                from app.actions.git_sync_action import git_sync_action
                res = await loop.run_in_executor(None, lambda: git_sync_action(parameters=args))
                return res

            else:
                return f"Herramienta '{name}' no reconocida."

        except Exception as e:
            logger.error(f"[ACTION_ERR] Error ejecutando '{name}': {e}", exc_info=True)
            return f"Error ejecutando '{name}': {str(e)}"


action_dispatcher = ActionDispatcher()
