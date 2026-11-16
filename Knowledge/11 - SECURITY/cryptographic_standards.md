---
type: security-doc
status: implemented
priority: critical
created: 2026-11-15
updated: 2026-11-15
author: 'Cybersecurity Specialist'
source_paths:
  - app/core/auth.py
  - app/services/saas_service.py
tags:
  - security
  - cryptography
  - standards
verified: true
---

# 🔒 CRYPTOGRAPHIC STANDARDS // ESPECIFICACIÓN CRIPTOGRÁFICA EN PRODUCCIÓN

- **Hashing de Contraseñas:** PBKDF2-HMAC-SHA256 con 100,000 rondas y salt criptográfico de 32 bytes (`os.urandom(32)`).
- **Protección PIN Maestro:** scrypt (`N=16384, r=8, p=1`).
- **Cifrado de API Keys:** AES-256-GCM autenticado con tag de integridad de 128 bits. Formato canónico `v1:<nonce>:<tag>:<ciphertext>`.
- Ver [[ADR-003-AES256GCM-Tenant-Keys]].
