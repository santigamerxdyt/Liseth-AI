---
type: moc
status: active
priority: high
created: 2026-11-15
updated: 2026-11-15
author: 'Hardware & Systems Engineer'
tags:
  - moc
  - nfc
  - hardware
  - ndef
  - contactless
verified: true
---

# 📡 NFC CORE ECOSYSTEM MAP (MOC)

> **PROPÓSITO:** Mapa técnico de la integración física y lógica de la tecnología **Near Field Communication (NFC)** en Liseth AI Core, abarcando el estándar W3C Web NFC, lectura/escritura NDEF y emulación P2P.

---

## 📶 TOPOLOGÍA DE HARDWARE Y SOFTWARE NFC

```mermaid
graph TD
    PhysicalTag["🏷️ Tarjeta Física NFC (NTAG213 / NTAG215 / NTAG216 / Mifare Ultralight)"]
    MobileReader["📱 Dispositivo Móvil / Lector USB Contactless (Android Chrome / PC)"]
    
    PhysicalTag -->|Frecuencia 13.56 MHz (Estándar ISO 14443 Type A)| MobileReader
    
    MobileReader --> WebNFCAPI["🌐 W3C Web NFC API (`window.NDEFReader`)"]
    
    subgraph "Motor NFC en el Cyber-HUD Frontend"
        WebNFCAPI -->|Soportado| HardwareMode["⚡ Modo Hardware Físico (Lectura/Escritura Real)"]
        WebNFCAPI -->|No Soportado / Escritorio| FallbackMode["🖥️ Modo Simulador Emulado (NFC Simulator & Virtual Hub)"]
        
        HardwareMode --> CoreNFC["Liseth NFC Engine (JavaScript Controller)"]
        FallbackMode --> CoreNFC
        
        CoreNFC --> Parser["NDEF Record Parser (Text, URI, MIME, vCard)"]
        CoreNFC --> Writer["NDEF Record Serializer"]
    end
    
    subgraph "Casos de Uso del Ecosistema"
        Parser --> UseCase1["📇 Tarjeta de Contacto Digital vCard 4.0"]
        Parser --> UseCase2["💸 Transferencia Instantánea de Créditos P2P"]
        Parser --> UseCase3["🔐 Autenticación de Dos Factores Contactless"]
        Parser --> UseCase4["⚡ Prompt Trigger (Activación de Tareas por Toque)"]
    end
    
    subgraph "Sincronización Backend"
        CoreNFC -->|POST /api/nfc/exchange| BackendNFC["FastAPI NFC Router & Ledger"]
        BackendNFC --> SaasLedger["📘 SaasCreditLedger (Transferencias Inmutables)"]
    end
```

---

## 🏷️ ESPECIFICACIONES TÉCNICAS DEL HARDWARE

- **Frecuencia Operativa:** 13.56 MHz (±7 kHz).
- **Formatos NDEF Compatibles:**
  - `RTD_TEXT`: Texto plano y payloads JSON codificados en UTF-8.
  - `RTD_URI`: Enlaces dinámicos universales (`https://liseth.ai/card/{id}`).
  - `MIME_MEDIA`: Registros de tipo `text/vcard` para tarjetas de presentación profesionales.
- **Tipos de Tags Soportados:**
  - **NTAG213:** Capacidad útil de 144 bytes (ideal para links rápidos y transferencias cortas).
  - **NTAG215:** Capacidad útil de 504 bytes (utilizado para vCards completas con foto y credenciales).
  - **NTAG216:** Capacidad útil de 888 bytes (ideal para perfiles corporativos y firmas criptográficas).

Ver especificación en [[web_nfc_spec]] y [[nfc_p2p_and_vcard]].

---

## 📲 CASOS DE USO IMPLEMENTADOS

1. **Digital Business Card (vCard 4.0):** El Señor Santiago puede aproximar su teléfono al de cualquier cliente para transferir instantáneamente su ficha de contacto ejecutivo con un solo toque, sin necesidad de instalar apps externas.
2. **Transferencia de Créditos P2P Contactless:** Dos usuarios suscritos a Liseth pueden chocar sus teléfonos para transferir créditos de IA de manera instantánea y segura con firma criptográfica.
3. **Llave Física de Autenticación (NFC 2FA):** Una tarjeta personalizada permite desbloquear el panel Superadmin CREATOR mediante aproximación física al sensor.
