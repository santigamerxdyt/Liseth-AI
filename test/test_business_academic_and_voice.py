"""
Comprehensive test suite for:
- Business Administration & Financial Models (VAN, TIR, ROI, Punto de Equilibrio, WACC, FODA, Canvas)
- University & Academic Assistant (Normas APA 7, Ensayos, Informes)
- Data & Developer Tools (Estadística Descriptiva, JSON a Markdown, CSV a SQL)
- Voice Engine Low-Latency Optimizations
- Direct Intent 0ms routing for all new modules
"""
import pytest
from app.actions.business_finance import (
    calculate_van,
    calculate_tir,
    calculate_roi,
    calculate_break_even,
    calculate_wacc,
    get_strategic_framework,
    business_finance_action,
)
from app.actions.academic_helper import (
    generate_apa_citation,
    get_academic_structure,
    academic_helper_action,
)
from app.actions.data_dev_tools import (
    compute_descriptive_stats,
    json_to_markdown_table,
    csv_to_sql_inserts,
    data_dev_tools_action,
)
from app.services.brain_router import detect_direct_intent
from app.services.voice_engine import voice_engine


# ── 1. Business Administration & Finance Tests ───────────────────────────────

def test_calculate_van():
    # Example: Initial Inv = 100,000, Flows = [30000, 40000, 50000, 60000], Rate = 10%
    res = calculate_van(rate=10.0, initial_investment=100000, cash_flows=[30000, 40000, 50000, 60000])
    assert res["is_viable"] is True
    assert res["van"] > 0
    assert "FINANCIERAMENTE VIABLE" in res["recommendation"]


def test_calculate_tir():
    res = calculate_tir(initial_investment=100000, cash_flows=[30000, 40000, 50000, 60000])
    assert res["tir_percentage"] > 10.0
    assert "Tasa Interna de Retorno" in res["interpretation"]


def test_calculate_roi():
    res = calculate_roi(investment_cost=1000000, total_return=1500000)
    assert res["roi_percentage"] == 50.0
    assert res["net_profit"] == 500000.0
    assert res["multiplier"] == 1.5


def test_calculate_break_even():
    # Fixed costs = 5,000,000, Price = 50,000, Variable Cost = 20,000
    res = calculate_break_even(fixed_costs=5000000, price_per_unit=50000, variable_cost_per_unit=20000)
    assert round(res["break_even_units"]) == 167
    assert res["unit_contribution_margin"] == 30000.0


def test_calculate_wacc():
    res = calculate_wacc(equity=60000000, debt=40000000, cost_of_equity=15.0, cost_of_debt=8.0, tax_rate=35.0)
    assert res["wacc_percentage"] > 0
    assert "WACC" in res["interpretation"]


def test_strategic_frameworks():
    foda = get_strategic_framework("foda", "TechCo")
    assert "Matriz FODA" in foda
    assert "Fortalezas" in foda
    assert "Oportunidades" in foda

    canvas = get_strategic_framework("canvas", "TechCo")
    assert "Business Model Canvas" in canvas
    assert "Propuesta de Valor" in canvas


def test_business_finance_action():
    res = business_finance_action({"operation": "van", "rate": 12.0, "inversion": 50000, "flujos": [20000, 30000, 25000]})
    assert "Valor Actual Neto" in res
    assert "VAN Calculado" in res


# ── 2. Academic & University Helper Tests ────────────────────────────────────

def test_generate_apa_citation_book():
    res = generate_apa_citation(
        source_type="book",
        authors="Kotler, P., & Keller, K. L.",
        year="2016",
        title="Dirección de marketing",
        publisher="Pearson Educación"
    )
    assert "Kotler" in res["bibliographic_reference"]
    assert "Dirección de marketing" in res["bibliographic_reference"]
    assert "Pearson" in res["bibliographic_reference"]
    assert "(Kotler et al., 2016)" in res["in_text_parenthetical"]


def test_generate_apa_citation_journal():
    res = generate_apa_citation(
        source_type="journal",
        authors="Porter, M. E.",
        year="2008",
        title="The Five Competitive Forces That Shape Strategy",
        journal="Harvard Business Review",
        volume="86",
        issue="1",
        pages="78-93"
    )
    assert "Harvard Business Review" in res["bibliographic_reference"]
    assert "78-93" in res["bibliographic_reference"]


