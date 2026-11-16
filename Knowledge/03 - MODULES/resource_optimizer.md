---
type: module
status: implemented
priority: medium
module: resource_optimizer
created: 2026-11-15
updated: 2026-11-15
author: 'Performance Engineer'
source_paths:
  - app/main.py
tags:
  - module
  - memory
  - gc
  - optimization
verified: true
---

# 🧹 RESOURCE OPTIMIZER // RECOLECTOR DE MEMORIA Y OPTIMIZADOR

## 🎯 Objetivo y Responsabilidad
Controla el ciclo de vida de los procesos en segundo plano, ejecutando recolección de basura forzada (`gc.collect()`), cerrando conexiones inactivas de SQLite y liberando texturas de Three.js para sostener un consumo de RAM inferior a 180 MB en el backend y menos de 120 MB en el navegador.

## 📍 Ubicación e Hipervínculos
- **Archivo Fuente:** [app/main.py](file:///c:/Users/Usuario/Desktop/MI%20LISEHT/app/main.py)
- **Activación:** Automática cada 15 minutos de inactividad o mediante el botón del Cyber-HUD `Liberar Memoria`.
