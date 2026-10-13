/**
 * Conector de Google Workspace Completo (Fase 2)
 * Gmail, Calendar, Tasks, Drive, Docs, Sheets, Slides, Contacts (People API) y YouTube Data API v3
 * Utiliza llamadas HTTP directas con OAuth 2.0 y tokens cifrados con AES-256-GCM
 */

const https = require('https');
const BaseConnector = require('./BaseConnector');
const { encrypt, decrypt } = require('../crypto');

/**
 * Cuotas y Restricciones del Plan Gratuito de APIs de Google:
 * 
 * 1. YouTube Data API v3:
 *    - Cuota gratuita diaria por proyecto: 10,000 unidades / día.
 *    - Lecturas: search.list = 100 unidades, videos.list = 1 unidad.
 *    - Escrituras:
 *      * videos.insert (Subida de video): consume 1,600 unidades por video (~6 videos/día máx).
 *      * videos.update (Editar metadatos): consume 50 unidades.
 *      * playlists.insert (Crear playlist): consume 50 unidades.
 *    - Restricción de verificación: Los videos subidos a través de proyectos de desarrollador
 *      no auditados por Google se publican obligatoriamente con visibilidad "Privado" (private).
 * 
 * 2. Google Workspace (Gmail, Calendar, Drive, Docs, Sheets, Slides, Tasks, People API):
 *    - Cuota gratuita para cuentas personales @gmail.com:
 *      * Gmail: Máximo 500 correos enviados por día (2,000 para Google Workspace de pago).
 *      * Drive / Docs / Sheets / Slides: Sin costo de API, sujeto únicamente al espacio libre de Google Drive (15 GB compartidos).
 *      * People API: 90 peticiones por minuto por usuario.
 */

class GoogleWorkspaceConnector extends BaseConnector {
  constructor() {
    super('google_workspace', 'Google Workspace', 'Integración completa con Gmail, Calendar, Drive, Tasks, Docs, Sheets, Slides, Contacts y YouTube');
    this.clientId = process.env.GOOGLE_CLIENT_ID || '';
    this.clientSecret = process.env.GOOGLE_CLIENT_SECRET || '';
    this.redirectUri = process.env.GOOGLE_REDIRECT_URI || 'http://localhost:3000/api/google/oauth2callback';
    this.tokens = null; // { access_token, refresh_token_encrypted, expiry_date }
  }

  setCredentials({ clientId, clientSecret, redirectUri }) {
    if (clientId) this.clientId = clientId;
    if (clientSecret) this.clientSecret = clientSecret;
    if (redirectUri) this.redirectUri = redirectUri;
  }

  loadEncryptedTokens(storedData) {
    if (storedData && storedData.refresh_token_encrypted) {
      this.tokens = {
        access_token: storedData.access_token || '',
        refresh_token_encrypted: storedData.refresh_token_encrypted,
        expiry_date: storedData.expiry_date || 0
      };
      this.connected = true;
    }
  }

