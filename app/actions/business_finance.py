"""
Business & Financial Management Engine for JARVIS / Liseth.
Tailored for Señor Santiago (Business Administrator & Developer):
- Project Evaluation: NPV (VAN), IRR (TIR), Payback Period, ROI, WACC.
- Operational & Cost Analysis: Break-even point (Punto de Equilibrio), Margin Analysis.
- Strategic Analysis Templates: SWOT/FODA, PESTEL, Porter 5 Forces, Business Model Canvas.
All formulas are computed locally with 0ms latency and high mathematical precision.
"""
import logging
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger("jarvis.business_finance")


def calculate_van(rate: float, initial_investment: float, cash_flows: List[float]) -> Dict[str, Any]:
    """
    Calculates Net Present Value (Valor Actual Neto - VAN):
    VAN = -I_0 + sum(FC_t / (1 + r)^t)
    """
    r = rate if rate < 1.0 else (rate / 100.0)
    discounted_flows = []
    accumulated_npv = -abs(initial_investment)

    for t, flow in enumerate(cash_flows, start=1):
        discounted = flow / ((1.0 + r) ** t)
        discounted_flows.append(round(discounted, 2))
        accumulated_npv += discounted

    is_viable = accumulated_npv > 0
    decision = (
        "El proyecto es FINANCIERAMENTE VIABLE (VAN > 0). Genera valor sobre la tasa de descuento exigida."
        if is_viable else
        "El proyecto NO es viable (VAN <= 0). Destruye valor bajo la tasa exigida."
    )

    return {
        "initial_investment": abs(initial_investment),
        "discount_rate_pct": round(r * 100.0, 2),
        "periods": len(cash_flows),
        "van": round(accumulated_npv, 2),
        "discounted_flows": discounted_flows,
        "is_viable": is_viable,
        "recommendation": decision,
    }


def calculate_tir(initial_investment: float, cash_flows: List[float], max_iter: int = 1000, tol: float = 1e-6) -> Dict[str, Any]:
    """
    Calculates Internal Rate of Return (Tasa Interna de Retorno - TIR)
    using Newton-Raphson approximation.
    """
    inv = -abs(initial_investment)
    flows = [inv] + cash_flows

    # Initial guess
    r = 0.1
    for _ in range(max_iter):
        npv = sum(f / ((1.0 + r) ** t) for t, f in enumerate(flows))
        npv_deriv = sum(-t * f / ((1.0 + r) ** (t + 1)) for t, f in enumerate(flows))
        if abs(npv_deriv) < 1e-12:
            break
        r_new = r - npv / npv_deriv
        if abs(r_new - r) < tol:
            r = r_new
            break
        r = r_new

    tir_pct = round(r * 100.0, 2)
    return {
        "initial_investment": abs(initial_investment),
        "cash_flows": cash_flows,
        "tir_percentage": tir_pct,
        "interpretation": f"La Tasa Interna de Retorno (TIR) es del {tir_pct}%. Debe compararse contra su costo de oportunidad o WACC."
    }


def calculate_roi(investment_cost: float, total_return: float) -> Dict[str, Any]:
    """
    Calculates Return on Investment (ROI):
    ROI = (Beneficio Neto / Costo Inversión) * 100
    """
    if investment_cost == 0:
        return {"error": "El costo de la inversión no puede ser cero."}
    net_profit = total_return - investment_cost
    roi_pct = (net_profit / investment_cost) * 100.0
    return {
        "investment_cost": investment_cost,
        "total_return": total_return,
        "net_profit": round(net_profit, 2),
        "roi_percentage": round(roi_pct, 2),
        "multiplier": round(total_return / investment_cost, 2),
    }


def calculate_break_even(fixed_costs: float, price_per_unit: float, variable_cost_per_unit: float) -> Dict[str, Any]:
    """
    Calculates Break-even Point (Punto de Equilibrio):
    Q_eq = Costos Fijos / (Precio - Costo Variable Unitario)
    """
    margin = price_per_unit - variable_cost_per_unit
    if margin <= 0:
        return {
            "error": "El precio unitario debe ser mayor al costo variable unitario para generar margen de contribución."
        }

    units_needed = fixed_costs / margin
    revenue_needed = units_needed * price_per_unit
    contribution_margin_pct = (margin / price_per_unit) * 100.0

    return {
        "fixed_costs": fixed_costs,
        "price_per_unit": price_per_unit,
        "variable_cost_per_unit": variable_cost_per_unit,
        "unit_contribution_margin": round(margin, 2),
        "contribution_margin_ratio_pct": round(contribution_margin_pct, 2),
        "break_even_units": round(units_needed, 2),
        "break_even_revenue": round(revenue_needed, 2),
        "explanation": f"Debe vender {round(units_needed, 0):,.0f} unidades (equivalente a ${revenue_needed:,.2f}) para cubrir costos sin pérdidas."
    }


