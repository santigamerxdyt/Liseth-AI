"""
Executive Pitch Deck & Presentation Generator Service for Liseth / JARVIS.
Generates structured, investor-grade 10-slide presentations based on Guy Kawasaki / Sequoia Capital standards:
- Slide 1: Title & Core Mission Statement
- Slide 2: The Critical Market Problem
- Slide 3: The Solution & Value Proposition
- Slide 4: Business Model & Monetization Engines
- Slide 5: The Underlying Magic / Proprietary Tech
- Slide 6: Market Opportunity (TAM, SAM, SOM)
- Slide 7: Go-to-Market & Customer Acquisition Strategy
- Slide 8: Competitive Landscape & Defensive Moat
- Slide 9: Management Team & Strategic Advisory
- Slide 10: Financial Pro-Forma Milestones & The Investment Ask
"""
from typing import Any, Dict, List, Optional


class PitchGeneratorService:
    def __init__(self):
        pass

    def generate_deck(
        self,
        business_name: str,
        industry: str = "tech_saas",
        problem_statement: Optional[str] = None,
        solution_value: Optional[str] = None,
        funding_ask: float = 250000000.0,
        currency: str = "COP",
        founder_name: str = "Santiago Huerfano Lopez",
        city: str = "Palmira / Cali, Colombia"
    ) -> Dict[str, Any]:
        """
        Creates an executive 10-slide pitch deck tailored to Colombian venture capital or university incubators.
        """
        b_name = business_name.strip()
        ind = industry.lower()

        if ind == "consultoria":
            tagline = "Excelencia en Estrategia Empresarial, Finanzas Cuantitativas y Operaciones"
            problem = problem_statement or "Las MiPyMes en el Valle del Cauca carecen de herramientas financieras sofisticadas (WACC, VAN, optimización tributaria) y pierden competitividad."
            solution = solution_value or "Consultoría directiva integral soportada por automatización analítica, auditoría continua y modelos matemáticos de alta precisión."
            tam = "$1.2 Billones COP (Mercado consultoría empresarial Colombia)"
            sam = "$180.000 Millones COP (Empresas sector servicios Valle y Suroccidente)"
            som = "$15.000 Millones COP (Objetivo 24 meses)"
            monetization = "Retainers mensuales de asesoría estratégica, comisiones de éxito por optimización de costos y licencias de software analítico."
            magic = "Framework automatizado de modelado financiero pro-forma y auditoría tributaria en tiempo real."
        elif ind == "agroindustria":
            tagline = "Innovación Biotecnológica y Eficiencia en Cadenas de Valor Agroindustriales"
            problem = problem_statement or "Altos costos en fertilizantes, pérdidas post-cosecha y trazabilidad fragmentada en cultivos de caña, frutas y granos del Valle del Cauca."
            solution = solution_value or "Plataforma integrada de bio-insumos optimizados y monitoreo en tiempo real con trazabilidad NFC/QR desde el campo hasta la distribución."
            tam = "$8.5 Billones COP (Producción agroindustrial Colombia)"
            sam = "$1.4 Billones COP (Sector agroindustrial y azucarero Valle del Cauca)"
            som = "$80.000 Millones COP (Captura inicial en 3 años)"
            monetization = "Venta directa de bio-soluciones, suscripción a sensores de campo y comisiones por intermediación logística."
            magic = "Protocolos biotecnológicos validados por investigación académica UNAL y algoritmos de predicción climática."
        elif ind == "ecommerce":
            tagline = "Comercio Electrónico de Nueva Generación con Liquidación Inmediata Bre-B"
            problem = problem_statement or "Comisiones abusivas de pasarelas de pago (3.5% + IVA) y lentitud en desembolsos ahogan el flujo de caja de comerciantes locales."
            solution = solution_value or "Ecosistema de cobros omnicanal sin fricción mediante transferencias interoperables Bre-B y pagos por contacto NFC con acreditación en 0 segundos."
            tam = "$5.4 Billones COP (Transacciones de comercio digital Colombia)"
            sam = "$750.000 Millones COP (Comercio minorista independiente regional)"
            som = "$45.000 Millones COP (Volumen procesado meta a 18 meses)"
            monetization = "Tarifa plana ultra baja por transacción (0.4%), módulos premium de analítica de clientes y terminales NFC de hardware."
            magic = "Enrutamiento inteligente directo con el Banco de la República y emulación de tarjetas contactless."
        else:  # tech_saas (default)
            tagline = "Inteligencia Artificial y Automatización Ejecutiva para Alta Dirección"
            problem = problem_statement or "Los directores ejecutivos pierden hasta el 40% de su jornada en tareas administrativas dispersas y análisis de datos no integrados."
            solution = solution_value or "Liseth / JARVIS Core: Un sistema operativo ejecutivo autónomo que fusiona control del PC, finanzas cuantitativas, ciberseguridad y Google Workspace."
            tam = "$3.2 Billones COP (Gasto en software empresarial y productividad Colombia)"
            sam = "$420.000 Millones COP (Directivos, firmas y PYMEs de servicios de alto valor)"
            som = "$28.000 Millones COP (Penetración inicial primer bienio)"
            monetization = "Suscripciones mensuales recurrentes (SaaS B2B), licencias corporativas Stark Enterprise e integraciones API."
            magic = "Arquitectura modular multimodal con reconocimiento de voz, emulación de terminales NFC y cifrado de alta entropía."

        slides = [
            {
                "slide_number": 1,
                "title": b_name.upper(),
                "subtitle": tagline,
                "key_takeaway": f"Fundador & CEO: {founder_name} | {city}",
                "bullets": [
                    f"Presentación para Inversionistas y Comités Estratégicos",
                    f"Ronda de Financiamiento: Semilla / Expansión",
                    f"Sede de Desarrollo: {city}"
                ],
                "graphic_type": "hero_cover"
            },
            {
                "slide_number": 2,
                "title": "El Gran Problema de Mercado",
                "subtitle": "¿Qué ineficiencia crítica estamos resolviendo hoy?",
                "key_takeaway": "Dolor real, medible y no resuelto por soluciones tradicionales.",
                "bullets": [
                    problem,
                    "Pérdida de márgenes de beneficio por procesos obsoletos y lentos.",
                    "Falta de trazabilidad y gobernanza de datos en tiempo real.",
                    "Frustración creciente entre los tomadores de decisiones."
                ],
                "graphic_type": "problem_pain_points"
            },
            {
                "slide_number": 3,
                "title": "La Solución & Propuesta de Valor",
                "subtitle": "Transformando el dolor del cliente en una ventaja exponencial",
                "key_takeaway": "Eficiencia 10x frente a cualquier alternativa del mercado.",
                "bullets": [
                    solution,
                    "Ahorro de hasta un 65% en tiempos de respuesta operativa.",
                    "Garantía de precisión matemática, cumplimiento normativo y legal.",
                    "Experiencia de usuario de última generación (holográfica e intuitiva)."
                ],
                "graphic_type": "solution_benefits"
            },
            {
                "slide_number": 4,
                "title": "La Magia Subyacente / Tecnología",
                "subtitle": "Nuestra barrera de entrada y propiedad intelectual",
                "key_takeaway": "Ventaja tecnológica propietaria protegida por know-how.",
                "bullets": [
                    magic,
                    "Infraestructura nativa asíncrona de alto rendimiento y cero latencia.",
                    "Algoritmos propietarios adaptados a la realidad regulatoria y económica.",
                    "Bóveda de ciberseguridad integrada con entropía criptográfica."
                ],
                "graphic_type": "tech_architecture"
            },
            {
                "slide_number": 5,
                "title": "Modelo de Negocio & Monetización",
                "subtitle": "¿Cómo generamos ingresos sostenibles y recurrentes?",
                "key_takeaway": "Estructura de ingresos predecible con márgenes brutos > 75%.",
                "bullets": [
                    monetization,
                    "Ingresos recurrentes mensuales (MRR) con retención superior al 92%.",
                    "Estrategia de expansión de cuentas (Up-selling y Cross-selling).",
                    "Costos marginales de adquisición decrecientes por efecto de red."
                ],
                "graphic_type": "revenue_streams"
            },
            {
                "slide_number": 6,
                "title": "Tamaño del Mercado (TAM - SAM - SOM)",
                "subtitle": "Un mercado masivo con espacio para un nuevo líder",
                "key_takeaway": f"SOM proyectado de {som} en 24 meses.",
                "bullets": [
                    f"TAM (Total Addressable Market): {tam}",
                    f"SAM (Serviceable Available Market): {sam}",
                    f"SOM (Serviceable Obtainable Market): {som}",
                    "Tasa de crecimiento anual compuesta (CAGR) del sector: 14.8%"
                ],
                "graphic_type": "tam_sam_som_funnel"
            },
            {
                "slide_number": 7,
                "title": "Estrategia Go-to-Market & Canales",
                "subtitle": "Cómo adquirimos clientes al menor costo posible (CAC)",
                "key_takeaway": "Relación LTV / CAC proyectada superior a 4.5x.",
                "bullets": [
                    "Alianzas directas con cámaras de comercio y gremios sectoriales.",
                    "Canal directo B2B para cuentas corporativas clave (Outbound consultivo).",
                    "Inbound Marketing técnico y casos de éxito cuantificables.",
                    "Pilotos de rápida adopción con garantía de retorno sobre inversión en 30 días."
                ],
                "graphic_type": "gtm_pipeline"
            },
            {
                "slide_number": 8,
                "title": "Panorama Competitivo & Foso Defensivo",
                "subtitle": "¿Por qué ganamos frente a los operadores establecidos?",
                "key_takeaway": "Foso defensivo basado en costos, agilidad y tecnología local.",
                "bullets": [
                    "Soluciones tradicionales: Lentas, costosas de implementar y rígidas.",
                    "Nosotros: Implementación en minutos, adaptabilidad normativa local y UI táctica.",
                    "Efecto de red acumulativo de datos y confianza empresarial.",
                    "Barreras de salida elevadas por integración profunda en el flujo de trabajo."
                ],
                "graphic_type": "competition_matrix"
            },
            {
                "slide_number": 9,
                "title": "Equipo Directivo & Asesores",
                "subtitle": "Liderazgo multidisciplinario con capacidad de ejecución",
                "key_takeaway": "Combinación óptima de visión directiva, rigor cuantitativo y tecnología.",
                "bullets": [
                    f"{founder_name} - Fundador & CEO (Estrategia, Finanzas y Dirección)",
                    "Equipo de Ingeniería & Arquitectura de Software de Vanguardia",
                    "Consejo Asesor Académico y Comercial (Egresados UNAL & Empresarios)",
                    "Track record de disciplina técnica, entrega ágil y rigor ético."
                ],
                "graphic_type": "team_cards"
            },
            {
                "slide_number": 10,
                "title": "Proyecciones Financieras & La Solicitud (Ask)",
                "subtitle": "Destino del capital y retorno estimado para inversionistas",
                "key_takeaway": f"Buscamos ${funding_ask:,.2f} {currency} para acelerar el crecimiento.",
                "bullets": [
                    f"Monto de la Ronda: ${funding_ask:,.2f} {currency}",
                    "Distribución del Capital: 50% Expansión Comercial, 35% Desarrollo Tecnológico, 15% Capital de Trabajo",
                    "Punto de Equilibrio (Break-even): Mes 14 de operaciones",
                    "Múltiplo de Salida / Retorno Esperado: 3.5x a 5.0x en horizonte de 5 años"
                ],
                "graphic_type": "financial_ask_pie"
            }
        ]

        return {
            "business_name": b_name,
            "industry": ind,
            "tagline": tagline,
            "funding_ask": funding_ask,
            "currency": currency,
            "founder": founder_name,
            "city": city,
            "total_slides": len(slides),
            "slides": slides
        }

    def format_markdown(self, deck: Dict[str, Any]) -> str:
        lines = [
            f"# 🎯 PITCH DECK EJECUTIVO: {deck['business_name'].upper()}",
            f"**Sector**: `{deck['industry'].upper()}` | **Solicitud de Capital**: `${deck['funding_ask']:,.2f} {deck['currency']}`",
            f"**Líder del Proyecto**: `{deck['founder']}` | **Ubicación**: `{deck['city']}`",
            "",
            "---"
        ]

        for s in deck["slides"]:
            lines.append(f"\n## Diapositiva {s['slide_number']}: {s['title']}")
            lines.append(f"*{s['subtitle']}*\n")
            for b in s["bullets"]:
                lines.append(f"- {b}")
            lines.append(f"\n> 💡 **Conclusión Clave**: {s['key_takeaway']}\n")
            lines.append("---")

        return "\n".join(lines)


pitch_generator_service = PitchGeneratorService()
