# -*- coding: utf-8 -*-
"""
Dividend Screener & Tight Budget Portfolio Allocator for Liseth.
Analyzes accessible dividend-paying stocks in Colombia (BVC) and Wall Street (US),
calculating optimal allocation for constrained budgets and DRIP (Dividend Reinvestment Plan) compounding.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("liseth.dividend_screener")

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
HISTORY_FILE = DATA_DIR / "dividend_screener_history.json"

# Stock Database with Dividend Yields & Fundamentals
DIVIDEND_CATALOG: List[Dict[str, Any]] = [
    # BVC (Colombia)
    {
        "ticker": "PFAVAL",
        "name": "Grupo Aval Acciones y Valores Pref.",
        "market": "BVC",
        "currency": "COP",
        "price": 485.0,
        "dividend_yield_pct": 8.25,
        "payout_frequency": "Mensual",
        "annual_dividend_per_share": 40.0,
        "sector": "Financiero",
        "budget_accessibility": "EXTREMA (Menos de $1,000 COP por acción)",
        "drip_eligible": True,
        "description": "Holding financiero líder en Colombia. Excelente para presupuestos micro por su bajo precio nominal y pago mensual."
    },
    {
        "ticker": "ECOPETROL",
        "name": "Ecopetrol S.A.",
        "market": "BVC",
        "currency": "COP",
        "price": 1960.0,
        "dividend_yield_pct": 11.80,
        "payout_frequency": "Trimestral",
        "annual_dividend_per_share": 231.28,
        "sector": "Energía & Petróleo",
        "budget_accessibility": "ALTA (Acceso con presupuestos desde $20,000 COP)",
        "drip_eligible": True,
        "description": "Mayor empresa petrolera de Colombia con dividendos históricos de dos dígitos y alto flujo de caja libre."
    },
    {
        "ticker": "GEB",
        "name": "Grupo Energía Bogotá",
        "market": "BVC",
        "currency": "COP",
        "price": 2480.0,
        "dividend_yield_pct": 8.60,
        "payout_frequency": "Semestral",
        "annual_dividend_per_share": 213.28,
        "sector": "Servicios Públicos",
        "budget_accessibility": "ALTA (Menos de $3,000 COP por acción)",
        "drip_eligible": True,
        "description": "Generación y transmisión eléctrica en Colombia, Perú y Brasil. Ingresos regulados y defensivos."
    },
    {
        "ticker": "CELSIA",
        "name": "Celsia S.A. E.S.P.",
        "market": "BVC",
        "currency": "COP",
        "price": 3820.0,
        "dividend_yield_pct": 7.45,
        "payout_frequency": "Trimestral",
        "annual_dividend_per_share": 284.59,
        "sector": "Energías Renovables",
        "budget_accessibility": "MEDIA-ALTA",
        "drip_eligible": True,
        "description": "Pionero en energía solar y transición energética con dividendos constantes respaldados por contratos PPA."
    },
    {
        "ticker": "MINEROS",
        "name": "Mineros S.A.",
        "market": "BVC",
        "currency": "COP",
        "price": 2150.0,
        "dividend_yield_pct": 8.10,
        "payout_frequency": "Trimestral",
        "annual_dividend_per_share": 174.15,
        "sector": "Materiales Básicos & Oro",
        "budget_accessibility": "ALTA (Alrededor de $2,000 COP)",
        "drip_eligible": True,
        "description": "Productora aurífera con operaciones en Colombia y Nicaragua; dividendo indexado en USD pagado en pesos."
    },
    {
        "ticker": "ISA",
        "name": "Interconexión Eléctrica S.A.",
        "market": "BVC",
        "currency": "COP",
        "price": 18900.0,
        "dividend_yield_pct": 7.30,
        "payout_frequency": "Semestral",
        "annual_dividend_per_share": 1379.70,
        "sector": "Infraestructura & Redes",
        "budget_accessibility": "MEDIA",
        "drip_eligible": True,
        "description": "Monopolio natural en transmisión eléctrica de alta tensión en América Latina con ingresos de ultra bajo riesgo."
    },
    {
        "ticker": "PFBCOLOM",
        "name": "Bancolombia Pref.",
        "market": "BVC",
        "currency": "COP",
        "price": 34800.0,
        "dividend_yield_pct": 8.90,
        "payout_frequency": "Trimestral",
        "annual_dividend_per_share": 3097.20,
        "sector": "Financiero",
        "budget_accessibility": "MEDIA (Ideal para paquetes acumulativos)",
        "drip_eligible": True,
        "description": "Institución bancaria número 1 de Colombia y Centroamérica. Blue-chip por excelencia con sólida solvencia."
    },

    # US Stocks (Wall Street)
    {
        "ticker": "VALE",
        "name": "Vale S.A. ADR",
        "market": "US",
        "currency": "USD",
        "price": 10.40,
        "dividend_yield_pct": 8.40,
        "payout_frequency": "Semestral",
        "annual_dividend_per_share": 0.87,
        "sector": "Minería & Mineral de Hierro",
        "budget_accessibility": "EXTREMA (~$10 USD por acción)",
        "drip_eligible": True,
        "description": "Gigante minero global con bajísimo coste de entrada e historial de dividendos sustanciales."
    },
    {
        "ticker": "F",
        "name": "Ford Motor Company",
        "market": "US",
        "currency": "USD",
        "price": 10.85,
        "dividend_yield_pct": 5.60,
        "payout_frequency": "Trimestral",
        "annual_dividend_per_share": 0.60,
        "sector": "Automotriz",
        "budget_accessibility": "EXTREMA (~$11 USD por acción)",
        "drip_eligible": True,
        "description": "Acceso accesible a la industria automotriz global con dividendos trimestrales regulares más especiales."
    },
    {
        "ticker": "T",
        "name": "AT&T Inc.",
        "market": "US",
        "currency": "USD",
        "price": 21.50,
        "dividend_yield_pct": 5.15,
        "payout_frequency": "Trimestral",
        "annual_dividend_per_share": 1.11,
        "sector": "Telecomunicaciones",
        "budget_accessibility": "ALTA (~$21 USD)",
        "drip_eligible": True,
        "description": "Flujo de caja libre masivo post-escisión de WarnerMedia enfocado 100% en 5G y fibra óptica."
    },
    {
        "ticker": "PFE",
        "name": "Pfizer Inc.",
        "market": "US",
        "currency": "USD",
        "price": 28.30,
        "dividend_yield_pct": 5.95,
        "payout_frequency": "Trimestral",
        "annual_dividend_per_share": 1.68,
        "sector": "Salud & Farmacéutica",
        "budget_accessibility": "ALTA (~$28 USD)",
        "drip_eligible": True,
        "description": "Líder biofarmacéutico con cartera madura de oncología y vacunas, rindiendo cerca del 6% de dividendo."
    },
    {
        "ticker": "O",
        "name": "Realty Income Corp",
        "market": "US",
        "currency": "USD",
        "price": 53.80,
        "dividend_yield_pct": 5.85,
        "payout_frequency": "Mensual",
        "annual_dividend_per_share": 3.15,
        "sector": "Bienes Raíces (REIT)",
        "budget_accessibility": "MEDIA (Aristócrata de Dividendos Mensuales)",
        "drip_eligible": True,
        "description": "El estándar de oro en bienes raíces comerciales: pago de dividendo mensual ininterrumpido por más de 25 años."
    },
    {
        "ticker": "MO",
        "name": "Altria Group, Inc.",
        "market": "US",
        "currency": "USD",
        "price": 50.90,
        "dividend_yield_pct": 7.95,
        "payout_frequency": "Trimestral",
        "annual_dividend_per_share": 4.08,
        "sector": "Consumo Defensivo",
        "budget_accessibility": "MEDIA",
        "drip_eligible": True,
        "description": "Poder de fijación de precios inelástico y rey de dividendos con 54 años consecutivos de incrementos."
    }
]


class DividendScreenerService:
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
            logger.error(f"[DIVIDEND_ERR] Error loading history: {e}")
        return []

    def _save_history(self, history: List[Dict[str, Any]]) -> None:
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[DIVIDEND_ERR] Error saving history: {e}")

    def list_available_stocks(self, market: Optional[str] = None) -> List[Dict[str, Any]]:
        if not market or market.upper() == "ALL":
            return DIVIDEND_CATALOG
        m = market.upper()
        return [s for s in DIVIDEND_CATALOG if s["market"].upper() == m]

    def screen_dividend_stocks(
        self,
        budget: float,
        market: str = "BVC",
        min_yield_pct: float = 5.0,
        reinvest_dividends: bool = True,
        projection_years: int = 5
    ) -> Dict[str, Any]:
        """
        Screens stocks within budget, prioritizes accessibility, allocates capital,
        and projects dividend cashflow and DRIP compounding over 1, 3, and 5 years.
        """
        budget_val = max(100.0 if market.upper() == "BVC" else 1.0, float(budget))
        m = market.upper()
        currency = "COP" if m == "BVC" else "USD"

        # 1. Filter eligible candidates
        candidates = [
            s for s in DIVIDEND_CATALOG
            if s["market"].upper() == m and s["dividend_yield_pct"] >= min_yield_pct
        ]

        if not candidates:
            # Fallback to any in that market
            candidates = [s for s in DIVIDEND_CATALOG if s["market"].upper() == m]

        # Sort candidates primarily by affordability and dividend yield
        candidates.sort(key=lambda x: (x["price"], -x["dividend_yield_pct"]))

        # 2. Portfolio Allocation within Budget
        # Distribute budget across the top accessible candidates
        portfolio = []
        remaining_budget = budget_val

        # Find affordable stocks
        affordable = [s for s in candidates if s["price"] <= remaining_budget]

        if not affordable:
            # Even the cheapest stock is too expensive for total budget
            cheapest = candidates[0]
            recommendation = (
                f"El presupuesto de {currency} {budget_val:,.2f} no alcanza para comprar 1 acción completa "
                f"de {cheapest['ticker']} ({currency} {cheapest['price']:,.2f}). "
                f"Se recomienda un ahorro acumulativo hasta alcanzar al menos {currency} {cheapest['price']:,.2f}."
            )
            return {
                "budget": budget_val,
                "currency": currency,
                "market": m,
                "status": "INSUFFICIENT_BUDGET",
                "recommendation": recommendation,
                "cheapest_alternative": cheapest,
                "portfolio": [],
                "summary": {
                    "total_invested": 0.0,
                    "cash_remaining": budget_val,
                    "expected_annual_dividend": 0.0,
                    "weighted_yield_pct": 0.0
                },
                "drip_projections": []
            }

        # Diversified weighting: prioritize low unit cost + high yield
        target_stocks = affordable[:4]  # Top 3-4 stocks
        equal_weight = remaining_budget / len(target_stocks)

        total_annual_dividends = 0.0
        total_invested = 0.0

        for stock in target_stocks:
            stock_budget = equal_weight
            shares = int(stock_budget // stock["price"])
            if shares > 0:
                cost = shares * stock["price"]
                annual_div = shares * stock["annual_dividend_per_share"]
                total_invested += cost
                total_annual_dividends += annual_div
                remaining_budget -= cost
                portfolio.append({
                    "ticker": stock["ticker"],
                    "name": stock["name"],
                    "sector": stock["sector"],
                    "price_per_share": stock["price"],
                    "shares_to_buy": shares,
                    "total_cost": round(cost, 2),
                    "dividend_yield_pct": stock["dividend_yield_pct"],
                    "annual_dividend_income": round(annual_div, 2),
                    "payout_frequency": stock["payout_frequency"],
                    "budget_accessibility": stock["budget_accessibility"]
                })

        # If remaining budget can still buy more of the cheapest stock, buy them
        if portfolio and remaining_budget >= portfolio[0]["price_per_share"]:
            extra_shares = int(remaining_budget // portfolio[0]["price_per_share"])
            if extra_shares > 0:
                extra_cost = extra_shares * portfolio[0]["price_per_share"]
                portfolio[0]["shares_to_buy"] += extra_shares
                portfolio[0]["total_cost"] = round(portfolio[0]["total_cost"] + extra_cost, 2)
                extra_div = extra_shares * (portfolio[0]["annual_dividend_income"] / (portfolio[0]["shares_to_buy"] - extra_shares))
                portfolio[0]["annual_dividend_income"] = round(portfolio[0]["annual_dividend_income"] + extra_div, 2)
                total_invested += extra_cost
                total_annual_dividends += extra_div
                remaining_budget -= extra_cost

        weighted_yield = (total_annual_dividends / total_invested * 100) if total_invested > 0 else 0.0

        # 3. DRIP (Dividend Reinvestment Plan) Multi-Year Compounding Projection
        # Assumes dividend reinvestment at weighted yield + modest 3.5% capital appreciation
        drip_projections = []
        current_corpus = total_invested
        annual_div_flow = total_annual_dividends

        years_to_simulate = min(max(projection_years, 1), 10)
        for yr in range(1, years_to_simulate + 1):
            if reinvest_dividends:
                # Reinvest dividends into the capital base + 3.5% asset appreciation
                earned_div = current_corpus * (weighted_yield / 100.0)
                current_corpus = (current_corpus + earned_div) * 1.035
            else:
                earned_div = current_corpus * (weighted_yield / 100.0)
                current_corpus = current_corpus * 1.035

            drip_projections.append({
                "year": yr,
                "projected_portfolio_value": round(current_corpus, 2),
                "projected_annual_dividend": round(current_corpus * (weighted_yield / 100.0), 2),
                "cumulative_dividends_reinvested": round(current_corpus - total_invested, 2) if reinvest_dividends else round(earned_div * yr, 2)
            })

        result = {
            "budget": round(budget_val, 2),
            "currency": currency,
            "market": m,
            "status": "SUCCESS",
            "summary": {
                "total_invested": round(total_invested, 2),
                "cash_remaining": round(remaining_budget, 2),
                "expected_annual_dividend": round(total_annual_dividends, 2),
                "expected_monthly_average": round(total_annual_dividends / 12.0, 2),
                "weighted_yield_pct": round(weighted_yield, 2),
                "number_of_stocks": len(portfolio)
            },
            "portfolio": portfolio,
            "drip_projections": drip_projections,
            "strategy_advice": (
                f"Estrategia de dividendos optimizada para capital reducido: con {currency} {total_invested:,.2f} "
                f"ha adquirido participaciones en {len(portfolio)} empresas defensivas, generando un rendimiento por dividendo "
                f"ponderado de {weighted_yield:.2f}% anual ({currency} {total_annual_dividends:,.2f}/año). "
                f"Reinvertir sistemáticamente estos dividendos (DRIP) acelera el interés compuesto exponencialmente."
            ),
            "timestamp": datetime.now().isoformat()
        }

        history = self._load_history()
        history.insert(0, {"type": "dividend_screening", "data": result})
        self._save_history(history[:50])
        return result


dividend_screener_service = DividendScreenerService()
