# -*- coding: utf-8 -*-
"""
Excelencia Operacional Lean Six Sigma, OEE & Teoría de Restricciones (TOC) Service.
Provides industrial and service operations engineering diagnostics:
1. Six Sigma Quality: DPMO, Yield %, Sigma Level (1σ - 6σ with 1.5σ shift), Cp and Cpk
2. Overall Equipment Effectiveness (OEE = Availability × Performance × Quality) vs 85% World Class
3. Lean Manufacturing: Takt Time vs Cycle Time synchronization & Goldratt TOC Bottleneck Analysis
"""

import math
from datetime import datetime
from typing import Any, Dict, List


class LeanSixSigmaService:
    """Motor cuantitativo de Excelencia Operacional Lean Six Sigma, OEE y TOC."""

    @staticmethod
    def _dpmo_to_sigma(dpmo: float) -> float:
        """Converts DPMO to Motorola Sigma Level (including 1.5 sigma long-term shift)."""
        if dpmo <= 3.4:
            return 6.0
        if dpmo >= 933193.0:
            return 0.5
        p_defect = max(1e-7, min(0.9999, dpmo / 1_000_000.0))
        # Rational approximation to inverse standard normal CDF for 1 - p_defect
        # Using Acklam/Hastings approximation
        q = 1.0 - p_defect
        if q == 0.5:
            z = 0.0
        else:
            p = p_defect if q > 0.5 else q
            t = math.sqrt(-2.0 * math.log(p))
            c0, c1, c2 = 2.515517, 0.802853, 0.010328
            d1, d2, d3 = 1.432788, 0.189269, 0.001308
            z_abs = t - ((c0 + c1 * t + c2 * t * t) / (1.0 + d1 * t + d2 * t * t + d3 * t * t * t))
            z = z_abs if q > 0.5 else -z_abs
        sigma_lvl = max(0.5, min(6.0, z + 1.5))
        return round(sigma_lvl, 2)

    def evaluate_operational_excellence(
        self,
        process_name: str = "Línea de Producción & Fulfillment Central",
        units_produced: int = 10000,
        defect_opportunities_per_unit: int = 5,
        total_defects: int = 85,
        planned_production_minutes: float = 480.0,
        downtime_minutes: float = 36.0,
        ideal_cycle_time_seconds: float = 2.4,
        customer_daily_demand: int = 9000,
        usl: float = 105.0,
        lsl: float = 95.0,
        process_mean: float = 100.2,
        process_std_dev: float = 1.15
    ) -> Dict[str, Any]:
        units = max(1, int(units_produced))
        opps_per_unit = max(1, int(defect_opportunities_per_unit))
        defects = max(0, int(total_defects))
        planned_min = max(1.0, float(planned_production_minutes))
        down_min = max(0.0, min(planned_min - 1.0, float(downtime_minutes)))
        ideal_sec = max(0.05, float(ideal_cycle_time_seconds))
        demand = max(1, int(customer_daily_demand))
        std_dev = max(0.0001, float(process_std_dev))

        # 1. Six Sigma & Process Capability (Cp, Cpk)
        total_opportunities = units * opps_per_unit
        dpmo = round((defects / max(1, total_opportunities)) * 1_000_000.0, 1)
        yield_pct = round(max(0.0, (1.0 - (defects / max(1, total_opportunities))) * 100.0), 4)
        sigma_level = self._dpmo_to_sigma(dpmo)

        spec_width = max(0.01, float(usl) - float(lsl))
        cp = round(spec_width / (6.0 * std_dev), 2)
        cpu = (float(usl) - float(process_mean)) / (3.0 * std_dev)
        cpl = (float(process_mean) - float(lsl)) / (3.0 * std_dev)
        cpk = round(min(cpu, cpl), 2)

        if cpk >= 1.33:
            capability_verdict = "CAPAZ Y CENTRADO (Clase Mundial >= 1.33)"
        elif cpk >= 1.00:
            capability_verdict = "ACEPTABLE CON VIGILANCIA (1.00 - 1.32)"
        else:
            capability_verdict = "INCAPAZ (< 1.00 - Requiere Intervención DMAIC)"

        # 2. OEE (Overall Equipment Effectiveness)
        operating_min = max(1.0, planned_min - down_min)
        availability_pct = round((operating_min / planned_min) * 100.0, 2)

        ideal_run_minutes = (units * ideal_sec) / 60.0
        performance_pct = round(min(100.0, (ideal_run_minutes / operating_min) * 100.0), 2)

        good_units = max(0, units - min(units, defects))
        quality_pct = round((good_units / units) * 100.0, 2)

        oee_pct = round((availability_pct / 100.0) * (performance_pct / 100.0) * (quality_pct / 100.0) * 100.0, 2)

        if oee_pct >= 85.0:
            oee_class = "CLASE MUNDIAL (OEE >= 85%)"
        elif oee_pct >= 70.0:
            oee_class = "COMPETITIVO ESTÁNDAR (70% - 84.9%)"
        else:
            oee_class = "BAJA EFICIENCIA (< 70% - Activar TPM / SMED)"

        # 3. Lean Takt Time vs Actual Cycle Time & Goldratt TOC
        takt_time_sec = round((planned_min * 60.0) / demand, 2)
        actual_cycle_sec = round((operating_min * 60.0) / units, 2)

        if actual_cycle_sec <= takt_time_sec:
            takt_status = "FLUJO SINCRONIZADO (Ciclo Real <= Takt Time)"
        else:
            takt_status = "CUELLO DE BOTELLA ACTIVO (Ciclo Real > Takt Time)"

        # Identify weakest OEE pillar (TOC Primary Constraint)
        pillars = {
            "Disponibilidad (Paradas / Averías)": availability_pct,
            "Rendimiento (Velocidad / Microparadas)": performance_pct,
            "Calidad (Defectos / Reprocesos)": quality_pct
        }
        primary_bottleneck = min(pillars, key=pillars.get)

        dmaic_roadmap: List[str] = [
            f"1. IDENTIFICAR RESTRICCIÓN (TOC): El eslabón crítico actual es '{primary_bottleneck}' ({pillars[primary_bottleneck]}%).",
            f"2. EXPLOTAR & SUBORDINAR (SMED/TPM): Reducir los {down_min:.0f} min de paradas no programadas para elevar OEE desde {oee_pct}% hacia 85%+.",
            f"3. CONTROL ESTADÍSTICO (SPC): Con Nivel {sigma_level}σ ({dpmo:,.1f} DPMO) y Cpk = {cpk}, centrar la media μ={process_mean} respecto a [{lsl}, {usl}]."
        ]

        return {
            "process_name": process_name,
            "six_sigma_metrics": {
                "units_produced": units,
                "defect_opportunities_per_unit": opps_per_unit,
                "total_opportunities": total_opportunities,
                "total_defects": defects,
                "dpmo": dpmo,
                "yield_pct": yield_pct,
                "sigma_level": sigma_level,
                "cp": cp,
                "cpk": cpk,
                "capability_verdict": capability_verdict
            },
            "oee_metrics": {
                "availability_pct": availability_pct,
                "performance_pct": performance_pct,
                "quality_pct": quality_pct,
                "oee_pct": oee_pct,
                "oee_classification": oee_class,
                "world_class_benchmark_pct": 85.0
            },
            "lean_toc_metrics": {
                "takt_time_seconds": takt_time_sec,
                "actual_cycle_time_seconds": actual_cycle_sec,
                "ideal_cycle_time_seconds": ideal_sec,
                "takt_synchronization_status": takt_status,
                "primary_bottleneck": primary_bottleneck
            },
            "dmaic_action_plan": dmaic_roadmap,
            "timestamp": datetime.now().isoformat()
        }


lean_six_sigma_service = LeanSixSigmaService()
