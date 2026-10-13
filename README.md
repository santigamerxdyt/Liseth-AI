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

## 🌐 Google Workspace & Function Calling (Fase 2)

JARVIS integra 28 herramientas de **Google Workspace** mediante OAuth 2.0 con scopes mínimos y function calling nativo:

| Servicio | Herramientas Disponibles | Sensible (Requiere Aprobación) |
|---|---|---|
| **Gmail** | `list_emails`, `search_emails`, `read_email`, `send_email`, `reply_email`, `archive_email`, `label_email`, `delete_email` | `send`, `reply`, `delete` |
| **Calendar** | `list_events`, `create_event`, `update_event`, `delete_event` | `create`, `update`, `delete` |
| **Tasks** | `list_tasks`, `create_task`, `complete_task`, `delete_task` | `delete` |
| **Drive** | `list_drive_files`, `search_drive_files`, `read_drive_file`, `upload_drive_file`, `move_drive_file` | `upload`, `move` |
| **Docs** | `read_doc`, `create_doc`, `append_doc` | `create`, `append` |
| **Sheets** | `read_sheet`, `create_sheet`, `append_sheet_row` | `create`, `append_row` |
| **Slides** | `read_slides`, `create_slides`, `add_slide` | `create`, `add_slide` |
| **Contacts (People API)** | `search_contacts` (búsqueda por nombre, email o teléfono) | Ninguna (Solo lectura) |
| **YouTube Data API v3** | `search_youtube`, `list_my_youtube_videos`, `get_youtube_video_stats` | Ninguna (Solo lectura) |

### 📌 Límites y Cuotas Gratuitas de YouTube Data API v3:
- **Cuota Diaria Gratuita**: 10,000 unidades por día por proyecto.
- **Costos de Lectura**: `videos.list` (estadísticas) cuesta **1 unidad**; `search.list` cuesta **100 unidades**.
- **Costos de Escritura**: Subir videos (`videos.insert`) consume **1,600 unidades** por video (máximo ~6 videos/día antes de agotar cuota). Actualizar metadata (`videos.update`) cuesta **50 unidades**.
- **Políticas de Privacidad**: Los videos subidos a través de aplicaciones no verificadas por Google se marcan obligatoriamente como **Privados**.

### 🛡️ Acciones Sensibles & AuditManager
- Todas las operaciones destructivas o que envían información a terceros exigen confirmación en pantalla en [`jarvis.html`](file:///c:/Users/Usuario/Desktop/MI%20LISEHT/jarvis.html).
- Si Google Workspace no está conectado, JARVIS expone igualmente las herramientas y responde educadamente indicando: *"Para realizar esta acción, conecta Google Workspace en el Dashboard de Servicios"*.

---

## ⏰ Programador de Tareas y Mensajería Proactiva (Fase 3)

### 1. Programador Persistente (`lib/scheduler/TaskScheduler.js`)
El sistema cuenta con un motor de ejecución en segundo plano (`ticker` cada 30 segundos) sin dependencias externas pesadas, con persistencia garantizada en `data/scheduled_tasks.json`:
- **Resumen Matutino (08:00 AM)**: Compila agenda de Google Calendar, tareas pendientes y clima/noticias para enviar a WhatsApp/Telegram.
- **Revisión Estratégica Semanal (Lunes 08:30 AM)**: Análisis de metas de la semana.
- **Monitor de Eventos (Cada 15 min)**: Alerta anticipada 15 minutos antes de citas agendadas.
- **Reporte de Salud del Sistema (Cada 60 min)**: Auditoría de estado de cerebro, tokens consumidos y conectividad.
- **API REST Protegida**: Endpoints `/api/scheduler/tasks`, `/api/scheduler/tasks/update`, `/api/scheduler/tasks/delete` y `/api/scheduler/tasks/trigger`.

### 2. WhatsApp Meta Cloud API y Ventana de 24 Horas
- **Política Oficial de Meta**: WhatsApp Business Cloud API no permite enviar mensajes libres fuera de una ventana de 24 horas desde el último mensaje entrante del usuario (las políticas de Meta exigen *Message Templates* aprobadas).
- `NotificationManager` registra la última interacción del usuario en cada mensaje recibido y bloquea intentos proactivos fuera de ventana para evitar sanciones o errores de entrega en Meta.

### 3. Bot Interactivo de Telegram
- Conexión mediante sondeo HTTP nativo con reconexión automática.
- Comandos rápidos integrados:
  - `/start`: Bienvenida y menú de comandos.
  - `/estado`: Monitor en tiempo real de cerebro activo, consumo de tokens y estado de Workspace.
  - `/resumen`: Próximos eventos y compromisos del día.
- **Conversación Libre**: Cualquier consulta que no sea comando es procesada por `BrainRouter` respondiendo como Liseth directamente en Telegram.

---

## 💰 Control de Costes, Modelos y Límites de Tokens (Fase 4)

JARVIS integra un sistema contable y de protección preventiva contra sobrecostes en [`lib/ai/BrainRouter.js`](file:///c:/Users/Usuario/Desktop/MI%20LISEHT/lib/ai/BrainRouter.js):

### 1. Límite Diario de Tokens & Bloqueo Preventivo
- **Límite Configurable**: `DAILY_TOKEN_LIMIT` en `.env` (por defecto `100,000` tokens).
- **Protección Activa**: Si el consumo acumulado del día alcanza el límite, el servidor detiene las consultas retornando error `429 Too Many Requests` y envía una alerta proactiva por WhatsApp/Telegram.
- **Alerta Temprana**: Al superar `ALERT_THRESHOLD_PCT` (por defecto 80%), notifica al usuario del consumo alcanzado.
- **Rollover Automático a Medianoche**: Al cambiar la fecha calendario, las estadísticas diarias de tokens y costes se reinician limpiamente a cero.

### 2. Parametrización de Modelos de Inteligencia Artificial
- **Google Gemini**: Configurable mediante `GEMINI_MODEL` (ej. `gemini-2.0-flash`, `gemini-1.5-flash`, `gemini-1.5-pro`).
- **Anthropic Claude**: Configurable mediante `ANTHROPIC_MODEL` (ej. `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022`).
- Soporte para override puntual por llamada en `options.model`.

### 3. Estimación Financiera de Costes (USD)
- Tarifas oficiales por 1,000 tokens integradas en `DEFAULT_RATES` (o configurables vía variables de entorno).
- Desglose contable en tiempo real expuesto en `GET /api/brain/status` y `GET /api/stats`.
- Visualización interactiva en el modal de Cerebro en [`jarvis.html`](file:///c:/Users/Usuario/Desktop/MI%20LISEHT/jarvis.html) con indicador en vivo de costes hoy y del mes, desglose por modelo y barra de consumo con alertas visuales.

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
│   ├── notifications/
│   │   └── NotificationManager.js     # Envío proactivo a WhatsApp (Meta) y bot interactivo de Telegram
│   └── scheduler/
│       └── TaskScheduler.js           # Programador recurrente persistente en disco
├── test/
│   └── suite.js                       # Suite de pruebas unitarias (node:test y node:assert)
├── data/                              # Base de datos persistente (JSON) y métricas
├── jarvis.html                        # Interfaz gráfica principal (Frontend SPA)
├── server.js                          # Servidor HTTP con middleware de autenticación y endpoints
├── package.json                       # Metadatos del proyecto y scripts
└── .env                               # Variables de entorno y secretos locales (ignorado en git)
```
