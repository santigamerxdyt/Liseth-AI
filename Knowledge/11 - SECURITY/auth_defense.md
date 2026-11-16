---
type: security-doc
status: implemented
priority: critical
created: 2026-11-15
updated: 2026-11-15
author: 'Application Security Specialist'
source_paths:
  - app/main.py
tags:
  - security
  - defense
  - rate-limiting
verified: true
---

# 🛡️ AUTH DEFENSE // PROTECCIÓN CONTRA FUERZA BRUTA Y REVOCACIÓN

1. **Rate Limiting Dinámico:** Bloquea peticiones de login que excedan 5 intentos fallidos por minuto desde la misma IP.
2. **Revocación Instantánea:** Los tokens liquidados al cerrar sesión se insertan en `saas_revoked_tokens` en SQLite. El middleware rechaza cualquier reutilización subsecuente.
