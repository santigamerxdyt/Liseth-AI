---
type: security-doc
status: implemented
priority: critical
created: 2026-11-15
updated: 2026-11-15
author: 'Cybersecurity Engineer'
source_paths:
  - app/routers/
tags:
  - security
  - multi-tenant
  - bola-defense
verified: true
---

# 🛡️ TENANT ISOLATION // AISLAMIENTO Y DEFENSA CONTRA ATAQUES BOLA

1. **Principio de Mínimo Privilegio:** Ninguna consulta SQL selecciona registros sin incluir la condición explícita `WHERE user_id = current_user.id`.
2. **Defensa contra IDOR/BOLA:** Si un usuario malicioso intenta solicitar `/api/conversations/{id}` o `/api/files/{id}` perteneciente a otro usuario, el sistema responde con `403 Forbidden` o `404 Not Found` registrando el intento en el log de auditoría.
3. **Verificación Automatizada:** Suite de pruebas con el caso `test_multitenant_file_isolation_bola_protection` aprobado.
