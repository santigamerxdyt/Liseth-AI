"""
Workspace Automation & Office Productivity Service for JARVIS / Liseth.
Generates complex spreadsheet formulas (Excel & Google Sheets),
academic & consulting report blueprints, and executive presentation outlines for Señor Santiago.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvis.workspace_automation")


class WorkspaceAutomationService:
    """
    Office Productivity and Advanced Document Architecture Engine.
    Equips Liseth to solve complex spreadsheet requirements and structure university/consulting deliverables.
    """

    def get_status(self) -> Dict[str, Any]:
        """Returns the operational status of the workspace automation engine."""
        return {
            "engine": "Workspace Automation & Productivity Suite (v1.0)",
            "supported_tools": ["Excel (Español/Inglés)", "Google Sheets", "PowerPoint / Slides", "Word / Docs"],
            "modules": [
                "Generador Bilingüe de Fórmulas Avanzadas (BUSCARX, INDICE/COINCIDIR, Matrices Dinámicas)",
                "Arquitectura y Esquemas para Ensayos Académicos e Informes de Consultoría",
                "Estructurador de Diapositivas Ejecutivas con Notas de Orador"
            ],
            "status": "ONLINE"
        }

    def format_status_report(self, st: Dict[str, Any]) -> str:
        """Formats the status report for Señor Santiago."""
        mods = "\n".join([f"  - {m}" for m in st.get("modules", [])])
        return (
            "### 📑 Motor de Automatización Ofimática y Productividad (Workspace Automation)\n"
            f"- **Suite**: `{st.get('engine')}`\n"
            f"- **Herramientas**: {', '.join(st.get('supported_tools', []))}\n"
            f"- **Módulos Disponibles**:\n{mods}\n\n"
            "Listo para construir fórmulas de hojas de cálculo, estructurar informes de consultoría y diseñar presentaciones, señor Santiago."
        )

    def generate_excel_formula(self, query: str) -> str:
        """
        Generates bilingual formulas and step-by-step guidance for Excel and Google Sheets.
        """
        q = query.lower().strip()

        if any(w in q for w in ["buscar", "cruce", "vlookup", "xlookup", "buscarx", "coincidir"]):
            formula_es = '=BUSCARX(A2; Clientes!A:A; Clientes!B:E; "No encontrado"; 0)'
            formula_en = '=XLOOKUP(A2, Customers!A:A, Customers!B:E, "Not found", 0)'
            alt_es = '=INDICE(Clientes!B:B; COINCIDIR(1; (Clientes!A:A=A2)*(Clientes!C:C="Activo"); 0))'
            alt_en = '=INDEX(Customers!B:B, MATCH(1, (Customers!A:A=A2)*(Customers!C:C="Active"), 0))'
            title = "Búsqueda Bidireccional y Cruce de Tablas"
            explanation = (
                "`BUSCARX` supera al clásico `BUSCARV`: busca a la izquierda o derecha, no se rompe al insertar columnas "
                "y devuelve múltiples columnas contiguas en una sola fórmula matricial."
            )

        elif any(w in q for w in ["sumar", "condicion", "criterio", "sumifs"]):
            formula_es = '=SUMAR.SI.CONJUNTO(Ventas!D:D; Ventas!B:B; ">=01/01/2026"; Ventas!C:C; "Santiago")'
            formula_en = '=SUMIFS(Sales!D:D, Sales!B:B, ">=01/01/2026", Sales!C:C, "Santiago")'
            alt_es = '=SUMAPRODUCTO((Ventas!B:B>=FECHA(2026;1;1))*(Ventas!C:C="Santiago")*(Ventas!D:D))'
            alt_en = '=SUMPRODUCT((Sales!B:B>=DATE(2026,1,1))*(Sales!C:C="Santiago")*(Sales!D:D))'
            title = "Suma Multicriterio con Múltiples Condiciones"
            explanation = "Permite sumar valores numéricos cuando se cumplen simultáneamente dos o más condiciones de fecha, texto o categoría."

        elif any(w in q for w in ["filtrar", "unicos", "dinamica", "ordenar"]):
            formula_es = '=ORDENAR(UNICOS(FILTRAR(Ventas!A2:C100; Ventas!C2:C100>5000; "Sin ventas")); 1; 1)'
            formula_en = '=SORT(UNIQUE(FILTER(Sales!A2:C100, Sales!C2:C100>5000, "No sales")), 1, 1)'
            alt_es = '=QUERY(Ventas!A2:C; "SELECT A, B, C WHERE C > 5000 ORDER BY A ASC")'
            alt_en = '=QUERY(Sales!A2:C, "SELECT A, B, C WHERE C > 5000 ORDER BY A ASC")'
            title = "Extracción y Filtrado con Matrices Dinámicas"
            explanation = "Fórmula matricial que extrae registros únicos que superan el umbral establecido y los entrega ordenados automáticamente."

        elif any(w in q for w in ["cuota", "prestamo", "pago", "tasa"]):
            formula_es = '=PAGO(18%/12; 36; -50000000)'
            formula_en = '=PMT(18%/12, 36, -50000000)'
            alt_es = '=PAGOPRIN(18%/12; 1; 36; -50000000) + PAGOINT(18%/12; 1; 36; -50000000)'
            alt_en = '=PPMT(18%/12, 1, 36, -50000000) + IPMT(18%/12, 1, 36, -50000000)'
            title = "Cálculo de Cuota Financiera Mensual (Amortización)"
            explanation = "Calcula la cuota mensual fija para un crédito de $50,000,000 a una tasa anual del 18% diferido a 36 meses."

        else:
            formula_es = '=SI.ERROR(BUSCARX(A2; Datos!A:A; Datos!B:B); "Revisar")'
            formula_en = '=IFERROR(XLOOKUP(A2, Data!A:A, Data!B:B), "Check")'
            alt_es = '=INDICE(Datos!B:B; COINCIDIR(A2; Datos!A:A; 0))'
            alt_en = '=INDEX(Data!B:B, MATCH(A2, Data!A:A, 0))'
            title = "Fórmula Paramétrica de Consulta"
            explanation = "Permite consultar valores relacionados con control automático de errores."

        lines = [
            f"### 📊 Solución de Hoja de Cálculo: *{title}*",
            f"**Requerimiento**: {query}\n",
            "#### 1. Fórmulas Listas para Usar",
            f"- **Excel en Español / Google Sheets (Separador punto y coma `;`)**:",
            f"  ```excel\n  {formula_es}\n  ```",
            f"- **Excel en Inglés (Separador coma `,`)**:",
            f"  ```excel\n  {formula_en}\n  ```\n",
            "#### 2. Alternativa Avanzada (Matricial / Doble Criterio)",
            f"- **En Español**: `{alt_es}`",
            f"- **En Inglés**: `{alt_en}`\n",
            f"#### 3. Explicación Técnica y Buenas Prácticas",
            f"{explanation}",
            "- **Tip para Santiago**: En Excel recuerde que si su configuración regional usa coma decimal (`1,5`), el separador de argumentos de fórmula es `;`. Si usa punto decimal (`1.5`), el separador es `,`."
        ]
        return "\n".join(lines)

    def generate_report_blueprint(self, title: str, doc_type: str = "consultoria") -> str:
        """
        Generates structured blueprints for consulting reports or university essays.
        """
        t = title.strip() or "Diagnóstico Estratégico Organizacional"
        dtype = doc_type.lower().strip()

        if "ensayo" in dtype or "academico" in dtype:
            lines = [
                f"### 🎓 Esquema Estructural para Ensayo Académico: *{t}*",
                f"**Estándar**: Normas APA 7.ª Edición | **Tono**: Riguroso, Argumentativo y Analítico\n",
                "#### 1. Introducción (Aprox. 15% del total)",
                "- **Gancho inicial**: Planteamiento de una paradoja o cifra impactante de la industria.",
                "- **Contextualización**: Definición del problema en el escenario económico actual.",
                "- **Tesis central**: Afirmación contundente que será defendida a lo largo del texto.",
                "- **Hoja de ruta**: Mención breve de los tres ejes temáticos que se abordarán.\n",
                "#### 2. Cuerpo Argumentativo (Aprox. 70% del total)",
                "- **Argumento 1 (Fundamento Teórico)**: Respaldado con citas de literatura científica indexada.",
                "- **Argumento 2 (Evidencia Cuantitativa)**: Datos empíricos, métricas financieras y casos de estudio reales.",
                "- **Contraargumento y Refutación**: Exposición de una postura contraria y su desarticulación mediante evidencia objetiva.\n",
                "#### 3. Conclusiones y Discusión (Aprox. 15% del total)",
                "- **Reafirmación de la tesis**: Síntesis de hallazgos sin repetir palabras literales.",
                "- **Implicaciones para la Administración**: Aportes prácticos para la toma de decisiones.",
                "- **Vacíos futuros**: Líneas abiertas de investigación para profundizar."
            ]
        else:
            lines = [
                f"### 💼 Estructura de Informe de Consultoría Gerencial: *{t}*",
                f"**Destinatario**: Junta Directiva / Alta Dirección | **Tono**: Ejecutivo, Orientado a Resultados\n",
                "#### 1. Resumen Ejecutivo (Executive Summary)",
                "- Diagnóstico central en 3 viñetas concisas.",
                "- Impacto financiero proyectado e inversión requerida.",
                "- Decisión recomendada inmediata.\n",
                "#### 2. Diagnóstico del Estado Actual (As-Is)",
                "- Cuello de botella identificado y análisis de causa raíz.",
                "- Métricas actuales: Costo, tiempo de ciclo y margen de pérdida.\n",
                "#### 3. Propuesta de Solución Estratégica (To-Be)",
                "- Arquitectura de la solución en 3 fases de implementación.",
                "- Plan de gestión del cambio y mitigación de riesgos operativos.\n",
                "#### 4. Evaluación Financiera y Retorno (ROI)",
                "- Presupuesto de inversión inicial (CAPEX) y costos operativos (OPEX).",
                "- Plazo de recuperación de la inversión (Payback) y Valor Presente Neto (VAN).\n",
                "#### 5. Plan de Acción Inmediato (Primeros 30-60-90 Días)",
                "- Hitos críticos, responsables de entrega y matriz de seguimiento."
            ]

        return "\n".join(lines)

    def generate_presentation_deck(self, topic: str, slide_count: int = 5) -> str:
        """
        Creates an executive slide presentation blueprint with speaker notes.
        """
        top = topic.strip() or "Plan Estratégico de Transformación"
        lines = [
            f"### 🖥️ Estructura de Presentación Ejecutiva: *{top}*",
            f"**Total de Diapositivas**: `{slide_count}` | **Diseño**: Minimalista, Visual, Alto Impacto\n"
        ]

        deck_slides = [
            ("1. Portada e Impacto Inicial", "Título contundente, subtítulo descriptivo, nombre de Santiago y fecha.", "Abrir con energía, agradecer la atención y fijar la expectativa en una sola frase memorable."),
            ("2. El Desafío / La Oportunidad de Mercado", "Gráfico comparativo o métrica clave que evidencie el dolor o la oportunidad.", "Conectar con la audiencia explicando por qué este problema cuesta dinero o tiempo cada día."),
            ("3. Nuestra Solución Estratégica", "Diagrama de 3 pilares conceptuales con beneficios directos.", "Explicar el 'cómo': simplificar la solución para que sea obvia y atractiva."),
            ("4. Viabilidad Financiera y Métricas Clave", "Tabla compacta con ROI proyectado, Costo de Adquisición y Margen Neto.", "Demostrar que los números están respaldados con supuestos conservadores y sostenibles."),
            ("5. Hoja de Ruta y Próximos Pasos (Llamado a la Acción)", "Cronograma visual en 3 fases (Lanzamiento, Expansión, Consolidación).", "Cerrar con la decisión concreta que se requiere hoy para poner el plan en marcha.")
        ]

        for num, (title, content, notes) in enumerate(deck_slides[:slide_count], start=1):
            lines.append(f"#### Diapositiva {num}: **{title}**")
            lines.append(f"- **Contenido Visual Recomendado**: {content}")
            lines.append(f"- **Notas para el Orador (Speaker Notes)**: *\"{notes}\"*\n")

        return "\n".join(lines)


# Global Singleton
workspace_automation_service = WorkspaceAutomationService()
