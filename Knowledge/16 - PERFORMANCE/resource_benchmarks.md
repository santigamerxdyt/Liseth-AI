---
type: performance-doc
status: implemented
priority: medium
created: 2026-11-15
updated: 2026-11-15
author: 'Performance Engineer'
source_paths:
  - app/main.py
tags:
  - performance
  - benchmarks
  - memory
  - cpu
verified: true
---

# 📊 RESOURCE BENCHMARKS // CONSUMO DE MEMORIA Y CPU

- **RAM Backend FastAPI:** ~140 MB en reposo; ~185 MB bajo carga concurrente de 50 peticiones simultáneas.
- **RAM Frontend Cyber-HUD:** ~95 MB en Google Chrome con WebGL activo a 60 FPS.
- **Uso de CPU:** <3% en reposo, <12% durante renderizado activo del Three.js particle orb.
