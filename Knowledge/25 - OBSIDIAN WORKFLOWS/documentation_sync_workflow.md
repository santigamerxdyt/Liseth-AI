---
type: workflow
status: active
priority: high
created: 2026-11-15
updated: 2026-11-15
author: 'DevOps & Documentation Team'
tags:
  - workflow
  - sync
  - maintenance
verified: true
---

# 🔄 WORKFLOW: SINCRONIZACIÓN AUTOMÁTICA DE DOCUMENTACIÓN

## Flujo de Trabajo Antes y Después de Modificar Código

### FASE 1: Antes de Tocar el Código
1. **Identificar el Módulo:** Buscar en [[MODULES DATABASE]] el archivo exacto.
2. **Revisar Incidencias Previas:** Consultar [[BUGS DATABASE]] para comprobar si el componente tuvo problemas similares.
3. **Comprobar ADRs Vigentes:** Verificar en [[DECISIONS DATABASE]] las restricciones de diseño.
4. **Planificar el Cambio:** Redactar un plan conciso con las líneas a modificar.

### FASE 2: Modificación y Pruebas
1. Aplicar la edición con `edit_file`.
2. Correr la suite de pruebas:
   ```powershell
   python -m pytest test/ -q
   ```
3. Comprobar que el resultado arroje **438 passed, 0 failed**.

### FASE 3: Actualización del Vault
1. Si se creó un nuevo endpoint, documentarlo en [[rest_api_reference]].
2. Si se resolvió un defecto, añadirlo a [[resolved_bugs_history]] y actualizar [[BUGS DATABASE]].
3. Actualizar la cabecera YAML de la nota con `updated: YYYY-MM-DD` y `verified: true`.
