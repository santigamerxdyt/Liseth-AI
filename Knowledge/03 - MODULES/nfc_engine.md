---
type: module
status: implemented
priority: high
module: nfc_engine
created: 2026-11-15
updated: 2026-11-15
author: 'Hardware Lead'
source_paths:
  - index.html
tags:
  - module
  - nfc
  - contactless
verified: true
---

# 📶 NFC ENGINE // CONTROLADOR DE HARDWARE Y EMULACIÓN WEB NFC

## 🎯 Objetivo y Responsabilidad
Gestiona el escaneo y escritura de etiquetas NDEF a través de la API `window.NDEFReader`.
- Si el navegador o hardware no soporta Web NFC (ej: PC de escritorio), inicia el simulador interactivo de radiofrecuencia con animaciones hápticas en el Cyber-HUD.
- Permite serializar registros vCard 4.0 con los datos de contacto ejecutivo del Señor Santiago.
- Ver [[ADR-006-Web-NFC-Hardware]].
