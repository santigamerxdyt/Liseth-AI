---
type: database-doc
status: implemented
priority: critical
created: 2026-11-15
updated: 2026-11-15
author: 'Database Architect'
source_paths:
  - app/models/saas.py
tags:
  - database
  - schema
  - sqlalchemy
  - tables
verified: true
---

# 🗄️ DATABASE SCHEMA // MODELO RELACIONAL SAAS Y CONVERSACIONAL

## 📊 Tablas Normalizadas (14 Tablas)
1. `saas_users`: Usuarios, roles, hash de contraseña, API keys cifradas, saldo de créditos.
2. `saas_plans`: Definición de tiers comerciales (FREE a ENTERPRISE) con límites y tarifas.
3. `saas_subscriptions`: Ciclo de facturación activo, pasarela utilizada y estados (`active`, `past_due`, `canceled`).
4. `saas_credit_ledger`: Libro contable inmutable con registros de cargo y abono.
5. `saas_referrals`: Relación jerárquica de referidos, comisiones ganadas y estado de pago.
6. `saas_revoked_tokens`: Registro de tokens invalidados para revocación de sesión.
7. `chat_conversations`: Sesiones de chat con aislamiento estricto por `user_id`.
8. `chat_messages`: Mensajes individuales con conteo de tokens e indicador de modelo.
- **Archivo Fuente:** [app/models/saas.py](file:///c:/Users/Usuario/Desktop/MI%20LISEHT/app/models/saas.py)
