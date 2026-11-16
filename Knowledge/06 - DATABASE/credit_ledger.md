---
type: database-doc
status: implemented
priority: critical
created: 2026-11-15
updated: 2026-11-15
author: 'Financial Systems Lead'
source_paths:
  - app/models/saas.py
tags:
  - database
  - ledger
  - accounting
  - immutability
verified: true
---

# 📘 SAAS CREDIT LEDGER // LIBRO CONTABLE INMUTABLE DE CRÉDITOS

## 📐 Estructura de Registro
Cada operación financiera crea una nueva entrada inmutable:
- `id` (UUIDv4)
- `user_id` (Clave foránea hacia `saas_users.id`)
- `delta` (Entero con signo: positivo para compras/referidos, negativo para deducciones de uso)
- `balance_after` (Saldo verificado posterior a la transacción)
- `reason` (`subscription_grant`, `ai_query_cost`, `referral_reward`, `nfc_p2p_transfer`)
- `meta` (JSON con detalles del modelo, tokens gastados o pasarela de pago)
- `created_at` (Timestamp UTC)
- Ver [[ADR-004-Immutable-Credit-Ledger]].
