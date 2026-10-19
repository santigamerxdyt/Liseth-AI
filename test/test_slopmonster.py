"""
Automated Test Suite for SlopMonster & Deslop Service in Liseth.
Verifies AI pattern hunting, scoring (0 to 5), copy humanization,
action dispatching, and brain router intent classification.
"""

import pytest
from app.services.slopmonster_service import SlopMonsterService, slopmonster_service
from app.actions.slopmonster_action import slopmonster_action
from app.services.action_dispatcher import action_dispatcher
from app.services.brain_router import detect_direct_intent


class TestSlopMonsterService:
    """Tests for SlopMonsterService primitives."""

    def test_status_structure(self):
        st = slopmonster_service.get_status()
        assert isinstance(st, dict)
        assert "SlopMonster" in st["engine"]
        assert "Español" in st["languages_supported"]

    def test_detect_english_slop(self):
        ai_draft = """
        In today's fast-paced digital world, it is a testament to our cutting-edge technology
        that Acme seamlessly elevates your workflow. We delve into holistic synergies — not only
        providing a robust platform, but also empowering teams to unleash their potential.
        In conclusion, this is a game-changer.
        """
        audit = slopmonster_service.deslop_text(ai_draft, "Landing.md")
        assert audit["score"] <= 2.0
        assert audit["total_violations"] >= 4
        assert not audit["is_clean"]
        cats = audit["failed_categories"]
        assert "Vocabulario" in cats
        assert "Patrones de Oración" in cats

    def test_detect_spanish_slop(self):
        ai_draft_es = """
        En el vertiginoso mundo actual, profundizar en este tema es la piedra angular del éxito.
        Nuestra solución vanguardista no solo revoluciona el mercado, sino también empodera
        a cada usuario — permitiendo un viaje hacia la transformación sin fisuras.
        En conclusión, cabe destacar que representa un hito fundamental.
        """
        audit = slopmonster_service.deslop_text(ai_draft_es, "Ensayo.txt")
        assert audit["score"] <= 2.0
        assert audit["total_violations"] >= 4
        assert not audit["is_clean"]

    def test_clean_human_text_high_score(self):
        human_text = """
        We build software that helps teams ship updates faster.
        Our tool connects to your repository, runs tests automatically,
        and deploys clean builds directly to production servers.
        You can inspect every run in the dashboard.
        """
        audit = slopmonster_service.deslop_text(human_text, "README.md")
        assert audit["score"] >= 4.0
        assert audit["is_clean"] is True

    def test_humanize_rewrites_ai_cliches(self):
        cliche_text = """
        En el vertiginoso mundo actual, profundizar en las finanzas corporativas es vital.
        No solo ayuda a reducir costos, sino también eleva la rentabilidad — transformando el negocio.
        En conclusión, la clave está en el control.
        """
        res = slopmonster_service.humanize_text(cliche_text)
        assert res["changes_made"] >= 2
        cleansed = res["cleansed_text"]
        assert "En el vertiginoso mundo actual" not in cleansed
        assert "profundizar en" not in cleansed
        assert res["new_score"] > 2.0


class TestSlopMonsterAction:
    """Tests for slopmonster_action wrapper."""

    def test_action_status(self):
        out = slopmonster_action({"action": "status"})
        assert "SlopMonster" in out
        assert "Vocabulario" in out

    def test_action_deslop(self):
        out = slopmonster_action({
            "action": "deslop",
            "text": "In today's fast-paced world, delve into seamless synergies."
        })
        assert "Análisis Anti-Slop" in out
        assert "Vocabulario" in out

    def test_action_humanize(self):
        out = slopmonster_action({
            "action": "humanize",
            "text": "En el vertiginoso mundo actual, cabe destacar que nuestra plataforma es un tapiz de opciones."
        })
        assert "Texto Humanizado" in out
        assert "Versión Limpia" in out

    def test_action_missing_text(self):
        out = slopmonster_action({"action": "deslop"})
        assert "debe proporcionar el texto" in out.lower()


class TestBrainRouterSlopMonsterIntegration:
    """Tests zero-latency intent classification for SlopMonster in brain_router."""

    def test_status_intent(self):
        res = detect_direct_intent("Liseth como esta el estado de slopmonster")
        assert res is not None
        tool, args, prompt = res
        assert tool == "slopmonster"
        assert args.get("action") == "status"

    def test_humanize_text_intent(self):
        res = detect_direct_intent("humaniza este texto: 'En el vertiginoso mundo actual...'")
        assert res is not None
        tool, args, prompt = res
        assert tool == "slopmonster"
        assert args.get("action") == "humanize"

    def test_deslop_audit_intent(self):
        res = detect_direct_intent("analiza si parece ia este parrafo")
        assert res is not None
        tool, args, prompt = res
        assert tool == "slopmonster"
        assert args.get("action") == "deslop"


def test_action_dispatcher_slopmonster_integration():
    """Verifies slopmonster_action dispatches slopmonster calls."""
    res = slopmonster_action({"action": "status"})
    assert "SlopMonster" in res

