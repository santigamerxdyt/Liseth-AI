---
type: backend
status: implemented
priority: critical
created: 2026-11-15
updated: 2026-11-15
author: 'Software Architect'
source_paths:
  - app/main.py
tags:
  - backend
  - fastapi
  - middleware
  - architecture
verified: true
---

# ⚡ FASTAPI ARCHITECTURE // NÚCLEO ASÍNCRONO DEL BACKEND

## 📐 Pipeline de Middlewares
1. **SecurityHeadersMiddleware:** Inyección de `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`.
2. **RateLimitMiddleware:** Protección de fuerza bruta en autenticación y limitación de DoS.
3. **ApiAuthMiddleware:** Validación de Bearer Token, consulta de lista negra `saas_revoked_tokens` y verificación de pertenencia de tenant.
- **Punto de Entrada:** [app/main.py](file:///c:/Users/Usuario/Desktop/MI%20LISEHT/app/main.py)
