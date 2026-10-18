"""
Academic & University Assistance Engine for JARVIS / Liseth.
Tailored for Señor Santiago's university coursework and research:
- APA 7th Edition Citation & Reference Generator (Book, Journal Article, Website, Thesis)
- Academic Paper / Essay / Executive Report Structure Generator
- Academic Formatting Standards (APA 7 guidelines, margins, typography, heading hierarchy)
- Plagiarism Prevention & Methodology Guidance
"""
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("jarvis.academic_helper")


def generate_apa_citation(
    source_type: str = "book",
    authors: str = "",
    year: str = "",
    title: str = "",
    publisher: str = "",
    journal: str = "",
    volume: str = "",
    issue: str = "",
    pages: str = "",
    url: str = "",
    doi: str = ""
) -> Dict[str, str]:
    """
    Generates exact APA 7th Edition in-text citation and bibliographic reference.
    """
    source = source_type.lower().strip()
    authors = authors.strip() or "Autor Desconocido"
    year = str(year).strip() or "s. f."
    title = title.strip() or "Título de la obra"

    # Extract primary surname for in-text citation
    first_author_surname = authors.split(",")[0].strip() if "," in authors else authors.split()[-1] if authors else "Autor"
    if " y " in authors.lower() or "&" in authors:
        in_text_parenthetical = f"({first_author_surname} et al., {year})"
        in_text_narrative = f"{first_author_surname} et al. ({year})"
    else:
        in_text_parenthetical = f"({first_author_surname}, {year})"
        in_text_narrative = f"{first_author_surname} ({year})"

    reference = ""
    if source in ("journal", "articulo", "revista", "paper"):
        vol_str = f", *{volume}*" if volume else ""
        iss_str = f"({issue})" if issue else ""
        pg_str = f", {pages}" if pages else ""
        doi_url = f" https://doi.org/{doi.strip()}" if doi else (f" {url.strip()}" if url else "")
        reference = f"{authors} ({year}). {title}. *{journal or 'Nombre de la Revista'}*{vol_str}{iss_str}{pg_str}.{doi_url}".strip()

    elif source in ("web", "website", "pagina", "sitio"):
        site = publisher or "Nombre del Sitio Web"
        url_str = f" {url.strip()}" if url else ""
        reference = f"{authors} ({year}). *{title}*. {site}.{url_str}".strip()

    elif source in ("thesis", "tesis", "grado"):
        inst = publisher or "Universidad"
        url_str = f" {url.strip()}" if url else ""
        reference = f"{authors} ({year}). *{title}* [Tesis de pregrado/maestría, {inst}]. Repositorio Institucional.{url_str}".strip()

    else:  # book / libro default
        pub = publisher or "Editorial"
        doi_url = f" https://doi.org/{doi.strip()}" if doi else (f" {url.strip()}" if url else "")
        reference = f"{authors} ({year}). *{title}*. {pub}.{doi_url}".strip()

    return {
        "source_type": source,
        "bibliographic_reference": reference,
        "in_text_parenthetical": in_text_parenthetical,
        "in_text_narrative": in_text_narrative,
    }


