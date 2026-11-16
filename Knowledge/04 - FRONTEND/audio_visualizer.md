---
type: frontend
status: implemented
priority: medium
created: 2026-11-15
updated: 2026-11-15
author: 'Frontend Engineer'
source_paths:
  - index.html
tags:
  - frontend
  - audio
  - visualizer
  - web-audio-api
verified: true
---

# 🎙️ AUDIO VISUALIZER // RECONOCIMIENTO Y ESPECTRO DE VOZ

## 🎯 Capacidades
- **Captura:** `navigator.mediaDevices.getUserMedia({ audio: true })`.
- **Análisis FFT:** `AnalyserNode` con `fftSize = 256` para extracción de espectro en tiempo real.
- **Transcripción Continua:** Integración con la Web Speech API (`webkitSpeechRecognition`) con reconexión automática tras 20 segundos de reposo.
