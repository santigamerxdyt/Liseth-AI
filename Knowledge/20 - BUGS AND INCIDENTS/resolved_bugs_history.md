---
type: bugs-history
status: active
priority: high
created: 2026-11-15
updated: 2026-11-15
author: 'QA Automation Lead'
tags:
  - bugs
  - history
  - resolution
verified: true
---

# 📜 HISTORIAL DE VULNERABILIDADES Y DEFECTOS RESUELTOS

### Incidencia 1: Conflicto de Superposición en Barra Flotante Inferior Derecha
- **Síntoma:** Los controles de módulos en la barra derecha inferior quedaban distorsionados y sobrepuestos visualmente.
- **Solución:** Reestructuración de la rejilla CSS en el Cyber-HUD eliminando el contenedor duplicado y unificando el layout de navegación lateral.

### Incidencia 2: ImportError de `_extract_token` en `saas_router.py`
- **Síntoma:** El router de SaaS fallaba al iniciar debido a un import de función privada inexistente.
- **Solución:** Corrección a `extract_token_from_request` exportada formalmente por `app.core.auth`.

### Incidencia 3: NameError `applied_promo` en Checkout de Suscripciones
- **Síntoma:** La creación de suscripciones con código promocional lanzaba error 500 no capturado.
- **Solución:** Unificación de la variable de ámbito a `applied_promo_code`.

### Incidencia 4: Vulnerabilidad BOLA en Descarga de Archivos Multi-Tenant
- **Síntoma:** Un usuario autenticado podía descargar adjuntos de otro tenant suministrando el ID del archivo.
- **Solución:** Inyección de cláusula `WHERE user_id = current_user.id` retornando 403/404 ante intentos cruzados.
