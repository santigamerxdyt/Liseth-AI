"""
Test suite verifying the Stark Mark 85 Universal Accessibility (WCAG 2.1 AA/AAA)
and Visual HUD Enhancements for Liseth (48 Tactical Modules).
"""
from pathlib import Path
import re
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
JARVIS_HTML = ROOT_DIR / "jarvis.html"
INDEX_HTML = ROOT_DIR / "index.html"
STATIC_INDEX_HTML = ROOT_DIR / "app" / "static" / "index.html"


def test_html_files_byte_identical():
    """Verify jarvis.html, index.html, and app/static/index.html are 100% in sync."""
    content_jarvis = JARVIS_HTML.read_bytes()
    content_index = INDEX_HTML.read_bytes()
    content_static = STATIC_INDEX_HTML.read_bytes()
    assert content_jarvis == content_index, "index.html is out of sync with jarvis.html"
    assert content_jarvis == content_static, "app/static/index.html is out of sync with jarvis.html"


def test_skip_links_present():
    """Verify WCAG 2.4.1 Bypass Blocks via skip-links for keyboard navigation."""
    content = JARVIS_HTML.read_text(encoding="utf-8")
    assert '<a href="#user-input" class="skip-link">Saltar al campo de entrada de chat (Alt+K)</a>' in content
    assert '<a href="#btn-hud-menu" class="skip-link">Saltar al Centro de Módulos HUD (Alt+H)</a>' in content
    assert ".skip-link" in content
    assert ".skip-link:focus" in content


def test_wcag_focus_visible_and_reduced_motion():
    """Verify keyboard focus rings and reduced-motion media query."""
    content = JARVIS_HTML.read_text(encoding="utf-8")
    # WCAG 2.4.7 Focus Visible
    assert ":focus-visible" in content
    assert "outline: 2px solid" in content
    # WCAG 2.3.3 Animation from Interactions / Reduced motion
    assert "@media (prefers-reduced-motion: reduce)" in content
    assert "body.a11y-reduced-motion" in content


def test_high_contrast_stark_mode():
    """Verify WCAG 1.4.6 High Contrast (Enhanced) mode definitions."""
    content = JARVIS_HTML.read_text(encoding="utf-8")
    assert "body.a11y-high-contrast" in content
    assert "#000000" in content
    assert "#00f0ff" in content


def test_touch_target_and_typography_scaling():
    """Verify minimum touch targets (44px) and scalable typography."""
    content = JARVIS_HTML.read_text(encoding="utf-8")
    assert "min-height: 44px" in content
    assert "min-width: 44px" in content
    assert "body.a11y-font-lg" in content
    assert "body.a11y-font-xl" in content
    assert "body.a11y-dyslexia" in content


def test_accessibility_modal_and_controls():
    """Verify presence of Accessibility Panel modal and trigger button."""
    content = JARVIS_HTML.read_text(encoding="utf-8")
    assert 'id="btn-a11y-panel"' in content
    assert 'id="a11y-modal"' in content
    assert 'role="dialog"' in content
    assert 'aria-modal="true"' in content
    assert 'id="btn-toggle-high-contrast"' in content
    assert 'id="btn-toggle-motion"' in content
    assert 'id="btn-toggle-dyslexia"' in content
    assert "setA11yFontSize" in content


def test_keyboard_shortcuts_and_persistence_js():
    """Verify keyboard shortcuts and localStorage persistence in JS engine."""
    content = JARVIS_HTML.read_text(encoding="utf-8")
    # Check hotkey handling
    assert "liseth_a11y_fontsize" in content
    assert "liseth_a11y_contrast" in content
    assert "liseth_a11y_motion" in content
    assert "liseth_a11y_dyslexia" in content
    assert "window.openA11yModal" in content
    assert "window.closeA11yModal" in content
    # Shortcuts Alt + A, Alt + H, Alt + K, Alt + M, Alt + V, Esc
    assert "Alt + A" in content
    assert "Alt + H" in content
    assert "Alt + K" in content
    assert "Alt + M" in content
    assert "Alt + V" in content
    assert 'e.key === "Escape"' in content
    assert 'e.altKey && (e.key === "m" || e.key === "M")' in content