def test_get_academic_structure():
    essay = get_academic_structure("ensayo", "Liderazgo Transformacional")
    assert "Ensayo Académico" in essay
    assert "Introducción" in essay
    assert "Desarrollo Argumentativo" in essay
    assert "Conclusiones" in essay

    report = get_academic_structure("informe", "Transformación Digital")
    assert "Informe Ejecutivo" in report
    assert "Resumen Ejecutivo" in report


def test_academic_helper_action():
    res_normas = academic_helper_action({"action": "normas"})
    assert "Normas APA 7ª Edición" in res_normas
    assert "Márgenes" in res_normas

    res_apa = academic_helper_action({"action": "apa", "authors": "Chiavenato, I.", "year": "2020", "title": "Administración de Recursos Humanos", "publisher": "McGraw-Hill"})
    assert "Chiavenato" in res_apa
    assert "Referencia Bibliográfica" in res_apa


# ── 3. Data & Developer Tools Tests ─────────────────────────────────────────

def test_compute_descriptive_stats():
    data = [10.0, 20.0, 30.0, 40.0, 50.0]
    stats = compute_descriptive_stats(data)
    assert stats["count"] == 5
    assert stats["mean"] == 30.0
    assert stats["median"] == 30.0
    assert stats["min"] == 10.0
    assert stats["max"] == 50.0


def test_json_to_markdown_table():
    sample_json = [
        {"Mes": "Enero", "Ventas": 15000, "Margen": "35%"},
        {"Mes": "Febrero", "Ventas": 18000, "Margen": "38%"}
    ]
    table = json_to_markdown_table(sample_json)
    assert "| Mes | Ventas | Margen |" in table
    assert "| Enero | 15000 | 35% |" in table


def test_csv_to_sql_inserts():
    csv_sample = "id,nombre,precio\n1,Software ERP,1200\n2,Consultoria,800"
    sql = csv_to_sql_inserts("productos", csv_sample)
    assert "INSERT INTO `productos`" in sql
    assert "Software ERP" in sql


def test_data_dev_tools_action():
    res = data_dev_tools_action({"operation": "stats", "data": "100, 200, 300, 400"})
    assert "Análisis Estadístico Descriptivo" in res
    assert "Media (Promedio): 250.00" in res


# ── 4. Direct Intents Tests for All New Domains ─────────────────────────────

def test_direct_intents_business_academic():
    cases = [
        ("calcula el van", "business_finance", "operation", "van"),
        ("calcula la tir", "business_finance", "operation", "tir"),
        ("calcula el roi", "business_finance", "operation", "roi"),
        ("punto de equilibrio", "business_finance", "operation", "punto_equilibrio"),
        ("matriz foda", "business_strategy", "action", "foda"),
        ("modelo canvas", "business_strategy", "action", "canvas"),
        ("analisis pestel", "business_strategy", "action", "pestel"),
        ("normas apa", "academic_helper", "action", "normas"),
        ("cita apa", "academic_helper", "action", "apa"),
        ("estructura de ensayo", "academic_helper", "action", "estructura"),
        ("estructura de informe", "academic_helper", "action", "estructura"),
        ("estadistica descriptiva", "data_dev_tools", "operation", "stats"),
    ]

    for phrase, expected_tool, expected_key, expected_val in cases:
        intent = detect_direct_intent(phrase)
        assert intent is not None, f"Failed for '{phrase}'"
        tool_name, tool_args, _ = intent
        assert tool_name == expected_tool, f"Expected {expected_tool} for '{phrase}', got {tool_name}"
        assert tool_args.get(expected_key) == expected_val


# ── 5. VoiceEngine Latency Configuration Verification ────────────────────────

def test_voice_engine_optimizations():
    # Recognizer pause threshold should be 0.5s for snappy turn-taking
    assert voice_engine._recognizer.pause_threshold == 0.5
    # Energy threshold optimized
    assert voice_engine._recognizer.energy_threshold == 280
    assert voice_engine._recognizer.non_speaking_duration == 0.3
