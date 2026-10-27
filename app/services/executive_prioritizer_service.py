# -*- coding: utf-8 -*-
"""
Executive Prioritization Matrix & CEO High-Impact Focus Service (Eisenhower 2.0).
Classifies executive workload and commitments into 4 dynamic quadrants:
1. Q1 - Urgente & Crítico (Crisis, firmas notariales, contingencias) -> Ejecutar Hoy
2. Q2 - Estratégico / Alto Retorno (M&A, I+D, alianzas, cultura, salud CEO) -> Foco Primario (60-70%)
3. Q3 - Operativo Delegable (Reportes de rutina, reuniones informativas) -> Delegar Inmediatamente
4. Q4 - Ruido & Descarte (Solicitudes de bajo valor, micro-gestión) -> Eliminar
Computes CEO Strategic Focus Index (%) and actionable workload rebalancing directives.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional


class ExecutivePrioritizerService:
    """Motor de análisis de carga ejecutiva y matriz de priorización Eisenhower 2.0."""

    def evaluate_priorities(
        self,
        ceo_name: str = "Santiago Huerfano",
        items: Optional[List[Dict[str, Any]]] = None,
        working_hours_day: float = 9.0
    ) -> Dict[str, Any]:
        hours = max(1.0, float(working_hours_day))

        # Default sample executive workload if none provided
        if not items or len(items) == 0:
            items = [
                {
                    "title": "Negociación de ronda de capital con inversionistas institucionales",
                    "estimated_hours": 3.0,
                    "urgency": "alta",
                    "importance": "estrategica",
                    "quadrant": "Q2"
                },
                {
                    "title": "Revisión y firma de estados financieros DIAN / SuperSociedades",
                    "estimated_hours": 1.5,
                    "urgency": "inmediata",
                    "importance": "critica",
                    "quadrant": "Q1"
                },
                {
                    "title": "Diseño de hoja de ruta de innovación con equipo de IA",
                    "estimated_hours": 2.5,
                    "urgency": "media",
                    "importance": "estrategica",
                    "quadrant": "Q2"
                },
                {
                    "title": "Responder consultas operativas de cotizaciones rutinarias",
                    "estimated_hours": 2.0,
                    "urgency": "alta",
                    "importance": "baja",
                    "quadrant": "Q3"
                },
                {
                    "title": "Reunión de actualización interna sin agenda previa",
                    "estimated_hours": 1.0,
                    "urgency": "baja",
                    "importance": "baja",
                    "quadrant": "Q4"
                }
            ]

        # Categorize into quadrants
        q1_items = []
        q2_items = []
        q3_items = []
        q4_items = []

        for item in items:
            q = item.get("quadrant", "").upper()
            if not q:
                urg = str(item.get("urgency", "")).lower()
                imp = str(item.get("importance", "")).lower()
                if "inmediata" in urg or "alta" in urg:
                    q = "Q1" if ("critica" in imp or "estrategica" in imp or "alta" in imp) else "Q3"
                else:
                    q = "Q2" if ("critica" in imp or "estrategica" in imp or "alta" in imp) else "Q4"
                item["quadrant"] = q

            if q == "Q1":
                q1_items.append(item)
            elif q == "Q2":
                q2_items.append(item)
            elif q == "Q3":
                q3_items.append(item)
            else:
                q4_items.append(item)

        q1_hours = sum(float(i.get("estimated_hours", 1.0)) for i in q1_items)
        q2_hours = sum(float(i.get("estimated_hours", 1.0)) for i in q2_items)
        q3_hours = sum(float(i.get("estimated_hours", 1.0)) for i in q3_items)
        q4_hours = sum(float(i.get("estimated_hours", 1.0)) for i in q4_items)
        total_hours = max(0.1, q1_hours + q2_hours + q3_hours + q4_hours)

        # Strategic Focus Index: % of time in Q2 (High-leverage strategic foresight)
        strategic_focus_index_pct = round((q2_hours / total_hours) * 100.0, 1)
        urgency_trap_index_pct = round(((q1_hours + q3_hours) / total_hours) * 100.0, 1)

        if strategic_focus_index_pct >= 55.0:
            diagnostic = "ÓPTIMO: Enfoque de Alta Dirección blindado en creación de valor a largo plazo (Q2)."
            status_color = "VERDE"
        elif strategic_focus_index_pct >= 35.0:
            diagnostic = "MODERADO: Riesgo de sobrecarga operativa. Se aconseja delegar las tareas de Q3 a mandos medios."
            status_color = "AMARILLO"
        else:
            diagnostic = "ALERTA CEO: 'Trampa de la Urgencia' activa. Más del 65% de la energía está consumida en contingencias y micro-gestión."
            status_color = "ROJO"

        delegation_orders = [
            f"Delegar '{i.get('title')}' ({i.get('estimated_hours')}h) al equipo de operaciones con fecha límite estricta."
            for i in q3_items
        ]
        elimination_orders = [
            f"Eliminar o declinar '{i.get('title')}' ({i.get('estimated_hours')}h) para liberar ancho de banda cognitivo."
            for i in q4_items
        ]

        actionable_directives = [
            f"1. BLOQUE DE FOCO PROFUNDO (Q2): Proteger {q2_hours:.1f} horas sin interrupciones para visión, M&A y productos.",
            f"2. GESTIÓN INMEDIATA (Q1): Resolver {q1_hours:.1f} horas de prioridades críticas en la primera ventana del día.",
            f"3. DEPURACIÓN DE AGENDA: Liberar {(q3_hours + q4_hours):.1f} horas delegando {len(q3_items)} tareas operativas y descartando {len(q4_items)} actividades de bajo impacto."
        ]

        return {
            "ceo_name": ceo_name,
            "metrics": {
                "strategic_focus_index_pct": strategic_focus_index_pct,
                "urgency_trap_index_pct": urgency_trap_index_pct,
                "total_workload_hours": round(total_hours, 1),
                "planned_day_capacity_hours": hours,
                "workload_utilization_pct": round((total_hours / hours) * 100.0, 1),
                "status_color": status_color,
                "diagnostic": diagnostic
            },
            "quadrants": {
                "q1_urgent_critical": {
                    "label": "Q1: Urgente & Crítico (Resolver Hoy)",
                    "hours": round(q1_hours, 1),
                    "items": q1_items
                },
                "q2_strategic_high_value": {
                    "label": "Q2: Estratégico & Alto Valor (Foco Principal CEO)",
                    "hours": round(q2_hours, 1),
                    "items": q2_items
                },
                "q3_urgent_delegate": {
                    "label": "Q3: Operativo Delegable (Transferir a Equipo)",
                    "hours": round(q3_hours, 1),
                    "items": q3_items,
                    "delegation_orders": delegation_orders
                },
                "q4_eliminate": {
                    "label": "Q4: Ruido & Descarte (Eliminar)",
                    "hours": round(q4_hours, 1),
                    "items": q4_items,
                    "elimination_orders": elimination_orders
                }
            },
            "directives": actionable_directives,
            "timestamp": datetime.now().isoformat()
        }


executive_prioritizer_service = ExecutivePrioritizerService()
