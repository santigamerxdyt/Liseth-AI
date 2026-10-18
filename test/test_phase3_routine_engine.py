"""
Tests for Phase 3: RoutineEngine and Automated Multi-step Routines.
"""
import pytest
from app.services.routine_engine import RoutineEngine, routine_engine
from app.actions.routine_action import routine_action


def test_list_available_routines():
    routines = routine_engine.list_available_routines()
    assert len(routines) >= 3
    ids = [r["id"] for r in routines]
    assert "morning" in ids
    assert "focus" in ids
    assert "wrap_up" in ids


def test_execute_morning_routine():
    engine = RoutineEngine()
    result = engine.execute_routine("morning")
    assert result.success is True
    assert "Rutina Matutina" in result.summary
    assert len(result.step_results) >= 2
    step_names = [s.step_name for s in result.step_results]
    assert "Pronóstico del Clima" in step_names


def test_execute_focus_routine():
    engine = RoutineEngine()
    result = engine.execute_routine("focus")
    assert result.success is True
    assert "Concentración" in result.summary or "Trabajo" in result.summary
    assert len(result.step_results) >= 2


def test_execute_wrap_up_routine():
    engine = RoutineEngine()
    result = engine.execute_routine("wrap_up")
    assert result.success is True
    assert "Cierre" in result.summary
    assert len(result.step_results) >= 2


def test_routine_action_wrapper():
    # 1. List
    res_list = routine_action({"action": "list"})
    assert "Rutinas Automatizadas Disponibles" in res_list

    # 2. History
    res_hist = routine_action({"action": "history"})
    assert isinstance(res_hist, str)

    # 3. Execute
    res_exec = routine_action({"action": "execute", "routine": "focus"})
    assert "ejecutada exitosamente" in res_exec


def test_routine_direct_intents():
    from app.services.brain_router import detect_direct_intent

    cases = [
        ("mis rutinas", "execute_routine", "action", "list"),
        ("rutina de la mañana", "execute_routine", "routine", "morning"),
        ("inicia mi rutina de la mañana", "execute_routine", "routine", "morning"),
        ("rutina de trabajo", "execute_routine", "routine", "focus"),
        ("rutina de concentracion", "execute_routine", "routine", "focus"),
        ("rutina de cierre", "execute_routine", "routine", "wrap_up"),
        ("finalizar jornada", "execute_routine", "routine", "wrap_up"),
    ]

    for phrase, expected_tool, expected_key, expected_val in cases:
        intent = detect_direct_intent(phrase)
        assert intent is not None, f"Failed for '{phrase}'"
        tool_name, tool_args, _ = intent
        assert tool_name == expected_tool, f"Expected {expected_tool} for '{phrase}', got {tool_name}"
        assert tool_args.get(expected_key) == expected_val

