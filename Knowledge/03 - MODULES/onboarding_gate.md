---
type: module
status: implemented
priority: critical
module: onboarding_gate
created: 2026-11-15
updated: 2026-11-15
author: 'Security & Product Lead'
source_paths:
  - app/routers/saas_router.py
  - index.html
tags:
  - module
  - gate
  - onboarding
  - protection
verified: true
---

# 🚪 ONBOARDING GATE GUARD // BARRERA DE ACTIVACIÓN OBLIGATORIA

## 🎯 Objetivo y Responsabilidad
Impide el uso no autorizado de la plataforma asegurando que ningún usuario pueda cerrar el modal de planes ni realizar peticiones cognitivas sin haber cumplido:
1. Crear cuenta y vincular credenciales en Google Firebase.
2. Ingresar y cifrar sus API Keys de cerebros de IA.
3. Completar el pago o activación de un plan de suscripción formal.
- Ver [[ADR-005-Onboarding-Gate]].
