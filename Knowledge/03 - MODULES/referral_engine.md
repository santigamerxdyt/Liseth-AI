---
type: module
status: implemented
priority: high
module: referral_engine
created: 2026-11-15
updated: 2026-11-15
author: 'Monetization Engineer'
source_paths:
  - app/services/saas_service.py
tags:
  - module
  - referrals
  - anti-fraud
verified: true
---

# 🎁 REFERRAL FRAUD GUARD // MOTOR ANTI-FRAUDE DE REFERIDOS

## 🎯 Objetivo y Responsabilidad
Calcula y acredita recompensas en créditos del programa viral de referidos:
- Nivel 1: 50% de comisión.
- Nivel 2: 25% de comisión.
- Nivel 3: Upgrade gratuito al plan PRO durante 30 días.
- Nivel 4+: 10% recurrente.
- **Mecanismos Anti-Fraude:** Prohíbe la auto-referenciación (`user_id == referrer_id`) y valida que el pago de la suscripción haya sido confirmado en el gateway antes de otorgar comisiones.