def get_academic_structure(doc_type: str = "essay", topic: str = "Tema Académico") -> str:
    """Generates rigorous academic frameworks with section guidance."""
    dt = doc_type.lower().strip()

    if "ensayo" in dt or "essay" in dt:
        return (
            f"📝 **Estructura Recomendada para Ensayo Académico: {topic}**\n\n"
            "**1. Título Conciso y Atractivo** (conforme a Normas APA 7)\n"
            "**2. Introducción (10-15% del texto):**\n"
            "   • Contextualización del problema en el ámbito empresarial o de gestión.\n"
            "   • Tesis central (postura crítica o hipótesis que defenderá).\n"
            "   • Breve justificación y hoja de ruta del ensayo.\n"
            "**3. Desarrollo Argumentativo (70-75% del texto):**\n"
            "   • **Argumento 1:** Base teórica y autores relevantes (citas directas o parafraseo APA).\n"
            "   • **Argumento 2:** Evidencia práctica, datos empíricos o casos de estudio reales.\n"
            "   • **Contraargumento:** Consideración de posturas opuestas y refutación analítica.\n"
            "**4. Conclusiones (10-15% del texto):**\n"
            "   • Reafirmación de la tesis a la luz de los argumentos presentados.\n"
            "   • Implicaciones prácticas para la administración de empresas o tecnología.\n"
            "   • Preguntas abiertas o futuras líneas de investigación.\n"
            "**5. Referencias Bibliográficas** (orden alfabético estricto con sangría francesa)."
        )

    elif "informe" in dt or "report" in dt or "caso" in dt:
        return (
            f"📊 **Estructura para Informe Ejecutivo / Caso de Estudio: {topic}**\n\n"
            "**1. Portada Profesional & Resumen Ejecutivo (Executive Summary):**\n"
            "   • Síntesis en 250 palabras: problema, metodología, hallazgos clave y recomendación.\n"
            "**2. Diagnóstico de la Situación Actual:**\n"
            "   • Análisis del entorno interno y externo (matrices FODA, PESTEL o Canvas).\n"
            "**3. Definición del Problema Central & Objetivos:**\n"
            "   • Objetivo general y específicos (metodología SMART).\n"
            "**4. Propuesta de Solución o Plan Estratégico:**\n"
            "   • Plan de acción, cronograma (Gantt), presupuesto e indicadores clave (KPIs/OKRs).\n"
            "**5. Evaluación Financiera & Viabilidad:**\n"
            "   • Proyección de flujos, cálculo de VAN, TIR y Punto de Equilibrio.\n"
            "**6. Matriz de Gestión de Riesgos y Mitigación:**\n"
            "**7. Conclusiones y Recomendaciones Finales.**"
        )

    return (
        f"📚 **Estructura de Trabajo de Grado / Monografía Universitaria: {topic}**\n\n"
        "• **Capítulo 1: Planteamiento del Problema** (Pregunta de investigación, justificación, objetivos).\n"
        "• **Capítulo 2: Marco Referencial** (Antecedentes, marco teórico, marco conceptual y legal).\n"
        "• **Capítulo 3: Metodología** (Enfoque cualitativo/cuantitativo, población, muestra, instrumentos).\n"
        "• **Capítulo 4: Análisis de Resultados & Discusión** (Gráficos, tablas, contraste con la literatura).\n"
        "• **Capítulo 5: Propuesta Administrativa / Modelo de Solución.**\n"
        "• **Capítulo 6: Conclusiones, Recomendaciones y Referencias APA 7.**"
    )


def academic_helper_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    """Action entry point for ActionDispatcher."""
    params = parameters or {}
    action = params.get("action", "apa").lower().strip()

    if action in ("apa", "cita", "referencia"):
        res = generate_apa_citation(
            source_type=params.get("source_type", "book"),
            authors=params.get("authors", ""),
            year=params.get("year", ""),
            title=params.get("title", ""),
            publisher=params.get("publisher", ""),
            journal=params.get("journal", ""),
            volume=params.get("volume", ""),
            issue=params.get("issue", ""),
            pages=params.get("pages", ""),
            url=params.get("url", ""),
            doi=params.get("doi", "")
        )
        return (
            f"📖 **Formato APA 7ª Edición Generado:**\n\n"
            f"• **Referencia Bibliográfica (Lista de Referencias):**\n"
            f"  `{res['bibliographic_reference']}`\n\n"
            f"• **Cita Paréntesis (en el texto):** `{res['in_text_parenthetical']}`\n"
            f"• **Cita Narrativa (en el texto):** `{res['in_text_narrative']}`"
        )

    elif action in ("estructura", "template", "ensayo", "informe"):
        doc_t = params.get("doc_type", "ensayo")
        topic = params.get("topic", "Administración de Empresas y Tecnología")
        return get_academic_structure(doc_type=doc_t, topic=topic)

    elif action in ("normas", "formato"):
        return (
            "📏 **Parámetros Oficiales Normas APA 7ª Edición:**\n"
            "• **Márgenes:** 2.54 cm (1 pulgada) en los 4 lados.\n"
            "• **Tipografías recomendadas:** Times New Roman 12 pt, Arial 11 pt, Calibri 11 pt o Georgia 11 pt.\n"
            "• **Interlineado:** Doble (2.0) en todo el texto, sin espacio entre párrafos.\n"
            "• **Sangría:** 1.27 cm (media pulgada) en la primera línea de cada párrafo.\n"
            "• **Referencias:** Sangría francesa de 1.27 cm y orden alfabético estricto."
        )

    return "Acción académica no reconocida. Acciones soportadas: apa, estructura, normas."
