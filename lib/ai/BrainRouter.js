/**
 * BrainRouter - Cerebro Dual con Failover Automático y Monitor de Tokens
 * Maneja Gemini (Primario) y Anthropic Claude (Secundario) con interfaz común y Function Calling
 */
const https = require('https');
const fs = require('fs');
const path = require('path');
const NotificationManager = require('../notifications/NotificationManager');

const TOKEN_USAGE_FILE = path.join(__dirname, '..', '..', 'data', 'token_usage.json');

class BrainRouter {
  constructor() {
    this.primaryBrain = 'gemini';
    this.forcedBrain = null; // 'gemini' | 'claude' | null
    this.activeBrain = 'gemini';
    this.lastFailover = null;
    this.tokenStats = {
      today: { input: 0, output: 0, costEstimate: 0 },
      month: { input: 0, output: 0 },
      history: [] // [{ date: '2026-10-12', brain: 'gemini', input: 120, output: 85 }]
    };
    this.limits = {
      dailyTokenLimit: 100000,
      alertThresholdPct: 80
    };
    this.initStats();
  }

  initStats() {
    try {
      if (fs.existsSync(TOKEN_USAGE_FILE)) {
        const raw = fs.readFileSync(TOKEN_USAGE_FILE, 'utf8');
        const data = JSON.parse(raw);
        this.tokenStats = data.stats || this.tokenStats;
        this.limits = data.limits || this.limits;
      }
    } catch (e) {
      this.saveStats();
    }
  }

  saveStats() {
    try {
      const dir = path.dirname(TOKEN_USAGE_FILE);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(TOKEN_USAGE_FILE, JSON.stringify({ stats: this.tokenStats, limits: this.limits }, null, 2), 'utf8');
    } catch (e) {}
  }

  recordUsage(brain, inputTokens = 0, outputTokens = 0) {
    const todayStr = new Date().toISOString().split('T')[0];
    this.tokenStats.today.input += inputTokens;
    this.tokenStats.today.output += outputTokens;
    this.tokenStats.month.input += inputTokens;
    this.tokenStats.month.output += outputTokens;

    this.tokenStats.history.push({
      timestamp: new Date().toISOString(),
      date: todayStr,
      brain,
      inputTokens,
      outputTokens
    });

    if (this.tokenStats.history.length > 500) {
      this.tokenStats.history = this.tokenStats.history.slice(-500);
    }

    this.saveStats();

    // Verificación de alerta de umbral
    const totalToday = this.tokenStats.today.input + this.tokenStats.today.output;
    const pct = Math.round((totalToday / this.limits.dailyTokenLimit) * 100);
    if (pct >= this.limits.alertThresholdPct && pct < (this.limits.alertThresholdPct + 5)) {
      NotificationManager.sendAlert(`⚠️ Aviso de consumo: Ha utilizado el ${pct}% de su límite diario de tokens (${totalToday} / ${this.limits.dailyTokenLimit}).`);
    }
  }

  setForcedBrain(brain) {
    if (brain === 'gemini' || brain === 'claude' || brain === null) {
      this.forcedBrain = brain;
      this.activeBrain = brain || this.primaryBrain;
      return true;
    }
    return false;
  }

  getEffectiveBrain() {
    if (this.forcedBrain) return this.forcedBrain;
    return this.activeBrain;
  }

  /**
   * Ejecución inteligente con failover automático
   * @param {Object} options { systemInstruction, contents, tools, apiKeyGemini, apiKeyClaude }
   */
  async generateResponse(options) {
    const targetBrain = this.getEffectiveBrain();
    const geminiKey = options.apiKeyGemini || process.env.GEMINI_API_KEY;
    const claudeKey = options.apiKeyClaude || process.env.ANTHROPIC_API_KEY;

    if (targetBrain === 'gemini') {
      try {
        const res = await this._callGemini(geminiKey, options);
        this.activeBrain = 'gemini';
        return { brainUsed: 'gemini', ...res };
      } catch (geminiError) {
        console.warn('Fallo en Gemini, verificando failover a Claude:', geminiError.message);
        
        // Detectar si fue error 429 de cuota o indisponibilidad
        const isQuota = geminiError.code === 429 || geminiError.message.toLowerCase().includes('quota') || geminiError.message.toLowerCase().includes('resource_exhausted');
        
        if (claudeKey && (isQuota || !this.forcedBrain)) {
          this.activeBrain = 'claude';
          this.lastFailover = {
            from: 'gemini',
            to: 'claude',
            reason: geminiError.message,
            timestamp: new Date().toISOString()
          };
          NotificationManager.sendAlert(`🚨 Failover Activado: Gemini alcanzó límite o error de cuota. Conmutando automáticamente al cerebro secundario (Claude).`);
          
          const claudeRes = await this._callClaude(claudeKey, options);
          return { brainUsed: 'claude', failoverNotice: true, ...claudeRes };
        }
        throw geminiError;
      }
    } else {
      // Usar Claude directamente
      if (!claudeKey) throw new Error('API Key de Anthropic Claude no configurada.');
      try {
        const res = await this._callClaude(claudeKey, options);
        return { brainUsed: 'claude', ...res };
      } catch (claudeError) {
        if (!this.forcedBrain && geminiKey) {
          console.warn('Fallo en Claude, retornando a Gemini:', claudeError.message);
          this.activeBrain = 'gemini';
          const geminiRes = await this._callGemini(geminiKey, options);
          return { brainUsed: 'gemini', failoverNotice: true, ...geminiRes };
        }
        throw claudeError;
      }
    }
  }

