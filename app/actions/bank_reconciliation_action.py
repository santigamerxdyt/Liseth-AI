# -*- coding: utf-8 -*-
"""
Action handler for Automated Bank Reconciliation & GMF (4x1000) Tax Audit.
Reconciles bank balances vs general ledger, calculates adjusted balances,
and audits the 4x1000 financial movements tax with 50% deductibility (Art. 115 E.T.).
"""

from typing import Any, Dict
from app.services.bank_reconciliation_service import bank_reconciliation_service


def bank_reconciliation_action(parameters: Dict[str, Any]) -> str:
    stmt_bal = float(parameters.get("bank_statement_balance", 45000000.0))
    book_bal = float(parameters.get("general_ledger_balance", 42500000.0))
    dep_transit = float(parameters.get("deposits_in_transit", 5000000.0))
    out_checks = float(parameters.get("outstanding_checks", 7200000.0))
    fees = float(parameters.get("bank_charges_and_fees", 300000.0))
    unrec_credits = float(parameters.get("unrecorded_bank_credits", 600000.0))
    unrec_debits = float(parameters.get("unrecorded_bank_debits", 0.0))
    total_debits = float(parameters.get("total_monthly_debits_cop", 25000000.0))
    exempt = bool(parameters.get("is_account_gmf_exempt", False))
    bank = str(parameters.get("bank_name", "Bancolombia")).strip()
    currency = str(parameters.get("currency", "COP")).strip().upper()

    res = bank_reconciliation_service.reconcile_statement(
        bank_statement_balance=stmt_bal,
        general_ledger_balance=book_bal,
        deposits_in_transit=dep_transit,
        outstanding_checks=out_checks,
        bank_charges_and_fees=fees,
        unrecorded_bank_credits=unrec_credits,
        unrecorded_bank_debits=unrec_debits,
        total_monthly_debits_cop=total_debits,
        is_account_gmf_exempt=exempt,
        bank_name=bank,
        currency=currency
    )

    s = res["summary"]
    g = res["gmf_4x1000_audit"]

    lines = [
        f"🏦 **AUDITORÍA DE CONCILIACIÓN BANCARIA & GMF (4x1000) — {res['bank_name'].upper()}**\n",
        f"• **Estado del Cuadre:** **{res['status_label']}**",
        f"• **Saldo en Extracto Bancario:** {currency} ${s['bank_statement_balance']:,.2f}",
        f"• **Saldo en Libros Contables:** {currency} ${s['general_ledger_balance']:,.2f}\n",
        f"⚖️ **ECUACIÓN DE CONCILIACIÓN AJUSTADA:**",
        f"  - **Saldo Bancos Ajustado:** {currency} ${s['adjusted_bank_balance']:,.2f} (+ Depósitos tránsito: ${dep_transit:,.2f} - Cheques pendientes: ${out_checks:,.2f})",
        f"  - **Saldo Libros Ajustado:** {currency} ${s['adjusted_book_balance']:,.2f} (+ Créditos no contabilizados: ${unrec_credits:,.2f} - Gastos bancarios: ${fees:,.2f})",
        f"  - **Diferencia de Cuadre:** **{currency} ${s['difference']:,.2f}**\n",
        f"📊 **AUDITORÍA TRIBUTARIA DEL 4x1000 (GMF):**",
        f"• **Débitos Totales del Mes:** {currency} ${g['total_monthly_debits']:,.2f}",
        f"• **Condición de Cuenta:** {g['audit_note']}",
        f"• **GMF Total Generado (0.4%):** **{currency} ${g['total_gmf_generated_cop']:,.2f}**",
        f"• **50% Deducible en Renta (Art. 115 E.T.):** **{currency} ${g['gmf_50pct_tax_deductible_cop']:,.2f}** (Beneficio tributario)",
        f"• **50% No Deducible:** {currency} ${g['gmf_non_deductible_cop']:,.2f}\n",
        f"💡 **Recomendación Contable:** {g['tax_tip']}"
    ]

    if res["suggested_journal_entries"]:
        lines.append("\n📝 **ASIENTOS DE AJUSTE SUGERIDOS EN LIBROS:**")
        for e in res["suggested_journal_entries"]:
            lines.append(f"  • {e['account']}: Débito ${e['debit']:,.2f} | Crédito ${e['credit']:,.2f} ({e['notes']})")

    return "\n".join(lines)
