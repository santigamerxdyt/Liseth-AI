"""
Business Strategy Action for JARVIS / Liseth.
Entrypoint for strategic matrices (FODA, Porter, Canvas) and corporate finance models (Cash Flow, Amortization, WACC).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.services.business_strategy_service import business_strategy_service

logger = logging.getLogger("jarvis.business_strategy_action")


def business_strategy_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    """
    Synchronous entrypoint for Business Strategy & Corporate Finance.
    Handles: 'status', 'foda', 'porter', 'canvas', 'cash_flow', 'amortization', 'wacc'.
    """
    params = parameters or {}
    action = params.get("action", "status").lower().strip()

    try:
        if action in ["status", "estado", "info"]:
            st = business_strategy_service.get_status()
            return business_strategy_service.format_status_report(st)

        if action in ["foda", "swot", "matriz_foda"]:
            target = params.get("organization") or params.get("company") or params.get("topic") or "Mi Empresa / Proyecto"
            return business_strategy_service.generate_foda(target)

        if action in ["porter", "cinco_fuerzas", "fuerzas_porter"]:
            industry = params.get("industry") or params.get("sector") or params.get("topic") or "Sector Comercial"
            return business_strategy_service.generate_porter(industry)

        if action in ["pestel", "matriz_pestel", "analisis_pestel"]:
            topic = params.get("topic") or params.get("industry") or params.get("sector") or "Sector Empresarial"
            return business_strategy_service.generate_pestel(topic)

        if action in ["canvas", "business_model", "modelo_canvas"]:
            topic = params.get("topic") or params.get("business") or params.get("company") or "Negocio Digital"
            return business_strategy_service.generate_canvas(topic)

        if action in ["cash_flow", "flujo_caja", "proyeccion"]:
            revenue = float(params.get("revenue") or params.get("initial_revenue") or 100000.0)
            growth = float(params.get("growth") or params.get("growth_rate") or 0.15)
            margin = float(params.get("margin") or params.get("operating_margin") or 0.25)
            tax = float(params.get("tax") or params.get("tax_rate") or 0.35)
            periods = int(params.get("periods") or 5)
            return business_strategy_service.cash_flow_projection(
                initial_revenue=revenue,
                growth_rate=growth,
                operating_margin=margin,
                tax_rate=tax,
                periods=periods
            )

        if action in ["amortization", "amortizacion", "prestamo", "credito"]:
            principal = float(params.get("principal") or params.get("amount") or 50000.0)
            rate = float(params.get("rate") or params.get("annual_rate") or 18.0)
            months = int(params.get("months") or params.get("periods") or 12)
            system = params.get("system") or "frances"
            return business_strategy_service.loan_amortization_schedule(
                principal=principal,
                annual_rate_pct=rate,
                months=months,
                system=system
            )

        if action in ["wacc", "costo_capital", "cppc"]:
            equity = float(params.get("equity") or 60000.0)
            debt = float(params.get("debt") or 40000.0)
            ke = float(params.get("ke") or params.get("cost_of_equity") or 15.0)
            kd = float(params.get("kd") or params.get("cost_of_debt") or 10.0)
            tax = float(params.get("tax") or 35.0)
            return business_strategy_service.calculate_wacc(
                equity=equity,
                debt=debt,
                cost_of_equity_pct=ke,
                cost_of_debt_pct=kd,
                tax_rate_pct=tax
            )

        return f"Acción de estrategia de negocio '{action}' no reconocida. Opciones: 'foda', 'porter', 'canvas', 'cash_flow', 'amortization', 'wacc', 'status'."

    except Exception as e:
        logger.error(f"Error in business_strategy_action: {e}", exc_info=True)
        return f"Error ejecutando análisis estratégico: {str(e)}"