  getAuthUrl() {
    const scopes = [
      'https://www.googleapis.com/auth/gmail.modify',
      'https://www.googleapis.com/auth/calendar.events',
      'https://www.googleapis.com/auth/drive',
      'https://www.googleapis.com/auth/tasks',
      'https://www.googleapis.com/auth/documents',
      'https://www.googleapis.com/auth/spreadsheets',
      'https://www.googleapis.com/auth/presentations',
      'https://www.googleapis.com/auth/contacts.readonly',
      'https://www.googleapis.com/auth/youtube.readonly'
    ];
    const params = new URLSearchParams({
      client_id: this.clientId,
      redirect_uri: this.redirectUri,
      response_type: 'code',
      scope: scopes.join(' '),
      access_type: 'offline',
      prompt: 'consent'
    });
    return `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
  }

  async exchangeCodeForTokens(code) {
    const postData = new URLSearchParams({
      code,
      client_id: this.clientId,
      client_secret: this.clientSecret,
      redirect_uri: this.redirectUri,
      grant_type: 'authorization_code'
    }).toString();

    const res = await this._httpRequest('oauth2.googleapis.com', '/token', 'POST', postData, {
      'Content-Type': 'application/x-www-form-urlencoded'
    });

    if (res.access_token) {
      this.tokens = {
        access_token: res.access_token,
        refresh_token_encrypted: encrypt(res.refresh_token || ''),
        expiry_date: Date.now() + (res.expires_in || 3600) * 1000
      };
      this.connected = true;
      return this.tokens;
    }
    throw new Error(res.error_description || res.error || 'Fallo obteniendo tokens de Google');
  }

  async getValidAccessToken() {
    if (!this.tokens) throw new Error('Google Workspace no está autenticado');
    if (Date.now() < (this.tokens.expiry_date - 60000) && this.tokens.access_token) {
      return this.tokens.access_token;
    }

    // Refrescar access token usando refresh token descifrado
    const refreshToken = decrypt(this.tokens.refresh_token_encrypted);
    if (!refreshToken) throw new Error('No hay refresh token válido disponible');

    const postData = new URLSearchParams({
      client_id: this.clientId,
      client_secret: this.clientSecret,
      refresh_token: refreshToken,
      grant_type: 'refresh_token'
    }).toString();

    const res = await this._httpRequest('oauth2.googleapis.com', '/token', 'POST', postData, {
      'Content-Type': 'application/x-www-form-urlencoded'
    });

    if (res.access_token) {
      this.tokens.access_token = res.access_token;
      this.tokens.expiry_date = Date.now() + (res.expires_in || 3600) * 1000;
      return this.tokens.access_token;
    }
    throw new Error('No se pudo refrescar el token de Google: ' + JSON.stringify(res));
  }

  list_actions() {
    return [
      // 1. Gmail
      {
        name: 'google_list_emails',
        description: 'Lista los correos más recientes en Gmail (asunto, remitente, snippet)',
        parameters: { maxResults: { type: 'number', description: 'Número máximo de correos a listar (ej. 5)' } },
        sensitive: false
      },
      {
        name: 'google_search_emails',
        description: 'Busca correos en Gmail usando sintaxis de búsqueda (ej. is:unread, from:persona, subject:reunion)',
        parameters: {
          query: { type: 'string', description: 'Consulta de búsqueda en Gmail' },
          maxResults: { type: 'number', description: 'Máximo de correos a retornar (ej. 5)' }
        },
        sensitive: false
      },
      {
        name: 'google_read_email',
        description: 'Lee el contenido completo, remitente, fecha y cuerpo de un correo en Gmail dado su messageId',
        parameters: { messageId: { type: 'string', description: 'ID del mensaje de Gmail' } },
        sensitive: false
      },
      {
        name: 'google_send_email',
        description: 'Envía un nuevo correo electrónico a través de Gmail',
        parameters: {
          to: { type: 'string', description: 'Dirección del destinatario' },
          subject: { type: 'string', description: 'Asunto del correo' },
          body: { type: 'string', description: 'Cuerpo o contenido del mensaje' }
        },
        sensitive: true
      },
      {
        name: 'google_reply_email',
        description: 'Responde a un correo electrónico existente en Gmail en su mismo hilo (thread)',
        parameters: {
          messageId: { type: 'string', description: 'ID del mensaje al que se responderá' },
          body: { type: 'string', description: 'Texto de la respuesta' }
        },
        sensitive: true
      },
      {
        name: 'google_archive_email',
        description: 'Archiva un correo de Gmail (quita la etiqueta INBOX)',
        parameters: { messageId: { type: 'string', description: 'ID del mensaje a archivar' } },
        sensitive: false
      },
      {
        name: 'google_label_email',
        description: 'Agrega o remueve etiquetas a un correo de Gmail (ej. STARRED, IMPORTANT, UNREAD)',
        parameters: {
          messageId: { type: 'string', description: 'ID del mensaje' },
          addLabelIds: { type: 'string', description: 'Etiquetas a añadir separadas por coma (ej. STARRED)' },
          removeLabelIds: { type: 'string', description: 'Etiquetas a remover separadas por coma (ej. UNREAD)' }
        },
        sensitive: false
      },
      {
        name: 'google_delete_email',
        description: 'Mueve un correo a la papelera de Gmail',
        parameters: { messageId: { type: 'string', description: 'ID del mensaje a eliminar' } },
        sensitive: true
      },

      // 2. Calendar
      {
        name: 'google_list_events',
        description: 'Consulta los eventos y citas próximas en Google Calendar',
        parameters: { maxResults: { type: 'number', description: 'Máximo de eventos a consultar (ej. 10)' } },
        sensitive: false
      },
      {
        name: 'google_create_event',
        description: 'Programa un nuevo evento o reunión en Google Calendar',
        parameters: {
          summary: { type: 'string', description: 'Título del evento' },
          startDateTime: { type: 'string', description: 'Fecha y hora de inicio (ISO 8601, ej. 2026-10-15T10:00:00)' },
          endDateTime: { type: 'string', description: 'Fecha y hora de fin (ISO 8601, ej. 2026-10-15T11:00:00)' },
          description: { type: 'string', description: 'Descripción o notas del evento' }
        },
        sensitive: true
      },
      {
        name: 'google_update_event',
        description: 'Modifica o reprograma un evento existente en Google Calendar',
        parameters: {
          eventId: { type: 'string', description: 'ID del evento a modificar' },
          summary: { type: 'string', description: 'Nuevo título opcional' },
          startDateTime: { type: 'string', description: 'Nueva fecha/hora inicio ISO 8601' },
          endDateTime: { type: 'string', description: 'Nueva fecha/hora fin ISO 8601' },
          description: { type: 'string', description: 'Nueva descripción opcional' }
        },
        sensitive: true
      },
      {
        name: 'google_delete_event',
        description: 'Elimina un evento existente de Google Calendar',
        parameters: { eventId: { type: 'string', description: 'ID del evento a eliminar' } },
        sensitive: true
      },

      // 3. Tasks
      {
        name: 'google_list_tasks',
        description: 'Obtiene las tareas pendientes registradas en Google Tasks',
        parameters: {},
        sensitive: false
      },
      {
        name: 'google_create_task',
        description: 'Crea una nueva tarea en Google Tasks',
        parameters: {
          title: { type: 'string', description: 'Título o nombre de la tarea' },
          notes: { type: 'string', description: 'Detalles o notas adicionales' },
          due: { type: 'string', description: 'Fecha límite (ISO 8601, ej. 2026-10-20T18:00:00Z)' }
        },
        sensitive: false
      },
      {
        name: 'google_complete_task',
        description: 'Marca una tarea de Google Tasks como completada',
        parameters: { taskId: { type: 'string', description: 'ID de la tarea a completar' } },
        sensitive: false
      },
      {
        name: 'google_delete_task',
        description: 'Elimina permanentemente una tarea de Google Tasks',
        parameters: { taskId: { type: 'string', description: 'ID de la tarea a eliminar' } },
        sensitive: true
      },

      // 4. Drive
      {
        name: 'google_list_drive_files',
        description: 'Lista los archivos recientes en Google Drive',
        parameters: { query: { type: 'string', description: 'Filtro por nombre opcional' } },
        sensitive: false
      },
      {
        name: 'google_search_drive_files',
        description: 'Busca archivos en Google Drive por texto o tipo de archivo',
        parameters: {
          query: { type: 'string', description: 'Término de búsqueda' },
          mimeType: { type: 'string', description: 'Filtro por tipo MIME opcional' }
        },
        sensitive: false
      },
      {
        name: 'google_read_drive_file',
        description: 'Lee o exporta el contenido en texto de un archivo en Google Drive (Docs a texto, Sheets a CSV, archivos texto)',
        parameters: { fileId: { type: 'string', description: 'ID del archivo en Google Drive' } },
        sensitive: false
      },
      {
        name: 'google_upload_drive_file',
        description: 'Sube un nuevo archivo de texto o documento a Google Drive',
        parameters: {
          name: { type: 'string', description: 'Nombre del archivo con extensión (ej. reporte.txt, notas.md)' },
          content: { type: 'string', description: 'Contenido del archivo en texto' },
          mimeType: { type: 'string', description: 'Tipo MIME (ej. text/plain, text/markdown)' }
        },
        sensitive: true
      },
      {
        name: 'google_move_drive_file',
        description: 'Mueve un archivo de Google Drive a otra carpeta',
        parameters: {
          fileId: { type: 'string', description: 'ID del archivo a mover' },
          newFolderId: { type: 'string', description: 'ID de la carpeta destino' }
        },
        sensitive: true
      },

      // 5. Docs, Sheets y Slides
      {
        name: 'google_read_doc',
        description: 'Lee el texto completo y título de un documento de Google Docs',
        parameters: { documentId: { type: 'string', description: 'ID del documento de Google Docs' } },
        sensitive: false
      },
      {
        name: 'google_create_doc',
        description: 'Crea un nuevo documento de Google Docs con título y texto inicial',
        parameters: {
          title: { type: 'string', description: 'Título del documento' },
          content: { type: 'string', description: 'Contenido inicial opcional' }
        },
        sensitive: true
      },
      {
        name: 'google_append_doc',
        description: 'Añade texto al final de un documento de Google Docs existente',
        parameters: {
          documentId: { type: 'string', description: 'ID del documento' },
          text: { type: 'string', description: 'Texto a añadir' }
        },
        sensitive: true
      },
      {
        name: 'google_read_sheet',
        description: 'Lee los valores de una tabla en Google Sheets por ID y rango',
        parameters: {
          spreadsheetId: { type: 'string', description: 'ID de la hoja de cálculo' },
          range: { type: 'string', description: 'Rango a leer (ej. A1:Z100 o Hoja1!A1:D20)' }
        },
        sensitive: false
      },
      {
        name: 'google_create_sheet',
        description: 'Crea una nueva hoja de cálculo en Google Sheets',
        parameters: { title: { type: 'string', description: 'Título de la hoja de cálculo' } },
        sensitive: true
      },
      {
        name: 'google_append_sheet_row',
        description: 'Inserta filas con datos en una hoja de cálculo Google Sheets',
        parameters: {
          spreadsheetId: { type: 'string', description: 'ID de la hoja de cálculo' },
          range: { type: 'string', description: 'Rango inicial (ej. Hoja1!A1 o A1)' },
          values: { type: 'string', description: 'Valores a insertar separados por coma (ej. "Dato1, Dato2, Dato3")' }
        },
        sensitive: true
      },
      {
        name: 'google_read_slides',
        description: 'Lee los títulos y diapositivas de una presentación Google Slides',
        parameters: { presentationId: { type: 'string', description: 'ID de la presentación' } },
        sensitive: false
      },
      {
        name: 'google_create_slides',
        description: 'Crea una nueva presentación en Google Slides',
        parameters: { title: { type: 'string', description: 'Título de la presentación' } },
        sensitive: true
      },
      {
        name: 'google_add_slide',
        description: 'Agrega una nueva diapositiva a una presentación Google Slides',
        parameters: { presentationId: { type: 'string', description: 'ID de la presentación' } },
        sensitive: true
      },

      // 6. Contacts (People API)
      {
        name: 'google_search_contacts',
        description: 'Busca contactos en Google Contacts por nombre, correo electrónico o teléfono',
        parameters: { query: { type: 'string', description: 'Nombre, email o teléfono a buscar' } },
        sensitive: false
      },

      // 7. YouTube Data API v3
      {
        name: 'google_search_youtube',
        description: 'Busca videos en YouTube por término de búsqueda (consume 100 unidades de cuota)',
        parameters: {
          query: { type: 'string', description: 'Término de búsqueda' },
          maxResults: { type: 'number', description: 'Máximo de resultados (ej. 5)' }
        },
        sensitive: false
      },
      {
        name: 'google_list_my_youtube_videos',
        description: 'Lista los videos publicados en el canal de YouTube del usuario autenticado',
        parameters: { maxResults: { type: 'number', description: 'Máximo de videos a listar (ej. 5)' } },
        sensitive: false
      },
      {
        name: 'google_get_youtube_video_stats',
        description: 'Obtiene las estadísticas de un video de YouTube (vistas, likes, comentarios)',
        parameters: { videoId: { type: 'string', description: 'ID del video de YouTube' } },
        sensitive: false
      }
    ];
  }

  async execute_action(actionName, params = {}) {
    // Si Google no está conectado, retornar mensaje claro para el function calling
    if (!this.connected || !this.tokens) {
      return {
        error: 'Google Workspace no está conectado. Por favor conecta tu cuenta de Google en Ajustes > Conexiones para poder acceder a esta función.',
        requiresConnection: true
      };
    }

    const token = await this.getValidAccessToken();

    switch (actionName) {
      // --- 1. GMAIL ---
      case 'google_list_emails': {
        const count = params.maxResults || 5;
        const listRes = await this._httpRequest('gmail.googleapis.com', `/gmail/v1/users/me/messages?maxResults=${count}`, 'GET', null, {
          'Authorization': `Bearer ${token}`
        });
        if (!listRes.messages || listRes.messages.length === 0) return { emails: [] };
        
        const details = [];
        for (const msg of listRes.messages.slice(0, count)) {
          const m = await this._httpRequest('gmail.googleapis.com', `/gmail/v1/users/me/messages/${msg.id}?format=metadata`, 'GET', null, {
            'Authorization': `Bearer ${token}`
          });
          const headers = m.payload?.headers || [];
          const subject = headers.find(h => h.name.toLowerCase() === 'subject')?.value || '(Sin asunto)';
          const from = headers.find(h => h.name.toLowerCase() === 'from')?.value || 'Desconocido';
          const date = headers.find(h => h.name.toLowerCase() === 'date')?.value || '';
          details.push({ id: msg.id, threadId: msg.threadId, subject, from, date, snippet: m.snippet });
        }
        return { emails: details };
      }

      case 'google_search_emails': {
        const query = params.query || '';
        const count = params.maxResults || 5;
        const listRes = await this._httpRequest('gmail.googleapis.com', `/gmail/v1/users/me/messages?q=${encodeURIComponent(query)}&maxResults=${count}`, 'GET', null, {
          'Authorization': `Bearer ${token}`
        });
        if (!listRes.messages || listRes.messages.length === 0) return { emails: [], query };
        
        const results = [];
        for (const msg of listRes.messages.slice(0, count)) {
          const m = await this._httpRequest('gmail.googleapis.com', `/gmail/v1/users/me/messages/${msg.id}?format=metadata`, 'GET', null, {
            'Authorization': `Bearer ${token}`
          });
          const headers = m.payload?.headers || [];
          const subject = headers.find(h => h.name.toLowerCase() === 'subject')?.value || '(Sin asunto)';
          const from = headers.find(h => h.name.toLowerCase() === 'from')?.value || 'Desconocido';
          const date = headers.find(h => h.name.toLowerCase() === 'date')?.value || '';
          results.push({ id: msg.id, subject, from, date, snippet: m.snippet });
        }
        return { query, emails: results };
      }

      case 'google_read_email': {
        const msgId = params.messageId;
        if (!msgId) throw new Error('Parámetro messageId requerido');
        const m = await this._httpRequest('gmail.googleapis.com', `/gmail/v1/users/me/messages/${msgId}?format=full`, 'GET', null, {
          'Authorization': `Bearer ${token}`
        });
        const headers = m.payload?.headers || [];
        const subject = headers.find(h => h.name.toLowerCase() === 'subject')?.value || '(Sin asunto)';
        const from = headers.find(h => h.name.toLowerCase() === 'from')?.value || 'Desconocido';
        const to = headers.find(h => h.name.toLowerCase() === 'to')?.value || '';
        const date = headers.find(h => h.name.toLowerCase() === 'date')?.value || '';

        // Extraer texto plano del cuerpo multipart
        let bodyText = '';
        function extractText(part) {
          if (!part) return;
          if (part.mimeType === 'text/plain' && part.body?.data) {
            bodyText += Buffer.from(part.body.data, 'base64').toString('utf8') + '\n';
          }
          if (part.parts && Array.isArray(part.parts)) {
            part.parts.forEach(extractText);
          }
        }
        if (m.payload) extractText(m.payload);
        if (!bodyText && m.snippet) bodyText = m.snippet;

        return { id: m.id, threadId: m.threadId, subject, from, to, date, body: bodyText.trim(), snippet: m.snippet };
      }

      case 'google_send_email': {
        const utf8Subject = `=?utf-8?B?${Buffer.from(params.subject || '').toString('base64')}?=`;
        const emailLines = [
          `To: ${params.to}`,
          'Content-Type: text/plain; charset=utf-8',
          'MIME-Version: 1.0',
          `Subject: ${utf8Subject}`,
          '',
          params.body || ''
        ];
        const rawEmail = Buffer.from(emailLines.join('\r\n')).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
        const sendRes = await this._httpRequest('gmail.googleapis.com', '/gmail/v1/users/me/messages/send', 'POST', JSON.stringify({ raw: rawEmail }), {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        });
        return { ok: true, messageId: sendRes.id };
      }

      case 'google_reply_email': {
        const msgId = params.messageId;
        if (!msgId) throw new Error('Parámetro messageId requerido');
        // Obtener mensaje original para extraer headers de respuesta
        const orig = await this._httpRequest('gmail.googleapis.com', `/gmail/v1/users/me/messages/${msgId}?format=metadata`, 'GET', null, {
          'Authorization': `Bearer ${token}`
        });
        const headers = orig.payload?.headers || [];
        const origSubject = headers.find(h => h.name.toLowerCase() === 'subject')?.value || '';
        const replyTo = headers.find(h => h.name.toLowerCase() === 'reply-to')?.value || 
                        headers.find(h => h.name.toLowerCase() === 'from')?.value || '';
        const messageIdHeader = headers.find(h => h.name.toLowerCase() === 'message-id')?.value || '';
        const subject = origSubject.toLowerCase().startsWith('re:') ? origSubject : `Re: ${origSubject}`;

        const emailLines = [
          `To: ${replyTo}`,
          `Subject: =?utf-8?B?${Buffer.from(subject).toString('base64')}?=`,
          messageIdHeader ? `In-Reply-To: ${messageIdHeader}` : '',
          messageIdHeader ? `References: ${messageIdHeader}` : '',
          'Content-Type: text/plain; charset=utf-8',
          'MIME-Version: 1.0',
          '',
          params.body || ''
        ].filter(Boolean);

        const rawEmail = Buffer.from(emailLines.join('\r\n')).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
        const sendRes = await this._httpRequest('gmail.googleapis.com', '/gmail/v1/users/me/messages/send', 'POST', JSON.stringify({
          raw: rawEmail,
          threadId: orig.threadId
        }), {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        });
        return { ok: true, messageId: sendRes.id, threadId: orig.threadId };
      }

      case 'google_archive_email': {
        const msgId = params.messageId;
        if (!msgId) throw new Error('Parámetro messageId requerido');
        await this._httpRequest('gmail.googleapis.com', `/gmail/v1/users/me/messages/${msgId}/modify`, 'POST', JSON.stringify({
          removeLabelIds: ['INBOX']
        }), {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        });
        return { ok: true, message: `Correo ${msgId} archivado exitosamente.` };
      }

      case 'google_label_email': {
        const msgId = params.messageId;
        if (!msgId) throw new Error('Parámetro messageId requerido');
        const addLabels = params.addLabelIds ? params.addLabelIds.split(',').map(s => s.trim()).filter(Boolean) : [];
        const removeLabels = params.removeLabelIds ? params.removeLabelIds.split(',').map(s => s.trim()).filter(Boolean) : [];

        const res = await this._httpRequest('gmail.googleapis.com', `/gmail/v1/users/me/messages/${msgId}/modify`, 'POST', JSON.stringify({
          addLabelIds: addLabels,
          removeLabelIds: removeLabels
        }), {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        });
        return { ok: true, labelIds: res.labelIds };
      }

      case 'google_delete_email': {
        const msgId = params.messageId;
        if (!msgId) throw new Error('Parámetro messageId requerido');
        await this._httpRequest('gmail.googleapis.com', `/gmail/v1/users/me/messages/${msgId}/trash`, 'POST', '{}', {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        });
        return { ok: true, message: `Correo ${msgId} movido a la papelera.` };
      }

      // --- 2. CALENDAR ---
      case 'google_list_events': {
        const timeMin = new Date().toISOString();
        const max = params.maxResults || 10;
        const res = await this._httpRequest('www.googleapis.com', `/calendar/v3/calendars/primary/events?timeMin=${encodeURIComponent(timeMin)}&maxResults=${max}&singleEvents=true&orderBy=startTime`, 'GET', null, {
          'Authorization': `Bearer ${token}`
        });
        const events = (res.items || []).map(e => ({
          id: e.id,
          summary: e.summary || '(Sin título)',
          start: e.start?.dateTime || e.start?.date,
          end: e.end?.dateTime || e.end?.date,
          location: e.location || '',
          htmlLink: e.htmlLink || ''
        }));
        return { events };
      }

      case 'google_create_event': {
        const body = {
          summary: params.summary,
          description: params.description || '',
          start: { dateTime: params.startDateTime },
          end: { dateTime: params.endDateTime }
        };
        const res = await this._httpRequest('www.googleapis.com', '/calendar/v3/calendars/primary/events', 'POST', JSON.stringify(body), {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        });
        return { ok: true, eventId: res.id, htmlLink: res.htmlLink };
      }

      case 'google_update_event': {
        const eventId = params.eventId;
        if (!eventId) throw new Error('Parámetro eventId requerido');
        const patchBody = {};
        if (params.summary) patchBody.summary = params.summary;
        if (params.description !== undefined) patchBody.description = params.description;
        if (params.startDateTime) patchBody.start = { dateTime: params.startDateTime };
        if (params.endDateTime) patchBody.end = { dateTime: params.endDateTime };

        const res = await this._httpRequest('www.googleapis.com', `/calendar/v3/calendars/primary/events/${eventId}`, 'PATCH', JSON.stringify(patchBody), {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        });
        return { ok: true, eventId: res.id, summary: res.summary, htmlLink: res.htmlLink };
      }

      case 'google_delete_event': {
        const eventId = params.eventId;
        if (!eventId) throw new Error('Parámetro eventId requerido');
        await this._httpRequest('www.googleapis.com', `/calendar/v3/calendars/primary/events/${eventId}`, 'DELETE', null, {
          'Authorization': `Bearer ${token}`
        });
        return { ok: true, message: `Evento ${eventId} eliminado de Google Calendar.` };
      }

      // --- 3. TASKS ---
      case 'google_list_tasks': {
        const res = await this._httpRequest('tasks.googleapis.com', '/tasks/v1/lists/@default/tasks?showCompleted=false', 'GET', null, {
          'Authorization': `Bearer ${token}`
        });
        const tasks = (res.items || []).map(t => ({ id: t.id, title: t.title, notes: t.notes, due: t.due, status: t.status }));
        return { tasks };
      }

      case 'google_create_task': {
        const body = { title: params.title, notes: params.notes || '', due: params.due || null };
        const res = await this._httpRequest('tasks.googleapis.com', '/tasks/v1/lists/@default/tasks', 'POST', JSON.stringify(body), {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        });
        return { ok: true, taskId: res.id, title: res.title };
      }

      case 'google_complete_task': {
        const taskId = params.taskId;
        if (!taskId) throw new Error('Parámetro taskId requerido');
        const res = await this._httpRequest('tasks.googleapis.com', `/tasks/v1/lists/@default/tasks/${taskId}`, 'PATCH', JSON.stringify({
          status: 'completed'
        }), {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        });
        return { ok: true, taskId: res.id, status: res.status };
      }

      case 'google_delete_task': {
        const taskId = params.taskId;
        if (!taskId) throw new Error('Parámetro taskId requerido');
        await this._httpRequest('tasks.googleapis.com', `/tasks/v1/lists/@default/tasks/${taskId}`, 'DELETE', null, {
          'Authorization': `Bearer ${token}`
        });
        return { ok: true, message: `Tarea ${taskId} eliminada de Google Tasks.` };
      }

      // --- 4. DRIVE ---
      case 'google_list_drive_files': {
        let q = "trashed = false";
        if (params.query) q += ` and name contains '${params.query}'`;
        const res = await this._httpRequest('www.googleapis.com', `/drive/v3/files?q=${encodeURIComponent(q)}&pageSize=10&fields=files(id,name,mimeType,webViewLink)`, 'GET', null, {
          'Authorization': `Bearer ${token}`
        });
        return { files: res.files || [] };
      }

      case 'google_search_drive_files': {
        let q = "trashed = false";
        if (params.query) q += ` and (name contains '${params.query}' or fullText contains '${params.query}')`;
        if (params.mimeType) q += ` and mimeType = '${params.mimeType}'`;
        const res = await this._httpRequest('www.googleapis.com', `/drive/v3/files?q=${encodeURIComponent(q)}&pageSize=15&fields=files(id,name,mimeType,size,modifiedTime,webViewLink)`, 'GET', null, {
          'Authorization': `Bearer ${token}`
        });
        return { files: res.files || [] };
      }

      case 'google_read_drive_file': {
        const fileId = params.fileId;
        if (!fileId) throw new Error('Parámetro fileId requerido');
        
        // Obtener metadatos del archivo para saber su tipo
        const meta = await this._httpRequest('www.googleapis.com', `/drive/v3/files/${fileId}?fields=id,name,mimeType`, 'GET', null, {
          'Authorization': `Bearer ${token}`
        });

        // Si es Google Doc, exportar a texto
        if (meta.mimeType === 'application/vnd.google-apps.document') {
          const text = await this._httpRequest('www.googleapis.com', `/drive/v3/files/${fileId}/export?mimeType=text/plain`, 'GET', null, {
            'Authorization': `Bearer ${token}`
          });
          return { id: fileId, name: meta.name, mimeType: meta.mimeType, content: typeof text === 'string' ? text : JSON.stringify(text) };
        }

        // Si es Google Sheet, exportar a CSV
        if (meta.mimeType === 'application/vnd.google-apps.spreadsheet') {
          const csv = await this._httpRequest('www.googleapis.com', `/drive/v3/files/${fileId}/export?mimeType=text/csv`, 'GET', null, {
            'Authorization': `Bearer ${token}`
          });
          return { id: fileId, name: meta.name, mimeType: meta.mimeType, content: typeof csv === 'string' ? csv : JSON.stringify(csv) };
        }

        // Descarga de archivo estándar
        const content = await this._httpRequest('www.googleapis.com', `/drive/v3/files/${fileId}?alt=media`, 'GET', null, {
          'Authorization': `Bearer ${token}`
        });
        return { id: fileId, name: meta.name, mimeType: meta.mimeType, content: typeof content === 'string' ? content : JSON.stringify(content) };
      }

      case 'google_upload_drive_file': {
        const name = params.name || `archivo_${Date.now()}.txt`;
        const content = params.content || '';
        const mimeType = params.mimeType || 'text/plain';

        const boundary = '-------314159265358979323846';
        const delimiter = `\r\n--${boundary}\r\n`;
        const closeDelimiter = `\r\n--${boundary}--`;

        const metadata = JSON.stringify({ name, mimeType });
        const multipartBody = 
          delimiter +
          'Content-Type: application/json; charset=UTF-8\r\n\r\n' +
          metadata +
          delimiter +
          `Content-Type: ${mimeType}\r\n\r\n` +
          content +
          closeDelimiter;

        const res = await this._httpRequest('www.googleapis.com', '/upload/drive/v3/files?uploadType=multipart', 'POST', multipartBody, {
          'Authorization': `Bearer ${token}`,
          'Content-Type': `multipart/related; boundary=${boundary}`
        });
        return { ok: true, fileId: res.id, name: res.name, mimeType: res.mimeType };
      }

      case 'google_move_drive_file': {
        const fileId = params.fileId;
        const newFolderId = params.newFolderId;
        if (!fileId || !newFolderId) throw new Error('fileId y newFolderId son requeridos');

        // Consultar carpetas padres previas
        const meta = await this._httpRequest('www.googleapis.com', `/drive/v3/files/${fileId}?fields=parents`, 'GET', null, {
          'Authorization': `Bearer ${token}`
        });
        const prevParents = (meta.parents || []).join(',');

        const res = await this._httpRequest('www.googleapis.com', `/drive/v3/files/${fileId}?addParents=${encodeURIComponent(newFolderId)}&removeParents=${encodeURIComponent(prevParents)}&fields=id,parents`, 'PATCH', '{}', {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        });
        return { ok: true, fileId: res.id, parents: res.parents };
      }

      // --- 5. DOCS, SHEETS Y SLIDES ---
      case 'google_read_doc': {
        const docId = params.documentId;
        if (!docId) throw new Error('Parámetro documentId requerido');
        const doc = await this._httpRequest('docs.googleapis.com', `/v1/documents/${docId}`, 'GET', null, {
          'Authorization': `Bearer ${token}`
        });

        let fullText = '';
        (doc.body?.content || []).forEach(struct => {
          if (struct.paragraph?.elements) {
            struct.paragraph.elements.forEach(elem => {
              if (elem.textRun?.content) fullText += elem.textRun.content;
            });
          }
        });
        return { id: doc.documentId, title: doc.title, text: fullText.trim() };
      }

      case 'google_create_doc': {
        const title = params.title || 'Nuevo Documento JARVIS';
        const doc = await this._httpRequest('docs.googleapis.com', '/v1/documents', 'POST', JSON.stringify({ title }), {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        });

        if (params.content && doc.documentId) {
          await this._httpRequest('docs.googleapis.com', `/v1/documents/${doc.documentId}:batchUpdate`, 'POST', JSON.stringify({
            requests: [{
              insertText: {
                location: { index: 1 },
                text: params.content
              }
            }]
          }), {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          });
        }
        return { ok: true, documentId: doc.documentId, title: doc.title };
      }

      case 'google_append_doc': {
        const docId = params.documentId;
        const text = params.text || '';
        if (!docId || !text) throw new Error('documentId y text son requeridos');

        await this._httpRequest('docs.googleapis.com', `/v1/documents/${docId}:batchUpdate`, 'POST', JSON.stringify({
          requests: [{
            insertText: {
              endOfSegmentLocation: {},
              text: '\n' + text
            }
          }]
        }), {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        });
        return { ok: true, documentId: docId, message: 'Texto añadido exitosamente al documento.' };
      }

      case 'google_read_sheet': {
        const sheetId = params.spreadsheetId;
        const range = params.range || 'A1:Z100';
        if (!sheetId) throw new Error('Parámetro spreadsheetId requerido');

        const res = await this._httpRequest('sheets.googleapis.com', `/v4/spreadsheets/${sheetId}/values/${encodeURIComponent(range)}`, 'GET', null, {
          'Authorization': `Bearer ${token}`
        });
        return { spreadsheetId: sheetId, range: res.range, values: res.values || [] };
      }

      case 'google_create_sheet': {
        const title = params.title || 'Nueva Hoja JARVIS';
        const res = await this._httpRequest('sheets.googleapis.com', '/v4/spreadsheets', 'POST', JSON.stringify({
          properties: { title }
        }), {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        });
        return { ok: true, spreadsheetId: res.spreadsheetId, title: res.properties?.title, url: res.spreadsheetUrl };
      }

      case 'google_append_sheet_row': {
        const sheetId = params.spreadsheetId;
        const range = params.range || 'A1';
        if (!sheetId) throw new Error('Parámetro spreadsheetId requerido');

        let rowValues = [];
        if (typeof params.values === 'string') {
          rowValues = params.values.split(',').map(v => v.trim());
        } else if (Array.isArray(params.values)) {
          rowValues = params.values;
        }

        const res = await this._httpRequest('sheets.googleapis.com', `/v4/spreadsheets/${sheetId}/values/${encodeURIComponent(range)}:append?valueInputOption=USER_ENTERED`, 'POST', JSON.stringify({
          values: [rowValues]
        }), {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        });
        return { ok: true, updatedRange: res.updates?.updatedRange, updatedRows: res.updates?.updatedRows };
      }

      case 'google_read_slides': {
        const presId = params.presentationId;
        if (!presId) throw new Error('Parámetro presentationId requerido');

        const pres = await this._httpRequest('slides.googleapis.com', `/v1/presentations/${presId}`, 'GET', null, {
          'Authorization': `Bearer ${token}`
        });

        const slides = (pres.slides || []).map((s, idx) => {
          let text = '';
          (s.pageElements || []).forEach(el => {
            if (el.shape?.text?.textElements) {
              el.shape.text.textElements.forEach(te => {
                if (te.textRun?.content) text += te.textRun.content;
              });
            }
          });
          return { slideNumber: idx + 1, slideId: s.objectId, text: text.trim() };
        });

        return { presentationId: pres.presentationId, title: pres.title, slidesCount: slides.length, slides };
      }

      case 'google_create_slides': {
        const title = params.title || 'Nueva Presentación JARVIS';
        const res = await this._httpRequest('slides.googleapis.com', '/v1/presentations', 'POST', JSON.stringify({ title }), {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        });
        return { ok: true, presentationId: res.presentationId, title: res.title };
      }

      case 'google_add_slide': {
        const presId = params.presentationId;
        if (!presId) throw new Error('Parámetro presentationId requerido');

        const res = await this._httpRequest('slides.googleapis.com', `/v1/presentations/${presId}:batchUpdate`, 'POST', JSON.stringify({
          requests: [{
            createSlide: {
              insertionIndex: 1
            }
          }]
        }), {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        });
        return { ok: true, presentationId: presId, newSlideId: res.replies?.[0]?.createSlide?.objectId };
      }

      // --- 6. CONTACTS (PEOPLE API) ---
      case 'google_search_contacts': {
        const query = (params.query || '').trim();
        if (!query) throw new Error('Parámetro query requerido');

        try {
          const res = await this._httpRequest('people.googleapis.com', `/v1/people:searchContacts?query=${encodeURIComponent(query)}&readMask=names,emailAddresses,phoneNumbers`, 'GET', null, {
            'Authorization': `Bearer ${token}`
          });
          const results = (res.results || []).map(r => {
            const p = r.person || {};
            const name = p.names?.[0]?.displayName || 'Sin nombre';
            const email = p.emailAddresses?.[0]?.value || '';
            const phone = p.phoneNumbers?.[0]?.value || '';
            return { name, email, phone };
          });
          return { query, contacts: results };
        } catch (searchErr) {
          // Fallback a listado de conexiones con filtrado local
          const listRes = await this._httpRequest('people.googleapis.com', `/v1/people/me/connections?pageSize=50&personFields=names,emailAddresses,phoneNumbers`, 'GET', null, {
            'Authorization': `Bearer ${token}`
          });
          const qLower = query.toLowerCase();
          const filtered = (listRes.connections || []).filter(c => {
            const name = (c.names?.[0]?.displayName || '').toLowerCase();
            const email = (c.emailAddresses?.[0]?.value || '').toLowerCase();
            const phone = (c.phoneNumbers?.[0]?.value || '').toLowerCase();
            return name.includes(qLower) || email.includes(qLower) || phone.includes(qLower);
          }).map(c => ({
            name: c.names?.[0]?.displayName || 'Sin nombre',
            email: c.emailAddresses?.[0]?.value || '',
            phone: c.phoneNumbers?.[0]?.value || ''
          }));
          return { query, contacts: filtered };
        }
      }

      // --- 7. YOUTUBE DATA API V3 ---
      case 'google_search_youtube': {
        const query = params.query || '';
        const max = params.maxResults || 5;
        const res = await this._httpRequest('youtube.googleapis.com', `/youtube/v3/search?part=snippet&type=video&q=${encodeURIComponent(query)}&maxResults=${max}`, 'GET', null, {
          'Authorization': `Bearer ${token}`
        });
        const videos = (res.items || []).map(item => ({
          videoId: item.id?.videoId,
          title: item.snippet?.title,
          channelTitle: item.snippet?.channelTitle,
          description: item.snippet?.description,
          publishedAt: item.snippet?.publishedAt,
          url: `https://www.youtube.com/watch?v=${item.id?.videoId}`
        }));
        return { query, videos };
      }

      case 'google_list_my_youtube_videos': {
        const max = params.maxResults || 5;
        const res = await this._httpRequest('youtube.googleapis.com', `/youtube/v3/search?part=snippet&forMine=true&type=video&maxResults=${max}`, 'GET', null, {
          'Authorization': `Bearer ${token}`
        });
        const videos = (res.items || []).map(item => ({
          videoId: item.id?.videoId,
          title: item.snippet?.title,
          publishedAt: item.snippet?.publishedAt,
          description: item.snippet?.description,
          url: `https://www.youtube.com/watch?v=${item.id?.videoId}`
        }));
        return { videos };
      }

      case 'google_get_youtube_video_stats': {
        const videoId = params.videoId;
        if (!videoId) throw new Error('Parámetro videoId requerido');

        const res = await this._httpRequest('youtube.googleapis.com', `/youtube/v3/videos?part=snippet,statistics&id=${encodeURIComponent(videoId)}`, 'GET', null, {
          'Authorization': `Bearer ${token}`
        });

        const item = res.items?.[0];
        if (!item) return { error: `Video ${videoId} no encontrado` };

        return {
          videoId,
          title: item.snippet?.title,
          channel: item.snippet?.channelTitle,
          publishedAt: item.snippet?.publishedAt,
          statistics: {
            views: parseInt(item.statistics?.viewCount || '0', 10),
            likes: parseInt(item.statistics?.likeCount || '0', 10),
            comments: parseInt(item.statistics?.commentCount || '0', 10)
          }
        };
      }

      default:
        throw new Error(`Acción desconocida en Google Workspace: ${actionName}`);
    }
  }

  _httpRequest(hostname, path, method, data, headers = {}) {
    return new Promise((resolve, reject) => {
      const options = { hostname, path, method, headers };
      const req = https.request(options, (res) => {
        let body = '';
        res.on('data', chunk => body += chunk);
        res.on('end', () => {
          try {
            const parsed = body ? JSON.parse(body) : {};
            if (res.statusCode >= 200 && res.statusCode < 300) {
              resolve(parsed);
            } else {
              reject(new Error(`API Error [${res.statusCode}]: ${JSON.stringify(parsed)}`));
            }
          } catch (e) {
            if (res.statusCode >= 200 && res.statusCode < 300) resolve(body);
            else reject(new Error(`API Response Error [${res.statusCode}]: ${body}`));
          }
        });
      });
      req.on('error', reject);
      if (data) req.write(data);
      req.end();
    });
  }
}

const connectorInstance = new GoogleWorkspaceConnector();
connectorInstance.GoogleWorkspaceConnector = GoogleWorkspaceConnector;
module.exports = connectorInstance;
