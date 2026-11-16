---
type: incident-registry
status: active
priority: medium
created: 2026-11-15
updated: 2026-11-15
author: 'DevOps & SRE'
tags:
  - incidents
  - postmortem
  - sre
verified: true
---

# 🚨 REGISTRO DE INCIDENTES ACTIVOS Y LIMITACIONES CONOCIDAS

| ID | Incidencia / Limitación | Estado | Nivel de Riesgo | Mitigación Actual |
| :--- | :--- | :--- | :--- | :--- |
| `LIM-01` | Web NFC API no expuesta en navegadores Desktop (Windows/Mac) | `Conocida / Mitigada` | Bajo | Modo emulador virtual activado automáticamente en PC. |
| `LIM-02` | Cuota de tokens por minuto en Groq Cloud (TPM/RPM) | `Mitigada` | Medio | Fallback automático a Gemini 2.5 Flash ante error HTTP 429. |
| `LIM-03` | Conexión inicial de SQLite sin WAL | `Resuelta` | Alto | `PRAGMA journal_mode=WAL` activado en el arranque de la app. |
