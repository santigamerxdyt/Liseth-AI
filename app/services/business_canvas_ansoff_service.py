"""
Business Model Canvas & Ansoff Growth Strategy Service for JARVIS / Liseth.
Combines Alexander Osterwalder's 9-block Business Model Canvas with Igor Ansoff's
Product-Market Growth Matrix to deliver actionable strategic intelligence for Señor Santiago.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvis.business_canvas_ansoff")


class BusinessCanvasAnsoffService:
    """
    Strategic engine for business model architecture, risk-adjusted growth vectors,
    and commercial expansion roadmaps.
    """

    ANSOFF_QUADRANTS = {
        "market_penetration": {
            "name": "Penetración de Mercado (Mercado Actual / Producto Actual)",
            "risk_level": "Bajo (1.0x)",
            "primary_focus": "Aumento de cuota de mercado, fidelización, maximización de LTV y programas de lealtad.",
            "typical_roi_pct": 22.5,
            "payback_months": 8,
            "strategic_initiatives": [
                "Optimización de embudo comercial y retención de clientes existentes",
                "Ajuste táctico de precios por volumen o planes de fidelización anual",
                "Campañas de captación hipersegmentadas sobre clientes de la competencia"
            ]
        },
        "product_development": {
            "name": "Desarrollo de Nuevos Productos (Mercado Actual / Producto Nuevo)",
            "risk_level": "Moderado (2.0x)",
            "primary_focus": "I+D, innovación de catálogo, ventas cruzadas (Cross-selling) y upselling sobre clientes fieles.",
            "typical_roi_pct": 32.0,
            "payback_months": 14,
            "strategic_initiatives": [
                "Lanzamiento de versiones Premium / Enterprise o add-ons de alto valor",
                "Extensión de línea complementaria para resolver fricciones del usuario",
                "Ciclos iterativos de producto basados en Voice of Customer (VoC)"
            ]
        },
        "market_development": {
            "name": "Desarrollo de Nuevos Mercados (Nuevo Mercado / Producto Actual)",
            "risk_level": "Moderado-Alto (2.2x)",
            "primary_focus": "Expansión geográfica, apertura de canales B2B/B2G o targeting a nuevos segmentos demográficos.",
            "typical_roi_pct": 28.0,
            "payback_months": 16,
            "strategic_initiatives": [
                "Entrada a ciudades satélite en Colombia o mercados andinos (Perú/Ecuador/México)",
                "Apertura de canal digital institucional o alianzas de distribución mayorista",
                "Adaptación de packaging, empaque o pricing a microsegmentos emergentes"
            ]
        },
        "diversification": {
            "name": "Diversificación (Nuevo Mercado / Nuevo Producto)",
            "risk_level": "Alto (4.0x)",
            "primary_focus": "Creación de nuevas unidades de negocio fuera del núcleo central (diversificación concéntrica o conglomerada).",
            "typical_roi_pct": 45.0,
            "payback_months": 24,
            "strategic_initiatives": [
                "Spin-off tecnológico o integración vertical hacia atrás/adelante",
                "Adquisición de activos complementarios con sinergias operativas clave",
                "Blindaje de flujos de caja mediante fuentes de ingreso descorrelacionadas"
            ]
        }
    }

    def evaluate_canvas_and_ansoff(
        self,
        project_name: str,
        industry: str = "Servicios / Tecnología / Comercio",
        value_proposition: str = "",
        customer_segments: str = "",
        channels: str = "",
        customer_relationships: str = "",
        revenue_streams: str = "",
        key_resources: str = "",
        key_activities: str = "",
        key_partners: str = "",
        cost_structure: str = "",
        ansoff_quadrant: str = "market_penetration",
        investment_budget: float = 30000000.0,
        currency: str = "COP"
    ) -> Dict[str, Any]:
        """
        Synthesizes the 9 Osterwalder canvas blocks, scores strategic consistency,
        and builds an Ansoff matrix growth roadmap with financial projections.
        """
        # Validate quadrant
        quadrant_key = ansoff_quadrant.lower().replace(" ", "_")
        if quadrant_key not in self.ANSOFF_QUADRANTS:
            quadrant_key = "market_penetration"
        quadrant_data = self.ANSOFF_QUADRANTS[quadrant_key]

        # Standardize 9 blocks
        vp = value_proposition.strip() or "Solución integral de alto valor con eficiencia operativa y servicio personalizado."
        cs = customer_segments.strip() or "Empresas medianas (B2B) y profesionales ejecutivos en Colombia."
        ch = channels.strip() or "Canal directo digital (Web/App), fuerza de ventas consultiva y redes corporativas."
        cr = customer_relationships.strip() or "Atención personalizada, soporte continuo y automatización omnicanal."
        rs = revenue_streams.strip() or "Suscripciones mensuales recurrentes, honorarios de consultoría y comisiones de éxito."
        kr = key_resources.strip() or "Plataforma tecnológica propietaria, talento directivo y capital de trabajo."
        ka = key_activities.strip() or "Desarrollo continuo de soluciones, gestión de relaciones y marketing de atracción."
        kp = key_partners.strip() or "Proveedores de infraestructura en la nube, pasarelas de pago y agremiaciones del sector."
        cost = cost_structure.strip() or "Nómina técnica/comercial, infraestructura tecnológica y presupuesto de adquisición (CAC)."

        # Strategic Coherence Scoring (0-100)
        coherence_score = 75.0
        strengths = []
        bottlenecks = []

        if len(vp) > 25 and len(cs) > 20:
            coherence_score += 7.0
            strengths.append("Alineación clara entre Propuesta de Valor y Segmento de Clientes objetivo.")
        else:
            bottlenecks.append("La propuesta de valor o el segmento requieren mayor especificidad para evitar dilución comercial.")

        if "recurrent" in rs.lower() or "suscrip" in rs.lower() or "mensual" in rs.lower():
            coherence_score += 8.0
            strengths.append("Modelo de monetización recurrente que reduce volatilidad y eleva el múltiplo de valoración.")
        else:
            bottlenecks.append("Dependencia de ventas transaccionales no recurrentes; se sugiere explorar modelos de suscripción.")

        if len(kp) > 20 and len(ch) > 20:
            coherence_score += 5.0
            strengths.append("Red de aliados estratégicos y canales de distribución balanceados.")
        else:
            bottlenecks.append("Canales o alianzas poco estructurados para un escalamiento ágil.")

        if investment_budget > 0:
            coherence_score += 5.0

        coherence_score = min(98.0, max(50.0, coherence_score))

        # Financial Calculations based on Ansoff Quadrant
        expected_roi_pct = quadrant_data["typical_roi_pct"]
        payback_months = quadrant_data["payback_months"]
        projected_gross_return = investment_budget * (1.0 + (expected_roi_pct / 100.0))
        net_profit_expansion = projected_gross_return - investment_budget

        # 4-Quarter Implementation Roadmap
        roadmap = [
            {
                "phase": "Q1: Diagnóstico & Refinamiento del Canvas",
                "focus": "Validación de propuesta de valor con clientes piloto y blindaje de estructura de costos.",
                "milestone": "3 a 5 contratos cerrados / NPS inicial > 70 pts."
            },
            {
                "phase": f"Q2: Despliegue de Estrategia Ansoff ({quadrant_data['name'].split('(')[0].strip()})",
                "focus": quadrant_data["strategic_initiatives"][0],
                "milestone": f"Alcanzar el 30% del retorno proyectado (${(net_profit_expansion * 0.3):,.0f} {currency})."
            },
            {
                "phase": "Q3: Escalamiento y Eficiencia de Canales",
                "focus": quadrant_data["strategic_initiatives"][1],
                "milestone": f"Recuperación estimada de capital (Payback proyectado: mes {payback_months})."
            },
            {
                "phase": "Q4: Consolidación, Alianzas y Múltiplos",
                "focus": quadrant_data["strategic_initiatives"][2],
                "milestone": f"Generación total estimada de ${(net_profit_expansion):,.0f} {currency} en nuevo valor neto."
            }
        ]

        # Compile full canvas dictionary
        canvas_blocks = {
            "value_proposition": vp,
            "customer_segments": cs,
            "channels": ch,
            "customer_relationships": cr,
            "revenue_streams": rs,
            "key_resources": kr,
            "key_activities": ka,
            "key_partners": kp,
            "cost_structure": cost
        }

        return {
            "project_name": project_name,
            "industry": industry,
            "canvas_blocks": canvas_blocks,
            "coherence_score": round(coherence_score, 1),
            "coherence_status": "Excelente / Alta Viabilidad" if coherence_score >= 85 else "Favorable / Requiere Ajustes Menores",
            "ansoff_strategy": {
                "quadrant_key": quadrant_key,
                "name": quadrant_data["name"],
                "risk_level": quadrant_data["risk_level"],
                "primary_focus": quadrant_data["primary_focus"],
                "expected_roi_pct": expected_roi_pct,
                "payback_months": payback_months,
                "strategic_initiatives": quadrant_data["strategic_initiatives"]
            },
            "financials": {
                "investment_budget": investment_budget,
                "projected_gross_return": projected_gross_return,
                "net_profit_expansion": net_profit_expansion,
                "currency": currency
            },
            "strengths": strengths,
            "bottlenecks": bottlenecks,
            "roadmap": roadmap
        }


business_canvas_ansoff_service = BusinessCanvasAnsoffService()
