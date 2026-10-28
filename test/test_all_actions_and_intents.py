"""
Comprehensive unit and integration test suite for:
- All ActionDispatcher system tools
- All direct intent patterns (0ms native execution)
- VoiceEngine wake words and command extraction
- Performance and speed optimizations
"""
import asyncio
import os
import pytest
from app.services.action_dispatcher import action_dispatcher
from app.services.brain_router import detect_direct_intent, brain_router
from app.services.soul_service import soul_service
from app.services.voice_engine import contains_wake_word, extract_command
from app.actions.open_app import _normalize
from app.actions.computer_settings import _detect_action


def test_open_app_aliases_resolution():
    """Verifies that common Spanish app and site names map correctly."""
    assert "calc.exe" in _normalize("calculadora")
    assert "notepad.exe" in _normalize("bloc de notas")
    assert "notepad.exe" in _normalize("notas")
    assert "explorer.exe" in _normalize("explorador de archivos")
    assert "explorer.exe" in _normalize("explorador")
    assert "chrome" in _normalize("navegador")
    assert "ms-settings:" in _normalize("configuracion")
    assert "ms-settings:" in _normalize("configuración")
    assert "taskmgr.exe" in _normalize("administrador de tareas")
    assert "youtube" in _normalize("youtube")
    assert "Spotify" in _normalize("musica")


def test_computer_settings_aliases_resolution():
    """Verifies that system setting aliases in Spanish map correctly."""
    assert _detect_action("subir volumen")["action"] == "volume_up"
    assert _detect_action("sube el volumen")["action"] == "volume_up"
    assert _detect_action("bajar volumen")["action"] == "volume_down"
    assert _detect_action("baja el volumen")["action"] == "volume_down"
    assert _detect_action("silenciar")["action"] == "volume_mute"
    assert _detect_action("mutear")["action"] == "volume_mute"
    assert _detect_action("subir brillo")["action"] == "brightness_up"
    assert _detect_action("bajar brillo")["action"] == "brightness_down"
    assert _detect_action("captura de pantalla")["action"] == "take_screenshot"
    assert _detect_action("pantalla completa")["action"] == "full_screen"
    assert _detect_action("mostrar escritorio")["action"] == "minimize_window"
    assert _detect_action("cerrar ventana")["action"] == "close_window"
    assert _detect_action("bloquear pantalla")["action"] == "lock_screen"


def test_detect_direct_intents_comprehensive():
    """Verifies all direct intents trigger deterministic actions without calling external LLM."""
    cases = [
        ("abre la calculadora", "open_app", "app_name", "calculadora"),
        ("abre bloc de notas", "open_app", "app_name", "bloc de notas"),
        ("abre el explorador de archivos", "open_app", "app_name", "explorador de archivos"),
        ("abre chrome", "open_app", "app_name", "chrome"),
        ("sube el volumen", "computer_settings", "action", "volume_up"),
        ("baja el volumen", "computer_settings", "action", "volume_down"),
        ("silencia el equipo", "computer_settings", "action", "volume_mute"),
        ("volumen al 70%", "computer_settings", "action", "volume_set"),
        ("sube el brillo", "computer_settings", "action", "brightness_up"),
        ("baja el brillo", "computer_settings", "action", "brightness_down"),
        ("toma una captura de pantalla", "computer_settings", "action", "take_screenshot"),
        ("pantalla completa", "computer_settings", "action", "full_screen"),
        ("muestra el escritorio", "computer_settings", "action", "minimize_window"),
        ("maximiza la ventana", "computer_settings", "action", "maximize_window"),
        ("cierra la ventana", "computer_settings", "action", "close_window"),
        ("bloquea la pantalla", "computer_settings", "action", "lock_screen"),
        ("pausa la musica", "computer_settings", "action", "pause_video"),
        ("estado de mi pc", "system_monitor", "metric", "all"),
        ("como esta mi pc", "system_monitor", "metric", "all"),
        ("reproduce coldplay viva la vida", "youtube_video", "action", "play"),
        ("deshacer", "undo", "action", "undo"),
        ("mira mi pantalla", "screen_process", "query", "mira mi pantalla"),
        ("que estoy viendo", "screen_process", "query", "que estoy viendo"),
        ("modo trabajo profundo", "deep_work", "action", "start"),
        ("iniciar pomodoro", "deep_work", "action", "start"),
        ("cancelar pomodoro", "deep_work", "action", "stop"),
        ("estado del pomodoro", "deep_work", "action", "status"),
        ("analiza mi portapapeles", "smart_clipboard", "action", "analyze"),
        ("que tengo copiado", "smart_clipboard", "action", "analyze"),
        ("explica lo que copie", "smart_clipboard", "action", "analyze"),
        ("siguiente cancion", "computer_settings", "action", "media_next"),
        ("cancion anterior", "computer_settings", "action", "media_prev"),
        ("para la musica", "computer_settings", "action", "media_stop"),
        ("pon en spotify coldplay", "computer_settings", "action", "spotify_play"),
        ("revisa mi correo", "gmail_summary", "max_results", "10"),
        ("tengo correos urgentes", "gmail_summary", "max_results", "10"),
        ("cierra tu aplicacion", "shutdown_app", "delay_seconds", "2.0"),
        ("cierra tu programa", "shutdown_app", "delay_seconds", "2.0"),
        ("apagate liseth", "shutdown_app", "delay_seconds", "2.0"),
        ("deten tu programa", "shutdown_app", "delay_seconds", "2.0"),
        ("tareas en segundo plano", "background_task", "action", "list"),
        ("cancela la tarea en segundo plano", "background_task", "action", "cancel"),
        ("estado del centinela", "workspace_sentinel", "action", "status"),
        ("escanea mis proyectos", "workspace_sentinel", "action", "scan"),
        ("mis rutinas", "execute_routine", "action", "list"),
        ("rutina de trabajo", "execute_routine", "routine", "focus"),
        ("rutina de la manana", "execute_routine", "routine", "morning"),
        ("rutina de cierre", "execute_routine", "routine", "wrap_up"),
        ("que hiciste hoy", "daily_debrief", "action", "summary"),
        ("bitacora de hoy", "daily_debrief", "action", "summary"),
        ("busca en internet sobre computacion cuantica", "web_search", "query", "computacion cuantica"),
        ("noticias de hoy sobre tecnologia", "web_search", "query", "tecnologia"),
        ("precio actual de bitcoin", "web_search", "query", "bitcoin"),
    ]

    for user_input, expected_tool, expected_key, expected_val in cases:
        intent = detect_direct_intent(user_input)
        assert intent is not None, f"Failed to detect intent for: '{user_input}'"
        tool_name, tool_args, _ = intent
        assert tool_name == expected_tool, f"Expected {expected_tool} but got {tool_name} for '{user_input}'"
        if expected_key:
            assert expected_val in str(tool_args.get(expected_key)), f"Expected {expected_val} in args[{expected_key}] for '{user_input}'"


