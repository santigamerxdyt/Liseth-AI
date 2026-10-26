"""
DIAN Tax Payment Assistant & Formulario 490 Settlement Engine for Liseth / JARVIS.
Directly tailored for Colombian Taxpayers, Freelancers, and Corporations:
- Formulario 490 (Recibo Oficial de Pago de Tributos Nacionales DIAN) Settlement
- Statutory Daily Moratory Interest Calculation (Art. 635 Estatuto Tributario - Usury Rate)
- Extemporaneity Penalties Calculation (Art. 641 E.T. with 10 UVT Minimum Statutory Cap)
- Simulated PSE Direct Payment Token & Bank Routing (Bancolombia, Davivienda, Nequi, MUISCA)
- Persistent Paid Tax Records in data/tax_payments_history.json
"""
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

DATA_FILE = os.path.join("data", "tax_payments_history.json")

# UVT 2026 Reference Baseline
UVT_2026 = 49799.0
MINIMUM_TAX_PENALTY_UVT = 10  # 10 UVT = $497,990 COP en 2026

# Tax Concepts Catalog for Form 490
TAX_CONCEPTS_490 = {
    "renta_pj": {"code": "01", "name": "Impuesto sobre la Renta Personas Jurídicas", "dian_form": "110"},
    "renta_pn": {"code": "01", "name": "Impuesto sobre la Renta Personas Naturales", "dian_form": "210"},
    "retefuente": {"code": "02", "name": "Retención en la Fuente Mensual", "dian_form": "350"},
    "iva": {"code": "03", "name": "Impuesto sobre las Ventas (IVA)", "dian_form": "300"},
    "rst_anticipo": {"code": "49", "name": "Anticipo Bimestral Régimen Simple (RST)", "dian_form": "2593"},
    "ica_municipal": {"code": "05", "name": "Impuesto de Industria y Comercio (ICA)", "dian_form": "Municipal"}
}

# Tasa de Usura Moratoria DIAN Anual Efectiva certificada (Art. 635 E.T.)
ANNUAL_USURY_RATE_PCT = 26.50  # ~26.5% E.A.


