/**
 * BrainRouter - Cerebro Dual con Failover Automático, Monitor de Tokens y Control de Costes
 * Maneja Gemini (Primario) y Anthropic Claude (Secundario) con interfaz común y Function Calling
 */
const https = require('https');
const fs = require('fs');
const path = require('path');
const NotificationManager = require('../notifications/NotificationManager');

const TOKEN_USAGE_FILE = path.join(__dirname, '..', '..', 'data', 'token_usage.json');

// Tarifas USD por 1,000 tokens (1K) oficiales
const DEFAULT_RATES = {
  'gemini-2.0-flash': { inputPer1k: 0.0001, outputPer1k: 0.0004 },
  'gemini-1.5-flash': { inputPer1k: 0.000075, outputPer1k: 0.0003 },
  'gemini-1.5-pro': { inputPer1k: 0.00125, outputPer1k: 0.005 },
  'claude-3-5-sonnet-20241022': { inputPer1k: 0.003, outputPer1k: 0.015 },
  'claude-3-5-sonnet': { inputPer1k: 0.003, outputPer1k: 0.015 },
  'claude-3-5-haiku-20241022': { inputPer1k: 0.0008, outputPer1k: 0.004 },
  'claude-3-5-haiku': { inputPer1k: 0.0008, outputPer1k: 0.004 },
  'claude-3-haiku-20240307': { inputPer1k: 0.00025, outputPer1k: 0.00125 },
  'gemini-default': { inputPer1k: 0.0001, outputPer1k: 0.0004 },
  'claude-default': { inputPer1k: 0.003, outputPer1k: 0.015 }
};

