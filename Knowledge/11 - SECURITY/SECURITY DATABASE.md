---
type: database
status: active
priority: critical
created: 2026-11-15
updated: 2026-11-15
author: 'Cybersecurity Engineer'
tags:
  - database
  - security
  - vulnerabilities
  - controls
verified: true
---

# 🛡️ SECURITY DATABASE // MATRIZ DE RIESGOS Y CONTROLES CRIPTOGRÁFICOS

> Catálogo de controles de ciberseguridad, mitigaciones OWASP y políticas criptográficas activas en **Liseth AI Core**.

| Dominio de Seguridad | Amenaza / Vector de Ataque | Control Implementado | Estado | Nivel de Blindaje |
| :--- | :--- | :--- | :--- | :--- |
| **Contraseñas de Usuarios** | Ataques de Diccionario y Fuerza Bruta | PBKDF2-HMAC-SHA256 (100,000 iteraciones + Salt 32 bytes) | `Activo` | Grado Militar |
| **PIN Maestro del Creador** | Craqueo con Clusters GPU/ASIC | Algoritmo computacionalmente costoso `scrypt` | `Activo` | Máximo Aislamiento |
| **Llaves API de Clientes** | Volcado indebido de base de datos | AES-256-GCM autenticado (Nonce 96 bits + Tag 128 bits) | `Activo` | Zero-Knowledge |
| **Aislamiento Multi-Tenant** | Ataques BOLA / IDOR entre usuarios | Inyección obligatoria de `user_id` en cada consulta SQL | `Activo` | Verificado con 438 tests |
| **Gestión de Sesiones** | Reutilización de Tokens (Replay Attacks) | Lista negra persistente en SQLite (`saas_revoked_tokens`) | `Activo` | Revocación Instantánea |
| **Ataques de Denegación (DoS)**| Saturación masiva de endpoints | Rate Limiting por IP y Token con ventana deslizante | `Activo` | Bloqueo Progresivo |
| **Panel Superadmin CREATOR** | Escalamiento horizontal/vertical | Validación de identidad exclusiva de Señor Santiago | `Activo` | Intercepción Middleware |
