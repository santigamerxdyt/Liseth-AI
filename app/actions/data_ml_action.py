"""
Data Science & Machine Learning Action for JARVIS / Liseth.
Entrypoint for dataset profiling, outlier detection, linear regression, and ML code generation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.services.data_ml_service import data_ml_service

logger = logging.getLogger("jarvis.data_ml_action")


def data_ml_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    """
    Synchronous entrypoint for Data Science & ML Toolkit.
    Handles: 'status', 'profile', 'clean', 'regression', 'forecast', 'code'.
    """
    params = parameters or {}
    action = params.get("action", "status").lower().strip()

    try:
        if action in ["status", "estado", "info"]:
            st = data_ml_service.get_status()
            return data_ml_service.format_status_report(st)

        if action in ["profile", "clean", "limpieza", "outliers", "calidad"]:
            data_str = params.get("data") or params.get("csv") or params.get("dataset") or ""
            if not data_str:
                return "Señor Santiago, proporcione los datos en formato CSV o lista numérica para analizarlos."
            return data_ml_service.profile_and_clean_data(data_str)

        if action in ["regression", "regresion", "ols", "ajuste"]:
            x_raw = params.get("x") or []
            y_raw = params.get("y") or []
            pred_x = params.get("predict_x")

            if isinstance(x_raw, str):
                x_vals = [float(val.strip()) for val in x_raw.split(",") if val.strip()]
            else:
                x_vals = [float(v) for v in x_raw]

            if isinstance(y_raw, str):
                y_vals = [float(val.strip()) for val in y_raw.split(",") if val.strip()]
            else:
                y_vals = [float(v) for v in y_raw]

            predict_val = float(pred_x) if pred_x is not None else None
            return data_ml_service.linear_regression(x_vals, y_vals, predict_x=predict_val)

        if action in ["forecast", "series", "pronostico", "tiempo"]:
            vals_raw = params.get("values") or params.get("series") or params.get("data") or []
            if isinstance(vals_raw, str):
                values = [float(v.strip()) for v in vals_raw.split(",") if v.strip()]
            else:
                values = [float(v) for v in vals_raw]

            periods = int(params.get("periods") or 3)
            return data_ml_service.time_series_forecast(values, periods_ahead=periods)

        if action in ["code", "script", "codigo", "pipeline"]:
            task = params.get("task") or params.get("type") or "classification"
            script = data_ml_service.generate_ml_python_script(task)
            return f"```python\n{script}\n```"

        return f"Acción de Data/ML '{action}' no reconocida. Opciones: 'profile', 'regression', 'forecast', 'code', 'status'."

    except Exception as e:
        logger.error(f"Error in data_ml_action: {e}", exc_info=True)
        return f"Error ejecutando análisis de datos: {str(e)}"
