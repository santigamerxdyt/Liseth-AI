# -*- coding: utf-8 -*-
"""
Corporate Treasury, Working Capital & Factoring Service for Liseth.
Provides Cash Conversion Cycle (CCC), Net Operating Working Capital (KTNO),
and Colombian Factoring (RADIAN / DIAN) discount simulators.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("liseth.treasury_working_capital")

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
HISTORY_FILE = DATA_DIR / "treasury_working_capital_history.json"


class TreasuryWorkingCapitalService:
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
            logger.error(f"[TREASURY_ERR] Error loading history: {e}")
        return []

    def _save_history(self, history: List[Dict[str, Any]]) -> None:
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[TREASURY_ERR] Error saving history: {e}")

    def calculate_cash_conversion_cycle(
        self,
        dso_receivables_days: float,  # Días de cobro
        dio_inventory_days: float,    # Días de inventario
        dpo_payables_days: float,     # Días de pago a proveedores
        annual_revenue_cop: float = 1200000000.0,
        annual_cogs_cop: float = 750000000.0
    ) -> Dict[str, Any]:
        """
        Calculates:
        CCC = DSO + DIO - DPO (Cash Conversion Cycle in days)
        KTNO = Cuentas por Cobrar + Inventarios - Cuentas por Pagar
        Daily liquidity required = COGS / 365 * CCC
        """
        dso = max(0.0, float(dso_receivables_days))
        dio = max(0.0, float(dio_inventory_days))
        dpo = max(0.0, float(dpo_payables_days))

        # CCC in days
        ccc_days = (dso + dio) - dpo

        # Balance sheet balances estimation based on days
        cxc_cop = (annual_revenue_cop / 365.0) * dso
        inv_cop = (annual_cogs_cop / 365.0) * dio
        cxp_cop = (annual_cogs_cop / 365.0) * dpo

        # Capital de Trabajo Neto Operativo (KTNO)
        ktno_cop = (cxc_cop + inv_cop) - cxp_cop

        # Working capital efficiency assessment
        if ccc_days <= 30.0:
            efficiency = "ALTA EFICIENCIA (Caja Ágil): La empresa financia gran parte de su operación con crédito de proveedores."
            status = "optimal"
        elif ccc_days <= 60.0:
            efficiency = "MODERADA / ACEPTABLE: Ciclo estándar en Colombia para manufactura y distribución comercial."
            status = "healthy"
        elif ccc_days <= 90.0:
            efficiency = "TENSA: Se requiere alto capital inmovilizado; evaluar aceleración de cobros o factoring."
            status = "warning"
        else:
            efficiency = "CRÍTICA (Atrapamiento de Liquidez): Alto riesgo de asfixia financiera por cobros excesivamente lentos o inventarios obsoletos."
            status = "critical"

        result = {
            "dso_receivables_days": round(dso, 1),
            "dio_inventory_days": round(dio, 1),
            "dpo_payables_days": round(dpo, 1),
            "ccc_days": round(ccc_days, 1),
            "annual_revenue_cop": round(annual_revenue_cop, 2),
            "annual_cogs_cop": round(annual_cogs_cop, 2),
            "cuentas_por_cobrar_cop": round(cxc_cop, 2),
            "inventarios_cop": round(inv_cop, 2),
            "cuentas_por_pagar_cop": round(cxp_cop, 2),
            "ktno_cop": round(ktno_cop, 2),
            "efficiency_diagnosis": efficiency,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }

        history = self._load_history()
        history.insert(0, {"type": "cash_conversion_cycle", "data": result})
        self._save_history(history[:50])
        return result

    def simulate_factoring_discount(
        self,
        invoice_face_value_cop: float,
        days_to_maturity: int,
        monthly_discount_rate_pct: float = 1.45,  # Tasa mensual típica factoring Colombia ~1.2% - 1.8%
        platform_fee_pct: float = 0.30            # Comisión RADIAN / fiduciaria
    ) -> Dict[str, Any]:
        """
        Simulates electronic invoice factoring (Facturación Electrónica DIAN / RADIAN):
        - Advance payment released immediately
        - Discount financial cost
        - Effective Annual Rate (Tasa Efectiva Anual E.A.)
        """
        if invoice_face_value_cop <= 0:
            invoice_face_value_cop = 10000000.0
        if days_to_maturity <= 0:
            days_to_maturity = 30

        # Monthly discount to effective period discount
        months = days_to_maturity / 30.0
        discount_rate_period = (monthly_discount_rate_pct / 100.0) * months
        platform_fee_rate = platform_fee_pct / 100.0

        discount_cost_cop = invoice_face_value_cop * discount_rate_period
        platform_fee_cop = invoice_face_value_cop * platform_fee_rate
        total_financing_cost_cop = discount_cost_cop + platform_fee_cop

        # Net liquidity received today
        net_cash_received_cop = invoice_face_value_cop - total_financing_cost_cop

        # Effective Annual Rate (E.A.)
        # E.A. = (1 + r_period)^(365 / days) - 1
        effective_period_rate = total_financing_cost_cop / net_cash_received_cop if net_cash_received_cop > 0 else 0.0
        compounding_frequency = 365.0 / days_to_maturity
        effective_annual_rate_pct = (((1.0 + effective_period_rate) ** compounding_frequency) - 1.0) * 100.0

        result = {
            "invoice_face_value_cop": round(invoice_face_value_cop, 2),
            "days_to_maturity": days_to_maturity,
            "monthly_discount_rate_pct": round(monthly_discount_rate_pct, 2),
            "platform_fee_pct": round(platform_fee_pct, 2),
            "discount_cost_cop": round(discount_cost_cop, 2),
            "platform_fee_cop": round(platform_fee_cop, 2),
            "total_financing_cost_cop": round(total_financing_cost_cop, 2),
            "net_cash_received_cop": round(net_cash_received_cop, 2),
            "effective_annual_rate_ea_pct": round(effective_annual_rate_pct, 2),
            "recommendation": (
                f"Anticipar esta factura de ${invoice_face_value_cop:,.0f} COP libera ${net_cash_received_cop:,.0f} COP "
                f"de liquidez inmediata hoy mismo con un costo financiero total del {((total_financing_cost_cop/invoice_face_value_cop)*100):.2f}%."
            ),
            "timestamp": datetime.now().isoformat()
        }

        history = self._load_history()
        history.insert(0, {"type": "factoring_simulation", "data": result})
        self._save_history(history[:50])
        return result


treasury_working_capital_service = TreasuryWorkingCapitalService()
