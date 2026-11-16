---
type: changelog
status: active
priority: medium
created: 2026-11-15
updated: 2026-11-15
author: 'Release Manager'
tags:
  - changelog
  - releases
  - versions
verified: true
---

# 📢 RELEASE CHANGELOG // HISTORIAL DE VERSIONES

## [v3.8.0] - 2026-11-15 (Enterprise Hardened + Obsidian Vault Engine)
### Añadido:
- Integración completa del Vault Inteligente de Obsidian con 26 dominios técnicos en `Knowledge/`.
- 6 Mapas de Contenido (MOCs) especializados y Centro de Mando `PROJECT COMMAND CENTER.md`.
- Puerta obligatoria de Onboarding: Bloqueo de navegación hasta enlazar Firebase, suministrar API Keys de IA y activar plan pagado.
- Cifrado autenticado AES-256-GCM para llaves de cerebros de cada usuario.
- 18 índices compuestos en SQLite y activación de modo WAL.
- Protocolo de 5 niveles de recuperación de contexto para Antigravity.

### Corregido:
- Corregida barra flotante inferior derecha en el Cyber-HUD.
- Corregido `ImportError: _extract_token` en `saas_router.py`.
- Corregido `NameError: applied_promo` en `saas_service.py`.
- Corregida asincronía en llamadas a `record_credit_ledger`.
- Mitigada vulnerabilidad BOLA en descargas de archivos.
- 438 tests de pytest pasando al 100% sin regresiones.
