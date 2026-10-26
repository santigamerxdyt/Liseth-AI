"""
Personal Finance & Smart Budgeting Service for JARVIS / Liseth.
Manages personal cash flow, expense categorisation, monthly budget caps,
predictive burn-rate analysis, and direct linkage with contactless NFC payments.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvis.personal_finance")

DEFAULT_CATEGORIES = [
    "Alimentacion",
    "Transporte",
    "Educacion UNAL",
    "Servicios & Hogar",
    "Consultoria & Negocios",
    "Entretenimiento",
    "Inversion & Ahorro",
    "Otros"
]

DEFAULT_BUDGET_CAPS = {
    "Alimentacion": 650000.0,
    "Transporte": 220000.0,
    "Educacion UNAL": 300000.0,
    "Servicios & Hogar": 350000.0,
    "Entretenimiento": 180000.0,
    "Inversion & Ahorro": 500000.0
}


class PersonalFinanceService:
    """
    Personal Wealth & Financial Administration Engine for Señor Santiago.
    Provides proactive budget surveillance and financial metrics according to
    classical managerial accounting principles.
    """

    def __init__(self):
        self._entries: List[Dict[str, Any]] = []
        self._budgets: Dict[str, float] = dict(DEFAULT_BUDGET_CAPS)
        self._seed_initial_data()

    def _seed_initial_data(self):
        """Seeds realistic recent entries so dashboard displays immediately."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        seeds = [
            {"type": "income", "category": "Consultoria & Negocios", "amount": 1500000.0, "desc": "Honorarios Asesoría Financiera WACC", "method": "Bre-B Contactless"},
            {"type": "expense", "category": "Alimentacion", "amount": 45000.0, "desc": "Almuerzo Ejecutivo & Café", "method": "NFC Nequi"},
            {"type": "expense", "category": "Transporte", "amount": 18000.0, "desc": "Transporte Intermunicipal Palmira-Cali", "method": "Efectivo"},
            {"type": "expense", "category": "Educacion UNAL", "amount": 65000.0, "desc": "Material Académico & Fotocopias FIA", "method": "Daviplata Tap"},
            {"type": "expense", "category": "Alimentacion", "amount": 120000.0, "desc": "Compras de Supermercado", "method": "Tarjeta Contactless"},
            {"type": "income", "category": "Consultoria & Negocios", "amount": 850000.0, "desc": "Elaboración de Matriz Estratégica & Flujo de Caja", "method": "Transferencia"}
        ]
        for s in seeds:
            eid = f"FIN-{uuid.uuid4().hex[:6].upper()}"
            self._entries.append({
                "id": eid,
                "date": today,
                "type": s["type"],
                "category": s["category"],
                "amount": float(s["amount"]),
                "currency": "COP",
                "description": s["desc"],
                "payment_method": s["method"],
                "created_at": datetime.now(timezone.utc).isoformat()
            })

    def get_status(self) -> Dict[str, Any]:
        """Returns the operational status of the finance engine."""
        return {
            "engine": "Liseth Personal Wealth & Budgeting Engine (v1.0)",
            "categories": DEFAULT_CATEGORIES,
            "budget_caps": self._budgets,
            "total_entries": len(self._entries),
            "status": "ONLINE"
        }

    def add_entry(
        self,
        amount: float,
        category: str,
        entry_type: str = "expense",
        description: str = "Gasto general",
        payment_method: str = "Contactless / Efectivo",
        currency: str = "COP",
        date: Optional[str] = None,
        nfc_ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """Registers a new financial transaction (income or expense)."""
        eid = f"FIN-{uuid.uuid4().hex[:6].upper()}"
        d = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        t = entry_type.lower().strip()
        cat = category.strip()

        entry = {
            "id": eid,
            "date": d,
            "type": t,
            "category": cat,
            "amount": float(amount),
            "currency": currency.upper(),
            "description": description,
            "payment_method": payment_method,
            "nfc_ref": nfc_ref,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        self._entries.append(entry)
        return entry

    def set_budget_cap(self, category: str, monthly_limit: float) -> Dict[str, Any]:
        """Updates the monthly spending cap for a specific category."""
        self._budgets[category] = float(monthly_limit)
        return {"category": category, "monthly_limit": float(monthly_limit)}

    def get_summary(self, month: Optional[str] = None) -> Dict[str, Any]:
        """Calculates income, expenses, category breakdown, and budget health."""
        target_month = month or datetime.now(timezone.utc).strftime("%Y-%m")

        filtered = [e for e in self._entries if e.get("date", "").startswith(target_month)]
        total_income = sum(e["amount"] for e in filtered if e["type"] == "income")
        total_expense = sum(e["amount"] for e in filtered if e["type"] == "expense")
        net_savings = total_income - total_expense
        savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0.0

        # Group expenses by category
        category_breakdown: Dict[str, float] = {}
        for e in filtered:
            if e["type"] == "expense":
                c = e.get("category", "Otros")
                category_breakdown[c] = category_breakdown.get(c, 0.0) + e["amount"]

        # Evaluate budget alerts
        alerts = []
        for cat, limit in self._budgets.items():
            spent = category_breakdown.get(cat, 0.0)
            pct = (spent / limit * 100) if limit > 0 else 0
            if pct >= 100:
                alerts.append(f"⚠️ ¡Límite superado en {cat}! Gastado: ${spent:,.0f} / ${limit:,.0f} ({pct:.1f}%)")
            elif pct >= 80:
                alerts.append(f"🔔 Alerta preventiva: {cat} ha consumido el {pct:.1f}% de su presupuesto mensual (${spent:,.0f} / ${limit:,.0f})")

        return {
            "month": target_month,
            "total_income": total_income,
            "total_expense": total_expense,
            "net_savings": net_savings,
            "savings_rate_pct": round(savings_rate, 1),
            "category_expenses": category_breakdown,
            "budget_limits": self._budgets,
            "alerts": alerts,
            "entries_count": len(filtered)
        }

    def format_summary_markdown(self, sm: Dict[str, Any]) -> str:
        """Formats the monthly financial health report for Santiago."""
        lines = [
            f"### 📊 Balance Financiero y Flujo de Caja ({sm.get('month')})",
            f"- **Ingresos Totales**: `+${sm.get('total_income', 0):,.2f} COP`",
            f"- **Gastos Totales**: `-${sm.get('total_expense', 0):,.2f} COP`",
            f"- **Ahorro Neto (Superávit)**: **`${sm.get('net_savings', 0):,.2f} COP`**",
            f"- **Tasa de Ahorro**: `{sm.get('savings_rate_pct', 0):.1f}%`",
            "",
            "#### 🏷️ Desglose por Categorías y Control Presupuestal:"
        ]

        cats = sm.get("category_expenses", {})
        limits = sm.get("budget_limits", {})

        for cat, spent in cats.items():
            lim = limits.get(cat, 0)
            if lim > 0:
                pct = (spent / lim) * 100
                bar = "█" * int(pct // 10) + "░" * max(0, 10 - int(pct // 10))
                lines.append(f"- **{cat}**: `${spent:,.0f}` / `${lim:,.0f}` `[{bar}]` ({pct:.1f}%)")
            else:
                lines.append(f"- **{cat}**: `${spent:,.0f} COP`")

        if sm.get("alerts"):
            lines.append("\n#### ⚠️ Alertas del Centinela Financiero:")
            for a in sm.get("alerts", []):
                lines.append(f"- {a}")

        lines.append("\nListo para registrar nuevos gastos, reasignar límites o exportar su libro contable, señor Santiago.")
        return "\n".join(lines)

    def get_entries(self, limit: int = 30) -> List[Dict[str, Any]]:
        return list(reversed(self._entries[-limit:]))


# Global singleton instance
personal_finance_service = PersonalFinanceService()
