# -*- coding: utf-8 -*-
"""
Automated Bank Reconciliation & GMF (4x1000) Tax Audit Service for Liseth.
Performs 3-way reconciliation between bank statements and general ledger,
detects outstanding deposits/checks, audits bank fees, and computes GMF (4x1000)
with 50% tax-deductibility (Art. 115 Estatuto Tributario) and 350 UVT exemption verification.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("liseth.bank_reconciliation")

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
HISTORY_FILE = DATA_DIR / "bank_reconciliation_history.json"

# UVT Value for Colombia (2026 reference: ~$49,799 COP)
UVT_2026_COP = 49799.0
EXEMPTION_350_UVT_COP = 350.0 * UVT_2026_COP  # ~$17,429,650 COP monthly limit


class BankReconciliationService:
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
            logger.error(f"[RECON_ERR] Error loading history: {e}")
        return []

    def _save_history(self, history: List[Dict[str, Any]]) -> None:
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[RECON_ERR] Error saving history: {e}")

    def reconcile_statement(
        self,
        bank_statement_balance: float,
        general_ledger_balance: float,
        deposits_in_transit: float = 0.0,
        outstanding_checks: float = 0.0,
        bank_charges_and_fees: float = 0.0,
        unrecorded_bank_credits: float = 0.0,
        unrecorded_bank_debits: float = 0.0,
        total_monthly_debits_cop: float = 0.0,
        is_account_gmf_exempt: bool = False,
        bank_name: str = "Bancolombia",
        currency: str = "COP"
    ) -> Dict[str, Any]:
        """
        Executes formal bank reconciliation equation:
        Adjusted Bank Balance = Bank Statement Balance + Deposits in Transit - Outstanding Checks
        Adjusted Book Balance = General Ledger Balance + Unrecorded Bank Credits - Bank Charges - Unrecorded Debits
        Difference = Adjusted Bank Balance - Adjusted Book Balance
        """
        stmt_bal = float(bank_statement_balance)
        book_bal = float(general_ledger_balance)
        dep_transit = max(0.0, float(deposits_in_transit))
        out_checks = max(0.0, float(outstanding_checks))
        fees = max(0.0, float(bank_charges_and_fees))
        unrec_credits = max(0.0, float(unrecorded_bank_credits))
        unrec_debits = max(0.0, float(unrecorded_bank_debits))
        total_debits = max(0.0, float(total_monthly_debits_cop))

        # 1. Adjusted Bank Balance
        adjusted_bank_balance = round(stmt_bal + dep_transit - out_checks, 2)

        # 2. Adjusted Book Balance (Saldo en Libros Ajustado)
        adjusted_book_balance = round(book_bal + unrec_credits - fees - unrec_debits, 2)

        # 3. Discrepancy / Reconciliation Difference
        difference = round(adjusted_bank_balance - adjusted_book_balance, 2)
        is_reconciled = abs(difference) < 0.01

        # 4. GMF (Gravamen a los Movimientos Financieros - 4x1000) Audit
        # Law 2277 / Art. 871 E.T. Rate: 0.4% on debits / withdrawals
        gmf_applicable_base = 0.0
        gmf_total = 0.0
        gmf_deductible_income_tax = 0.0
        gmf_non_deductible = 0.0
        exemption_status = "Cuenta no marcada como exenta (Aplica 4x1000 pleno)"

        if total_debits > 0:
            if is_account_gmf_exempt:
                # Up to 350 UVT exempt per month
                if total_debits <= EXEMPTION_350_UVT_COP:
                    gmf_applicable_base = 0.0
                    gmf_total = 0.0
                    exemption_status = f"100% Exenta por ley (Debits ${total_debits:,.2f} <= 350 UVT: ${EXEMPTION_350_UVT_COP:,.2f})"
                else:
                    gmf_applicable_base = total_debits - EXEMPTION_350_UVT_COP
                    gmf_total = gmf_applicable_base * 0.004
                    exemption_status = f"Parcialmente exenta: primeros 350 UVT (${EXEMPTION_350_UVT_COP:,.2f}) gravados con 0%. Gravable: ${gmf_applicable_base:,.2f}"
            else:
                gmf_applicable_base = total_debits
                gmf_total = total_debits * 0.004

            # Art. 115 Estatuto Tributario: 50% of GMF is 100% tax-deductible in corporate/personal income tax
            gmf_deductible_income_tax = round(gmf_total * 0.50, 2)
            gmf_non_deductible = round(gmf_total * 0.50, 2)

        # 5. Strategic Advice and Journal Entries Required
        journal_entries = []
        if fees > 0:
            journal_entries.append({
                "account": "530515 Gastos Comisiones / Servicios Bancarios",
                "debit": fees,
                "credit": 0.0,
                "notes": "Registrar gastos bancarios y cuotas de manejo del extracto"
            })
            journal_entries.append({
                "account": "1110 Bancos",
                "debit": 0.0,
                "credit": fees,
                "notes": "Salida de bancos por notas débito bancarias"
            })

        if unrec_credits > 0:
            journal_entries.append({
                "account": "1110 Bancos",
                "debit": unrec_credits,
                "credit": 0.0,
                "notes": "Ingreso bancario por transferencias o rendimientos no contabilizados"
            })
            journal_entries.append({
                "account": "4210 Ingresos Financieros / Clientes",
                "debit": 0.0,
                "credit": unrec_credits,
                "notes": "Abono directo de clientes o intereses ganados"
            })

        reconciliation_status = (
            "CONCILIACIÓN PERFECTA (Cuadre Exacto sin Diferencias)" if is_reconciled
            else f"DESCUADRE DETECTADO: Diferencia de ${difference:,.2f} {currency} requiere revisión de partidas en tránsito o errores de digitación."
        )

        result = {
            "bank_name": bank_name,
            "currency": currency,
            "is_reconciled": is_reconciled,
            "status_label": reconciliation_status,
            "summary": {
                "bank_statement_balance": stmt_bal,
                "general_ledger_balance": book_bal,
                "adjusted_bank_balance": adjusted_bank_balance,
                "adjusted_book_balance": adjusted_book_balance,
                "difference": difference
            },
            "reconciling_items": {
                "deposits_in_transit": dep_transit,
                "outstanding_checks": out_checks,
                "bank_charges_and_fees": fees,
                "unrecorded_bank_credits": unrec_credits,
                "unrecorded_bank_debits": unrec_debits
            },
            "gmf_4x1000_audit": {
                "total_monthly_debits": total_debits,
                "is_account_exempt": is_account_gmf_exempt,
                "uvt_350_threshold_cop": round(EXEMPTION_350_UVT_COP, 2),
                "gmf_taxable_base": round(gmf_applicable_base, 2),
                "total_gmf_generated_cop": round(gmf_total, 2),
                "gmf_50pct_tax_deductible_cop": gmf_deductible_income_tax,
                "gmf_non_deductible_cop": gmf_non_deductible,
                "audit_note": exemption_status,
                "tax_tip": "El 50% del GMF pagado en el año gravable es 100% deducible en el renglón de deducciones de su Declaración de Renta (Art. 115 E.T.)."
            },
            "suggested_journal_entries": journal_entries,
            "timestamp": datetime.now().isoformat()
        }

        history = self._load_history()
        history.insert(0, {"type": "bank_reconciliation", "data": result})
        self._save_history(history[:50])
        return result


bank_reconciliation_service = BankReconciliationService()
