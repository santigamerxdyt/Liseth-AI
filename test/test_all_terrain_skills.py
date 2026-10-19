"""
Automated Test Suite for All-Terrain ("Todo Terreno") Skills in Liseth AI:
1. Academic Researcher (OpenAlex, arXiv, Literature Reviews, APA 7th Edition)
2. Business Strategist & Corporate Finance (FODA, Porter, Canvas, Cash Flow, Amortization, WACC)
3. Data Science & ML Toolkit (Data Profiling, IQR Outliers, OLS Linear Regression, Time Series, Python Pipelines)
4. Workspace Automation (Bilingual Excel Formulas, Report Blueprints, Presentation Decks)
Verifies services, actions, dispatcher execution, and brain router zero-latency intents.
"""

import pytest
from app.services.academic_research_service import academic_research_service
from app.actions.academic_research_action import academic_research_action

from app.services.business_strategy_service import business_strategy_service
from app.actions.business_strategy_action import business_strategy_action

from app.services.data_ml_service import data_ml_service
from app.actions.data_ml_action import data_ml_action

from app.services.workspace_automation_service import workspace_automation_service
from app.actions.workspace_automation_action import workspace_automation_action

from app.services.brain_router import detect_direct_intent
from app.services.action_dispatcher import action_dispatcher


# =============================================================================
# 1. ACADEMIC RESEARCHER TESTS
# =============================================================================

class TestAcademicResearcher:
    def test_status_structure(self):
        st = academic_research_service.get_status()
        assert "Academic Researcher" in st["engine"]
        assert "APA" in st["citation_standard"]
        assert len(st["datasources"]) >= 2

    def test_apa_citation_formatting_single_author(self):
        paper = {
            "title": "Corporate Governance and Financial Performance",
            "authors": ["Hernández, Carlos"],
            "year": 2024,
            "journal": "Journal of Finance",
            "doi": "https://doi.org/10.1016/j.jfin.2024.01"
        }
        res = academic_research_service.format_apa_citation(paper)
        assert "(2024)" in res["bibliography"]
        assert "Hernández, C." in res["bibliography"]
        assert "https://doi.org/10.1016/j.jfin.2024.01" in res["bibliography"]
        assert "(Hernández, 2024)" == res["parenthetical"]
        assert "Hernández (2024)" == res["narrative"]

    def test_apa_citation_formatting_multiple_authors(self):
        paper = {
            "title": "Competitive Advantage in Latin America",
            "authors": ["Gómez, Felipe", "Rodríguez, Mariana", "Torres, Laura"],
            "year": 2023,
            "journal": "Strategic Management Review",
            "doi": "https://doi.org/10.1002/smj.123"
        }
        res = academic_research_service.format_apa_citation(paper)
        assert "(2023)" in res["bibliography"]
        assert "(Gómez et al., 2023)" == res["parenthetical"]
        assert "Gómez et al. (2023)" == res["narrative"]

    def test_search_papers_fallback_quality(self):
        papers = academic_research_service.search_papers("Finanzas corporativas y WACC", limit=2)
        assert len(papers) >= 1
        p = papers[0]
        assert "title" in p
        assert "authors" in p
        assert p["year"] > 2020

    def test_generate_literature_review(self):
        review = academic_research_service.generate_literature_review("Transformación Digital y Productividad")
        assert "Estado del Arte" in review
        assert "Normas APA" in review
        assert "Lista de Referencias Bibliográficas" in review

    def test_action_status_and_search(self):
        out_st = academic_research_action({"action": "status"})
        assert "Academic Researcher" in out_st

        out_search = academic_research_action({"action": "search", "query": "Estrategia empresarial"})
        assert "Artículos Científicos Encontrados" in out_search
        assert "APA 7" in out_search


# =============================================================================
# 2. BUSINESS STRATEGIST TESTS
# =============================================================================

