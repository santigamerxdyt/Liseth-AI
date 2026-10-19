---
name: data-ml-toolkit
description: >
  Data science, automated dataset cleaning, exploratory data analysis (EDA), statistical testing,
  and machine learning modeling (linear regression, time series forecasting, K-means clustering).
  Generates reproducible Python (Pandas/Scikit-Learn) and analytical SQL code.
license: MIT
metadata:
  version: "1.0.0"
  author: "Liseth AI"
---

# Data & Machine Learning Toolkit Skill

## Overview
The `data-ml-toolkit` skill provides automated exploratory data analysis, dataset cleaning, outlier detection, statistical hypothesis testing, and machine learning models for decision making.

## Core Capabilities
1. **Automated Data Profiling & Cleaning (`clean_profile`)**:
   - Detects missing values, duplicated records, data types, and cardinality.
   - Outlier detection using the Interquartile Range (IQR) rule ($Q_1 - 1.5 \cdot IQR, Q_3 + 1.5 \cdot IQR$) and Z-score ($|Z| > 3.0$).
2. **Correlation & Descriptive Statistics (`stats_correlation`)**:
   - Computes Pearson and Spearman correlation matrices.
   - Computes Mean, Median, Mode, Variance, Standard Deviation, Skewness, and Kurtosis.
3. **Linear Regression & Forecasting (`regression_forecast`)**:
   - Simple & Multiple Linear Regression: Slope ($\beta$), Intercept ($\alpha$), Coefficient of Determination ($R^2$), $MSE$, and $RMSE$.
   - Time Series Forecasting: Simple Exponential Smoothing, Holt-Winters trend estimation, and Moving Averages.
4. **Clustering & Segmentation (`clustering`)**:
   - K-Means clustering algorithm: Centroid initialization, distance metrics, cluster distribution, and feature importance.
5. **Code Generation (`generate_code`)**:
   - Produces clean, documented Python code (Pandas, NumPy, Scikit-Learn) and SQL queries.
