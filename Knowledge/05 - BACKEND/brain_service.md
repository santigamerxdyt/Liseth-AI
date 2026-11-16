---
type: backend
status: implemented
priority: critical
created: 2026-11-15
updated: 2026-11-15
author: 'AI Backend Lead'
source_paths:
  - app/services/brain_service.py
tags:
  - backend
  - brain-service
  - ai-orchestration
verified: true
---

# 🧠 BRAIN SERVICE // ORQUESTADOR MULTI-CEREBRO

## ⚙️ Módulos de Servicio
- **`generate_response(prompt, user_id, provider)`:** Coordina la llamada HTTP/SDK asíncrona hacia el proveedor correspondiente descifrando previamente las credenciales del usuario con AES-256-GCM.
- **Gestión de Errores 429:** Implementa retroceso exponencial y salto inmediato al cerebro secundario.
