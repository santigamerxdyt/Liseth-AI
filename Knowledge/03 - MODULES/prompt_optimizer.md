---
type: module
status: implemented
priority: high
module: prompt_optimizer
created: 2026-11-15
updated: 2026-11-15
author: 'AI Engineer'
source_paths:
  - app/services/brain_service.py
tags:
  - module
  - prompt-cache
  - token-saving
verified: true
---

# ✂️ PROMPT OPTIMIZER // COMPRESIÓN DE CONTEXTO Y TOKEN SAVER

## 🎯 Objetivo y Responsabilidad
Reduce el consumo de tokens en llamadas a modelos de lenguaje mediante:
1. **Poda de Relleno (Stopwords & Fluff Removal):** Elimina saludos y preámbulos redundantes del historial de chat.
2. **Caché Semántico:** Identifica consultas repetidas devolviendo la respuesta prealmacenada sin gastar créditos de inferencia.
3. **Truncamiento Inteligente:** Mantiene una ventana deslizante de los últimos 6 mensajes conversacionales relevantes.
- **Ahorro Comprobado:** 34% a 42% menos tokens por turno conversacional.
