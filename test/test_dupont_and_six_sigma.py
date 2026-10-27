# -*- coding: utf-8 -*-
"""
Unit tests for Module 45 (Pirámide DuPont, Altman Z''-Score & EVA),
Module 46 (Excelencia Operacional Lean Six Sigma, OEE & TOC),
and static audit of 100% frontend JS handler coverage.
"""

import re
from pathlib import Path

from app.services.dupont_altman_service import dupont_altman_service
from app.services.lean_six_sigma_service import lean_six_sigma_service
from app.actions.dupont_altman_action import dupont_altman_action
from app.actions.lean_six_sigma_action import lean_six_sigma_action
from app.services.action_dispatcher import SYSTEM_TOOL_DECLARATIONS


def test_dupont_altman_high_eva_and_safe_zone():
    res = dupont_altman_service.analyze_corporate_performance(
        company_name="Grupo Empresarial Andino S.A.S.",
        revenue=1200000000.0,
        ebit=216000000.0,
        net_income=126000000.0,
        total_assets=950000000.0,
        total_equity=475000000.0,
        working_capital=220000000.0,
        retained_earnings=190000000.0,
        wacc_pct=12.5,
        effective_tax_rate_pct=35.0,
        currency="COP"
    )

    assert res["company_name"] == "Grupo Empresarial Andino S.A.S."
    assert res["dupont_analysis"]["roe_pct"] == 26.53
    assert res["dupont_analysis"]["net_margin_pct"] == 10.5
    assert res["dupont_analysis"]["equity_multiplier"] == 2.0
    assert res["altman_z_score"]["z_double_prime"] > 5.85
    assert "ZONA SEGURA" in res["altman_z_score"]["zone"]
    assert res["eva_analysis"]["eva_amount"] > 0
    assert "CREACIÓN DE VALOR" in res["eva_analysis"]["value_creation_status"]


def test_dupont_altman_distress_and_negative_eva():
    res = dupont_altman_service.analyze_corporate_performance(
        company_name="Textiles en Reestructuración",
        revenue=650000000.0,
        ebit=25000000.0,
        net_income=5000000.0,
        total_assets=950000000.0,
        total_equity=150000000.0,
        working_capital=-40000000.0,
        retained_earnings=5000000.0,
        wacc_pct=16.0,
        currency="COP"
    )

    assert res["altman_z_score"]["z_double_prime"] < 4.15
    assert "ALERTA" in res["altman_z_score"]["zone"]
    assert res["eva_analysis"]["eva_amount"] < 0
    assert "DESTRUCCIÓN" in res["eva_analysis"]["value_creation_status"]


def test_dupont_altman_action_wrapper():
    output = dupont_altman_action({
        "company_name": "Holding Financiero del Valle",
        "revenue": 1500000000.0,
        "ebit": 300000000.0,
        "net_income": 180000000.0,
        "total_assets": 1000000000.0,
        "total_equity": 500000000.0,
        "working_capital": 250000000.0,
        "retained_earnings": 200000000.0,
        "wacc_pct": 12.0
    })
    assert "PIRÁMIDE DUPONT, ALTMAN Z''-SCORE & VALOR ECONÓMICO AGREGADO (EVA)" in output
    assert "Holding Financiero del Valle" in output
    assert "ROE DuPont:" in output


def test_lean_six_sigma_world_class_oee():
    res = lean_six_sigma_service.evaluate_operational_excellence(
        process_name="Planta Automatizada Clase Mundial",
        units_produced=10500,
        defect_opportunities_per_unit=5,
        total_defects=25,
        planned_production_minutes=480.0,
        downtime_minutes=18.0,
        ideal_cycle_time_seconds=2.5,
        customer_daily_demand=9500,
        usl=105.0,
        lsl=95.0,
        process_mean=100.1,
        process_std_dev=1.05
    )

    assert res["six_sigma_metrics"]["dpmo"] < 1000.0
    assert res["six_sigma_metrics"]["sigma_level"] >= 4.5
    assert res["six_sigma_metrics"]["cpk"] >= 1.33
    assert "CLASE MUNDIAL" in res["oee_metrics"]["oee_classification"]
    assert res["oee_metrics"]["oee_pct"] >= 85.0
    assert "FLUJO SINCRONIZADO" in res["lean_toc_metrics"]["takt_synchronization_status"]


def test_lean_six_sigma_bottleneck_and_low_cpk():
    res = lean_six_sigma_service.evaluate_operational_excellence(
        process_name="Línea con Cuello de Botella",
        units_produced=5000,
        defect_opportunities_per_unit=5,
        total_defects=450,
        planned_production_minutes=480.0,
        downtime_minutes=120.0,
        ideal_cycle_time_seconds=2.5,
        customer_daily_demand=9000,
        usl=105.0,
        lsl=95.0,
        process_mean=102.5,
        process_std_dev=1.9
    )

    assert res["six_sigma_metrics"]["cpk"] < 1.0
    assert "INCAPAZ" in res["six_sigma_metrics"]["capability_verdict"]
    assert res["oee_metrics"]["oee_pct"] < 70.0
    assert "CUELLO DE BOTELLA ACTIVO" in res["lean_toc_metrics"]["takt_synchronization_status"]


def test_lean_six_sigma_action_wrapper():
    output = lean_six_sigma_action({
        "process_name": "Centro Logístico Palmira",
        "units_produced": 10000,
        "total_defects": 40
    })
    assert "EXCELENCIA OPERACIONAL LEAN SIX SIGMA, OEE & TEORÍA DE RESTRICCIONES (TOC)" in output
    assert "Centro Logístico Palmira" in output
    assert "Efectividad Global de Equipos (OEE):" in output


def test_system_tool_declarations_73_and_zero_missing_onclick():
    tool_names = [t["name"] for t in SYSTEM_TOOL_DECLARATIONS]
    assert "dupont_altman_eva" in tool_names
    assert "lean_six_sigma" in tool_names
    assert len(SYSTEM_TOOL_DECLARATIONS) == 73

    html = Path("jarvis.html").read_text(encoding="utf-8")
    onclicks = set(re.findall(r'onclick="([a-zA-Z0-9_]+)\(', html))
    missing = []
    for fn in sorted(onclicks):
        if fn in ("if", "window", "document", "this", "localStorage", "navigator"):
            continue
        pat = rf"(function\s+{fn}\b|window\.{fn}\s*=|const\s+{fn}\s*=|let\s+{fn}\s*=)"
        if not re.search(pat, html):
            missing.append(fn)
    assert len(missing) == 0, f"Missing JS handlers in jarvis.html: {missing}"
