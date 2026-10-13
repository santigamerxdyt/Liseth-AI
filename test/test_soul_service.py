"""
Unit tests for SOUL service, persistent memories, and modular skills.
"""
import pytest
from app.services.soul_service import SoulService, soul_service


def test_soul_service_reads_soul():
    soul = soul_service.get_soul()
    assert "Liseth" in soul
    assert "Santiago" in soul


def test_soul_service_lists_skills():
    skills = soul_service.list_skills()
    assert isinstance(skills, list)
    skill_names = [s["name"] for s in skills]
    assert "contratos" in skill_names
    assert "resumen_agenda" in skill_names
    assert "redaccion_email" in skill_names


def test_soul_service_builds_enriched_system_instruction():
    instruction = soul_service.build_system_instruction("Instrucción temporal de prueba")
    assert "IDENTIDAD Y REGLAS DE LISETH (SOUL)" in instruction
    assert "Liseth" in instruction
    assert "HABILIDADES (SKILLS) DISPONIBLES" in instruction
    assert "contratos" in instruction
    assert "Instrucción temporal de prueba" in instruction


def test_soul_service_memory_append():
    original = soul_service.get_system_memory()
    test_note = "Prueba de nota de memoria temporal unit test"
    try:
        success = soul_service.append_memory(test_note, target="memory")
        assert success is True
        mem = soul_service.get_system_memory()
        assert test_note in mem
    finally:
        from app.services.soul_service import MEMORY_FILE
        MEMORY_FILE.write_text(original, encoding="utf-8")
