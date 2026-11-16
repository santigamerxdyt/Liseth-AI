---
type: integration-doc
status: implemented
priority: critical
created: 2026-11-15
updated: 2026-11-15
author: 'Cloud Architect'
source_paths:
  - app/services/saas_service.py
tags:
  - integration
  - firebase
  - google-cloud
verified: true
---

# 🔥 FIREBASE INTEGRATION // SINCRONIZACIÓN Y REGLAS DE SEGURIDAD

## 🎯 Política de Control
- El proyecto utiliza Firebase como repositorio cloud y autenticación federada complementaria.
- **Regla Estricta del Creador:** Solo el **Señor Santiago** posee credenciales de administrador para modificar reglas de seguridad en Firestore y Firebase Auth. Los usuarios estándar no pueden alterar la configuración bajo ninguna circunstancia.
- Ver [[ADR-005-Onboarding-Gate]].