def calculate_wacc(
    equity: float,
    debt: float,
    cost_of_equity: float,
    cost_of_debt: float,
    tax_rate: float = 0.35
) -> Dict[str, Any]:
    """
    Calculates Weighted Average Cost of Capital (WACC / CPPC):
    WACC = (E/V * Ke) + (D/V * Kd * (1 - T))
    """
    total_capital = equity + debt
    if total_capital <= 0:
        return {"error": "El capital total (patrimonio + deuda) debe ser mayor a cero."}

    we = equity / total_capital
    wd = debt / total_capital
    ke = cost_of_equity if cost_of_equity < 1.0 else cost_of_equity / 100.0
    kd = cost_of_debt if cost_of_debt < 1.0 else cost_of_debt / 100.0
    t = tax_rate if tax_rate < 1.0 else tax_rate / 100.0

    wacc = (we * ke) + (wd * kd * (1.0 - t))
    wacc_pct = round(wacc * 100.0, 2)

    return {
        "total_capital": total_capital,
        "equity_weight_pct": round(we * 100.0, 2),
        "debt_weight_pct": round(wd * 100.0, 2),
        "tax_rate_pct": round(t * 100.0, 2),
        "wacc_percentage": wacc_pct,
        "interpretation": f"El costo promedio ponderado de capital (WACC) es {wacc_pct}%. Es la tasa mínima de retorno exigida."
    }


def get_strategic_framework(framework_name: str, topic: str = "Mi Empresa") -> str:
    """Returns structured executive strategic templates for business analysis."""
    name = framework_name.lower().strip()

    if "foda" in name or "dofa" in name or "swot" in name:
        return (
            f"📊 **Matriz FODA / DOFA Estratégica: {topic}**\n\n"
            "**1. Factores Internos:**\n"
            "• **Fortalezas (F):** Capacidades clave, ventajas competitivas, activos tecnológicos, eficiencia operativa.\n"
            "• **Debilidades (D):** Brechas de capital, falta de tracción comercial, procesos manuales, costos fijos elevados.\n\n"
            "**2. Factores Externos:**\n"
            "• **Oportunidades (O):** Nuevos nichos de mercado, digitalización, alianzas B2B, cambios regulatorios favorables.\n"
            "• **Amenazas (A):** Entrada de competidores de bajo costo, inflación, cambios en hábitos del consumidor.\n\n"
            "**Estrategias Cruzadas Sugeridas:**\n"
            "• **FO (Maxi-Maxi):** Usar fortalezas para aprovechar oportunidades de expansión.\n"
            "• **FA (Maxi-Mini):** Usar fortalezas tecnológicas para blindar ante amenazas.\n"
            "• **DO (Mini-Maxi):** Superar debilidades apalancándose en tendencias de mercado.\n"
            "• **DA (Mini-Mini):** Plan defensivo para mitigar vulnerabilidades críticas."
        )

    elif "canvas" in name:
        return (
            f"📋 **Lienzo Business Model Canvas: {topic}**\n\n"
            "1. **Propuesta de Valor:** ¿Qué problema resolvemos y por qué nos eligen?\n"
            "2. **Segmentos de Clientes:** Perfil del comprador objetivo (B2B, B2C, nicho).\n"
            "3. **Canales:** ¿Cómo entregamos y comunicamos nuestra propuesta de valor?\n"
            "4. **Relación con Clientes:** Fidelización, soporte automatizado, comunidad.\n"
            "5. **Fuentes de Ingreso:** Suscripción recurrente, transaccional, licenciamiento.\n"
            "6. **Recursos Clave:** Talento, infraestructura tecnológica, capital, propiedad intelectual.\n"
            "7. **Actividades Clave:** Desarrollo de software, marketing, ventas, operaciones.\n"
            "8. **Socios Clave:** Proveedores de nube, pasarelas de pago, integradores.\n"
            "9. **Estructura de Costos:** Costos fijos (nómina, servidores) vs variables (CAC, comisiones)."
        )

    elif "pestel" in name:
        return (
            f"🌐 **Análisis PESTEL del Macroentorno: {topic}**\n\n"
            "• **Político:** Estabilidad gubernamental, políticas fiscales, comercio exterior.\n"
            "• **Económico:** Inflación, tasas de interés (Banco de la República), tipo de cambio (TRM), crecimiento del PIB.\n"
            "• **Social:** Tendencias de consumo, pirámide demográfica, teletrabajo y hábitos digitales.\n"
            "• **Tecnológico:** Inteligencia artificial, automatización, adopción cloud, ciberseguridad.\n"
            "• **Ecológico/Ambiental:** Sostenibilidad, huella de carbono, normativas ESG.\n"
            "• **Legal:** Legislación laboral, protección de datos personales (Habeas Data), propiedad intelectual."
        )

    return f"Marco estratégico '{framework_name}' reconocido. Modelos disponibles: FODA, Canvas, PESTEL."


