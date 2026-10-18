"""
Unit tests for HeartbeatService and Gatekeeper autonomous components.
"""
import time
from unittest.mock import MagicMock, patch
import pytest

from app.services.heartbeat_service import Gatekeeper, HeartbeatService


def test_gatekeeper_quiet_hours():
    gk = Gatekeeper(quiet_hours_start=23, quiet_hours_end=7)
    with patch("app.services.heartbeat_service.datetime") as mock_dt:
        mock_now = MagicMock()
        mock_now.hour = 2  # 2:00 AM
        mock_dt.now.return_value = mock_now
        assert gk.is_quiet_hours() is True

        mock_now.hour = 14  # 2:00 PM
        assert gk.is_quiet_hours() is False


def test_gatekeeper_can_speak_cooldown():
    gk = Gatekeeper(voice_cooldown_secs=100)
    gk.is_quiet_hours = MagicMock(return_value=False)
    gk.is_fullscreen_or_busy = MagicMock(return_value=False)

    # Initial state
    assert gk.can_speak("normal") is True

    # Mark spoken
    gk.last_voice_alert_time = time.time()
    # Immediate subsequent call should be blocked by cooldown
    assert gk.can_speak("normal") is False

    # But high or critical priority bypasses cooldown
    assert gk.can_speak("high") is True
    assert gk.can_speak("critical") is True


def test_gatekeeper_quiet_hours_blocks_normal_voice():
    gk = Gatekeeper()
    gk.is_quiet_hours = MagicMock(return_value=True)

    # Normal voice blocked during quiet hours
    assert gk.can_speak("normal") is False
    assert gk.can_speak("high") is False

    # Only critical emergency bypasses quiet hours
    assert gk.can_speak("critical") is True


def test_heartbeat_service_start_stop():
    hb = HeartbeatService()
    assert hb.is_running is False

    hb.start()
    assert hb.is_running is True

    hb.stop()
    assert hb.is_running is False


def test_heartbeat_hardware_sentinel_high_ram_detection():
    hb = HeartbeatService()
    hb.dispatch_proactive_alert = MagicMock()

    # Simulate 2 consecutive checks of RAM > 90%
    with patch("psutil.virtual_memory") as mock_vm, \
         patch("psutil.cpu_percent") as mock_cpu, \
         patch("psutil.disk_usage") as mock_disk:

        mock_vm.return_value.percent = 94.0
        mock_cpu.return_value = 20.0
        mock_disk.return_value.free = 50 * (1024 ** 3)

        # Streak 1
        hb._check_hardware_sentinel()
        assert hb._high_ram_streak == 1
        hb.dispatch_proactive_alert.assert_not_called()

        # Streak 2 -> Triggers alert
        hb._check_hardware_sentinel()
        assert hb._high_ram_streak == 2
        hb.dispatch_proactive_alert.assert_called_once()
        args, kwargs = hb.dispatch_proactive_alert.call_args
        assert "Centinela de Recursos" in kwargs.get("title", args[0] if args else "")
        assert "94%" in kwargs.get("message", args[1] if len(args) > 1 else "")


def test_heartbeat_dispatch_proactive_alert_event():
    hb = HeartbeatService()
    hb.gatekeeper.can_speak = MagicMock(return_value=True)

    with patch("app.services.voice_engine.voice_engine.broadcast_event") as mock_broadcast, \
         patch("app.services.voice_engine.voice_engine.speak") as mock_speak:

        hb.dispatch_proactive_alert(
            title="Prueba Autónoma",
            message="Mensaje de prueba de autonomía",
            priority="normal",
            allow_voice=True,
        )

        mock_broadcast.assert_called_once()
        mock_speak.assert_called_once_with("Mensaje de prueba de autonomía")


