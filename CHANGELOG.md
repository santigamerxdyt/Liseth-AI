# Registro de Cambios (Changelog)

Todos los cambios notables en este proyecto serán documentados en este archivo.
El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y este proyecto se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [2.3.0] - 2026-10-12

### Añadido (Fase 3 — Programador de Tareas y Mensajería WhatsApp/Telegram)
- **Programador de Tareas Persistente (`lib/scheduler/TaskScheduler.js`)**:
  - Motor de ejecución en segundo plano (`ticker` cada 30 segundos) con persistencia garantizada en disco (`data/scheduled_tasks.json`).
  - Tareas recurrentes preconfiguradas que sobreviven a reinicios del servidor:
    - *Resumen Matutino Ejecutivo*: Diario a las 08:00 AM con agenda, eventos y tareas pendientes vía WhatsApp/Telegram.
    - *Revisión Estratégica Semanal*: Lunes a las 08:30 AM con balance de metas y proyección semanal.
    - *Monitor de Eventos Próximos*: Cada 15 minutos alertando 15 min antes de cualquier cita de Google Calendar.
    - *Reporte de Salud y Conectividad*: Cada 60 minutos verificando estado de cerebro, tokens y conectividad.
  - Endpoints REST protegidos para gestión del programador en `server.js`:
    - `GET /api/scheduler/tasks`: Listado de tareas activas con su próxima fecha y hora de ejecución.
    - `POST /api/scheduler/tasks/update`: Creación o modificación de tareas programadas.
    - `POST /api/scheduler/tasks/delete`: Eliminación controlada de tareas.
    - `POST /api/scheduler/tasks/trigger`: Disparo manual inmediato de cualquier tarea.
- **Mensajería Proactiva e Interactiva (`lib/notifications/NotificationManager.js`)**:
  - **Cumplimiento Estricto de Política Meta WhatsApp (Ventana 24h)**:
    - Registro de marcas de tiempo en mensajes entrantes (`recordIncomingWhatsApp`).
    - Verificación automática de ventana de 24 horas (`isWithinWhatsApp24hWindow`).
    - Bloqueo preventivo de mensajes proactivos en texto libre fuera de la ventana de 24h, indicando el requisito de plantillas (*Message Templates*) pre-aprobadas para evitar penalizaciones en la API de Meta.
  - **Bot Interactivo de Telegram**:
    - Sondeo de mensajes sin dependencias externas (`_pollTelegramUpdates`).
    - Comandos nativos interactivos:
      - `/start`: Presentación del asistente Liseth y guía de comandos disponibles.
      - `/estado`: Reporte en vivo del cerebro activo, consumo de tokens de hoy, estado de Google Workspace y uptime.
      - `/resumen`: Consulta inmediata de agenda y eventos de Google Calendar.
    - Conversación libre bidireccional: Cualquier mensaje que no sea comando es procesado a través de `BrainRouter` respondiendo con la calidez y precisión de Liseth en el mismo chat.
  - **Webhooks en `server.js`**:
    - `GET /api/webhook/whatsapp`: Verificación estándar de webhook de Meta (`hub.mode`, `hub.challenge`, `hub.verify_token`).
    - `POST /api/webhook/whatsapp`: Recepción de eventos y mensajes entrantes de WhatsApp con actualización de ventana de 24 horas.
- **Suite de Pruebas Unitarias (`test/suite.js`)**:
  - 4 nuevas pruebas unitarias añadidas (18 pruebas en total) validando persistencia y cálculo cron de `TaskScheduler`, operaciones CRUD, política de 24 horas de Meta y comandos interactivos de Telegram con mock de `BrainRouter`.

---

## [2.2.0] - 2026-10-12

### Añadido (Fase 2 — Google Workspace Completo & Function Calling)
- **Expansión Completa de Google Workspace (`lib/connectors/GoogleWorkspaceConnector.js`)**:
  - Ampliación del catálogo de 7 a 28 herramientas disponibles para Function Calling de IA.
  - **Gmail**: Búsqueda avanzada (`google_search_emails`), lectura detallada de mensajes (`google_read_email`), respuestas automáticas en hilo (`google_reply_email`), archivado (`google_archive_email`), gestión de etiquetas (`google_label_email`) y eliminación a papelera (`google_delete_email`).
  - **Calendar**: Edición y reprogramación de eventos (`google_update_event`) y eliminación de eventos (`google_delete_event`).
  - **Tasks**: Marcar tareas como completadas (`google_complete_task`) y eliminación permanente (`google_delete_task`).
  - **Drive**: Búsqueda avanzada por texto/MIME (`google_search_drive_files`), lectura/exportación de archivos a texto o CSV (`google_read_drive_file`), subida de archivos multipart (`google_upload_drive_file`) y traslado de carpetas (`google_move_drive_file`).
  - **Docs**: Lectura de documentos (`google_read_doc`), creación (`google_create_doc`) y adición de texto (`google_append_doc`).
  - **Sheets**: Lectura de celdas y tablas (`google_read_sheet`), creación de libros (`google_create_sheet`) y adición de filas (`google_append_sheet_row`).
  - **Slides**: Lectura de diapositivas (`google_read_slides`), creación de presentaciones (`google_create_slides`) y creación de nuevas diapositivas (`google_add_slide`).
  - **Contacts (People API)**: Búsqueda rápida de contactos por nombre, email o teléfono (`google_search_contacts`) con fallback a conexiones de libreta.
  - **YouTube Data API v3**: Búsqueda de videos (`google_search_youtube`), listado de videos del canal autenticado (`google_list_my_youtube_videos`) y consulta de estadísticas de vistas, likes y comentarios (`google_get_youtube_video_stats`).
- **Seguridad en Acciones Sensibles (`AuditManager`)**:
  - Todas las operaciones destructivas o que envían/modifican datos de terceros (`send_email`, `reply_email`, `delete_email`, `create_event`, `update_event`, `delete_event`, `delete_task`, `upload_drive_file`, `move_drive_file`, `create_doc`, `append_doc`, `create_sheet`, `append_sheet_row`, `create_slides`, `add_slide`) marcadas estrictamente con `sensitive: true`.
  - Exigen confirmación interactiva en pantalla mediante `AuditManager.createPendingConfirmation` antes de su ejecución real.
- **Function Calling Permanente & Resiliente**:
  - Todas las herramientas se exponen permanentemente a Gemini y Claude independientemente de si Google está conectado o no.
  - Si el usuario solicita una acción de Google y no está vinculado, el sistema responde guiando al usuario a conectar su cuenta en el Dashboard de Servicios en lugar de fallar o quedarse mudo.
- **Pruebas Automatizadas en `test/suite.js`**:
  - 4 nuevas pruebas unitarias añadidas (14 pruebas en total) cubriendo catálogo de acciones, validación de marcas `sensitive`, comportamiento desconectado, URL OAuth con scopes mínimos y simulación de llamadas HTTP a YouTube y Docs.

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