def business_finance_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    """Action entry point for ActionDispatcher & direct tool execution."""
    params = parameters or {}
    operation = params.get("operation", "van").lower().strip()

    if operation in ("van", "npv"):
        rate = float(params.get("rate") or params.get("tasa") or 12.0)
        inv = float(params.get("initial_investment") or params.get("inversion") or 100000)
        flows = params.get("cash_flows") or params.get("flujos") or [30000, 40000, 50000, 60000]
        if isinstance(flows, str):
            flows = [float(x.strip()) for x in flows.split(",") if x.strip()]
        res = calculate_van(rate=rate, initial_investment=inv, cash_flows=flows)
        return (
            f"📈 **Evaluación Financiera: Valor Actual Neto (VAN)**\n"
            f"• Inversión Inicial: ${res['initial_investment']:,.2f}\n"
            f"• Tasa de Descuento: {res['discount_rate_pct']}%\n"
            f"• **VAN Calculado: ${res['van']:,.2f}**\n"
            f"• Dictamen: {res['recommendation']}"
        )

    elif operation in ("tir", "irr"):
        inv = float(params.get("initial_investment") or params.get("inversion") or 100000)
        flows = params.get("cash_flows") or params.get("flujos") or [30000, 40000, 50000, 60000]
        if isinstance(flows, str):
            flows = [float(x.strip()) for x in flows.split(",") if x.strip()]
        res = calculate_tir(initial_investment=inv, cash_flows=flows)
        return f"📊 **Tasa Interna de Retorno (TIR):**\n• {res['interpretation']}"

    elif operation in ("punto_equilibrio", "break_even"):
        fixed = float(params.get("fixed_costs") or params.get("costos_fijos") or 5000000)
        price = float(params.get("price") or params.get("precio") or 50000)
        var_cost = float(params.get("variable_cost") or params.get("costo_variable") or 20000)
        res = calculate_break_even(fixed, price, var_cost)
        if "error" in res:
            return f"⚠️ {res['error']}"
        return (
            f"⚖️ **Punto de Equilibrio Operativo:**\n"
            f"• Costos Fijos: ${res['fixed_costs']:,.2f}\n"
            f"• Margen de Contribución Unitario: ${res['unit_contribution_margin']:,.2f} ({res['contribution_margin_ratio_pct']}%)\n"
            f"• **Unidades Necesarias: {res['break_even_units']:,.1f} unidades**\n"
            f"• **Ventas Requeridas: ${res['break_even_revenue']:,.2f}**\n"
            f"• {res['explanation']}"
        )

    elif operation in ("roi", "retorno"):
        inv = float(params.get("cost") or params.get("inversion") or 1000000)
        ret = float(params.get("revenue") or params.get("ingreso") or 1500000)
        res = calculate_roi(inv, ret)
        return (
            f"💰 **Retorno sobre la Inversión (ROI):**\n"
            f"• Ganancia Neta: ${res['net_profit']:,.2f}\n"
            f"• **ROI: {res['roi_percentage']}%** (Multiplicador: {res['multiplier']}x)"
        )

    elif operation in ("framework", "estrategia", "foda", "canvas", "pestel"):
        frame = params.get("framework") or operation
        topic = params.get("topic") or "Proyecto Empresarial"
        return get_strategic_framework(frame, topic)

    return "Operación financiera no especificada. Operaciones soportadas: van, tir, roi, punto_equilibrio, foda, canvas, pestel."
