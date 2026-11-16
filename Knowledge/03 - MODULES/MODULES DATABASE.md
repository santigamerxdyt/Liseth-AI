---
type: database
status: active
priority: high
created: 2026-11-15
updated: 2026-11-15
author: 'Software Architect Team'
tags:
  - database
  - modules
  - registry
  - inventory
verified: true
---

# 📦 MODULES DATABASE // INVENTARIO MAESTRO DE MÓDULOS

> Esta base de datos cataloga los 48 módulos HUD y los componentes nucleares de backend y frontend de **Liseth AI Core**, indicando su estado de implementación real, ubicación de código y documentación asociada.

| Módulo / Componente | Dominio | Estado | Criticidad | Ruta Fuente Principal | Documentación Técnica |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Cognitive Brain Router** | Backend | `Implemented` | `Critical` | `app/services/brain_service.py` | [[brain_router]] |
| **Action Dispatcher** | Backend | `Implemented` | `Critical` | `core/action_dispatcher.py` | [[action_dispatcher]] |
| **Multi-Tenant SaaS Engine** | Backend | `Implemented` | `Critical` | `app/services/saas_service.py` | [[saas_engine]] |
| **Onboarding Gate Guard** | Backend/UI | `Implemented` | `Critical` | `app/routers/saas_router.py` | [[onboarding_gate]] |
| **Credit Ledger Contable** | Backend | `Implemented` | `Critical` | `app/models/saas.py` | [[credit_ledger]] |
| **Web NFC Core Engine** | Frontend/HW| `Implemented` | `High` | `index.html` (Línea ~4150) | [[nfc_engine]] |
| **Cyber-HUD WebGL AI Orb** | Frontend | `Implemented` | `High` | `index.html` (Línea ~2200) | [[cyber_hud_architecture]] |
| **Token & Prompt Optimizer**| Backend | `Implemented` | `High` | `app/services/brain_service.py` | [[prompt_optimizer]] |
| **ChromaDB Semantic Memory**| Backend | `Implemented` | `High` | `core/chroma_memory.py` | [[memory_architecture]] |
| **Referral Fraud Guard** | Backend | `Implemented` | `High` | `app/services/saas_service.py` | [[referral_engine]] |
| **Audio Visualizer Web API**| Frontend | `Implemented` | `Medium` | `index.html` (Línea ~3100) | [[audio_visualizer]] |
| **Resource Optimizer & GC** | Backend | `Implemented` | `Medium` | `app/main.py` | [[resource_optimizer]] |
| **PBKDF2/scrypt Auth Guard**| Backend | `Implemented` | `Critical` | `app/core/auth.py` | [[auth_engine]] |
| **AES-256-GCM Vault Key** | Backend | `Implemented` | `Critical` | `app/services/saas_service.py` | [[cryptographic_standards]] |
| **Firebase Cloud Link** | Backend/Cloud| `Implemented` | `High` | `app/services/saas_service.py` | [[firebase_integration]] |
| **Bre-B & Nequi Webhook** | Backend | `Implemented` | `High` | `app/routers/saas_router.py` | [[payment_gateways]] |
