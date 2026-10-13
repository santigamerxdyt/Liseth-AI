/**
 * Notificador Multicanal: WhatsApp Business Cloud API & Telegram Bot
 * Incluye alertas de errores, resúmenes, recordatorios y verificación de horas de silencio
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
  }

  setConfig(cfg) {
    this.config = { ...this.config, ...cfg };
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

  async sendTelegram(text) {
    const token = process.env.TELEGRAM_BOT_TOKEN;
    const chatId = process.env.TELEGRAM_CHAT_ID;
    if (!token || !chatId) {
      return { ok: false, error: 'Credenciales de Telegram no configuradas' };
    }

    const postData = JSON.stringify({
      chat_id: chatId,
      text: `👑 *JARVIS / Liseth Alerta*\n\n${text}`,
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

  async sendWhatsApp(text) {
    const token = process.env.META_WA_ACCESS_TOKEN;
    const phoneId = process.env.META_WA_PHONE_NUMBER_ID;
    const recipient = process.env.META_WA_RECIPIENT_PHONE;
    if (!token || !phoneId || !recipient) {
      return { ok: false, error: 'Credenciales de WhatsApp Meta no configuradas' };
    }

    const postData = JSON.stringify({
      messaging_product: 'whatsapp',
      to: recipient,
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

module.exports = new NotificationManager();
