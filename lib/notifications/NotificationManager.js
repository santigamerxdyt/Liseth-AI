/**
 * Notificador Multicanal: WhatsApp Business Cloud API & Telegram Bot
 * Incluye gestión de ventana de 24h de Meta, bot interactivo de Telegram (/start, /estado, /resumen)
 * y alertas proactivas sin restricción de 24h en Telegram
 */

const https = require('https');

class NotificationManager {
  constructor() {
    this.config = {
      quietHoursStart: '22:00',
      quietHoursEnd: '07:00',
      enableWhatsApp: false,
      enableTelegram: true
    };
    // Registro de marcas de tiempo de mensajes entrantes para validar ventana de 24h de Meta
    this.incomingWhatsAppWindows = new Map();
    this.telegramPollingActive = false;
    this.telegramPollOffset = 0;
  }

  setConfig(cfg) {
    this.config = { ...this.config, ...cfg };
  }

  recordIncomingWhatsApp(phoneNumber) {
    if (!phoneNumber) return;
    const cleanPhone = phoneNumber.replace(/[^0-9]/g, '');
    this.incomingWhatsAppWindows.set(cleanPhone, Date.now());
  }

  isWithinWhatsApp24hWindow(phoneNumber) {
    if (!phoneNumber) return false;
    const cleanPhone = phoneNumber.replace(/[^0-9]/g, '');
    const lastSeen = this.incomingWhatsAppWindows.get(cleanPhone);
    if (!lastSeen) return false;
    const elapsedMs = Date.now() - lastSeen;
    return elapsedMs <= 24 * 60 * 60 * 1000;
  }

  isQuietHour() {
    try {
      const now = new Date();
      const currentMinutes = now.getHours() * 60 + now.getMinutes();

      const [startH, startM] = (this.config.quietHoursStart || '22:00').split(':').map(Number);
      const [endH, endM] = (this.config.quietHoursEnd || '07:00').split(':').map(Number);

      const startMinutes = startH * 60 + startM;
      const endMinutes = endH * 60 + endM;

      if (startMinutes > endMinutes) {
        // Cruza la medianoche (ej. 22:00 a 07:00)
        return currentMinutes >= startMinutes || currentMinutes < endMinutes;
      } else {
        return currentMinutes >= startMinutes && currentMinutes < endMinutes;
      }
    } catch (e) {
      return false;
    }
  }

  async sendAlert(text, forceBypassQuiet = false) {
    if (!forceBypassQuiet && this.isQuietHour()) {
      console.log(`[Notificaciones] Mensaje silenciado por horario de descanso: ${text.slice(0, 50)}...`);
      return { skipped: true, reason: 'quiet_hours' };
    }

    const results = {};
    if (this.config.enableTelegram || process.env.TELEGRAM_BOT_TOKEN) {
      results.telegram = await this.sendTelegram(text);
    }
    if (this.config.enableWhatsApp || process.env.META_WA_ACCESS_TOKEN) {
      results.whatsapp = await this.sendWhatsApp(text);
    }
    return results;
  }

  async sendTelegram(text, targetChatId = null) {
    const token = process.env.TELEGRAM_BOT_TOKEN;
    const chatId = targetChatId || process.env.TELEGRAM_CHAT_ID;
    if (!token || !chatId) {
      return { ok: false, error: 'Credenciales de Telegram no configuradas' };
    }

    const postData = JSON.stringify({
      chat_id: chatId,
      text: `👑 *JARVIS / Liseth*\n\n${text}`,
      parse_mode: 'Markdown'
    });

    try {
      return await this._httpRequest('api.telegram.org', `/bot${token}/sendMessage`, 'POST', postData, {
        'Content-Type': 'application/json'
      });
    } catch (e) {
      return { ok: false, error: e.message };
    }
  }

  async sendWhatsApp(text, targetPhone = null, options = {}) {
    const recipient = targetPhone || process.env.META_WA_RECIPIENT_PHONE;
    if (!recipient) {
      return { ok: false, error: 'Número de destinatario de WhatsApp no especificado' };
    }

    const cleanRecipient = recipient.replace(/[^0-9]/g, '');

    // Validación de la política de ventana de 24 horas de Meta
    const isInsideWindow = this.isWithinWhatsApp24hWindow(cleanRecipient);
    const isTemplate = Boolean(options.templateName);

    if (!isInsideWindow && !isTemplate && !options.bypassWindowCheck) {
      // Política de Meta: Mensajes libres fuera de 24 horas son rechazados por la API de Meta
      console.warn(`[WhatsApp] Advertencia de política Meta: Mensaje proactivo fuera de ventana de 24h para ${cleanRecipient}. Se requiere plantilla aprobada.`);
      // Si el usuario no ha enviado mensaje en 24h, se notifica la restricción
      return {
        ok: false,
        error: 'Restricción de Meta WhatsApp: La ventana de atención al cliente de 24 horas está inactiva. Para iniciar conversaciones proactivas fuera de 24h, Meta exige el uso de Plantillas de Mensaje (Templates) pre-aprobadas.',
        requiresTemplate: true,
        recipient: cleanRecipient
      };
    }

    const token = process.env.META_WA_ACCESS_TOKEN;
    const phoneId = process.env.META_WA_PHONE_NUMBER_ID;
    if (!token || !phoneId) {
      return { ok: false, error: 'Credenciales de WhatsApp Meta no configuradas' };
    }

    const postData = JSON.stringify({
      messaging_product: 'whatsapp',
      to: cleanRecipient,
      type: 'text',
      text: { body: `👑 JARVIS: ${text}` }
    });

    try {
      return await this._httpRequest('graph.facebook.com', `/v21.0/${phoneId}/messages`, 'POST', postData, {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      });
    } catch (e) {
      return { ok: false, error: e.message };
    }
  }

