---
type: workflow
status: active
priority: high
created: 2026-11-15
updated: 2026-11-15
author: 'Software Architect'
tags:
  - workflow
  - impact-analysis
  - risk-assessment
verified: true
---

# ⚡ RUNBOOK: ANÁLISIS DE IMPACTO DE CÓDIGO (CODE IMPACT ANALYSIS)

> Guía obligatoria para evaluar el radio de afectación antes de modificar componentes nucleares en **Liseth AI Core**.

## Matriz de Impacto por Componente

| Componente a Modificar | Nivel de Riesgo | Áreas Potencialmente Afectadas | Pruebas Obligatorias |
| :--- | :--- | :--- | :--- |
| `app/models/saas.py` | **CRÍTICO** | Base de datos SQLite, migraciones, ledger, BOLA | `test_saas_features.py` (Suite completa) |
| `app/services/saas_service.py` | **CRÍTICO** | Pasarelas de pago, créditos, cifrado de llaves | `test_checkout_subscription`, `test_ledger` |
| `app/main.py` (Middlewares) | **ALTO** | Autenticación, CORS, cabeceras seguras, rate limit | `test_auth.py`, `test_security_headers` |
| `app/services/brain_service.py` | **ALTO** | Enrutador cognitivo, memoria semántica, tokens | `test_brain_routing.py` |
| `index.html` (Cyber-HUD) | **MEDIO** | Three.js particle orb, modal de onboarding, NFC | Pruebas visuales y de interacción |
