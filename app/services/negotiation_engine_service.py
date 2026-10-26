"""
Strategic Negotiation & Conflict Resolution Service for Liseth / JARVIS.
Implements the Harvard Negotiation Project Framework (Fisher, Ury & Patton):
- ZOPA Calculation (Zone of Possible Agreement / Zona de Posible Acuerdo)
- BATNA Assessment (Best Alternative to a Negotiated Agreement / MAAN)
- Reservation Price & Target Price Surplus Dynamics (Nash Equilibrium)
- Interests vs Positions Matrix & Value Creation Tactics
"""
from typing import Any, Dict, List, Optional


class NegotiationEngineService:
    def __init__(self):
        pass

    def evaluate_negotiation(
        self,
        buyer_reservation_price: float,
        seller_reservation_price: float,
        buyer_target_price: Optional[float] = None,
        seller_target_price: Optional[float] = None,
        buyer_batna: Optional[str] = None,
        seller_batna: Optional[str] = None,
        currency: str = "COP"
    ) -> Dict[str, Any]:
        """
        Analyzes buyer/seller negotiation boundaries, ZOPA existence, and surplus distribution.
        """
        b_res = float(buyer_reservation_price)
        s_res = float(seller_reservation_price)

        b_tgt = float(buyer_target_price) if buyer_target_price is not None else b_res * 0.85
        s_tgt = float(seller_target_price) if seller_target_price is not None else s_res * 1.15

        has_zopa = b_res >= s_res
        zopa_size = round(b_res - s_res, 2) if has_zopa else 0.0
        gap = round(s_res - b_res, 2) if not has_zopa else 0.0

        midpoint_agreement = round((b_res + s_res) / 2.0, 2) if has_zopa else None

        # Strategic advice
        if has_zopa:
            status = "ZOPA_POSITIVA"
            verdict = (
                f"Existe una Zona de Posible Acuerdo (ZOPA) de ${zopa_size:,.2f} {currency}. "
                f"Cualquier acuerdo entre ${s_res:,.2f} y ${b_res:,.2f} genera excedente para ambas partes. "
                f"El punto medio equitativo de Nash se sitúa en ${midpoint_agreement:,.2f} {currency}."
            )
        else:
            status = "ZOPA_NEGATIVA_IMPASSE"
            verdict = (
                f"No existe ZOPA monetaria directa. Hay una brecha de ${gap:,.2f} {currency} entre el mínimo "
                f"del vendedor (${s_res:,.2f}) y el máximo del comprador (${b_res:,.2f}). "
                f"Se recomienda ejecutar el BATNA o incorporar variables no monetarias (plazos, exclusividad, soporte, garantías)."
            )

        tactics = [
            {
                "principle": "Separar a las personas del problema",
                "tactic": "Despersonalizar el conflicto; enfocarse en métricas operativas y mantener una relación cordial y profesional."
            },
            {
                "principle": "Enfocarse en intereses y no en posiciones",
                "tactic": "Descubrir por qué el cliente exige ese precio (¿flujo de caja, presupuesto anual, riesgo percibido?) y estructurar pagos diferidos."
            },
            {
                "principle": "Inventar opciones de mutuo beneficio",
                "tactic": "Ampliar la torta: intercambiar concesiones de bajo costo para usted pero de alto valor para la contraparte."
            },
            {
                "principle": "Insistir en criterios objetivos",
                "tactic": "Respaldar la propuesta con precios de referencia de mercado, índices de inflación IPC y retorno sobre inversión (ROI)."
            }
        ]

        return {
            "status": status,
            "has_zopa": has_zopa,
            "zopa_size": zopa_size,
            "gap": gap,
            "currency": currency,
            "buyer": {
                "reservation_price": b_res,
                "target_price": b_tgt,
                "batna": buyer_batna or "Explorar proveedores alternativos en el mercado regional"
            },
            "seller": {
                "reservation_price": s_res,
                "target_price": s_tgt,
                "batna": seller_batna or "Mantener capacidad instalada para otros proyectos de consultoría"
            },
            "fair_midpoint_price": midpoint_agreement,
            "verdict": verdict,
            "harvard_tactics": tactics
        }

    def format_markdown_report(self, data: Dict[str, Any]) -> str:
        curr = data["currency"]
        b = data["buyer"]
        s = data["seller"]
        zopa_txt = "🟢 ZOPA POSITIVA (Acuerdo Viable)" if data["has_zopa"] else "🔴 ZOPA NEGATIVA (Impasse / Brecha)"

        md = [
            "# 🤝 SIMULADOR DE NEGOCIACIÓN ESTRATÉGICA (MODELO HARVARD)",
            f"**Diagnóstico de Viabilidad**: `{zopa_txt}`",
            "",
            "### ⚖️ Límites y Precios de Reserva",
            f"- **Comprador - Precio Máximo de Reserva**: `${b['reservation_price']:,.2f} {curr}`",
            f"- **Comprador - Precio Objetivo Ideal**: `${b['target_price']:,.2f} {curr}`",
            f"- **Comprador - BATNA / MAAN**: *{b['batna']}*",
            "",
            f"- **Vendedor - Precio Mínimo de Reserva**: `${s['reservation_price']:,.2f} {curr}`",
            f"- **Vendedor - Precio Objetivo Ideal**: `${s['target_price']:,.2f} {curr}`",
            f"- **Vendedor - BATNA / MAAN**: *{s['batna']}*",
            "",
            f"> 💡 **Dictamen**: {data['verdict']}",
            ""
        ]

        if data["has_zopa"]:
            md.extend([
                f"- **Tamaño del Excedente Negociable (ZOPA)**: **`${data['zopa_size']:,.2f} {curr}`**",
                f"- **Punto Medio Equitativo (Solución de Nash)**: **`${data['fair_midpoint_price']:,.2f} {curr}`**",
                ""
            ])

        md.append("### 📚 Tácticas del Método Harvard")
        for t in data["harvard_tactics"]:
            md.append(f"- **{t['principle']}**: {t['tactic']}")

        return "\n".join(md)


negotiation_engine_service = NegotiationEngineService()
