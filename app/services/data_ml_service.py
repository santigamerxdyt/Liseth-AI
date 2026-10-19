"""
Data Science, Machine Learning & Analytics Service for JARVIS / Liseth.
Provides automated data profiling, outlier detection, Pearson correlation,
Linear Regression, Time Series Forecasting, and Scikit-Learn Python code generation.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import math
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger("jarvis.data_ml")


class DataMLService:
    """
    Data Science & Applied Machine Learning Suite.
    Empowers Liseth to clean dirty datasets, perform statistical modeling,
    and generate predictive analytics for Señor Santiago.
    """

    def get_status(self) -> Dict[str, Any]:
        """Returns the operational status of the Data & ML toolkit."""
        return {
            "engine": "Data Science & Machine Learning Toolkit (v1.0)",
            "algorithms": [
                "Auto-Profiling & Detección de Outliers (Método IQR y Z-Score)",
                "Estadística Descriptiva e Inferencial (Matriz de Correlación Pearson)",
                "Regresión Lineal OLS (Pendiente, Intercepto, R², MSE, RMSE)",
                "Pronóstico de Series de Tiempo (Suavizamiento Exponencial y Medias Móviles)",
                "Generador de Pipelines de ML en Python (Pandas + Scikit-Learn)"
            ],
            "status": "ONLINE"
        }

    def format_status_report(self, st: Dict[str, Any]) -> str:
        """Formats the status report for Señor Santiago."""
        algos = "\n".join([f"  - {a}" for a in st.get("algorithms", [])])
        return (
            "### 🔬 Motor de Ciencia de Datos y Machine Learning (Data & ML Toolkit)\n"
            f"- **Suite**: `{st.get('engine')}`\n"
            f"- **Capacidades Analíticas Activas**:\n{algos}\n\n"
            "Listo para auditar y limpiar datos, entrenar modelos estadísticos y generar código predictivo, señor Santiago."
        )

    # -------------------------------------------------------------------------
    # 1. Data Profiling & Outlier Detection
    # -------------------------------------------------------------------------

    def profile_and_clean_data(self, data_str: str) -> str:
        """
        Profiles CSV/tabular text data: missing values, types, duplicates, and outliers.
        """
        raw = data_str.strip()
        if not raw:
            return "Debe proporcionar una cadena con datos en formato CSV o lista numérica."

        # Detect CSV or comma-separated numbers
        lines = [line.strip() for line in raw.split("\n") if line.strip()]
        if not lines:
            return "No se detectaron filas válidas en los datos."

        # Parse CSV
        reader = csv.reader(io.StringIO(raw))
        rows = list(reader)
        if len(rows) < 2:
            # Single row of numbers
            try:
                nums = [float(x.strip()) for x in rows[0] if x.strip()]
                return self._profile_single_numeric_series("Serie Numérica", nums)
            except ValueError:
                return "Los datos proporcionados no contienen filas suficientes para un perfilamiento tabular."

        headers = [h.strip() for h in rows[0]]
        data_rows = rows[1:]
        total_rows = len(data_rows)
        total_cols = len(headers)

        col_data: Dict[str, List[str]] = {h: [] for h in headers}
        for r in data_rows:
            for idx, h in enumerate(headers):
                val = r[idx].strip() if idx < len(r) else ""
                col_data[h].append(val)

        report_lines = [
            f"### 📋 Reporte de Perfilamiento y Calidad de Datos",
            f"- **Dimensiones del Dataset**: `{total_rows} filas` × `{total_cols} columnas`",
            f"- **Columnas Identificadas**: `{', '.join(headers)}`\n",
            "#### 1. Diagnóstico de Columnas y Valores Nulos",
            "| Columna | Tipo Inferido | Registros | Nulos / Vacíos | % Nulos | Alerta de Calidad |",
            "| :--- | :---: | :---: | :---: | :---: | :---: |"
        ]

        outlier_alerts = []

        for h in headers:
            vals = col_data[h]
            nulls = sum(1 for v in vals if v in ["", "null", "none", "nan", "na", "n/a", "?"])
            null_pct = (nulls / total_rows) * 100.0 if total_rows > 0 else 0.0

            # Infer type
            numeric_vals = []
            for v in vals:
                try:
                    numeric_vals.append(float(v))
                except ValueError:
                    pass

            is_numeric = len(numeric_vals) >= (total_rows - nulls) * 0.8 and len(numeric_vals) > 0
            inferred_type = "Numérico (Float/Int)" if is_numeric else "Texto / Categórico"

            alert = "🟢 Óptimo" if null_pct == 0 else ("🟡 Moderado" if null_pct < 15 else "🔴 Crítico (>15% nulos)")
            report_lines.append(f"| `{h}` | {inferred_type} | {total_rows} | {nulls} | {null_pct:.1f}% | {alert} |")

            # Outlier check for numeric columns
            if is_numeric and len(numeric_vals) >= 4:
                numeric_vals.sort()
                n = len(numeric_vals)
                q1 = numeric_vals[int(n * 0.25)]
                q3 = numeric_vals[int(n * 0.75)]
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                outliers = [x for x in numeric_vals if x < lower_bound or x > upper_bound]
                if outliers:
                    outlier_alerts.append(
                        f"- Columna **`{h}`**: `{len(outliers)} outliers detectados` por rango IQR "
                        f"(Valores fuera del intervalo `[{lower_bound:.2f}, {upper_bound:.2f}]`). "
                        f"Ejemplos extremos: `{outliers[:3]}`"
                    )

        report_lines.append("")
        if outlier_alerts:
            report_lines.append("#### 2. Detección de Valores Atípicos (Outliers)")
            report_lines.extend(outlier_alerts)
            report_lines.append("")

        report_lines.extend([
            "#### 3. Recomendaciones de Limpieza para Santiago",
            "1. **Imputación de Nulos**: En variables numéricas con < 5% nulos, imputar con la mediana para no distorsionar por asimetría; en categóricas, usar la moda.",
            "2. **Tratamiento de Outliers**: Evaluar si los atípicos son errores de digitación o transacciones legítimas de alto valor (Winsorización recomendada antes de modelos lineales).",
            "3. **Normalización**: Escalar variables numéricas con `StandardScaler` o `RobustScaler` antes de aplicar algoritmos de agrupamiento o regresión."
        ])
        return "\n".join(report_lines)

    def _profile_single_numeric_series(self, name: str, numbers: List[float]) -> str:
        """Profiles a single list of numbers."""
        n = len(numbers)
        if n == 0:
            return "La serie no contiene números válidos."
        mean = sum(numbers) / n
        variance = sum((x - mean) ** 2 for x in numbers) / (n - 1 if n > 1 else 1)
        std_dev = math.sqrt(variance)
        sorted_nums = sorted(numbers)
        median = sorted_nums[n // 2] if n % 2 != 0 else (sorted_nums[n // 2 - 1] + sorted_nums[n // 2]) / 2.0
        q1 = sorted_nums[int(n * 0.25)]
        q3 = sorted_nums[int(n * 0.75)]
        iqr = q3 - q1

        outliers = [x for x in sorted_nums if x < (q1 - 1.5 * iqr) or x > (q3 + 1.5 * iqr)]

        return (
            f"### 📊 Perfil Estadístico: *{name}*\n"
            f"- **Observaciones (N)**: `{n}`\n"
            f"- **Media (Promedio)**: `{mean:.2f}`\n"
            f"- **Mediana**: `{median:.2f}`\n"
            f"- **Desviación Estándar**: `{std_dev:.2f}` (Varianza: `{variance:.2f}`)\n"
            f"- **Rango Intercuartil (IQR)**: Q1=`{q1:.2f}` | Q3=`{q3:.2f}` | IQR=`{iqr:.2f}`\n"
            f"- **Mínimo**: `{sorted_nums[0]:.2f}` | **Máximo**: `{sorted_nums[-1]:.2f}`\n"
            f"- **Outliers Detectados**: `{len(outliers)}` ({outliers[:4] if outliers else 'Ninguno'})\n"
        )

    # -------------------------------------------------------------------------
    # 2. Linear Regression & Forecasting
    # -------------------------------------------------------------------------

    def linear_regression(self, x_vals: List[float], y_vals: List[float], predict_x: Optional[float] = None) -> str:
        """
        Fits an OLS Linear Regression: y = alpha + beta * x
        Computes R², MSE, RMSE and predicts target value if requested.
        """
        if len(x_vals) != len(y_vals) or len(x_vals) < 2:
            return "Se requieren al menos 2 pares de coordenadas (X, Y) con la misma longitud."

        n = len(x_vals)
        mean_x = sum(x_vals) / n
        mean_y = sum(y_vals) / n

        ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_vals, y_vals))
        ss_xx = sum((x - mean_x) ** 2 for x in x_vals)
        ss_yy = sum((y - mean_y) ** 2 for y in y_vals)

        if ss_xx == 0:
            return "La varianza de X es cero; no es posible ajustar una recta de regresión."

        beta = ss_xy / ss_xx
        alpha = mean_y - (beta * mean_x)

        # R² and MSE
        y_preds = [alpha + beta * x for x in x_vals]
        ss_res = sum((y - y_p) ** 2 for y, y_p in zip(y_vals, y_preds))
        r_squared = 1.0 - (ss_res / ss_yy) if ss_yy > 0 else 1.0
        mse = ss_res / n
        rmse = math.sqrt(mse)

        # Pearson correlation r
        r = math.sqrt(max(0.0, r_squared)) if beta >= 0 else -math.sqrt(max(0.0, r_squared))

        lines = [
            "### 📈 Modelo de Regresión Lineal (OLS)",
            f"- **Muestra analizada**: `{n} observaciones`",
            f"- **Ecuación del Modelo**: $$\\hat{{Y}} = {alpha:.4f} + {beta:.4f} \\cdot X$$\n",
            "#### 1. Métricas de Bondad de Ajuste y Rendimiento",
            f"- **Coeficiente de Determinación ($R^2$)**: `{r_squared:.4f}` ({r_squared * 100:.2f}% de la variabilidad explicada)",
            f"- **Coeficiente de Correlación de Pearson ($r$)**: `{r:.4f}` ({'Fuerte positiva' if r > 0.7 else ('Fuerte negativa' if r < -0.7 else 'Moderada/Débil')})",
            f"- **Error Cuadrático Medio ($MSE$)**: `{mse:.4f}`",
            f"- **Raíz del Error Cuadrático Medio ($RMSE$)**: `{rmse:.4f}`\n"
        ]

        if predict_x is not None:
            pred_y = alpha + beta * float(predict_x)
            lines.extend([
                "#### 2. Pronóstico Específico",
                f"- **Para un valor de X = {predict_x}**, el valor proyectado de **$$\\hat{{Y}}$$** es: **`${pred_y:,.2f}`**"
            ])

        lines.extend([
            "",
            "> **Interpretación para Santiago:** Por cada unidad que se incremente la variable independiente $X$, "
            f"la variable dependiente $Y$ varía en promedio **{beta:.4f}** unidades. "
            f"El modelo tiene una precisión explicativa del **{r_squared*100:.1f}%**."
        ])
        return "\n".join(lines)

    def time_series_forecast(self, values: List[float], periods_ahead: int = 3, alpha: float = 0.3) -> str:
        """
        Forecasts future values using Simple Exponential Smoothing (SES) and Moving Average.
        """
        if len(values) < 3:
            return "Se requieren al menos 3 períodos históricos para proyectar una serie temporal."

        n = len(values)
        # 1. Moving average (last 3 periods)
        ma_3 = sum(values[-3:]) / 3.0

        # 2. Simple exponential smoothing
        smoothed = [values[0]]
        for t in range(1, n):
            s_t = alpha * values[t] + (1 - alpha) * smoothed[-1]
            smoothed.append(s_t)

        forecast_val = smoothed[-1]
        diff = values[-1] - values[0]
        trend = "Creciente / Alcista" if diff > 0 else ("Decreciente / Bajista" if diff < 0 else "Estable / Plana")

        lines = [
            f"### ⏱️ Pronóstico de Series de Tiempo (Forecasting)",
            f"- **Datos Históricos**: `{n} períodos` | **Tendencia General**: `{trend}`",
            f"- **Media Móvil Reciente (3 períodos)**: `${ma_3:,.2f}`",
            f"- **Factor de Suavizamiento ($\alpha$)**: `{alpha}`\n",
            "| Período Proyectado | Pronóstico Suavizado (SES) | Pronóstico Media Móvil |",
            "| :---: | :---: | :---: |"
        ]

        for p in range(1, periods_ahead + 1):
            lines.append(f"| **t + {p}** | `${forecast_val:,.2f}` | `${ma_3:,.2f}` |")

        lines.extend([
            "",
            f"> **Nota de Decisión para Santiago:** La serie muestra un comportamiento {trend.lower()}. "
            "Para series con marcada estacionalidad trimestral o mensual, se sugiere aplicar descomposición estacional Holt-Winters."
        ])
        return "\n".join(lines)

    # -------------------------------------------------------------------------
    # 3. Python Code Generation for ML
    # -------------------------------------------------------------------------

    def generate_ml_python_script(self, task: str = "classification") -> str:
        """Generates clean, production-grade Python script for Data Science & ML."""
        task_clean = task.lower().strip()
        if "regres" in task_clean:
            return """# Script de Machine Learning: Regresión con Scikit-Learn
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

