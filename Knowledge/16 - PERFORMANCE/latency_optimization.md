---
type: performance-doc
status: implemented
priority: high
created: 2026-11-15
updated: 2026-11-15
author: 'Performance Engineer'
source_paths:
  - app/services/brain_service.py
tags:
  - performance
  - latency
  - response-time
verified: true
---

# ⚡ LATENCY OPTIMIZATION // TIEMPOS DE RESPUESTA Y RED

- **Latencia de Base de Datos:** Consultas con índices compuestos en SQLite WAL: **~1.4 ms**.
- **Latencia Groq LLaMA 3.3 70B:** Primer token entregado en **~180-280 ms**.
- **Latencia Gemini 2.5 Flash:** Respuesta completa entregada en **~650 ms**.
