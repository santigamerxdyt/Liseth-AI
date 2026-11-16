---
type: database
status: active
priority: critical
created: 2026-11-15
updated: 2026-11-15
author: 'Chief Technology Officer'
tags:
  - database
  - decisions
  - adr
  - architecture
verified: true
---

# 🏛️ DECISIONS DATABASE // REGISTRO MAESTRO DE DECISIONES TÉCNICAS (ADRs)

> Índice central de los Architectural Decision Records (ADRs) adoptados para garantizar la estabilidad, escalabilidad, rentabilidad y seguridad de **Liseth AI Core**.

| ID ADR | Título de la Decisión Técnica | Estado | Fecha de Adopción | Componentes Impactados | Justificación Principal |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **[[ADR-001-Multi-Brain-Cascade]]** | Cascada Cognitiva Híbrida Multi-Proveedor | `Aprobado` | 2026-10-15 | `brain_service.py`, Enrutador | Reducción de 68% en costes de inferencia y latencia <400ms |
| **[[ADR-002-SQLite-WAL-Indexes]]** | SQLite en modo WAL con 18 Índices Compuestos | `Aprobado` | 2026-10-20 | `app/database/`, `app.db` | Cero bloqueos de concurrencia y consultas BOLA en <2ms |
| **[[ADR-003-AES256GCM-Tenant-Keys]]** | Cifrado Autenticado AES-256-GCM para Llaves IA | `Aprobado` | 2026-11-01 | `saas_service.py`, BD | Cumplimiento Zero-Knowledge y confidencialidad multi-tenant |
| **[[ADR-004-Immutable-Credit-Ledger]]** | Libro Mayor Inmutable de Doble Entrada | `Aprobado` | 2026-11-05 | `saas.py`, `saas_service.py` | Auditabilidad financiera estricta y protección anti-manipulación |
| **[[ADR-005-Onboarding-Gate]]** | Puerta Obligatoria de Firebase + API Key + Pago | `Aprobado` | 2026-11-12 | `index.html`, `saas_router.py` | Eliminación de usuarios parásitos y rentabilidad SaaS garantizada |
| **[[ADR-006-Web-NFC-Hardware]]** | Integración Web NFC con Fallback Emulado | `Aprobado` | 2026-11-14 | `index.html`, NFC Hub | Compatibilidad dual: hardware móvil real y emulador de escritorio |
