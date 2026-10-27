# -*- coding: utf-8 -*-
"""
Action handler for Operational Excellence Lean Six Sigma, OEE & Theory of Constraints (TOC).
"""

from typing import Any, Dict
from app.services.lean_six_sigma_service import lean_six_sigma_service


def lean_six_sigma_action(parameters: Dict[str, Any]) -> str:
    process_name = parameters.get("process_name", "Línea de Producción & Fulfillment Central")
    units_produced = int(parameters.get("units_produced", 10000))
    defect_opportunities = int(parameters.get("defect_opportunities_per_unit", 5))
    total_defects = int(parameters.get("total_defects", 85))
    planned_minutes = float(parameters.get("planned_production_minutes", 480.0))
    downtime_minutes = float(parameters.get("downtime_minutes", 36.0))
    ideal_cycle_sec = float(parameters.get("ideal_cycle_time_seconds", 2.4))
    daily_demand = int(parameters.get("customer_daily_demand", 9000))
    usl = float(parameters.get("usl", 105.0))
    lsl = float(parameters.get("lsl", 95.0))
    process_mean = float(parameters.get("process_mean", 100.2))
    process_std_dev = float(parameters.get("process_std_dev", 1.15))

    res = lean_six_sigma_service.evaluate_operational_excellence(
        process_name=process_name,
        units_produced=units_produced,
        defect_opportunities_per_unit=defect_opportunities,
        total_defects=total_defects,
        planned_production_minutes=planned_minutes,
        downtime_minutes=downtime_minutes,
        ideal_cycle_time_seconds=ideal_cycle_sec,
        customer_daily_demand=daily_demand,
        usl=usl,
        lsl=lsl,
        process_mean=process_mean,
        process_std_dev=process_std_dev
    )

    sig = res["six_sigma_metrics"]
    oee = res["oee_metrics"]
    toc = res["lean_toc_metrics"]
    plan = "\n".join([f"  • {step}" for step in res["dmaic_action_plan"]])

    return (
        f"⚙️ **EXCELENCIA OPERACIONAL LEAN SIX SIGMA, OEE & TEORÍA DE RESTRICCIONES (TOC)**\n\n"
        f"• **Proceso Auditado:** {res['process_name']}\n"
        f"• **Nivel Six Sigma:** **{sig['sigma_level']}σ** ({sig['dpmo']:,.1f} DPMO | Yield: {sig['yield_pct']}%)\n"
        f"• **Capacidad de Proceso:** Cp = **{sig['cp']}** | Cpk = **{sig['cpk']}** → {sig['capability_verdict']}\n"
        f"• **Efectividad Global de Equipos (OEE):** **{oee['oee_pct']}%** ({oee['oee_classification']})\n"
        f"  - Disponibilidad: {oee['availability_pct']}% | Rendimiento: {oee['performance_pct']}% | Calidad: {oee['quality_pct']}%\n"
        f"• **Sincronización Lean (Takt vs Ciclo):** Takt Time {toc['takt_time_seconds']}s vs Ciclo Real {toc['actual_cycle_time_seconds']}s → **{toc['takt_synchronization_status']}**\n"
        f"• **Restricción Dominante (TOC Goldratt):** {toc['primary_bottleneck']}\n"
        f"• **Hoja de Ruta DMAIC & Kaizen:**\n{plan}"
    )
