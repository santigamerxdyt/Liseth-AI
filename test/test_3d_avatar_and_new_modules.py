"""
Test suite for 3D WebGL Holographic Avatar, Live Market Ticker Tape,
and Modules 47 & 48 (Meeting Minutes AI & Executive Prioritizer Eisenhower 2.0).
"""
import re
import pytest
from pathlib import Path

from app.services.meeting_minutes_service import meeting_minutes_service
from app.services.executive_prioritizer_service import executive_prioritizer_service
from app.actions.meeting_minutes_action import meeting_minutes_action
from app.actions.executive_prioritizer_action import executive_prioritizer_action
from app.services.action_dispatcher import SYSTEM_TOOL_DECLARATIONS

ROOT_DIR = Path(__file__).resolve().parent.parent
JARVIS_HTML = ROOT_DIR / "jarvis.html"
INDEX_HTML = ROOT_DIR / "index.html"
STATIC_INDEX_HTML = ROOT_DIR / "app" / "static" / "index.html"
THREE_JS = ROOT_DIR / "app" / "static" / "js" / "three.min.js"


def test_threejs_asset_exists_and_valid():
    """Verify Three.js bundle is locally cached for desktop 3D WebGL rendering."""
    assert THREE_JS.exists(), "app/static/js/three.min.js does not exist"
    size = THREE_JS.stat().st_size
    assert size > 500_000, f"Three.js file too small: {size} bytes"


def test_meeting_minutes_service_extraction():
    """Test AI extraction of meeting minutes into structured executive decisions and tasks."""
    notes = (
        "Reunión de Junta Directiva 2026-10-27. "
        "Participantes: Santiago (CEO), Laura Gómez (CFO), Martín Silva (CTO). "
        "Decisión: Aprobar presupuesto de $120M COP para expansión de infraestructura en la nube. "
        "Decisión: Implementar nuevo protocolo SAGRILAFT para onboarding de proveedores internacionales. "
        "Compromiso: Laura presentará flujo de caja proyectado para el viernes. "
        "Compromiso: Martín liderará auditoría de seguridad y migración a Kubernetes antes del 15 de noviembre."
    )
    res = meeting_minutes_service.extract_minutes_and_actions(
        meeting_title="Junta Directiva Ordinaria",
        attendees="Santiago (CEO), Laura Gómez (CFO), Martín Silva (CTO)",
        raw_notes_or_transcript=notes
    )
    assert res["meeting_title"] == "Junta Directiva Ordinaria"
    assert len(res["executive_summary"]) == 3
    assert len(res["approved_decisions"]) >= 2
    assert len(res["action_items"]) >= 2

    # Check action item structure
    first_item = res["action_items"][0]
    assert "task" in first_item
    assert "owner" in first_item
    assert "deadline" in first_item
    assert "priority" in first_item
    assert "status" in first_item

    # Check follow-up email draft
    assert "follow_up_email_draft" in res
    assert "Asunto:" in res["follow_up_email_draft"]
    assert "Junta Directiva" in res["follow_up_email_draft"]


def test_meeting_minutes_action_wrapper():
    """Test the action dispatcher wrapper for meeting minutes extractor."""
    result = meeting_minutes_action({
        "meeting_title": "Comité Comercial",
        "attendees": "Santiago Huerfano, Carlos López",
        "notes": "Definir meta de ventas de Q4 en 450 millones. Responsable: Carlos López para el 30 de octubre."
    })
    assert isinstance(result, str)
    assert "ACTA EJECUTIVA CON IA & EXTRACTOR DE COMPROMISOS" in result
    assert "Comité Comercial" in result
    assert "BORRADOR DE CORREO DE SEGUIMIENTO" in result


def test_executive_prioritizer_service():
    """Test Eisenhower 2.0 evaluation and CEO focus index calculation."""
    items = [
        {"title": "Cerrar ronda Serie A con venture capital", "estimated_hours": 3.0, "urgency": "alta", "importance": "estrategica", "quadrant": "Q2"},
        {"title": "Atender requerimiento urgente de SuperSociedades", "estimated_hours": 2.0, "urgency": "inmediata", "importance": "critica", "quadrant": "Q1"},
        {"title": "Coordinar cotización de papelería y suministros", "estimated_hours": 1.5, "urgency": "alta", "importance": "operativa", "quadrant": "Q3"},
        {"title": "Revisar newsletters y correos de spam", "estimated_hours": 1.0, "urgency": "baja", "importance": "baja", "quadrant": "Q4"}
    ]
    res = executive_prioritizer_service.evaluate_priorities(
        ceo_name="Santiago Huerfano",
        items=items,
        working_hours_day=9.0
    )
    assert res["ceo_name"] == "Santiago Huerfano"
    assert "quadrants" in res
    assert "q1_urgent_critical" in res["quadrants"]
    assert "q2_strategic_high_value" in res["quadrants"]
    assert "q3_urgent_delegate" in res["quadrants"]
    assert "q4_eliminate" in res["quadrants"]

    # Check metrics
    m = res["metrics"]
    assert "strategic_focus_index_pct" in m
    assert 0.0 <= m["strategic_focus_index_pct"] <= 100.0
    assert "urgency_trap_index_pct" in m
    assert len(res["directives"]) >= 1


