---
type: payments-doc
status: implemented
priority: high
created: 2026-11-15
updated: 2026-11-15
author: 'SaaS Lead'
source_paths:
  - app/services/saas_service.py
tags:
  - subscriptions
  - lifecycle
  - recurring
verified: true
---

# 🔄 SUBSCRIPTION LIFECYCLE // CICLO DE VIDA DE LA SUSCRIPCIÓN

Controla los estados de las suscripciones:
- `trialing` -> `active` -> `past_due` -> `canceled`.
- Acreditación automática de créditos al renovar el ciclo mensual y suspensión del acceso cognitivo si la factura vence impaga.