def test_wake_words_and_command_extraction():
    """Verifies that wake words (Liseth, Liceth, Jarvis) are detected and stripped cleanly."""
    assert contains_wake_word("Liseth que hora es") is True
    assert contains_wake_word("oye liceth como estas") is True
    assert contains_wake_word("Jarvis abre chrome") is True
    assert contains_wake_word("Hola buenos dias") is False

    assert extract_command("Liseth abre la calculadora") == "abre la calculadora"
    assert extract_command("oye jarvis sube el volumen") == "sube el volumen"
    assert extract_command("Liceth, toma una captura") == "toma una captura"


@pytest.mark.asyncio
async def test_action_dispatcher_system_monitor():
    """Verifies that system telemetry is queried quickly via psutil without errors."""
    res = await action_dispatcher.execute_tool("system_monitor", {"metric": "all"})
    assert "Telemetría actual del sistema" in res
    assert "CPU" in res
    assert "RAM" in res
    assert "Disco" in res


@pytest.mark.asyncio
async def test_action_dispatcher_desktop_control():
    """Verifies desktop stats/listing tools."""
    res = await action_dispatcher.execute_tool("desktop_control", {"action": "stats"})
    assert isinstance(res, str)
    assert len(res) > 0


@pytest.mark.asyncio
async def test_action_dispatcher_background_monitor():
    """Verifies adding, listing, and removing topic monitors."""
    await action_dispatcher.execute_tool("background_monitor", {"action": "remove", "topic": "inteligencia artificial"})
    add_res = await action_dispatcher.execute_tool("background_monitor", {"action": "add", "topic": "inteligencia artificial"})
    assert "agregado" in add_res or "activo" in add_res

    list_res = await action_dispatcher.execute_tool("background_monitor", {"action": "list"})
    assert "inteligencia artificial" in list_res

    rem_res = await action_dispatcher.execute_tool("background_monitor", {"action": "remove", "topic": "inteligencia artificial"})
    assert "eliminado" in rem_res


