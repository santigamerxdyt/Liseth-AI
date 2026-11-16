---
type: api-doc
status: implemented
priority: high
created: 2026-11-15
updated: 2026-11-15
author: 'Integration Specialist'
source_paths:
  - app/routers/saas_router.py
tags:
  - api
  - webhooks
  - payments
verified: true
---

# 🪝 WEBHOOKS & PAYMENT GATEWAYS // RECEPTOR DE EVENTOS ASÍNCRONOS

## 🇨🇴 Integración Nacional: Bre-B y Nequi
- **Identificador Bre-B:** Llave interbancaria `@NEQUISAN243100`.
- **Nequi Oficial:** Cuenta oficial `3122376474` a nombre de **Santiago Huérfano López**.
- **Validación:** El webhook procesa el comprobante digital o notificación bancaria y acredita atómicamente los créditos en el [[credit_ledger]].

## 🌎 Integración Internacional: Stripe & PayPal
- **Eventos Monitoreados:** `checkout.session.completed`, `invoice.payment_succeeded`, `customer.subscription.deleted`.
- **Idempotencia:** Cada `event_id` se registra para evitar doble acreditación de créditos ante reintentos de red.
