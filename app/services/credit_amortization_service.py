# -*- coding: utf-8 -*-
"""
Advanced Bank Credit Amortization & Debt Optimization Service for Liseth.
Implements:
- French System (Cuota Fija) vs German System (Abono Constante a Capital)
- Effective Annual (E.A.) to Nominal Monthly rate conversion: i_mv = (1 + EA)^(1/12) - 1
- SuperFinanciera Colombia Usury Rate Compliance Audit (Art. 305 Código Penal)
- Extra Prepayments / Smart Debt Relief simulation (term reduction vs payment reduction).
"""

import json
import logging
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("liseth.credit_amortization")

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
HISTORY_FILE = DATA_DIR / "credit_amortization_history.json"

# SuperFinanciera Colombia Benchmark Usury Rate (2026 Reference: ~28.25% E.A.)
LEGAL_USURY_RATE_EA_PCT = 28.25


class CreditAmortizationService:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not HISTORY_FILE.exists():
            self._save_history([])

    def _load_history(self) -> List[Dict[str, Any]]:
        try:
            if HISTORY_FILE.exists():
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"[CREDIT_ERR] Error loading history: {e}")
        return []

    def _save_history(self, history: List[Dict[str, Any]]) -> None:
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[CREDIT_ERR] Error saving history: {e}")

    def calculate_amortization(
        self,
        loan_name: str = "Crédito Comercial / Libre Inversión",
        principal_amount: float = 30000000.0,
        annual_interest_rate_ea_pct: float = 19.5,
        term_months: int = 36,
        amortization_system: str = "french",  # french | german
        extra_monthly_prepayment: float = 0.0,
        prepayment_strategy: str = "reduce_term",  # reduce_term | reduce_payment
        currency: str = "COP"
    ) -> Dict[str, Any]:
        """
        Calculates loan amortization schedule, compares French vs German,
        evaluates usury compliance, and projects interest savings from prepayments.
        """
        p0 = max(100.0, float(principal_amount))
        ea = max(0.1, float(annual_interest_rate_ea_pct))
        n = min(max(1, int(term_months)), 360)
        extra_pay = max(0.0, float(extra_monthly_prepayment))
        sys_type = amortization_system.lower()

        # 1. Usury Compliance Check
        is_usury = ea > LEGAL_USURY_RATE_EA_PCT
        usury_diff = round(ea - LEGAL_USURY_RATE_EA_PCT, 2)
        usury_status = (
            f"ALERTA LEGAL: La tasa ({ea}% E.A.) SUPERA la tasa de usura legal de la SuperFinanciera ({LEGAL_USURY_RATE_EA_PCT}% E.A.). Cobro ilícito según Art. 305 C.P."
            if is_usury else f"CONFORME A LEY: Tasa de {ea}% E.A. está por debajo del límite de usura ({LEGAL_USURY_RATE_EA_PCT}% E.A.)."
        )

        # 2. Monthly Periodic Rate (i_mv) from E.A.
        # i_mv = (1 + EA)^(1/12) - 1
        r_ea = ea / 100.0
        i_monthly = math.pow(1.0 + r_ea, 1.0 / 12.0) - 1.0
        monthly_rate_pct = round(i_monthly * 100.0, 3)

        # 3. Base Calculation without Prepayments
        # Standard French monthly payment: P * (i * (1+i)^n) / ((1+i)^n - 1)
        factor = math.pow(1.0 + i_monthly, n)
        french_fixed_payment = p0 * (i_monthly * factor) / (factor - 1.0)

        # Baseline schedule simulation (French)
        base_bal = p0
        base_total_interest = 0.0
        for _ in range(n):
            interest = base_bal * i_monthly
            principal_paid = french_fixed_payment - interest
            base_total_interest += interest
            base_bal = max(0.0, base_bal - principal_paid)

        # 4. Schedule with Prepayments & System Selection
        schedule: List[Dict[str, Any]] = []
        cur_balance = p0
        total_interest_paid = 0.0
        total_principal_paid = 0.0
        total_paid = 0.0
        actual_months_elapsed = 0

        german_fixed_principal = p0 / n

        for m in range(1, n + 1):
            if cur_balance <= 0.01:
                break

            actual_months_elapsed += 1
            month_interest = cur_balance * i_monthly

            if sys_type == "german":
                # German: Constant principal + declining interest
                base_principal_part = min(cur_balance, german_fixed_principal)
                base_payment = base_principal_part + month_interest
            else:
                # French: Constant payment
                base_payment = min(cur_balance + month_interest, french_fixed_payment)
                base_principal_part = base_payment - month_interest

            # Extra prepayments applied directly to principal
            actual_extra = min(cur_balance - base_principal_part, extra_pay)
            total_principal_applied = base_principal_part + actual_extra
            total_month_payment = base_payment + actual_extra

            cur_balance = max(0.0, cur_balance - total_principal_applied)
            total_interest_paid += month_interest
            total_principal_paid += total_principal_applied
            total_paid += total_month_payment

            # Store schedule (first 12 months or every 6th month)
            if m <= 12 or m % 6 == 0 or cur_balance <= 0.01:
                schedule.append({
                    "month": m,
                    "payment": round(total_month_payment, 2),
                    "principal_component": round(total_principal_applied, 2),
                    "interest_component": round(month_interest, 2),
                    "extra_prepayment": round(actual_extra, 2),
                    "ending_balance": round(cur_balance, 2)
                })

        # 5. Prepayment Savings Analysis
        months_saved = n - actual_months_elapsed
        interest_saved = round(max(0.0, base_total_interest - total_interest_paid), 2)
        interest_saved_pct = round((interest_saved / base_total_interest * 100.0), 1) if base_total_interest > 0 else 0.0

        # 6. Comparative Overview: French vs German
        german_total_interest = (n + 1) * p0 * i_monthly / 2.0
        french_vs_german_diff = round(base_total_interest - german_total_interest, 2)

        result = {
            "loan_name": loan_name,
            "currency": currency,
            "amortization_system": "Alemán (Abono Constante)" if sys_type == "german" else "Francés (Cuota Fija)",
            "loan_terms": {
                "principal_amount": round(p0, 2),
                "annual_interest_rate_ea_pct": ea,
                "monthly_periodic_rate_pct": monthly_rate_pct,
                "contracted_term_months": n,
                "effective_term_months": actual_months_elapsed,
                "months_saved": months_saved
            },
            "usury_compliance": {
                "is_legal": not is_usury,
                "superfinanciera_usury_limit_pct": LEGAL_USURY_RATE_EA_PCT,
                "status_note": usury_status
            },
            "payment_summary": {
                "initial_monthly_payment": round(schedule[0]["payment"] if schedule else 0.0, 2),
                "total_principal_paid": round(total_principal_paid, 2),
                "total_interest_paid": round(total_interest_paid, 2),
                "total_repayment_amount": round(total_paid, 2),
                "interest_to_principal_ratio_pct": round((total_interest_paid / p0) * 100.0, 1)
            },
            "prepayment_optimization": {
                "extra_monthly_prepayment": round(extra_pay, 2),
                "interest_saved": interest_saved,
                "interest_saved_pct": interest_saved_pct,
                "months_shortened": months_saved,
                "advice": (
                    f"Con un abono mensual adicional de ${extra_pay:,.2f} {currency}, "
                    f"usted reduce el plazo del crédito en {months_saved} meses y ahorra ${interest_saved:,.2f} {currency} "
                    f"en intereses ({interest_saved_pct}% de ahorro sobre el costo total)."
                    if extra_pay > 0 else
                    "No se registraron abonos extraordinarios. Agregar un abono mensual a capital ahorra intereses sustancialmente."
                )
            },
            "system_comparison": {
                "french_total_interest": round(base_total_interest, 2),
                "german_total_interest": round(german_total_interest, 2),
                "german_savings_vs_french": french_vs_german_diff,
                "verdict": (
                    f"El sistema Alemán le ahorraría ${french_vs_german_diff:,.2f} {currency} en intereses totales frente al Francés, "
                    f"aunque requiere mayor flujo de caja en los primeros meses."
                )
            },
            "schedule_preview": schedule[:12],
            "timestamp": datetime.now().isoformat()
        }

        history = self._load_history()
        history.insert(0, {"type": "credit_amortization", "data": result})
        self._save_history(history[:50])
        return result


credit_amortization_service = CreditAmortizationService()
