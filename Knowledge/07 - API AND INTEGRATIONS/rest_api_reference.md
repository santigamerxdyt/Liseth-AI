---
type: api-doc
status: implemented
priority: critical
created: 2026-11-15
updated: 2026-11-15
author: 'Backend Lead'
source_paths:
  - app/routers/
tags:
  - api
  - rest
  - endpoints
verified: true
---

# 🌐 REST API SPECIFICATION // REFERENCIA MAESTRA DE ENDPOINTS

## 🔐 Endpoints de Autenticación (`/api/auth`)
- `POST /api/auth/register`: Registro de nuevos usuarios con hash PBKDF2 y cifrado de llaves AES-256-GCM.
- `POST /api/auth/login`: Autenticación con credenciales, validación contra fuerza bruta y retorno de Bearer Token.
- `POST /api/auth/logout`: Revocación inmediata del token actual con registro en `saas_revoked_tokens`.
- `GET /api/auth/me`: Retorna el perfil del usuario autenticado, rol, créditos disponibles y estado de onboarding.

## 💳 Endpoints SaaS y Pagos (`/api/saas`)
- `GET /api/saas/plans`: Catálogo público de planes de suscripción (FREE, STARTER, PRO, BUSINESS, ENTERPRISE).
- `POST /api/saas/checkout`: Creación de orden de suscripción, aplicación de códigos de promoción y redirección a pasarela.
- `GET /api/saas/credits`: Historial auditable de movimientos del usuario extraído de `saas_credit_ledger`.
- `GET /api/saas/referrals`: Estadísticas de invitados, comisiones acumuladas y enlace único de referidos.
- `POST /api/saas/keys`: Actualización y rotación segura de API keys de IA personales cifradas en reposo.

## 🧠 Endpoints Cognitivos (`/api/brain`)
- `POST /api/brain/chat`: Envío de mensaje conversacional; despacha al modelo seleccionado a través del [[brain_router]].
- `GET /api/brain/history`: Recuperación de conversaciones previas aisladas por tenant.
- `POST /api/brain/soul`: Endpoint de administración de personalidad reservado **exclusivamente al Superadmin CREATOR**.

## 📶 Endpoints Contactless NFC (`/api/nfc`)
- `POST /api/nfc/exchange`: Procesamiento y validación de transferencias de créditos P2P por radiofrecuencia.
- `GET /api/nfc/card/{card_id}`: Resolución de vCard pública 4.0 para tarjetas de visita ejecutivas.
