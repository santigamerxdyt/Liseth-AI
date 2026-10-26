"""
Balanced Scorecard (BSC) & Corporate OKRs Service for Liseth / JARVIS.
Implements Kaplan & Norton 4 Perspectives and Doerr OKR Methodology:
- 4 Perspectives: Financial, Customer, Internal Processes, Learning & Growth
- Key Results Tracking with current vs target metrics and weightings
- Consolidated Corporate Health Index (%) & Traffic Light Status
- Persistent Storage in data/corporate_okrs.json
"""
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

DATA_FILE = os.path.join("data", "corporate_okrs.json")


class BscOkrsService:
    def __init__(self):
        self._ensure_storage()

    def _ensure_storage(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(DATA_FILE):
            default_okrs = [
                {
                    "id": "OKR-FIN-01",
                    "perspective": "Financiera",
                    "objective": "Acelerar el Crecimiento de Ingresos y Flujo de Caja Libre",
                    "key_results": [
                        {
                            "id": "KR-01",
                            "title": "Cerrar $80.000.000 COP en contratos de consultoría",
                            "current": 52000000.0,
                            "target": 80000000.0,
                            "unit": "COP",
                            "weight": 0.50
                        },
                        {
                            "id": "KR-02",
                            "title": "Mantener margen operativo EBITDA superior al 30%",
                            "current": 33.5,
                            "target": 30.0,
                            "unit": "%",
                            "weight": 0.50
                        }
                    ]
                },
                {
                    "id": "OKR-CLI-01",
                    "perspective": "Clientes",
                    "objective": "Consolidar la Lealtad y Satisfacción de Clientes Corporativos",
                    "key_results": [
                        {
                            "id": "KR-03",
                            "title": "Alcanzar Net Promoter Score (NPS) mayor a 75",
                            "current": 82.0,
                            "target": 75.0,
                            "unit": "pts",
                            "weight": 0.50
                        },
                        {
                            "id": "KR-04",
                            "title": "Tasa de retención anual de clientes corporativos > 90%",
                            "current": 94.0,
                            "target": 90.0,
                            "unit": "%",
                            "weight": 0.50
                        }
                    ]
                },
                {
                    "id": "OKR-INT-01",
                    "perspective": "Procesos Internos",
                    "objective": "Automatización Total y Excelencia en Tiempos de Entrega",
                    "key_results": [
                        {
                            "id": "KR-05",
                            "title": "Automatizar 80% de informes financieros con IA",
                            "current": 85.0,
                            "target": 80.0,
                            "unit": "%",
                            "weight": 0.60
                        },
                        {
                            "id": "KR-06",
                            "title": "Reducir tiempo de ciclo de cotización a menos de 4 horas",
                            "current": 3.2,
                            "target": 4.0,
                            "unit": "horas",
                            "weight": 0.40
                        }
                    ]
                },
                {
                    "id": "OKR-APR-01",
                    "perspective": "Aprendizaje & Crecimiento",
                    "objective": "Desarrollo de Competencias en Analítica y Ciberseguridad",
                    "key_results": [
                        {
                            "id": "KR-07",
                            "title": "Certificar 100% de proyectos con auditoría de ciberseguridad",
                            "current": 100.0,
                            "target": 100.0,
                            "unit": "%",
                            "weight": 0.50
                        },
                        {
                            "id": "KR-08",
                            "title": "Completar 40 horas de estudio avanzado en finanzas cuantitativas",
                            "current": 32.0,
                            "target": 40.0,
                            "unit": "horas",
                            "weight": 0.50
                        }
                    ]
                }
            ]
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(default_okrs, f, indent=2, ensure_ascii=False)

    def _load(self) -> List[Dict[str, Any]]:
        self._ensure_storage()
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save(self, okrs: List[Dict[str, Any]]):
        os.makedirs("data", exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(okrs, f, indent=2, ensure_ascii=False)

    def get_dashboard(self) -> Dict[str, Any]:
        """
        Calculates weighted progress across all 4 perspectives and overall corporate index.
        """
        okrs = self._load()
        perspectives = {
            "Financiera": {"items": [], "progress_sum": 0.0, "count": 0},
            "Clientes": {"items": [], "progress_sum": 0.0, "count": 0},
            "Procesos Internos": {"items": [], "progress_sum": 0.0, "count": 0},
            "Aprendizaje & Crecimiento": {"items": [], "progress_sum": 0.0, "count": 0}
        }

        total_weighted_progress = 0.0
        total_okr_count = len(okrs)

        for obj in okrs:
            persp = obj.get("perspective", "Financiera")
            krs = obj.get("key_results", [])

            # Compute objective progress
            obj_prog = 0.0
            total_weight = sum(kr.get("weight", 1.0) for kr in krs) or 1.0
            kr_details = []

            for kr in krs:
                cur = float(kr.get("current", 0.0))
                tgt = float(kr.get("target", 1.0))
                wt = float(kr.get("weight", 1.0))

                # Handle inverse metrics (e.g. reducing cycle time)
                unit = kr.get("unit", "")
                if unit == "horas" and cur <= tgt:
                    kr_pct = 100.0
                elif tgt > 0:
                    kr_pct = min(100.0, max(0.0, (cur / tgt) * 100.0))
                else:
                    kr_pct = 100.0 if cur >= tgt else 0.0

                obj_prog += (kr_pct * (wt / total_weight))
                kr_details.append({
                    **kr,
                    "progress_pct": round(kr_pct, 1)
                })

            obj_score = round(obj_prog, 1)
            status = "VERDE" if obj_score >= 70.0 else ("AMARILLO" if obj_score >= 40.0 else "ROJO")

            item = {
                "id": obj.get("id"),
                "objective": obj.get("objective"),
                "perspective": persp,
                "progress_pct": obj_score,
                "status": status,
                "key_results": kr_details
            }

            if persp in perspectives:
                perspectives[persp]["items"].append(item)
                perspectives[persp]["progress_sum"] += obj_score
                perspectives[persp]["count"] += 1

            total_weighted_progress += obj_score

        # Calculate perspective averages
        persp_summary = {}
        for p_name, p_data in perspectives.items():
            cnt = p_data["count"]
            avg = round(p_data["progress_sum"] / cnt, 1) if cnt > 0 else 0.0
            persp_summary[p_name] = {
                "average_pct": avg,
                "status": "VERDE" if avg >= 70.0 else ("AMARILLO" if avg >= 40.0 else "ROJO"),
                "objectives": p_data["items"]
            }

        global_avg = round(total_weighted_progress / total_okr_count, 1) if total_okr_count > 0 else 0.0
        global_status = "VERDE" if global_avg >= 70.0 else ("AMARILLO" if global_avg >= 40.0 else "ROJO")

        return {
            "global_corporate_health_pct": global_avg,
            "global_status": global_status,
            "perspectives": persp_summary,
            "raw_okrs": okrs
        }

    def update_kr_progress(self, kr_id: str, new_value: float) -> bool:
        """
        Updates the current value of a specific Key Result.
        """
        okrs = self._load()
        found = False
        for obj in okrs:
            for kr in obj.get("key_results", []):
                if kr.get("id") == kr_id:
                    kr["current"] = float(new_value)
                    found = True
                    break
            if found:
                break
        if found:
            self._save(okrs)
            return True
        return False

    def format_markdown_report(self) -> str:
        data = self.get_dashboard()
        g_pct = data["global_corporate_health_pct"]
        g_st = data["global_status"]

        md = [
            "# 📈 CUADRO DE MANDO INTEGRAL (BALANCED SCORECARD) & OKRs",
            f"**Índice Global de Salud Corporativa**: **`{g_pct}%`** | **Semáforo**: `{g_st}`",
            "",
            "### 🎯 Desempeño por las 4 Perspectivas de Kaplan & Norton"
        ]

        for p_name, p_info in data["perspectives"].items():
            st_icon = "🟢" if p_info["status"] == "VERDE" else ("🟡" if p_info["status"] == "AMARILLO" else "🔴")
            md.append(f"\n#### {st_icon} Perspectiva {p_name} — Avance: `{p_info['average_pct']}%`")

            for obj in p_info["objectives"]:
                md.append(f"- **{obj['objective']}** (`{obj['progress_pct']}%`)")
                for kr in obj["key_results"]:
                    md.append(f"  * [{kr['progress_pct']}%] {kr['title']} (Actual: {kr['current']} / Meta: {kr['target']} {kr['unit']})")

        return "\n".join(md)


bsc_okrs_service = BscOkrsService()
