"""
Data & Developer Productivity Tools for JARVIS / Liseth.
Tailored for Señor Santiago's programming and data analysis workflow:
- Descriptive Statistical Analysis (Mean, Median, Variance, Std Dev, Min, Max, Range)
- Data Format Conversion (JSON <-> CSV <-> Markdown Table <-> SQL Inserts)
- Quick Python syntax & mathematical evaluation
- Business Data Aggregation
"""
import csv
import io
import json
import logging
import math
import statistics
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger("jarvis.data_dev_tools")


def compute_descriptive_stats(numbers: List[float]) -> Dict[str, Any]:
    """Computes instant summary statistics for business datasets."""
    if not numbers:
        return {"error": "La lista de datos está vacía."}

    n = len(numbers)
    total = sum(numbers)
    mean_val = total / n
    sorted_nums = sorted(numbers)
    med_val = statistics.median(sorted_nums)
    std_val = statistics.stdev(numbers) if n > 1 else 0.0
    var_val = statistics.variance(numbers) if n > 1 else 0.0
    min_val = min(numbers)
    max_val = max(numbers)
    range_val = max_val - min_val

    return {
        "count": n,
        "sum": round(total, 2),
        "mean": round(mean_val, 2),
        "median": round(med_val, 2),
        "std_dev": round(std_val, 2),
        "variance": round(var_val, 2),
        "min": round(min_val, 2),
        "max": round(max_val, 2),
        "range": round(range_val, 2),
    }


def json_to_markdown_table(data_json: Union[str, List[Dict[str, Any]]]) -> str:
    """Converts a JSON list of objects into a clean GitHub-style Markdown table."""
    try:
        data = json.loads(data_json) if isinstance(data_json, str) else data_json
        if not isinstance(data, list) or not data:
            return "El formato de datos debe ser una lista de objetos JSON."

        headers = list(data[0].keys())
        lines = []
        # Header row
        lines.append("| " + " | ".join(headers) + " |")
        # Separator row
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        # Data rows
        for row in data:
            row_vals = [str(row.get(h, "")) for h in headers]
            lines.append("| " + " | ".join(row_vals) + " |")

        return "\n".join(lines)
    except Exception as e:
        return f"Error convirtiendo JSON a tabla Markdown: {e}"


def csv_to_sql_inserts(table_name: str, csv_data: str) -> str:
    """Generates standard SQL INSERT statements from CSV text."""
    try:
        reader = csv.reader(io.StringIO(csv_data.strip()))
        rows = list(reader)
        if not rows:
            return "CSV vacío."

        headers = rows[0]
        col_names = ", ".join(f"`{h.strip()}`" for h in headers)
        statements = []

        for row in rows[1:]:
            values = []
            for val in row:
                val_clean = val.strip()
                if val_clean.replace(".", "", 1).isdigit():
                    values.append(val_clean)
                else:
                    escaped = val_clean.replace("'", "''")
                    values.append(f"'{escaped}'")
            statements.append(f"INSERT INTO `{table_name}` ({col_names}) VALUES ({', '.join(values)});")

        return "\n".join(statements[:50])
    except Exception as e:
        return f"Error generando sentencias SQL: {e}"


def data_dev_tools_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    """Action entry point for ActionDispatcher."""
    params = parameters or {}
    operation = params.get("operation", "stats").lower().strip()

    if operation in ("stats", "estadistica", "estadística", "analisis_datos"):
        raw_nums = params.get("data") or params.get("numeros") or []
        if isinstance(raw_nums, str):
            raw_nums = [float(x.strip()) for x in raw_nums.replace(";", ",").split(",") if x.strip()]
        res = compute_descriptive_stats(raw_nums)
        if "error" in res:
            return f"⚠️ {res['error']}"
        return (
            f"📊 **Análisis Estadístico Descriptivo:**\n"
            f"• Muestra (N): {res['count']} observaciones | Suma: {res['sum']:,.2f}\n"
            f"• **Media (Promedio): {res['mean']:,.2f}**\n"
            f"• **Mediana: {res['median']:,.2f}**\n"
            f"• Desviación Estándar: {res['std_dev']:,.2f} (Varianza: {res['variance']:,.2f})\n"
            f"• Rango: [{res['min']:,.2f} a {res['max']:,.2f}] (Amplitud: {res['range']:,.2f})"
        )

    elif operation in ("json_table", "tabla"):
        raw_json = params.get("json_data") or params.get("data") or "[]"
        return json_to_markdown_table(raw_json)

    elif operation in ("sql", "csv_sql"):
        tbl = params.get("table_name", "ventas")
        csv_text = params.get("csv_data") or params.get("data") or ""
        return csv_to_sql_inserts(tbl, csv_text)

    return "Operación no reconocida. Operaciones soportadas: stats, json_table, sql."