  async _callGemini(apiKey, { systemInstruction, contents, tools }) {
    if (!apiKey) throw new Error('API Key de Google Gemini requerida');
    const model = 'gemini-2.0-flash';
    const endpoint = `/v1beta/models/${model}:generateContent?key=${apiKey}`;

    const payload = {
      system_instruction: { parts: [{ text: systemInstruction || '' }] },
      contents: contents,
      generationConfig: { temperature: 0.7, maxOutputTokens: 3000 }
    };

    if (tools && tools.length > 0) {
      payload.tools = [{
        function_declarations: tools.map(t => ({
          name: t.name,
          description: t.description,
          parameters: {
            type: 'OBJECT',
            properties: t.parameters || {},
            required: Object.keys(t.parameters || {})
          }
        }))
      }];
    }

    const res = await this._httpRequest('generativelanguage.googleapis.com', endpoint, 'POST', JSON.stringify(payload), {
      'Content-Type': 'application/json'
    });

    if (res.error) {
      const err = new Error(res.error.message || 'Error de API Gemini');
      err.code = res.error.code || 500;
      throw err;
    }

    const candidate = res.candidates?.[0];
    const textPart = candidate?.content?.parts?.find(p => p.text);
    const functionCallPart = candidate?.content?.parts?.find(p => p.functionCall);

    // Métricas de tokens de Gemini
    const usage = res.usageMetadata || {};
    const inTokens = usage.promptTokenCount || 0;
    const outTokens = usage.candidatesTokenCount || 0;
    this.recordUsage('gemini', inTokens, outTokens);

    return {
      text: textPart?.text || '',
      functionCall: functionCallPart?.functionCall || null,
      tokens: { input: inTokens, output: outTokens }
    };
  }

  async _callClaude(apiKey, { systemInstruction, contents, tools }) {
    if (!apiKey) throw new Error('API Key de Anthropic Claude requerida');

    // Adaptar formato de historial a mensajes de Claude
    const claudeMessages = [];
    (contents || []).forEach(turn => {
      const role = turn.role === 'model' ? 'assistant' : 'user';
      let contentText = '';
      if (Array.isArray(turn.parts)) {
        contentText = turn.parts.map(p => p.text || '').filter(Boolean).join('\n');
      } else if (typeof turn.parts === 'string') {
        contentText = turn.parts;
      }
      if (contentText.trim()) {
        claudeMessages.push({ role, content: contentText });
      }
    });

    const payload = {
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 3000,
      system: systemInstruction || '',
      messages: claudeMessages.length > 0 ? claudeMessages : [{ role: 'user', content: 'Hola' }]
    };

    if (tools && tools.length > 0) {
      payload.tools = tools.map(t => ({
        name: t.name,
        description: t.description,
        input_schema: {
          type: 'object',
          properties: t.parameters || {}
        }
      }));
    }

    const res = await this._httpRequest('api.anthropic.com', '/v1/messages', 'POST', JSON.stringify(payload), {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01'
    });

    if (res.error) {
      const err = new Error(res.error.message || 'Error de API Claude');
      err.code = res.error.type || 500;
      throw err;
    }

    const textBlock = (res.content || []).find(b => b.type === 'text');
    const toolUseBlock = (res.content || []).find(b => b.type === 'tool_use');

    // Métricas de tokens de Claude
    const usage = res.usage || {};
    const inTokens = usage.input_tokens || 0;
    const outTokens = usage.output_tokens || 0;
    this.recordUsage('claude', inTokens, outTokens);

    let functionCall = null;
    if (toolUseBlock) {
      functionCall = {
        name: toolUseBlock.name,
        args: toolUseBlock.input || {}
      };
    }

    return {
      text: textBlock?.text || '',
      functionCall: functionCall,
      tokens: { input: inTokens, output: outTokens }
    };
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
            if (res.statusCode >= 400 && !parsed.error) {
              parsed.error = { message: `HTTP ${res.statusCode}: ${body}`, code: res.statusCode };
            }
            resolve(parsed);
          } catch (e) {
            resolve({ error: { message: body, code: res.statusCode } });
          }
        });
      });
      req.on('error', reject);
      if (data) req.write(data);
      req.end();
    });
  }
}

module.exports = new BrainRouter();
