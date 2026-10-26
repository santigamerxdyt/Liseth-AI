"""
Personal Finance Action for JARVIS / Liseth.
Entrypoint for personal wealth management, expense tracking, and monthly budget reports.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.services.personal_finance_service import personal_finance_service

logger = logging.getLogger("jarvis.personal_finance_action")


def personal_finance_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    params = parameters or {}
    action = str(params.get("action") or "summary").lower().strip()

    try:
        if action in ["summary", "balance", "resumen", "estado", "reporte"]:
            month = params.get("month")
            sm = personal_finance_service.get_summary(month=month)
            return personal_finance_service.format_summary_markdown(sm)

        if action in ["add_expense", "gasto", "registrar_gasto"]:
            amount = float(params.get("amount") or 0.0)
            category = str(params.get("category") or "Alimentacion")
            desc = str(params.get("description") or params.get("concept") or "Gasto registrado")
            method = str(params.get("method") or "Contactless / Efectivo")

            if amount <= 0:
                return "Señor Santiago, indique un valor mayor a cero para registrar el gasto."

            e = personal_finance_service.add_entry(
                amount=amount,
                category=category,
                entry_type="expense",
                description=desc,
                payment_method=method
            )
            return f"✓ Gasto registrado: ${e['amount']:,.2f} COP en la categoría '{e['category']}' ({e['description']})."

        if action in ["add_income", "ingreso", "registrar_ingreso"]:
            amount = float(params.get("amount") or 0.0)
            category = str(params.get("category") or "Consultoria & Negocios")
            desc = str(params.get("description") or "Ingreso recibido")
            method = str(params.get("method") or "Transferencia / Bre-B")

            if amount <= 0:
                return "Señor Santiago, indique un valor mayor a cero para el ingreso."

            e = personal_finance_service.add_entry(
                amount=amount,
                category=category,
                entry_type="income",
                description=desc,
                payment_method=method
            )
            return f"✓ Ingreso registrado exitosamente: +${e['amount']:,.2f} COP en '{e['category']}' ({e['description']})."

        if action in ["set_budget", "presupuesto", "limite"]:
            category = str(params.get("category") or "Alimentacion")
            limit = float(params.get("limit") or params.get("amount") or 500000.0)
            res = personal_finance_service.set_budget_cap(category, limit)
            return f"✓ Límite de gasto mensual fijado para '{res['category']}': ${res['monthly_limit']:,.2f} COP."

        return f"Acción financiera '{action}' no reconocida. Opciones: 'summary', 'add_expense', 'add_income', 'set_budget'."

    except Exception as e:
        logger.error(f"Error in personal_finance_action: {e}", exc_info=True)
        return f"Error procesando finanzas personales: {str(e)}"
