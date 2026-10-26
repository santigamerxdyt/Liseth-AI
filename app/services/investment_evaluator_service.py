"""
Investment Project Evaluator Service for Liseth / JARVIS.
Provides rigorous financial evaluation of capital budgeting projects:
- Net Present Value (NPV / VAN)
- Internal Rate of Return (IRR / TIR) using numerical root finding
- Simple and Discounted Payback Period (Recuperación de la Inversión)
- Benefit-Cost Ratio (B/C / Relación Beneficio-Costo)
- Multi-Scenario Sensitivity Analysis (Base, Optimistic +20%, Pessimistic -20%)
- Executive Verdict and UNAL Palmira Business Administration Standards
"""
import uuid
from typing import Any, Dict, List, Optional


class InvestmentEvaluatorService:
    def __init__(self):
        pass

    def calculate_npv(self, initial_investment: float, cash_flows: List[float], discount_rate: float) -> float:
        """
        Calculates Net Present Value (VAN):
        NPV = -I_0 + sum(F_t / (1 + k)^t)
        """
        npv = -float(initial_investment)
        for t, flow in enumerate(cash_flows, start=1):
            npv += float(flow) / ((1.0 + discount_rate) ** t)
        return round(npv, 2)

    def calculate_irr(self, initial_investment: float, cash_flows: List[float], max_iter: int = 1000, tol: float = 1e-6) -> Optional[float]:
        """
        Calculates Internal Rate of Return (TIR) using Bisection method.
        Returns IRR as a decimal (e.g. 0.234 for 23.4%) or None if undefined.
        """
        low = -0.999
        high = 5.0  # up to 500%

        # Check signs
        npv_low = self.calculate_npv(initial_investment, cash_flows, low)
        npv_high = self.calculate_npv(initial_investment, cash_flows, high)

        if npv_low * npv_high > 0:
            # Check higher upper bound
            high = 20.0
            npv_high = self.calculate_npv(initial_investment, cash_flows, high)
            if npv_low * npv_high > 0:
                return None

        for _ in range(max_iter):
            mid = (low + high) / 2.0
            npv_mid = self.calculate_npv(initial_investment, cash_flows, mid)

            if abs(npv_mid) < tol or (high - low) / 2.0 < tol:
                return round(mid, 4)

            if (npv_low * npv_mid) <= 0:
                high = mid
                npv_high = npv_mid
            else:
                low = mid
                npv_low = npv_mid

        return round((low + high) / 2.0, 4)

    def calculate_payback(self, initial_investment: float, cash_flows: List[float]) -> Optional[float]:
        """
        Calculates simple payback period in years.
        """
        accumulated = 0.0
        for t, flow in enumerate(cash_flows, start=1):
            prev = accumulated
            accumulated += flow
            if accumulated >= initial_investment:
                fraction = (initial_investment - prev) / flow if flow > 0 else 0
                return round((t - 1) + fraction, 2)
        return None

    def calculate_discounted_payback(self, initial_investment: float, cash_flows: List[float], discount_rate: float) -> Optional[float]:
        """
        Calculates discounted payback period in years (PRD).
        """
        accumulated = 0.0
        for t, flow in enumerate(cash_flows, start=1):
            pv_flow = flow / ((1.0 + discount_rate) ** t)
            prev = accumulated
            accumulated += pv_flow
            if accumulated >= initial_investment:
                fraction = (initial_investment - prev) / pv_flow if pv_flow > 0 else 0
                return round((t - 1) + fraction, 2)
        return None

    def evaluate_project(
        self,
        name: str,
        initial_investment: float,
        cash_flows: List[float],
        discount_rate: float = 0.12,
        currency: str = "COP"
    ) -> Dict[str, Any]:
        """
        Evaluates a complete capital budgeting proposal with multi-scenario analysis.
        """
        inv = float(initial_investment)
        flows = [float(f) for f in cash_flows]
        k = float(discount_rate)

        # Base Calculations
        npv_base = self.calculate_npv(inv, flows, k)
        irr_base = self.calculate_irr(inv, flows)
        payback_simple = self.calculate_payback(inv, flows)
        payback_discounted = self.calculate_discounted_payback(inv, flows, k)

        # Present Value of Inflows
        pv_inflows = npv_base + inv
        bcr = round(pv_inflows / inv, 3) if inv > 0 else 0.0

        # Executive Verdict
        if npv_base > 0 and (irr_base is not None and irr_base > k):
            decision = "VIABLE_EXCELENTE"
            verdict = "PROYECTO ALTAMENTE VIABLE: Genera riqueza neta superior a la tasa de descuento exigida (VAN > 0 y TIR > WACC)."
        elif npv_base > 0:
            decision = "VIABLE"
            verdict = "PROYECTO VIABLE: Rentabilidad suficiente para cubrir el costo de oportunidad del capital (VAN > 0)."
        elif npv_base == 0:
            decision = "EQUILIBRIO"
            verdict = "PROYECTO EN PUNTO DE EQUILIBRIO: Ni crea ni destruye valor corporativo (VAN = 0)."
        else:
            decision = "RECHAZADO"
            verdict = "PROYECTO NO VIABLE: Destruye valor patrimonial (VAN negativo). No se recomienda su ejecución."

        # Scenario Analysis
        optimistic_flows = [round(f * 1.20, 2) for f in flows]
        pessimistic_flows = [round(f * 0.80, 2) for f in flows]

        npv_opt = self.calculate_npv(inv, optimistic_flows, k)
        irr_opt = self.calculate_irr(inv, optimistic_flows)

        npv_pess = self.calculate_npv(inv, pessimistic_flows, k)
        irr_pess = self.calculate_irr(inv, pessimistic_flows)

        # Annual breakdown details
        annual_table = []
        accum = 0.0
        disc_accum = 0.0
        for t, flow in enumerate(flows, start=1):
            pv_f = round(flow / ((1.0 + k) ** t), 2)
            accum += flow
            disc_accum += pv_f
            annual_table.append({
                "period": t,
                "nominal_flow": flow,
                "discount_factor": round(1.0 / ((1.0 + k) ** t), 4),
                "discounted_flow": pv_f,
                "accumulated_nominal": round(accum, 2),
                "accumulated_discounted": round(disc_accum, 2)
            })

        project_id = f"PROJ-{uuid.uuid4().hex[:6].upper()}"

        result = {
            "project_id": project_id,
            "name": name,
            "currency": currency,
            "initial_investment": inv,
            "discount_rate_pct": round(k * 100, 2),
            "npv": npv_base,
            "irr_pct": round(irr_base * 100, 2) if irr_base is not None else None,
            "payback_years": payback_simple,
            "discounted_payback_years": payback_discounted,
            "benefit_cost_ratio": bcr,
            "decision": decision,
            "verdict": verdict,
            "scenarios": {
                "pessimistic_minus_20": {
                    "npv": npv_pess,
                    "irr_pct": round(irr_pess * 100, 2) if irr_pess is not None else None
                },
                "base": {
                    "npv": npv_base,
                    "irr_pct": round(irr_base * 100, 2) if irr_base is not None else None
                },
                "optimistic_plus_20": {
                    "npv": npv_opt,
                    "irr_pct": round(irr_opt * 100, 2) if irr_opt is not None else None
                }
            },
            "annual_table": annual_table
        }
        return result

    def format_markdown_report(self, eval_data: Dict[str, Any]) -> str:
        """
        Formats evaluation in an executive Markdown report.
        """
        curr = eval_data.get("currency", "COP")
        inv = eval_data["initial_investment"]
        k = eval_data["discount_rate_pct"]
        npv = eval_data["npv"]
        irr = eval_data["irr_pct"]
        pb = eval_data["payback_years"]
        dpb = eval_data["discounted_payback_years"]
        bcr = eval_data["benefit_cost_ratio"]
        verdict = eval_data["verdict"]

        md = [
            f"# 📊 EVALUACIÓN FINANCIERA DE PROYECTO: {eval_data['name'].upper()}",
            f"**ID del Proyecto**: `{eval_data['project_id']}` | **Moneda**: `{curr}`",
            "",
            "### 📈 Indicadores Financieros Clave",
            f"- **Inversión Inicial ($I_0$)**: `${inv:,.2f} {curr}`",
            f"- **Tasa de Oportunidad / WACC ($k$)**: `{k}%`",
            f"- **Valor Actual Neto (VAN / NPV)**: **`${npv:,.2f} {curr}`**",
            f"- **Tasa Interna de Retorno (TIR / IRR)**: **`{irr if irr is not None else 'N/A'}%`**",
            f"- **Período de Recuperación Simple (Payback)**: `{pb if pb is not None else '> horizonte'} años`",
            f"- **Período de Recuperación Descontado (PRD)**: `{dpb if dpb is not None else '> horizonte'} años`",
            f"- **Relación Beneficio / Costo (B/C)**: `{bcr}x`",
            "",
            f"> 💡 **Dictamen Ejecutivo**: {verdict}",
            "",
            "### 🎯 Análisis de Sensibilidad por Escenarios",
            "| Escenario | Variación Flujos | VAN (COP) | TIR (%) |",
            "| :--- | :--- | :--- | :--- |",
            f"| 🔴 Pesimista | -20% | `${eval_data['scenarios']['pessimistic_minus_20']['npv']:,.2f}` | `{eval_data['scenarios']['pessimistic_minus_20']['irr_pct']}%` |",
            f"| 🔵 Base | 0% | `${eval_data['scenarios']['base']['npv']:,.2f}` | `{eval_data['scenarios']['base']['irr_pct']}%` |",
            f"| 🟢 Optimista | +20% | `${eval_data['scenarios']['optimistic_plus_20']['npv']:,.2f}` | `{eval_data['scenarios']['optimistic_plus_20']['irr_pct']}%` |",
            "",
            "### 📋 Cronograma de Flujos Descontados",
            "| Año | Flujo Nominal | Factor Desc. | Flujo Descontado | Acumulado Descontado |",
            "| :---: | :---: | :---: | :---: | :---: |"
        ]

        for row in eval_data["annual_table"]:
            md.append(
                f"| {row['period']} | ${row['nominal_flow']:,.2f} | {row['discount_factor']} | ${row['discounted_flow']:,.2f} | ${row['accumulated_discounted']:,.2f} |"
            )

        return "\n".join(md)


investment_evaluator_service = InvestmentEvaluatorService()
