---
type: backend
status: implemented
priority: critical
created: 2026-11-15
updated: 2026-11-15
author: 'Cybersecurity Engineer'
source_paths:
  - app/core/auth.py
tags:
  - backend
  - auth
  - pbkdf2
  - scrypt
verified: true
---

# 🔐 AUTH ENGINE // AUTENTICACIÓN Y GESTIÓN DE SESIONES

## 🛡️ Algoritmos y Procedimientos
- **Contraseñas:** PBKDF2 con HMAC-SHA256 y 100,000 rondas. Sal criptográfica aleatoria de 32 bytes.
- **PIN Creador:** Derivación robusta con `scrypt` resistente a GPUs.
- **Revocación Inmediata:** Al invocar `/api/auth/logout`, el token actual es insertado en `saas_revoked_tokens` invalidando cualquier uso posterior.