def test_hud_modules_prominence_and_chips():
    """Verify that btn-hud-menu is at the front of .top-actions, quick chip exists, and header is responsive."""
    content = JARVIS_HTML.read_text(encoding="utf-8")
    # Exactly one button with id btn-hud-menu
    assert content.count('id="btn-hud-menu"') == 1
    # Check that btn-hud-menu is the very first button inside top-actions
    top_actions_idx = content.find('<div class="top-actions">')
    hud_menu_idx = content.find('id="btn-hud-menu"')
    assert top_actions_idx != -1 and hud_menu_idx != -1
    between = content[top_actions_idx:hud_menu_idx]
    # No other <button> before btn-hud-menu inside top-actions
    assert '<button' in between
    assert between.count('<button') == 1

    # Quick chip in main view
    assert 'id="btn-quick-hud-modules"' in content

    # Responsive styles
    assert "max-width: 1480px" in content
    assert "overflow-x: auto" in content


def test_hud_modules_search_and_finance_tab():
    """Verify search input, finance tab, and all 48 cards availability."""
    content = JARVIS_HTML.read_text(encoding="utf-8")
    assert 'id="hud-modules-search"' in content
    assert 'id="hud-visible-count-pill"' in content
    assert 'data-filter="finance"' in content
    assert "window.openHudModal" in content
    assert "filterHudModules" in content

    # Verify all 48 cards exist
    cards = re.findall(r'id="(hud-card-[^"]*)"', content)
    assert len(cards) == 48, f"Expected 48 cards, found {len(cards)}"

    # Specific check for newly added modules
    assert 'id="hud-card-marketing"' in content
    assert 'id="hud-card-talent"' in content
    assert 'id="hud-card-forex"' in content
    assert 'id="hud-card-a11y"' in content
    assert 'id="hud-card-esg"' in content
    assert 'id="hud-card-treasury"' in content
    assert 'id="hud-card-stock-trading"' in content
    assert 'id="hud-card-dividend-screener"' in content
    assert 'id="hud-card-bank-reconciliation"' in content
    assert 'id="hud-card-monte-carlo"' in content
    assert 'id="hud-card-pricing-elasticity"' in content
    assert 'id="hud-card-credit-amortization"' in content
    assert 'id="hud-card-business-canvas-ansoff"' in content
    assert 'id="hud-card-sagrilaft-compliance"' in content
    assert 'id="marketing-modal"' in content
    assert 'id="talent-modal"' in content
    assert 'id="forex-modal"' in content
    assert 'id="esg-modal"' in content
    assert 'id="treasury-modal"' in content
    assert 'id="stock-trading-modal"' in content
    assert 'id="dividend-screener-modal"' in content
    assert 'id="bank-reconciliation-modal"' in content
    assert 'id="monte-carlo-modal"' in content
    assert 'id="pricing-elasticity-modal"' in content
    assert 'id="credit-amortization-modal"' in content
    assert 'id="business-canvas-ansoff-modal"' in content
    assert 'id="sagrilaft-compliance-modal"' in content
    assert "window.openMarketingModal" in content
    assert "window.openTalentModal" in content
    assert "window.openForexModal" in content
    assert "window.openEsgModal" in content
    assert "window.openTreasuryModal" in content
    assert "window.openStockTradingModal" in content
    assert "window.openDividendScreenerModal" in content
    assert "window.openBankReconciliationModal" in content
    assert "window.openMonteCarloModal" in content
    assert "window.openPricingElasticityModal" in content
    assert "window.openCreditAmortizationModal" in content
    assert "window.openBusinessCanvasAnsoffModal" in content
    assert "window.openSagrilaftComplianceModal" in content
    assert 'id="hud-card-dupont-altman"' in content
    assert 'id="hud-card-lean-six-sigma"' in content
    assert 'id="dupont-altman-modal"' in content
    assert 'id="lean-six-sigma-modal"' in content
    assert "window.openDupontAltmanModal" in content
    assert "window.openLeanSixSigmaModal" in content
    assert 'id="hud-card-meeting-minutes"' in content
    assert 'id="hud-card-executive-prioritizer"' in content
    assert 'id="meeting-minutes-modal"' in content
    assert 'id="executive-prioritizer-modal"' in content
    assert "window.openMeetingMinutesModal" in content
    assert "window.openExecutivePrioritizerModal" in content
