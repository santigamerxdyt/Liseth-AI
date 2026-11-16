---
type: security-doc
status: implemented
priority: critical
created: 2026-11-15
updated: 2026-11-15
author: 'Security Lead'
source_paths:
  - app/main.py
tags:
  - security
  - creator
  - superadmin
verified: true
---

# 👑 CREATOR PROTECTION // BLINDAJE EXCLUSIVO DEL PROPIETARIO

- **Identidad del Propietario:** **Señor Santiago Huérfano López** (`@NEQUISAN243100`).
- **Rutas Restringidas:** `/api/brain/soul` y `/api/admin/*` son interceptadas directamente por el middleware antes de cualquier procesamiento Pydantic, garantizando que nadie sin el flag verificado de Creator pueda acceder o modificar la personalidad de Liseth.
