# -*- coding: utf-8 -*-
"""
Pricing Strategy & Price Elasticity of Demand (PED) Service for Liseth.
Implements managerial economics models:
- Arc / Midpoint Price Elasticity: Ed = (%ΔQ) / (%ΔP)
- Optimal Pricing via Lerner Index & Marginal Revenue: P* = MC / (1 + 1/Ed)
- Price sensitivity curve simulation (-20% to +20%) with revenue & margin forecasting.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("liseth.pricing_elasticity")

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
HISTORY_FILE = DATA_DIR / "pricing_elasticity_history.json"


class PricingElasticityService:
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
            logger.error(f"[PRICING_ERR] Error loading history: {e}")
        return []

    def _save_history(self, history: List[Dict[str, Any]]) -> None:
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[PRICING_ERR] Error saving history: {e}")

    def evaluate_pricing_strategy(
        self,
        product_name: str = "Producto / Servicio",
        current_price: float = 50000.0,
        unit_marginal_cost: float = 25000.0,
        current_monthly_units: float = 1000.0,
        price_elasticity: Optional[float] = None,
        test_price: Optional[float] = None,
        test_volume: Optional[float] = None,
        currency: str = "COP"
    ) -> Dict[str, Any]:
        """
        Evaluates demand elasticity and simulates pricing adjustments
        to maximize revenue and contribution margin.
        """
        p0 = max(0.01, float(current_price))
        mc = max(0.0, float(unit_marginal_cost))
        q0 = max(1.0, float(current_monthly_units))

        # 1. Determine or Calculate Elasticity
        if price_elasticity is not None:
            ed = float(price_elasticity)
        elif test_price is not None and test_volume is not None and test_price != p0:
            p1 = float(test_price)
            q1 = float(test_volume)
            # Midpoint (Arc) Formula: (ΔQ / AvgQ) / (ΔP / AvgP)
            pct_dq = (q1 - q0) / ((q0 + q1) / 2.0)
            pct_dp = (p1 - p0) / ((p0 + p1) / 2.0)
            ed = pct_dq / pct_dp if pct_dp != 0 else -1.0
        else:
            # Default typical moderately elastic consumer good
            ed = -1.35

        abs_ed = abs(ed)

        # 2. Elasticity Classification
        if abs_ed < 0.95:
            classification = "INELÁSTICA (|Ed| < 1)"
            diag = "La demanda reacciona poco ante aumentos de precio. Un incremento de precio aumentará los ingresos totales."
            action_plan = "Incrementar precio gradualmente (+5% a +10%) para capturar margen sin perder volumen significativo."
        elif abs_ed <= 1.05:
            classification = "ELASTICIDAD UNITARIA (|Ed| ≈ 1)"
            diag = "La variación porcentual del volumen compensa exactamente el precio. Los ingresos totales se mantienen constantes."
            action_plan = "El ingreso está maximizado. Optimizar costos variables para elevar el margen operativo."
        else:
            classification = "ELÁSTICA (|Ed| > 1)"
            diag = "La demanda es altamente sensible al precio. Subir precios destruye volumen y reduce ingresos brutos."
            action_plan = "Evitar subidas de precio unilaterales. Usar empaquetamiento (bundling), descuentos por volumen o fidelización."

        # 3. Optimal Theoretical Price via Lerner Index (if Ed < -1)
        if ed < -1.0:
            optimal_price = mc / (1.0 + (1.0 / ed))
            markup_optimal_pct = round(((optimal_price - mc) / mc) * 100.0, 1)
        else:
            optimal_price = p0 * 1.25  # Inelastic demand can absorb higher markup
            markup_optimal_pct = round(((optimal_price - mc) / mc) * 100.0, 1)

        current_revenue = p0 * q0
        current_margin = (p0 - mc) * q0

        # 4. Simulation Curve across price variations (-15%, -10%, -5%, 0%, +5%, +10%, +15%, +20%)
        simulation_curve = []
        variations = [-0.15, -0.10, -0.05, 0.0, 0.05, 0.10, 0.15, 0.20]

        for var in variations:
            new_p = p0 * (1.0 + var)
            # Q' = Q0 * (1 + Ed * ΔP/P0)
            new_q = max(0.0, q0 * (1.0 + (ed * var)))
            new_rev = new_p * new_q
            new_marg = (new_p - mc) * new_q
            delta_margin = new_marg - current_margin

            simulation_curve.append({
                "price_change_pct": round(var * 100, 1),
                "simulated_price": round(new_p, 2),
                "projected_units": round(new_q, 1),
                "projected_revenue": round(new_rev, 2),
                "projected_margin": round(new_marg, 2),
                "delta_margin": round(delta_margin, 2),
                "is_current": var == 0.0
            })

        # Find best scenario from simulation
        best_scenario = max(simulation_curve, key=lambda x: x["projected_margin"])

        result = {
            "product_name": product_name,
            "currency": currency,
            "current_state": {
                "price": round(p0, 2),
                "unit_marginal_cost": round(mc, 2),
                "unit_contribution_margin": round(p0 - mc, 2),
                "margin_pct": round(((p0 - mc) / p0) * 100.0, 1),
                "monthly_units": round(q0, 1),
                "monthly_revenue": round(current_revenue, 2),
                "monthly_contribution_margin": round(current_margin, 2)
            },
            "elasticity_analysis": {
                "coefficient_ed": round(ed, 2),
                "absolute_ed": round(abs_ed, 2),
                "classification": classification,
                "diagnosis": diag,
                "action_plan": action_plan
            },
            "optimization": {
                "optimal_theoretical_price": round(optimal_price, 2),
                "optimal_markup_pct": markup_optimal_pct,
                "best_simulated_price": best_scenario["simulated_price"],
                "best_simulated_margin": best_scenario["projected_margin"],
                "potential_margin_gain": round(best_scenario["delta_margin"], 2),
                "recommended_price_change_pct": best_scenario["price_change_pct"]
            },
            "simulation_curve": simulation_curve,
            "timestamp": datetime.now().isoformat()
        }

        history = self._load_history()
        history.insert(0, {"type": "pricing_elasticity_evaluation", "data": result})
        self._save_history(history[:50])
        return result


pricing_elasticity_service = PricingElasticityService()
