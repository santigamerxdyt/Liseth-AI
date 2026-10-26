# -*- coding: utf-8 -*-
"""
Forex Radar, Exchange Arbitrage & Currency Hedging Service for Liseth.
Covers Colombia Official TRM (Superfinanciera / BanRep), USDT Crypto Dollar,
EUR/COP, Bank Spreads, and Forward Hedging Cost Simulators.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("liseth.forex_radar")

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
HISTORY_FILE = DATA_DIR / "forex_radar_history.json"


class ForexRadarService:
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
            logger.error(f"[FOREX_ERR] Error loading history: {e}")
        return []

    def _save_history(self, history: List[Dict[str, Any]]) -> None:
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[FOREX_ERR] Error saving history: {e}")

    def get_forex_radar(self, base_usd_cop: float = 4185.00) -> Dict[str, Any]:
        """
        Calculates real-time rate estimates and spreads across Colombian foreign exchange channels:
        - TRM Oficial (Superfinanciera)
        - Dólar Tarjeta Crédito (+2.5% impuesto y spread)
        - Dólar Cripto USDT (P2P mercado libre)
        - Euro EUR/COP (con paridad 1.08 USD/EUR)
        - Dólar Efectivo Casas de Cambio
        """
        trm = round(float(base_usd_cop), 2)
        dolar_tarjeta = round(trm * 1.026, 2)
        dolar_usdt = round(trm * 0.998, 2)  # Typically traded with slight discount or parity
        euro_cop = round(trm * 1.085, 2)
        dolar_efectivo_compra = round(trm * 0.965, 2)
        dolar_efectivo_venta = round(trm * 0.985, 2)

        # Spread bancario interbancario
        spread_tarjeta_trm = round(dolar_tarjeta - trm, 2)
        spread_usdt_trm = round(dolar_usdt - trm, 2)

        result = {
            "trm_oficial_cop": trm,
            "dolar_tarjeta_cop": dolar_tarjeta,
            "dolar_usdt_p2p_cop": dolar_usdt,
            "euro_cop": euro_cop,
            "efectivo_compra_cop": dolar_efectivo_compra,
            "efectivo_venta_cop": dolar_efectivo_venta,
            "spread_tarjeta_cop": spread_tarjeta_trm,
            "spread_usdt_cop": spread_usdt_trm,
            "arbitrage_tip": (
                "Para compras internacionales corporativas, pagar vía tarjeta de débito multi-moneda o "
                "USDT P2P ahorra hasta un 2.6% frente al spread de tarjetas de crédito tradicionales."
            ),
            "timestamp": datetime.now().isoformat()
        }

        history = self._load_history()
        history.insert(0, {"type": "forex_radar", "data": result})
        self._save_history(history[:50])
        return result

    def simulate_forward_hedge(
        self,
        amount_usd: float,
        spot_rate_cop: float = 4185.00,
        days_forward: int = 90,
        rate_cop_annual_pct: float = 9.75,   # Tasa de intervención Banco de la República
        rate_usd_annual_pct: float = 4.50    # Tasa FED Funds Rate
    ) -> Dict[str, Any]:
        """
        Simulates theoretical Forward Exchange Rate under Interest Rate Parity (IRP):
        F = S * [ (1 + r_cop * (days/360)) / (1 + r_usd * (days/360)) ]
        """
        if amount_usd <= 0:
            amount_usd = 10000.0
        if days_forward <= 0:
            days_forward = 30

        r_cop = (rate_cop_annual_pct / 100.0) * (days_forward / 360.0)
        r_usd = (rate_usd_annual_pct / 100.0) * (days_forward / 360.0)

        forward_rate = spot_rate_cop * ((1.0 + r_cop) / (1.0 + r_usd))
        premium_cop = forward_rate - spot_rate_cop
        premium_pct = (premium_cop / spot_rate_cop) * 100.0

        total_spot_cop = amount_usd * spot_rate_cop
        total_forward_cop = amount_usd * forward_rate
        hedging_cost_cop = total_forward_cop - total_spot_cop

        result = {
            "amount_usd": round(amount_usd, 2),
            "spot_rate_cop": round(spot_rate_cop, 2),
            "days_forward": days_forward,
            "rate_cop_annual_pct": round(rate_cop_annual_pct, 2),
            "rate_usd_annual_pct": round(rate_usd_annual_pct, 2),
            "forward_rate_cop": round(forward_rate, 2),
            "premium_devaluation_cop": round(premium_cop, 2),
            "premium_pct": round(premium_pct, 2),
            "total_spot_cop": round(total_spot_cop, 2),
            "total_forward_cop": round(total_forward_cop, 2),
            "hedging_cost_cop": round(hedging_cost_cop, 2),
            "strategic_recommendation": (
                f"Si la devaluación esperada en {days_forward} días supera el {premium_pct:.2f}%, "
                f"conviene pactar contrato Forward para congelar la tasa en ${forward_rate:,.2f} COP "
                f"y proteger el margen operativo de la importación."
            ),
            "timestamp": datetime.now().isoformat()
        }

        history = self._load_history()
        history.insert(0, {"type": "forward_hedge", "data": result})
        self._save_history(history[:50])
        return result


forex_radar_service = ForexRadarService()
