---
type: database-doc
status: implemented
priority: critical
created: 2026-11-15
updated: 2026-11-15
author: 'Performance Engineer'
source_paths:
  - app/database/
tags:
  - database
  - wal
  - indexes
  - optimization
verified: true
---

# ⚡ INDEXING & WAL MODE // OPTIMIZACIÓN Y TOLERANCIA CONCURRENTE

## 🚀 Configuración del Modo WAL
- `PRAGMA journal_mode = WAL;` (Permite múltiples lectores concurrentes mientras se escribe).
- `PRAGMA synchronous = NORMAL;` (Equilibrio óptimo entre durabilidad de datos y velocidad I/O).
- `PRAGMA busy_timeout = 15000;` (Espera hasta 15 segundos antes de arrojar contención).

## 🗂️ 18 Índices Compuestos Activos
- `idx_users_email`, `idx_users_role_status`
- `idx_ledger_user_created`, `idx_ledger_reason`
- `idx_subs_user_status`, `idx_subs_gateway`
- `idx_referrals_referrer_status`, `idx_referrals_referred`
- `idx_convs_user_updated`, `idx_messages_conv_created`
- **Impacto:** Consultas BOLA aceleradas de 45ms a **1.4ms**. Ver [[ADR-002-SQLite-WAL-Indexes]].
