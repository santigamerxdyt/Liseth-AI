---
type: adr
status: approved
priority: high
created: 2026-11-14
updated: 2026-11-15
author: 'Hardware Systems Lead'
tags:
  - adr
  - nfc
  - hardware
  - web-nfc
verified: true
---

# 🏛️ ADR-006: Protocolo Web NFC con Motor Fallback Emulado

## Estado
**APROBADO E IMPLEMENTADO**

## Contexto y Problema
La API Web NFC (`window.NDEFReader`) del W3C solo está disponible de forma nativa en navegadores basados en Chromium en dispositivos Android compatibles. En computadores de escritorio (Windows, Mac, Linux) o navegadores como Firefox/Safari, el hardware NFC no es expuesto directamente a JavaScript, lo cual podría impedir la experiencia de usuario o generar errores no controlados.

## Alternativas Evaluadas
1. **Limitar la funcionalidad NFC únicamente a Android:** Deja fuera a los usuarios que utilizan la plataforma en laptop o PC de escritorio.
2. **Forzar un driver nativo de escritorio por WebSockets:** Requiere que el usuario instale software adicional en su sistema operativo.
3. **Arquitectura Híbrida con Detección Automática y Simulador:** Si `window.NDEFReader` está presente, utiliza el hardware real; si no está disponible, activa un emulador gráfico en el HUD que simula la aproximación de tarjetas, lectura de registros NDEF y transferencias P2P.

## Decisión Tomada
Adoptar la arquitectura híbrida con fallback emulado transparente.
- En Android Chrome: Lectura y escritura real a 13.56 MHz sobre tags físicos NTAG213/215/216.
- En Escritorio / Otros: Modal interactivo con emulación de radiofrecuencia, generación de vCard virtual y transferencias de prueba.

## Justificación
Garantiza que el 100% de los usuarios puedan experimentar las funcionalidades contactless de la plataforma independientemente de su dispositivo, manteniendo el soporte de hardware real para demostraciones físicas del Señor Santiago.

## Consecuencias y Verificación
- **Validación:** Verificado en pruebas de UI del Cyber-HUD y componentes de emulación.
- **Archivo Fuente:** [index.html](file:///c:/Users/Usuario/Desktop/MI%20LISEHT/index.html) (Módulo NFC)
