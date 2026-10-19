# -*- coding: utf-8 -*-
"""
Tests for UNAL Palmira Business Administration Pensum Academic Service and Action.
Acuerdo 19 de 2012 / Acuerdo 033 de 2007 (Facultad de Ingeniería y Administración).
"""

import pytest
import asyncio
from app.services.unal_pensum_service import unal_pensum_service
from app.actions.unal_pensum_action import unal_pensum_action
from app.services.action_dispatcher import action_dispatcher
from app.services.brain_router import detect_direct_intent


def test_pensum_overview():
    """Verify curricular structure totals 166 credits according to Acuerdo 19 de 2012."""
    overview = unal_pensum_service.get_pensum_overview()
    assert overview["total_creditos"] == 166
    assert overview["fundamentacion_creditos"] == 35
    assert overview["disciplinar_creditos"] == 97
    assert overview["libre_eleccion_creditos"] == 34
    assert overview["duracion_semestres"] == 10
    assert "Sede Palmira" in overview["sede"]


def test_get_subject_by_code():
    """Verify lookup by exact SIA subject code."""
    res = unal_pensum_service.get_subject_details("5000859")
    assert res is not None
    assert "Administración" in res["nombre"]
    assert res["creditos"] == 4
    assert res["semestre"] == 1

    grado = unal_pensum_service.get_subject_details("5000943")
    assert grado is not None
    assert "Trabajo de Grado" in grado["nombre"]
    assert grado["creditos"] == 6
    assert grado["semestre"] == 10
    assert "80% créditos disciplinar" in grado["prerrequisitos"]


def test_get_subject_by_name_fuzzy():
    """Verify fuzzy lookup by subject name."""
    res = unal_pensum_service.get_subject_details("costos")
    assert res is not None
    assert "Costos" in res["nombre"]

    res_fin = unal_pensum_service.get_subject_details("administracion financiera")
    assert res_fin is not None
    assert "Financiera" in res_fin["nombre"]


def test_prerequisites_chain():
    """Verify prerequisite chain analysis."""
    prereqs_grado = unal_pensum_service.get_prerequisites_chain("Trabajo de Grado")
    assert "materia" in prereqs_grado
    assert prereqs_grado["materia"]["codigo"] == "5000943"
    assert "80% créditos disciplinar" in prereqs_grado["materia"]["prerrequisitos"]

    prereqs_presup = unal_pensum_service.get_prerequisites_chain("Presupuestos")
    assert len(prereqs_presup["prerrequisitos_directos"]) >= 1
    assert any("5000852" in p["codigo"] for p in prereqs_presup["prerrequisitos_directos"])


def test_semester_subjects():
    """Verify retrieving subjects for specific semesters."""
    sem1 = unal_pensum_service.get_semester_subjects(1)
    assert len(sem1) >= 3
    assert any(s["codigo"] == "5000859" for s in sem1)

    sem10 = unal_pensum_service.get_semester_subjects(10)
    assert any("Trabajo de Grado" in a["nombre"] for a in sem10)


def test_graduation_audit():
    """Verify graduation credit audit checks and percentages."""
    audit_early = unal_pensum_service.audit_graduation_checklist(credits_approved=45)
    assert audit_early["porcentaje_avance"] == 27.1
    assert audit_early["consultoria_habilitada"] is False
    assert audit_early["trabajo_grado_habilitado"] is False

    audit_consultoria = unal_pensum_service.audit_graduation_checklist(credits_approved=115)
    assert audit_consultoria["consultoria_habilitada"] is True

    audit_grad = unal_pensum_service.audit_graduation_checklist(credits_approved=166)
    assert audit_grad["porcentaje_avance"] == 100.0
    assert audit_grad["consultoria_habilitada"] is True
    assert audit_grad["trabajo_grado_habilitado"] is True


def test_normative_framework():
    """Verify Colombian regulatory framework lookups."""
    norm_labor = unal_pensum_service.get_normative_framework("laboral")
    assert "CST" in norm_labor or "Código Sustantivo del Trabajo" in norm_labor

    norm_pub = unal_pensum_service.get_normative_framework("contratacion publica")
    assert "80" in norm_pub


def test_action_execution():
    """Verify unal_pensum_action handles multiple actions."""
    res_overview = unal_pensum_action({"action": "overview"})
    assert "Sede Palmira" in res_overview
    assert "166" in res_overview

    res_subject = unal_pensum_action({"action": "subject", "query": "5000859"})
    assert "Administración" in res_subject

    res_prereq = unal_pensum_action({"action": "prerequisites", "query": "Trabajo de Grado"})
    assert "80%" in res_prereq or "78" in res_prereq

    res_sem = unal_pensum_action({"action": "semester", "semester": 5})
    assert "Matrícula 5" in res_sem

    res_audit = unal_pensum_action({"action": "checklist", "credits_approved": 70})
    assert "Checklist" in res_audit

    res_norm = unal_pensum_action({"action": "normative", "query": "tributario"})
    assert "Estatuto Tributario" in res_norm


def test_action_dispatcher_unal_pensum():
    """Verify unal_pensum is registered in SYSTEM_TOOL_DECLARATIONS."""
    from app.services.action_dispatcher import SYSTEM_TOOL_DECLARATIONS
    tools = [t["name"] for t in SYSTEM_TOOL_DECLARATIONS]
    assert "unal_pensum" in tools


def test_zero_latency_direct_intents():
    """Verify zero-latency router catches UNAL curriculum queries directly."""
    intent_overview = detect_direct_intent("muestrame mi pensum de administracion")
    assert intent_overview is not None
    assert intent_overview[0] == "unal_pensum"
    assert intent_overview[1]["action"] == "overview"

    intent_sem = detect_direct_intent("que materias veo en el semestre 4")
    assert intent_sem is not None
    assert intent_sem[0] == "unal_pensum"
    assert intent_sem[1]["action"] == "semester"
    assert intent_sem[1]["semester"] == 4

    intent_prereq = detect_direct_intent("cuales son los prerrequisitos de consultoria")
    assert intent_prereq is not None
    assert intent_prereq[0] == "unal_pensum"
    assert intent_prereq[1]["action"] == "prerequisites"

    intent_audit = detect_direct_intent("auditoria de creditos para grado con 80 creditos")
    assert intent_audit is not None
    assert intent_audit[0] == "unal_pensum"
    assert intent_audit[1]["action"] == "checklist"
    assert intent_audit[1]["credits_approved"] == 80
