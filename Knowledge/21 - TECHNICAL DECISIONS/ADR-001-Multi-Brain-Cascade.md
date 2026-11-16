---
type: adr
status: approved
priority: critical
created: 2026-10-15
updated: 2026-11-15
author: 'Chief Technology Officer'
tags:
  - adr
  - architecture
  - multi-brain
  - cascade
verified: true
---

# 🏛️ ADR-001: Cascada Cognitiva Híbrida Multi-Proveedor

## Estado
**APROBADO E IMPLEMENTADO**

## Contexto y Problema
Depender de un único proveedor de Inteligencia Artificial (por ejemplo, únicamente OpenAI o Anthropic) genera un riesgo crítico de punto único de falla (Single Point of Failure), expone la plataforma a caídas del servicio, impone costes elevados por llamada (hasta \$30 USD / 1M tokens) y limita la agilidad en respuestas conversacionales simples donde la latencia es primordial.

## Alternativas Evaluadas
1. **Proveedor Único (Solo OpenAI GPT-4o):** Sencillo de implementar, pero con costes mensuales elevados y dependencia total de su infraestructura.
2. **Modelos Locales On-Premise (Ollama / vLLM):** Privacidad máxima, pero consumo prohibitivo de memoria GPU en máquinas de desarrollo y baja capacidad en dispositivos móviles.
3. **Cascada Híbrida Inteligente (Google + Groq + Anthropic + OpenAI):** Orquestación heurística basada en la complejidad de la tarea y el presupuesto de tokens.

## Decisión Tomada
Se adoptó la **Cascada Cognitiva Híbrida**:
- **Groq (LLaMA 3.3 70B):** Para tareas de baja latencia (<400ms), chat conversacional fluido y consultas de código rápido.
- **Google Cloud (Gemini 2.5 / 3.8 Flash):** Como cerebro principal por su inmensa ventana de contexto (1M tokens) y coste ultracompetitivo (\$0.075 / 1M).
- **Anthropic (Claude 3.5 Sonnet):** Para razonamiento crítico, arquitectura de software y análisis de seguridad.
- **OpenAI (GPT-4o):** Como fallback de contingencia.

## Justificación
Permite garantizar una disponibilidad del 99.9%, reduce el costo operativo de inferencia en un **68%** en comparación con un stack monomoderador y ofrece una experiencia de usuario inmediata en el Cyber-HUD.

## Consecuencias y Verificación
- **Consecuencias Positivas:** Flexibilidad económica y resistencia a fallas.
- **Consecuencias a Gestionar:** Necesidad de mantener compatibilidad con las diferentes APIs y gestionar cuotas por proveedor.
- **Archivo Fuente:** [app/services/brain_service.py](file:///c:/Users/Usuario/Desktop/MI%20LISEHT/app/services/brain_service.py)