def test_commitment_service_lifecycle():
    from app.services.commitment_service import CommitmentService
    cs = CommitmentService()

    # Add commitment
    item = cs.add_commitment(text="Revisar servidor de base de datos", due_time="14:00", priority="high")
    assert item["id"].startswith("comm_")
    assert item["text"] == "Revisar servidor de base de datos"
    assert item["status"] == "pending"

    # List pending
    pending = cs.list_commitments(status="pending")
    assert any(c["id"] == item["id"] for c in pending)

    # Format summary
    summary = cs.format_commitments_summary()
    assert "Revisar servidor de base de datos" in summary

    # Mark completed
    assert cs.complete_commitment(item["id"]) is True
    completed = cs.list_commitments(status="completed")
    assert any(c["id"] == item["id"] for c in completed)

    # Delete
    assert cs.delete_commitment(item["id"]) is True


def test_heartbeat_daily_briefing_synthesis():
    hb = HeartbeatService()
    hb.dispatch_proactive_alert = MagicMock()

    with patch("app.actions.weather_report.fetch_weather_report") as mock_weather:
        mock_weather.return_value = {
            "ok": True,
            "city": "Bogotá",
            "summary": "En Bogotá tenemos actualmente 17°C con cielo parcialmente nublado."
        }
        hb._synthesize_and_send_briefing()

        hb.dispatch_proactive_alert.assert_called_once()
        args, kwargs = hb.dispatch_proactive_alert.call_args
        title = kwargs.get("title", args[0] if args else "")
        msg = kwargs.get("message", args[1] if len(args) > 1 else "")

        assert title == "Resumen Matutino"
        assert "Santiago" in msg
        assert "17°C" in msg


def test_heartbeat_execute_scheduled_tasks():
    hb = HeartbeatService()
    hb._synthesize_and_send_briefing = MagicMock()
    hb._check_hardware_sentinel = MagicMock()
    hb._check_calendar_events = MagicMock()
    hb._check_commitments = MagicMock()
    hb.dispatch_proactive_alert = MagicMock()

    # Daily summary task
    res1 = hb.execute_scheduled_task({"type": "daily_summary", "title": "Resumen"})
    assert "iniciado" in res1

    # Hardware check task
    res2 = hb.execute_scheduled_task({"type": "process_report", "title": "Hardware"})
    assert "ejecutada" in res2
    hb._check_hardware_sentinel.assert_called_once()

    # Event / commitments task
    res3 = hb.execute_scheduled_task({"type": "event_check", "title": "Eventos"})
    assert "ejecutada" in res3
    hb._check_commitments.assert_called_once()


def test_weather_report_action_and_open_meteo():
    from app.actions.weather_report import weather_action, fetch_weather_report

    # Real or fallback weather report
    res = fetch_weather_report("Bogotá")
    assert "temperature" in res
    assert "summary" in res

    action_text = weather_action({"city": "Bogotá"})
    assert len(action_text) > 10
    assert "Bogotá" in action_text or "clima" in action_text.lower()


def test_detect_direct_intent_weather_and_commitments():
    from app.services.brain_router import detect_direct_intent

    # Weather intent
    intent_w = detect_direct_intent("cómo está el clima hoy")
    assert intent_w is not None
    assert intent_w[0] == "weather_report"

    intent_rain = detect_direct_intent("va a llover hoy?")
    assert intent_rain is not None
    assert intent_rain[0] == "weather_report"

    # Commitments intent
    intent_c = detect_direct_intent("qué tengo pendiente?")
    assert intent_c is not None
    assert intent_c[0] == "manage_commitments"

    intent_c2 = detect_direct_intent("cuales son mis compromisos")
    assert intent_c2 is not None
    assert intent_c2[0] == "manage_commitments"


def test_gatekeeper_dnd_mode():
    from app.services.voice_engine import voice_engine
    voice_engine.is_speaking = False
    voice_engine.is_thinking = False

    gk = Gatekeeper()
    gk.is_quiet_hours = MagicMock(return_value=False)
    gk.is_fullscreen_or_busy = MagicMock(return_value=False)
    gk.is_in_call_or_meeting = MagicMock(return_value=False)

    assert gk.dnd_mode is False
    assert gk.can_speak("normal") is True

    # Enable DND
    gk.enable_dnd()
    assert gk.dnd_mode is True
    # In DND, normal and high voice are completely blocked
    assert gk.can_speak("normal") is False
    assert gk.can_speak("high") is False
    # Critical emergency bypasses DND
    assert gk.can_speak("critical") is True

    # Disable DND
    gk.disable_dnd()
    assert gk.dnd_mode is False
    assert gk.can_speak("normal") is True