  // --- BOT INTERACTIVO DE TELEGRAM (/start, /estado, /resumen) ---

  startTelegramBot() {
    const token = process.env.TELEGRAM_BOT_TOKEN;
    if (!token || this.telegramPollingActive) return;

    this.telegramPollingActive = true;
    console.log('✓ Bot de Telegram interactivo (/start, /estado, /resumen) INICIADO');
    this._pollTelegramUpdates();
  }

  stopTelegramBot() {
    this.telegramPollingActive = false;
  }

  async _pollTelegramUpdates() {
    const token = process.env.TELEGRAM_BOT_TOKEN;
    if (!token || !this.telegramPollingActive) return;

    try {
      const path = `/bot${token}/getUpdates?offset=${this.telegramPollOffset}&timeout=20`;
      const res = await this._httpRequest('api.telegram.org', path, 'GET');

      if (res.ok && Array.isArray(res.result)) {
        for (const update of res.result) {
          this.telegramPollOffset = update.update_id + 1;
          if (update.message && update.message.text) {
            await this.handleTelegramMessage(update.message);
          }
        }
      }
    } catch (e) {
      // Backoff suave ante errores de red
      await new Promise(r => setTimeout(r, 5000));
    }

    if (this.telegramPollingActive) {
      setImmediate(() => this._pollTelegramUpdates());
    }
  }

  async handleTelegramMessage(message) {
    const chatId = message.chat.id;
    const text = (message.text || '').trim();
    console.log(`[Telegram Recibido de ${chatId}]: ${text}`);

    // 1. Comando /start
    if (text === '/start') {
      const welcome = `👑 *Hola Santiago, soy Liseth.*\nTu Asistente Personal de Inteligencia Artificial.\n\nPuedes hablar conmigo normalmente o utilizar estos comandos directos:\n• /estado - Monitoreo del sistema, tokens y cerebro activo\n• /resumen - Agenda, eventos y tareas pendientes de hoy`;
      return this.sendTelegram(welcome, chatId);
    }

    // 2. Comando /estado
    if (text === '/estado') {
      const BrainRouter = require('../ai/BrainRouter');
      const GoogleWorkspace = require('../connectors/GoogleWorkspaceConnector');
      const todayTokens = (BrainRouter.tokenStats?.today?.input || 0) + (BrainRouter.tokenStats?.today?.output || 0);
      const activeBrain = BrainRouter.getEffectiveBrain().toUpperCase();
      const googleStatus = GoogleWorkspace.connected ? '🟢 Conectado' : '⚪ Desconectado';

      const statusMsg = `📊 *Estado del Asistente (JARVIS / Liseth)*:\n• Cerebro Activo: *${activeBrain}*\n• Consumo de Tokens Hoy: *${todayTokens.toLocaleString()} tokens*\n• Google Workspace: *${googleStatus}*\n• Uptime: *${(process.uptime() / 3600).toFixed(1)} horas*`;
      return this.sendTelegram(statusMsg, chatId);
    }

    // 3. Comando /resumen
    if (text === '/resumen') {
      let scheduleText = '• No hay eventos programados en su agenda inmediata.';
      try {
        const GoogleWorkspace = require('../connectors/GoogleWorkspaceConnector');
        if (GoogleWorkspace.connected) {
          const eventsData = await GoogleWorkspace.execute_action('google_list_events', { maxResults: 5 });
          if (eventsData.events && eventsData.events.length > 0) {
            scheduleText = eventsData.events.map(e => `• ${e.summary} (${e.start})`).join('\n');
          }
        }
      } catch (e) {}

      const summaryMsg = `📋 *Resumen Ejecutivo del Día*:\n\n*Agenda Próxima*:\n${scheduleText}\n\nTodo listo para avanzar, Santiago.`;
      return this.sendTelegram(summaryMsg, chatId);
    }

    // 4. Mensajes conversacionales normales: Procesar con BrainRouter y responder en el mismo chat
    try {
      const BrainRouter = require('../ai/BrainRouter');
      const aiRes = await BrainRouter.generateResponse({
        systemInstruction: 'Eres Liseth, asistente personal en Telegram. Responde con calidez, pulcritud, brevedad y alta capacidad de resolución.',
        contents: [{ role: 'user', parts: [{ text }] }]
      });
      if (aiRes.text) {
        return this.sendTelegram(aiRes.text, chatId);
      }
    } catch (err) {
      return this.sendTelegram(`⚠️ Ocurrió un error procesando su mensaje: ${err.message}`, chatId);
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
            resolve(parsed);
          } catch (e) {
            resolve({ raw: body, status: res.statusCode });
          }
        });
      });
      req.on('error', reject);
      if (data) req.write(data);
      req.end();
    });
  }
}

const notificationInstance = new NotificationManager();
notificationInstance.NotificationManager = NotificationManager;
module.exports = notificationInstance;
