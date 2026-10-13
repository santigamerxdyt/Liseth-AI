# JARVIS / Liseth — Asistente Personal de Inteligencia Artificial v2.0

Asistente personal local desarrollado en **Node.js** con cerebro dual (**Google Gemini** y **Anthropic Claude**), integración con **Google Workspace**, notificaciones proactivas (**WhatsApp** / **Telegram**), interfaz sci-fi moderna en `jarvis.html` y arquitectura de seguridad reforzada.

---

## 🔒 Seguridad y Protección del Sistema (Fase 1 — Hardening)

El sistema cuenta con un modelo de defensa en profundidad para proteger todos los datos y endpoints locales:

1. **Autenticación con PIN Criptográfico (`scrypt`)**:
   - El PIN de acceso (`JARVIS_ACCESS_PIN`) se almacena y verifica mediante derivación de clave con algoritmo nativo `crypto.scrypt` (salt aleatorio de 16 bytes, clave derivada de 64 bytes).
   - Verificación en tiempo constante (`crypto.timingSafeEqual`) para mitigar ataques de temporización (*timing attacks*).
2. **Sesiones Criptográficas Firmadas (`HMAC-SHA256`)**:
   - Sesión emitida mediante token firmado (`sessionId.expiresAt.signature`) transportado en cookie `jarvis_session` con banderas `HttpOnly; SameSite=Strict; Path=/`.
   - Middleware en `server.js` que intercepta y protege todas las rutas `/api/*` (rechazo `401 Unauthorized` si no existe sesión válida).
3. **Protección contra Fuerza Bruta (Rate Limiting)**:
   - Máximo 5 intentos fallidos de PIN por IP en una ventana de 15 minutos. Si se supera el umbral, se bloquea la IP con código `429 Too Many Requests` y cabecera `Retry-After`.
4. **Validación Estricta de Arranque**:
   - El servidor aborta inmediatamente su inicio (`process.exit(1)`) si `JARVIS_ACCESS_PIN` o `MASTER_ENCRYPTION_KEY` continúan con los valores por defecto del `.env.example` o cadenas débiles (`1234`, `0000`, `admin`, etc.).
5. **CORS Restringido**:
   - Se eliminaron todos los comodines `Access-Control-Allow-Origin: *`.
   - Las respuestas autorizan exclusivamente el origen coincidente con el host del usuario (`localhost`, `127.0.0.1` o IP de red local autorizada) con soporte de credenciales.
6. **Enlace Seguro a Red**:
   - Por defecto el servidor escucha exclusivamente en `127.0.0.1` (`HOST`).
   - Para habilitar el acceso desde el celular o tablet en la red Wi-Fi, debe configurarse explícitamente `HOST=0.0.0.0` en `.env`.
7. **Cifrado AES-256-GCM (`lib/crypto.js`)**:
   - Tokens de OAuth y credenciales sensibles se cifran con AES-256-GCM con detección de manipulación de tags de autenticación.

---

## 🚀 Inicio Rápido

### Requisitos
- **Node.js** v18 o superior (probado en Node.js v24).
- Sin dependencias externas obligatorias para el núcleo (utiliza APIs nativas de Node).

### Configuración del Entorno
Copia `.env.example` a `.env` y configura tus valores personales:
```bash
cp .env.example .env
```

Asegúrate de definir:
- `JARVIS_ACCESS_PIN`: Tu PIN personal seguro (no uses `1234`).
- `MASTER_ENCRYPTION_KEY`: Clave única de cifrado de al menos 16 caracteres.
- `HOST`: `127.0.0.1` (seguridad local) o `0.0.0.0` (red local).
- `PORT`: `3000` (por defecto).
- `GEMINI_API_KEY`: Clave del cerebro principal de Google.
- `ANTHROPIC_API_KEY`: Clave del cerebro de respaldo de Claude (opcional).

### Ejecución del Servidor
```bash
npm start
# o directamente:
node server.js
```
Abre tu navegador en: [http://127.0.0.1:3000](http://127.0.0.1:3000)

### Ejecución de Pruebas Automatizadas
```bash
npm test
# o directamente:
node test/suite.js
```

---

## 🧪 Suite de Pruebas (`test/suite.js`)
La suite de pruebas valida automáticamente:
- Derivación y validación de PINs mediante `scrypt`.
- Emisión y validación de tokens de sesión con HMAC y rechazo de tokens alterados o expirados.
- Rate limiting por IP contra fuerza bruta y reseteo tras éxito.
- Parser de cookies HTTP.
- Cifrado simétrico AES-256-GCM y rechazo ante alteración del payload o auth tag.
- Enrutador de IA (`BrainRouter`) con mocks:
  - Ejecución en cerebro primario (Gemini).
  - Conmutación automática (*failover*) a Claude ante error 429 de cuota en Gemini.
  - Forzado manual de cerebro.
- Verificación de listas de claves y PINs prohibidos por seguridad.

---

## 📁 Estructura del Proyecto
```
├── lib/
│   ├── auth.js                        # Hashing scrypt, sesiones HMAC, rate limiting y cookies
│   ├── crypto.js                      # Cifrado simétrico AES-256-GCM
│   ├── ai/
│   │   └── BrainRouter.js             # Cerebro dual Gemini/Claude con failover y monitor de tokens
│   ├── audit/
│   │   └── AuditManager.js            # Registro de auditoría y confirmación de acciones sensibles
│   ├── connectors/
│   │   ├── BaseConnector.js           # Clase base con interfaz común de conectores
│   │   └── GoogleWorkspaceConnector.js# Conector OAuth 2.0 para Google Workspace
│   └── notifications/
│       └── NotificationManager.js     # Envío proactivo a WhatsApp (Meta) y Telegram
├── test/
│   └── suite.js                       # Suite de pruebas unitarias (node:test y node:assert)
├── data/                              # Base de datos persistente (JSON) y métricas
├── jarvis.html                        # Interfaz gráfica principal (Frontend SPA)
├── server.js                          # Servidor HTTP con middleware de autenticación y endpoints
├── package.json                       # Metadatos del proyecto y scripts
└── .env                               # Variables de entorno y secretos locales (ignorado en git)
```
