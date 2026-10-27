"""
Unit tests for Predictive Intelligence & Anticipatory 3-Step Action Service.
"""

from app.services.predictive_intelligence_service import predictive_intelligence_service
from app.actions.predictive_intelligence_action import predictive_intelligence_action
from app.services.action_dispatcher import SYSTEM_TOOL_DECLARATIONS


def test_predictive_intelligence_steps():
    res = predictive_intelligence_service.get_anticipatory_plan()
    assert "steps" in res
    assert len(res["steps"]) == 3
    for s in res["steps"]:
        assert "title" in s
        assert "description" in s
        assert "action_prompt" in s
        assert "timing" in s
        assert "tag" in s
    assert "persona_status" in res
    assert "Chief of Staff" in res["persona_status"]["role"]


def test_predictive_intelligence_custom_context():
    res = predictive_intelligence_service.get_anticipatory_plan(context="Inversión inmobiliaria")
    assert "Inversión inmobiliaria" in res["steps"][0]["description"]


def test_predictive_intelligence_action_wrapper():
    output = predictive_intelligence_action({"context": "Bolsa de valores"})
    assert "INTELIGENCIA PREDICTIVA LISETH" in output
    assert "PENSANDO 3 PASOS ADELANTE" in output
    assert "PLAN ANTICIPATORIO SECUENCIAL" in output


def test_predictive_intelligence_registered_tool():
    names = [t["name"] for t in SYSTEM_TOOL_DECLARATIONS]
    assert "predictive_intelligence" in names
