---
type: module
status: implemented
priority: critical
module: action_dispatcher
created: 2026-11-15
updated: 2026-11-15
author: 'Backend Team'
source_paths:
  - core/action_dispatcher.py
tags:
  - module
  - dispatcher
  - skills
verified: true
---

# ⚡ ACTION DISPATCHER // DESPACHADOR CENTRAL DE ACCIONES

## 🎯 Objetivo y Responsabilidad
El `ActionDispatcher` actúa como el bus de ejecución de comandos de Liseth. Intercepta intenciones del usuario en lenguaje natural o llamadas estructuradas del HUD y las despacha a sus controladores respectivos (consultas web, operaciones de base de datos, diagnósticos del sistema, cálculos financieros).

## 📍 Ubicación e Hipervínculos
- **Archivo Fuente:** [core/action_dispatcher.py](file:///c:/Users/Usuario/Desktop/MI%20LISEHT/core/action_dispatcher.py)
- **Tests Asociados:** [test/test_brain.py](file:///c:/Users/Usuario/Desktop/MI%20LISEHT/test/test_brain.py)

## ⚙️ Flujo de Operación
1. Recibe la orden estructurada: `{"action": "lookup_data", "payload": {...}}`.
2. Verifica permisos del rol del usuario (`CREATOR`, `ADMIN`, etc.).
3. Despacha la ejecución hacia la skill correspondiente.
4. Retorna el resultado con formato enriquecido para el Cyber-HUD.
