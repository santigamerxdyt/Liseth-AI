---
type: ai-doc
status: implemented
priority: critical
created: 2026-11-15
updated: 2026-11-15
author: 'AI Architect'
source_paths:
  - app/services/brain_service.py
tags:
  - ai
  - providers
  - models
verified: true
---

# 🤖 PROVIDERS & MODELS // INVENTARIO DE CAPACIDADES DE INTELIGENCIA ARTIFICIAL

## 1. Google Cloud — Gemini 2.5 & 3.8 Flash
- **Ventana:** 1,000,000 tokens.
- **Fortaleza:** Procesamiento masivo de contexto, ingesta de PDFs, imágenes, audio y síntesis analítica.
- **Costo:** \$0.075 a \$0.150 USD por millón de tokens de entrada.

## 2. Groq Cloud — LLaMA 3.3 70B Versatile
- **Ventana:** 128,000 tokens.
- **Fortaleza:** Inferencia LPUs ultrarrápida (260 tokens/segundo, latencia ~180ms).
- **Costo:** \$0.59 USD input / \$0.79 USD output por millón.

## 3. Anthropic — Claude 3.5 Sonnet
- **Ventana:** 200,000 tokens.
- **Fortaleza:** Máximo nivel de razonamiento arquitectónico, refactorización de código y análisis formal.
- **Costo:** \$3.00 USD input / \$15.00 USD output por millón.

## 4. OpenAI — GPT-4o
- **Ventana:** 128,000 tokens.
- **Fortaleza:** Fallback de respaldo universal.
