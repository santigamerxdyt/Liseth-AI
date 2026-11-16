---
type: referrals-doc
status: implemented
priority: critical
created: 2026-11-15
updated: 2026-11-15
author: 'Cybersecurity Specialist'
source_paths:
  - app/services/saas_service.py
tags:
  - referrals
  - anti-fraud
  - anti-sybil
verified: true
---

# 🛡️ ANTI-FRAUD ENGINE // BLINDAJE CONTRA ABUSO DE REFERIDOS

- **Prohibición de Auto-Referencia:** El sistema detecta y bloquea si el usuario intenta referirse a sí mismo.
- **Condición de Pago Exitoso:** Las recompensas quedan en estado `pending` hasta que la pasarela confirme el cobro real de fondos.