class TaxPaymentService:
    def __init__(self):
        self._ensure_storage()

    def _ensure_storage(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(DATA_FILE):
            default_history = [
                {
                    "receipt_id": "REC-490-2026-001",
                    "concept_code": "02",
                    "concept_name": "Retención en la Fuente Mensual (Form 350)",
                    "tax_year": 2026,
                    "period": "01",
                    "nit": "901.884.221-3",
                    "base_amount": 1850000.0,
                    "penalties": 0.0,
                    "moratory_interest": 0.0,
                    "total_paid": 1850000.0,
                    "payment_channel": "PSE / Bancolombia",
                    "bank_cus": "CUS-883920194",
                    "status": "PAGADO_PAZ_Y_SALVO",
                    "paid_at": datetime.now(timezone.utc).isoformat()
                }
            ]
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(default_history, f, indent=2, ensure_ascii=False)

    def _load(self) -> List[Dict[str, Any]]:
        self._ensure_storage()
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save(self, history: List[Dict[str, Any]]):
        os.makedirs("data", exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    def settle_form_490(
        self,
        concept_key: str,
        tax_year: int,
        period: str,
        nit: str,
        base_tax_amount: float,
        due_date_str: Optional[str] = None,
        payment_date_str: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Settles Formulario 490 (Recibo Oficial de Pago DIAN) including statutory penalties and interest.
        """
        c_info = TAX_CONCEPTS_490.get(concept_key, TAX_CONCEPTS_490["retefuente"])
        base = max(0.0, float(base_tax_amount))
        min_penalty = round(MINIMUM_TAX_PENALTY_UVT * UVT_2026, 2)

        # Date calculations
        now = datetime.now(timezone.utc)
        due_date = datetime.fromisoformat(due_date_str) if due_date_str else now
        payment_date = datetime.fromisoformat(payment_date_str) if payment_date_str else now

        days_late = max(0, (payment_date - due_date).days)
        months_late = (days_late // 30) + (1 if (days_late % 30 > 0) else 0)

        # Sanción por Extemporaneidad (Art. 641 E.T. - 5% por mes o fracción)
        if days_late > 0:
            raw_penalty = base * 0.05 * months_late
            penalty = round(max(min_penalty, raw_penalty), 2)
        else:
            penalty = 0.0

        # Intereses Moratorios (Art. 635 E.T.)
        # Tasa diaria equivalente a partir de la tasa anual efectiva
        daily_rate = ((1.0 + (ANNUAL_USURY_RATE_PCT / 100.0)) ** (1.0 / 365.0)) - 1.0
        if days_late > 0:
            interest = round(base * (((1.0 + daily_rate) ** days_late) - 1.0), 2)
        else:
            interest = 0.0

        total_settlement = round(base + penalty + interest, 2)

        # Generate unique receipt reference
        receipt_id = f"F490-{tax_year}-{uuid.uuid4().hex[:6].upper()}"

        result = {
            "receipt_id": receipt_id,
            "concept_code": c_info["code"],
            "concept_name": c_info["name"],
            "dian_form_reference": c_info["dian_form"],
            "tax_year": int(tax_year),
            "period": str(period),
            "nit": str(nit),
            "due_date": due_date.strftime("%Y-%m-%d"),
            "payment_date": payment_date.strftime("%Y-%m-%d"),
            "days_late": days_late,
            "months_late": months_late,
            "base_tax_amount": base,
            "extemporaneity_penalty": penalty,
            "applied_minimum_penalty": (penalty == min_penalty and days_late > 0),
            "moratory_interest": interest,
            "annual_moratory_rate_pct": ANNUAL_USURY_RATE_PCT,
            "total_payable": total_settlement,
            "currency": "COP"
        }
        return result

    def generate_pse_intent(self, settlement: Dict[str, Any], bank_name: str = "Bancolombia") -> Dict[str, Any]:
        """
        Creates a simulated PSE payment gateway intent with direct redirect URL and verification CUS.
        """
        cus = f"CUS-DIAN-{uuid.uuid4().hex[:8].upper()}"
        payment_url = f"https://muisca.dian.gov.co/WebPagos/pseGateway?ref={settlement['receipt_id']}&cus={cus}"

        guidelines = [
            f"1. Acceda a la plataforma de pagos DIAN / PSE para {bank_name}.",
            f"2. Verifique que el beneficiario oficial sea 'DIAN - Dirección de Impuestos y Aduanas Nacionales'.",
            f"3. Confirme el monto exacto liquidado: ${settlement['total_payable']:,.2f} COP.",
            f"4. Guarde el número CUS ({cus}) y el comprobante con sello de aprobación bancaria.",
            "5. El sistema de Liseth registrará automáticamente su Paz y Salvo en el historial fiscal."
        ]

        return {
            "receipt_id": settlement["receipt_id"],
            "bank_name": bank_name,
            "cus_code": cus,
            "amount_cop": settlement["total_payable"],
            "payment_url": payment_url,
            "instructions": guidelines,
            "status": "PENDIENTE_DE_PAGO"
        }

    def confirm_payment(
        self,
        settlement: Dict[str, Any],
        bank_name: str,
        cus_code: str
    ) -> Dict[str, Any]:
        """
        Confirms and archives the tax payment in the persistent fiscal records.
        """
        history = self._load()
        payment_record = {
            "receipt_id": settlement["receipt_id"],
            "concept_code": settlement["concept_code"],
            "concept_name": settlement["concept_name"],
            "tax_year": settlement["tax_year"],
            "period": settlement["period"],
            "nit": settlement["nit"],
            "base_amount": settlement["base_tax_amount"],
            "penalties": settlement["extemporaneity_penalty"],
            "moratory_interest": settlement["moratory_interest"],
            "total_paid": settlement["total_payable"],
            "payment_channel": f"PSE / {bank_name}",
            "bank_cus": cus_code,
            "status": "PAGADO_PAZ_Y_SALVO",
            "paid_at": datetime.now(timezone.utc).isoformat()
        }
        history.insert(0, payment_record)
        self._save(history)
        return payment_record

    def get_payment_history(self) -> List[Dict[str, Any]]:
        return self._load()

    def format_markdown_report(self, settlement: Dict[str, Any]) -> str:
        md = [
            f"# 🧾 RECIBO OFICIAL DE PAGO DIAN (FORMULARIO 490)",
            f"**ID de Recibo**: `{settlement['receipt_id']}` | **NIT / Cédula**: `{settlement['nit']}`",
            f"**Concepto Tributario**: `[{settlement['concept_code']}] {settlement['concept_name']}`",
            f"**Año Gravable**: `{settlement['tax_year']}` | **Período**: `{settlement['period']}`",
            "",
            "### 💵 Liquidación Oficial de Valores a Pagar",
            f"- **Impuesto Neto a Cargo (Casilla Base)**: `${settlement['base_tax_amount']:,.2f} COP`",
            f"- **Sanción por Extemporaneidad (Art. 641 E.T.)**: `${settlement['extemporaneity_penalty']:,.2f} COP`",
            f"- **Intereses Moratorios (Art. 635 E.T. - {settlement['annual_moratory_rate_pct']}% E.A.)**: `${settlement['moratory_interest']:,.2f} COP`",
            f"- **Días de Retraso Liquidados**: `{settlement['days_late']} días` ({settlement['months_late']} mes/fracción)",
            "",
            f"> 🏛️ **TOTAL A PAGAR EN BANCOS / PSE**: **`${settlement['total_payable']:,.2f} COP`**",
            "",
            "> 💡 *Para proceder al pago inmediato, presione el botón 'Pagar con PSE' en el HUD o solicite a Liseth: 'Pagar este recibo con PSE'.*"
        ]
        return "\n".join(md)


tax_payment_service = TaxPaymentService()
