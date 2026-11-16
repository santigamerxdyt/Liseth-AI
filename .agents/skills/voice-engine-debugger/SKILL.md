---
name: voice-engine-debugger
description: Diagnostica y resuelve anomalías en el ciclo de vida de voz, captura de micrófono, VAD, STT, TTS y reproducción.
---

# Voice Engine Debugger

## 🎯 Objetivo
Diagnosticar, auditar y resolver problemas en el pipeline de voz de Liseth (captura, umbrales de energía RMS, VAD, transcripciones vacías o bucles de reproducción).

## 🛠️ Herramientas Necesarias
- `run_command` para inspeccionar logs y ejecutar tests de audio.
- `read_file` y `edit_file` para ajustar umbrales en `app/services/voice_engine.py`.

## ⚙️ Procedimiento de Diagnóstico
1. Consultar estado en `/api/voice/state`.
2. Verificar si el estado es `ERROR` o si `lastError` contiene excepciones de dispositivo.
3. Evaluar el umbral `energy_threshold` (rango óptimo: 250 a 450 RMS).
4. Probar captura con buffers sintéticos o streams de prueba.
