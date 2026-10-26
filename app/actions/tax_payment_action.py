"""
Action handler for tax_payment tool in JARVIS / Liseth.
Bridges Gemini Tool Calls with the DIAN Tax Payment & Formulario 490 Service.
"""
from typing import Any, Dict
from app.services.tax_payment_service import tax_payment_service


def tax_payment_action(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handles DIAN tax settlement (Formulario 490), moratory interest, and PSE payment routing.
    """
    action = parameters.get("action") or "settle"

    if action in ("pse_link", "pagar", "pagar_pse"):
        concept = parameters.get("concept") or "retefuente"
        year = int(parameters.get("year") or 2026)
        period = str(parameters.get("period") or "01")
        nit = str(parameters.get("nit") or "901.884.221-3")
        amount = float(parameters.get("amount") or 1500000.0)
        bank = parameters.get("bank") or "Bancolombia"

        settlement = tax_payment_service.settle_form_490(
            concept_key=concept,
            tax_year=year,
            period=period,
            nit=nit,
            base_tax_amount=amount
        )
        pse_intent = tax_payment_service.generate_pse_intent(settlement, bank_name=bank)
        md = [
            f"# 💳 PASARELA DE PAGO DIAN PSE: RECIBO `{settlement['receipt_id']}`",
            f"- **Banco Seleccionado**: `{bank}`",
            f"- **Código CUS**: `{pse_intent['cus_code']}`",
            f"- **Monto Total a Debitar**: **`${pse_intent['amount_cop']:,.2f} COP`**",
            f"- **Enlace de Pago Seguro**: [Proceder al Pago en Línea DIAN PSE]({pse_intent['payment_url']})",
            "",
            "### 📌 Instrucciones de Pago:",
            "\n".join(f"- {i}" for i in pse_intent["instructions"])
        ]
        return {
            "status": "success",
            "action": "tax_payment.pse",
            "intent": pse_intent,
            "markdown": "\n".join(md)
        }

    elif action in ("history", "historial", "paz_y_salvo"):
        hist = tax_payment_service.get_payment_history()
        md = [
            "# 📋 HISTORIAL DE IMPUESTOS PAGADOS & PAZ Y SALVO DIAN",
            f"**Total de Pagos Registrados**: `{len(hist)}`",
            "",
            "| ID Recibo | Concepto | Año/Per | Total Pagado | Canal / Banco | CUS |",
            "| :--- | :--- | :---: | :---: | :--- | :--- |"
        ]
        for p in hist:
            md.append(f"| `{p['receipt_id']}` | {p['concept_name']} | {p['tax_year']}-{p['period']} | **${p['total_paid']:,.2f} COP** | {p['payment_channel']} | `{p['bank_cus']}` |")

        return {
            "status": "success",
            "action": "tax_payment.history",
            "history": hist,
            "markdown": "\n".join(md)
        }

    else:  # settle (default)
        concept = parameters.get("concept") or parameters.get("concepto") or "retefuente"
        year = int(parameters.get("year") or parameters.get("ano") or 2026)
        period = str(parameters.get("period") or parameters.get("periodo") or "01")
        nit = str(parameters.get("nit") or "901.884.221-3")
        amount = float(parameters.get("amount") or parameters.get("monto") or 1500000.0)
        due_date = parameters.get("due_date") or parameters.get("fecha_vencimiento")
        pay_date = parameters.get("payment_date") or parameters.get("fecha_pago")

        settlement = tax_payment_service.settle_form_490(
            concept_key=concept,
            tax_year=year,
            period=period,
            nit=nit,
            base_tax_amount=amount,
            due_date_str=due_date,
            payment_date_str=pay_date
        )
        report = tax_payment_service.format_markdown_report(settlement)

        return {
            "status": "success",
            "action": "tax_payment.settle",
            "settlement": settlement,
            "markdown": report
        }
