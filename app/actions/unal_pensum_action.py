"""
UNAL Pensum Action for JARVIS / Liseth.
Entrypoint for curriculum navigation, prerequisite verification, subject guides,
and graduation tracking for Universidad Nacional de Colombia (Sede Palmira).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.services.unal_pensum_service import unal_pensum_service

logger = logging.getLogger("jarvis.unal_pensum_action")


def unal_pensum_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    """
    Synchronous entrypoint for UNAL Pensum academic tool.
    Handles: 'overview', 'subject', 'prerequisites', 'semester', 'checklist'.
    """
    params = parameters or {}
    action = params.get("action", "overview").lower().strip()
    query = params.get("query") or params.get("materia") or params.get("asignatura") or params.get("codigo") or ""
    semester = params.get("semester") or params.get("semestre") or params.get("matricula")
    credits_approved = params.get("credits") or params.get("creditos") or params.get("approved_credits")

    try:
        # 1. Overview
        if action in ["overview", "pensum", "plan_estudios", "resumen"]:
            info = unal_pensum_service.get_curriculum_overview()
            dist = info["distribucion_creditos"]
            rutas = "\n".join([f"  - {r}" for r in info["rutas_profundizacion_palmira"]])
            lines = [
                f"### 🏛️ Plan de Estudios Oficial: Administración de Empresas",
                f"- **Institución**: {info['universidad']} ({info['sede']})",
                f"- **Facultad**: {info['facultad']}",
                f"- **Normativa Vigente**: `{info['acuerdo_vigente']}`",
                f"- **Total Créditos Exigidos**: `{info['creditos_totales']} créditos`\n",
                "#### 1. Distribución de Créditos por Componente",
                f"- **Fundamentación**: `{dist['fundamentacion']['total']} créditos` ({dist['fundamentacion']['obligatorios']} obligatorios + {dist['fundamentacion']['optativos']} optativos)",
                f"- **Disciplinar o Profesional**: `{dist['disciplinar']['total']} créditos` ({dist['disciplinar']['obligatorios']} obligatorios + {dist['disciplinar']['optativos']} optativos)",
                f"- **Libre Elección**: `{dist['libre_eleccion']['total']} créditos` ({dist['libre_eleccion']['porcentaje']} del total del plan)\n",
                "#### 2. Requisitos Clave de Grado",
                f"- **Inglés**: {info['requisitos_adicionales']['ingles']}",
                f"- **Consultoría y Asesoría**: {info['requisitos_adicionales']['consultoria_asesoria']}",
                f"- **Trabajo de Grado**: {info['requisitos_adicionales']['trabajo_de_grado']}\n",
                f"#### 3. Rutas de Profundización en Sede Palmira:\n{rutas}\n\n",
                "Liseth está configurada con cada una de las materias, fórmulas, prerrequisitos y metodologías de su carrera, señor Santiago."
            ]
            return "\n".join(lines)

        # 2. Prerequisites check
        if action in ["prerequisites", "prerrequisitos", "prerrequisito", "prerequisito", "requisitos", "prereq", "correquisitos"]:
            if not query:
                return "Señor Santiago, indique la materia para consultar sus prerrequisitos (ejemplo: `query='Trabajo de Grado'` o `query='Formulación y Evaluación de Proyectos'`)."
            return unal_pensum_service.check_prerequisites(query)

        # 3. Subject academic briefing
        if action in ["subject", "asignatura", "materia", "guia", "info"]:
            if not query:
                return "Señor Santiago, especifique el nombre o código de la asignatura que desea consultar (ejemplo: `query='Costos'` o `query='Investigación de Operaciones'`)."
            return unal_pensum_service.generate_subject_academic_briefing(query)

        # 4. Semester list
        if action in ["semester", "semestre", "matricula"]:
            sem_num = int(semester or 1)
            subjects = unal_pensum_service.get_semester_subjects(sem_num)
            if not subjects:
                return f"No se hallaron asignaturas registradas para la matrícula/semestre {sem_num}."

            lines = [
                f"### 📚 Asignaturas de la Matrícula {sem_num} — UNAL Sede Palmira",
                "| Código | Nombre de la Asignatura | Créditos | Tipología | Prerrequisito |",
                "| :---: | :--- | :---: | :---: | :--- |"
            ]
            for s in subjects:
                pr = ", ".join(s.get("prerrequisitos", [])) if s.get("prerrequisitos") else "Ninguno"
                lines.append(f"| `{s['codigo']}` | **{s['nombre']}** | {s['creditos']} | {s['tipologia']} | {pr} |")
            return "\n".join(lines)

        # 5. Graduation Checklist
        if action in ["checklist", "avance", "progreso", "grado"]:
            disc_credits = int(credits_approved or 0)
            return unal_pensum_service.calculate_graduation_checklist(disc_credits)

        # 6. Normative Framework
        if action in ["normative", "normatividad", "ley", "marco_legal", "marco_normativo"]:
            return unal_pensum_service.get_normative_framework(query)

        return f"Acción curricular '{action}' no reconocida. Opciones: 'overview', 'subject', 'prerequisites', 'semester', 'checklist', 'normative'."

    except Exception as e:
        logger.error(f"Error in unal_pensum_action: {e}", exc_info=True)
        return f"Error consultando el pensum de la Universidad Nacional: {str(e)}"
