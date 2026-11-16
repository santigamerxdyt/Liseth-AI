---
name: background-voice-manager
description: Administra la escucha continua, wake words en segundo plano, políticas de visibilidad y reconexión tras suspensión.
---

# Background Voice Manager

## 🎯 Objetivo
Mantener la experiencia conversacional sin fricción cuando la ventana pierde el foco o el usuario opera en modo manos libres.

## ⚙️ Procedimiento
1. Detectar transiciones de visibilidad (`document.visibilityState`).
2. Sostener la captura mediante Web Audio API en primer plano o proceso nativo Python en escritorio.
3. Reactivar el reconocimiento ante desconexiones automáticas del navegador.
