/**
 * Conector de Google Workspace (Gmail, Calendar, Drive, Tasks, Sheets, Docs, Contacts, YouTube)
 * Utiliza llamadas HTTP directas con OAuth 2.0 y tokens cifrados (Sin dependencias pesadas)
 */
const https = require('https');
const BaseConnector = require('./BaseConnector');
const { encrypt, decrypt } = require('../crypto');

class GoogleWorkspaceConnector extends BaseConnector {
  constructor() {
    super('google_workspace', 'Google Workspace', 'Integración con Gmail, Calendar, Drive, Tasks, Sheets y Docs');
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
      'https://www.googleapis.com/auth/drive.file',
      'https://www.googleapis.com/auth/tasks',
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

    // Refrescar access token
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
      {
        name: 'google_list_emails',
        description: 'Lista los correos recientes de Gmail (asunto, remitente, snippet)',
        parameters: { maxResults: { type: 'number', description: 'Número máximo de correos (ej. 5)' } },
        sensitive: false
      },
      {
        name: 'google_send_email',
        description: 'Envía un correo electrónico a través de Gmail',
        parameters: {
          to: { type: 'string', description: 'Destinatario' },
          subject: { type: 'string', description: 'Asunto' },
          body: { type: 'string', description: 'Contenido del correo' }
        },
        sensitive: true // Requiere confirmación si no está preautorizado
      },
      {
        name: 'google_list_events',
        description: 'Lista los eventos próximos en Google Calendar',
        parameters: { maxResults: { type: 'number', description: 'Máximo de eventos (ej. 10)' } },
        sensitive: false
      },
      {
        name: 'google_create_event',
        description: 'Crea un nuevo evento o cita en Google Calendar',
        parameters: {
          summary: { type: 'string', description: 'Título del evento' },
          startDateTime: { type: 'string', description: 'Fecha y hora inicio (ISO 8601)' },
          endDateTime: { type: 'string', description: 'Fecha y hora fin (ISO 8601)' },
          description: { type: 'string', description: 'Detalles o ubicación' }
        },
        sensitive: true
      },
      {
        name: 'google_list_tasks',
        description: 'Obtiene la lista de tareas pendientes de Google Tasks',
        parameters: {},
        sensitive: false
      },
      {
        name: 'google_create_task',
        description: 'Crea una nueva tarea en Google Tasks',
        parameters: {
          title: { type: 'string', description: 'Título de la tarea' },
          notes: { type: 'string', description: 'Notas opcionales' },
          due: { type: 'string', description: 'Fecha límite (ISO 8601)' }
        },
        sensitive: false
      },
      {
        name: 'google_list_drive_files',
        description: 'Busca o lista archivos en Google Drive',
        parameters: { query: { type: 'string', description: 'Término de búsqueda o vacío' } },
        sensitive: false
      }
    ];
  }

  async execute_action(actionName, params = {}) {
    const token = await this.getValidAccessToken();

    switch (actionName) {
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
          details.push({ id: msg.id, subject, from, date, snippet: m.snippet });
        }
        return { emails: details };
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
          location: e.location || ''
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

      case 'google_list_tasks': {
        const res = await this._httpRequest('tasks.googleapis.com', '/tasks/v1/lists/@default/tasks?showCompleted=false', 'GET', null, {
          'Authorization': `Bearer ${token}`
        });
        const tasks = (res.items || []).map(t => ({ id: t.id, title: t.title, notes: t.notes, due: t.due }));
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

      case 'google_list_drive_files': {
        let q = "trashed = false";
        if (params.query) q += ` and name contains '${params.query}'`;
        const res = await this._httpRequest('www.googleapis.com', `/drive/v3/files?q=${encodeURIComponent(q)}&pageSize=10&fields=files(id,name,mimeType,webViewLink)`, 'GET', null, {
          'Authorization': `Bearer ${token}`
        });
        return { files: res.files || [] };
      }

      default:
        throw new Error(`Acción desconocida: ${actionName}`);
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

module.exports = new GoogleWorkspaceConnector();