def test_gatekeeper_in_call_detection_blocks_speech():
    from app.services.voice_engine import voice_engine
    voice_engine.is_speaking = False
    voice_engine.is_thinking = False

    gk = Gatekeeper()
    gk.is_quiet_hours = MagicMock(return_value=False)
    gk.is_fullscreen_or_busy = MagicMock(return_value=False)

    # When user is in call
    gk.is_in_call_or_meeting = MagicMock(return_value=True)
    assert gk.can_speak("normal") is False
    assert gk.can_speak("high") is False
    assert gk.can_speak("critical") is True

    # When call ends
    gk.is_in_call_or_meeting = MagicMock(return_value=False)
    assert gk.can_speak("normal") is True


def test_calendar_service_lifecycle():
    from app.services.calendar_service import CalendarService
    from datetime import datetime, timedelta

    cs = CalendarService()
    now = datetime.now()
    meeting_time = (now + timedelta(minutes=10)).strftime("%H:%M")

    # Add meeting
    evt = cs.add_event(
        summary="Reunión con inversionistas",
        start_time=meeting_time,
        meeting_link="https://meet.google.com/test-abc",
    )
    assert evt["id"].startswith("evt_")
    assert evt["summary"] == "Reunión con inversionistas"
    assert evt["meeting_link"] == "https://meet.google.com/test-abc"

    # Check upcoming within 15 min lead time
    upcoming = cs.check_upcoming_events(lead_minutes=15)
    assert any(e["id"] == evt["id"] for e in upcoming)

    # Mark alerted
    cs.mark_alerted(evt["id"])
    upcoming_after = cs.check_upcoming_events(lead_minutes=15)
    assert not any(e["id"] == evt["id"] for e in upcoming_after)

    # Daily agenda
    agenda = cs.format_daily_agenda()
    assert "Reunión con inversionistas" in agenda
    assert "videollamada" in agenda

    # Delete
    assert cs.delete_event(evt["id"]) is True


def test_optimize_memory_action():
    from app.actions.system_monitor import optimize_memory
    res = optimize_memory()
    assert isinstance(res, str)
    assert "RAM" in res or "Memoria" in res or "Optimización" in res


def test_detect_direct_intents_dnd_ram_calendar():
    from app.services.brain_router import detect_direct_intent

    # DND
    dnd_on = detect_direct_intent("activa el modo no molestar")
    assert dnd_on is not None
    assert dnd_on[0] == "toggle_dnd"
    assert dnd_on[1].get("enabled") is True

    dnd_off = detect_direct_intent("desactiva no molestar")
    assert dnd_off is not None
    assert dnd_off[0] == "toggle_dnd"
    assert dnd_off[1].get("enabled") is False

    # RAM
    ram = detect_direct_intent("libera la memoria por favor")
    assert ram is not None
    assert ram[0] == "optimize_ram"

    # Calendar
    cal = detect_direct_intent("qué reuniones tengo hoy?")
    assert cal is not None
    assert cal[0] == "manage_calendar"


def test_deep_work_manager_session_and_completion():
    from app.actions.deep_work import deep_work_manager

    # 1. Start
    res = deep_work_manager.start_session(duration_minutes=1, task="Investigación")
    assert res["status"] == "started"
    assert deep_work_manager.is_active is True

    # 2. Before completion
    assert deep_work_manager.check_completion() is None

    # 3. Simulate completion
    deep_work_manager.target_end_time = 0.0
    alert = deep_work_manager.check_completion()
    assert alert is not None
    assert "concluido exitosamente" in alert
    assert "Investigación" in alert
    assert deep_work_manager.is_active is False


