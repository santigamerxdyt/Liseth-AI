---
type: database
status: active
priority: high
created: 2026-11-15
updated: 2026-11-15
author: 'QA Automation Engineer'
tags:
  - database
  - bugs
  - security
  - postmortem
verified: true
---

# 🐛 BUGS & INCIDENTS DATABASE // REGISTRO DE DEFECTOS Y VULNERABILIDADES

> Registro histórico y vivo de incidencias de software, vulnerabilidades de seguridad mitigadas y defectos resueltos en el ecosistema **Liseth AI Core**.

| ID Incidencia | Título / Defecto | Severidad | Módulo Afectado | Causa Raíz | Estado | Prueba de Verificación |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `BUG-001` | Flotante HUD roto en esquina inferior derecha | `Medium` | Frontend HUD | Conflicto de posicionamiento CSS `fixed` y `z-index` | **`SOLUCIONADO`** | Verificado en navegador |
| `BUG-002` | `ImportError: _extract_token` en saas_router | `Critical` | `saas_router.py` | Import obsoleto; reemplazado por `extract_token_from_request` | **`SOLUCIONADO`** | `test/test_saas_features.py` |
| `BUG-003` | `NameError: applied_promo` en checkout | `High` | `saas_service.py` | Variable renombrada a `applied_promo_code` sin actualizar scope | **`SOLUCIONADO`** | `test_checkout_subscription` |
| `BUG-004` | Falta `await` en llamadas a `record_credit_ledger` | `Critical` | `saas_service.py` | Corrutina asíncrona invocada como llamada sincrónica | **`SOLUCIONADO`** | `test_ledger_immutability` |
| `BUG-005` | Discrepancia en formato cifrado API Key (`iv:tag:ct`)| `Critical` | `saas_service.py` | Falta de prefijo de versión canónica `v1:` | **`SOLUCIONADO`** | `test_user_registration` |
| `BUG-006` | Vulnerabilidad BOLA en descarga de archivos | `Critical` | `saas_router.py` | Consulta permitía descargar archivo de otro tenant sin validar `user_id`| **`SOLUCIONADO`** | `test_multitenant_file_isolation` |
| `BUG-007` | Fuga de esquema Pydantic en `/api/brain/soul` | `High` | `app/main.py` | Pydantic validaba antes que el middleware de autorización | **`SOLUCIONADO`** | `test_unauthorized_soul` |
| `BUG-008` | Falla intermitente en tests por bloqueo SQLite | `High` | `app/database/` | Concurrencia sin WAL activado (`database is locked`) | **`SOLUCIONADO`** | `pytest test/ -q` (438 tests) |
