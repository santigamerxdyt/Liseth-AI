# Registro de Cambios (Changelog)

Todos los cambios notables en este proyecto serán documentados en este archivo.
El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y este proyecto se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [2.1.0] - 2026-10-12

### Añadido (Fase 1 — Seguridad & Hardening)
- **Módulo de Autenticación (`lib/auth.js`)**:
  - Hashing seguro de PIN con `crypto.scrypt` (salt aleatorio de 16 bytes y clave derivada de 64 bytes).
  - Verificación en tiempo constante con `crypto.timingSafeEqual` para prevenir ataques de temporización.
  - Generación y verificación de tokens de sesión criptográficos firmados con HMAC-SHA256 (`sessionId.expiresAt.signature`).
  - Rate limiting en memoria por IP para mitigar ataques de fuerza bruta (máximo 5 intentos fallidos cada 15 minutos con cabecera `Retry-After`).
  - Helper `parseCookies` para procesar cabeceras `Cookie` en peticiones HTTP nativas.
- **Rutas de Autenticación en `server.js`**:
  - `POST /api/auth/login`: Autenticación por PIN y emisión de cookie segura `jarvis_session` (`HttpOnly; SameSite=Strict; Path=/; Max-Age=86400`).
  - `GET /api/auth/status`: Verificación del estado de sesión activa.
  - `POST /api/auth/logout`: Invalidación de sesión y revocación de cookie.
- **Middleware Global de Autenticación**:
  - Interceptación y protección de todas las rutas `/api/*` en `server.js`, bloqueando peticiones no autorizadas con código `401 Unauthorized` y bandera `authRequired: true`.
- **Validación Estricta de Claves en Tiempo de Arranque**:
  - Bloqueo preventivo (`process.exit(1)`) si `JARVIS_ACCESS_PIN` o `MASTER_ENCRYPTION_KEY` conservan valores inseguros o por defecto del `.env.example`.
- **Suite de Pruebas Automatizadas (`test/suite.js`)**:
  - Pruebas completas con `node:test` y `node:assert` cubriendo autenticación `scrypt`, sesiones HMAC, rate limiting, parser de cookies, cifrado AES-256-GCM, detección de manipulación de payloads, enrutamiento y failover con mocks en `BrainRouter`, y políticas de claves prohibidas.
- **Interfaz Gráfica (`jarvis.html`)**:
  - Pantalla modal de desbloqueo seguro con PIN (`#auth-modal`) con teclado numérico, feedback de errores y bloqueo en vivo.
  - Botón de bloqueo de sesión inmediato (`#btn-session-lock`) en la barra superior.
  - Manejo automático de re-autenticación cuando un endpoint responde con `401`.

### Cambiado
- **Política de CORS Restringida**:
  - Eliminado el comodín `Access-Control-Allow-Origin: *` de todos los endpoints y servido de archivos estáticos.
  - Origen restringido a coincidencia estricta con el host del usuario (`localhost`, `127.0.0.1` o IP de red local autorizada) con cabeceras `Access-Control-Allow-Credentials: true`.
- **Enlace de Red por Defecto**:
  - El servidor ahora escucha exclusivamente en `127.0.0.1` (`HOST`) para impedir accesos no autorizados desde la red local, permitiendo acceso externo solo si el usuario configura explícitamente `HOST=0.0.0.0` en `.env`.
- **Dependencias en `package.json`**:
  - Declaración explícita de campos `dependencies`, `optionalDependencies` (`edge-tts-universal`) y script `npm test`.