class BrainRouter {
  constructor() {
    this.primaryBrain = 'gemini';
    this.forcedBrain = null; // 'gemini' | 'claude' | null
    this.activeBrain = 'gemini';
    this.lastFailover = null;
    this.tokenStats = {
      todayDate: new Date().toISOString().split('T')[0],
      today: {
        input: 0,
        output: 0,
        costEstimate: 0,
        byBrain: {
          gemini: { input: 0, output: 0, costEstimate: 0 },
          claude: { input: 0, output: 0, costEstimate: 0 }
        }
      },
      month: { input: 0, output: 0, costEstimate: 0 },
      history: []
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
        if (data.stats) {
          this.tokenStats = { ...this.tokenStats, ...data.stats };
          if (!this.tokenStats.today.byBrain) {
            this.tokenStats.today.byBrain = {
              gemini: { input: 0, output: 0, costEstimate: 0 },
              claude: { input: 0, output: 0, costEstimate: 0 }
            };
          }
        }
        if (data.limits) this.limits = { ...this.limits, ...data.limits };
      }
    } catch (e) {
      this.saveStats();
    }
    this.checkDailyRollover();
  }

  checkDailyRollover() {
    const todayStr = new Date().toISOString().split('T')[0];
    if (this.tokenStats.todayDate !== todayStr) {
      this.tokenStats.todayDate = todayStr;
      this.tokenStats.today = {
        input: 0,
        output: 0,
        costEstimate: 0,
        byBrain: {
          gemini: { input: 0, output: 0, costEstimate: 0 },
          claude: { input: 0, output: 0, costEstimate: 0 }
        }
      };
      this.saveStats();
    } else if (!this.tokenStats.today.byBrain) {
      this.tokenStats.today.byBrain = {
        gemini: { input: 0, output: 0, costEstimate: 0 },
        claude: { input: 0, output: 0, costEstimate: 0 }
      };
    }
  }

  saveStats() {
    try {
      const dir = path.dirname(TOKEN_USAGE_FILE);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(TOKEN_USAGE_FILE, JSON.stringify({ stats: this.tokenStats, limits: this.limits }, null, 2), 'utf8');
    } catch (e) {}
  }

  getDailyTokenLimit() {
    if (process.env.DAILY_TOKEN_LIMIT) {
      const parsed = parseInt(process.env.DAILY_TOKEN_LIMIT, 10);
      if (!isNaN(parsed) && parsed > 0) return parsed;
    }
    return this.limits.dailyTokenLimit || 100000;
  }

  getAlertThresholdPct() {
    if (process.env.ALERT_THRESHOLD_PCT) {
      const parsed = parseInt(process.env.ALERT_THRESHOLD_PCT, 10);
      if (!isNaN(parsed) && parsed > 0) return parsed;
    }
    return this.limits.alertThresholdPct || 80;
  }

  getRatesForModel(brain, modelName = null) {
    if (brain === 'gemini') {
      const inCustom = parseFloat(process.env.GEMINI_INPUT_COST_PER_1K);
      const outCustom = parseFloat(process.env.GEMINI_OUTPUT_COST_PER_1K);
      if (!isNaN(inCustom) && !isNaN(outCustom)) {
        return { inputPer1k: inCustom, outputPer1k: outCustom };
      }
    } else if (brain === 'claude') {
      const inCustom = parseFloat(process.env.CLAUDE_INPUT_COST_PER_1K);
      const outCustom = parseFloat(process.env.CLAUDE_OUTPUT_COST_PER_1K);
      if (!isNaN(inCustom) && !isNaN(outCustom)) {
        return { inputPer1k: inCustom, outputPer1k: outCustom };
      }
    }

    if (modelName && DEFAULT_RATES[modelName]) {
      return DEFAULT_RATES[modelName];
    }
    return brain === 'gemini' ? DEFAULT_RATES['gemini-default'] : DEFAULT_RATES['claude-default'];
  }

  getGeminiModel(override = null) {
    return override || process.env.GEMINI_MODEL || 'gemini-2.0-flash';
  }

  getClaudeModel(override = null) {
    return override || process.env.ANTHROPIC_MODEL || 'claude-3-5-sonnet-20241022';
  }

  recordUsage(brain, inputTokens = 0, outputTokens = 0, modelName = null) {
    this.checkDailyRollover();
    const todayStr = new Date().toISOString().split('T')[0];

    const rates = this.getRatesForModel(brain, modelName);
    const cost = ((inputTokens / 1000) * rates.inputPer1k) + ((outputTokens / 1000) * rates.outputPer1k);
    const roundedCost = Math.round(cost * 1000000) / 1000000;

    this.tokenStats.today.input += inputTokens;
    this.tokenStats.today.output += outputTokens;
    this.tokenStats.today.costEstimate = Math.round(((this.tokenStats.today.costEstimate || 0) + roundedCost) * 1000000) / 1000000;

    if (!this.tokenStats.today.byBrain) {
      this.tokenStats.today.byBrain = {
        gemini: { input: 0, output: 0, costEstimate: 0 },
        claude: { input: 0, output: 0, costEstimate: 0 }
      };
    }
    if (this.tokenStats.today.byBrain[brain]) {
      this.tokenStats.today.byBrain[brain].input += inputTokens;
      this.tokenStats.today.byBrain[brain].output += outputTokens;
      this.tokenStats.today.byBrain[brain].costEstimate = Math.round(((this.tokenStats.today.byBrain[brain].costEstimate || 0) + roundedCost) * 1000000) / 1000000;
    }

    this.tokenStats.month.input += inputTokens;
    this.tokenStats.month.output += outputTokens;
    this.tokenStats.month.costEstimate = Math.round(((this.tokenStats.month.costEstimate || 0) + roundedCost) * 1000000) / 1000000;

    this.tokenStats.history.push({
      timestamp: new Date().toISOString(),
      date: todayStr,
      brain,
      model: modelName,
      inputTokens,
      outputTokens,
      costEstimate: roundedCost
    });

    if (this.tokenStats.history.length > 500) {
      this.tokenStats.history = this.tokenStats.history.slice(-500);
    }

    this.saveStats();

    // Verificación de alerta de umbral
    const totalToday = this.tokenStats.today.input + this.tokenStats.today.output;
    const limit = this.getDailyTokenLimit();
    const alertPct = this.getAlertThresholdPct();
    const pct = Math.round((totalToday / limit) * 100);
    if (pct >= alertPct && pct < (alertPct + 5)) {
      NotificationManager.sendAlert(`⚠️ Aviso de consumo: Ha utilizado el ${pct}% de su límite diario de tokens (${totalToday.toLocaleString()} / ${limit.toLocaleString()}). Coste estimado hoy: $${(this.tokenStats.today.costEstimate || 0).toFixed(4)} USD.`);
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

  getBrainStatus() {
    this.checkDailyRollover();
    const todayTokens = (this.tokenStats.today.input || 0) + (this.tokenStats.today.output || 0);
    const limit = this.getDailyTokenLimit();
    const pct = Math.min(100, Math.round((todayTokens / limit) * 100));

    return {
      activeBrain: this.getEffectiveBrain(),
      forcedBrain: this.forcedBrain,
      lastFailover: this.lastFailover,
      models: {
        gemini: this.getGeminiModel(),
        claude: this.getClaudeModel()
      },
      stats: {
        ...this.tokenStats,
        todayTotal: todayTokens,
        usagePct: pct
      },
      limits: {
        dailyTokenLimit: limit,
        alertThresholdPct: this.getAlertThresholdPct()
      },
      costs: {
        todayUSD: this.tokenStats.today.costEstimate || 0,
        monthUSD: this.tokenStats.month.costEstimate || 0,
        byBrain: this.tokenStats.today.byBrain || {
          gemini: { input: 0, output: 0, costEstimate: 0 },
          claude: { input: 0, output: 0, costEstimate: 0 }
        },
        rates: {
          gemini: this.getRatesForModel('gemini', this.getGeminiModel()),
          claude: this.getRatesForModel('claude', this.getClaudeModel())
        }
      }
    };
  }

  /**
   * Ejecución inteligente con control de límites y failover automático
   * @param {Object} options { systemInstruction, contents, tools, apiKeyGemini, apiKeyClaude, model, bypassLimit }
   */
  async generateResponse(options = {}) {
    this.checkDailyRollover();

    // 1. Verificación de límite diario de tokens
    const dailyLimit = this.getDailyTokenLimit();
    const totalToday = (this.tokenStats.today.input || 0) + (this.tokenStats.today.output || 0);

    if (totalToday >= dailyLimit && !options.bypassLimit) {
      const errMsg = `Límite diario de tokens alcanzado (${totalToday.toLocaleString()} / ${dailyLimit.toLocaleString()} tokens). Las consultas han sido detenidas preventivamente para proteger sus cuotas y costes.`;
      NotificationManager.sendAlert(`🛑 ${errMsg}`);
      const limitErr = new Error(errMsg);
      limitErr.dailyLimitExceeded = true;
      limitErr.totalToday = totalToday;
      limitErr.dailyLimit = dailyLimit;
      limitErr.code = 429;
      throw limitErr;
    }

    const targetBrain = this.getEffectiveBrain();
    const geminiKey = options.apiKeyGemini || process.env.GEMINI_API_KEY;
    const claudeKey = options.apiKeyClaude || process.env.ANTHROPIC_API_KEY;

    if (targetBrain === 'gemini') {
      try {
        const res = await this._callGemini(geminiKey, options);
        this.activeBrain = 'gemini';
        return { brainUsed: 'gemini', ...res };
      } catch (geminiError) {
        if (geminiError.dailyLimitExceeded) throw geminiError;
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
        if (claudeError.dailyLimitExceeded) throw claudeError;
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

  async _callGemini(apiKey, options = {}) {
    const { systemInstruction, contents, tools } = options;
    if (!apiKey) throw new Error('API Key de Google Gemini requerida');
    const model = this.getGeminiModel(options.model);
    const endpoint = `/v1beta/models/${model}:generateContent?key=${apiKey}`;

    const payload = {
      system_instruction: { parts: [{ text: systemInstruction || '' }] },
      contents: contents,
      generationConfig: { temperature: 0.7, maxOutputTokens: 3000 }
    };

    if (tools && tools.length > 0) {
      payload.tools = [{
        function_declarations: tools.map(t => {
          const props = {};
          Object.entries(t.parameters || {}).forEach(([pName, pDef]) => {
            const rawType = (pDef.type || 'string').toUpperCase();
            const validType = ['STRING', 'NUMBER', 'INTEGER', 'BOOLEAN', 'ARRAY', 'OBJECT'].includes(rawType) ? rawType : 'STRING';
            props[pName] = {
              type: validType,
              description: pDef.description || ''
            };
          });
          return {
            name: t.name,
            description: t.description,
            parameters: {
              type: 'OBJECT',
              properties: props,
              required: t.required || Object.keys(props)
            }
          };
        })
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
    this.recordUsage('gemini', inTokens, outTokens, model);

    return {
      text: textPart?.text || '',
      functionCall: functionCallPart?.functionCall || null,
      tokens: { input: inTokens, output: outTokens },
      modelUsed: model
    };
  }

  async _callClaude(apiKey, options = {}) {
    const { systemInstruction, contents, tools } = options;
    if (!apiKey) throw new Error('API Key de Anthropic Claude requerida');
    const model = this.getClaudeModel(options.model);

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
      model: model,
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
    this.recordUsage('claude', inTokens, outTokens, model);

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
      tokens: { input: inTokens, output: outTokens },
      modelUsed: model
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

const routerInstance = new BrainRouter();
routerInstance.BrainRouter = BrainRouter;
module.exports = routerInstance;
