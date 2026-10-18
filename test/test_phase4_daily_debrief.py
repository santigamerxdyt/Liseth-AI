"""
Tests for Phase 4: DailyDebriefService and Autonomous Activity Ledger.
"""
import pytest
from app.services.daily_debrief_service import DailyDebriefService, daily_debrief_service
from app.actions.daily_debrief_action import daily_debrief_action


def test_log_and_retrieve_entries():
    service = DailyDebriefService()
    entry = service.log_activity(
        category="background_task",
        title="Compilación de dependencias",
        details="5 librerías actualizadas con éxito"
    )

    assert entry.title == "Compilación de dependencias"
    assert entry.category == "background_task"

    entries = service.get_entries(category="background_task")
    assert len(entries) >= 1
    assert any(e.title == "Compilación de dependencias" for e in entries)


def test_generate_debrief_with_data():
    service = DailyDebriefService()
    service.log_activity("background_task", "Test Runner", "101 pruebas ejecutadas")
    service.log_activity("routine", "Rutina Matutina", "Completada")
    service.log_activity("sentinel", "Auditoría de Código", "Sin errores de sintaxis")

    debrief = service.generate_debrief()
    assert "Reporte Ejecutivo" in debrief
    assert "Tareas en Segundo Plano" in debrief
    assert "Rutinas Automatizadas" in debrief
    assert "Centinela de Código" in debrief


def test_daily_debrief_action_wrapper():
    # 1. Summary
    res_summary = daily_debrief_action({"action": "summary"})
    assert isinstance(res_summary, str)
    assert len(res_summary) > 0

    # 2. List
    res_list = daily_debrief_action({"action": "list"})
    assert isinstance(res_list, str)
    assert len(res_list) > 0


def test_daily_debrief_direct_intents():
    from app.services.brain_router import detect_direct_intent

    cases = [
        ("que hiciste hoy", "daily_debrief", "action", "summary"),
        ("que has hecho hoy", "daily_debrief", "action", "summary"),
        ("resumen del dia", "daily_debrief", "action", "summary"),
        ("bitacora de hoy", "daily_debrief", "action", "summary"),
        ("reporte ejecutivo", "daily_debrief", "action", "summary"),
        ("lista de actividades de hoy", "daily_debrief", "action", "list"),
        ("bitacora de eventos", "daily_debrief", "action", "list"),
    ]

    for phrase, expected_tool, expected_key, expected_val in cases:
        intent = detect_direct_intent(phrase)
        assert intent is not None, f"Failed for '{phrase}'"
        tool_name, tool_args, _ = intent
        assert tool_name == expected_tool, f"Expected {expected_tool} for '{phrase}', got {tool_name}"
        assert tool_args.get(expected_key) == expected_val

