---
type: research
status: completed
created: 2026-11-15
updated: 2026-11-15
author: 'Hardware & Protocols Specialist'
tags:
  - research
  - nfc
  - w3c
  - contactless
verified: true
---

# 🔬 ESTUDIO DEL ESTÁNDAR W3C WEB NFC Y COMPATIBILIDAD

## Estado del Estándar en la Industria
La especificación W3C Web NFC permite a aplicaciones web comerciales leer y escribir etiquetas NFC NDEF cuando el usuario aproxima su teléfono al tag.
- **Soporte Nativo:** Google Chrome para Android versión 89 o superior, Edge para Android, Opera para Android.
- **Restricciones de Seguridad:** Requiere HTTPS obligatorio, visibilidad en pestaña activa y permiso explícito del usuario.
- **Estrategia para Liseth AI:** Arquitectura de conmutación adaptativa: si `window.NDEFReader` no está presente (ej. Windows Desktop), se inicia el simulador virtual en el HUD sin interrumpir la experiencia.