class TestBusinessStrategist:
    def test_status_structure(self):
        st = business_strategy_service.get_status()
        assert "Business Strategy" in st["engine"]
        assert len(st["strategic_frameworks"]) >= 4

    def test_foda_generation(self):
        foda = business_strategy_service.generate_foda("Constructora Santiago SAS")
        assert "Constructora Santiago SAS" in foda
        assert "Fortalezas (F)" in foda
        assert "Oportunidades (O)" in foda
        assert "Estrategias FO" in foda
        assert "Estrategias DA" in foda

    def test_porter_generation(self):
        porter = business_strategy_service.generate_porter("Fintech y Banca Digital")
        assert "5 Fuerzas de Michael Porter" in porter
        assert "Rivalidad entre Competidores" in porter
        assert "Poder de Negociación" in porter

    def test_canvas_generation(self):
        canvas = business_strategy_service.generate_canvas("Plataforma SaaS de Logística")
        assert "Business Model Canvas" in canvas
        assert "Propuesta de Valor" in canvas
        assert "Segmentos de Clientes" in canvas
        assert "Estructura de Costos" in canvas

    def test_cash_flow_projection(self):
        cf = business_strategy_service.cash_flow_projection(100000, growth_rate=0.10, operating_margin=0.20, periods=3)
        assert "Flujo de Caja Libre" in cf
        assert "Año 1" in cf
        assert "Año 3" in cf
        assert "EBIT" in cf

    def test_loan_amortization_french_and_german(self):
        fr = business_strategy_service.loan_amortization_schedule(10000000, 15.0, 12, system="frances")
        assert "Sistema Francés (Cuota Fija)" in fr
        assert "Mes 1" in fr
        assert "Total Intereses Pagados" in fr

        de = business_strategy_service.loan_amortization_schedule(10000000, 15.0, 12, system="aleman")
        assert "Sistema Alemán (Amortización Constante)" in de
        assert "Mes 1" in de

    def test_wacc_calculation(self):
        wacc = business_strategy_service.calculate_wacc(
            equity=60000000,
            debt=40000000,
            cost_of_equity_pct=16.0,
            cost_of_debt_pct=10.0,
            tax_rate_pct=35.0
        )
        assert "WACC" in wacc
        assert "Patrimonio de Accionistas" in wacc
        assert "Tasa Interna de Retorno" in wacc

    def test_action_integration(self):
        out = business_strategy_action({"action": "foda", "organization": "Empresa Test"})
        assert "Empresa Test" in out
        out_w = business_strategy_action({"action": "wacc", "equity": 50000, "debt": 50000})
        assert "WACC" in out_w


# =============================================================================
# 3. DATA SCIENCE & MACHINE LEARNING TOOLKIT TESTS
# =============================================================================

class TestDataMLToolkit:
    def test_status_structure(self):
        st = data_ml_service.get_status()
        assert "Data Science & Machine Learning" in st["engine"]
        assert len(st["algorithms"]) >= 4

    def test_data_profiling_and_outliers(self):
        csv_data = "id,ventas,sucursal\n1,100,Norte\n2,110,Sur\n3,105,Norte\n4,95,Sur\n5,9999,Norte"
        rep = data_ml_service.profile_and_clean_data(csv_data)
        assert "Reporte de Perfilamiento" in rep
        assert "ventas" in rep
        assert "outliers detectados" in rep.lower()

    def test_linear_regression(self):
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        res = data_ml_service.linear_regression(x, y, predict_x=6)
        assert "Regresión Lineal" in res
        assert "R²" in res or "R^2" in res
        assert "12.00" in res  # predict_x = 6 should yield 12

    def test_time_series_forecast(self):
        vals = [100.0, 105.0, 110.0, 118.0, 125.0]
        res = data_ml_service.time_series_forecast(vals, periods_ahead=2)
        assert "Pronóstico de Series de Tiempo" in res
        assert "t + 1" in res
        assert "t + 2" in res

    def test_generate_ml_code(self):
        py_reg = data_ml_service.generate_ml_python_script("regression")
        assert "sklearn" in py_reg
        assert "Ridge" in py_reg

        py_clus = data_ml_service.generate_ml_python_script("clustering")
        assert "KMeans" in py_clus

    def test_action_integration(self):
        out = data_ml_action({"action": "regression", "x": "1,2,3,4", "y": "2,4,6,8", "predict_x": 5})
        assert "Regresión Lineal" in out
        assert "10.00" in out


# =============================================================================
# 4. WORKSPACE AUTOMATION TESTS
# =============================================================================

