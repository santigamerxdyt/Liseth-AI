# -*- coding: utf-8 -*-
"""
Marketing & Digital Growth Engine Service for Liseth.
Provides Unit Economics (CAC, LTV, LTV/CAC ratio, Payback, Churn),
Funnel Conversion Diagnostics, and ROAS / Multi-channel Ad Spend Attribution.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("liseth.marketing_growth")

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
HISTORY_FILE = DATA_DIR / "marketing_growth_history.json"


class MarketingGrowthService:
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
            logger.error(f"[MKT_ERR] Error loading history: {e}")
        return []

    def _save_history(self, history: List[Dict[str, Any]]) -> None:
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[MKT_ERR] Error saving history: {e}")

    def calculate_unit_economics(
        self,
        cac: float,
        arpu: float,
        churn_monthly_pct: float,
        gross_margin_pct: float = 75.0,
        currency: str = "COP"
    ) -> Dict[str, Any]:
        """
        Calculates SaaS and digital product unit economics:
        - LTV = (ARPU * Gross Margin) / Churn
        - LTV / CAC ratio
        - CAC Payback Period (months)
        - Annualized Churn Rate
        """
        if cac <= 0:
            cac = 1.0
        if arpu <= 0:
            arpu = 1.0
        if churn_monthly_pct <= 0.05:
            churn_monthly_pct = 0.05  # minimum boundary to prevent zero division
        if churn_monthly_pct > 100.0:
            churn_monthly_pct = 100.0

        churn_decimal = churn_monthly_pct / 100.0
        margin_decimal = gross_margin_pct / 100.0
        monthly_gross_profit = arpu * margin_decimal

        # Average customer lifetime in months = 1 / churn
        customer_lifetime_months = 1.0 / churn_decimal
        ltv = monthly_gross_profit * customer_lifetime_months
        ltv_cac_ratio = ltv / cac

        # CAC Payback period in months = CAC / Monthly Gross Profit per customer
        cac_payback_months = cac / monthly_gross_profit if monthly_gross_profit > 0 else 999.0

        # Annualized Churn = 1 - (1 - monthly_churn)^12
        annual_churn_pct = (1.0 - ((1.0 - churn_decimal) ** 12)) * 100.0

        # Benchmarking diagnostic
        if ltv_cac_ratio >= 4.0:
            diagnostic = "EXCELENTE (Hiper-escalable): Retorno extraordinario sobre la inversión en adquisición."
            status = "optimal"
        elif ltv_cac_ratio >= 3.0:
            diagnostic = "SALUDABLE (Benchmark SaaS ideal): Modelo sostenible y listo para acelerar pauta."
            status = "healthy"
        elif ltv_cac_ratio >= 1.5:
            diagnostic = "ACEPTABLE / EN OPTIMIZACIÓN: Rentable pero vulnerable a aumentos de costo por clic."
            status = "warning"
        else:
            diagnostic = "CRÍTICO (Destructor de Capital): El costo de adquisición supera o iguala el valor de vida."
            status = "critical"

        result = {
            "cac": round(cac, 2),
            "arpu": round(arpu, 2),
            "gross_margin_pct": round(gross_margin_pct, 2),
            "churn_monthly_pct": round(churn_monthly_pct, 2),
            "annual_churn_pct": round(annual_churn_pct, 2),
            "customer_lifetime_months": round(customer_lifetime_months, 1),
            "ltv": round(ltv, 2),
            "ltv_cac_ratio": round(ltv_cac_ratio, 2),
            "cac_payback_months": round(cac_payback_months, 1),
            "diagnostic": diagnostic,
            "status": status,
            "currency": currency,
            "timestamp": datetime.now().isoformat()
        }

        history = self._load_history()
        history.insert(0, {"type": "unit_economics", "data": result})
        self._save_history(history[:50])
        return result

    def diagnose_funnel(
        self,
        impressions: int,
        clicks: int,
        leads_mql: int,
        opportunities_sql: int,
        closed_won: int
    ) -> Dict[str, Any]:
        """
        Diagnoses conversion bottlenecks across the 4 stages of the growth funnel.
        """
        ctr_pct = (clicks / impressions * 100.0) if impressions > 0 else 0.0
        click_to_mql_pct = (leads_mql / clicks * 100.0) if clicks > 0 else 0.0
        mql_to_sql_pct = (opportunities_sql / leads_mql * 100.0) if leads_mql > 0 else 0.0
        sql_to_won_pct = (closed_won / opportunities_sql * 100.0) if opportunities_sql > 0 else 0.0
        overall_conversion_pct = (closed_won / clicks * 100.0) if clicks > 0 else 0.0

        # Bottleneck detection
        bottlenecks = []
        if ctr_pct < 1.0:
            bottlenecks.append("Atracción (CTR bajo < 1.0%): Optimizar creativos, propuesta de valor y segmentación de anuncios.")
        if click_to_mql_pct < 3.0:
            bottlenecks.append("Captura (Click a Lead < 3.0%): Landing page con fricción excesiva o promesa desalineada.")
        if mql_to_sql_pct < 20.0:
            bottlenecks.append("Calificación (MQL a SQL < 20%): Filtrar leads no cualificados o implementar lead scoring.")
        if sql_to_won_pct < 20.0:
            bottlenecks.append("Cierre (SQL a Won < 20%): Objeciones de precio, demo débil o ciclo comercial dilatado.")

        if not bottlenecks:
            bottleneck_summary = "Flujo equilibrado y eficiente en todas las etapas del funnel."
        else:
            bottleneck_summary = "Cuello de botella principal detectado en: " + "; ".join(bottlenecks)

        result = {
            "stages": {
                "impressions": impressions,
                "clicks": clicks,
                "leads_mql": leads_mql,
                "opportunities_sql": opportunities_sql,
                "closed_won": closed_won
            },
            "conversion_rates": {
                "ctr_pct": round(ctr_pct, 2),
                "click_to_mql_pct": round(click_to_mql_pct, 2),
                "mql_to_sql_pct": round(mql_to_sql_pct, 2),
                "sql_to_won_pct": round(sql_to_won_pct, 2),
                "overall_conversion_pct": round(overall_conversion_pct, 3)
            },
            "bottlenecks": bottlenecks,
            "bottleneck_summary": bottleneck_summary,
            "timestamp": datetime.now().isoformat()
        }

        history = self._load_history()
        history.insert(0, {"type": "funnel_diagnostic", "data": result})
        self._save_history(history[:50])
        return result

    def calculate_roas_and_attribution(
        self,
        channels: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyzes ad spend efficiency across channels (Meta, Google, LinkedIn, etc.):
        - ROAS = Revenue / Spend
        - Blended CAC
        - Marginal budget recommendation
        """
        total_spend = 0.0
        total_revenue = 0.0
        total_conversions = 0

        analyzed_channels = []
        for ch in channels:
            name = ch.get("channel", "Canal")
            spend = float(ch.get("spend", 0.0))
            revenue = float(ch.get("revenue", 0.0))
            conversions = int(ch.get("conversions", 0))

            roas = (revenue / spend) if spend > 0 else 0.0
            cpa = (spend / conversions) if conversions > 0 else 0.0

            total_spend += spend
            total_revenue += revenue
            total_conversions += conversions

            analyzed_channels.append({
                "channel": name,
                "spend": round(spend, 2),
                "revenue": round(revenue, 2),
                "conversions": conversions,
                "roas": round(roas, 2),
                "cpa": round(cpa, 2),
                "efficiency": "Alta" if roas >= 3.5 else ("Media" if roas >= 2.0 else "Baja")
            })

        blended_roas = (total_revenue / total_spend) if total_spend > 0 else 0.0
        blended_cac = (total_spend / total_conversions) if total_conversions > 0 else 0.0

        # Sort channels by ROAS descending
        analyzed_channels.sort(key=lambda x: x["roas"], reverse=True)
        best_channel = analyzed_channels[0]["channel"] if analyzed_channels else "N/A"

        result = {
            "total_spend": round(total_spend, 2),
            "total_revenue": round(total_revenue, 2),
            "total_conversions": total_conversions,
            "blended_roas": round(blended_roas, 2),
            "blended_cac": round(blended_cac, 2),
            "best_channel": best_channel,
            "channels": analyzed_channels,
            "recommendation": f"Asignar mayor presupuesto marginal a '{best_channel}' por liderar el ROAS de la cartera.",
            "timestamp": datetime.now().isoformat()
        }

        history = self._load_history()
        history.insert(0, {"type": "roas_attribution", "data": result})
        self._save_history(history[:50])
        return result


marketing_growth_service = MarketingGrowthService()
