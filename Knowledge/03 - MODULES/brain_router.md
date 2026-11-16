---
type: module
status: implemented
priority: critical
module: brain_router
created: 2026-11-15
updated: 2026-11-15
author: 'AI Systems Lead'
source_paths:
  - app/services/brain_service.py
tags:
  - module
  - router
  - llm-cascade
verified: true
---

# 🔀 COGNITIVE BRAIN ROUTER // ENRUTADOR DINÁMICO DE CEREBROS

## 🎯 Objetivo y Responsabilidad
Evalúa la complejidad semántica de la consulta del usuario y selecciona el mejor proveedor:
- Consultas simples / chat interactivo: **Groq LLaMA 3.3 70B** (Respuesta inmediata).
- Documentos largos / análisis de datos: **Google Gemini 2.5 / 3.8 Flash** (1M contexto).
- Tareas de código complejas / arquitectura: **Anthropic Claude 3.5 Sonnet**.
- Errores 429 de cuota: Traspaso transparente al siguiente modelo de la cascada.
- Ver [[ADR-001-Multi-Brain-Cascade]].