def test_executive_prioritizer_action_wrapper():
    """Test action dispatcher wrapper for executive prioritization."""
    result = executive_prioritizer_action({
        "ceo_name": "Santiago Huerfano",
        "working_hours_day": 8.5
    })
    assert isinstance(result, str)
    assert "MATRIZ DE PRIORIZACIÓN CEO EISENHOWER 2.0" in result
    assert "Santiago Huerfano" in result
    assert "Índice de Foco Estratégico (Q2)" in result


def test_action_dispatcher_tools_count_and_declarations():
    """Verify tool definitions in SYSTEM_TOOL_DECLARATIONS (total 75 tools)."""
    assert len(SYSTEM_TOOL_DECLARATIONS) == 75, f"Expected 75 tools, got {len(SYSTEM_TOOL_DECLARATIONS)}"
    names = [t["name"] for t in SYSTEM_TOOL_DECLARATIONS]
    assert "meeting_minutes_extractor" in names
    assert "executive_prioritizer" in names


def test_ui_and_html_elements_presence():
    """Verify 3D WebGL Avatar, ticker tape, and cards 47 & 48 in jarvis.html."""
    html = JARVIS_HTML.read_text(encoding="utf-8")

    # 3D Desktop Avatar elements
    assert 'id="liseth-3d-avatar-container"' in html
    assert 'id="liseth-3d-canvas"' in html
    assert 'id="btn-avatar-3d"' in html
    assert "setAvatarMode('avatar3d')" in html
    assert 'initLiseth3DAvatar' in html
    assert 'three.min.js' in html

    # Market Ticker Tape (Pure CSS3 Hardware Accelerated Scrolling Tape)
    assert 'id="executive-ticker-tape"' in html
    assert 'id="ticker-tape-track"' in html
    assert 'tickerScroll' in html
    assert 'ticker-item' in html

    # Modules 47 & 48
    assert 'id="hud-card-meeting-minutes"' in html
    assert 'id="hud-card-executive-prioritizer"' in html
    assert 'id="meeting-minutes-modal"' in html
    assert 'id="executive-prioritizer-modal"' in html
    assert 'window.openMeetingMinutesModal' in html
    assert 'window.openExecutivePrioritizerModal' in html
    assert 'submitMeetingMinutes' in html
    assert 'submitExecutivePrioritizer' in html


def test_zero_missing_onclick_handlers():
    """Ensure every onclick handler in jarvis.html corresponds to an existing JS function."""
    html = JARVIS_HTML.read_text(encoding="utf-8")
    onclicks = set(re.findall(r'onclick="([a-zA-Z0-9_]+)\(', html))
    missing = []
    for fn in sorted(onclicks):
        if fn in ("if", "window", "document", "this", "localStorage", "navigator"):
            continue
        pat = rf"(function\s+{fn}\b|window\.{fn}\s*=|const\s+{fn}\s*=|let\s+{fn}\s*=)"
        if not re.search(pat, html):
            missing.append(fn)
    assert len(missing) == 0, f"Missing JS handlers in jarvis.html: {missing}"


def test_dynamic_tab_responsive_system():
    """Verify dynamic tab and window resize engine and responsive media query coverage."""
    html = JARVIS_HTML.read_text(encoding="utf-8")

    # JavaScript Engine
    assert "updateLisethDynamicLayout" in html
    assert "window.recalculateLisethLayout" in html
    assert "ResizeObserver" in html
    assert "data-tab-width" in html
    assert "data-tab-height" in html
    assert "liseth:layout-adapted" in html

    # CSS Responsive Breakpoints for Tab Resizing
    assert "@media (min-width: 1600px)" in html
    assert "@media (max-width: 1200px) and (min-width: 961px)" in html
    assert "@media (max-width: 960px) and (min-width: 769px)" in html
    assert "@media (max-height: 720px)" in html
    assert "@media (max-height: 560px)" in html


def test_html_files_byte_parity():
    """Ensure jarvis.html, index.html, and app/static/index.html have identical bytes."""
    b_jarvis = JARVIS_HTML.read_bytes()
    b_index = INDEX_HTML.read_bytes()
    b_static = STATIC_INDEX_HTML.read_bytes()

    assert len(b_jarvis) == len(b_index) == len(b_static)
    assert b_jarvis == b_index == b_static
