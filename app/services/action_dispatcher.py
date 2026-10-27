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
import json
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
    },
    {
        "name": "academic_research",
        "description": "Investigación académica y científica: busca artículos y preprints en OpenAlex y arXiv (250M+ papers), extrae resúmenes, DOIs y PDFs abiertos, elabora revisiones sistemáticas de literatura (Estado del Arte) y genera referencias bibliográficas y citas parentéticas/narrativas en Normas APA 7ª Edición.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "search | literature_review | status"},
                "query": {"type": "STRING", "description": "Tema de investigación académica, palabras clave o autor"},
                "limit": {"type": "INTEGER", "description": "Número máximo de artículos a recuperar (por defecto 5)"}
            },
            "required": []
        }
    },
    {
        "name": "business_strategy",
        "description": "Estrategia corporativa y finanzas avanzadas para Administración de Empresas: matrices estratégicas (Matriz FODA/SWOT con cruces FO, FA, DO, DA; 5 Fuerzas de Michael Porter; PESTEL; Business Model Canvas de 9 bloques de Osterwalder) y modelos financieros cuantitativos (proyección de Flujo de Caja Libre FCF a N años, tablas de amortización de préstamos en Sistema Francés y Alemán, y cálculo del Costo Promedio Ponderado de Capital WACC).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "foda | porter | canvas | cash_flow | amortization | wacc | status"},
                "organization": {"type": "STRING", "description": "Nombre de la empresa, proyecto o caso de estudio para FODA o Canvas"},
                "industry": {"type": "STRING", "description": "Sector industrial o de mercado para análisis Porter o PESTEL"},
                "revenue": {"type": "NUMBER", "description": "Ingreso base proyectado para flujo de caja"},
                "growth": {"type": "NUMBER", "description": "Tasa de crecimiento anual esperada (ejemplo: 0.15 para 15%)"},
                "margin": {"type": "NUMBER", "description": "Margen operativo EBIT esperado (ejemplo: 0.25 para 25%)"},
                "principal": {"type": "NUMBER", "description": "Monto del crédito o préstamo a amortizar"},
                "rate": {"type": "NUMBER", "description": "Tasa de interés anual en porcentaje (ejemplo: 18.0)"},
                "months": {"type": "INTEGER", "description": "Plazo de amortización en meses (ejemplo: 12)"},
                "system": {"type": "STRING", "description": "frances (cuota fija) | aleman (amortización constante)"},
                "equity": {"type": "NUMBER", "description": "Patrimonio de accionistas para WACC"},
                "debt": {"type": "NUMBER", "description": "Deuda financiera para WACC"},
                "ke": {"type": "NUMBER", "description": "Costo del patrimonio en % para WACC"},
                "kd": {"type": "NUMBER", "description": "Costo de la deuda en % para WACC"}
            },
            "required": []
        }
    },
    {
        "name": "data_ml_toolkit",
        "description": "Ciencia de datos, analítica y Machine Learning: perfilamiento y auto-limpieza de datasets tabulares/CSV (detección de nulos, inconsistencias y outliers por rango intercuartil IQR), estadística descriptiva e inferencial (matriz de correlación de Pearson), regresión lineal por mínimos cuadrados OLS (con R², MSE, RMSE y pronóstico), pronóstico de series de tiempo (suavizamiento exponencial) y generador de pipelines de código Python (Pandas y Scikit-Learn).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "profile | regression | forecast | code | status"},
                "data": {"type": "STRING", "description": "Datos CSV o serie numérica a perfilar"},
                "x": {"type": "STRING", "description": "Valores numéricos de variable independiente X separados por coma"},
                "y": {"type": "STRING", "description": "Valores numéricos de variable dependiente Y separados por coma"},
                "predict_x": {"type": "NUMBER", "description": "Valor de X para el cual se desea pronosticar Y"},
                "series": {"type": "STRING", "description": "Valores históricos de serie de tiempo separados por coma"},
                "periods": {"type": "INTEGER", "description": "Períodos hacia el futuro a proyectar"},
                "task": {"type": "STRING", "description": "Tipo de modelo para código Python: classification | regression | clustering"}
            },
            "required": []
        }
    },
    {
        "name": "workspace_automation",
        "description": "Automatización ofimática y productividad ejecutiva: generador bilingüe de fórmulas complejas de Excel y Google Sheets (BUSCARX/XLOOKUP, INDICE/COINCIDIR, SUMAR.SI.CONJUNTO, matrices dinámicas y funciones financieras), generador de arquitecturas y esquemas estructurados para informes de consultoría gerencial y ensayos universitarios, y diseñador de diapositivas ejecutivas con notas de orador.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "excel_formula | report_blueprint | presentation_deck | status"},
                "query": {"type": "STRING", "description": "Descripción del requerimiento o cálculo que se desea en Excel/Sheets"},
                "title": {"type": "STRING", "description": "Título o tema del informe, ensayo o presentación"},
                "type": {"type": "STRING", "description": "consultoria | ensayo | academico"},
                "slides": {"type": "INTEGER", "description": "Cantidad de diapositivas para la presentación"}
            },
            "required": []
        }
    },
    {
        "name": "unal_pensum",
        "description": "Copiloto académico y curricular especializado para el pensum de Administración de Empresas de la Universidad Nacional de Colombia (UNAL) - Sede Palmira (Acuerdo 19 de 2012 / Acuerdo 033 de 2007). Consulta asignaturas (códigos SIA, créditos, tipología), prerrequisitos, cadenas curriculares, núcleos temáticos, marcos normativos colombianos (CST, DIAN, Ley 80/93, Ley 99/93, etc.), fórmulas financieras y de costos, semestres (1 al 10) y auditoría de créditos para grado (166 créditos totales, 68 cr para Consultoría, 78 cr para Trabajo de Grado).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {
                    "type": "STRING",
                    "description": "overview | subject | prerequisites | semester | checklist | normative | status"
                },
                "query": {
                    "type": "STRING",
                    "description": "Nombre o código SIA de la asignatura (ej: Costos, Consultoría, 5000869, Finanzas, Microeconomía) o marco temático"
                },
                "semester": {
                    "type": "INTEGER",
                    "description": "Número de semestre (1 al 10)"
                },
                "credits_approved": {
                    "type": "INTEGER",
                    "description": "Créditos disciplinares o totales aprobados para auditoría de grado"
                }
            },
            "required": []
        }
    },
    {
        "name": "credentials_vault",
        "description": "Abre la Bóveda Central de Autenticadores y APIs de Liseth para configurar claves de API (Gemini, Claude, Groq, OpenAI, ElevenLabs, Telegram, GitHub, WhatsApp, Google OAuth, etc.).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "open | test | status"}
            },
            "required": []
        }
    },
    {
        "name": "nfc_contactless",
        "description": "Ecosistema NFC, Pagos por Contacto y Facturación Electrónica (Contactless, Beam & Invoicing): genera cobros tokenizados por proximidad (Bre-B Interoperable Colombia, Nequi, Daviplata, tarjetas contactless y cripto), emite facturas electrónicas pro-forma DIAN con hash CUFE y desglose de IVA/Retefuente, convierte divisas (COP, USD, EUR, USDT, BTC, ETH), transmite tarjetas de contacto digital vCard 3.0, valida llaves de seguridad NFC para desbloqueo por proximidad y consulta el libro contable de transacciones.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {
                    "type": "STRING",
                    "description": "status | payment_request | beam_vcard | read_tag | invoice | convert | badge | history | clear_history"
                },
                "amount": {"type": "NUMBER", "description": "Monto para el cobro, factura o conversión de divisas (ej: 25000)"},
                "currency": {"type": "STRING", "description": "Moneda: COP, USD, EUR, USDT, BTC, ETH (por defecto COP)"},
                "concept": {"type": "STRING", "description": "Concepto o descripción del cobro, factura o servicio"},
                "recipient": {"type": "STRING", "description": "Nombre del destinatario, cliente o comercio"},
                "client_id": {"type": "STRING", "description": "Documento o NIT del cliente para facturación"},
                "method": {"type": "STRING", "description": "bre_b | nequi | daviplata | card | crypto"},
                "from_currency": {"type": "STRING", "description": "Moneda de origen para conversión (ej: USD)"},
                "to_currency": {"type": "STRING", "description": "Moneda de destino para conversión (ej: COP)"},
                "name": {"type": "STRING", "description": "Nombre completo para la tarjeta digital vCard"},
                "role": {"type": "STRING", "description": "Cargo o título para la vCard"},
                "phone": {"type": "STRING", "description": "Número de teléfono para la vCard"},
                "email": {"type": "STRING", "description": "Correo electrónico para la vCard"},
                "limit": {"type": "INTEGER", "description": "Límite de transacciones a consultar en el historial"}
            },
            "required": []
        }
    },
    {
        "name": "personal_finances",
        "description": "Gestor de Finanzas Personales, Presupuesto y Flujo de Caja: registra gastos e ingresos clasificados por categorías (Alimentación, Transporte, Educación UNAL, etc.), calcula el balance mensual, superávit/déficit, tasa de ahorro y alertas preventivas de sobrecosto.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "summary | add_expense | add_income | set_budget"},
                "amount": {"type": "NUMBER", "description": "Monto en pesos (COP)"},
                "category": {"type": "STRING", "description": "Categoría: Alimentacion | Transporte | Educacion UNAL | Servicios & Hogar | Consultoria & Negocios | Entretenimiento | Inversion & Ahorro"},
                "description": {"type": "STRING", "description": "Descripción o concepto del gasto o ingreso"},
                "method": {"type": "STRING", "description": "Método de pago (Contactless, Nequi, Daviplata, Efectivo)"},
                "limit": {"type": "NUMBER", "description": "Tope mensual asignado al configurar presupuesto"}
            },
            "required": []
        }
    },
    {
        "name": "stark_vault",
        "description": "Bóveda Stark de Ciberseguridad: genera contraseñas de alta entropía, frases de paso memorables (Diceware) y tokens PIN, evalúa la entropía de Shannon y resistencia a ataques de fuerza bruta en segundos/años, y empaqueta credenciales seguras para transmisión por NFC.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "generate | audit | package_nfc"},
                "length": {"type": "INTEGER", "description": "Longitud de la contraseña a generar (ej: 18)"},
                "mode": {"type": "STRING", "description": "complex | passphrase | pin"},
                "password": {"type": "STRING", "description": "Contraseña a auditar y calcular entropía"},
                "secret": {"type": "STRING", "description": "Texto o secreto a empaquetar para NFC"}
            },
            "required": []
        }
    },
    {
        "name": "legal_contracts",
        "description": "Generador de Contratos Comerciales y Minutas Legales Colombianas: redacta contratos de prestación de servicios profesionales independientes, acuerdos de confidencialidad y no divulgación (NDA), pagarés a la orden y actas de entrega/liquidación con plena validez legal comercial.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "draft | templates"},
                "template": {"type": "STRING", "description": "servicios_profesionales | nda | pagare | acta_entrega"},
                "client": {"type": "STRING", "description": "Nombre o razón social de la contraparte"},
                "client_id": {"type": "STRING", "description": "NIT o cédula de la contraparte"},
                "amount": {"type": "NUMBER", "description": "Valor económico del contrato o pagaré"},
                "scope": {"type": "STRING", "description": "Objeto o alcance de las actividades contratadas"},
                "city": {"type": "STRING", "description": "Ciudad de suscripción (ej: Palmira, Valle del Cauca)"}
            },
            "required": []
        }
    },
    {
        "name": "investment_evaluator",
        "description": "Evaluador Financiero de Proyectos de Inversión y Presupuesto de Capital: calcula VAN (NPV), TIR (IRR con aproximación numérica), período de recuperación (Payback simple y descontado), relación Beneficio/Costo y análisis de escenarios (Base, Optimista +20%, Pesimista -20%).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "project_name": {"type": "STRING", "description": "Nombre de la iniciativa o proyecto"},
                "initial_investment": {"type": "NUMBER", "description": "Monto de inversión inicial en COP"},
                "cash_flows": {"type": "ARRAY", "description": "Flujos de caja proyectados anuales", "items": {"type": "NUMBER"}},
                "discount_rate": {"type": "NUMBER", "description": "Tasa de descuento o costo de oportunidad (ejemplo: 0.12 para 12%)"},
                "currency": {"type": "STRING", "description": "Moneda (COP por defecto)"}
            },
            "required": ["initial_investment"]
        }
    },
    {
        "name": "risk_matrix",
        "description": "Matriz de Riesgos Corporativos y Mapa de Calor 5x5 (ISO 31000 / COSO): gestiona riesgos estratégicos, financieros, operacionales, legales y de ciberseguridad, calculando niveles inherentes y residuales tras controles mitigantes.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "summary | add | delete"},
                "title": {"type": "STRING", "description": "Título o descripción del evento de riesgo"},
                "category": {"type": "STRING", "description": "Estrategico | Financiero | Operacional | Legal | Ciberseguridad"},
                "probability": {"type": "INTEGER", "description": "Probabilidad inherente de 1 (rara) a 5 (casi segura)"},
                "impact": {"type": "INTEGER", "description": "Impacto inherente de 1 (insignificante) a 5 (catastrófico)"},
                "control": {"type": "STRING", "description": "Medida o protocolo de control preventivo/detectivo"},
                "residual_probability": {"type": "INTEGER", "description": "Probabilidad residual tras control (1-5)"},
                "residual_impact": {"type": "INTEGER", "description": "Impacto residual tras control (1-5)"},
                "owner": {"type": "STRING", "description": "Líder o responsable del riesgo"},
                "risk_id": {"type": "STRING", "description": "Identificador para eliminación (ej: RSK-001)"}
            },
            "required": []
        }
    },
    {
        "name": "colombia_macro",
        "description": "Radar Macroeconómico de Colombia y Liquidador Laboral Pro-Forma: indicadores en tiempo real (TRM, UVT, SMLMV, Auxilio de Transporte, Tasa BanRep, IPC) y liquidación de costos laborales patronales con desglose de seguridad social, parafiscales (exoneración Art. 114-1 E.T.) y prestaciones sociales.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "indicators | payroll | uvt"},
                "base_salary": {"type": "NUMBER", "description": "Salario base mensual en COP para liquidación"},
                "risk_level": {"type": "INTEGER", "description": "Clase de riesgo ARL (1 a 5, por defecto 1)"},
                "include_transport": {"type": "BOOLEAN", "description": "Forzar inclusión de auxilio de transporte"},
                "apply_exemption_114_1": {"type": "BOOLEAN", "description": "Aplicar exoneración de aportes patronales Art. 114-1 E.T."},
                "amount": {"type": "NUMBER", "description": "Monto para conversión UVT"},
                "direction": {"type": "STRING", "description": "cop_to_uvt | uvt_to_cop"}
            },
            "required": []
        }
    },
    {
        "name": "pitch_generator",
        "description": "Generador de Presentaciones Ejecutivas y Pitch Decks de Inversión (Norma Guy Kawasaki 10/20/30 & Sequoia Capital): genera 10 diapositivas maestras (problema, solución, monetización, tecnología, TAM/SAM/SOM, go-to-market, competencia, equipo y solicitud de capital).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "business_name": {"type": "STRING", "description": "Nombre de la empresa, startup o proyecto"},
                "industry": {"type": "STRING", "description": "tech_saas | consultoria | agroindustria | ecommerce"},
                "problem": {"type": "STRING", "description": "Dolor o problema principal de mercado"},
                "solution": {"type": "STRING", "description": "Propuesta de valor y solución ofrecida"},
                "funding_ask": {"type": "NUMBER", "description": "Monto de capital solicitado a inversionistas"},
                "currency": {"type": "STRING", "description": "Moneda (COP por defecto)"},
                "founder": {"type": "STRING", "description": "Nombre del fundador o líder del proyecto"},
                "city": {"type": "STRING", "description": "Ciudad y país"}
            },
            "required": ["business_name"]
        }
    },
    {
        "name": "logistics_inventory",
        "description": "Gestión de Cadena de Suministro e Inventarios: calcula el Lote Económico de Pedido (EOQ / Modelo de Wilson), el Punto de Reorden (ROP) con Stock de Seguridad (SS) y realiza la clasificación ABC de inventarios según la Ley de Pareto 80/20.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "eoq | rop | abc"},
                "annual_demand": {"type": "NUMBER", "description": "Demanda anual en unidades (D)"},
                "order_cost": {"type": "NUMBER", "description": "Costo por emitir una orden de compra en COP (S)"},
                "holding_cost": {"type": "NUMBER", "description": "Costo anual de almacenamiento por unidad en COP (H)"},
                "unit_cost": {"type": "NUMBER", "description": "Costo de compra unitario en COP (C)"},
                "daily_demand": {"type": "NUMBER", "description": "Demanda promedio diaria (d)"},
                "lead_time": {"type": "NUMBER", "description": "Tiempo de entrega del proveedor en días (L)"},
                "service_level": {"type": "NUMBER", "description": "Nivel de servicio exigido en % (ej: 95)"},
                "std_dev": {"type": "NUMBER", "description": "Desviación estándar de la demanda diaria (sigma)"}
            },
            "required": []
        }
    },
    {
        "name": "negotiation_engine",
        "description": "Simulador de Negociación Estratégica y Resolución de Conflictos (Modelo Harvard): analiza el rango de acuerdo ZOPA (Zone of Possible Agreement), evalúa los precios de reserva y BATNA (MAAN) del comprador y vendedor, y genera tácticas basadas en intereses objetivos.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "buyer_reservation_price": {"type": "NUMBER", "description": "Precio máximo que el comprador está dispuesto a pagar"},
                "seller_reservation_price": {"type": "NUMBER", "description": "Precio mínimo que el vendedor está dispuesto a aceptar"},
                "buyer_target_price": {"type": "NUMBER", "description": "Precio ideal deseado por el comprador"},
                "seller_target_price": {"type": "NUMBER", "description": "Precio ideal deseado por el vendedor"},
                "buyer_batna": {"type": "STRING", "description": "Mejor alternativa del comprador si no hay acuerdo"},
                "seller_batna": {"type": "STRING", "description": "Mejor alternativa del vendedor si no hay acuerdo"},
                "currency": {"type": "STRING", "description": "Moneda (COP por defecto)"}
            },
            "required": ["buyer_reservation_price", "seller_reservation_price"]
        }
    },
    {
        "name": "dian_tax",
        "description": "Auditor Tributario y Calendario Fiscal DIAN (Colombia 2026): verifica causales de obligación para declarar renta persona natural (topes UVT), simula y compara la carga impositiva del Régimen Simple (RST) vs Régimen Ordinario, y consulta fechas de vencimiento según los últimos dígitos del NIT/Cédula.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "rst_vs_ordinario | renta_check | calendar"},
                "patrimonio_bruto": {"type": "NUMBER", "description": "Patrimonio bruto en COP para prueba de renta"},
                "ingresos_brutos": {"type": "NUMBER", "description": "Ingresos brutos anuales en COP para prueba de renta"},
                "consumos_tarjeta": {"type": "NUMBER", "description": "Consumos con tarjeta de crédito en COP"},
                "compras_totales": {"type": "NUMBER", "description": "Compras y consumos totales en COP"},
                "consignaciones": {"type": "NUMBER", "description": "Consignaciones bancarias en COP"},
                "ingresos": {"type": "NUMBER", "description": "Ingresos anuales para comparador RST vs Ordinario"},
                "costos": {"type": "NUMBER", "description": "Costos y deducciones deducibles para comparador"},
                "actividad": {"type": "STRING", "description": "servicios_profesionales | comercio_al_por_mayor_menor | actividades_industriales | tiendas_minimercados"},
                "nit": {"type": "STRING", "description": "NIT o cédula para consultar calendario tributario"}
            },
            "required": []
        }
    },
    {
        "name": "bsc_okrs",
        "description": "Cuadro de Mando Integral (Balanced Scorecard) y Matriz de OKRs Corporativos: evalúa el cumplimiento en las 4 perspectivas de Kaplan & Norton (Financiera, Clientes, Procesos Internos, Aprendizaje/Crecimiento) y calcula el Índice Global de Salud Corporativa con semáforos.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "dashboard | update"},
                "kr_id": {"type": "STRING", "description": "Identificador del Resultado Clave (ej: KR-01)"},
                "value": {"type": "NUMBER", "description": "Nuevo valor actual alcanzado"}
            },
            "required": []
        }
    },
    {
        "name": "tax_payment",
        "description": "Asistente Oficial de Liquidación y Pago de Impuestos DIAN (Formulario 490): liquida el recibo oficial de pago de tributos nacionales (Renta, Retención en la fuente, IVA, Anticipo RST, ICA), calcula intereses moratorios diarios exactos (Art. 635 E.T. tasa de usura), sanción por extemporaneidad (Art. 641 E.T. mínimo 10 UVT), genera el botón/enlace de pago seguro PSE con CUS bancario y registra el paz y salvo.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "settle | pse_link | history"},
                "concept": {"type": "STRING", "description": "renta_pj | renta_pn | retefuente | iva | rst_anticipo | ica_municipal"},
                "year": {"type": "INTEGER", "description": "Año gravable (ej: 2026)"},
                "period": {"type": "STRING", "description": "Período fiscal: mes (01-12) o bimestre (01-06)"},
                "nit": {"type": "STRING", "description": "NIT o cédula del contribuyente"},
                "amount": {"type": "NUMBER", "description": "Monto del impuesto a pagar en COP"},
                "due_date": {"type": "STRING", "description": "Fecha límite oficial de vencimiento (AAAA-MM-DD)"},
                "payment_date": {"type": "STRING", "description": "Fecha real proyectada de pago (AAAA-MM-DD)"},
                "bank": {"type": "STRING", "description": "Banco para pasarela PSE (Bancolombia, Davivienda, Nequi, etc.)"}
            },
            "required": ["concept", "amount"]
        }
    },
    {
        "name": "business_valuation",
        "description": "Valuador Financiero de Empresas y Startups: valora compañías mediante Flujo de Caja Libre Descontado (DCF) con Valor Terminal Gordon-Shapiro (EV y Equity Value), Múltiplos Comparables de Mercado (EV/EBITDA y EV/Sales por industria) y Método Venture Capital (Post-money, Pre-money y dilución de socios).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "method": {"type": "STRING", "description": "dcf | multiples | vc"},
                "cash_flows": {"type": "ARRAY", "description": "Lista de flujos de caja libre proyectados anuales", "items": {"type": "NUMBER"}},
                "wacc": {"type": "NUMBER", "description": "Costo de capital promedio ponderado (ej: 0.12 para 12%)"},
                "terminal_growth_g": {"type": "NUMBER", "description": "Tasa de crecimiento a perpetuidad (ej: 0.03 para 3%)"},
                "cash": {"type": "NUMBER", "description": "Saldo en caja y equivalentes en COP"},
                "debt": {"type": "NUMBER", "description": "Deuda financiera total en COP"},
                "ebitda": {"type": "NUMBER", "description": "EBITDA anual en COP para múltiplos"},
                "annual_revenue": {"type": "NUMBER", "description": "Ventas o ingresos brutos anuales en COP"},
                "industry": {"type": "STRING", "description": "tech_saas | consultoria | agroindustria | retail_ecommerce"},
                "target_exit_value": {"type": "NUMBER", "description": "Valor esperado de venta de la startup para método VC"},
                "years_to_exit": {"type": "INTEGER", "description": "Años hasta la salida del inversionista"},
                "required_roi_multiple": {"type": "NUMBER", "description": "Múltiplo de retorno exigido (ej: 5.0 para 5x)"},
                "investment_amount": {"type": "NUMBER", "description": "Monto de inversión solicitada en COP"},
                "currency": {"type": "STRING", "description": "Moneda (COP por defecto)"}
            },
            "required": []
        }
    },
    {
        "name": "fleet_routes",
        "description": "Optimizador de Rutas y Fletes Logísticos en Colombia: liquida el costo de fletes de transporte de carga y distribución regional (Cali, Palmira, Yumbo, Buenaventura, Bogotá, Medellín, Eje Cafetero), calcula galones de combustible, peajes INVIAS, viáticos de conductor, desgaste por km y huella de carbono CO2.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "route": {"type": "STRING", "description": "palmira_cali | palmira_yumbo | palmira_buenaventura | palmira_pereira | palmira_bogota | palmira_medellin"},
                "vehicle": {"type": "STRING", "description": "van_urbana | turbo_4_ton | sencillo_8_ton | tractomula_32_ton"},
                "distance_km": {"type": "NUMBER", "description": "Distancia personalizada en km si es otra ruta"},
                "fuel_price": {"type": "NUMBER", "description": "Precio por galón de combustible en COP"},
                "cargo_weight": {"type": "NUMBER", "description": "Peso de la carga en toneladas"}
            },
            "required": []
        }
    },
    {
        "name": "marketing_growth",
        "description": "Motor de Crecimiento & Unit Economics 360: CAC, LTV, ratio LTV/CAC, Payback, Churn mensual y anual, auditoría de embudos (funnels) y atribución de pauta publicitaria multicanal (ROAS).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action_type": {"type": "STRING", "description": "unit_economics | funnel | roas"},
                "cac": {"type": "NUMBER", "description": "Costo de Adquisición de Clientes en COP o USD"},
                "arpu": {"type": "NUMBER", "description": "Ingreso Promedio por Usuario mensual"},
                "churn_monthly_pct": {"type": "NUMBER", "description": "Porcentaje de churn mensual (ej: 3.5)"},
                "gross_margin_pct": {"type": "NUMBER", "description": "Margen bruto en porcentaje (ej: 80.0)"}
            },
            "required": []
        }
    },
    {
        "name": "talent_management",
        "description": "Gestión Estratégica de Talento Humano & Clima Organizacional: Evaluación de colaboradores en la Matriz 9-Box (Desempeño vs Potencial), cálculo de eNPS de clima y costo de rotación (turnover) con normativa colombiana.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action_type": {"type": "STRING", "description": "9box | enps | turnover"},
                "employee_name": {"type": "STRING", "description": "Nombre del colaborador"},
                "performance_score": {"type": "NUMBER", "description": "Desempeño 1.0 a 3.0"},
                "potential_score": {"type": "NUMBER", "description": "Potencial 1.0 a 3.0"},
                "role": {"type": "STRING", "description": "Cargo del colaborador"}
            },
            "required": []
        }
    },
    {
        "name": "esg_governance",
        "description": "Gobierno Corporativo & Sostenibilidad ESG: Evaluaciones Ambientales (E), Sociales (S) y Gobernanza (G) bajo estándares IFRS S1/S2 y GRI, calificación compuesta (AAA a CCC) y plan de acción de descarbonización y ética corporativa.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "company_name": {"type": "STRING", "description": "Nombre de la empresa"},
                "environmental_score": {"type": "NUMBER", "description": "Puntaje Ambiental (0 a 100)"},
                "social_score": {"type": "NUMBER", "description": "Puntaje Social (0 a 100)"},
                "governance_score": {"type": "NUMBER", "description": "Puntaje Gobernanza (0 a 100)"},
                "sector": {"type": "STRING", "description": "Sector económico"}
            },
            "required": []
        }
    },
    {
        "name": "treasury_working_capital",
        "description": "Tesorería Corporativa, Capital de Trabajo (KTNO) y Factoring: Ciclo de Conversión de Efectivo (CCC = DSO + DIO - DPO), liquidez atrapada y simulador de descuento de facturas electrónicas (RADIAN / DIAN) con Tasa Efectiva Anual (E.A.).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action_type": {"type": "STRING", "description": "ccc | factoring"},
                "dso_receivables_days": {"type": "NUMBER", "description": "Días de cobro a clientes (DSO)"},
                "dio_inventory_days": {"type": "NUMBER", "description": "Días de rotación de inventarios (DIO)"},
                "dpo_payables_days": {"type": "NUMBER", "description": "Días de pago a proveedores (DPO)"},
                "invoice_face_value_cop": {"type": "NUMBER", "description": "Valor nominal de factura en factoring"},
                "days_to_maturity": {"type": "INTEGER", "description": "Días restantes para el vencimiento de la factura"}
            },
            "required": []
        }
    },
    {
        "name": "forex_radar",
        "description": "Radar Cambiario, Arbitraje de Divisas y Cobertura Forward: TRM oficial Banco de la República, Dólar Cripto USDT P2P, Dólar Tarjeta, EUR/COP, spreads bancarios y simulador de contratos Forward para importaciones.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action_type": {"type": "STRING", "description": "radar | hedge"},
                "amount_usd": {"type": "NUMBER", "description": "Monto en dólares a convertir o cubrir"},
                "days_forward": {"type": "INTEGER", "description": "Días de plazo para la cobertura Forward (ej: 90)"}
            },
            "required": []
        }
    },
    {
        "name": "biocognitive_habits",
        "description": "Centro de Telemetría Biocognitiva y Hábitos Ejecutivos del CEO: evalúa el descanso nocturno, hidratación, bloques de trabajo profundo, nivel de energía, cronotipo (alondra vs búho) e Índice de Rendimiento Biocognitivo con sugerencias ergonómicas y neuro-productivas.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "status | log"},
                "sleep_hours": {"type": "NUMBER", "description": "Horas de descanso nocturno (ej: 7.5)"},
                "water_glasses": {"type": "INTEGER", "description": "Vasos de agua consumidos en el día"},
                "deep_work_hours": {"type": "NUMBER", "description": "Horas dedicadas a trabajo profundo / estudio"},
                "energy_rating": {"type": "INTEGER", "description": "Vigor y claridad mental percibida de 1 a 10"},
                "chronotype": {"type": "STRING", "description": "matutino_alondra | vespertino_buho"}
            },
            "required": []
        }
    },
    {
        "name": "stock_trading",
        "description": "Terminal Bursátil y Trading Cuantitativo: analiza activos (BVC o Wall Street) en tiempo real con RSI, MACD, Golden Cross (EMA 50/200), Stop-Loss y Take-Profit dinámicos basados en ATR (ratio 1:2.5) y regla estricta de gestión de riesgo del 1.5% de capital para minimizar el margen de error.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "ticker": {"type": "STRING", "description": "Símbolo bursátil o acción (ej: ECOPETROL, PFBCOLOM, AAPL, NVDA, TSLA)"},
                "current_price": {"type": "NUMBER", "description": "Precio actual de cotización de la acción"},
                "rsi": {"type": "NUMBER", "description": "Valor del RSI (14 períodos, ej: 32 o 65)"},
                "macd_signal": {"type": "STRING", "description": "Señal MACD: bullish_cross | bearish_cross | neutral"},
                "ema_50": {"type": "NUMBER", "description": "Valor de la Media Móvil Exponencial de 50 períodos"},
                "ema_200": {"type": "NUMBER", "description": "Valor de la Media Móvil Exponencial de 200 períodos"},
                "atr": {"type": "NUMBER", "description": "Volatilidad Average True Range (ATR)"},
                "total_trading_capital": {"type": "NUMBER", "description": "Capital total de la cuenta de trading para dimensionamiento de riesgo"},
                "currency": {"type": "STRING", "description": "Moneda: COP o USD"}
            },
            "required": ["ticker", "current_price"]
        }
    },
    {
        "name": "dividend_screener",
        "description": "Radar de Acciones con Dividendos y Asignador de Portafolio para Presupuesto Ajustado: filtra empresas de alta rentabilidad por dividendo en Colombia (BVC) y Wall Street (US), optimiza compras fraccionadas o nominales bajas con presupuestos reducidos y simula proyecciones de interés compuesto por reinversión de dividendos (DRIP).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "budget": {"type": "NUMBER", "description": "Presupuesto disponible para invertir (ej: 500000 COP o 200 USD)"},
                "market": {"type": "STRING", "description": "Mercado bursátil: BVC (Colombia) o US (Wall Street)"},
                "min_yield_pct": {"type": "NUMBER", "description": "Rentabilidad por dividendo mínima anual deseada (%)"},
                "reinvest_dividends": {"type": "BOOLEAN", "description": "Si se reinvierten dividendos (plan DRIP)"},
                "projection_years": {"type": "INTEGER", "description": "Años de proyección de interés compuesto (ej: 5)"}
            },
            "required": ["budget"]
        }
    },
    {
        "name": "bank_reconciliation",
        "description": "Conciliador Bancario y Auditoría de GMF (4x1000): realiza la ecuación de conciliación entre extractos bancarios y libros contables (depósitos en tránsito, cheques pendientes, notas débito/crédito bancarias) y audita el 4x1000 generado con el 50% deducible en renta (Art. 115 E.T.) y exención de 350 UVT.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "bank_statement_balance": {"type": "NUMBER", "description": "Saldo final según extracto bancario"},
                "general_ledger_balance": {"type": "NUMBER", "description": "Saldo final según libros contables auxiliares"},
                "deposits_in_transit": {"type": "NUMBER", "description": "Consignaciones o depósitos en tránsito no acreditados por el banco"},
                "outstanding_checks": {"type": "NUMBER", "description": "Cheques o giros emitidos pendientes de cobro"},
                "bank_charges_and_fees": {"type": "NUMBER", "description": "Gastos bancarios, cuotas de manejo y comisiones del extracto"},
                "unrecorded_bank_credits": {"type": "NUMBER", "description": "Abonos directos o intereses a favor no contabilizados"},
                "unrecorded_bank_debits": {"type": "NUMBER", "description": "Débitos bancarios directos no registrados en libros"},
                "total_monthly_debits_cop": {"type": "NUMBER", "description": "Monto total de débitos y retiros del mes para auditar 4x1000"},
                "is_account_gmf_exempt": {"type": "BOOLEAN", "description": "Si la cuenta está marcada como exenta de 4x1000 (hasta 350 UVT)"},
                "bank_name": {"type": "STRING", "description": "Nombre de la entidad bancaria (ej: Bancolombia, Davivienda, BBVA)"},
                "currency": {"type": "STRING", "description": "Moneda: COP o USD"}
            },
            "required": ["bank_statement_balance", "general_ledger_balance"]
        }
    },
    {
        "name": "monte_carlo_simulation",
        "description": "Simulador Estocástico Monte Carlo y Stress Testing de Capital: ejecuta de 1.000 a 10.000 iteraciones estocásticas vectorizadas para evaluar proyectos de inversión, calculando la probabilidad de VAN positivo P(VAN > 0), VAN esperado, volatilidad, Value at Risk (VaR 95% y VaR 99%) y diagnóstico de resiliencia financiera.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "project_name": {"type": "STRING", "description": "Nombre del proyecto, expansión o iniciativa estratégica"},
                "initial_investment": {"type": "NUMBER", "description": "Inversión inicial o capex requerido"},
                "mean_annual_revenue": {"type": "NUMBER", "description": "Ingreso anual promedio esperado"},
                "std_annual_revenue": {"type": "NUMBER", "description": "Desviación estándar o volatilidad del ingreso anual"},
                "fixed_operating_costs": {"type": "NUMBER", "description": "Costos y gastos fijos operativos anuales"},
                "variable_costs_ratio": {"type": "NUMBER", "description": "Ratio de costos variables sobre ingresos (0.0 a 1.0, ej: 0.25)"},
                "discount_rate_wacc": {"type": "NUMBER", "description": "Tasa de descuento WACC (ej: 0.12 para 12%)"},
                "project_years": {"type": "INTEGER", "description": "Años de vida útil o proyección del proyecto (ej: 5)"},
                "simulations_count": {"type": "INTEGER", "description": "Número de iteraciones Monte Carlo (ej: 5000)"},
                "currency": {"type": "STRING", "description": "Moneda: COP o USD"}
            },
            "required": ["initial_investment", "mean_annual_revenue"]
        }
    },
    {
        "name": "pricing_elasticity",
        "description": "Estrategia de Precios y Elasticidad de la Demanda: evalúa el coeficiente de elasticidad precio (Ed), clasifica la sensibilidad de la demanda (inelástica, elástica, unitaria), calcula el precio óptimo mediante la regla de Lerner (P* = MC / (1 + 1/Ed)) y simula curvas de variación de precios (-20% a +20%) con impacto en margen de contribución y EBITDA.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "product_name": {"type": "STRING", "description": "Nombre del producto, línea o servicio"},
                "current_price": {"type": "NUMBER", "description": "Precio unitario de venta actual"},
                "unit_marginal_cost": {"type": "NUMBER", "description": "Costo marginal o costo variable unitario"},
                "current_monthly_units": {"type": "NUMBER", "description": "Volumen de ventas mensual actual en unidades"},
                "price_elasticity": {"type": "NUMBER", "description": "Coeficiente de elasticidad precio estimado (ej: -1.4)"},
                "test_price": {"type": "NUMBER", "description": "Precio de prueba histórico o proyectado"},
                "test_volume": {"type": "NUMBER", "description": "Volumen de prueba asociado al precio de prueba"},
                "currency": {"type": "STRING", "description": "Moneda: COP o USD"}
            },
            "required": ["current_price", "unit_marginal_cost"]
        }
    },
    {
        "name": "credit_amortization",
        "description": "Simulador de Créditos y Optimización de Deuda Bancaria: genera tablas de amortización en Sistema Francés (cuota fija) y Alemán (abono constante a capital), convierte tasa Efectiva Anual (E.A.) a tasa mensual periódica, audita el límite de usura de la SuperFinanciera y calcula el ahorro de intereses y meses reducidos mediante abonos extraordinarios inteligentes.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "loan_name": {"type": "STRING", "description": "Nombre o concepto del crédito (ej: Préstamo Bancolombia, Capital de Trabajo)"},
                "principal_amount": {"type": "NUMBER", "description": "Monto del capital solicitado o saldo adeudado"},
                "annual_interest_rate_ea_pct": {"type": "NUMBER", "description": "Tasa de interés Efectiva Anual en porcentaje (ej: 19.5 para 19.5% E.A.)"},
                "term_months": {"type": "INTEGER", "description": "Plazo pactado en meses (ej: 36)"},
                "amortization_system": {"type": "STRING", "description": "french (cuota fija) | german (abono constante a capital)"},
                "extra_monthly_prepayment": {"type": "NUMBER", "description": "Abono mensual extraordinario a capital (ej: 500000)"},
                "prepayment_strategy": {"type": "STRING", "description": "reduce_term (reducir plazo) | reduce_payment (reducir cuota)"},
                "currency": {"type": "STRING", "description": "Moneda: COP o USD"}
            },
            "required": ["principal_amount", "annual_interest_rate_ea_pct"]
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
                res = reverse_engineering_action(parameters=args)
                return res

            elif name in ("ego_browser", "ego", "browser_automation", "fast_browser", "ego_lite"):
                from app.actions.ego_browser_action import ego_browser_action
                res = ego_browser_action(parameters=args)
                return res

            elif name in ("vercel_skills", "vercel", "react_best_practices", "web_design_guidelines", "deploy_app", "vercel_deploy"):
                from app.actions.vercel_skills_action import vercel_skills_action
                res = vercel_skills_action(parameters=args)
                return res

            elif name in ("security_audit", "security", "vulnerability_scan", "cve_audit", "owasp_audit"):
                from app.actions.security_audit_action import security_audit_action
                res = security_audit_action(parameters=args)
                return res

            elif name in ("slopmonster", "deslop", "humanize_copy", "anti_slop", "humanize_text"):
                from app.actions.slopmonster_action import slopmonster_action
                res = slopmonster_action(parameters=args)
                return res

            elif name in ("git_sync", "sync_github", "github_sync", "git_push", "repo_sync"):
                from app.actions.git_sync_action import git_sync_action
                res = git_sync_action(parameters=args)
                return res

            elif name in ("academic_research", "academic_papers", "scientific_literature", "openalex", "arxiv"):
                from app.actions.academic_research_action import academic_research_action
                res = academic_research_action(parameters=args)
                return res

            elif name in ("business_strategy", "corporate_strategy", "strategic_matrix", "business_model"):
                from app.actions.business_strategy_action import business_strategy_action
                res = business_strategy_action(parameters=args)
                return res

            elif name in ("data_ml_toolkit", "data_science", "machine_learning", "data_cleaning", "predictive_analytics"):
                from app.actions.data_ml_action import data_ml_action
                res = data_ml_action(parameters=args)
                return res

            elif name in ("workspace_automation", "office_automation", "excel_tools", "spreadsheet_modeling"):
                from app.actions.workspace_automation_action import workspace_automation_action
                res = workspace_automation_action(parameters=args)
                return res

            elif name in ("unal_pensum", "pensum_unal", "pensum_administracion", "unal_curriculum"):
                from app.actions.unal_pensum_action import unal_pensum_action
                res = unal_pensum_action(parameters=args)
                return res

            elif name in ("credentials_vault", "open_credentials_vault", "api_vault", "configurar_apis", "boveda_credenciales"):
                return json.dumps({
                    "status": "success",
                    "action": "open_credentials_vault",
                    "message": "He abierto la Bóveda Central de Autenticadores y APIs para usted, señor Santiago."
                }, ensure_ascii=False)

            elif name in ("nfc_contactless", "nfc_pay", "contactless_payment", "nfc_beam", "pago_contacto", "nfc", "factura_electronica", "digital_invoice", "convertir_divisas", "crypto_converter"):
                from app.actions.nfc_action import nfc_action
                res = nfc_action(parameters=args)
                return res

            elif name in ("personal_finances", "finanzas_personales", "presupuesto", "flujo_caja", "gastos"):
                from app.actions.personal_finance_action import personal_finance_action
                res = personal_finance_action(parameters=args)
                return res

            elif name in ("stark_vault", "vault_generator", "generador_claves", "boveda_stark", "password_generator"):
                from app.actions.stark_vault_action import stark_vault_action
                res = stark_vault_action(parameters=args)
                return res

            elif name in ("legal_contracts", "contratos_legales", "minutas_colombia", "nda_generator", "redactar_contrato"):
                from app.actions.legal_contracts_action import legal_contracts_action
                res = legal_contracts_action(parameters=args)
                return res

            elif name in ("investment_evaluator", "evaluador_proyectos", "van_tir", "evaluar_inversion", "presupuesto_capital"):
                from app.actions.investment_evaluator_action import investment_evaluator_action
                res = investment_evaluator_action(parameters=args)
                return res

            elif name in ("risk_matrix", "matriz_riesgos", "mapa_calor", "gestor_riesgos", "iso_31000"):
                from app.actions.risk_matrix_action import risk_matrix_action
                res = risk_matrix_action(parameters=args)
                return res

            elif name in ("colombia_macro", "macro_colombia", "nomina_colombia", "indicadores_macro", "costo_laboral", "liquidador_laboral"):
                from app.actions.colombia_macro_action import colombia_macro_action
                res = colombia_macro_action(parameters=args)
                return res

            elif name in ("pitch_generator", "generar_pitch", "presentacion_ejecutiva", "pitch_deck", "diapositivas_inversion"):
                from app.actions.pitch_generator_action import pitch_generator_action
                res = pitch_generator_action(parameters=args)
                return res

            elif name in ("logistics_inventory", "eoq", "inventarios", "cadena_suministro", "rop_wilson", "clasificacion_abc"):
                from app.actions.logistics_inventory_action import logistics_inventory_action
                res = logistics_inventory_action(parameters=args)
                return res

            elif name in ("negotiation_engine", "negociacion_harvard", "zopa", "batna", "simulador_negociacion"):
                from app.actions.negotiation_engine_action import negotiation_engine_action
                res = negotiation_engine_action(parameters=args)
                return res

            elif name in ("dian_tax", "impuestos_dian", "regimen_simple", "rst_vs_ordinario", "calendario_tributario", "declaracion_renta"):
                from app.actions.dian_tax_action import dian_tax_action
                res = dian_tax_action(parameters=args)
                return res

            elif name in ("bsc_okrs", "balanced_scorecard", "okrs_corporativos", "cuadro_mando", "metas_estrategicas"):
                from app.actions.bsc_okrs_action import bsc_okrs_action
                res = bsc_okrs_action(parameters=args)
                return res

            elif name in ("tax_payment", "pago_impuestos", "formulario_490", "pagar_dian", "intereses_moratorios", "pago_pse_dian"):
                from app.actions.tax_payment_action import tax_payment_action
                res = tax_payment_action(parameters=args)
                return res

            elif name in ("business_valuation", "valuacion_empresas", "valor_empresa", "dcf", "multiplos_ebitda", "venture_capital_valuation"):
                from app.actions.business_valuation_action import business_valuation_action
                res = business_valuation_action(parameters=args)
                return res

            elif name in ("fleet_routes", "rutas_colombia", "fletes_colombia", "costo_transporte", "logistica_flotas"):
                from app.actions.fleet_routes_action import fleet_routes_action
                res = fleet_routes_action(parameters=args)
                return res

            elif name in ("biocognitive_habits", "habitos_ejecutivos", "telemetria_ceo", "energia_cognitiva", "cronotipo"):
                from app.actions.biocognitive_habits_action import biocognitive_habits_action
                res = biocognitive_habits_action(parameters=args)
                return res





            elif name in ("marketing_growth", "saas_metrics", "unit_economics", "cac_ltv", "embudo_ventas", "roas"):
                from app.actions.marketing_growth_action import marketing_growth_action
                res = marketing_growth_action(parameters=args)
                return res

            elif name in ("talent_management", "matriz_9box", "nine_box", "clima_laboral", "enps", "rotacion_personal"):
                from app.actions.talent_management_action import talent_management_action
                res = talent_management_action(parameters=args)
                return res

            elif name in ("forex_radar", "radar_cambiario", "trm_colombia", "dolar_colombia", "forward_hedging", "cobertura_divisas"):
                from app.actions.forex_radar_action import forex_radar_action
                res = forex_radar_action(parameters=args)
                return res

            elif name in ("esg_governance", "sostenibilidad_esg", "gobierno_corporativo", "esg_score"):
                from app.actions.esg_governance_action import esg_governance_action
                res = esg_governance_action(parameters=args)
                return res

            elif name in ("treasury_working_capital", "capital_trabajo", "ktno", "ciclo_efectivo", "ccc", "factoring", "radian"):
                from app.actions.treasury_working_capital_action import treasury_working_capital_action
                res = treasury_working_capital_action(parameters=args)
                return res

            elif name in ("stock_trading", "trading_cuantitativo", "bolsa_valores", "analisis_bursatil", "orden_trading"):
                from app.actions.stock_trading_action import stock_trading_action
                res = stock_trading_action(parameters=args)
                return res

            elif name in ("dividend_screener", "acciones_dividendos", "dividendos_baratos", "portafolio_dividendos", "drip_compounding"):
                from app.actions.dividend_screener_action import dividend_screener_action
                res = dividend_screener_action(parameters=args)
                return res

            elif name in ("bank_reconciliation", "conciliacion_bancaria", "extracto_bancario", "auditoria_4x1000", "gmf_colombia"):
                from app.actions.bank_reconciliation_action import bank_reconciliation_action
                res = bank_reconciliation_action(parameters=args)
                return res

            elif name in ("monte_carlo_simulation", "simulacion_monte_carlo", "monte_carlo", "stress_testing", "var_financiero", "riesgo_estocastico"):
                from app.actions.monte_carlo_action import monte_carlo_action
                res = monte_carlo_action(parameters=args)
                return res

            elif name in ("pricing_elasticity", "elasticidad_precio", "fijacion_precios", "precio_optimo", "regla_lerner"):
                from app.actions.pricing_elasticity_action import pricing_elasticity_action
                res = pricing_elasticity_action(parameters=args)
                return res

            elif name in ("credit_amortization", "simulador_credito", "tabla_amortizacion", "prestamo_bancario", "abono_capital", "tasa_usura"):
                from app.actions.credit_amortization_action import credit_amortization_action
                res = credit_amortization_action(parameters=args)
                return res

            else:
                return f"Herramienta '{name}' no reconocida."

        except Exception as e:
            logger.error(f"[ACTION_ERR] Error ejecutando '{name}': {e}", exc_info=True)
            return f"Error ejecutando '{name}': {str(e)}"


action_dispatcher = ActionDispatcher()