class TestWorkspaceAutomation:
    def test_status_structure(self):
        st = workspace_automation_service.get_status()
        assert "Workspace Automation" in st["engine"]
        assert len(st["modules"]) >= 3

    def test_excel_formula_generation(self):
        # 1. Lookup formula
        f_lookup = workspace_automation_service.generate_excel_formula("buscar cliente segun codigo")
        assert "BUSCARX" in f_lookup
        assert "XLOOKUP" in f_lookup

        # 2. Multi-criteria sum
        f_sum = workspace_automation_service.generate_excel_formula("sumar ventas con condicion de fecha y vendedor")
        assert "SUMAR.SI.CONJUNTO" in f_sum
        assert "SUMIFS" in f_sum

        # 3. Dynamic array
        f_filter = workspace_automation_service.generate_excel_formula("filtrar registros unicos mayores a 5000")
        assert "FILTRAR" in f_filter
        assert "FILTER" in f_filter

    def test_report_blueprint(self):
        bp_consulting = workspace_automation_service.generate_report_blueprint("Plan Estratégico 2026", doc_type="consultoria")
        assert "Informe de Consultoría" in bp_consulting
        assert "Resumen Ejecutivo" in bp_consulting

        bp_essay = workspace_automation_service.generate_report_blueprint("Ética y Liderazgo", doc_type="ensayo")
        assert "Ensayo Académico" in bp_essay
        assert "Tesis central" in bp_essay

    def test_presentation_deck(self):
        deck = workspace_automation_service.generate_presentation_deck("Estrategia Omnicanal", slide_count=4)
        assert "Presentación Ejecutiva" in deck
        assert "Diapositiva 1" in deck
        assert "Diapositiva 4" in deck
        assert "Speaker Notes" in deck

    def test_action_integration(self):
        out = workspace_automation_action({"action": "excel_formula", "query": "buscar precio de producto"})
        assert "BUSCARX" in out
        assert "XLOOKUP" in out


# =============================================================================
# 5. BRAIN ROUTER ZERO-LATENCY INTENT TESTS
# =============================================================================

class TestBrainRouterAllTerrainIntents:
    def test_academic_research_intents(self):
        res1 = detect_direct_intent("busca articulos sobre finanzas corporativas")
        assert res1 is not None
        tool, args, _ = res1
        assert tool == "academic_research"
        assert args.get("action") == "search"

        res2 = detect_direct_intent("estado del arte sobre inteligencia artificial en empresas")
        assert res2 is not None
        tool, args, _ = res2
        assert tool == "academic_research"
        assert args.get("action") == "literature_review"

    def test_business_strategy_intents(self):
        res1 = detect_direct_intent("matriz foda de Empresa Alpina")
        assert res1 is not None
        tool, args, _ = res1
        assert tool == "business_strategy"
        assert args.get("action") == "foda"
        assert "Alpina" in args.get("organization", "")

        res2 = detect_direct_intent("5 fuerzas de porter del sector bancario")
        assert res2 is not None
        tool, args, _ = res2
        assert tool == "business_strategy"
        assert args.get("action") == "porter"

        res3 = detect_direct_intent("modelo canvas de tienda de ropa online")
        assert res3 is not None
        tool, args, _ = res3
        assert tool == "business_strategy"
        assert args.get("action") == "canvas"

        res4 = detect_direct_intent("proyeccion de flujo de caja para el proximo año")
        assert res4 is not None
        tool, args, _ = res4
        assert tool == "business_strategy"
        assert args.get("action") == "cash_flow"

        res5 = detect_direct_intent("tabla de amortizacion de prestamo")
        assert res5 is not None
        tool, args, _ = res5
        assert tool == "business_strategy"
        assert args.get("action") == "amortization"

        res6 = detect_direct_intent("calcula el wacc de mi empresa")
        assert res6 is not None
        tool, args, _ = res6
        assert tool == "business_strategy"
        assert args.get("action") == "wacc"

    def test_data_ml_intents(self):
        res1 = detect_direct_intent("script de machine learning para regresion")
        assert res1 is not None
        tool, args, _ = res1
        assert tool == "data_ml_toolkit"
        assert args.get("action") == "code"

    def test_workspace_automation_intents(self):
        res1 = detect_direct_intent("formula de excel para buscar clientes")
        assert res1 is not None
        tool, args, _ = res1
        assert tool == "workspace_automation"
        assert args.get("action") == "excel_formula"

        res2 = detect_direct_intent("estructura de informe de consultoria gerencial")
        assert res2 is not None
        tool, args, _ = res2
        assert tool == "workspace_automation"
        assert args.get("action") == "report_blueprint"

        res3 = detect_direct_intent("diapositivas para reunion de inversionistas")
        assert res3 is not None
        tool, args, _ = res3
        assert tool == "workspace_automation"
        assert args.get("action") == "presentation_deck"
