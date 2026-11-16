---
type: ai-doc
status: implemented
priority: high
created: 2026-11-15
updated: 2026-11-15
author: 'AI Performance Lead'
source_paths:
  - app/services/brain_service.py
tags:
  - ai
  - tokens
  - optimization
  - cache
verified: true
---

# 📉 TOKEN OPTIMIZATION // POLÍTICA DE AHORRO Y CACHÉ SEMÁNTICO

1. **Semantic Prompt Caching:** Las consultas repetitivas de estado, bienvenida o consultas frecuentes se almacenan con TTL de 24 horas.
2. **Eliminación de Preámbulos:** El optimizador recorta las frases de cortesía innecesarias ahorrando un 25-35% de tokens por intercambio.
3. **Modo Bajo Consumo en HUD:** Permite al usuario limitar la respuesta a concisión ejecutiva extrema.