@pytest.mark.asyncio
async def test_action_dispatcher_file_controller_safe():
    """Verifies file operations in a safe sandboxed temp folder."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "liseth_test.txt")

        # Create file
        create_res = await action_dispatcher.execute_tool("file_controller", {
            "action": "create_file",
            "path": test_file,
            "content": "Prueba de archivo para Liseth"
        })
        assert "creado" in create_res.lower() or os.path.exists(test_file)

        # Read file
        read_res = await action_dispatcher.execute_tool("file_controller", {
            "action": "read",
            "path": test_file
        })
        assert "Prueba de archivo para Liseth" in read_res

        # Delete file
        del_res = await action_dispatcher.execute_tool("file_controller", {
            "action": "delete",
            "path": test_file
        })
        assert not os.path.exists(test_file)


@pytest.mark.asyncio
async def test_brain_router_direct_intent_zero_latency():
    """Verifies that direct intents return immediately in generate_response without external network calls."""
    import time
    t0 = time.time()
    res = await brain_router.generate_response(prompt="abre la calculadora")
    elapsed = time.time() - t0

    assert res["brain"] == "native-automation"
    assert res["model"] == "direct-intent"
    assert len(res["executedTools"]) > 0
    assert res["executedTools"][0]["name"] == "open_app"
    # Should execute in less than 2.0s
    assert elapsed < 2.0


@pytest.mark.asyncio
async def test_action_dispatcher_screen_process(monkeypatch):
    """Verifies that screen_process tool integrates cleanly with action_dispatcher."""
    async def mock_screen_process(parameters=None):
        return "Veo su pantalla con código Python en el editor, señor Santiago."

    monkeypatch.setattr("app.actions.screen_processor.screen_process", mock_screen_process)
    res = await action_dispatcher.execute_tool("screen_process", {"query": "mira mi pantalla"})
    assert "pantalla" in res.lower()


@pytest.mark.asyncio
async def test_action_dispatcher_deep_work():
    """Verifies that deep_work action starts, reports status, and stops cleanly."""
    # 1. Start
    start_res = await action_dispatcher.execute_tool("deep_work", {"action": "start", "duration": 30, "task": "Refactor"})
    assert "activado" in start_res.lower()
    assert "30" in start_res

    # 2. Status
    status_res = await action_dispatcher.execute_tool("deep_work", {"action": "status"})
    assert "activa" in status_res.lower()
    assert "Refactor" in status_res

    # 3. Stop
    stop_res = await action_dispatcher.execute_tool("deep_work", {"action": "stop"})
    assert "finalizado" in stop_res.lower()


@pytest.mark.asyncio
async def test_clipboard_helper_detection_and_action(monkeypatch):
    """Verifies that clipboard types are categorized accurately and action execution works."""
    from app.actions.clipboard_helper import detect_clipboard_kind

    # 1. Classification tests
    assert detect_clipboard_kind("https://github.com/google/skills") == "url"
    assert detect_clipboard_kind('{"name": "Liseth", "version": 2}') == "json"
    assert detect_clipboard_kind("def process_data(x):\n    return x * 2") == "code"
    assert detect_clipboard_kind("Traceback (most recent call last):\n  File 'test.py', line 12, in <module>\nTypeError: unsupported operand") == "error"
    assert detect_clipboard_kind("Hola buenos días Santiago") == "text"
    assert detect_clipboard_kind("") == "empty"

    # 2. Action execution with mocked clipboard
    error_snippet = "Traceback (most recent call last):\n  File 'app.py', line 5\nZeroDivisionError: division by zero"
    monkeypatch.setattr("app.actions.clipboard_helper.get_clipboard_text", lambda: error_snippet)

    res = await action_dispatcher.execute_tool("smart_clipboard", {"action": "analyze"})
    assert "error" in res.lower() or "portapapeles" in res.lower()


@pytest.mark.asyncio
async def test_computer_settings_media_controls():
    """Verifies that media controls and Spotify handler return cleanly."""
    from app.actions.computer_settings import media_play_pause, media_next, media_prev, media_stop

    # 1. Direct function executions
    res_pp = media_play_pause()
    assert isinstance(res_pp, str)

    res_nxt = media_next()
    assert isinstance(res_nxt, str)

    res_prv = media_prev()
    assert isinstance(res_prv, str)

    res_stp = media_stop()
    assert isinstance(res_stp, str)

    # 2. Action dispatcher execution
    disp_res = await action_dispatcher.execute_tool("computer_settings", {"action": "media_play_pause"})
    assert isinstance(disp_res, str)


@pytest.mark.asyncio
async def test_gmail_smart_inbox_summary():
    """Verifies that Gmail smart summary filters urgent emails and ignores newsletters."""
    from app.connectors.google_workspace import google_connector

    sample_emails = [
        {
            "id": "1",
            "from": "CEO <jefe@empresa.com>",
            "subject": "Reunión urgente de directorio mañana",
            "snippet": "Por favor confirmar asistencia urgente a las 9am."
        },
        {
            "id": "2",
            "from": "Compañero <dev@empresa.com>",
            "subject": "Revisión de pull request",
            "snippet": "Te envié los cambios solicitados para revisar."
        },
        {
            "id": "3",
            "from": "Marketing <newsletter@tienda.com>",
            "subject": "Descuento del 50% de temporada",
            "snippet": "Aprovecha nuestras ofertas y promociones exclusivas."
        }
    ]

    summary = await google_connector.get_smart_inbox_summary(emails=sample_emails)
    assert "Resumen de su bandeja Gmail" in summary
    assert "🚨 Requieren su atención" in summary
    assert "Reunión urgente" in summary
    assert "📨 Mensajes generales" in summary
    assert "📢 Boletines y promociones ignorados" in summary
    assert "1" in summary  # 1 promo ignored


@pytest.mark.asyncio
async def test_action_dispatcher_shutdown_app():
    """Verifies that shutdown_app returns sweet farewell and handles parameters."""
    res = await action_dispatcher.execute_tool(
        "shutdown_app",
        {"delay_seconds": 0.1, "execute_exit": False}
    )
    assert "Hasta luego, señor Santiago" in res
    assert "Cerrando la aplicación" in res



