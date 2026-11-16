---
type: adr
status: approved
priority: critical
created: 2026-11-01
updated: 2026-11-15
author: 'Cybersecurity Engineer'
tags:
  - adr
  - security
  - cryptography
  - aes-256-gcm
verified: true
---

# 🏛️ ADR-003: Cifrado Autenticado AES-256-GCM para Llaves de IA por Usuario

## Estado
**APROBADO E IMPLEMENTADO**

## Contexto y Problema
Cada usuario registrado en la plataforma aporta sus propias API keys de los proveedores de IA (Google Gemini, Groq, Anthropic, OpenAI). Almacenar estas credenciales en texto plano en la base de datos representaría una vulnerabilidad catastrófica en caso de filtración de backups o acceso no autorizado a los archivos del servidor.

## Alternativas Evaluadas
1. **Almacenamiento en Texto Plano:** Inaceptable bajo cualquier estándar de seguridad.
2. **Cifrado Simétrico Clásico AES-CBC con padding PKCS7:** Seguro pero vulnerable a ataques de oráculo de padding (Padding Oracle Attacks) si la integridad no es verificada.
3. **Cifrado Autenticado AES-256-GCM (Galois/Counter Mode):** Proporciona confidencialidad e integridad criptográfica simultánea (AEAD) con detección inmediata de manipulación de datos.

## Decisión Tomada
Implementar **AES-256-GCM** en el backend para cifrar el diccionario serializado de API keys antes de persistirlo en la columna `api_keys_encrypted` de la tabla `saas_users`.
- Formato canónico: `v1:<nonce_hex_12bytes>:<tag_hex_16bytes>:<ciphertext_hex>`.
- Llave derivada mediante HKDF/HMAC-SHA256 acoplada al secreto maestro de la aplicación.

## Justificación
Si un atacante modifica un solo bit del texto cifrado, la verificación del Tag de 128 bits falla de inmediato y rechaza el descifrado, impidiendo inyecciones o alteraciones.

## Consecuencias y Verificación
- **Validación:** Test `test_user_registration_with_custom_brain_api_keys` aprueba al 100% el ciclo de cifrado, persistencia, lectura y descifrado seguro.
- **Archivo Fuente:** [app/services/saas_service.py](file:///c:/Users/Usuario/Desktop/MI%20LISEHT/app/services/saas_service.py)
