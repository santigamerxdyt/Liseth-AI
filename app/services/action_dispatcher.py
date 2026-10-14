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

            elif name == "reminder":
                from app.actions.reminder import reminder
                res = await loop.run_in_executor(None, lambda: reminder(parameters=args))
                return res or "Recordatorio programado."

            else:
                return f"Herramienta '{name}' no reconocida."

        except Exception as e:
            logger.error(f"[ACTION_ERR] Error ejecutando '{name}': {e}", exc_info=True)
            return f"Error ejecutando '{name}': {str(e)}"


action_dispatcher = ActionDispatcher()
