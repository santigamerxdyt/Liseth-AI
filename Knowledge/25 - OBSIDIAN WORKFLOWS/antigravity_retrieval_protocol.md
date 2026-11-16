---
type: workflow
status: active
priority: critical
created: 2026-11-15
updated: 2026-11-15
author: 'AI Engineering Lead'
tags:
  - workflow
  - antigravity
  - retrieval
  - token-optimization
verified: true
---

# 🔍 PROTOCOLO DE RECUPERACIÓN PROGRESIVA PARA ANTIGRAVITY

> **DIRECTIVA CRÍTICA:** Antigravity y cualquier agente asistente DEBEN seguir este protocolo de 5 niveles para interactuar con la base de código de Liseth AI. Queda prohibido leer archivos masivos de código sin antes consultar la documentación modular correspondiente.

---

## 🪜 LOS 5 NIVELES DE RECUPERACIÓN DE CONTEXTO

```mermaid
graph TD
    UserQuery["Petición del Usuario / Bug / Nueva Feature"] --> L1["Nivel 1: Resumen & MOC en Knowledge/"]
    L1 --> L2["Nivel 2: Documentación Técnica de Módulo"]
    L2 --> L3["Nivel 3: Lectura Quirúrgica de Archivos Fuente"]
    L3 --> L4["Nivel 4: Verificación con Decisiones (ADRs)"]
    L4 --> L5["Nivel 5: Ejecución de Tests & Actualización del Vault"]
```

### Nivel 1 — Búsqueda en el Knowledge Vault
- **Acción:** Consultar primero [[PROJECT COMMAND CENTER]] o el MOC específico:
  - Arquitectura y Backend: [[PROJECT ARCHITECTURE MAP]]
  - IA y Cerebros: [[AI ECOSYSTEM MAP]]
  - Facturación y Precios: [[BUSINESS AND REVENUE MAP]]
  - Seguridad y Permisos: [[SECURITY AND PRIVACY MAP]]
  - NFC y Hardware: [[NFC CORE ECOSYSTEM MAP]]
  - Inventario de Módulos: [[MODULES DATABASE]]
- **Consumo de Contexto:** Mínimo (<500 tokens).

### Nivel 2 — Documentación Técnica de Módulo
- **Acción:** Leer la nota del módulo específico en `Knowledge/03 - MODULES/` o `Knowledge/05 - BACKEND/`.
- **Información Obtenida:** Rutas exactas de archivos fuente, esquemas Pydantic, dependencias y riesgos conocidos.

### Nivel 3 — Lectura Quirúrgica de Código Real
- **Acción:** Leer exclusivamente las líneas necesarias del archivo fuente utilizando `read_file` con parámetros `StartLine` y `EndLine`.
- **Regla:** NUNCA volcar archivos completos de 1,000+ líneas si solo se requiere inspeccionar una función.

### Nivel 4 — Verificación con Registros de Decisiones (ADRs)
- **Acción:** Consultar `Knowledge/21 - TECHNICAL DECISIONS/` para validar que el cambio planeado no rompa una directiva arquitectónica previa (ej: inmutabilidad del ledger contable o modo WAL de SQLite).

### Nivel 5 — Ejecución de Pruebas y Actualización
- **Acción:**
  1. Ejecutar las pruebas: `python -m pytest test/ -q`
  2. Verificar que los 438 tests pasen sin fallos.
  3. Si se modificó la lógica de un módulo, actualizar la nota de Obsidian correspondiente con la fecha actual y marcar `verified: true`.
