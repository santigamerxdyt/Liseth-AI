"""
Academic Research Action for JARVIS / Liseth.
Entrypoint for scientific literature search, literature review synthesis, and APA formatting.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.services.academic_research_service import academic_research_service

logger = logging.getLogger("jarvis.academic_research_action")


def academic_research_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    """
    Synchronous entrypoint for Academic Research tool.
    Handles 'status', 'search', 'literature_review', 'cite_apa'.
    """
    params = parameters or {}
    action = params.get("action", "search").lower().strip()
    query = params.get("query") or params.get("topic") or params.get("title") or ""
    limit = int(params.get("limit") or 5)

    try:
        if action in ["status", "estado", "info"]:
            st = academic_research_service.get_status()
            return academic_research_service.format_status_report(st)

        if action in ["review", "literature_review", "estado_del_arte", "sintesis"]:
            if not query:
                return "Señor Santiago, por favor indique el tema para generar el Estado del Arte (ejemplo: `query='Finanzas corporativas y WACC'`)."
            return academic_research_service.generate_literature_review(query, max_papers=limit)

        if action in ["search", "buscar", "papers", "articulos"]:
            if not query:
                return "Señor Santiago, indique el tema o palabras clave para buscar artículos científicos (ejemplo: `query='Estrategias de ventaja competitiva'`)."
            papers = academic_research_service.search_papers(query, limit=limit)
            if not papers:
                return f"No se hallaron artículos científicos para la consulta '{query}'."

            lines = [
                f"### 📑 Artículos Científicos Encontrados para: *{query}*",
                f"**Cantidad**: `{len(papers)} publicaciones académicas` | **Formato**: Normas APA 7.ª Ed.\n"
            ]
            for idx, p in enumerate(papers, start=1):
                cite = academic_research_service.format_apa_citation(p)
                lines.append(f"**{idx}. {p['title']}**")
                lines.append(f"- **Autores**: {', '.join(p['authors']) if p['authors'] else 'N/A'} ({p['year']})")
                lines.append(f"- **Revista**: *{p['journal']}* | Citas: `{p.get('citations', 0)}`")
                lines.append(f"- **Resumen**: {p['abstract']}")
                lines.append(f"- **Referencia APA 7**: `{cite['bibliography']}`")
                lines.append(f"- **Cita en el texto**: `{cite['parenthetical']}`")
                if p.get("doi"):
                    lines.append(f"- **DOI**: [{p['doi']}]({p['doi']})")
                lines.append("")

            return "\n".join(lines)

        return f"Acción académica '{action}' no reconocida. Use: 'search', 'literature_review', o 'status'."

    except Exception as e:
        logger.error(f"Error in academic_research_action: {e}", exc_info=True)
        return f"Error ejecutando consulta académica: {str(e)}"