# 1. Carga y preparación de datos
df = pd.read_csv('dataset.csv')
X = df.drop(columns=['target_variable'])
y = df['target_variable']

# 2. Partición Train / Test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Escalado
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 4. Entrenamiento
model = Ridge(alpha=1.0)
model.fit(X_train_scaled, y_train)

# 5. Evaluación
y_pred = model.predict(X_test_scaled)
print(f"R² Score: {r2_score(y_test, y_pred):.4f}")
print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.4f}")
"""
        elif "cluster" in task_clean:
            return """# Script de Machine Learning: Segmentación K-Means
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

df = pd.read_csv('clientes.csv')
features = df[['recencia', 'frecuencia', 'valor_monetario']]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(features)

# Búsqueda del K óptimo
for k in range(2, 6):
    km = KMeans(n_clusters=k, random_state=42, n_init='auto')
    labels = km.fit_predict(X_scaled)
    sil = silhouette_score(X_scaled, labels)
    print(f"Clusters: {k} | Silhouette Score: {sil:.4f}")
"""
        else:
            return """# Script de Machine Learning: Clasificación con Random Forest
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

df = pd.read_csv('datos.csv')
X = df.drop(columns=['etiqueta'])
y = df['etiqueta']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
clf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
clf.fit(X_train, y_train)

preds = clf.predict(X_test)
print(classification_report(y_test, preds))
"""


# Global Singleton
data_ml_service = DataMLService()
