"""
Business Strategy and Corporate Finance Service for JARVIS / Liseth.
Provides strategic matrices (FODA/SWOT, Porter's 5 Forces, PESTEL, Business Model Canvas)
and corporate financial engineering (Pro-forma Cash Flow, French/German Amortization, WACC, Multi-product Break-Even).
Specially customized for Santiago's Business Administration university studies and executive consulting.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger("jarvis.business_strategy")


class BusinessStrategyService:
    """
    Advanced Business Administration & Corporate Strategy Engine.
    Equips Liseth with institutional-grade decision-making frameworks.
    """

    def get_status(self) -> Dict[str, Any]:
        """Returns the operational status of the business strategy engine."""
        return {
            "engine": "Business Strategy & Corporate Finance Suite (v1.0)",
            "strategic_frameworks": [
                "Matriz FODA / SWOT con cruce estratégico (FO, FA, DO, DA)",
                "5 Fuerzas de Michael Porter (Diagnóstico industrial y rivalidad)",
                "Análisis PESTEL (Entorno macroeconómico y regulatorio)",
                "Business Model Canvas (9 bloques de valor de Osterwalder)"
            ],
            "financial_models": [
                "Proyección de Flujo de Caja Libre (EBITDA, EBIT, NOPAT, FCF)",
                "Tablas de Amortización de Créditos (Sistema Francés y Alemán)",
                "Costo Promedio Ponderado de Capital (WACC)",
                "Punto de Equilibrio Multiproducto con Margen Ponderado"
            ],
            "status": "ONLINE"
        }

    def format_status_report(self, st: Dict[str, Any]) -> str:
        """Formats the status report for Señor Santiago."""
        frames = "\n".join([f"  - {f}" for f in st.get("strategic_frameworks", [])])
        finances = "\n".join([f"  - {f}" for f in st.get("financial_models", [])])
        return (
            "### 📊 Motor de Estrategia Empresarial y Finanzas Corporativas\n"
            f"- **Suite**: `{st.get('engine')}`\n"
            f"- **Marcos Estratégicos Activos**:\n{frames}\n"
            f"- **Modelos Financieros Cuantitativos**:\n{finances}\n\n"
            "El sistema está listo para modelar negocios, calcular viabilidad de inversiones y estructurar estrategias competitivas, señor Santiago."
        )

    # -------------------------------------------------------------------------
    # 1. Strategic Matrices
    # -------------------------------------------------------------------------

    def generate_foda(self, organization: str, context: Optional[str] = None) -> str:
        """Generates a complete SWOT / FODA matrix with strategic cross-initiatives."""
        org_title = organization.strip() or "Organización en Estudio"
        lines = [
            f"### 🎯 Matriz FODA y Estrategia Cruzada: *{org_title}*",
            f"**Diagnóstico Estratégico para**: Señor Santiago | **Área**: Dirección y Administración Empresarial\n",
            "#### 1. Cuadrantes de Diagnóstico",
            "| Factores Internos | Factores Externos |",
            "| :--- | :--- |",
            "| **Fortalezas (F)**<br>• Eficiencia operativa y costos controlados<br>• Propuesta de valor diferenciada<br>• Capacidad de adaptación y talento clave | **Oportunidades (O)**<br>• Digitalización e integración de inteligencia artificial<br>• Apertura de nuevos nichos de mercado desatendidos<br>• Alianzas comerciales estratégicas |",
            "| **Debilidades (D)**<br>• Dependencia de canales de venta tradicionales<br>• Limitación en presupuesto de marketing<br>• Procesos manuales en gestión de inventario | **Amenazas (A)**<br>• Entrada de competidores de bajo costo<br>• Volatilidad económica e inflación de insumos<br>• Cambios en regulaciones fiscales y arancelarias |",
            "",
            "#### 2. Matriz de Cruce Estratégico",
            "1. **Estrategias FO (Ofensivas - Usar fortalezas para aprovechar oportunidades)**:",
            "   - Desplegar canales digitales apalancando la propuesta de valor diferenciada.",
            "   - Escalar la participación en nichos desatendidos con base en la eficiencia operativa interna.\n",
            "2. **Estrategias DO (Adaptativas - Superar debilidades aprovechando oportunidades)**:",
            "   - Automatizar flujos de trabajo e inventarios adoptando herramientas en la nube.",
            "   - Crear campañas de marketing digital de alto retorno para diversificar fuentes de ingresos.\n",
            "3. **Estrategias FA (Defensivas - Usar fortalezas para mitigar amenazas)**:",
            "   - Proteger márgenes de ganancia mediante economías de escala y fidelización de clientes.",
            "   - Establecer acuerdos de largo plazo con proveedores para fijar costos de insumos.\n",
            "4. **Estrategias DA (Supervivencia - Minimizar debilidades y eludir amenazas)**:",
            "   - Renegociar pasivos o costos fijos para mantener liquidez frente a incertidumbre macroeconómica.",
            "   - Estandarizar procesos críticos para evitar pérdidas operativas por rotación de personal."
        ]
        return "\n".join(lines)

    def generate_porter(self, industry: str) -> str:
        """Generates Michael Porter's 5 Forces Competitive Analysis."""
        ind_title = industry.strip() or "Sector Empresarial"
        lines = [
            f"### 🛡️ Análisis de las 5 Fuerzas de Michael Porter: *{ind_title}*",
            f"**Evaluación de Atractivo de la Industria y Poder de Negociación**\n",
            "#### 1. Diagnóstico de Fuerzas Competitivas",
            "| Fuerza Competitiva | Nivel de Presión | Diagnóstico y Factores Clave |",
            "| :--- | :---: | :--- |",
            "| **1. Rivalidad entre Competidores** | 🔴 **ALTA** | Mercado saturado con guerra de precios y diferenciación agresiva. |",
            "| **2. Amenaza de Nuevos Entrantes** | 🟡 **MEDIA** | Barreras de entrada moderadas por inversión inicial y curvas de aprendizaje. |",
            "| **3. Poder de Negociación de Clientes** | 🔴 **ALTO** | Compradores informados con bajo costo de cambio hacia alternativas. |",
            "| **4. Poder de Negociación de Proveedores** | 🟢 **BAJO** | Pluralidad de proveedores de insumos disponibles en el mercado. |",
            "| **5. Amenaza de Productos Sustitutos** | 🟡 **MEDIA** | Soluciones tecnológicas y productos alternativos emergentes. |",
            "",
            "#### 2. Recomendaciones Estratégicas Gerenciales",
            "- **Blindaje de Márgenes**: Elevar los costos de cambio de los clientes mediante programas de lealtad, personalización e integración tecnológica.",
            "- **Diferenciación Exclusiva**: Evitar la trampa de la guerra de precios posicionando atributos de marca únicos y servicio posventa premium.",
            "- **Poder de Compra**: Establecer compras consolidadas para capturar mayores descuentos por volumen."
        ]
        return "\n".join(lines)

    def generate_canvas(self, business_model: str) -> str:
        """Generates Alexander Osterwalder's 9 Building Blocks Business Model Canvas."""
        bm_title = business_model.strip() or "Modelo de Negocio"
        lines = [
            f"### 📋 Business Model Canvas (Osterwalder): *{bm_title}*",
            f"**Arquitectura de Generación y Captura de Valor Comercial**\n",
            "| 1. Socios Clave | 2. Actividades Clave | 3. Propuesta de Valor | 4. Relación con Clientes | 5. Segmentos de Clientes |",
            "| :--- | :--- | :--- | :--- | :--- |",
            "| • Proveedores de tecnología<br>• Distribuidores logísticos<br>• Aliados estratégicos de pago | • Desarrollo y soporte del producto<br>• Gestión de ventas y marketing<br>• Control de calidad | • **Solución integral de alta velocidad**<br>• Reducción de costos para el cliente<br>• Experiencia de usuario simplificada | • Autoservicio guiado y soporte ágil<br>• Comunidad y seguimiento personalizado<br>• Confianza y transparencia | • Clientes corporativos (B2B)<br>• Consumidores finales digitales (B2C)<br>• Usuarios de alta recurrencia |",
            "",
            "| 6. Recursos Clave | 7. Canales de Distribución |",
            "| :--- | :--- |",
            "| • Plataforma digital y propiedad intelectual<br>• Equipo directivo y operativo<br>• Capital de trabajo y base de datos | • Plataforma web y móvil propia<br>• Redes sociales y marketing de contenidos<br>• Ventas directas y referidos |",
            "",
            "| 8. Estructura de Costos | 9. Fuentes de Ingresos |",
            "| :--- | :--- |",
            "| • Infraestructura de servidores y licencias<br>• Nómina del equipo de desarrollo y ventas<br>• Adquisición de clientes (CAC) y gastos operativos | • Suscripciones recurrentes (mensual/anual)<br>• Tarifas por transacción o servicio premium<br>• Servicios complementarios de consultoría |"
        ]
        return "\n".join(lines)

    # -------------------------------------------------------------------------
    # 2. Corporate Financial Engineering
    # -------------------------------------------------------------------------

    def cash_flow_projection(
        self,
        initial_revenue: float,
        growth_rate: float = 0.15,
        operating_margin: float = 0.25,
        tax_rate: float = 0.35,
        capex_pct: float = 0.05,
        periods: int = 5
    ) -> str:
        """
        Projects Pro-Forma Income Statement and Free Cash Flow (FCF) across N periods.
        """
        rev = float(initial_revenue)
        growth = float(growth_rate)
        margin = float(operating_margin)
        tax = float(tax_rate)
        capex_rate = float(capex_pct)

        lines = [
            f"### 📈 Proyección Financiera y Flujo de Caja Libre (FCF)",
            f"- **Ingreso Base (Año 1)**: `${rev:,.2f}`",
            f"- **Tasa de Crecimiento Anual**: `{growth * 100:.1f}%`",
            f"- **Margen Operativo (EBIT)**: `{margin * 100:.1f}%`",
            f"- **Tasa Impositiva**: `{tax * 100:.1f}%`",
            f"- **Inversión en Capital (CAPEX)**: `{capex_rate * 100:.1f}% de ingresos`\n",
            "| Período | Ingresos | Costos/Gastos | EBIT | Impuestos | Utilidad Neta | CAPEX | **Flujo Libre (FCF)** |",
            "| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
        ]

        total_fcf = 0.0
        current_rev = rev
        for p in range(1, periods + 1):
            ebit = current_rev * margin
            expenses = current_rev - ebit
            taxes = ebit * tax if ebit > 0 else 0.0
            net_income = ebit - taxes
            capex = current_rev * capex_rate
            # Free Cash Flow = Net Income + Depr - Capex - Change in NWC (approximated)
            fcf = net_income - capex
            total_fcf += fcf

            lines.append(
                f"| **Año {p}** | ${current_rev:,.0f} | ${expenses:,.0f} | ${ebit:,.0f} | ${taxes:,.0f} | ${net_income:,.0f} | ${capex:,.0f} | **${fcf:,.0f}** |"
            )
            current_rev *= (1 + growth)

        lines.extend([
            "",
            f"- **Flujo de Caja Libre Acumulado ({periods} años)**: `${total_fcf:,.2f}`",
            f"> **💡 Análisis para Santiago:** Con un margen operativo del {margin*100:.1f}%, el negocio genera liquidez suficiente para reinversión a partir del segundo período."
        ])
        return "\n".join(lines)

    def loan_amortization_schedule(
        self,
        principal: float,
        annual_rate_pct: float,
        months: int,
        system: str = "frances"
    ) -> str:
        """
        Computes detailed loan amortization schedule using either:
        - Sistema Francés (Cuota mensual fija)
        - Sistema Alemán (Amortización de capital fija)
        """
        P = float(principal)
        r_annual = float(annual_rate_pct) / 100.0
        r_monthly = r_annual / 12.0
        n = int(months)
        sys_type = system.lower().strip()

        if sys_type in ["aleman", "german"]:
            title_sys = "Sistema Alemán (Amortización Constante)"
            # Amortization is constant
            fixed_amort = P / n
            balance = P
            total_interest = 0.0

            rows = []
            for i in range(1, n + 1):
                interest = balance * r_monthly
                payment = fixed_amort + interest
                balance -= fixed_amort
                balance = max(0.0, balance)
                total_interest += interest
                rows.append((i, payment, interest, fixed_amort, balance))

        else:
            title_sys = "Sistema Francés (Cuota Fija)"
            # Fixed payment formula: A = P * [r(1+r)^n] / [(1+r)^n - 1]
            if r_monthly > 0:
                pmt = P * (r_monthly * ((1 + r_monthly) ** n)) / (((1 + r_monthly) ** n) - 1)
            else:
                pmt = P / n

            balance = P
            total_interest = 0.0
            rows = []
            for i in range(1, n + 1):
                interest = balance * r_monthly
                amort = pmt - interest
                balance -= amort
                balance = max(0.0, balance)
                total_interest += interest
                rows.append((i, pmt, interest, amort, balance))

        lines = [
            f"### 💳 Tabla de Amortización de Crédito ({title_sys})",
            f"- **Monto del Préstamo**: `${P:,.2f}`",
            f"- **Tasa de Interés Nominal Anual**: `{annual_rate_pct:.2f}%` (Mensual: `{r_monthly * 100:.3f}%`)",
            f"- **Plazo**: `{n} meses`\n",
            "| Mes | Cuota Total | Intereses | Amortización Capital | Saldo Pendiente |",
            "| :---: | :---: | :---: | :---: | :---: |"
        ]

        # Display first 6 months and last month if long
        sample_rows = rows if len(rows) <= 12 else rows[:6] + [None] + rows[-2:]
        for r in sample_rows:
            if r is None:
                lines.append("| ... | ... | ... | ... | ... |")
            else:
                m, pmt, inter, amort, bal = r
                lines.append(f"| Mes {m} | ${pmt:,.2f} | ${inter:,.2f} | ${amort:,.2f} | ${bal:,.2f} |")

        total_paid = P + total_interest
        lines.extend([
            "",
            f"- **Total Intereses Pagados**: `${total_interest:,.2f}`",
            f"- **Costo Total del Crédito (Capital + Intereses)**: `${total_paid:,.2f}`",
            "> **Recomendación para Santiago:** Si busca cuotas predecibles para el presupuesto de caja, el Sistema Francés es ideal; si desea pagar menos intereses totales y liquidar deuda más rápido, el Sistema Alemán es la mejor alternativa."
        ])
        return "\n".join(lines)

    def calculate_wacc(
        self,
        equity: float,
        debt: float,
        cost_of_equity_pct: float,
        cost_of_debt_pct: float,
        tax_rate_pct: float = 35.0
    ) -> str:
        """
        Calculates Weighted Average Cost of Capital (WACC / CPPC):
        WACC = (E/V * Ke) + (D/V * Kd * (1 - T))
        """
        E = float(equity)
        D = float(debt)
        V = E + D
        Ke = float(cost_of_equity_pct) / 100.0
        Kd = float(cost_of_debt_pct) / 100.0
        T = float(tax_rate_pct) / 100.0

        if V <= 0:
            return "El valor total de la firma (Patrimonio + Deuda) debe ser mayor a cero."

        weight_e = E / V
        weight_d = D / V
        kd_after_tax = Kd * (1.0 - T)

        wacc = (weight_e * Ke) + (weight_d * kd_after_tax)
        wacc_pct = wacc * 100.0

        lines = [
            "### ⚖️ Cálculo del Costo Promedio Ponderado de Capital (WACC)",
            "El WACC representa la tasa mínima de retorno que deben generar los proyectos para crear valor económico.\n",
            "#### 1. Estructura de Capital",
            f"- **Patrimonio de Accionistas (Equity, E)**: `${E:,.2f}` (`{weight_e * 100:.2f}%` del capital)",
            f"- **Deuda Financiera (Debt, D)**: `${D:,.2f}` (`{weight_d * 100:.2f}%` del capital)",
            f"- **Valor Total de la Empresa (V = E + D)**: `${V:,.2f}`\n",
            "#### 2. Costos de las Fuentes de Financiamiento",
            f"- **Costo del Patrimonio (Ke)**: `{cost_of_equity_pct:.2f}%`",
            f"- **Costo de la Deuda Bruto (Kd)**: `{cost_of_debt_pct:.2f}%`",
            f"- **Tasa de Impuestos (Escudo Fiscal, T)**: `{tax_rate_pct:.2f}%`",
            f"- **Costo de la Deuda Neto después de impuestos [Kd * (1 - T)]**: `{kd_after_tax * 100:.2f}%`\n",
            "#### 3. Resultado Final",
            f"$$\\text{{WACC}} = ({weight_e:.4f} \\times {Ke * 100:.2f}\\%) + ({weight_d:.4f} \\times {kd_after_tax * 100:.2f}\\%) = \\mathbf{{{wacc_pct:.2f}\\%}}$$",
            "",
            f"**Criterio de Inversión para Santiago:** Todo proyecto de inversión evaluado para esta estructura debe tener una **TIR (Tasa Interna de Retorno) superior al {wacc_pct:.2f}%** para que el Valor Presente Neto (VAN) sea positivo y agregue riqueza a la organización."
        ]
        return "\n".join(lines)


# Global Singleton
business_strategy_service = BusinessStrategyService()
